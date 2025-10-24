# dags/retrain_dag.py - Phase 13: 再学習オーケストレーション（Airflow DAG）
# 仕様: Phase 11のアラート等をトリガに、12ステップを順次実行
# 参照仕様: Phase 13 詳細（生成物/メトリクス/ID設計/ステップ定義）,
#           共通フェーズ（batch_id命名/MLflow・Registry連携）
"""
一次情報:
- Phase 13 再学習DAG（生成物: dags/retrain_dag.py, flows/retrain_flow.py, matrix/production_retrain.yaml）
- batch_id = {YYYYMMDDhhmmss}-{reason}-{hash}
- メトリクス: retrain_trigger_reason, retrain_elapsed_sec, n_trials_executed, cost_usd, co2_eq_kg, status
"""
from __future__ import annotations
import os, json, hashlib, time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except Exception:
    # Airflow未導入環境でもimport時に即死しないための軽量フォールバック
    DAG = object
    PythonOperator = object

# ---- ユーティリティ ----
ARTIFACT_DIR = Path(os.getenv("PHASE13_ARTIFACT_DIR", "outputs/phase13")).resolve()
MATRIX_PATH  = Path(os.getenv("PHASE13_MATRIX_PATH", "matrix/production_retrain.yaml")).resolve()
MLFLOW_URI   = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
REASON       = os.getenv("PHASE13_REASON", "alert")
NOW_TS       = datetime.utcnow().strftime("%Y%m%d%H%M%S")

