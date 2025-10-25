import json, subprocess, sys

def test_schema_template_infer_types():
    cmd = ["bin/dq","--input","tests/data/sample.csv","--emit-schema-template","-","--dataset-name","sample_timeseries"]
    r = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    schema = json.loads(r.stdout)
    cols = {c["name"]: c for c in schema["columns"]}
    assert cols["ds"]["dtype"] == "datetime"
    assert cols["y"]["dtype"] in ("float","int")  # サンプルに非数値1件あるため float を優先
