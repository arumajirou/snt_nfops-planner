import subprocess, sys, json, pathlib
def test_invalid_rate_threshold(tmp_path):
    out = tmp_path/"o"
    rc = subprocess.call([
        sys.executable, "src/phase2/dq_runner.py",
        "--input","tests/data/sample.csv",
        "--schema","schema/example_schema.json",
        "--outdir", str(out),
        "--invalid-rate-threshold","0.1"  # 10%で落とす
    ])
    # sample.csv は3行中>=1行がinvalidなので invalid_rate>=0.33 を想定→非ゼロ
    assert rc != 0
    s = json.loads((out/"summary.json").read_text())
    assert s["invalid_rate"] >= 0.1
