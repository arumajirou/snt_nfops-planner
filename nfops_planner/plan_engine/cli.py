# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
from typing import Any, Dict

from .spec_loader import load_spec, naive_count_combos, SpecError
from .cost_time_estimator import estimate_trial_seconds, aggregate_cost
from .invalid_loader import compile_rules, count_with_invalid, expand_param_values
from .mlflow_emitter import emit_to_mlflow

def _parse_time_budget(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("h"): return int(float(s[:-1]) * 3600)
    if s.endswith("m"): return int(float(s[:-1]) * 60)
    if s.endswith("s"): return int(float(s[:-1]))
    return int(float(s))  # seconds

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Planner Dry-run (Phase 1.1)")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--invalid", default=None, help="invalid rules yaml")
    ap.add_argument("--time-budget", default="12h", help="e.g. 12h, 30m, 3600s")
    ap.add_argument("--max-combos", type=int, default=200000, help="exact invalid filtering cap")
    ap.add_argument("--gpu-type", default="A100")
    ap.add_argument("--cost-unit", type=float, default=3.5, help="USD per GPU hour")
    ap.add_argument("--gpu-share", type=float, default=1.0, help="fraction of 1 GPU")
    ap.add_argument("--out-dir", default="plan")
    args = ap.parse_args(argv)

    # spec load
    try:
        spec = load_spec(args.spec)
    except SpecError as e:
        print(str(e), file=sys.stderr)
        return 2

    # invalid compile
    compiled = []
    invalid_file_present = False
    if args.invalid:
        p = Path(args.invalid)
        if p.exists():
            import yaml
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            compiled = compile_rules(raw)
            invalid_file_present = True
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
        sec_hat = max(sec_hat, estimate_trial_seconds(m))  # pessimistic per-trial
        modelwise.append({
            "name": m.get("name",""),
            "naive": int(naive),
            "valid": int(valid),
            "invalid": int(invalid),
            "applied": bool(applied),
        })

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

    outdir = Path(args.out_dir); outdir.mkdir(parents=True, exist_ok=True)

    # 予算超過→縮約案（最大カーディナリティ param を 30% トリム）
    status_note = "OK"
    recommended = {"models": []}
    if agg["total_sec"] > time_budget_sec:
        status_note = "EXCEEDS_BUDGET"
        reduced_total = 0
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
            trimmed = vals[:keep]
            new_params = dict(params)
            new_params[kmax] = trimmed
            recommended["models"].append({"name": m.get("name",""), "params": new_params})
            from .spec_loader import naive_count_combos as _n
            reduced_total += _n({"params": new_params})
        result["space_reduction_rate"] = round(1.0 - (reduced_total / max(1, combos)), 3)
        (outdir / "recommended_space.json").write_text(
            json.dumps(recommended, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        result["assumptions"].append(f"status={status_note}")
        result["assumptions"].append("reduction_strategy=trim_top30pct_by_max_cardinality")

    # 生成物出力
    (outdir / "plan_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 構造化ログ（JSONL 1行追記）
    try:
        logline = {
            "ts": time.time(),
            "status": status_note,
            "result": result,
            "modelwise": modelwise,
            "args": {
                "spec": args.spec, "invalid": args.invalid or "",
                "time_budget": args.time_budget, "max_combos": args.max_combos,
                "gpu_type": args.gpu_type, "cost_unit": args.cost_unit, "gpu_share": args.gpu_share
            }
        }
        with (outdir / "planning.log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(logline, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # MLflow（存在時のみ）
    _ = emit_to_mlflow(result, {
        "spec": args.spec, "invalid": args.invalid or "",
        "time_budget": args.time_budget, "max_combos": args.max_combos,
        "gpu_type": args.gpu_type, "cost_unit": args.cost_unit, "gpu_share": args.gpu_share,
        "status": status_note
    })

    # stdout は契約JSON
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
