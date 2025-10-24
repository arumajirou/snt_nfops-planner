"""residual_monitor.py - 残差監視"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_monitor.models import AccuracyMetrics


class ResidualMonitor:
    """Residual and accuracy monitor"""
    
    def __init__(
        self,
        increase_pct_warning: float = 10.0,
        increase_pct_critical: float = 20.0
    ):
        """
        Args:
            increase_pct_warning: Warning threshold (%)
            increase_pct_critical: Critical threshold (%)
        """
        self.increase_pct_warning = increase_pct_warning
        self.increase_pct_critical = increase_pct_critical
    
    def calculate_smape(
        self,
        y_true: pd.Series,
        y_pred: pd.Series
    ) -> float:
        """Calculate SMAPE"""
        
        # Remove NaN
        mask = ~(y_true.isna() | y_pred.isna())
        y_true = y_true[mask]
        y_pred = y_pred[mask]
        
        if len(y_true) == 0:
            return 0.0
        
        numerator = np.abs(y_true - y_pred)
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
        
        # Avoid division by zero
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        smape = 100 * np.mean(numerator / denominator)
        
        return smape
    
    def calculate_mae(
        self,
        y_true: pd.Series,
        y_pred: pd.Series
    ) -> float:
        """Calculate MAE"""
        
        mask = ~(y_true.isna() | y_pred.isna())
        y_true = y_true[mask]
        y_pred = y_pred[mask]
        
        if len(y_true) == 0:
            return 0.0
        
        mae = np.mean(np.abs(y_true - y_pred))
        
        return mae
    
    def monitor(
        self,
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame,
        y_col: str = 'y',
        y_hat_col: str = 'y_hat'
    ) -> AccuracyMetrics:
        """Monitor accuracy metrics"""
        logger.info("Monitoring accuracy metrics")
        
        # Calculate reference metrics
        ref_smape = self.calculate_smape(
            reference_df[y_col],
            reference_df[y_hat_col]
        )
        ref_mae = self.calculate_mae(
            reference_df[y_col],
            reference_df[y_hat_col]
        )
        
        # Calculate current metrics
        cur_smape = self.calculate_smape(
            current_df[y_col],
            current_df[y_hat_col]
        )
        cur_mae = self.calculate_mae(
            current_df[y_col],
            current_df[y_hat_col]
        )
        
        # Calculate delta
        if ref_smape > 0:
            delta_pct = ((cur_smape - ref_smape) / ref_smape) * 100
        else:
            delta_pct = 0.0
        
        # Determine alert level
        if delta_pct >= self.increase_pct_critical:
            alert_level = "critical"
        elif delta_pct >= self.increase_pct_warning:
            alert_level = "warning"
        else:
            alert_level = "ok"
        
        metrics = AccuracyMetrics(
            window="7d",
            smape=cur_smape,
            mae=cur_mae,
            delta_pct=delta_pct,
            alert_level=alert_level
        )
        
        logger.info(
            f"Accuracy: SMAPE={cur_smape:.2f} (ref={ref_smape:.2f}, "
            f"delta={delta_pct:+.1f}%) | level={alert_level}"
        )
        
        return metrics
