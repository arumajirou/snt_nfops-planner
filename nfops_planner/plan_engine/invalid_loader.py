# -*- coding: utf-8 -*-
from __future__ import annotations
import re
from typing import Any, Dict, List, Callable, Tuple

Rule = Dict[str, Any]

_num = re.compile(r"^-?\d+(?:\.\d+)?$")

def _to_num(x: str):
    return float(x) if "." in x else int(x)

def _parse_expr(expr: str) -> Callable[[Any], bool]:
    s = str(expr).strip()
    m = re.match(r"^(==|!=|<=|>=|<|>)\s*(-?\d+(?:\.\d+)?)$", s)
    if m:
        op, val = m.group(1), _to_num(m.group(2))
        if op == "==": return lambda x: x == val
        if op == "!=": return lambda x: x != val
        if op == "<=": return lambda x: x <= val
        if op == ">=": return lambda x: x >= val
        if op == "<":  return lambda x: x <  val
        if op == ">":  return lambda x: x >  val
    m = re.match(r"^in\s*\[(.*)\]$", s)
    if m:
        items = [t.strip() for t in m.group(1).split(",") if t.strip() != ""]
        vals = []
        for t in items:
            if _num.match(t): vals.append(_to_num(t))
            else: vals.append(t.strip("'\""))
        return lambda x: x in vals
    # fallback: exact
    return lambda x: str(x) == s

def compile_rules(raw: Dict[str, Any]) -> List[Tuple[List[str], Dict[str, Callable[[Any], bool]], str]]:
    """
    returns list of tuples: (models, compiled_conditions, reason)
    models=[] means global.
    """
    rules = []
    for r in raw.get("rules", []):
        models = r.get("model")
        if models is None: model_list: List[str] = []
        elif isinstance(models, str): model_list = [models]
        else: model_list = list(models)
        conds = {}
        for k, v in (r.get("conditions") or {}).items():
            conds[k] = _parse_expr(str(v))
        reason = str(r.get("reason") or "invalid")
        rules.append((model_list, conds, reason))
    return rules

def expand_param_values(v: Any):
    if isinstance(v, list):
        return list(v)
    if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
        mn, mx, st = v["min"], v["max"], v["step"]
        if st <= 0 or mx < mn: return []
        out = []
        x = mn
        # inclusive stepping
        while True:
            out.append(x)
            x = x + st
            if (st > 0 and x > mx) or (st < 0 and x < mx):
                break
        return out
    return [v]

def count_with_invalid(model: Dict[str, Any], compiled_rules, max_enumeration: int = 200000) -> Tuple[int, int, bool]:
    """returns (valid_count, invalid_count, applied)"""
    name = model.get("name","")
    params = model.get("params",{})
    keys = list(params.keys())
    values = [expand_param_values(params[k]) for k in keys]
    total = 1
    for vs in values:
        total *= max(1, len(vs))
    if total > max_enumeration:
        return total, 0, False

    invalid = 0
    valid = 0
    # build fast matcher
    def is_invalid(assign: Dict[str, Any]) -> bool:
        for models, conds, _reason in compiled_rules:
            if models and name not in models:
                continue
            # all conditions must hold
            ok = True
            for k, f in conds.items():
                if k not in assign: ok = False; break
                if not f(assign[k]): ok = False; break
            if ok: return True
        return False

    from itertools import product
    for combo in product(*values):
        assign = dict(zip(keys, combo))
        if is_invalid(assign):
            invalid += 1
        else:
            valid += 1
    return valid, invalid, True
