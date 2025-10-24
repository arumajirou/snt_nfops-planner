"""test_drift_detector.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_monitor.detectors.drift_detector import DriftDetector


class TestDriftDetector:
    def test_psi_no_drift(self):
        """Test PSI with no drift"""
        detector = DriftDetector()
        
        # Same distribution
        ref = pd.Series(np.random.normal(0, 1, 1000))
        cur = pd.Series(np.random.normal(0, 1, 1000))
        
        psi = detector.calculate_psi(ref, cur)
        
        # PSI should be small
        assert psi < 0.1
    
    def test_psi_with_drift(self):
        """Test PSI with drift"""
        detector = DriftDetector()
        
        # Different distributions
        ref = pd.Series(np.random.normal(0, 1, 1000))
        cur = pd.Series(np.random.normal(2, 1, 1000))  # Mean shift
        
        psi = detector.calculate_psi(ref, cur)
        
        # PSI should be large
        assert psi > 0.25
    
    def test_ks_test(self):
        """Test KS test"""
        detector = DriftDetector()
        
        ref = pd.Series(np.random.normal(0, 1, 1000))
        cur = pd.Series(np.random.normal(2, 1, 1000))
        
        statistic, pvalue = detector.ks_test(ref, cur)
        
        # Should detect difference
        assert pvalue < 0.01
