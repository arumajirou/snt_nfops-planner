"""
カスタム例外定義
"""


class NfopsPlannerError(Exception):
    """Base exception for nfops-planner"""
    pass


class SpecValidationError(NfopsPlannerError):
    """E-SPEC-xxx: Spec validation errors"""
    pass


class CircularDependencyError(SpecValidationError):
    """E-SPEC-101: Circular dependency detected"""
    pass


class InvalidTableError(NfopsPlannerError):
    """E-INV-xxx: Invalid table errors"""
    pass


class CombinationError(NfopsPlannerError):
    """E-COMB-xxx: Combination counting errors"""
    pass


class ZeroCombinationsError(CombinationError):
    """E-COMB-301: Total combinations is zero"""
    pass


class EstimationError(NfopsPlannerError):
    """E-EST-xxx: Estimation errors"""
    pass


class MlflowError(NfopsPlannerError):
    """E-MLF-xxx: MLflow connection errors"""
    pass
