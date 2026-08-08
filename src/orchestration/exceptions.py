"""
Enterprise Decision Orchestration Exceptions

Exception hierarchy for the enterprise decision orchestration domain.
"""

from __future__ import annotations


class OrchestrationError(Exception):
    """
    Base exception for all orchestration failures.
    """


class OrchestrationValidationError(OrchestrationError):
    """
    Raised when an orchestration request or result is invalid.
    """


class OrchestrationConfigurationError(OrchestrationError):
    """
    Raised when orchestration configuration is invalid.
    """


class OrchestrationDependencyError(OrchestrationError):
    """
    Raised when a required domain dependency is missing or inconsistent.
    """


class OrchestrationStageError(OrchestrationError):
    """
    Raised when one orchestration stage cannot complete successfully.
    """


class OrchestrationEngineError(OrchestrationError):
    """
    Raised when the orchestration engine fails.
    """


class OrchestrationServiceError(OrchestrationError):
    """
    Raised when the orchestration service fails.
    """


__all__ = [
    "OrchestrationConfigurationError",
    "OrchestrationDependencyError",
    "OrchestrationEngineError",
    "OrchestrationError",
    "OrchestrationServiceError",
    "OrchestrationStageError",
    "OrchestrationValidationError",
]