import json, subprocess, pathlib, sys

def test_bin_dq_schema_template_stdout():
    cmd = ["bin/dq", "--input", "tests/data/sample.csv", "--emit-schema-template", "-", "--dataset-name", "sample_timeseries"]
    r = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["dataset_name"] == "sample_timeseries"
    assert isinstance(data.get("columns"), list) and len(data["columns"]) >= 1
