"""gatekeeper.py - 昇格条件チェック"""
from loguru import logger
from typing import Dict
from nfops_promotion.models import GateDecision


class Gatekeeper:
    """Gate keeper for model promotion"""
    
    def __init__(
        self,
        min_smape_improvement: float = -1.0,
        coverage_range: tuple = (0.87, 0.93),
        max_pvalue: float = 0.05
    ):
        """
        Args:
            min_smape_improvement: Minimum SMAPE improvement (negative)
            coverage_range: Acceptable coverage range
            max_pvalue: Maximum p-value for statistical tests
        """
        self.min_smape_improvement = min_smape_improvement
        self.coverage_range = coverage_range
        self.max_pvalue = max_pvalue
    
    def check(
        self,
        metrics: Dict[str, float]
    ) -> GateDecision:
        """Check if model passes gate"""
        logger.info("Running gate check...")
        
        reasons = []
        passed = True
        
        # Check SMAPE improvement
        smape_delta = metrics.get('delta_smape', 0.0)
        if smape_delta > self.min_smape_improvement:
            reasons.append(
                f"SMAPE improvement insufficient: {smape_delta:.2f} > {self.min_smape_improvement}"
            )
            passed = False
        else:
            logger.success(f"SMAPE improvement OK: {smape_delta:.2f}")
        
        # Check coverage
        coverage = metrics.get('coverage_90', 0.0)
        if not (self.coverage_range[0] <= coverage <= self.coverage_range[1]):
            reasons.append(
                f"Coverage out of range: {coverage:.3f} not in "
                f"[{self.coverage_range[0]}, {self.coverage_range[1]}]"
            )
            passed = False
        else:
            logger.success(f"Coverage OK: {coverage:.3f}")
        
        # Check statistical test
        dm_pvalue = metrics.get('dm_pvalue', 1.0)
        if dm_pvalue > self.max_pvalue:
            reasons.append(
                f"DM test not significant: p={dm_pvalue:.4f} > {self.max_pvalue}"
            )
            passed = False
        else:
            logger.success(f"DM test OK: p={dm_pvalue:.4f}")
        
        reason = "; ".join(reasons) if reasons else "All checks passed"
        
        decision = GateDecision(
            passed=passed,
            reason=reason,
            metrics=metrics
        )
        
        if passed:
            logger.success("Gate check PASSED")
        else:
            logger.error(f"Gate check FAILED: {reason}")
        
        return decision
