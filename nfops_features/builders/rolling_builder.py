"""rolling_builder.py - 移動統計特徴"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import List, Dict


class RollingBuilder:
    """Rolling statistics builder"""
ECHO is on.
    def __init__(self, rolling_specs: List[Dict]):
        """
        Args:
            rolling_specs: List of {window: int, ops: [str]}
        """
        self.rolling_specs = rolling_specs or []
ECHO is on.
    def build(self, df: pd.DataFrame, target_col: str = 'y_scaled') -> pd.DataFrame:
        """Build rolling features"""
        logger.info(f"Building rolling features: {len^(self.rolling_specs^)} specs")
ECHO is on.
        df = df.copy()
ECHO is on.
        for spec in self.rolling_specs:
            window = spec.get('window')
            ops = spec.get('ops', ['mean'])
ECHO is on.
            for op in ops:
                col_name = f'h_r{window}_{op}_{target_col}'
ECHO is on.
                if op == 'mean':
                    df[col_name] = df.groupby('unique_id')[target_col].rolling(
                        window=window, min_periods=window, closed='left'
                    ).mean().reset_index(level=0, drop=True)
ECHO is on.
                elif op == 'std':
                    df[col_name] = df.groupby('unique_id')[target_col].rolling(
                        window=window, min_periods=window, closed='left'
                    ).std().reset_index(level=0, drop=True)
ECHO is on.
                elif op == 'min':
                    df[col_name] = df.groupby('unique_id')[target_col].rolling(
                        window=window, min_periods=window, closed='left'
                    ).min().reset_index(level=0, drop=True)
ECHO is on.
                elif op == 'max':
                    df[col_name] = df.groupby('unique_id')[target_col].rolling(
                        window=window, min_periods=window, closed='left'
                    ).max().reset_index(level=0, drop=True)
ECHO is on.
                logger.debug(f"Created: {col_name}")
ECHO is on.
        logger.success(f"Built rolling features")
        return df
ECHO is on.
    def build_ema(self, df: pd.DataFrame, spans: List[int], target_col: str = 'y_scaled') -> pd.DataFrame:
        """Build EMA features"""
        logger.info(f"Building EMA features: {len^(spans^)} spans")
ECHO is on.
        df = df.copy()
ECHO is on.
        for span in spans:
            col_name = f'h_ema{span}_{target_col}'
            df[col_name] = df.groupby('unique_id')[target_col].ewm(
                span=span, adjust=False
            ).mean().reset_index(level=0, drop=True)
            logger.debug(f"Created: {col_name}")
ECHO is on.
        logger.success(f"Built {len^(spans^)} EMA features")
        return df
