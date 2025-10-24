"""Training カスタム例外"""


class TrainError(Exception):
    """Base exception for training"""
    pass


class NaNDetectedError(TrainError):
    """E-TRN-001: NaN detected in loss or gradients"""
    pass


class OOMError(TrainError):
    """E-TRN-021: GPU out of memory"""
    pass


class TimeoutError(TrainError):
    """E-RAY-101: Trial timeout"""
    pass


class CheckpointError(TrainError):
    """E-CKPT-201: Checkpoint corruption or inconsistency"""
    pass


class ResumeError(TrainError):
    """E-RES-301: No resume targets found"""
    pass
