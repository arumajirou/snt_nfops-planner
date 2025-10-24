# -*- coding: utf-8 -*-
import json, pathlib
def test_assumptions_has_strategy():
    p = pathlib.Path("plan/planning/assumptions.json")
    assert p.exists(), "assumptions.json が無い"
    data = json.loads(p.read_text())
    assert data.get("reduction_strategy") == "importance_quantile_loop"
