"""
設定管理
"""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class PlannerConfig(BaseModel):
    """プランナー設定"""
    
    # パス設定
    spec_dir: Path = Field(default=Path("data/specs"))
    invalid_dir: Path = Field(default=Path("data/invalid_tables"))
    output_dir: Path = Field(default=Path("plan"))
    log_dir: Path = Field(default=Path("logs"))
    
    # MLflow設定
    mlflow_tracking_uri: Optional[str] = Field(default="http://localhost:5000")
    mlflow_experiment_name: str = Field(default="nfops-planning")
    
    # 実行制約
    max_combos: int = Field(default=500, ge=1)
    time_budget_hours: float = Field(default=12.0, gt=0)
    max_gpu_hours: Optional[float] = Field(default=None)
    
    # GPU設定
    gpu_type: str = Field(default="A100")
    cost_per_gpu_hour: float = Field(default=3.5, ge=0)
    
    # 推定器設定
    estimator_min_samples: int = Field(default=10)
    confidence_level: float = Field(default=0.95, ge=0, le=1)
    
    # 縮約設定
    space_reduction_target: float = Field(default=0.42, ge=0, le=1)
    importance_threshold: float = Field(default=0.05, ge=0, le=1)
`