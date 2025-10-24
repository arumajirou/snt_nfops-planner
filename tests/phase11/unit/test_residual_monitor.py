"""test_residual_monitor.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_monitor.detectors.residual_monitor import ResidualMonitor


class TestResidualMonitor:
    def test_smape_calculation(self):
        """Test SMAPE calculation"""
        monitor = ResidualMonitor()
        
        y_true = pd.Series([100, 110, 105])
        y_pred = pd.Series([98, 112, 103])
        
        smape = monitor.calculate_smape(y_true, y_pred)
        
        # SMAPE should be reasonable
        assert 0 <= smape <= 100
    
    def test_accuracy_degradation(self):
        """Test accuracy degradation detection"""
        monitor = ResidualMonitor(increase_pct_critical=20.0)
        
        # Reference: good predictions
        ref_df = pd.DataFrame({
            'y': [100, 110, 105, 115],
            'y_hat': [99, 111, 104, 116]
        })
        
        # Current: worse predictions
        cur_df = pd.DataFrame({
            'y': [100, 110, 105, 115],
            'y_hat': [90, 120, 95, 125]
        })
        
        metrics = monitor.monitor(ref_df, cur_df)
        
        # Should detect degradation
        assert metrics.delta_pct > 0
