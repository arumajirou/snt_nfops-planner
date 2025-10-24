"""Evaluation カスタム例外"""


class EvalError(Exception):
    """Base exception for evaluation"""
    pass


class InputError(EvalError):
    """E-EVAL-001: Input missing or invalid"""
    pass


class KeyMismatchError(EvalError):
    """E-EVAL-021: Key mismatch between predictions and actuals"""
    pass


class HorizonMismatchError(EvalError):
    """E-EVAL-031: Horizon mismatch"""
    pass


class InsufficientSliceError(EvalError):
    """E-EVAL-051: Insufficient samples in slice"""
    pass


class TestError(EvalError):
    """E-EVAL-081: Statistical test failure"""
    pass
