# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path

def run_cmd(args):
    r = subprocess.run([sys.executable, "-m", "nfops_planner.plan_engine.cli"] + args,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def test_status_text_and_dry_run(tmp_path: Path):
    out = run_cmd(["--spec","configs/examples/matrix_spec.yaml","--status-format","text","--dry-run"])
    assert "trials=" in out and "status=" in out
    # dry-run ではファイルを作らない
    assert not (tmp_path/"plan"/"plan_summary.json").exists()

def test_artifacts_when_budget_exceeds(tmp_path: Path):
    d = tmp_path/"p"; d.mkdir()
    out = run_cmd([
        "--spec","configs/examples/matrix_spec.yaml",
        "--invalid","configs/examples/invalid_values.yaml",
        "--time-budget","60s",
        "--out-dir", str(d)
    ])
    js = json.loads(out)
    assert js["estimated_trials"] >= 1
    # 縮約が出る
    assert (d/"recommended_space.json").exists()
    # importance.json は optuna が無ければ出ないが、存在したら JSON として妥当
    if (d/"importance.json").exists():
        imp = json.loads((d/"importance.json").read_text(encoding="utf-8"))
        assert isinstance(imp, dict)
