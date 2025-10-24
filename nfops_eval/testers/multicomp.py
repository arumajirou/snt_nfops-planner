"""multicomp.py - ���d��r�␳"""
import numpy as np
from loguru import logger
from typing import List


class MultiCompCorrector:
    """Multiple comparison corrector"""
ECHO �� <ON> �ł��B
    def benjamini_hochberg(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Benjamini-Hochberg FDR correction"""
        logger.info(f"Applying BH correction with alpha={alpha}")
ECHO �� <ON> �ł��B
        m = len(pvalues)
ECHO �� <ON> �ł��B
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
ECHO �� <ON> �ł��B
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
ECHO �� <ON> �ł��B
        for i in range(m-1, -1, -1):
            if i == m - 1:
                adjusted[i] = sorted_pvals[i]
            else:
                adjusted[i] = min(
                    adjusted[i+1],
                    sorted_pvals[i] * m / (i + 1)
                )
ECHO �� <ON> �ł��B
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
ECHO �� <ON> �ł��B
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
ECHO �� <ON> �ł��B
        return adj_pvalues
ECHO �� <ON> �ł��B
    def holm(
        self,
        pvalues: np.ndarray,
        alpha: float = 0.05
    ) -> np.ndarray:
        """Holm correction"""
        logger.info(f"Applying Holm correction with alpha={alpha}")
ECHO �� <ON> �ł��B
        m = len(pvalues)
ECHO �� <ON> �ł��B
        # Sort p-values
        sorted_idx = np.argsort(pvalues)
        sorted_pvals = pvalues[sorted_idx]
ECHO �� <ON> �ł��B
        # Calculate adjusted p-values
        adjusted = np.zeros(m)
ECHO �� <ON> �ł��B
        for i in range(m):
            adjusted[i] = sorted_pvals[i] * (m - i)
ECHO �� <ON> �ł��B
        # Enforce monotonicity
        for i in range(1, m):
            adjusted[i] = max(adjusted[i], adjusted[i-1])
ECHO �� <ON> �ł��B
        # Clip at 1.0
        adjusted = np.minimum(adjusted, 1.0)
ECHO �� <ON> �ł��B
        # Restore original order
        adj_pvalues = np.zeros(m)
        adj_pvalues[sorted_idx] = adjusted
ECHO �� <ON> �ł��B
        n_rejected = np.sum(adj_pvalues <= alpha)
        logger.info(f"Rejected {n_rejected}/{m} null hypotheses")
ECHO �� <ON> �ł��B
        return adj_pvalues
