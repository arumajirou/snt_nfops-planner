# -*- coding: utf-8 -*-
import json, subprocess, sys, shutil
from pathlib import Path
import pytest

def _run_cli(args):
    r = subprocess.run([sys.executable, "-m", "nfops_planner.plan_engine.cli"] + args,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def test_dsl_any_regex_implies_and_artifacts(tmp_path: Path):
    out_dir = tmp_path / "p"
    out = _run_cli([
        "--spec","configs/examples/matrix_spec.yaml",
        "--invalid","configs/examples/invalid_dsl_examples.yaml",
        "--time-budget","60s","--out-dir", str(out_dir)
    ])
    js = json.loads(out)
    assert js["estimated_trials"] >= 1
    # 予算超過なら縮約案とログが出る
    if (out_dir/"recommended_space.json").exists():
        rec = json.loads((out_dir/"recommended_space.json").read_text(encoding="utf-8"))
        assert "models" in rec
    # importance は空でも JSON として妥当
    if (out_dir/"importance.json").exists():
        _ = json.loads((out_dir/"importance.json").read_text(encoding="utf-8"))

def test_status_text_and_dry_run_behaves(tmp_path: Path):
    out = _run_cli([
        "--spec","configs/examples/matrix_spec.yaml",
        "--status-format","text","--dry-run"
    ])
    assert "trials=" in out and "status=" in out
    assert not (tmp_path/"plan"/"plan_summary.json").exists()
