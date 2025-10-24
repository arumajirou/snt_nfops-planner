"""futr_loader.py - 将来外生変数読込"""
import pandas as pd
from pathlib import Path
from loguru import logger
from nfops_predict.exceptions import FutureCoverageError


class FutrLoader:
    """Future exogenous variable loader"""
    def __init__(self, h: int, freq: str = 'D'):
        """
        Args:
            h: Forecast horizon
            freq: Frequency
        """
        self.h = h
        self.freq = freq
    def load(
        self, 
        futr_path: Path,
        scenario_id: str = "base"
    ) -> pd.DataFrame:
        """Load and validate future exog"""
        logger.info(f"Loading future exog from {futr_path}")
        # Load data
        if str(futr_path).endswith('.parquet'):
            df = pd.read_parquet(futr_path)
        else:
            df = pd.read_csv(futr_path, parse_dates=['ds'])
        # Validate
        required_cols = ['unique_id', 'ds']
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        # Add scenario_id
        df['scenario_id'] = scenario_id
        # Check coverage
        for uid, group in df.groupby('unique_id'):
            if len(group) < self.h:
                logger.warning(
                    f"Series {uid} has only {len(group)} points, "
                    f"less than horizon {self.h}"
                )
        logger.success(f"Loaded {len(df)} future records for scenario '{scenario_id}'")
        return df
