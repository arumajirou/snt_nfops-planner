# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, sys, time, socket, subprocess
from pathlib import Path
from typing import Any, Dict
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

    compiled = []
    if args.invalid:
        p = Path(args.invalid)
        if p.exists():
            import yaml
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            compiled = compile_rules(raw)
        else:
            print("E-SPEC-101 invalid file not found", file=sys.stderr)

    combos = 0
    sec_hat = 0.0
    invalid_applied = False
    modelwise = []
    for m in spec["_active_models"]:
        naive = naive_count_combos(m)
        if compiled:
            valid, invalid, applied = count_with_invalid(m, compiled, max_enumeration=args.max_combos)
        else:
            valid, invalid, applied = naive, 0, False
        invalid_applied = invalid_applied or applied
        combos += valid
        sec_hat = max(sec_hat, estimate_trial_seconds(m))
        modelwise.append({"name": m.get("name",""), "naive": int(naive), "valid": int(valid), "invalid": int(invalid), "applied": bool(applied)})

    # MLflow 過去runから学習できたら採用（保守的に max）
    learned, lo, hi, source = predict_sec_per_trial(spec, sec_hat)
    if source == "learned":
        sec_hat = max(sec_hat, learned)

    agg = aggregate_cost(combos, sec_hat, args.gpu_share, args.cost_unit)
    time_budget_sec = _parse_time_budget(args.time_budget)

    result: Dict[str, Any] = {
        "estimated_trials": int(combos),
        "estimated_gpu_hours": round(agg["gpu_hours"], 3),
        "estimated_duration_sec": int(agg["total_sec"]),
        "estimated_cost_usd": round(agg["cost_usd"], 2),
        "space_reduction_rate": 0.0,
        "assumptions": [
            f"sec_per_trial~{sec_hat:.1f}",
            f"gpu_share={args.gpu_share}",
            f"gpu_type={args.gpu_type}",
            f"usd_per_gpu_hour={args.cost_unit}",
            "invalid_table=" + ("applied" if invalid_applied else "ignored"),
        ],
    }
    if source == "learned":
        result["assumptions"].append(f"sec_per_trial_ci=[{lo:.1f},{hi:.1f}]")
        result["assumptions"].append("sec_per_trial_source=learned")

    outdir = Path(args.out_dir)
    if not args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)

    status_note = "OK"
    if agg["total_sec"] > time_budget_sec:
        status_note = "EXCEEDS_BUDGET"
        # まず fANOVA で縮約（なければフォールバック）
        used_strategy = None
        reduced_total = 0
        recommended = {"models": []}
        importance_dump = {}
        fanova_ok = True
        for m in spec["_active_models"]:
            try:
                imps = compute_importances(m, estimate_trial_seconds)
                importance_dump[m.get("name","")] = imps
                m2 = propose_by_importance(m, imps)
                recommended["models"].append(m2)
                reduced_total += naive_count_combos({"params": m2.get("params", {})})
            except Exception:
                fanova_ok = False; break
        if not fanova_ok or reduced_total >= combos:
            # fallback: 最大カーディナリティ30%トリム
            reduced_total = 0
            recommended = {"models": []}
            for m in spec["_active_models"]:
                params = m.get("params", {})
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
        if not args.dry_run and args.emit_artifacts == "on":
            (outdir / "recommended_space.json").write_text(json.dumps(recommended, ensure_ascii=False, indent=2), encoding="utf-8")
            if importance_dump:
                (outdir / "importance.json").write_text(json.dumps(importance_dump, ensure_ascii=False, indent=2), encoding="utf-8")

        result["assumptions"].append(f"status={status_note}")
        result["assumptions"].append(f"reduction_strategy={used_strategy}")

    # アーティファクト出力
    if not args.dry_run and args.emit_artifacts == "on":
        (outdir / "plan_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # MLflow（存在時のみ）
    run_id = emit_to_mlflow(result, {
        "spec": args.spec, "invalid": args.invalid or "",
        "time_budget": args.time_budget, "max_combos": args.max_combos,
        "gpu_type": args.gpu_type, "cost_unit": args.cost_unit, "gpu_share": args.gpu_share,
        "status": status_note
    })
    if run_id:  # 画面＆ログにも載せる
        result["mlflow_run_id"] = run_id

    # 構造化ログ(JSONL)
    try:
        logline = {
            "ts": time.time(),
            "phase": "P1.2",
            "status": status_note,
            "host": socket.gethostname(),
            "git_rev": subprocess.run(["git","rev-parse","--short","HEAD"], capture_output=True, text=True).stdout.strip() or "",
            "versions": _versions(),
            "mlflow_run_id": run_id or "",
            "result": result,
            "modelwise": modelwise,
            "args": {
                "spec": args.spec, "invalid": args.invalid or "",
                "time_budget": args.time_budget, "max_combos": args.max_combos,
                "gpu_type": args.gpu_type, "cost_unit": args.cost_unit, "gpu_share": args.gpu_share
            }
        }
        if not args.dry_run and args.emit_artifacts == "on":
            with (outdir / "planning.log.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(logline, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 表示
    if args.status_format == "text":
        print(f"trials={result['estimated_trials']} cost_usd={result['estimated_cost_usd']} status={status_note}")
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
