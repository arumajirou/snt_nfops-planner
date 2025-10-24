"""split_manager.py - Train/Valid/Test split"""
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from nfops_preprocess.models import Split


class SplitManager:
    """Train/Valid/Test split manager"""
ECHO is on.
    def __init__(self, h: int, valid_rate: float = 0.1):
        """
        Args:
            h: Forecast horizon
            valid_rate: Validation ratio
        """
        self.h = h
        self.valid_rate = valid_rate
ECHO is on.
    def resolve_split(
        self, 
        df: pd.DataFrame,
        cutoff: str = None
    ) -> Split:
        """Determine train/valid/test split"""
        logger.info("Resolving data split...")
ECHO is on.
        max_ds = df['ds'].max()
ECHO is on.
        if cutoff:
            train_end = pd.to_datetime(cutoff)
        else:
            # Auto-determine based on horizon
            train_end = max_ds - pd.Timedelta(days=self.h * 2)
ECHO is on.
        # Valid period = h steps
        valid_end = train_end + pd.Timedelta(days=self.h)
        test_end = max_ds
ECHO is on.
        split = Split(
            train_end=train_end,
            valid_end=valid_end,
            test_end=test_end
        )
ECHO is on.
        logger.info(f"Split: train^<={train_end}, valid^<={valid_end}, test^<={test_end}")
        return split
