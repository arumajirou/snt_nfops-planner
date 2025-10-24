# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
from typing import Iterable, List, Tuple

DEFAULT_QUANTILES: Tuple[float, ...] = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)

def emit_warning_if_any(msg: str | None) -> None:
    if msg:
        sys.stderr.write(f"[nfops-planner] {msg}\n")
        sys.stderr.flush()

def _parse_csv_floats(s: str) -> List[float]:
    parts = [p.strip() for p in s.split(",")]
    vals: List[float] = []
    for p in parts:
        if p == "":
            # 空要素は無効入力扱いにする（後段フォールバックのトリガ）
            raise ValueError("空要素を含む")
        try:
            vals.append(float(p))
        except Exception:
            raise ValueError(f"非数値を検出: {p!r}")
    return vals

def _is_sorted_strict(xs: Iterable[float]) -> bool:
    xs = list(xs)
    return all(xs[i] < xs[i+1] for i in range(len(xs)-1))

def parse_importance_quantiles(arg_value: str | None, env_value: str | None) -> Tuple[Tuple[float, ...], str | None]:
    """
    優先度: CLI 引数 > 環境変数 > 既定。
    正常系: (tuple_of_floats, None)
    フォールバック系: (DEFAULT_QUANTILES, warn_msg)
    """
    # list/tuple で渡る可能性に保険（nargs 等の歴史対応）
    def _normalize_seq_to_csv(x):
        if isinstance(x, (list, tuple)):
            return ",".join(str(v) for v in x)
        return x

    arg_value = _normalize_seq_to_csv(arg_value)
    env_value = _normalize_seq_to_csv(env_value)

    src = None
    raw = None
    if arg_value and str(arg_value).strip():
        raw = str(arg_value).strip()
        src = "CLI"
    elif env_value and str(env_value).strip():
        raw = str(env_value).strip()
        src = "ENV"
    else:
        return DEFAULT_QUANTILES, None

    try:
        vals = _parse_csv_floats(raw)
        if len(vals) < 1:
            raise ValueError("要素数が0")
        if not all(0.0 < v < 1.0 for v in vals):
            raise ValueError("0–1の開区間外の値を含む")
        # 重複除去後に昇順へ正規化（重複/非昇順は警告不要とする）
        uniq = tuple(sorted(set(vals)))
        return uniq, None
    except Exception as e:
        return DEFAULT_QUANTILES, f"{src} の --importance-quantiles が無効: {e}; 既定 {DEFAULT_QUANTILES} にフォールバックします。"

__all__ = ["DEFAULT_QUANTILES", "parse_importance_quantiles", "emit_warning_if_any"]
