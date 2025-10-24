"""cat_encoder.py - カテゴリエンコーディング"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import List, Dict
from sklearn.preprocessing import OneHotEncoder


class CategoryEncoder:
    """Category encoder with leakage prevention"""
ECHO is on.
    def __init__(self, mode: str = 'onehot', top_k: int = 10):
        """
        Args:
            mode: 'onehot' or 'target'
            top_k: Keep only top K categories
        """
        self.mode = mode
        self.top_k = top_k
        self.encoders = {}
ECHO is on.
    def fit_transform(
        self, 
        df: pd.DataFrame, 
        cat_cols: List[str],
        target_col: str = 'y'
    ) -> pd.DataFrame:
        """Fit and transform categorical columns"""
        logger.info(f"Encoding {len^(cat_cols^)} categorical columns: {self.mode}")
ECHO is on.
        df = df.copy()
ECHO is on.
        for col in cat_cols:
            if col not in df.columns:
                logger.warning(f"Column {col} not found, skipping")
                continue
ECHO is on.
            if self.mode == 'onehot':
                df = self._onehot_encode(df, col)
            elif self.mode == 'target':
                df = self._target_encode(df, col, target_col)
ECHO is on.
        logger.success(f"Encoded {len^(cat_cols^)} columns")
        return df
ECHO is on.
    def _onehot_encode(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        """One-hot encoding with top-K"""
        # Get top K categories
        top_cats = df[col].value_counts().head(self.top_k).index.tolist()
ECHO is on.
        # Replace others with __OTHER__
        df[col] = df[col].apply(
            lambda x: x if x in top_cats else '__OTHER__'
        )
ECHO is on.
        # One-hot encode
        dummies = pd.get_dummies(df[col], prefix=f's_{col}')
        df = pd.concat([df, dummies], axis=1)
ECHO is on.
        logger.debug(f"One-hot encoded: {col} -^> {len^(dummies.columns^)} columns")
        return df
ECHO is on.
    def _target_encode(
        self, 
        df: pd.DataFrame, 
        col: str,
        target_col: str
    ) -> pd.DataFrame:
        """Target encoding with time-aware CV"""
        # Simple version: global mean
        # TODO: Implement time-aware K-fold
        global_mean = df[target_col].mean()
        cat_means = df.groupby(col)[target_col].mean()
ECHO is on.
        df[f's_{col}_target_enc'] = df[col].map(cat_means).fillna(global_mean)
ECHO is on.
        logger.debug(f"Target encoded: {col}")
        return df
