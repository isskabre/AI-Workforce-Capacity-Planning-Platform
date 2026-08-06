"""
Enterprise Decision Reporting Exceptions

Exception hierarchy for the enterprise decision reporting domain.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


class ReportingError(Exception):
    """
    Base exception for all reporting-domain failures.
    """


class ReportingValidationError(ReportingError):
    """
    Raised when a reporting request, model, or output is invalid.
    """


class ReportingConfigurationError(ReportingError):
    """
    Raised when reporting configuration is invalid.
    """


class ReportingFormattingError(ReportingError):
    """
    Raised when report formatting or serialization fails.
    """


class ReportingServiceError(ReportingError):
    """
    Raised when the reporting service cannot complete execution.
    """


__all__ = [
    "ReportingConfigurationError",
    "ReportingError",
    "ReportingFormattingError",
    "ReportingServiceError",
    "ReportingValidationError",
]