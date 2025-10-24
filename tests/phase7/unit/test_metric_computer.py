"""test_metric_computer.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_eval.metrics.metric_computer import MetricComputer


class TestMetricComputer:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({
            'y': [100, 110, 105, 115, 120],
            'y_hat': [98, 112, 103, 118, 122]
        })
    def test_compute_metrics(self, sample_df):
        """Test metric computation"""
        computer = MetricComputer()
        metrics = computer.compute(sample_df)
        assert metrics.smape > 0
        assert metrics.mae > 0
        assert metrics.rmse > 0
        assert metrics.mape is not None
    def test_perfect_prediction(self):
        """Test with perfect predictions"""
        df = pd.DataFrame({
            'y': [100, 110, 120],
            'y_hat': [100, 110, 120]
        })
        computer = MetricComputer()
        metrics = computer.compute(df)
        assert metrics.mae == 0.0
        assert metrics.rmse == 0.0
