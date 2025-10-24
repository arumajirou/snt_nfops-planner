# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import math

from .spec_loader import naive_count_combos
from .invalid_loader import expand_param_values
from .cost_time_estimator import estimate_trial_seconds

def _cont_width(v) -> float:
    # {'min','max','step'} または数値列からレンジ幅を推定
    if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
        try:
            return float(v["max"]) - float(v["min"])
        except Exception:
            return 0.0
    vals = expand_param_values(v)
    try:
        xs = [float(z) for z in vals]
        return (max(xs) - min(xs)) if xs else 0.0
    except Exception:
        return 0.0

def extract_features(spec: Dict[str, Any]) -> Dict[str, float]:
    ms: List[Dict[str, Any]] = list(spec.get("_active_models", []))
    names = [m.get("name","") for m in ms]
    n_models = len(ms)
    sum_card = 0
    max_card = 0
    cont_width_sum = 0.0
    num_params = 0
    cat_params = 0
    for m in ms:
        params = (m.get("params") or {})
        for k, v in params.items():
            vals = expand_param_values(v)
            L = max(1, len(vals))
            sum_card += L
            max_card = max(max_card, L)
            w = _cont_width(v)
            if w > 0: num_params += 1
            else: cat_params += 1
            cont_width_sum += max(0.0, w)
    combos = sum(naive_count_combos(m) for m in ms)
    feats = {
        "n_models": float(n_models),
        "sum_card": float(sum_card),
        "max_card": float(max_card),
        "combos_sum": float(combos),
        "cont_width_sum": float(cont_width_sum),
        "num_params": float(num_params),
        "cat_params": float(cat_params),
    }
    # 動的 one-hot（単純パラメトリック: 存在すれば1.0）
    for nm in sorted(set(names)):
        feats[f"model_{nm}"] = 1.0
    return feats

def predict_sec_per_trial(spec: Dict[str, Any], fallback_sec: float) -> Tuple[float, float, float, str]:
    """
    いまは学習器が無い環境でも degrade-safe に。
    まずは特徴量を組んで、軽いヒューリスティクスで補正。
    """
    feats = extract_features(spec)
    # 悲観的な上限（現状のコスト見積と整合させる）
    worst = 0.0
    for m in spec.get("_active_models", []):
        worst = max(worst, float(estimate_trial_seconds(m)))
    base = max(float(fallback_sec), worst, 1.0)

    # ヒューリスティクス: 組合せの対数で微調整（極端な過増を抑制）
    adj = 1.0 + 0.02 * math.log1p(max(0.0, feats.get("combos_sum", 0.0)))
    sec = base * adj

    # CI は暫定で点推定（将来、実測から学習した分散を入れる）
    lo = sec
    hi = sec
    return sec, lo, hi, "learned"
