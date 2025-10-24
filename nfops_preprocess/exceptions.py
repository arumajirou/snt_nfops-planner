"""Preprocessing カスタム例外"""


class PreprocessError(Exception):
    """Base exception for preprocessing"""
    pass


class NonFiniteError(PreprocessError):
    """E-P3-101: Non-finite values introduced"""
    pass


class InverseError(PreprocessError):
    """E-P3-151: Inverse transform failed"""
    pass


class LeakageError(PreprocessError):
    """E-P3-201: Data leakage detected"""
    pass


class NegativeValueError(PreprocessError):
    """E-P3-251: Negative values in log transform"""
    pass
