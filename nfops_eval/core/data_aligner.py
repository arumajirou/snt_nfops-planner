"""data_aligner.py - データ整列"""
import pandas as pd
from loguru import logger
from nfops_eval.exceptions import KeyMismatchError


class DataAligner:
    """Data aligner for predictions and actuals"""
    def align(
        self,
        preds: pd.DataFrame,
        actuals: pd.DataFrame
    ) -> pd.DataFrame:
        """Align predictions with actuals"""
        logger.info("Aligning predictions with actuals...")
        # Check required columns
        pred_cols = set(preds.columns)
        act_cols = set(actuals.columns)
        required_pred = {'unique_id', 'ds', 'y_hat'}
        required_act = {'unique_id', 'ds', 'y'}
        missing_pred = required_pred - pred_cols
        missing_act = required_act - act_cols
        if missing_pred:
            raise KeyMismatchError(f"Missing columns in predictions: {missing_pred}")
        if missing_act:
            raise KeyMismatchError(f"Missing columns in actuals: {missing_act}")
        # For quantile predictions, get median
        if 'q' in preds.columns:
            logger.info("Extracting median prediction (q=0.5)")
            preds_median = preds[preds['q'] == 0.5].copy()
            if len(preds_median) == 0:
                logger.warning("No q=0.5 found, using all predictions")
                preds_median = preds.copy()
        else:
            preds_median = preds.copy()
        # Merge
        merged = preds_median.merge(
            actuals,
            on=['unique_id', 'ds'],
            how='inner',
            suffixes=('_pred', '_act')
        )
        # Calculate error
        merged['error'] = merged['y_hat'] - merged['y']
        merged['abs_error'] = merged['error'].abs()
        merged['squared_error'] = merged['error'] ** 2
        logger.success(f"Aligned {len(merged)} records")
        logger.info(f"Coverage: {len(merged)/len(preds_median)*100:.1f}%%")
        return merged
