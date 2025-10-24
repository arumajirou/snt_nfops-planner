"""scaler_factory.py - スケーラファクトリ"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.preprocessing import PowerTransformer
from loguru import logger
from nfops_preprocess.models import Split


class ScalerFactory:
    """スケーラファクトリ"""
ECHO is on.
    @staticmethod
    def create(
        scaler_type: str,
        scope: str = 'per_series'
    ):
        """Create scaler"""
        if scaler_type == 'standard':
            return CustomScaler('standard', scope, StandardScaler())
        elif scaler_type == 'robust':
            return CustomScaler('robust', scope, RobustScaler())
        elif scaler_type == 'minmax':
            return CustomScaler('minmax', scope, MinMaxScaler())
        elif scaler_type == 'log1p':
            return Log1pScaler(scope)
        elif scaler_type == 'yeo-johnson':
            return CustomScaler('yeo-johnson', scope, PowerTransformer(method='yeo-johnson'))
        else:
            raise ValueError(f"Unknown scaler_type: {scaler_type}")


class CustomScaler:
    """Custom scaler wrapper"""
ECHO is on.
    def __init__(self, scaler_type: str, scope: str, base_scaler):
        self.scaler_type = scaler_type
        self.scope = scope
        self.base_scaler = base_scaler
        self.series_scalers = {}
ECHO is on.
    def fit(self, df: pd.DataFrame, split: Split):
        """Fit on train only"""
        logger.info(f"Fitting {self.scaler_type} scaler ^({self.scope}^)")
ECHO is on.
        train_mask, _, _ = split.get_mask(df['ds'])
        df_train = df[train_mask]
ECHO is on.
        if self.scope == 'global':
            self.base_scaler.fit(df_train[['y_transformed']].dropna())
        elif self.scope == 'per_series':
            for uid, group in df_train.groupby('unique_id'):
                scaler = self.base_scaler.__class__()
                scaler.fit(group[['y_transformed']].dropna())
                self.series_scalers[uid] = scaler
ECHO is on.
        logger.success("Scaler fitted")
ECHO is on.
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform"""
        df = df.copy()
ECHO is on.
        if self.scope == 'global':
            df['y_scaled'] = self.base_scaler.transform(df[['y_transformed']].fillna(0))
        elif self.scope == 'per_series':
            for uid, group in df.groupby('unique_id'):
                if uid in self.series_scalers:
                    scaled = self.series_scalers[uid].transform(
                        group[['y_transformed']].fillna(0)
                    )
                    df.loc[group.index, 'y_scaled'] = scaled
ECHO is on.
        return df
ECHO is on.
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform"""
        df = df.copy()
ECHO is on.
        if self.scope == 'global':
            df['y_unscaled'] = self.base_scaler.inverse_transform(df[['y_scaled']])
        elif self.scope == 'per_series':
            for uid, group in df.groupby('unique_id'):
                if uid in self.series_scalers:
                    unscaled = self.series_scalers[uid].inverse_transform(
                        group[['y_scaled']]
                    )
                    df.loc[group.index, 'y_unscaled'] = unscaled
ECHO is on.
        return df


class Log1pScaler:
    """Log1p scaler"""
ECHO is on.
    def __init__(self, scope: str = 'per_series'):
        self.scope = scope
        self.offsets = {}
ECHO is on.
    def fit(self, df: pd.DataFrame, split: Split):
        """Fit"""
        logger.info("Fitting log1p scaler")
        train_mask, _, _ = split.get_mask(df['ds'])
        df_train = df[train_mask]
ECHO is on.
        if self.scope == 'per_series':
            for uid, group in df_train.groupby('unique_id'):
                min_val = group['y_transformed'].min()
                if min_val < 0:
                    self.offsets[uid] = -min_val + 1e-8
                else:
                    self.offsets[uid] = 0.0
ECHO is on.
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform"""
        df = df.copy()
ECHO is on.
        for uid, group in df.groupby('unique_id'):
            offset = self.offsets.get(uid, 0.0)
            df.loc[group.index, 'y_scaled'] = np.log1p(
                group['y_transformed'] + offset
            )
ECHO is on.
        return df
ECHO is on.
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inverse"""
        df = df.copy()
ECHO is on.
        for uid, group in df.groupby('unique_id'):
            offset = self.offsets.get(uid, 0.0)
            df.loc[group.index, 'y_unscaled'] = np.expm1(
                group['y_scaled']
            ) - offset
ECHO is on.
        return df
