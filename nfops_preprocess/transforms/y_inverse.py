"""y_inverse.py - 逆変換"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_preprocess.models import YTransformMeta
from nfops_preprocess.exceptions import InverseError


class YInverseRestorer:
    """Y逆変換"""
    def __init__(self, meta: YTransformMeta):
        self.meta = meta
    def inverse(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform"""
        logger.info(f"Applying inverse: {self.meta.y_type}")
        df = df.copy()
        if self.meta.y_type == 'raw':
            df['y_restored'] = df['y_transformed']
        elif self.meta.y_type == 'diff':
            # State lookup
            state_map = {s.unique_id: s for s in self.meta.series_state}
            for uid, group in df.groupby('unique_id'):
                if uid not in state_map:
                    raise InverseError(f"No state for {uid}")
                state = state_map[uid]
                # Cumulative sum with initial value
                restored = group['y_transformed'].cumsum() + state.last_y
                df.loc[group.index, 'y_restored'] = restored
        elif self.meta.y_type == 'rolling_sum':
            logger.warning("rolling_sum inverse not yet implemented")
            df['y_restored'] = df['y_transformed']
        elif self.meta.y_type == 'cumsum':
            # Diff
            df['y_restored'] = df.groupby('unique_id')['y_transformed'].diff()
        else:
            raise InverseError(f"Unknown y_type: {self.meta.y_type}")
        logger.success("Inverse completed")
        return df
