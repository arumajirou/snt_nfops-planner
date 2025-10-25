import json, subprocess

def test_schema_template_infer_types_and_pk():
    cmd = ["bin/dq","--input","tests/data/sample.csv","--emit-schema-template","-","--dataset-name","sample_timeseries"]
    r = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    schema = json.loads(r.stdout)
    cols = {c["name"]: c for c in schema["columns"]}
    assert cols["ds"]["dtype"] == "datetime"
    assert cols["y"]["dtype"] in ("float","int")
    # 測定列を PK にしない
    assert schema.get("primary_keys", []) == []
