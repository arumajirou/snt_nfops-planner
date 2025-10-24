"""test_dataset_builder.py"""
import pytest
import pandas as pd
import numpy as np
from nfops_train.core.dataset_builder import DatasetBuilder, TimeSeriesDataset


class TestDatasetBuilder:
    @pytest.fixture
    def sample_df(self):
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = []
        for sid in ['A', 'B']:
            for date in dates:
                data.append({
                    'unique_id': sid,
                    'ds': date,
                    'y': np.random.randn(),
                    'y_scaled': np.random.randn()
                })
        return pd.DataFrame(data)
ECHO is on.
    def test_dataset_creation(self, sample_df):
        """Test dataset creation"""
        dataset = TimeSeriesDataset(sample_df, h=7, input_size=14)
ECHO is on.
        assert len(dataset) == 2  # 2 series
ECHO is on.
        sample = dataset[0]
        assert 'hist' in sample
        assert 'futr' in sample
        assert sample['hist'].shape[0] == 14
        assert sample['futr'].shape[0] == 7
ECHO is on.
    def test_datamodule_build(self, sample_df):
        """Test DataModule build"""
        train_end = pd.to_datetime('2024-03-01')
        val_end = pd.to_datetime('2024-03-15')
ECHO is on.
        dm = DatasetBuilder.build(
            df=sample_df,
            train_end=train_end,
            val_end=val_end,
            h=7,
            input_size=14,
            batch_size=2
        )
ECHO is on.
        dm.setup('fit')
ECHO is on.
        train_loader = dm.train_dataloader()
        assert train_loader is not None
