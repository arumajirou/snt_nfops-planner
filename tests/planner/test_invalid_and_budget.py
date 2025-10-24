# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path

def _run_cli(spec, invalid, out_dir, time_budget="12h", max_combos=500):
    cmd = [sys.executable, "-m", "nfops_planner.plan_engine.cli",
           "--spec", spec, "--invalid", invalid, "--time-budget", time_budget,
           "--max-combos", str(max_combos), "--out-dir", str(out_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    js = json.loads(r.stdout)
    return js

def test_invalid_rule_reduces_trials(tmp_path: Path):
    spec = "configs/examples/matrix_spec.yaml"
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("""
rules:
  - model: "AutoNHITS"
    conditions:
      batch_size: "== 128"
      input_size: "== 72"
    reason: "avoid large batch with long input"
""", encoding="utf-8")
    out_dir = tmp_path / "plan1"
    js = _run_cli(spec, str(invalid), out_dir, time_budget="12h", max_combos=10000)
    assert js["estimated_trials"] < 18  # examples spec baseline is 18
    assert (out_dir/"plan_summary.json").exists()

def test_budget_exceeds_outputs_recommendation(tmp_path: Path):
    spec = "configs/examples/matrix_spec.yaml"
    invalid = "configs/examples/invalid_values.yaml"
    out_dir = tmp_path / "plan2"
    # かなり厳しい予算で縮約を発動させる
    js = _run_cli(spec, invalid, out_dir, time_budget="60s", max_combos=10000)
    assert js["estimated_trials"] >= 1
    # 縮約案が保存され、縮約率が0より大きい
    rec = out_dir / "recommended_space.json"
    assert rec.exists()
    assert js["space_reduction_rate"] > 0.0
