# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import math, os

from .cost_time_estimator import estimate_trial_seconds
from .spec_loader import naive_count_combos
from .invalid_loader import expand_param_values

def _is_numeric_list(xs: List[Any]) -> bool:
    try:
        for x in xs: float(x)
        return True
    except Exception:
        return False

def _central_slice(xs: List[Any], keep_frac: float) -> List[Any]:
    if not xs: return xs
    n = len(xs)
    k = max(1, int(math.ceil(n * keep_frac)))
    s = sorted(xs, key=lambda z: float(z)) if _is_numeric_list(xs) else list(xs)
    mid = n // 2
    b = max(0, mid - k // 2)
    e = min(n, b + k)
    return s[b:e]

def _compress_values(values: List[Any], policy: str = "IQR", frac: float = 0.5) -> List[Any]:
    if not values: return values
    if policy in ("IQR", "central"):
        return _central_slice(values, keep_frac=frac)
    return values

def compute_importances(model: Dict[str, Any], est_fn=estimate_trial_seconds) -> Dict[str, float]:
    params = (model or {}).get("params", {}) or {}
    if not params: return {}
    raw = {k: max(1, len(expand_param_values(v))) for k, v in params.items()}
    s = float(sum(raw.values())) or 1.0
    return {k: raw[k] / s for k in raw}

def _shrink_model_by_threshold(model: Dict[str, Any], imps: Dict[str, float],
                               threshold: float, weak_frac: float = 0.5) -> Dict[str, Any]:
    name = model.get("name","")
    params = dict((model.get("params") or {}))
    out_params: Dict[str, Any] = {}
    for k, v in params.items():
        vals = expand_param_values(v)
        if len(vals) <= 1:
            out_params[k] = v; continue
        imp = float(imps.get(k, 0.0))
        if imp < threshold:
            shrunk = _compress_values(vals, policy="IQR", frac=weak_frac)
            out_params[k] = list(shrunk)
        else:
            out_params[k] = v
    return {"name": name, "params": out_params}

def _estimate_duration_sec(models: List[Dict[str, Any]], gpu_share: float) -> Tuple[int, float]:
    combos = 0
    sec_hat = 0.0
    for m in models:
        combos += naive_count_combos(m)
        sec_hat = max(sec_hat, float(estimate_trial_seconds(m)))
    total_sec = (combos * max(1e-9, sec_hat)) / max(1e-9, float(gpu_share))
    return combos, total_sec

def _parse_env_thresholds() -> List[float] | None:
    s = os.environ.get("NFOPS_IMPORTANCE_QUANTILES", "").strip()
    if not s: return None
    try:
        qs = [float(x) for x in s.split(",") if x.strip()!=""]
        return [q for q in qs if 0.0 <= q <= 1.0]
    except Exception:
        return None

def shrink_until_budget(spec: Dict[str, Any], time_budget_sec: float,
                        gpu_share: float = 1.0,
                        thresholds: List[float] | None = None) -> Tuple[Dict[str, Any], Dict[str, Dict[str, float]], float, float]:
    base_models = list(spec.get("_active_models", []))
    base_combos, _ = _estimate_duration_sec(base_models, gpu_share=gpu_share)
    if thresholds is None:
        thresholds = _parse_env_thresholds() or [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    importance_dump: Dict[str, Dict[str, float]] = {}
    rec: List[Dict[str, Any]] = []

    for th in thresholds:
        rec.clear(); importance_dump.clear()
        for m in base_models:
            imps = compute_importances(m, estimate_trial_seconds)
            importance_dump[m.get("name","")] = imps
            rec.append(_shrink_model_by_threshold(m, imps, threshold=th, weak_frac=0.5))
        combos, total_sec = _estimate_duration_sec(rec, gpu_share=gpu_share)
        if total_sec <= time_budget_sec:
            rate = round(1.0 - (combos / max(1, base_combos)), 3)
            return ({"models": list(rec)}, dict(importance_dump), th, rate)

    combos, _ = _estimate_duration_sec(rec, gpu_share=gpu_share)
    rate = round(1.0 - (combos / max(1, base_combos)), 3)
    return ({"models": list(rec)}, dict(importance_dump), thresholds[-1], rate)

# ---- 後方互換: 旧CLIが import した名を維持 ---------------------------------
def propose_by_importance(model: Dict[str, Any], imps: Dict[str, float],
                          threshold: float = 0.5, weak_frac: float = 0.5) -> Dict[str, Any]:
    return _shrink_model_by_threshold(model, imps, threshold=threshold, weak_frac=weak_frac)
