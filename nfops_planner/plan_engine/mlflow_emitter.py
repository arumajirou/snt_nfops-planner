# -*- coding: utf-8 -*-
from __future__ import annotations

def emit_to_mlflow(result: dict, params: dict) -> bool:
    try:
        import mlflow
    except Exception:
        return False
    try:
        mlflow.set_experiment("planning")
        with mlflow.start_run(run_name="planning.dry_run"):
            # params: safe dump
            safe_params = {k: str(v) for k, v in params.items()}
            mlflow.log_params(safe_params)
            mlflow.log_metrics({
                "estimated_trials": float(result.get("estimated_trials", 0)),
                "estimated_gpu_hours": float(result.get("estimated_gpu_hours", 0.0)),
                "estimated_duration_sec": float(result.get("estimated_duration_sec", 0)),
                "estimated_cost_usd": float(result.get("estimated_cost_usd", 0.0)),
                "space_reduction_rate": float(result.get("space_reduction_rate", 0.0)),
            })
            # assumptions を artifact に書き出し
            import json, tempfile, os
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "assumptions.json")
                with open(p, "w", encoding="utf-8") as f:
                    json.dump({"assumptions": result.get("assumptions", [])}, f, ensure_ascii=False, indent=2)
                mlflow.log_artifact(p, artifact_path="planning")
        return True
    except Exception:
        return False
