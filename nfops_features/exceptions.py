"""Feature Engineering カスタム例外"""


class FeatureError(Exception):
    """Base exception for feature engineering"""
    pass


class FutureCoverageError(FeatureError):
    """E-FEAT-051: Future exog coverage insufficient"""
    pass


class LeakageError(FeatureError):
    """E-FEAT-081: Data leakage detected"""
    pass


class HighCardinalityError(FeatureError):
    """E-FEAT-111: High cardinality explosion"""
    pass


class ConvergenceError(FeatureError):
    """E-FEAT-171: Cluster convergence failure"""
    pass
