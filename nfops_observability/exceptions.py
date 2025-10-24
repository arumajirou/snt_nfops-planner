"""Observability カスタム例外"""


class ObservabilityError(Exception):
    """Base exception for observability"""
    pass


class MetricsError(ObservabilityError):
    """E-MON-001: Metrics collection error"""
    pass


class LogError(ObservabilityError):
    """E-MON-021: Log collection error"""
    pass


class AlertError(ObservabilityError):
    """E-MON-041: Alert generation error"""
    pass
