"""dm_tester.py - Diebold-Mariano検定"""
import numpy as np
from scipy import stats
from loguru import logger
from nfops_eval.models import TestResult


class DMTester:
    """Diebold-Mariano tester"""
ECHO is on.
    def __init__(self, h: int = 1):
        """
        Args:
            h: Forecast horizon for HAC variance
        """
        self.h = h
ECHO is on.
    def test(
        self,
        errors_a: np.ndarray,
        errors_b: np.ndarray
    ) -> TestResult:
        """Diebold-Mariano test"""
        logger.info("Running DM test...")
ECHO is on.
        # Loss differential
        d = errors_a**2 - errors_b**2  # Squared error loss
ECHO is on.
        # Mean differential
        d_mean = np.mean(d)
ECHO is on.
        # Variance (simplified - no HAC for now)
        d_var = np.var(d, ddof=1)
        n = len(d)
ECHO is on.
        # DM statistic
        if d_var > 0:
            dm_stat = d_mean / np.sqrt(d_var / n)
ECHO is on.
            # Two-tailed test
            pvalue = 2 * (1 - stats.t.cdf(np.abs(dm_stat), df=n-1))
ECHO is on.
            # Determine preference
            significant = pvalue < 0.05
ECHO is on.
            logger.info(f"DM statistic: {dm_stat:.4f}, p-value: {pvalue:.4f}")
        else:
            logger.warning("Zero variance in loss differential")
            dm_stat = 0.0
            pvalue = 1.0
            significant = False
ECHO is on.
        return TestResult(
            test_name="diebold_mariano",
            statistic=dm_stat,
            pvalue=pvalue,
            significant=significant
        )
