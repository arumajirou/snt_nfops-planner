"""coverage_tester.py - 被覆率検定"""
import numpy as np
from scipy import stats
from loguru import logger
from nfops_eval.models import TestResult


class CoverageTester:
    """Coverage tester using binomial test"""
    def test(
        self,
        y_true: np.ndarray,
        pi_lower: np.ndarray,
        pi_upper: np.ndarray,
        nominal_coverage: float = 0.9
    ) -> TestResult:
        """Test coverage with binomial test"""
        logger.info(f"Testing coverage (nominal={nominal_coverage})...")
        # Check if within interval
        in_interval = (y_true >= pi_lower) & (y_true <= pi_upper)
        n = len(y_true)
        k = int(in_interval.sum())
        # Empirical coverage
        empirical_coverage = k / n
        # Binomial test
        binom_test = stats.binomtest(
            k=k,
            n=n,
            p=nominal_coverage,
            alternative='two-sided'
        )
        pvalue = binom_test.pvalue
        significant = pvalue < 0.05
        # Coverage gap
        coverage_gap = empirical_coverage - nominal_coverage
        logger.info(
            f"Empirical coverage: {empirical_coverage:.3f}, "
            f"Gap: {coverage_gap:+.3f}, p-value: {pvalue:.4f}"
        )
        return TestResult(
            test_name="coverage_binomial",
            statistic=coverage_gap,
            pvalue=pvalue,
            significant=significant,
            effect_size=coverage_gap
        )
