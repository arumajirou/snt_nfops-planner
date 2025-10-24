"""metric_computer.py - 指標計算"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_eval.models import EvalMetrics


class MetricComputer:
    """Metric computer"""
    def compute(self, df: pd.DataFrame) -> EvalMetrics:
        """Compute evaluation metrics"""
        logger.info("Computing metrics...")
        y_true = df['y'].values
        y_pred = df['y_hat'].values
        # SMAPE
        epsilon = 1e-8
        smape = 2 * np.mean(
            np.abs(y_pred - y_true) / 
            (np.abs(y_pred) + np.abs(y_true) + epsilon)
        ) * 100
        # MAE
        mae = np.mean(np.abs(y_pred - y_true))
        # RMSE
        rmse = np.sqrt(np.mean((y_pred - y_true)**2))
        # MAPE
        mape = np.mean(
            np.abs((y_true - y_pred) / (y_true + epsilon))
        ) * 100
        metrics = EvalMetrics(
            smape=smape,
            mae=mae,
            rmse=rmse,
            mape=mape
        )
        logger.info(f"SMAPE: {smape:.2f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        return metrics
    def compute_by_group(
        self,
        df: pd.DataFrame,
        group_col: str
    ) -> pd.DataFrame:
        """Compute metrics by group"""
        logger.info(f"Computing metrics by {group_col}...")
        results = []
        for group_val, group_df in df.groupby(group_col):
            metrics = self.compute(group_df)
            results.append({
                group_col: group_val,
                'n': len(group_df),
                **metrics.to_dict()
            })
        return pd.DataFrame(results)
