"""price_promo_builder.py - 価格/販促特徴"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, List


class PricePromoBuilder:
    """Price and promo feature builder"""
ECHO is on.
    def __init__(self, price_spec: Dict = None, promo_spec: Dict = None):
        self.price_spec = price_spec or {}
        self.promo_spec = promo_spec or {}
ECHO is on.
    def build_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build price features"""
        logger.info("Building price features")
ECHO is on.
        df = df.copy()
ECHO is on.
        if 'price' not in df.columns:
            logger.warning("No 'price' column, skipping price features")
            return df
ECHO is on.
        windows = self.price_spec.get('pct_change_windows', [1])
ECHO is on.
        for w in windows:
            col_name = f'price_pctchg_{w}'
            df[col_name] = df.groupby('unique_id')['price'].pct_change(w)
            logger.debug(f"Created: {col_name}")
ECHO is on.
        logger.success("Built price features")
        return df
ECHO is on.
    def build_promo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build promo features"""
        logger.info("Building promo features")
ECHO is on.
        df = df.copy()
ECHO is on.
        if 'promo' not in df.columns:
            logger.warning("No 'promo' column, skipping promo features")
            return df
ECHO is on.
        flags = self.promo_spec.get('flags', ['on_off'])
ECHO is on.
        for flag in flags:
            if flag == 'on_off':
                df['promo_flag'] = (df['promo'] > 0).astype(int)
            elif flag == 'depth_bucket':
                df['promo_depth_bucket'] = pd.cut(
                    df['promo'], 
                    bins=[-np.inf, 0, 0.1, 0.2, np.inf],
                    labels=[0, 1, 2, 3]
                ).astype(int)
ECHO is on.
            logger.debug(f"Created: promo_{flag}")
ECHO is on.
        logger.success("Built promo features")
        return df
