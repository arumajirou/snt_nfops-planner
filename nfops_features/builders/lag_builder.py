"""lag_builder.py - ラグ特徴生成"""
import pandas as pd
from loguru import logger
from typing import List


class LagBuilder:
    """Lag feature builder"""
ECHO is on.
    def __init__(self, lags: List[int], seasonal_lags: List[int] = None):
        """
        Args:
            lags: Regular lag periods
            seasonal_lags: Seasonal lag periods
        """
        self.lags = lags or []
        self.seasonal_lags = seasonal_lags or []
ECHO is on.
    def build(self, df: pd.DataFrame, target_col: str = 'y_scaled') -> pd.DataFrame:
        """Build lag features"""
        logger.info(f"Building lag features: {len^(self.lags^)} regular, {len^(self.seasonal_lags^)} seasonal")
ECHO is on.
        df = df.copy()
ECHO is on.
        # Regular lags
        for lag in self.lags:
            col_name = f'h_lag_{lag}_{target_col}'
            df[col_name] = df.groupby('unique_id')[target_col].shift(lag)
            logger.debug(f"Created: {col_name}")
ECHO is on.
        # Seasonal lags
        for s_lag in self.seasonal_lags:
            col_name = f'h_lag_s{s_lag}_{target_col}'
            df[col_name] = df.groupby('unique_id')[target_col].shift(s_lag)
            logger.debug(f"Created: {col_name}")
ECHO is on.
        # Cold start flag
        max_lag = max(self.lags + self.seasonal_lags) if (self.lags or self.seasonal_lags) else 0
        if max_lag > 0:
            df['is_cold_start'] = df.groupby('unique_id').cumcount() < max_lag
ECHO is on.
        logger.success(f"Built {len^(self.lags^) + len^(self.seasonal_lags^)} lag features")
        return df
