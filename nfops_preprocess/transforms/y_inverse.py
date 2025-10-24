"""y_inverse.py - 逆変換"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_preprocess.models import YTransformMeta
from nfops_preprocess.exceptions import InverseError


class YInverseRestorer:
    """Y逆変換"""
ECHO is on.
    def __init__(self, meta: YTransformMeta):
        self.meta = meta
ECHO is on.
    def inverse(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform"""
        logger.info(f"Applying inverse: {self.meta.y_type}")
ECHO is on.
        df = df.copy()
ECHO is on.
        if self.meta.y_type == 'raw':
            df['y_restored'] = df['y_transformed']
ECHO is on.
        elif self.meta.y_type == 'diff':
            # State lookup
            state_map = {s.unique_id: s for s in self.meta.series_state}
ECHO is on.
            for uid, group in df.groupby('unique_id'):
                if uid not in state_map:
                    raise InverseError(f"No state for {uid}")
ECHO is on.
                state = state_map[uid]
                # Cumulative sum with initial value
                restored = group['y_transformed'].cumsum() + state.last_y
                df.loc[group.index, 'y_restored'] = restored
ECHO is on.
        elif self.meta.y_type == 'rolling_sum':
            logger.warning("rolling_sum inverse not yet implemented")
            df['y_restored'] = df['y_transformed']
ECHO is on.
        elif self.meta.y_type == 'cumsum':
            # Diff
            df['y_restored'] = df.groupby('unique_id')['y_transformed'].diff()
ECHO is on.
        else:
            raise InverseError(f"Unknown y_type: {self.meta.y_type}")
ECHO is on.
        logger.success("Inverse completed")
        return df
