# -*- coding: utf-8 -*-
from __future__ import annotations
import re
from typing import Any, Dict, List, Callable, Tuple

# ルールは {model: str|[str]|None, conditions: {param: expr}, reason: str} の最小DSL
# expr: "== 32", "!= 64", "<= 128", "in [32,64,128]" などをサポート

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
    # フォールバック：文字列の完全一致
    return lambda x: str(x) == s

def compile_rules(raw: Dict[str, Any]) -> List[Tuple[List[str], Dict[str, Callable[[Any], bool]], str]]:
    """
    return: List of (models, compiled_conditions, reason)
      - models: [] は全モデル適用
    """
    rules = []
    for r in (raw or {}).get("rules", []):
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
        if st == 0: return []
        if (st > 0 and mx < mn) or (st < 0 and mx > mn): return []
        out = []
        x = mn
        # inclusive stepping
        if st > 0:
            while x <= mx:
                out.append(x)
                x = x + st
        else:
            while x >= mx:
                out.append(x)
                x = x + st
        return out
    # スカラー等は固定値扱い
    return [v]

def count_with_invalid(model: Dict[str, Any], compiled_rules, max_enumeration: int = 200000) -> Tuple[int, int, bool]:
    """
    厳密列挙で invalid を除外してカウントする。
    return: (valid_count, invalid_count, applied=True/False)
      applied=False は「閾値超で厳密化をスキップ（=naive）」の意味。
    """
    name = model.get("name","")
    params = model.get("params", {})
    keys = list(params.keys())
    values = [expand_param_values(params[k]) for k in keys]
    total = 1
    for vs in values: total *= max(1, len(vs))
    if total > max_enumeration:
        # 閾値超なら厳密フィルタはスキップ
        return total, 0, False

    def is_invalid(assign: Dict[str, Any]) -> bool:
        for models, conds, _reason in compiled_rules:
            if models and name not in models:
                continue
            ok = True
            for k, f in conds.items():
                if k not in assign: ok = False; break
                if not f(assign[k]): ok = False; break
            if ok: return True
        return False

    from itertools import product
    invalid = 0
    valid = 0
    for combo in product(*values):
        assign = dict(zip(keys, combo))
        if is_invalid(assign): invalid += 1
        else: valid += 1
    return valid, invalid, True
