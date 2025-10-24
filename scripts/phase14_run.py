# scripts/phase14_run.py
from __future__ import annotations
import os, json, time
from pathlib import Path
from src.phase14.connectors.mlflow_connector import load_latest_phase13_artifacts
from src.phase14.normalizer import normalize, save_json
from src.phase14.summarizer import build_summary
from src.phase14.indexer import build_index
from src.phase14.publisher import publish_portal

def main():
    now = time.strftime("%Y%m%d%H%M%S")
    reason = os.getenv("PHASE14_REASON", "portal")
    batch_id = f"{now}-{reason}"
    out_dir = Path("outputs/phase14")/batch_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Source収集（最小：Phase13成果物があれば利用）
    p13 = load_latest_phase13_artifacts()
    eval = json.loads(p13.get("eval.json","{}") or "{}") if "eval.json" in p13 else {}
    gate = json.loads(p13.get("gatekeeper.json","{}") or "{}") if "gatekeeper.json" in p13 else {}
    plan = json.loads(p13.get("plan_summary.json","{}") or "{}") if "plan_summary.json" in p13 else {}
    smape = float(eval.get("sMAPE", 0.18))
    register = gate.get("register","unknown")
    est_trials = plan.get("estimated_trials", 8)
    est_gpu = plan.get("estimated_gpu_hours", 0.5)

    # 2) 正規化
    norm = normalize({
        "batch_id": batch_id,
        "metrics": {"valid_SMAPE": smape},
        "text": f"Batch {batch_id}: sMAPE={smape}, register={register}",
        "refs": {"phase13_dir": p13.get("latest_dir","N/A")}
    })
    save_json(out_dir/"normalized.json", {k:v for k,v in norm.__dict__.items()})

    # 3) 要約（ルール→固定テンプレ）
    summary = build_summary({
        "batch_id": batch_id, "register": register, "smape": smape,
        "smape_max": 0.20, "estimated_trials": est_trials,
        "estimated_gpu_hours": est_gpu, "ref_dir": p13.get("latest_dir","N/A")
    })
    (out_dir/"summary.md").write_text(summary, encoding="utf-8")

    # 4) インデックス
    from src.phase14.normalizer import NormalizedItem
    idx_size = build_index(NormalizedItem(**json.loads((out_dir/"normalized.json").read_text("utf-8"))), out_dir)

    # 5) ポータル発行（Markdown）
    portal_payload = {
        "batch_id": batch_id, "model_name": norm.key.get("model_name","unknown"),
        "model_version": norm.key.get("model_version","unknown"),
        "smape": smape, "register": register, "ref_dir": p13.get("latest_dir","N/A"),
        "summary": summary
    }
    page = publish_portal(portal_payload, Path("ops/portals"), Path("ops/portals/index.md"))

    # 6) メトリクス
    save_json(out_dir/"metrics.json", {
        "knowledge_posts": 1, "search_hits": 0, "summarize_latency_ms": 0,
        "index_size_docs": idx_size, "sync_errors": 0
    })

    # 7) MLflow（任意）
    try:
        if os.getenv("MLFLOW_TRACKING_URI") and os.getenv("PHASE14_EMIT_MLFLOW","false").lower()=="true":
            import mlflow
            mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
            with mlflow.start_run(run_name="phase14_portal"):
                mlflow.log_metrics({"index_size_docs": idx_size, "knowledge_posts": 1})
                mlflow.log_artifacts(str(out_dir))
    except Exception as e:
        print("[phase14] mlflow logging skipped:", e)

    print("[phase14] portal:", page)

if __name__ == "__main__":
    main()
