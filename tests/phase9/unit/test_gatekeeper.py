"""test_gatekeeper.py"""
import pytest
from nfops_promotion.core.gatekeeper import Gatekeeper


class TestGatekeeper:
    def test_pass_all_checks(self):
        """Test gate check passes"""
        gatekeeper = Gatekeeper()
        
        metrics = {
            'delta_smape': -1.5,
            'coverage_90': 0.90,
            'dm_pvalue': 0.018
        }
        
        decision = gatekeeper.check(metrics)
        
        assert decision.passed is True
        assert "All checks passed" in decision.reason
    
    def test_fail_smape(self):
        """Test gate check fails on SMAPE"""
        gatekeeper = Gatekeeper()
        
        metrics = {
            'delta_smape': 0.5,  # Positive = worse
            'coverage_90': 0.90,
            'dm_pvalue': 0.018
        }
        
        decision = gatekeeper.check(metrics)
        
        assert decision.passed is False
        assert "SMAPE improvement insufficient" in decision.reason
    
    def test_fail_coverage(self):
        """Test gate check fails on coverage"""
        gatekeeper = Gatekeeper()
        
        metrics = {
            'delta_smape': -1.5,
            'coverage_90': 0.80,  # Too low
            'dm_pvalue': 0.018
        }
        
        decision = gatekeeper.check(metrics)
        
        assert decision.passed is False
        assert "Coverage out of range" in decision.reason
