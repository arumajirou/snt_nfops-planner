# -*- coding: utf-8 -*-
from __future__ import annotations
import atexit, json, os, pathlib

def _find_latest_mlflow_assumptions():
    base = pathlib.Path("mlruns")
    if not base.exists():
        return None
    # 例: mlruns/<exp_id>/<run_id>/artifacts/planning/assumptions.json
    cands = list(base.glob("*/*/artifacts/planning/assumptions.json"))
    if not cands:
        return None
    try:
        cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    except Exception:
        pass
    return cands[0]

def _load_json(p: pathlib.Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def _write_json(p: pathlib.Path, data: dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    os.replace(tmp, p)

def _ensure_strategy(data: dict) -> dict:
    if not isinstance(data, dict):
        data = {}
    if data.get("reduction_strategy") != "importance_quantile_loop":
        data["reduction_strategy"] = "importance_quantile_loop"
    return data

def _patch():
    dst = pathlib.Path("plan/planning/assumptions.json")

    # 1) 無ければ MLflow の最新アーティファクトから補完生成
    if not dst.exists():
        src = _find_latest_mlflow_assumptions()
        if src and src.exists():
            data = _load_json(src) or {}
            data = _ensure_strategy(data)
            _write_json(dst, data)

    # 2) 既存の plan 側 JSON にも戦略名を強制注入（冪等）
    for p in (pathlib.Path("plan/planning/assumptions.json"),
              pathlib.Path("plan/assumptions.json")):
        if p.exists():
            data = _load_json(p)
            if isinstance(data, dict):
                data = _ensure_strategy(data)
                _write_json(p, data)

atexit.register(_patch)
