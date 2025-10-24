# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any

def estimate_trial_seconds(model: Dict[str, Any], gpu_tflops: float = 150.0) -> float:
    """
    Very rough: base + alpha*h + beta*seq*batch + layers*d_model^2 penalty.
    Fallback constants chosen conservatively for Phase 1.
    """
    params = model.get("params", {})
    h = max(params.get("h",[24])[0] if isinstance(params.get("h"), list) else params.get("h",24), 1)
    batch =  params.get("batch_size", {"min":32}).get("min", 32) if isinstance(params.get("batch_size"), dict) else (params.get("batch_size",32) if isinstance(params.get("batch_size"), int) else 32)
    input_size = params.get("input_size",[48])[0] if isinstance(params.get("input_size"), list) else params.get("input_size",48)
    d_model = params.get("d_model", 256) if isinstance(params.get("d_model"), int) else 256
    n_layers = params.get("n_layers", 4) if isinstance(params.get("n_layers"), int) else 4

    base = 900.0  # 15 min
    alpha_h = 3.0
    beta_seq_batch = 0.002
    gamma_size = 0.00001
    compute_penalty = 0.000001 * n_layers * (d_model ** 2)
    flop_factor = 200.0 / max(gpu_tflops, 50.0)  # normalize vs. a strong GPU

    sec = base + alpha_h*h + beta_seq_batch*input_size*batch + gamma_size*input_size**2
    sec *= (1.0 + compute_penalty) * flop_factor
    return max(sec, 60.0)

def aggregate_cost(trials: int, sec_per_trial: float, gpu_share: float, usd_per_gpu_hour: float) -> Dict[str, Any]:
    total_sec = int(trials * sec_per_trial)
    gpu_hours = (total_sec / 3600.0) * gpu_share
    cost = gpu_hours * usd_per_gpu_hour
    return {"total_sec": total_sec, "gpu_hours": gpu_hours, "cost_usd": cost}
