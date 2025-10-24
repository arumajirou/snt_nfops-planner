"""metric_computer.py - 指標計算"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_eval.models import EvalMetrics


class MetricComputer:
    """Metric computer"""
ECHO is on.
    def compute(self, df: pd.DataFrame) -> EvalMetrics:
        """Compute evaluation metrics"""
        logger.info("Computing metrics...")
ECHO is on.
        y_true = df['y'].values
        y_pred = df['y_hat'].values
ECHO is on.
        # SMAPE
        epsilon = 1e-8
        smape = 2 * np.mean(
            np.abs(y_pred - y_true) / 
            (np.abs(y_pred) + np.abs(y_true) + epsilon)
        ) * 100
ECHO is on.
        # MAE
        mae = np.mean(np.abs(y_pred - y_true))
ECHO is on.
        # RMSE
        rmse = np.sqrt(np.mean((y_pred - y_true)**2))
ECHO is on.
        # MAPE
        mape = np.mean(
            np.abs((y_true - y_pred) / (y_true + epsilon))
        ) * 100
ECHO is on.
        metrics = EvalMetrics(
            smape=smape,
            mae=mae,
            rmse=rmse,
            mape=mape
        )
ECHO is on.
        logger.info(f"SMAPE: {smape:.2f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        return metrics
ECHO is on.
    def compute_by_group(
        self,
        df: pd.DataFrame,
        group_col: str
    ) -> pd.DataFrame:
        """Compute metrics by group"""
        logger.info(f"Computing metrics by {group_col}...")
ECHO is on.
        results = []
ECHO is on.
        for group_val, group_df in df.groupby(group_col):
            metrics = self.compute(group_df)
ECHO is on.
            results.append({
                group_col: group_val,
                'n': len(group_df),
                **metrics.to_dict()
            })
ECHO is on.
        return pd.DataFrame(results)
