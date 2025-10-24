# -*- coding: utf-8 -*-
from __future__ import annotations

def _parse_sec_from_assumptions(assumptions):
    if not assumptions: return None
    for a in assumptions:
        if isinstance(a, str) and a.startswith("sec_per_trial~"):
            try: return float(a.split("~",1)[1])
            except Exception: return None
    return None

def emit_to_mlflow(result: dict, params: dict):
    try:
        import mlflow
    except Exception:
        return None
    try:
        mlflow.set_experiment("planning")
        with mlflow.start_run(run_name="planning.dry_run") as run:
            safe_params = {k: str(v) for k, v in params.items()}
            mlflow.log_params(safe_params)
            m = {
                "estimated_trials": float(result.get("estimated_trials", 0)),
                "estimated_gpu_hours": float(result.get("estimated_gpu_hours", 0.0)),
                "estimated_duration_sec": float(result.get("estimated_duration_sec", 0)),
                "estimated_cost_usd": float(result.get("estimated_cost_usd", 0.0)),
                "space_reduction_rate": float(result.get("space_reduction_rate", 0.0)),
            }
            sec_hat = _parse_sec_from_assumptions(result.get("assumptions"))
            if sec_hat is not None:
                m["sec_per_trial"] = float(sec_hat)
            mlflow.log_metrics(m)
            import json, tempfile, os
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "assumptions.json")
                with open(p, "w", encoding="utf-8") as f:
                    json.dump({"assumptions": result.get("assumptions", [])}, f, ensure_ascii=False, indent=2)
                mlflow.log_artifact(p, artifact_path="planning")
            return run.info.run_id
    except Exception:
        return None
