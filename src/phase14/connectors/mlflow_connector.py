# src/phase14/connectors/mlflow_connector.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

def load_latest_phase13_artifacts(base: Path = Path("outputs/phase13")) -> Dict[str, Any]:
    """Phase13成果物から eval/gatekeeper/plan を拾う（存在しない場合は空辞書）"""
    if not base.exists():
        return {}
    latest = max(base.glob("*"), key=lambda p: p.stat().st_mtime, default=None)
    if not latest:
        return {}
    out = {}
    for name in ["eval.json", "gatekeeper.json", "plan_summary.json", "production_retrain.yaml"]:
        p = latest / name
        if p.exists():
            out[name] = p.read_text(encoding="utf-8")
    out["latest_dir"] = str(latest)
    return out
