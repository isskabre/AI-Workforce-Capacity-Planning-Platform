"""
Enterprise Capacity Planning Exceptions

Domain-specific exceptions used by the enterprise capacity planning
services.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from src.workforce.exceptions import WorkforceError


# ============================================================
# Base Exception
# ============================================================

class CapacityPlanningError(WorkforceError):
    """
    Base exception for all capacity planning errors.
    """


# ============================================================
# Validation
# ============================================================

class CapacityPlanningValidationError(CapacityPlanningError):
    """
    Raised when capacity-planning request validation fails.
    """


# ============================================================
# Configuration
# ============================================================

class CapacityPlanningConfigurationError(
    CapacityPlanningError,
):
    """
    Raised when an invalid planning configuration is supplied.
    """


# ============================================================
# Calculation
# ============================================================

class CapacityPlanningCalculationError(
    CapacityPlanningError,
):
    """
    Raised when planning calculations fail.
    """


# ============================================================
# Engine
# ============================================================

class CapacityPlanningEngineError(
    CapacityPlanningError,
):
    """
    Raised when the planning engine cannot complete execution.
    """


# ============================================================
# Reporting
# ============================================================

class CapacityPlanningReportingError(
    CapacityPlanningError,
):
    """
    Raised when planning report generation fails.
    """


# ============================================================
# Service
# ============================================================

class CapacityPlanningServiceError(
    CapacityPlanningError,
):
    """
    Raised when the planning service fails.
    """


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningError",
    "CapacityPlanningValidationError",
    "CapacityPlanningConfigurationError",
    "CapacityPlanningCalculationError",
    "CapacityPlanningEngineError",
    "CapacityPlanningReportingError",
    "CapacityPlanningServiceError",
]