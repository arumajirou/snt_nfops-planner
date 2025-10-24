"""data_aligner.py - データ整列"""
import pandas as pd
from loguru import logger


class DataAligner:
    """Data aligner for XAI"""
    def align(
        self,
        features: pd.DataFrame,
        preds: pd.DataFrame,
        actuals: pd.DataFrame
    ) -> pd.DataFrame:
        """Align features, predictions, and actuals"""
        logger.info("Aligning features, predictions, and actuals...")
        # Get median predictions
        if 'q' in preds.columns:
            preds_median = preds[preds['q'] == 0.5].copy()
        else:
            preds_median = preds.copy()
        # Merge predictions with actuals
        merged = preds_median.merge(
            actuals,
            on=['unique_id', 'ds'],
            how='inner'
        )
        # Merge with features
        merged = merged.merge(
            features,
            on=['unique_id', 'ds'],
            how='inner'
        )
        logger.success(f"Aligned {len(merged)} records")
        return merged
