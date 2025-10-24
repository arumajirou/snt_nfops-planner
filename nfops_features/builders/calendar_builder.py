"""calendar_builder.py - カレンダー特徴"""
import pandas as pd
from loguru import logger
from typing import List


class CalendarBuilder:
    """Calendar feature builder"""
ECHO is on.
    def __init__(self, features: List[str], locale: str = 'ja'):
        """
        Args:
            features: Calendar features to build
            locale: Locale for holidays
        """
        self.features = features or []
        self.locale = locale
ECHO is on.
    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build calendar features"""
        logger.info(f"Building calendar features: {len^(self.features^)}")
ECHO is on.
        df = df.copy()
ECHO is on.
        # Ensure ds is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['ds']):
            df['ds'] = pd.to_datetime(df['ds'])
ECHO is on.
        for feat in self.features:
            if feat == 'dow':
                df['cal_dow'] = df['ds'].dt.dayofweek
            elif feat == 'month':
                df['cal_month'] = df['ds'].dt.month
            elif feat == 'is_month_end':
                df['cal_is_month_end'] = df['ds'].dt.is_month_end.astype(int)
            elif feat == 'is_year_end':
                df['cal_is_year_end'] = ((df['ds'].dt.month == 12) & (df['ds'].dt.day >= 29)).astype(int)
            elif feat == 'quarter':
                df['cal_quarter'] = df['ds'].dt.quarter
            elif feat == 'week_of_year':
                df['cal_week_of_year'] = df['ds'].dt.isocalendar().week
            elif feat == 'jp_holiday':
                try:
                    import jpholiday
                    df['cal_jp_holiday'] = df['ds'].apply(
                        lambda x: 1 if jpholiday.is_holiday(x.date()) else 0
                    )
                except ImportError:
                    logger.warning("jpholiday not installed, skipping jp_holiday")
                    df['cal_jp_holiday'] = 0
ECHO is on.
            logger.debug(f"Created: cal_{feat}")
ECHO is on.
        logger.success(f"Built {len^(self.features^)} calendar features")
        return df
