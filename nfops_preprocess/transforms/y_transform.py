"""y_transform.py - Y変換の適用と逆変換"""
import pandas as pd
import numpy as np
from typing import Tuple
from loguru import logger
from nfops_preprocess.models import Split, YTransformMeta, SeriesState
from nfops_preprocess.exceptions import NonFiniteError


class YTransformApplier:
    """Y変換適用"""
    def __init__(self, y_type: str, window: int = None, period: int = None):
        """
        Args:
            y_type: raw/diff/rolling_sum/cumsum/seasonal_diff
            window: Window size for rolling_sum
            period: Period for seasonal_diff
        """
        self.y_type = y_type
        self.window = window
        self.period = period
    def apply(
        self, 
        df: pd.DataFrame, 
        split: Split
    ) -> Tuple[pd.DataFrame, YTransformMeta]:
        """Apply transformation"""
        logger.info(f"Applying y_type={self.y_type}")
        df = df.copy()
        series_states = []
        if self.y_type == 'raw':
            df['y_transformed'] = df['y']
        elif self.y_type == 'diff':
            df['y_transformed'] = df.groupby('unique_id')['y'].diff()
            # State: last_y
            train_mask, _, _ = split.get_mask(df['ds'])
            for uid, group in df[train_mask].groupby('unique_id'):
                last_row = group.iloc[-1]
                series_states.append(SeriesState(
                    unique_id=uid,
                    last_train_ds=last_row['ds'],
                    last_y=last_row['y']
                ))
        elif self.y_type == 'rolling_sum':
            if self.window is None:
                raise ValueError("window is required for rolling_sum")
            df['y_transformed'] = df.groupby('unique_id')['y'].rolling(
                window=self.window, min_periods=self.window
            ).sum().reset_index(level=0, drop=True)
            # State: buffer
            train_mask, _, _ = split.get_mask(df['ds'])
            for uid, group in df[train_mask].groupby('unique_id'):
                last_row = group.iloc[-1]
                buffer = group['y'].iloc[-self.window:].tolist()
                series_states.append(SeriesState(
                    unique_id=uid,
                    last_train_ds=last_row['ds'],
                    buffer=buffer
                ))
        elif self.y_type == 'cumsum':
            df['y_transformed'] = df.groupby('unique_id')['y'].cumsum()
            # State: base_cumsum
            train_mask, _, _ = split.get_mask(df['ds'])
            for uid, group in df[train_mask].groupby('unique_id'):
                last_row = group.iloc[-1]
                series_states.append(SeriesState(
                    unique_id=uid,
                    last_train_ds=last_row['ds'],
                    base_cumsum=last_row['y_transformed']
                ))
        else:
            raise ValueError(f"Unknown y_type: {self.y_type}")
        # Check non-finite
        non_finite = df['y_transformed'].isna().sum() + np.isinf(df['y_transformed']).sum()
        if non_finite > 0:
            logger.warning(f"Non-finite values: {non_finite}")
        meta = YTransformMeta(
            version="1.0.0",
            y_type=self.y_type,
            window=self.window,
            period=self.period,
            anchor_ds=split.train_end,
            series_state=series_states
        )
        logger.success(f"Transform applied: {self.y_type}")
        return df, meta
