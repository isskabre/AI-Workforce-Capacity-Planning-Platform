"""
Enterprise Workforce Domain — Exceptions

Exception hierarchy shared by workforce capacity planning,
overtime recommendation, and downstream workforce decision
intelligence services.
"""

from __future__ import annotations


# ============================================================
# Base Workforce Exception
# ============================================================

class WorkforceError(Exception):
    """
    Base exception for all workforce domain failures.
    """


# ============================================================
# Validation Exceptions
# ============================================================

class WorkforceValidationError(WorkforceError):
    """
    Raised when workforce domain input validation fails.
    """


class WorkforceConfigurationError(WorkforceError):
    """
    Raised when workforce configuration is invalid.
    """


# ============================================================
# Capacity Exceptions
# ============================================================

class WorkforceCapacityError(WorkforceError):
    """
    Raised when workforce capacity cannot be calculated.
    """


class WorkforceAvailabilityError(WorkforceError):
    """
    Raised when workforce availability data is invalid or incomplete.
    """


# ============================================================
# Planning Exceptions
# ============================================================

class WorkforcePlanningError(WorkforceError):
    """
    Raised when workforce planning execution fails.
    """


# ============================================================
# Public API
# ============================================================

__all__ = [
    "WorkforceAvailabilityError",
    "WorkforceCapacityError",
    "WorkforceConfigurationError",
    "WorkforceError",
    "WorkforcePlanningError",
    "WorkforceValidationError",
]