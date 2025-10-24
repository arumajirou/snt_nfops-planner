"""
mlflow_emitter.py - MLflow記録
"""
from typing import Dict, Any
import mlflow
from loguru import logger


class MlflowEmitter:
    """MLflowへの計画結果送出"""
    
    def __init__(self, tracking_uri: str, experiment_name: str = "nfops-planning"):
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
    
    def emit(self, params: Dict[str, Any], metrics: Dict[str, Any], tags: Dict[str, str]):
        """計画結果をMLflowに記録"""
        logger.info("Emitting results to MLflow...")
        
        with mlflow.start_run(run_name="planning-run"):
            # Parameters
            for key, value in params.items():
                mlflow.log_param(f"planning.{key}", value)
            
            # Metrics
            for key, value in metrics.items():
                mlflow.log_metric(f"planning.{key}", value)
            
            # Tags
            tags["phase"] = "planning"
            mlflow.set_tags(tags)
            
            logger.success("MLflow emission completed")
```

---

### 🔵 推定器（`nfops_planner/estimators/`）
```
nfops_planner/estimators/
│
├─ __init__.py
├─ cost_time_estimator.py       # 時間・コスト推定
├─ space_recommender.py         # 探索空間縮約
└─ meta_learner.py              # メタ学習（重要度推定）