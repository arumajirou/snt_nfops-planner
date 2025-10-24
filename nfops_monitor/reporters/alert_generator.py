"""alert_generator.py - アラート生成"""
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import List
from nfops_monitor.models import MonitorAlert, DriftResult, AccuracyMetrics, CoverageMetrics


class AlertGenerator:
    """Alert generator"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        drift_results: List[DriftResult],
        accuracy_metrics: AccuracyMetrics,
        coverage_metrics: CoverageMetrics,
        model_name: str = "sales_demand_D",
        model_version: int = 27,
        filename: str = "alert.json"
    ):
        """Generate alert JSON"""
        logger.info("Generating alert")
        
        # Collect signals
        signals = []
        
        # Drift signals
        for result in drift_results:
            if result.alert_level in ["warning", "critical"]:
                signal = {
                    "type": "data_drift",
                    "feature": result.feature,
                    "psi": result.psi,
                    "ks_p": result.ks_pvalue
                }
                signals.append(signal)
        
        # Accuracy signal
        if accuracy_metrics.alert_level in ["warning", "critical"]:
            signal = {
                "type": "accuracy_drop",
                "metric": "rolling_sMAPE_7d",
                "delta_pct": accuracy_metrics.delta_pct
            }
            signals.append(signal)
        
        # Coverage signal
        if coverage_metrics.alert_level in ["warning", "critical"]:
            signal = {
                "type": "coverage_gap",
                "alpha": coverage_metrics.alpha,
                "gap_pt": coverage_metrics.gap
            }
            signals.append(signal)
        
        # Determine overall level
        if any(s.get("type") == "data_drift" for s in signals) or \
           accuracy_metrics.alert_level == "critical" or \
           coverage_metrics.alert_level == "critical":
            level = "critical"
        elif signals:
            level = "warning"
        else:
            level = "ok"
        
        # Generate recommendations
        recommendations = []
        
        if any(s.get("type") == "data_drift" for s in signals):
            recommendations.append(
                "Phase 4: Review feature engineering (scaling/binning)"
            )
        
        if accuracy_metrics.alert_level in ["warning", "critical"]:
            recommendations.append(
                "Phase 5: Consider warm-start HPO or retraining"
            )
        
        if coverage_metrics.alert_level in ["warning", "critical"]:
            recommendations.append(
                "Phase 6: Review conformal calibration"
            )
        
        if not recommendations:
            recommendations.append("Continue monitoring")
        
        # Create alert
        alert = MonitorAlert(
            ts=datetime.now().isoformat(),
            level=level,
            model_name=model_name,
            model_version=model_version,
            signals=signals,
            recommendations=recommendations
        )
        
        # Save
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(alert.to_dict(), f, indent=2)
        
        logger.success(f"Alert saved: {output_path}")
        logger.info(f"Alert level: {level} | Signals: {len(signals)}")
