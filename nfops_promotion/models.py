"""Data models for promotion"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Stage(Enum):
    """Model stage"""
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


@dataclass
class GateDecision:
    """Gate check decision"""
    passed: bool
    reason: str
    metrics: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "reason": self.reason,
            "metrics": self.metrics
        }


@dataclass
class ModelVersion:
    """Model version info"""
    name: str
    version: int
    stage: str
    run_id: str
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "stage": self.stage,
            "run_id": self.run_id
        }


@dataclass
class PromotionResult:
    """Promotion result"""
    model_name: str
    version: int
    stage: str
    gate_decision: GateDecision
    artifacts_bundled: List[str]
