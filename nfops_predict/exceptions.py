"""Prediction カスタム例外"""


class PredictError(Exception):
    """Base exception for prediction"""
    pass


class FutureCoverageError(PredictError):
    """E-PRED-001: Future exog coverage insufficient"""
    pass


class QuantileCrossingError(PredictError):
    """E-PRED-021: Quantile crossing detected"""
    pass


class InverseError(PredictError):
    """E-PRED-041: Inverse transformation failed"""
    pass


class DistributionError(PredictError):
    """E-PRED-061: Invalid distribution parameters"""
    pass


class CalibrationError(PredictError):
    """E-PRED-081: Calibration failure"""
    pass
