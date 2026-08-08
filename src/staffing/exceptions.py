"""
Enterprise Staffing Exceptions

Enterprise exception hierarchy for strategic staffing recommendation.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""


class StaffingError(Exception):
    """
    Base exception for the staffing recommendation domain.
    """


class StaffingValidationError(StaffingError):
    """
    Raised when staffing request validation fails.
    """


class StaffingConfigurationError(StaffingError):
    """
    Raised when staffing configuration is invalid.
    """


class StaffingEngineError(StaffingError):
    """
    Raised when the staffing recommendation engine fails.
    """


class StaffingServiceError(StaffingError):
    """
    Raised when the staffing service fails.
    """