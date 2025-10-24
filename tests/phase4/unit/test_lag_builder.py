"""test_lag_builder.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_features.builders.lag_builder import LagBuilder


class TestLagBuilder:
    @pytest.fixture
    def sample_df(self):
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        return pd.DataFrame({
            'unique_id': ['A'] * 10,
            'ds': dates,
            'y_scaled': range(10)
        })
ECHO is on.
    def test_regular_lag(self, sample_df):
        """Test regular lag"""
        builder = LagBuilder(lags=[1, 2])
        result = builder.build(sample_df)
ECHO is on.
        assert 'h_lag_1_y_scaled' in result.columns
        assert 'h_lag_2_y_scaled' in result.columns
        assert pd.isna(result['h_lag_1_y_scaled'].iloc[0])
        assert result['h_lag_1_y_scaled'].iloc[1] == 0
ECHO is on.
    def test_seasonal_lag(self, sample_df):
        """Test seasonal lag"""
        builder = LagBuilder(lags=[], seasonal_lags=[7])
        result = builder.build(sample_df)
ECHO is on.
        assert 'h_lag_s7_y_scaled' in result.columns
        assert result['h_lag_s7_y_scaled'].iloc[7] == 0
ECHO is on.
    def test_cold_start_flag(self, sample_df):
        """Test cold start flag"""
        builder = LagBuilder(lags=[2])
        result = builder.build(sample_df)
ECHO is on.
        assert 'is_cold_start' in result.columns
        assert result['is_cold_start'].iloc[0] == True
        assert result['is_cold_start'].iloc[2] == False
