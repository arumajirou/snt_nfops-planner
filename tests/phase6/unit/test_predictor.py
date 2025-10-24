"""test_predictor.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_predict.predictors.predictor import Predictor


class TestPredictor:
    @pytest.fixture
    def sample_df(self):
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = []
        for sid in ['A', 'B']:
            for date in dates:
                data.append({
                    'unique_id': sid,
                    'ds': date,
                    'y_scaled': np.random.randn()
                })
        return pd.DataFrame(data)
ECHO is on.
    def test_predict_quantiles(self, sample_df):
        """Test quantile prediction"""
        predictor = Predictor(
            model=None,
            hparams={'h': 7, 'model': 'Test'}
        )
ECHO is on.
        result = predictor.predict_quantiles(
            df=sample_df,
            quantiles=[0.1, 0.5, 0.9],
            scenario_id="test"
        )
ECHO is on.
        assert result.df is not None
        assert 'y_hat' in result.df.columns
        assert 'q' in result.df.columns
        assert len(result.df['q'].unique()) == 3
ECHO is on.
    def test_predict_point(self, sample_df):
        """Test point prediction"""
        predictor = Predictor(
            model=None,
            hparams={'h': 7, 'model': 'Test'}
        )
ECHO is on.
        result = predictor.predict_point(
            df=sample_df,
            scenario_id="test"
        )
ECHO is on.
        assert result.df is not None
        assert len(result.df['q'].unique()) == 1
