"""calibration_monitor.py - カバレッジ監視"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_monitor.models import CoverageMetrics


class CalibrationMonitor:
    """Calibration and coverage monitor"""
    
    def __init__(
        self,
        gap_critical: float = 5.0
    ):
        """
        Args:
            gap_critical: Critical gap threshold (percentage points)
        """
        self.gap_critical = gap_critical
    
    def calculate_coverage(
        self,
        df: pd.DataFrame,
        y_col: str = 'y',
        q_low_col: str = 'y_hat_q0.1',
        q_high_col: str = 'y_hat_q0.9',
        alpha: float = 0.1
    ) -> float:
        """Calculate empirical coverage"""
        
        # Remove NaN
        mask = ~(df[y_col].isna() | df[q_low_col].isna() | df[q_high_col].isna())
        y = df.loc[mask, y_col]
        q_low = df.loc[mask, q_low_col]
        q_high = df.loc[mask, q_high_col]
        
        if len(y) == 0:
            return 0.0
        
        # Check if y is within [q_low, q_high]
        within = (y >= q_low) & (y <= q_high)
        coverage = within.mean()
        
        return coverage
    
    def monitor(
        self,
        current_df: pd.DataFrame,
        alpha: float = 0.1,
        y_col: str = 'y',
        q_low_col: str = 'y_hat_q0.1',
        q_high_col: str = 'y_hat_q0.9'
    ) -> CoverageMetrics:
        """Monitor coverage metrics"""
        logger.info(f"Monitoring coverage for alpha={alpha}")
        
        # Calculate empirical coverage
        coverage = self.calculate_coverage(
            current_df,
            y_col=y_col,
            q_low_col=q_low_col,
            q_high_col=q_high_col,
            alpha=alpha
        )
        
        # Nominal coverage
        nominal = 1.0 - alpha
        
        # Gap (percentage points)
        gap = abs(coverage - nominal) * 100
        
        # Determine alert level
        if gap >= self.gap_critical:
            alert_level = "critical"
        else:
            alert_level = "ok"
        
        metrics = CoverageMetrics(
            alpha=alpha,
            coverage=coverage,
            nominal=nominal,
            gap=gap,
            alert_level=alert_level
        )
        
        logger.info(
            f"Coverage: {coverage:.3f} (nominal={nominal:.3f}, "
            f"gap={gap:.1f}pt) | level={alert_level}"
        )
        
        return metrics
