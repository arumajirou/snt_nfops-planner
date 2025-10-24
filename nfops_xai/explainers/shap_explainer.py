"""shap_explainer.py - SHAP説明器"""
import pandas as pd
import numpy as np
from loguru import logger
from sklearn.linear_model import LinearRegression


class ShapExplainer:
    """Simple SHAP explainer using linear approximation"""
ECHO is on.
    def __init__(self, n_samples: int = 100):
        """
        Args:
            n_samples: Number of samples for SHAP estimation
        """
        self.n_samples = n_samples
ECHO is on.
    def explain(
        self,
        df: pd.DataFrame,
        feature_cols: list
    ) -> pd.DataFrame:
        """Compute SHAP values ^(linear approximation^)"""
        logger.info(f"Computing SHAP values for {len^(feature_cols^)} features...")
ECHO is on.
        # Simple approach: use linear regression coefficients as proxy
        X = df[feature_cols].fillna(0)
        y = df['y_hat'].values
ECHO is on.
        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)
ECHO is on.
        # Use coefficients as importance
        shap_results = []
ECHO is on.
        for i, row in df.iterrows():
            base_value = model.intercept_
ECHO is on.
            for j, feature in enumerate(feature_cols):
                feature_value = row[feature] if pd.notna(row[feature]) else 0
                shap_value = model.coef_[j] * feature_value
ECHO is on.
                shap_results.append({
                    'unique_id': row['unique_id'],
                    'ds': row['ds'],
                    'feature': feature,
                    'shap_value': shap_value,
                    'base_value': base_value,
                    'y_hat': row['y_hat'],
                    'y': row['y']
                })
ECHO is on.
        shap_df = pd.DataFrame(shap_results)
        logger.success(f"Computed {len^(shap_df^)} SHAP values")
ECHO is on.
        return shap_df
ECHO is on.
    def aggregate_importance(
        self,
        shap_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Aggregate SHAP values to get global importance"""
        logger.info("Aggregating SHAP values...")
ECHO is on.
        importance = shap_df.groupby('feature')['shap_value'].apply(
            lambda x: np.abs(x).mean()
        ).reset_index()
ECHO is on.
        importance.columns = ['feature', 'importance']
        importance = importance.sort_values('importance', ascending=False)
ECHO is on.
        logger.info(f"Top 5 features: {list^(importance.head^(5^)['feature']^)}")
        return importance
