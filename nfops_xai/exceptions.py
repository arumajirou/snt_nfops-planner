"""XAI カスタム例外"""


class XAIError(Exception):
    """Base exception for XAI"""
    pass


class InputError(XAIError):
    """E-XAI-001: Input inconsistency"""
    pass


class OOMError(XAIError):
    """E-XAI-021: Out of memory"""
    pass


class UnstableError(XAIError):
    """E-XAI-041: SHAP unstable"""
    pass


class AlignError(XAIError):
    """E-XAI-101: Alignment failure"""
    pass
