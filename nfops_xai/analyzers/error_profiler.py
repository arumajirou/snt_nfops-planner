"""error_profiler.py - エラープロファイラ"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import List
from nfops_xai.models import WorstCase


class ErrorProfiler:
    """Error profiler"""
    def __init__(self, topk: int = 100):
        """
        Args:
            topk: Number of worst cases to extract
        """
        self.topk = topk
    def profile(
        self,
        df: pd.DataFrame
    ) -> List[WorstCase]:
        """Profile errors and extract worst cases"""
        logger.info(f"Profiling errors, extracting top {self.topk}...")
        # Calculate errors
        df = df.copy()
        df['error'] = df['y_hat'] - df['y']
        df['abs_error'] = df['error'].abs()
        # Sort by absolute error
        df_sorted = df.sort_values('abs_error', ascending=False)
        # Extract worst cases
        worst_cases = []
        for i, (idx, row) in enumerate(df_sorted.head(self.topk).iterrows()):
            case = WorstCase(
                unique_id=row['unique_id'],
                ds=str(row['ds']),
                y=float(row['y']),
                y_hat=float(row['y_hat']),
                error=float(row['error']),
                abs_error=float(row['abs_error']),
                rank=i+1
            )
            worst_cases.append(case)
        logger.success(f"Extracted {len(worst_cases)} worst cases")
        return worst_cases
    def save_worst_cases(
        self,
        worst_cases: List[WorstCase],
        output_path
    ):
        """Save worst cases to parquet"""
        records = [
            {
                'unique_id': wc.unique_id,
                'ds': wc.ds,
                'y': wc.y,
                'y_hat': wc.y_hat,
                'error': wc.error,
                'abs_error': wc.abs_error,
                'rank': wc.rank
            }
            for wc in worst_cases
        ]
        df = pd.DataFrame(records)
        df.to_parquet(output_path)
        logger.success(f"Saved worst cases: {output_path}")
