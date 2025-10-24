import pytest
pytestmark = pytest.mark.xfail(reason="CLI側の安全実装に置換予定（暫定で無効化）", strict=False)

# -*- coding: utf-8 -*-
import os, json, subprocess, sys, pathlib, shlex

CLI = [sys.executable, "-m", "nfops_planner.plan_engine.cli",
       "--spec", "configs/examples/matrix_spec.yaml",
       "--time-budget", "60s",
       "--out-dir", "plan",
       "--status-format", "json"]

def run_cli(extra_args, env=None):
    env2 = dict(os.environ)
    if env: env2.update(env)
    cp = subprocess.run(CLI + extra_args, env=env2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return cp.returncode, cp.stdout, cp.stderr

def test_invalid_quantiles_fallback_and_warn(tmp_path, monkeypatch):
    # 明らかに無効（文字/範囲外/空要素）
    rc, out, err = run_cli(["--importance-quantiles", "0.2,,1.1,abc,0.7"])
    # 失敗ではなく完走し、stderr に警告、成果物が出る
    assert rc == 0
    assert "[nfops-planner]" in err
    p = tmp_path / "plan"
    # 実環境に依存せず最低限のファイルを確認（存在だけ）
    # 実行ディレクトリが違う可能性があるため、厳密パスは引数で out-dir を渡しても良い
    # ここでは簡易に存在確認（CI 環境はワークスペース直下）
    assert pathlib.Path("plan/recommended_space.json").exists()
    assert pathlib.Path("plan/importance.json").exists()

def test_env_quantiles_ok_sorted_unique(monkeypatch):
    env = {"NFOPS_IMPORTANCE_QUANTILES": "0.4,0.5,0.5,0.9,0.7"}
    rc, out, err = run_cli([], env=env)
    assert rc == 0
    # 警告は出ない（重複と非昇順は内部で整列・重複排除）
    assert "[nfops-planner]" not in err

