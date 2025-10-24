# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .spec_loader import load_spec, naive_count_combos, SpecError
from .cost_time_estimator import estimate_trial_seconds, aggregate_cost

def _parse_time_budget(s: str) -> int:
    # accepts "12h", "30m", "3600s"
    s = s.strip().lower()
    if s.endswith("h"): return int(float(s[:-1]) * 3600)
    if s.endswith("m"): return int(float(s[:-1]) * 60)
    if s.endswith("s"): return int(float(s[:-1]))
    return int(float(s))  # seconds

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Planner Dry-run (Phase 1 minimal)")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--invalid", default=None)  # reserved for Phase 1.1
    ap.add_argument("--time-budget", default="12h")
    ap.add_argument("--max-combos", type=int, default=500)
    ap.add_argument("--gpu-type", default="A100")  # reserved
    ap.add_argument("--cost-unit", type=float, default=3.5)
    ap.add_argument("--gpu-share", type=float, default=1.0)
    ap.add_argument("--out-dir", default="plan")
    args = ap.parse_args(argv)

    try:
        spec = load_spec(args.spec)
    except SpecError as e:
        print(str(e), file=sys.stderr)
        return 2

    combos = 0
    sec_hat = 0.0
    for m in spec["_active_models"]:
        c = naive_count_combos(m)
        combos += c
        sec_hat = max(sec_hat, estimate_trial_seconds(m))  # pessimistic: use the slowest per trial

    agg = aggregate_cost(combos, sec_hat, args.gpu_share, args.cost_unit)
    result = {
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
            "invalid_table=ignored(Phase1-min)",
        ],
    }

    outdir = Path(args.out_dir); outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"plan_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    # MLflow emit は Phase 1.1 で追加
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
