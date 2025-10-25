import subprocess, sys, json, pathlib

def test_chunk_e2e(tmp_path):
    out = tmp_path/"o"
    rc = subprocess.call([
        sys.executable, "src/phase2/dq_runner.py",
        "--input","tests/data/sample.csv",
        "--schema","schema/example_schema.json",
        "--outdir", str(out),
        "--chunksize","2"  # 小さなチャンクでストリーミング経路を通す
    ])
    assert rc == 0
    s = json.loads((out/"summary.json").read_text())
    assert s["n_rows"] == 3
