# -*- coding: utf-8 -*-
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any, Dict, List
try:
    import yaml  # PyYAML
except Exception as e:
    print("E-SPEC-000 PyYAML not available: install pyyaml", file=sys.stderr)
    raise

class SpecError(RuntimeError): ...

def load_spec(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise SpecError("E-SPEC-001 spec file not found")
    with p.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    if not isinstance(spec, dict) or "models" not in spec:
        raise SpecError("E-SPEC-002 invalid schema: missing 'models'")
    models = [m for m in spec.get("models", []) if m.get("active", True)]
    for m in models:
        if "name" not in m or "params" not in m:
            raise SpecError("E-SPEC-003 each model needs name and params")
    spec["_active_models"] = models
    return spec

def naive_count_combos(model: Dict[str, Any]) -> int:
    """Naive product of discrete lists or ranges with 'step'. Ignore invalid table (Phase 1)."""
    params = model.get("params", {})
    def count_param(v: Any) -> int:
        if isinstance(v, list):
            return len(v)
        if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
            mn, mx, st = v["min"], v["max"], v["step"]
            if st <= 0 or mx < mn: return 0
            return int((mx - mn) // st + 1)
        # scalar or unknown => treat as fixed 1
        return 1
    c = 1
    for v in params.values():
        c *= max(1, count_param(v))
    return c
