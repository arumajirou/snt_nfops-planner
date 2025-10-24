"""Data models for prediction"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class PredictionResult:
    """Prediction result"""
    df: pd.DataFrame  # Long format predictions
    quantiles: Optional[List[float]] = None
    distribution: Optional[str] = None
    scenario_id: str = "base"
    run_id: str = "unknown"


@dataclass
class CalibrationMetrics:
    """Calibration metrics"""
    coverage_80: float
    coverage_90: float
    coverage_95: float
    pinball_losses: Dict[float, float]
    crps: Optional[float] = None
    nll: Optional[float] = None
ECHO is on.
    def to_dict(self) -> Dict:
        return {
            "coverage_80": self.coverage_80,
            "coverage_90": self.coverage_90,
            "coverage_95": self.coverage_95,
            "pinball_losses": self.pinball_losses,
            "crps": self.crps,
            "nll": self.nll
        }
