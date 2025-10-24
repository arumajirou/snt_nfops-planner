"""dataset_builder.py - Lightning DataModule構築"""
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from loguru import logger
from typing import Optional

try:
    import pytorch_lightning as pl
except ImportError:
    import lightning.pytorch as pl


class TimeSeriesDataset(Dataset):
    """Time series dataset"""
    def __init__(self, df: pd.DataFrame, h: int, input_size: int):
        """
        Args:
            df: Long format data with unique_id, ds, y, features
            h: Forecast horizon
            input_size: Input sequence length
        """
        self.df = df
        self.h = h
        self.input_size = input_size
        # Group by series
        self.series_groups = list(df.groupby('unique_id'))
    def __len__(self):
        return len(self.series_groups)
    def __getitem__(self, idx):
        uid, group = self.series_groups[idx]
        # Get y values
        y = group['y_scaled'].values if 'y_scaled' in group.columns else group['y'].values
        # Simple sliding window
        if len(y) < self.input_size + self.h:
            # Pad if too short
            y = np.pad(y, (0, self.input_size + self.h - len(y)), mode='edge')
        # Take last window
        hist = y[-self.input_size - self.h:-self.h]
        futr = y[-self.h:]
        return {
            'hist': torch.FloatTensor(hist),
            'futr': torch.FloatTensor(futr)
        }


class TimeSeriesDataModule(pl.LightningDataModule):
    """Lightning DataModule for time series"""
    def __init__(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        h: int,
        input_size: int,
        batch_size: int = 32,
        num_workers: int = 0
    ):
        super().__init__()
        self.train_df = train_df
        self.val_df = val_df
        self.test_df = test_df
        self.h = h
        self.input_size = input_size
        self.batch_size = batch_size
        self.num_workers = num_workers
    def setup(self, stage: Optional[str] = None):
        """Setup datasets"""
        if stage == 'fit' or stage is None:
            self.train_dataset = TimeSeriesDataset(
                self.train_df, self.h, self.input_size
            )
            self.val_dataset = TimeSeriesDataset(
                self.val_df, self.h, self.input_size
            )
        if stage == 'test' or stage is None:
            self.test_dataset = TimeSeriesDataset(
                self.test_df, self.h, self.input_size
            )
    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True
        )
    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True
        )
    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers
        )


class DatasetBuilder:
    """Dataset builder"""
    @staticmethod
    def build(
        df: pd.DataFrame,
        train_end,
        val_end,
        h: int,
        input_size: int,
        batch_size: int = 32
    ) -> TimeSeriesDataModule:
        """Build DataModule"""
        logger.info("Building DataModule...")
        # Split data
        train_df = df[df['ds'] <= train_end]
        val_df = df[(df['ds'] > train_end) & (df['ds'] <= val_end)]
        test_df = df[df['ds'] > val_end]
        logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        return TimeSeriesDataModule(
            train_df=train_df,
            val_df=val_df,
            test_df=test_df,
            h=h,
            input_size=input_size,
            batch_size=batch_size
        )
