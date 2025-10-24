# -*- coding: utf-8 -*-
from __future__ import annotations
import re
from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, List, Callable, Tuple, Optional, Pattern

Rule = Dict[str, Any]
_num = re.compile(r"^-?\d+(?:\.\d+)?$")

def _to_num(x: str):
    try:
        return float(x) if "." in x else int(x)
    except Exception:
        return x

def _parse_expr(expr: str) -> Callable[[Any], bool]:
    """
    文字列式を述語にコンパイル:
      - '== 3', '!= 1', '<= 10', 'in [a,b,3]'
      - フォールバックは文字列完全一致
    """
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
        vals: List[Any] = []
        for t in items:
            if _num.match(t): vals.append(_to_num(t))
            else: vals.append(t.strip("'\""))
        return lambda x: x in vals
    return lambda x: str(x) == s  # fallback exact

def _parse_cond_map(d: Dict[str, Any]) -> Dict[str, Callable[[Any], bool]]:
    return {k: _parse_expr(str(v)) for k, v in (d or {}).items()}

def expand_param_values(v: Any):
    """list or {'min','max','step'} を展開"""
    if isinstance(v, list):
        return list(v)
    if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
        mn, mx, st = v["min"], v["max"], v["step"]
        if st == 0: return []
        out = []
        x = mn
        if st > 0:
            while x <= mx:
                out.append(x); x = x + st
        else:
            while x >= mx:
                out.append(x); x = x + st
        return out
    return [v]

@dataclass
class CompiledRule:
    model_list: List[str]
    model_regex: Optional[Pattern]
    must: Dict[str, Callable[[Any], bool]]    # AND 条件
    forbid: Dict[str, Callable[[Any], bool]]  # これのどれかが真なら invalid
    reason: str

def compile_rules(raw: Dict[str, Any]) -> List[CompiledRule]:
    """
    DSL:
      - model: str | [str] | 省略
      - regex: str (re.compile して search)
      - conditions: {k: expr} (AND)
      - any: [ {k: expr}, ... ] (OR) -> ルールへ分配
      - implies: { if: {..}, then: {..} } -> if AND (NOT then) を invalid に
    """
    rules: List[CompiledRule] = []
    for r in (raw or {}).get("rules", []):
        models = r.get("model")
        if models is None: model_list: List[str] = []
        elif isinstance(models, str): model_list = [models]
        else: model_list = list(models)
        regex_pat = r.get("regex")
        model_regex = re.compile(regex_pat) if isinstance(regex_pat, str) else None
        reason = str(r.get("reason") or "invalid")

        # any: OR を単純ルールへ分配
        if isinstance(r.get("any"), list) and r["any"]:
            for sub in r["any"]:
                rules.append(CompiledRule(
                    model_list, model_regex,
                    must=_parse_cond_map(sub), forbid={}, reason=reason
                ))

        # 通常 conditions
        if r.get("conditions"):
            rules.append(CompiledRule(
                model_list, model_regex,
                must=_parse_cond_map(r["conditions"]), forbid={}, reason=reason
            ))

        # implies: if 真 かつ then 偽 を invalid
        if isinstance(r.get("implies"), dict):
            if_part = _parse_cond_map(r["implies"].get("if") or {})
            then_part = _parse_cond_map(r["implies"].get("then") or {})
            if if_part and then_part:
                rules.append(CompiledRule(
                    model_list, model_regex,
                    must=if_part, forbid=then_part, reason=reason
                ))
    return rules

def _in_model_scope(name: str, rule: CompiledRule) -> bool:
    ok1 = (not rule.model_list) or (name in rule.model_list)
    ok2 = (rule.model_regex is None) or bool(rule.model_regex.search(name))
    return ok1 and ok2

def count_with_invalid(model: Dict[str, Any], compiled: List[CompiledRule],
                       max_enumeration: int = 200000) -> Tuple[int, int, bool]:
    """
    与えられた model の param 空間を列挙して invalid を数える。
    列挙が cap を超える場合は degrade（invalid を数えず applied=False）。
    return (valid_count, invalid_count, applied)
    """
    name = model.get("name", "")
    params: Dict[str, Any] = model.get("params", {}) or {}
    keys = list(params.keys())
    grids = [expand_param_values(params[k]) for k in keys]
    # 空を 1 とみなす（異常ケース回避）
    lengths = [max(1, len(g)) for g in grids]
    total = 1
    for L in lengths: total *= L
    if total > max_enumeration:
        return total, 0, False  # degrade: invalid 未適用

    # 対象ルール抽出
    rs = [ru for ru in compiled if _in_model_scope(name, ru)]
    if not rs:
        return total, 0, True

    def _is_invalid(assign: Dict[str, Any]) -> bool:
        for ru in rs:
            # must が全部真か？
            must_ok = True
            for k, pred in ru.must.items():
                if k not in assign or not pred(assign[k]):
                    must_ok = False; break
            if not must_ok:
                continue
            # forbid が一つでも真なら invalid
            if ru.forbid:
                for k, pred in ru.forbid.items():
                    if k in assign and pred(assign[k]):
                        return True
                # if 真 かつ then 偽 は invalid なので、
                # forbid 全てが偽 ⇒ invalid（IF 成立時の THEN 未満足）
                return True
            # forbid 無しの普通の invalid 条件
            return True
        return False

    invalid = 0
    for combo in product(*grids):
        assign = dict(zip(keys, combo))
        if _is_invalid(assign):
            invalid += 1
    valid = total - invalid
    return valid, invalid, True
