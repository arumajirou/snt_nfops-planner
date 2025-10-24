"""drift_detector.py - ドリフト検知"""
import numpy as np
import pandas as pd
from loguru import logger
from typing import List, Dict
from scipy import stats
from nfops_monitor.models import DriftResult


class DriftDetector:
    """Drift detector using PSI and KS test"""
    
    def __init__(
        self,
        psi_warning: float = 0.1,
        psi_critical: float = 0.25,
        ks_alpha: float = 0.01
    ):
        """
        Args:
            psi_warning: PSI threshold for warning
            psi_critical: PSI threshold for critical
            ks_alpha: Significance level for KS test
        """
        self.psi_warning = psi_warning
        self.psi_critical = psi_critical
        self.ks_alpha = ks_alpha
    
    def calculate_psi(
        self,
        reference: pd.Series,
        current: pd.Series,
        n_bins: int = 10
    ) -> float:
        """Calculate Population Stability Index (PSI)"""
        
        # Remove NaN
        reference = reference.dropna()
        current = current.dropna()
        
        if len(reference) == 0 or len(current) == 0:
            return 0.0
        
        # Create bins based on reference
        bins = np.percentile(
            reference,
            np.linspace(0, 100, n_bins + 1)
        )
        bins = np.unique(bins)  # Remove duplicates
        
        if len(bins) < 2:
            return 0.0
        
        # Count in bins
        ref_counts, _ = np.histogram(reference, bins=bins)
        cur_counts, _ = np.histogram(current, bins=bins)
        
        # Normalize to proportions
        ref_props = ref_counts / len(reference)
        cur_props = cur_counts / len(current)
        
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        ref_props = ref_props + epsilon
        cur_props = cur_props + epsilon
        
        # Calculate PSI
        psi = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))
        
        return psi
    
    def ks_test(
        self,
        reference: pd.Series,
        current: pd.Series
    ) -> tuple:
        """Perform Kolmogorov-Smirnov test"""
        
        reference = reference.dropna()
        current = current.dropna()
        
        if len(reference) == 0 or len(current) == 0:
            return None, None
        
        statistic, pvalue = stats.ks_2samp(reference, current)
        
        return statistic, pvalue
    
    def detect(
        self,
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame,
        features: List[str]
    ) -> List[DriftResult]:
        """Detect drift for features"""
        logger.info(f"Detecting drift for {len(features)} features")
        
        results = []
        
        for feature in features:
            if feature not in reference_df.columns or feature not in current_df.columns:
                logger.warning(f"Feature {feature} not found in data")
                continue
            
            # Calculate PSI
            psi = self.calculate_psi(
                reference_df[feature],
                current_df[feature]
            )
            
            # KS test
            ks_stat, ks_pval = self.ks_test(
                reference_df[feature],
                current_df[feature]
            )
            
            # Determine alert level
            if psi >= self.psi_critical or (ks_pval is not None and ks_pval < self.ks_alpha):
                alert_level = "critical"
            elif psi >= self.psi_warning:
                alert_level = "warning"
            else:
                alert_level = "ok"
            
            result = DriftResult(
                feature=feature,
                psi=psi,
                ks_statistic=ks_stat,
                ks_pvalue=ks_pval,
                alert_level=alert_level
            )
            
            results.append(result)
            
            if alert_level != "ok":
                logger.warning(
                    f"Drift detected: {feature} | PSI={psi:.3f} | "
                    f"KS_p={ks_pval:.4f if ks_pval else 'N/A'} | level={alert_level}"
                )
        
        logger.success(f"Drift detection completed for {len(results)} features")
        
        return results
