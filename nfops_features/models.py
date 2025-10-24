"""Data models for feature engineering"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class FeatSpec:
    """Feature specification"""
    hist: Dict[str, Any]
    calendar: List[str]
    price: Optional[Dict[str, Any]] = None
    promo: Optional[Dict[str, Any]] = None
    stat: Optional[List[str]] = None
    futr: Optional[List[str]] = None


@dataclass
class FeatureCatalog:
    """Feature catalog metadata"""
    version: str
    features: List[Dict[str, Any]]
    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "features": self.features
        }


@dataclass
class QualityReport:
    """Feature quality metrics"""
    n_features: int
    na_introduced_rate: float
    const_feature_count: int
    high_corr_pairs: int
    cardinality_issues: List[str]
