# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Tuple

def compute_importances(model: Dict[str, Any], estimate_fn, sample_cap: int = 20000):
    try:
        import optuna
        from optuna.importance import get_param_importances
    except Exception:
        return {}  # degrade

    # fANOVA は trial の (params, value) が必要。ここでは「試行コスト=estimate_fn(params)」で擬似試行を作る。
    from itertools import product
    params = model.get("params", {})
    items = []
    keys = list(params.keys())

    # 値展開（list / range 辞書）
    def expand(v):
        if isinstance(v, list): return list(v)
        if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
            mn, mx, st = v["min"], v["max"], v["step"]
            if st == 0: return []
            out=[]; x=mn
            if st>0:
                while x<=mx: out.append(x); x+=st
            else:
                while x>=mx: out.append(x); x+=st
            return out
        return [v]

    grids = [expand(params[k]) for k in keys]
    # サンプル数が過大なら先頭から間引き
    total = 1
    for g in grids: total *= max(1, len(g))
    step = max(1, int(total / max(1, sample_cap)))
    # trial データ構築
    X = []
    ii = 0
    for combo in product(*grids):
        if (ii % step) == 0:
            p = dict(zip(keys, combo))
            X.append(p)
        ii += 1
    if not X:
        return {}

    # Optuna Studyに擬似トライアルを流し込み
    study = optuna.create_study(direction="minimize")
    def obj(trial):
        # 既存 p を trial に復元
        i = len(study.trials)
        p = X[min(i, len(X)-1)]
        for k, v in p.items():
            # 定義は形だけ（実値は固定で使う）
            if isinstance(v, (int, float)):
                _ = trial.suggest_float(k, float(v), float(v))
            else:
                _ = trial.suggest_categorical(k, [v])
        return float(estimate_fn({"params": p}))
    # 擬似実行
    for _ in range(len(X)):
        study.optimize(obj, n_trials=1, catch=(Exception,))

    imps = get_param_importances(study)
    return {k: float(v) for k, v in imps.items()}

def propose_by_importance(model: Dict[str, Any], importances: Dict[str, float]):
    # 低重要度: 固定（先頭値）。高重要度: 値域を 50% に圧縮（中央寄せ）
    from copy import deepcopy
    if not importances:
        return model  # no change
    params = deepcopy(model.get("params", {}))
    if not params: return model
    # 閾値: 上位50%を高重要度、残りを低重要度
    sorted_keys = sorted(importances, key=lambda k: importances[k], reverse=True)
    cutoff = max(1, len(sorted_keys)//2)
    hi = set(sorted_keys[:cutoff]); lo = set(sorted_keys[cutoff:])
    def expand(v):
        if isinstance(v, list): return list(v)
        if isinstance(v, dict) and {"min","max","step"}.issubset(v.keys()):
            mn, mx, st = v["min"], v["max"], v["step"]
            out=[]; x=mn
            if st>0:
                while x<=mx: out.append(x); x+=st
            else:
                while x>=mx: out.append(x); x+=st
            return out
        return [v]
    for k in params:
        vals = expand(params[k])
        if not vals: continue
        if k in lo:
            params[k] = [vals[0]]  # 固定
        else:
            keep = max(1, int(len(vals)*0.5))
            start = max(0, (len(vals)-keep)//2)
            params[k] = vals[start:start+keep]
    return {"name": model.get("name",""), "params": params}
