"""multicomp.py - 多重比較補正"""
import numpy as np
from loguru import logger
from typing import List


class MultiCompCorrector:
    """Multiple comparison corrector"""
    def benjamini_hochberg(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Benjamini-Hochberg FDR correction"""
        logger.info(f"Applying BH correction with alpha={alpha}")
        m = len(pvalues)
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
        for i in range(m-1, -1, -1):
            if i == m - 1:
                adjusted[i] = sorted_pvals[i]
            else:
                adjusted[i] = min(
                    adjusted[i+1],
                    sorted_pvals[i] * m / (i + 1)
                )
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
        return adj_pvalues
    def holm(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Holm correction"""
        logger.info(f"Applying Holm correction with alpha={alpha}")
        m = len(pvalues)
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
        for i in range(m):
            adjusted[i] = sorted_pvals[i] * (m - i)
        # Enforce monotonicity
        for i in range(1, m):
            adjusted[i] = max(adjusted[i], adjusted[i-1])
        # Clip at 1.0
        adjusted = np.minimum(adjusted, 1.0)
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
        return adj_pvalues
