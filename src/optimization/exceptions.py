"""
Enterprise Workforce Optimization Exceptions

Exception hierarchy for the enterprise workforce optimization domain.
"""

from __future__ import annotations


class OptimizationError(Exception):
    """
    Base exception for all workforce optimization failures.
    """


class OptimizationValidationError(OptimizationError):
    """
    Raised when an optimization request or result is invalid.
    """


class OptimizationConfigurationError(OptimizationError):
    """
    Raised when optimization configuration is invalid.
    """


class OptimizationConflictError(OptimizationError):
    """
    Raised when workforce recommendations cannot be reconciled.
    """


class OptimizationEngineError(OptimizationError):
    """
    Raised when the optimization engine cannot complete execution.
    """


class OptimizationServiceError(OptimizationError):
    """
    Raised when the optimization service cannot complete execution.
    """


__all__ = [
    "OptimizationConfigurationError",
    "OptimizationConflictError",
    "OptimizationEngineError",
    "OptimizationError",
    "OptimizationServiceError",
    "OptimizationValidationError",
]