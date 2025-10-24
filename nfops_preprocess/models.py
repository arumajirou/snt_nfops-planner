"""Data models for preprocessing"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Split:
    """Train/Valid/Test split definition"""
    train_end: datetime
    valid_end: Optional[datetime]
    test_end: datetime
ECHO is on.
    def get_mask(self, ds_series):
        """Get boolean masks for each split"""
        train_mask = ds_series <= self.train_end
        if self.valid_end:
            valid_mask = (ds_series > self.train_end) & (ds_series <= self.valid_end)
            test_mask = ds_series > self.valid_end
        else:
            valid_mask = None
            test_mask = ds_series > self.train_end
        return train_mask, valid_mask, test_mask


@dataclass
class SeriesState:
    """Series-level state for inverse transform"""
    unique_id: str
    last_train_ds: datetime
    last_y: Optional[float] = None
    buffer: Optional[List[float]] = None
    base_cumsum: Optional[float] = None
    last_s_values: Optional[List[float]] = None


@dataclass
class YTransformMeta:
    """Y transform metadata"""
    version: str
    y_type: str
    window: Optional[int]
    period: Optional[int]
    anchor_ds: datetime
    series_state: List[SeriesState]
ECHO is on.
    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "y_type": self.y_type,
            "window": self.window,
            "period": self.period,
            "anchor_ds": self.anchor_ds.isoformat(),
            "series_state": [
                {
                    "unique_id": s.unique_id,
                    "last_train_ds": s.last_train_ds.isoformat(),
                    "last_y": s.last_y,
                    "buffer": s.buffer,
                    "base_cumsum": s.base_cumsum,
                    "last_s_values": s.last_s_values
                }
                for s in self.series_state
            ]
        }
