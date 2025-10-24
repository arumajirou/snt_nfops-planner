# -*- coding: utf-8 -*-
from __future__ import annotations
import nfops_planner.plan_engine.assumptions_hook  # noqa: F401
import argparse, json, sys, time, socket, subprocess, os
from pathlib import Path
from typing import Any, Dict, List
from .spec_loader import load_spec, naive_count_combos, SpecError
from .cost_time_estimator import estimate_trial_seconds, aggregate_cost
from .invalid_loader import compile_rules, count_with_invalid, expand_param_values
from .mlflow_emitter import emit_to_mlflow
from .sec_model import predict_sec_per_trial
from .importance_reducer import compute_importances, propose_by_importance

def _parse_time_budget(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("h"): return int(float(s[:-1]) * 3600)
    if s.endswith("m"): return int(float(s[:-1]) * 60)
    if s.endswith("s"): return int(float(s[:-1]))
    return int(float(s))

def _versions():
    out = {}
    for name in ("optuna","mlflow","sklearn","pandas","yaml"):
        try:
            if name == "yaml":
                import yaml as _m; out["pyyaml"] = _m.__version__
            elif name == "sklearn":
                import sklearn as _m; out["scikit_learn"] = _m.__version__
            else:
                _m = __import__(name); out[name] = _m.__version__
        except Exception:
            pass
    return out

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Planner Dry-run (Phase 1.2)")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--invalid", default=None, help="invalid rules yaml")
    ap.add_argument("--time-budget", default="12h", help="e.g. 12h, 30m, 3600s")
    ap.add_argument("--max-combos", type=int, default=200000, help="exact invalid filtering cap")
    ap.add_argument("--gpu-type", default="A100")
    ap.add_argument("--cost-unit", type=float, default=3.5, help="USD per GPU hour")
    ap.add_argument("--gpu-share", type=float, default=1.0, help="fraction of 1 GPU")
    ap.add_argument("--out-dir", default="plan")
    ap.add_argument("--emit-artifacts", choices=["on","off"], default="on")
    ap.add_argument("--status-format", choices=["json","text"], default="json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    try:
        spec = load_spec(args.spec)
    except SpecError as e:
        print(str(e), file=sys.stderr)
        return 2

    # invalid ルール読み込み
    compiled = []
    dsl_kinds = {"simple":0,"any":0,"regex":0,"implies":0}
    if args.invalid:
        p = Path(args.invalid)
        if p.exists():
            import yaml
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            # DSL 種別カウント
            for r in raw.get("rules", []) if isinstance(raw.get("rules"), list) else []:
                if r.get("any"): dsl_kinds["any"] += 1
                if r.get("regex"): dsl_kinds["regex"] += 1
                if r.get("implies"): dsl_kinds["implies"] += 1
                if r.get("conditions"): dsl_kinds["simple"] += 1
            compiled = compile_rules(raw)
        else:
            print("E-SPEC-101 invalid file not found", file=sys.stderr)

    combos = 0
    sec_hat = 0.0
    invalid_applied = False
    modelwise: List[Dict[str, Any]] = []
    for m in spec["_active_models"]:
        naive = naive_count_combos(m)
        if compiled:
            valid, invalid, applied = count_with_invalid(m, compiled, max_enumeration=args.max_combos)
        else:
            valid, invalid, applied = naive, 0, False
        invalid_applied = invalid_applied or applied
        combos += max(0, int(valid))
        sec_hat = max(sec_hat, float(estimate_trial_seconds(m)))  # pessimistic per-trial
        modelwise.append({"name": m.get("name",""), "naive": naive, "valid": valid, "invalid": invalid, "applied": applied})

    # 学習ベースの sec_per_trial があれば CI 付きで採用（保守的に max を取る）
    learned, lo, hi, source = predict_sec_per_trial(spec, sec_hat if sec_hat>0 else 1.0)
    if source == "learned":
        sec_hat = max(sec_hat, learned)

    # --- 集計（フォールバック込みで安全に） -------------------------------
    agg = {}
    try:
        agg = aggregate_cost(combos, sec_hat, args.gpu_share, args.cost_unit) or {}
    except Exception:
        agg = {}
    # 決して欠けないデフォルトを構築
    default_duration = float(combos) * float(sec_hat)  # gpu_share=1 を基本に
    defaults = {
        "estimated_trials": int(combos),
        "estimated_duration_sec": default_duration,
        "estimated_gpu_hours": (default_duration / 3600.0),
        "estimated_cost_usd": (default_duration / 3600.0) * float(args.cost_unit),
        "space_reduction_rate": 0.0,
        "assumptions": []
    }
    # dict/シーケンスに両対応でマージ
    result: Dict[str, Any] = dict(defaults)
    if isinstance(agg, dict):
        result.update(agg)
    else:
        try:
            result.update(dict(agg))
        except Exception:
            pass

    # assumptions を追記（存在しない場合もケア）
    if "assumptions" not in result or not isinstance(result["assumptions"], list):
        result["assumptions"] = []
    result["assumptions"].append(f"sec_per_trial~{sec_hat}")
    result["assumptions"].append(f"gpu_share={args.gpu_share}")
    result["assumptions"].append(f"gpu_type={args.gpu_type}")
    result["assumptions"].append(f"usd_per_gpu_hour={args.cost_unit}")
    result["assumptions"].append("invalid_table=" + ("applied" if invalid_applied else "ignored"))
    result["assumptions"].append(f"sec_per_trial_source={source}")
    if source == "learned":
        result["assumptions"].append(f"sec_per_trial_ci=[{lo},{hi}]")

    # 予算判定
    time_budget_sec = _parse_time_budget(args.time_budget)
    status_note = "OK" if float(result.get("estimated_duration_sec", default_duration)) <= float(time_budget_sec) else "EXCEEDS_BUDGET"

    # 予算を超えたら縮約案を作る（fANOVA→失敗なら 30%トリム）
    used_strategy = None
    if status_note == "EXCEEDS_BUDGET":
        recommended = {"models": []}
        importance_dump: Dict[str, Dict[str, float]] = {}
        fanova_ok = True
        reduced_total = 0
        for m in spec["_active_models"]:
            try:
                imps = compute_importances(m, estimate_trial_seconds)
                importance_dump[m.get("name","")] = imps
                m2 = propose_by_importance(m, imps)
                recommended["models"].append(m2)
                reduced_total += naive_count_combos({"params": m2.get("params", {})})
            except Exception:
                fanova_ok = False
                break
        if (not fanova_ok) or (reduced_total >= combos):
            # フォールバック: 最大カーディナリティ 30% トリム
            reduced_total = 0
            recommended = {"models": []}
            for m in spec["_active_models"]:
                params = m.get("params", {}) or {}
                if not params:
                    recommended["models"].append({"name": m.get("name",""), "params": params})
                    reduced_total += 1
                    continue
                lens = {k: len(expand_param_values(v)) for k, v in params.items()}
                kmax = max(lens, key=lens.get)
                vals = expand_param_values(params[kmax])
                keep = max(1, int(len(vals) * 0.7))
                new_params = dict(params); new_params[kmax] = vals[:keep]
                recommended["models"].append({"name": m.get("name",""), "params": new_params})
                reduced_total += naive_count_combos({"params": new_params})
            used_strategy = "trim_top30pct_by_max_cardinality"
        else:
            used_strategy = "fanova_importance_shrink"

        result["space_reduction_rate"] = round(1.0 - (reduced_total / max(1, combos)), 3)
        result["assumptions"].append(f"status={status_note}")
        result["assumptions"].append(f"reduction_strategy={used_strategy}")

        # アーティファクト（dry-run では書かない）
        if args.emit_artifacts == "on" and not args.dry_run:
            out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "recommended_space.json").write_text(json.dumps(recommended, ensure_ascii=False, indent=2), encoding="utf-8")
            # importance.json（空でも出す）
            (out_dir / "importance.json").write_text(json.dumps(importance_dump, ensure_ascii=False, indent=2), encoding="utf-8")

    # MLflow へ emit（失敗は無視）
    params_for_ml = {
        "spec": args.spec, "invalid": args.invalid or "",
        "time_budget": args.time_budget, "max_combos": args.max_combos,
        "gpu_type": args.gpu_type, "cost_unit": args.cost_unit,
        "gpu_share": args.gpu_share, "status": status_note,
    }
    run_id = emit_to_mlflow(result, params_for_ml)
    if run_id: result["mlflow_run_id"] = run_id

    # アウトプット/ログ（dry-run ではファイルなし）
    if args.emit_artifacts == "on" and not args.dry_run:
        out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "plan_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            rev = subprocess.check_output(["git","rev-parse","--short","HEAD"], text=True).strip()
        except Exception:
            rev = "unknown"
        log = {
            "ts": time.time(), "phase": "P1.2", "status": status_note,
            "host": socket.gethostname(), "git_rev": rev,
            "versions": _versions(), "mlflow_run_id": run_id or "",
            "result": result, "modelwise": modelwise,
            "args": {
                "spec": args.spec, "invalid": args.invalid, "time_budget": args.time_budget,
                "max_combos": args.max_combos, "gpu_type": args.gpu_type,
                "cost_unit": args.cost_unit, "gpu_share": args.gpu_share
            },
            "dsl_kinds": dsl_kinds, "dsl_rules_count": sum(dsl_kinds.values())
        }
        with (out_dir / "planning.log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    # 出力形式
    if args.status_format == "text":
        line = (f"trials={result.get('estimated_trials')} "
                f"cost_usd={result.get('estimated_cost_usd')} "
                f"status={status_note} "
                f"budget={args.time_budget} "
                f"strategy={(used_strategy or '-') if status_note=='EXCEEDS_BUDGET' else '-'}").strip()
        print(line)
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
    # === P12-01: importance quantiles validation (CLI > ENV > default) ===
    from .quantiles_validator import parse_importance_quantiles, emit_warning_if_any, DEFAULT_QUANTILES
    import os as _os
    _q, _warn = parse_importance_quantiles(getattr(args, "importance_quantiles", None),
                                           _os.environ.get("NFOPS_IMPORTANCE_QUANTILES"))
    emit_warning_if_any(_warn)  # 無効入力なら stderr に警告を出す（落とさない）
    try:
        # 以降の互換性のため、args.* は CSV 文字列で保持しておく
        args.importance_quantiles = ",".join(str(x) for x in _q)
    except Exception:
        pass
    # 内部で tuple を参照したい箇所向けに、確定値を束ねておく（ある場合のみ使われる）
    # === P12-01: RELAX_IMPORTANCE_QUANTILES_ACTION (before parse_args) ===
    # argparse が type=float/nargs=+ 等で事前に落とさないよう、該当 Action を緩和
    try:
        _acts = getattr(parser, "_actions", [])
        for _a in _acts:
            if "--importance-quantiles" in getattr(_a, "option_strings", ()):
                _a.type = str  # まずは文字列で受ける
                # 複数トークン設定だった場合でも1トークンとして受ける（CSV想定）
                if getattr(_a, "nargs", None) not in (None, "?",):
                    _a.nargs = None
                break
    except Exception:
        # 失敗しても致命にはしない（後段のフォールバックで吸収）
        pass

    IMPORTANCE_QUANTILES = tuple(_q)
