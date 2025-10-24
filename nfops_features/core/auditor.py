"""auditor.py - 特徴量品質監査"""
import pandas as pd
import numpy as np
from loguru import logger
from nfops_features.models import QualityReport


class FeatureAuditor:
    """Feature quality auditor"""
ECHO is on.
    def audit(self, df: pd.DataFrame) -> QualityReport:
        """Audit feature quality"""
        logger.info("Auditing feature quality...")
ECHO is on.
        n_features = len(df.columns)
ECHO is on.
        # NA introduced rate
        na_count = df.isna().sum().sum()
        na_rate = na_count / (len(df) * n_features)
ECHO is on.
        # Constant features
        const_features = []
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                if df[col].nunique() <= 1:
                    const_features.append(col)
ECHO is on.
        # High correlation pairs
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr().abs()
            upper_tri = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )
            high_corr = (upper_tri > 0.98).sum().sum()
        else:
            high_corr = 0
ECHO is on.
        report = QualityReport(
            n_features=n_features,
            na_introduced_rate=round(na_rate, 4),
            const_feature_count=len(const_features),
            high_corr_pairs=int(high_corr),
            cardinality_issues=[]
        )
ECHO is on.
        logger.info(f"Quality: {n_features} features, NA rate: {na_rate:.2%%}")
        logger.info(f"Constant: {len^(const_features^)}, High corr: {high_corr}")
ECHO is on.
        return report
