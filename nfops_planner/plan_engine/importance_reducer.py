# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List
from .invalid_loader import expand_param_values

def compute_importances(model: Dict[str, Any], estimate_fn=None) -> Dict[str, float]:
    """
    劣化安全: Optuna が無い/試行データが無い環境でも 0 辞書を返す。
    ここでは OAT(one-at-a-time) 近似で「影響のありそう度」をざっくり計算。
    estimate_fn が無い場合は全パラ 0（=フォールバック経路へ）。
    """
    try:
        params = (model or {}).get("params", {}) or {}
        if not params: return {}
        if estimate_fn is None: return {}
        # ベース点は各パラの先頭値
        base = {k: (expand_param_values(v) or [None])[0] for k, v in params.items()}

        def sec(p: Dict[str, Any]) -> float:
            # estimate_fn は model dict を期待する実装想定が多いので、
            # 最低限の情報のみ詰め替えて呼ぶ（失敗したら 0）
            try:
                fake = dict(model)
                fake["params"] = dict(p)
                return float(estimate_fn(fake))
            except Exception:
                return 0.0

        importances: Dict[str, float] = {}
        base_sec = sec(base)
        for k, v in params.items():
            vals = expand_param_values(v)
            if len(vals) <= 1:
                importances[k] = 0.0
                continue
            diffs = []
            for val in vals:
                p = dict(base); p[k] = val
                diffs.append(abs(sec(p) - base_sec))
            importances[k] = float(max(diffs))
        # 正規化
        s = sum(importances.values())
        if s > 0:
            for k in list(importances.keys()):
                importances[k] = importances[k] / s
        return importances
    except Exception:
        return {}

def propose_by_importance(model: Dict[str, Any], imps: Dict[str, float]) -> Dict[str, Any]:
    """
    重要度が低い離散は半分に、高い連続は IQR(25–75%) に圧縮。
    importances が空のときはそのまま返す（CLI 側で 30% トリムにフォールバック）。
    """
    params = (model or {}).get("params", {}) or {}
    if not imps:
        return {"name": model.get("name", ""), "params": params}

    # 大きいほど重要とみなす
    sorted_keys = sorted(params.keys(), key=lambda k: imps.get(k, 0.0))
    new_params: Dict[str, Any] = {}
    for k in sorted_keys:
        v = params[k]
        vals = expand_param_values(v)
        if len(vals) <= 1:
            new_params[k] = v
            continue
        imp = imps.get(k, 0.0)
        # 連続辞書かどうか
        is_range = isinstance(v, dict) and {"min","max","step"}.issubset(v.keys())
        if is_range and imp >= 0.5:
            # IQR 圧縮
            n = len(vals)
            lo = max(0, int(n * 0.25))
            hi = max(lo + 1, int(n * 0.75))
            keep = vals[lo:hi]
            new_params[k] = {"min": keep[0], "max": keep[-1], "step": v["step"]}
        elif not is_range and imp < 0.3:
            # 低重要度の離散は 50% 残し（中央寄せ）
            n = len(vals); keep = max(1, int(n * 0.5))
            new_params[k] = vals[:keep]
        else:
            # 変更なし
            new_params[k] = v
    return {"name": model.get("name", ""), "params": new_params}
