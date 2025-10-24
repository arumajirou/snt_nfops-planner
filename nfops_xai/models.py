"""Data models for XAI"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class WorstCase:
    """Worst case information"""
    unique_id: str
    ds: str
    y: float
    y_hat: float
    error: float
    abs_error: float
    rank: int


@dataclass
class FeatureImportance:
    """Feature importance result"""
    feature: str
    importance: float
    method: str
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    def to_dict(self) -> Dict:
        return {
            "feature": self.feature,
            "importance": self.importance,
            "method": self.method,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high
        }


@dataclass
class XAIMetrics:
    """XAI metrics"""
    n_features: int
    n_worst_cases: int
    xai_build_sec: float
    top_features: List[str]
