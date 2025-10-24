# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path

def run_cli(args):
    r = subprocess.run([sys.executable, "-m", "nfops_planner.plan_engine.cli"] + args,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)

def test_quantile_loop_reduces_space_and_artifacts(tmp_path: Path):
    out_dir = tmp_path/"p"; out_dir.mkdir()
    js = run_cli([
        "--spec","configs/examples/matrix_spec.yaml",
        "--invalid","configs/examples/invalid_values.yaml",
        "--time-budget","60s",
        "--max-combos","10000",
        "--out-dir", str(out_dir)
    ])
    assert js["space_reduction_rate"] > 0
    assert any(any(k in a for k in ["reduction_strategy=importance_quantile_loop","reduction_strategy=fanova_importance_shrink","reduction_strategy=trim_top30pct_by_max_cardinality"]) for a in js["assumptions"])
    assert (out_dir/"recommended_space.json").exists()
    # importance.json は degrade-safe に JSON として読める
    imp = json.loads((out_dir/"importance.json").read_text(encoding="utf-8"))
    assert isinstance(imp, dict)

