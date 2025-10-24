"""pi_constructor.py - 予測区間構築"""
import pandas as pd
from loguru import logger


class PIConstructor:
    """Prediction Interval Constructor"""
ECHO is on.
    def __init__(self, alpha: float = 0.1):
        """
        Args:
            alpha: Significance level (default 0.1 for 90%% PI)
        """
        self.alpha = alpha
ECHO is on.
    def construct_from_quantiles(
        self,
        pred_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Construct PI from quantiles"""
        logger.info(f"Constructing PI with alpha={self.alpha}")
ECHO is on.
        # Pivot to get quantiles as columns
        pivot = pred_df.pivot_table(
            index=['unique_id', 'ds', 'scenario_id', 'run_id', 'model'],
            columns='q',
            values='y_hat',
            aggfunc='first'
        ).reset_index()
ECHO is on.
        # Calculate PI bounds
        lower_q = self.alpha / 2
        upper_q = 1 - self.alpha / 2
ECHO is on.
        # Find closest quantiles
        quantiles = [c for c in pivot.columns if isinstance(c, float)]
ECHO is on.
        if len(quantiles) >= 3:
            pivot['pi_lower'] = pivot[min(quantiles)]
            pivot['pi_upper'] = pivot[max(quantiles)]
            pivot['median'] = pivot[0.5] if 0.5 in quantiles else pivot[quantiles[len(quantiles)//2]]
ECHO is on.
            logger.success(f"Constructed PI for {len^(pivot^)} predictions")
        else:
            logger.warning("Insufficient quantiles for PI construction")
ECHO is on.
        return pivot
