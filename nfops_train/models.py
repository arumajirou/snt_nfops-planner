"""Data models for training"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TrialState(Enum):
    """Trial execution state"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PRUNED = "PRUNED"
    INTERRUPTED = "INTERRUPTED"


@dataclass
class TrainSpec:
    """Training specification"""
    model: str
    h: int
    input_size: int
    batch_size: int
    max_epochs: int
    loss: str
    quantiles: Optional[List[float]] = None
    lr: float = 1e-3
    weight_decay: float = 0.0
    seed: int = 42
    precision: str = "32"
    accelerator: str = "gpu"
    devices: int = 1


@dataclass
class TrialResult:
    """Trial execution result"""
    alias: str
    state: TrialState
    best_metric: Optional[float]
    duration_sec: float
    gpu_peak_mb: Optional[float]
    checkpoint_path: Optional[str]
