"""
Enterprise Overtime Recommendation Exceptions

Custom exception hierarchy for the Enterprise Overtime Recommendation
domain.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


class OvertimeError(Exception):
    """
    Base exception for the overtime recommendation domain.
    """


class OvertimeValidationError(OvertimeError):
    """
    Raised when overtime request validation fails.
    """


class OvertimeConfigurationError(OvertimeError):
    """
    Raised when overtime configuration is invalid.
    """


class OvertimeRecommendationError(OvertimeError):
    """
    Raised when a recommendation cannot be generated.
    """


class OvertimeCapacityError(OvertimeError):
    """
    Raised when workforce capacity information is invalid or inconsistent.
    """


class OvertimePolicyError(OvertimeError):
    """
    Raised when an overtime policy is violated.
    """


class OvertimeEngineError(OvertimeError):
    """
    Raised when the overtime recommendation engine fails.
    """


class OvertimeServiceError(OvertimeError):
    """
    Raised by the service layer.
    """


__all__ = [
    "OvertimeError",
    "OvertimeValidationError",
    "OvertimeConfigurationError",
    "OvertimeRecommendationError",
    "OvertimeCapacityError",
    "OvertimePolicyError",
    "OvertimeEngineError",
    "OvertimeServiceError",
]