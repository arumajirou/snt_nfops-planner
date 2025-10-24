"""inverse_restorer.py - 逆変換"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from loguru import logger


class InverseRestorer:
    """Y inverse transformation"""
    def __init__(self, transform_meta_path: Path):
        """
        Args:
            transform_meta_path: Path to y_transform.json
        """
        self.transform_meta_path = Path(transform_meta_path)
        self.meta = self._load_meta()
    def _load_meta(self) -> dict:
        """Load transformation metadata"""
        if not self.transform_meta_path.exists():
            logger.warning(f"Transform meta not found: {self.transform_meta_path}")
            return {'y_type': 'raw', 'series_state': []}
        with open(self.transform_meta_path, encoding='utf-8') as f:
            meta = json.load(f)
        logger.info(f"Loaded transform meta: y_type={meta.get('y_type')}")
        return meta
    def inverse(self, pred_df: pd.DataFrame) -> pd.DataFrame:
        """Apply inverse transformation"""
        logger.info("Applying inverse transformation...")
        df = pred_df.copy()
        y_type = self.meta.get('y_type', 'raw')
        if y_type == 'raw':
            # No transformation
            df['y_hat_original'] = df['y_hat']
        elif y_type == 'diff':
            # Inverse diff
            # Build state map
            state_map = {}
            for state in self.meta.get('series_state', []):
                uid = state['unique_id']
                state_map[uid] = state.get('last_y', 0)
            # Apply inverse
            df['y_hat_original'] = df.apply(
                lambda row: row['y_hat'] + state_map.get(row['unique_id'], 0),
                axis=1
            )
        elif y_type == 'cumsum':
            # Inverse cumsum (diff)
            df['y_hat_original'] = df.groupby('unique_id')['y_hat'].diff().fillna(df['y_hat'])
        else:
            logger.warning(f"Unknown y_type: {y_type}, no inverse applied")
            df['y_hat_original'] = df['y_hat']
        logger.success("Inverse transformation completed")
        return df
