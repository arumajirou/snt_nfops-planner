"""effect_size.py - 効果量計算"""
import numpy as np
from loguru import logger


class EffectSizeEstimator:
    """Effect size estimator"""
ECHO is on.
    def cliffs_delta(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Cliff's delta effect size"""
        logger.debug("Computing Cliff's delta...")
ECHO is on.
        n_a = len(a)
        n_b = len(b)
ECHO is on.
        # Count dominance
        dominance = 0
        for a_val in a:
            dominance += np.sum(a_val > b) - np.sum(a_val < b)
ECHO is on.
        delta = dominance / (n_a * n_b)
ECHO is on.
        logger.debug(f"Cliff's delta: {delta:.4f}")
        return delta
ECHO is on.
    def vargha_delaney_a12(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Vargha-Delaney A12 effect size"""
        logger.debug("Computing A12...")
ECHO is on.
        n_a = len(a)
        n_b = len(b)
ECHO is on.
        # Count wins
        wins = 0
        for a_val in a:
            wins += np.sum(a_val > b) + 0.5 * np.sum(a_val == b)
ECHO is on.
        a12 = wins / (n_a * n_b)
ECHO is on.
        logger.debug(f"A12: {a12:.4f}")
        return a12
ECHO is on.
    def hedges_g(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:
        """Hedges' g effect size"""
        logger.debug("Computing Hedges' g...")
ECHO is on.
        n_a = len(a)
        n_b = len(b)
ECHO is on.
        mean_a = np.mean(a)
        mean_b = np.mean(b)
ECHO is on.
        var_a = np.var(a, ddof=1)
        var_b = np.var(b, ddof=1)
ECHO is on.
        # Pooled standard deviation
        pooled_std = np.sqrt(
            ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
        )
ECHO is on.
        if pooled_std > 0:
            g = (mean_a - mean_b) / pooled_std
ECHO is on.
            # Small sample correction
            correction = 1 - 3 / (4 * (n_a + n_b) - 9)
            g = g * correction
        else:
            g = 0.0
ECHO is on.
        logger.debug(f"Hedges' g: {g:.4f}")
        return g
