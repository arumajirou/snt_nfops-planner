"""effect_size.py - 効果量計算"""
import numpy as np
from loguru import logger


class EffectSizeEstimator:
    """Effect size estimator"""
    def cliffs_delta(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Cliff's delta effect size"""
        logger.debug("Computing Cliff's delta...")
        n_a = len(a)
        n_b = len(b)
        # Count dominance
        dominance = 0
        for a_val in a:
            dominance += np.sum(a_val > b) - np.sum(a_val < b)
        delta = dominance / (n_a * n_b)
        logger.debug(f"Cliff's delta: {delta:.4f}")
        return delta
    def vargha_delaney_a12(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Vargha-Delaney A12 effect size"""
        logger.debug("Computing A12...")
        n_a = len(a)
        n_b = len(b)
        # Count wins
        wins = 0
        for a_val in a:
            wins += np.sum(a_val > b) + 0.5 * np.sum(a_val == b)
        a12 = wins / (n_a * n_b)
        logger.debug(f"A12: {a12:.4f}")
        return a12
    def hedges_g(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Hedges' g effect size"""
        logger.debug("Computing Hedges' g...")
        n_a = len(a)
        n_b = len(b)
        mean_a = np.mean(a)
        mean_b = np.mean(b)
        var_a = np.var(a, ddof=1)
        var_b = np.var(b, ddof=1)
        # Pooled standard deviation
        pooled_std = np.sqrt(
            ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
        )
        if pooled_std > 0:
            g = (mean_a - mean_b) / pooled_std
            # Small sample correction
            correction = 1 - 3 / (4 * (n_a + n_b) - 9)
            g = g * correction
        else:
            g = 0.0
        logger.debug(f"Hedges' g: {g:.4f}")
        return g
