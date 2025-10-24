"""test_y_transform.py"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from nfops_preprocess.transforms.y_transform import YTransformApplier
from nfops_preprocess.transforms.y_inverse import YInverseRestorer
from nfops_preprocess.models import Split


class TestYTransform:
    @pytest.fixture
    def sample_df(self):
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        return pd.DataFrame({
            'unique_id': ['A'] * 10,
            'ds': dates,
            'y': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        })
    @pytest.fixture
    def simple_split(self, sample_df):
        return Split(
            train_end=pd.to_datetime('2024-01-07'),
            valid_end=pd.to_datetime('2024-01-09'),
            test_end=pd.to_datetime('2024-01-10')
        )
    def test_raw_transform(self, sample_df, simple_split):
        """Raw transform"""
        applier = YTransformApplier('raw')
        df_t, meta = applier.apply(sample_df, simple_split)
        assert 'y_transformed' in df_t.columns
        assert (df_t['y_transformed'] == df_t['y']).all()
    def test_diff_transform_inverse(self, sample_df, simple_split):
        """Diff transform and inverse"""
        applier = YTransformApplier('diff')
        df_t, meta = applier.apply(sample_df, simple_split)
        # Check diff
        assert df_t['y_transformed'].iloc[1] == 1.0  # 11-10
        # Inverse
        restorer = YInverseRestorer(meta)
        # Simulate prediction
        df_pred = df_t[df_t['ds'] > simple_split.train_end].copy()
        df_pred = restorer.inverse(df_pred)
        assert 'y_restored' in df_pred.columns
