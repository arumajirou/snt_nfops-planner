"""dm_tester.py - Diebold-Mariano検定"""
import numpy as np
from scipy import stats
from loguru import logger
from nfops_eval.models import TestResult


class DMTester:
    """Diebold-Mariano tester"""
    def __init__(self, h: int = 1):
        """
        Args:
            h: Forecast horizon for HAC variance
        """
        self.h = h
    def test(
        self,
        errors_a: np.ndarray,
        errors_b: np.ndarray
    ) -> TestResult:
        """Diebold-Mariano test"""
        logger.info("Running DM test...")
        # Loss differential
        d = errors_a**2 - errors_b**2  # Squared error loss
        # Mean differential
        d_mean = np.mean(d)
        # Variance (simplified - no HAC for now)
        d_var = np.var(d, ddof=1)
        n = len(d)
        # DM statistic
        if d_var > 0:
            dm_stat = d_mean / np.sqrt(d_var / n)
            # Two-tailed test
            pvalue = 2 * (1 - stats.t.cdf(np.abs(dm_stat), df=n-1))
            # Determine preference
            significant = pvalue < 0.05
            logger.info(f"DM statistic: {dm_stat:.4f}, p-value: {pvalue:.4f}")
        else:
            logger.warning("Zero variance in loss differential")
            dm_stat = 0.0
            pvalue = 1.0
            significant = False
        return TestResult(
            test_name="diebold_mariano",
            statistic=dm_stat,
            pvalue=pvalue,
            significant=significant
        )
