import json, os, subprocess, sys, pathlib
def test_phase2_dq(tmp_path):
    out = tmp_path/"out"
    cmd = [sys.executable, "src/phase2/dq_runner.py",
           "--input","tests/data/sample.csv",
           "--schema","schema/example_schema.json",
           "--outdir", str(out),
           "--profile"]
    rc = subprocess.call(cmd)
    assert rc==0
    assert (out/"invalid_rows.parquet").exists()
    assert (out/"summary.json").exists()
    s = json.loads((out/"summary.json").read_text())
    assert s["n_rows"]==3
    assert s["n_invalid_rows"]>=1
