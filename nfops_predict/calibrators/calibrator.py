"""calibrator.py - 後校正"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional
from sklearn.isotonic import IsotonicRegression


class Calibrator:
    """Prediction calibrator"""
ECHO is on.
    def __init__(self, method: str = 'isotonic'):
        """
        Args:
            method: Calibration method (isotonic/quantile_map/conformal)
        """
        self.method = method
        self.isotonic_model = None
ECHO is on.
    def fit(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        quantile: float = 0.5
    ):
        """Fit calibrator on validation data"""
        logger.info(f"Fitting calibrator: {self.method}")
ECHO is on.
        if self.method == 'isotonic':
            self.isotonic_model = IsotonicRegression(out_of_bounds='clip')
            self.isotonic_model.fit(y_pred, y_true)
            logger.success("Isotonic calibrator fitted")
ECHO is on.
    def calibrate(
        self,
        pred_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply calibration"""
        logger.info(f"Applying calibration: {self.method}")
ECHO is on.
        df = pred_df.copy()
ECHO is on.
        if self.method == 'isotonic' and self.isotonic_model:
            # Apply isotonic regression
            df['y_hat_calibrated'] = self.isotonic_model.transform(df['y_hat'])
            logger.success("Calibration applied")
        else:
            # No calibration
            df['y_hat_calibrated'] = df['y_hat']
ECHO is on.
        return df
ECHO is on.
    def compute_coverage(
        self,
        y_true: np.ndarray,
        pi_lower: np.ndarray,
        pi_upper: np.ndarray
    ) -> float:
        """Compute empirical coverage"""
        in_interval = (y_true >= pi_lower) & (y_true <= pi_upper)
        coverage = in_interval.mean()
        return coverage
