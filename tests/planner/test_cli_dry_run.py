# -*- coding: utf-8 -*-
import json, subprocess, sys, shutil, os
from pathlib import Path

def test_dry_run_minimal(tmp_path: Path):
    spec = "configs/examples/matrix_spec.yaml"
    assert Path(spec).exists()

    out_dir = tmp_path / "plan"
    cmd = [sys.executable, "-m", "nfops_planner.plan_engine.cli",
           "--spec", spec, "--time-budget", "12h", "--max-combos", "500",
           "--out-dir", str(out_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    js = json.loads(r.stdout)
    for k in ["estimated_trials","estimated_gpu_hours","estimated_duration_sec","estimated_cost_usd","space_reduction_rate","assumptions"]:
        assert k in js
    assert js["estimated_trials"] > 0
    assert (out_dir/"plan_summary.json").exists()
