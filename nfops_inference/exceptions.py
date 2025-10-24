"""Inference カスタム例外"""


class InferenceError(Exception):
    """Base exception for inference"""
    pass


class InputError(InferenceError):
    """E-INF-001: Input validation failed"""
    pass


class PredictError(InferenceError):
    """E-INF-021: Prediction failed"""
    pass


class TimeoutError(InferenceError):
    """E-INF-041: Operation timeout"""
    pass


class CircuitOpenError(InferenceError):
    """E-INF-061: Circuit breaker open"""
    pass
