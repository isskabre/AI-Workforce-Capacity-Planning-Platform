"""
Enterprise Workforce Domain

Public API for workforce planning domain models, constants,
enumerations, and enterprise exceptions.
"""

from __future__ import annotations

from .constants import (
    CAPACITY_STATUS_BALANCED,
    CAPACITY_STATUS_SHORTAGE,
    CAPACITY_STATUS_SUFFICIENT,
    CAPACITY_STATUS_SURPLUS,
    DEFAULT_AVAILABLE_ASSOCIATES,
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_MAXIMUM_ASSOCIATES,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_ASSOCIATES,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    MAXIMUM_FORECAST_CONFIDENCE,
    MINIMUM_FORECAST_CONFIDENCE,
    RECOMMENDATION_ADD_ASSOCIATES,
    RECOMMENDATION_NO_ACTION,
    RECOMMENDATION_REDUCE_STAFFING,
    RECOMMENDATION_REVIEW_OVERTIME,
    WORKFORCE_DOMAIN_VERSION,
)
from .exceptions import (
    WorkforceAvailabilityError,
    WorkforceCapacityError,
    WorkforceConfigurationError,
    WorkforceError,
    WorkforcePlanningError,
    WorkforceValidationError,
)
from .models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)


__all__ = [
    # Version
    "WORKFORCE_DOMAIN_VERSION",

    # Enumerations
    "OvertimeType",
    "ShiftType",
    "WorkforceType",

    # Models
    "WorkforceCapacity",
    "WorkforceGap",
    "WorkforceRequirement",

    # Workforce defaults
    "DEFAULT_AVAILABLE_ASSOCIATES",
    "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
    "DEFAULT_SCHEDULED_HOURS",

    # Capacity-planning defaults
    "DEFAULT_MAXIMUM_ASSOCIATES",
    "DEFAULT_MINIMUM_ASSOCIATES",
    "DEFAULT_SAFETY_BUFFER_RATIO",
    "DEFAULT_TARGET_UTILIZATION",

    # Overtime defaults
    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",

    # Forecast confidence
    "DEFAULT_FORECAST_CONFIDENCE",
    "MAXIMUM_FORECAST_CONFIDENCE",
    "MINIMUM_FORECAST_CONFIDENCE",

    # Capacity statuses
    "CAPACITY_STATUS_BALANCED",
    "CAPACITY_STATUS_SHORTAGE",
    "CAPACITY_STATUS_SUFFICIENT",
    "CAPACITY_STATUS_SURPLUS",

    # Recommendations
    "RECOMMENDATION_ADD_ASSOCIATES",
    "RECOMMENDATION_NO_ACTION",
    "RECOMMENDATION_REDUCE_STAFFING",
    "RECOMMENDATION_REVIEW_OVERTIME",

    # Exceptions
    "WorkforceAvailabilityError",
    "WorkforceCapacityError",
    "WorkforceConfigurationError",
    "WorkforceError",
    "WorkforcePlanningError",
    "WorkforceValidationError",
]