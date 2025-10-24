"""multicomp.py - 多重比較補正"""
import numpy as np
from loguru import logger
from typing import List


class MultiCompCorrector:
    """Multiple comparison corrector"""
ECHO は <ON> です。
    def benjamini_hochberg(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Benjamini-Hochberg FDR correction"""
        logger.info(f"Applying BH correction with alpha={alpha}")
ECHO は <ON> です。
        m = len(pvalues)
ECHO は <ON> です。
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
ECHO は <ON> です。
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
ECHO は <ON> です。
        for i in range(m-1, -1, -1):
            if i == m - 1:
                adjusted[i] = sorted_pvals[i]
            else:
                adjusted[i] = min(
                    adjusted[i+1],
                    sorted_pvals[i] * m / (i + 1)
                )
ECHO は <ON> です。
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
ECHO は <ON> です。
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
ECHO は <ON> です。
        return adj_pvalues
ECHO は <ON> です。
    def holm(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Holm correction"""
        logger.info(f"Applying Holm correction with alpha={alpha}")
ECHO は <ON> です。
        m = len(pvalues)
ECHO は <ON> です。
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
ECHO は <ON> です。
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
ECHO は <ON> です。
        for i in range(m):
            adjusted[i] = sorted_pvals[i] * (m - i)
ECHO は <ON> です。
        # Enforce monotonicity
        for i in range(1, m):
            adjusted[i] = max(adjusted[i], adjusted[i-1])
ECHO は <ON> です。
        # Clip at 1.0
        adjusted = np.minimum(adjusted, 1.0)
ECHO は <ON> です。
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
ECHO は <ON> です。
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
ECHO は <ON> です。
        return adj_pvalues
