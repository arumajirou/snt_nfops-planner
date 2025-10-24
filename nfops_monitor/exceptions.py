"""Monitor カスタム例外"""


class MonitorError(Exception):
    """Base exception for monitoring"""
    pass


class DataError(MonitorError):
    """E-MON-001: Data loading error"""
    pass


class DriftError(MonitorError):
    """E-MON-021: Drift detection error"""
    pass


class AlertError(MonitorError):
    """E-MON-041: Alert generation error"""
    pass
