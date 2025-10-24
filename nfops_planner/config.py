"""設定管琁E""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class PlannerConfig(BaseModel):
    """プランナ�E設宁E""
    spec_dir: Path = Field(default=Path("data/specs"))
    output_dir: Path = Field(default=Path("plan"))
    log_dir: Path = Field(default=Path("logs"))
    mlflow_tracking_uri: Optional[str] = Field(default="http://localhost:5000")
    max_combos: int = Field(default=500, ge=1)
    time_budget_hours: float = Field(default=12.0, gt=0)
    gpu_type: str = Field(default="A100")
    cost_per_gpu_hour: float = Field(default=3.5, ge=0)
