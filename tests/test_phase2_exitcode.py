import subprocess, sys, pathlib, json

def test_exitcode_on_invalid(tmp_path):
    out = tmp_path/"o"
    cmd = [sys.executable, "src/phase2/dq_runner.py",
           "--input","tests/data/sample.csv",
           "--schema","schema/example_schema.json",
           "--outdir", str(out),
           "--fail-on-invalid"]
    rc = subprocess.call(cmd)
    assert rc != 0  # invalidがあるため非ゼロ
    # summaryは生成されている
    s = json.loads((out/"summary.json").read_text())
    assert s["n_rows"] == 3
    assert s["n_invalid_rows"] >= 1
