"""predictor.py - 予測エンジン"""
import pandas as pd
import numpy as np
import torch
from loguru import logger
from typing import List, Optional, Dict
from nfops_predict.models import PredictionResult


class Predictor:
    """Predictor"""
ECHO is on.
    def __init__(
        self,
        model: torch.nn.Module,
        hparams: Dict,
        device: str = 'cpu'
    ):
        """
        Args:
            model: Loaded model
            hparams: Hyperparameters
            device: Device to use
        """
        self.model = model
        self.hparams = hparams
        self.device = device
ECHO is on.
        if self.model:
            self.model.to(device)
            self.model.eval()
ECHO is on.
    def predict_quantiles(
        self,
        df: pd.DataFrame,
        quantiles: List[float],
        scenario_id: str = "base",
        run_id: str = "unknown"
    ) -> PredictionResult:
        """Predict quantiles"""
        logger.info(f"Predicting quantiles: {quantiles}")
ECHO is on.
        results = []
ECHO is on.
        # Simple forecast: use last value ± noise
        for uid, group in df.groupby('unique_id'):
            y_last = group['y_scaled'].iloc[-1] if 'y_scaled' in group.columns else group['y'].iloc[-1]
ECHO is on.
            # Generate future dates
            last_ds = group['ds'].max()
            future_dates = pd.date_range(
                start=last_ds + pd.Timedelta(days=1),
                periods=self.hparams.get('h', 24),
                freq='D'
            )
ECHO is on.
            # Predict for each quantile
            for q in quantiles:
                # Simple model: add quantile-based noise
                noise_scale = 0.1
                if q < 0.5:
                    noise = -(0.5 - q) * noise_scale * 2
                elif q > 0.5:
                    noise = (q - 0.5) * noise_scale * 2
                else:
                    noise = 0.0
ECHO is on.
                y_pred = y_last + noise
ECHO is on.
                for ds in future_dates:
                    results.append({
                        'unique_id': uid,
                        'ds': ds,
                        'q': q,
                        'y_hat': y_pred,
                        'scenario_id': scenario_id,
                        'run_id': run_id,
                        'model': self.hparams.get('model', 'SimpleSeq2Seq')
                    })
ECHO is on.
        pred_df = pd.DataFrame(results)
        logger.success(f"Generated {len^(pred_df^)} predictions")
ECHO is on.
        return PredictionResult(
            df=pred_df,
            quantiles=quantiles,
            scenario_id=scenario_id,
            run_id=run_id
        )
ECHO is on.
    def predict_point(
        self,
        df: pd.DataFrame,
        scenario_id: str = "base",
        run_id: str = "unknown"
    ) -> PredictionResult:
        """Predict point estimates"""
        return self.predict_quantiles(
            df=df,
            quantiles=[0.5],
            scenario_id=scenario_id,
            run_id=run_id
        )
