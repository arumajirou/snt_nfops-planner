# -*- coding: utf-8 -*-
import json, pathlib, subprocess, sys
def test_assumptions_has_strategy():
    # 先に成果物を生成
    cmd = [sys.executable, "-m", "nfops_planner.plan_engine.cli",
           "--spec", "configs/examples/matrix_spec.yaml",
           "--time-budget", "60s",
           "--out-dir", "plan",
           "--status-format", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    p = pathlib.Path("plan/planning/assumptions.json")
    assert p.exists(), "assumptions.json が無い"
    data = json.loads(p.read_text())
    assert data.get("reduction_strategy") == "importance_quantile_loop"
