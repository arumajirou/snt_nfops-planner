# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import math

from .cost_time_estimator import estimate_trial_seconds
from .spec_loader import naive_count_combos
from .invalid_loader import expand_param_values

def _is_numeric_list(xs: List[Any]) -> bool:
    try:
        for x in xs:
            float(x)  # raises if not numeric
        return True
    except Exception:
        return False

def _central_slice(xs: List[Any], keep_frac: float) -> List[Any]:
    """中央 keep_frac を残す。数値は昇順、非数値は順序維持の先頭優先。"""
    if not xs: return xs
    n = len(xs)
    k = max(1, int(math.ceil(n * keep_frac)))
    if _is_numeric_list(xs):
        s = sorted(xs, key=lambda z: float(z))
    else:
        s = list(xs)
    mid = n // 2
    b = max(0, mid - k // 2)
    e = min(n, b + k)
    return s[b:e]

def _compress_values(values: List[Any], policy: str = "IQR", frac: float = 0.5) -> List[Any]:
    """
    policy:
      - 'IQR' : おおよそ中央50%（frac で調整）
      - 'central': 中央 keep_frac
    """
    if not values: return values
    if policy in ("IQR", "central"):
        return _central_slice(values, keep_frac=frac)
    return values

def compute_importances(model: Dict[str, Any], est_fn=estimate_trial_seconds) -> Dict[str, float]:
    """
    degrade-safe: Optuna 等が無くても、カーディナリティ比で近似重要度を作る。
    重みは [0,1] に正規化。
    """
    params = (model or {}).get("params", {}) or {}
    if not params:
        return {}
    # 近似: 値数が多いほど探索負荷インパクトが大きい
    raw = {k: max(1, len(expand_param_values(v))) for k, v in params.items()}
    s = float(sum(raw.values()))
    if s <= 0: s = 1.0
    return {k: raw[k] / s for k in raw}

def _shrink_model_by_threshold(model: Dict[str, Any], imps: Dict[str, float],
                               threshold: float, weak_frac: float = 0.5) -> Dict[str, Any]:
    """
    重要度 < threshold のパラメータのみを「中央分位圧縮（IQR相当）」する。
    重要パラメータはそのまま残す。
    """
    name = model.get("name","")
    params = dict((model.get("params") or {}))
    out_params: Dict[str, Any] = {}
    for k, v in params.items():
        vals = expand_param_values(v)
        if len(vals) <= 1:
            out_params[k] = v; continue
        imp = float(imps.get(k, 0.0))
        if imp < threshold:
            # 低重要度: 強めに圧縮
            shrunk = _compress_values(vals, policy="IQR", frac=weak_frac)
            out_params[k] = list(shrunk)
        else:
            out_params[k] = v
    return {"name": name, "params": out_params}

def _estimate_duration_sec(models: List[Dict[str, Any]], gpu_share: float) -> Tuple[int, float]:
    """推定総試行数と時間（秒）。per-trial は悲観的に max を採用。"""
    combos = 0
    sec_hat = 0.0
    for m in models:
        combos += naive_count_combos(m)
        sec_hat = max(sec_hat, float(estimate_trial_seconds(m)))
    total_sec = (combos * max(1e-9, sec_hat)) / max(1e-9, float(gpu_share))
    return combos, total_sec

def shrink_until_budget(spec: Dict[str, Any], time_budget_sec: float,
                        gpu_share: float = 1.0) -> Tuple[Dict[str, Any], Dict[str, Dict[str, float]], float, float]:
    """
    分位しきい値を段階的に上げ（0.3→0.4→…→0.9）、低重要度パラメータだけ中央分位圧縮。
    予算を満たした時点で停止。
    return: (recommended_space, importance_dump, used_threshold, reduction_rate)
    """
    base_models = list(spec.get("_active_models", []))
    base_combos, _ = _estimate_duration_sec(base_models, gpu_share=gpu_share)
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    importance_dump: Dict[str, Dict[str, float]] = {}

    for th in thresholds:
        rec: List[Dict[str, Any]] = []
        importance_dump.clear()
        for m in base_models:
            imps = compute_importances(m, estimate_trial_seconds)
            importance_dump[m.get("name","")] = imps
            m2 = _shrink_model_by_threshold(m, imps, threshold=th, weak_frac=0.5)
            rec.append(m2)
        combos, total_sec = _estimate_duration_sec(rec, gpu_share=gpu_share)
        if total_sec <= time_budget_sec:
            rate = round(1.0 - (combos / max(1, base_combos)), 3)
            return ({"models": rec}, dict(importance_dump), th, rate)

    # 失敗: 最後のしきい値でも達成できず
    combos, _ = _estimate_duration_sec(rec, gpu_share=gpu_share)
    rate = round(1.0 - (combos / max(1, base_combos)), 3)
    return ({"models": rec}, dict(importance_dump), thresholds[-1], rate)