def _mk_batch_id(reason: str, payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    h   = hashlib.sha1(raw).hexdigest()[:8]
    return f"{NOW_TS}-{reason}-{h}"

def _log_mlflow(metrics: dict, params: dict | None = None, tags: dict | None = None):
    try:
        import mlflow
        mlflow.set_tracking_uri(MLFLOW_URI)
        with mlflow.start_run(run_name="phase13_retrain", nested=False):
            if params:
                mlflow.log_params(params)
            if metrics:
                mlflow.log_metrics(metrics)
            if tags:
                for k, v in tags.items():
                    mlflow.set_tag(k, v)
    except Exception as e:
        # MLflowが無くてもDAG自体は進行させる
        print(f"[phase13] mlflow logging skipped: {e}")

# ---- 各ステップのダミー実装（最小: 可観測性/契約の骨格） ----
def s1_drift_check(**ctx):
    payload = ctx.get("params", {}).get("alert_payload", {"dummy":"true"})
    batch_id = _mk_batch_id(REASON, payload)
    out = ARTIFACT_DIR / batch_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "trigger_context.json").write_text(json.dumps({
        "batch_id": batch_id, "reason": REASON, "payload": payload
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    _log_mlflow(
        metrics={"retrain_elapsed_sec": 0.0},
        tags={"batch_id": batch_id, "retrain_trigger_reason": REASON, "phase":"S1-DriftCheck"}
    )
    return {"batch_id": batch_id}

def s2_model_check(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S1_DriftCheck") or {}
    batch_id = x["batch_id"]
    # 最小: go判定固定（将来は直近kバッチ劣化/予算確認） 
    decision = {"decision":"go","models":["AutoNBEATS","AutoNHITS"]}
    (ARTIFACT_DIR / x["batch_id"] / "model_check.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    _log_mlflow(tags={"batch_id": batch_id, "phase":"S2-ModelCheck"})
    return {**x, **decision}

def s3_build_matrix(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S2_ModelCheck") or {}
    batch_id = x["batch_id"]
    # 本番用マトリクスをそのまま採用（必要ならサブセット/近傍抽出）
    assert MATRIX_PATH.exists(), f"matrix not found: {MATRIX_PATH}"
    target = ARTIFACT_DIR / batch_id / "production_retrain.yaml"
    target.write_text(MATRIX_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    _log_mlflow(tags={"batch_id": batch_id, "phase":"S3-BuildMatrix"})
    return x

def s4_plan_dry(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S3_BuildMatrix") or {}
    batch_id = x["batch_id"]
    # 最小の見積り（将来: Phase1のドライランを呼び出し）
    estimate = {
        "estimated_trials": 8,
        "estimated_gpu_hours": 0.5,
        "estimated_wallclock_hours": 0.7,
        "space_reduction_rate": 0.42,
        "status": "OK",
        "time_budget_hours": 12
    }
    (ARTIFACT_DIR / batch_id / "plan_summary.json").write_text(
        json.dumps(estimate, indent=2), encoding="utf-8")
    _log_mlflow(metrics={
        "planning.estimated_trials": estimate["estimated_trials"],
        "planning.estimated_gpu_hours": estimate["estimated_gpu_hours"],
        "planning.estimated_wallclock_hours": estimate["estimated_wallclock_hours"],
        "planning.space_reduction_rate": estimate["space_reduction_rate"]
    }, tags={"batch_id": batch_id, "phase":"S4-Plan"})
    return x

def _touch(batch_id: str, name: str):
    p = ARTIFACT_DIR / batch_id / name
    p.write_text(f"ok:{name}", encoding="utf-8")

def s5_data_feature(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S4_PlanDry") or {}
    _touch(x["batch_id"], "features_ready.marker")
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S5-DataFeature"})
    return x

def s6_train_hpo(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S5_DataFeature") or {}
    _touch(x["batch_id"], "train_done.marker")
    _log_mlflow(metrics={"n_trials_executed": 8}, tags={"batch_id": x["batch_id"], "phase":"S6-TrainHPO"})
    return x

def s7_predict(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S6_TrainHPO") or {}
    _touch(x["batch_id"], "predictions.parquet")  # ここではマーカーのみ
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S7-Predict"})
    return x

def s8_evaluate(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S7_Predict") or {}
    (ARTIFACT_DIR / x["batch_id"] / "eval.json").write_text(json.dumps({"sMAPE": 0.18}, indent=2), "utf-8")
    _log_mlflow(metrics={"eval.sMAPE": 0.18}, tags={"batch_id": x["batch_id"], "phase":"S8-Evaluate"})
    return x

def s9_gatekeeper(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S8_Evaluate") or {}
    (ARTIFACT_DIR / x["batch_id"] / "gatekeeper.json").write_text(json.dumps({"register":"yes"}, indent=2), "utf-8")
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S9-Gatekeeper"})
    return x

def s10_register(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S9_Gatekeeper") or {}
    _touch(x["batch_id"], "registry_registered.marker")
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S10-Register"})
    return x

def s11_notify(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S10_Register") or {}
    _touch(x["batch_id"], "notified.marker")
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S11-Notify"})
    return x

def s12_cleanup(**ctx):
    x = ctx["ti"].xcom_pull(task_ids="S11_Notify") or {}
    _touch(x["batch_id"], "cleanup.marker")
    _log_mlflow(tags={"batch_id": x["batch_id"], "phase":"S12-Cleanup"})
    return x

# ---- DAG 定義（Airflow 環境でのみ有効） ----
default_args = {"owner": "phase13", "retries": 0, "depends_on_past": False}
if DAG is not object:
    with DAG(
        dag_id="phase13_retrain",
        start_date=datetime(2025, 1, 1),
        schedule_interval=None,
        default_args=default_args,
        catchup=False,
        max_active_runs=1,
        dagrun_timeout=timedelta(hours=6),
        tags=["phase13","retrain","mlops"]
    ) as dag:
        t1 = PythonOperator(task_id="S1_DriftCheck", python_callable=s1_drift_check, op_kwargs={})
        t2 = PythonOperator(task_id="S2_ModelCheck", python_callable=s2_model_check)
        t3 = PythonOperator(task_id="S3_BuildMatrix", python_callable=s3_build_matrix)
        t4 = PythonOperator(task_id="S4_PlanDry",   python_callable=s4_plan_dry)
        t5 = PythonOperator(task_id="S5_DataFeature", python_callable=s5_data_feature)
        t6 = PythonOperator(task_id="S6_TrainHPO",    python_callable=s6_train_hpo)
        t7 = PythonOperator(task_id="S7_Predict",     python_callable=s7_predict)
        t8 = PythonOperator(task_id="S8_Evaluate",    python_callable=s8_evaluate)
        t9 = PythonOperator(task_id="S9_Gatekeeper",  python_callable=s9_gatekeeper)
        t10= PythonOperator(task_id="S10_Register",   python_callable=s10_register)
        t11= PythonOperator(task_id="S11_Notify",     python_callable=s11_notify)
        t12= PythonOperator(task_id="S12_Cleanup",    python_callable=s12_cleanup)
        t1>>t2>>t3>>t4>>t5>>t6>>t7>>t8>>t9>>t10>>t11>>t12
