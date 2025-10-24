"""Data models for monitoring"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DriftResult:
    """Drift detection result"""
    feature: str
    psi: float
    ks_statistic: Optional[float] = None
    ks_pvalue: Optional[float] = None
    alert_level: str = "ok"  # ok, warning, critical
    
    def to_dict(self) -> Dict:
        return {
            "feature": self.feature,
            "psi": self.psi,
            "ks_statistic": self.ks_statistic,
            "ks_pvalue": self.ks_pvalue,
            "alert_level": self.alert_level
        }


@dataclass
class AccuracyMetrics:
    """Rolling accuracy metrics"""
    window: str
    smape: float
    mae: float
    delta_pct: float
    alert_level: str = "ok"


@dataclass
class CoverageMetrics:
    """Coverage metrics"""
    alpha: float
    coverage: float
    nominal: float
    gap: float
    alert_level: str = "ok"


@dataclass
class MonitorAlert:
    """Monitor alert"""
    ts: str
    level: str
    model_name: str
    model_version: int
    signals: List[Dict]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "ts": self.ts,
            "level": self.level,
            "model": {
                "name": self.model_name,
                "version": self.model_version
            },
            "signals": self.signals,
            "recommendations": self.recommendations
        }
