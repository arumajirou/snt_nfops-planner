"""Data models for evaluation"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class EvalMetrics:
    """Evaluation metrics"""
    smape: float
    mae: float
    rmse: float
    mape: Optional[float] = None
    crps: Optional[float] = None
    def to_dict(self) -> Dict:
        return {
            "smape": self.smape,
            "mae": self.mae,
            "rmse": self.rmse,
            "mape": self.mape,
            "crps": self.crps
        }


@dataclass
class TestResult:
    """Statistical test result"""
    test_name: str
    statistic: float
    pvalue: float
    significant: bool
    effect_size: Optional[float] = None
    def to_dict(self) -> Dict:
        return {
            "test": self.test_name,
            "statistic": self.statistic,
            "pvalue": self.pvalue,
            "significant": self.significant,
            "effect_size": self.effect_size
        }


@dataclass
class ComparisonResult:
    """Model comparison result"""
    model_a: str
    model_b: str
    metrics_a: EvalMetrics
    metrics_b: EvalMetrics
    tests: List[TestResult]
    rank: int = 0
