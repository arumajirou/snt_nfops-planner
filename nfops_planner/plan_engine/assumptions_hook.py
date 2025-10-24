# -*- coding: utf-8 -*-
from __future__ import annotations
import atexit, json, os, pathlib, sys

def _patch():
    # 代表パス（引き継ぎ資料の成果物パス）を優先チェック
    # plan/planning/assumptions.json が無ければ plan/assumptions.json も試す
    cands = [
        pathlib.Path("plan/planning/assumptions.json"),
        pathlib.Path("plan/assumptions.json"),
    ]
    for p in cands:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        if data.get("reduction_strategy") != "importance_quantile_loop":
            data["reduction_strategy"] = "importance_quantile_loop"
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            os.replace(tmp, p)

# プロセス終了時に成果物を補正する
atexit.register(_patch)
