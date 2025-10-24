# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, Tuple

def predict_sec_per_trial(spec: Dict[str, Any], fallback: float) -> Tuple[float, float, float, str]:
    """
    MLflow の過去 runs から metrics.sec_per_trial の分布を取り、中央値と IQR を返す。
    データ不足/失敗時は (fallback, fallback, fallback, "heuristic")
    """
    try:
        import mlflow
        import numpy as np
    except Exception:
        return fallback, fallback, fallback, "heuristic"

    try:
        runs = mlflow.search_runs(experiment_names=["planning"])
    except Exception:
        return fallback, fallback, fallback, "heuristic"

    if runs is None or runs.empty or "metrics.sec_per_trial" not in runs.columns:
        return fallback, fallback, fallback, "heuristic"

    y = runs["metrics.sec_per_trial"].dropna().astype(float).values
    if y.size < 10:
        return fallback, fallback, fallback, "heuristic"

    med = float(np.median(y))
    iqr = float(np.percentile(y, 75) - np.percentile(y, 25))
    lo = max(1.0, med - 1.35 * iqr)
    hi = med + 1.35 * iqr
    return med, lo, hi, "learned"
