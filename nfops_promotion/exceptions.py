"""Promotion カスタム例外"""


class PromotionError(Exception):
    """Base exception for promotion"""
    pass


class GateFailError(PromotionError):
    """E-PROM-001: Gate check failed"""
    pass


class ArtifactMissingError(PromotionError):
    """E-PROM-021: Required artifact missing"""
    pass


class RegistryError(PromotionError):
    """E-PROM-041: Registry operation failed"""
    pass


class GenerationError(PromotionError):
    """E-API-061: API generation failed"""
    pass
