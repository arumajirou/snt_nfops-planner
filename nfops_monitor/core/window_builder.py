"""window_builder.py - ウィンドウ構築"""
import pandas as pd
from loguru import logger
from typing import Tuple


class WindowBuilder:
    """Window builder for reference and current data"""
    
    def __init__(
        self,
        reference_days: int = 90,
        current_days: int = 7
    ):
        """
        Args:
            reference_days: Reference window size in days
            current_days: Current window size in days
        """
        self.reference_days = reference_days
        self.current_days = current_days
    
    def build(
        self,
        df: pd.DataFrame,
        ds_col: str = 'ds'
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Build reference and current windows"""
        logger.info(
            f"Building windows: reference={self.reference_days}d, "
            f"current={self.current_days}d"
        )
        
        # Sort by date
        df = df.sort_values(ds_col)
        
        # Get date range
        max_date = df[ds_col].max()
        
        # Current window: last N days
        current_start = max_date - pd.Timedelta(days=self.current_days)
        current = df[df[ds_col] > current_start].copy()
        
        # Reference window: N days before current
        reference_end = current_start
        reference_start = reference_end - pd.Timedelta(days=self.reference_days)
        reference = df[
            (df[ds_col] > reference_start) & (df[ds_col] <= reference_end)
        ].copy()
        
        logger.success(
            f"Reference: {len(reference)} rows "
            f"({reference[ds_col].min()} to {reference[ds_col].max()})"
        )
        logger.success(
            f"Current: {len(current)} rows "
            f"({current[ds_col].min()} to {current[ds_col].max()})"
        )
        
        return reference, current
