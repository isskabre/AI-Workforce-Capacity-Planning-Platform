"""
Enterprise Workforce Domain — Constants

Centralized constants shared by workforce capacity planning,
overtime recommendation, reporting, and downstream decision
intelligence services.
"""

from __future__ import annotations


# ============================================================
# Module Version
# ============================================================

WORKFORCE_DOMAIN_VERSION = "1.0.0"


# ============================================================
# Workforce Defaults
# ============================================================

DEFAULT_PRODUCTIVITY_LINES_PER_HOUR = 120.0

DEFAULT_SCHEDULED_HOURS = 10.0

DEFAULT_AVAILABLE_ASSOCIATES = 0


# ============================================================
# Capacity Planning Defaults
# ============================================================

DEFAULT_TARGET_UTILIZATION = 0.90

DEFAULT_SAFETY_BUFFER_RATIO = 0.05

DEFAULT_MINIMUM_ASSOCIATES = 1

DEFAULT_MAXIMUM_ASSOCIATES = 10_000


# ============================================================
# Overtime Defaults
# ============================================================

DEFAULT_MINIMUM_OVERTIME_HOURS = 5.0

DEFAULT_MAXIMUM_OVERTIME_HOURS = 10.0

DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP = 1


# ============================================================
# Forecast Confidence Defaults
# ============================================================

MINIMUM_FORECAST_CONFIDENCE = 0.0

MAXIMUM_FORECAST_CONFIDENCE = 1.0

DEFAULT_FORECAST_CONFIDENCE = 0.80


# ============================================================
# Status Values
# ============================================================

CAPACITY_STATUS_SUFFICIENT = "SUFFICIENT"

CAPACITY_STATUS_SHORTAGE = "SHORTAGE"

CAPACITY_STATUS_SURPLUS = "SURPLUS"

CAPACITY_STATUS_BALANCED = "BALANCED"


# ============================================================
# Recommendation Values
# ============================================================

RECOMMENDATION_NO_ACTION = "NO_ACTION"

RECOMMENDATION_ADD_ASSOCIATES = "ADD_ASSOCIATES"

RECOMMENDATION_REDUCE_STAFFING = "REDUCE_STAFFING"

RECOMMENDATION_REVIEW_OVERTIME = "REVIEW_OVERTIME"


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CAPACITY_STATUS_BALANCED",
    "CAPACITY_STATUS_SHORTAGE",
    "CAPACITY_STATUS_SUFFICIENT",
    "CAPACITY_STATUS_SURPLUS",
    "DEFAULT_AVAILABLE_ASSOCIATES",
    "DEFAULT_FORECAST_CONFIDENCE",
    "DEFAULT_MAXIMUM_ASSOCIATES",
    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_ASSOCIATES",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",
    "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
    "DEFAULT_SAFETY_BUFFER_RATIO",
    "DEFAULT_SCHEDULED_HOURS",
    "DEFAULT_TARGET_UTILIZATION",
    "MAXIMUM_FORECAST_CONFIDENCE",
    "MINIMUM_FORECAST_CONFIDENCE",
    "RECOMMENDATION_ADD_ASSOCIATES",
    "RECOMMENDATION_NO_ACTION",
    "RECOMMENDATION_REDUCE_STAFFING",
    "RECOMMENDATION_REVIEW_OVERTIME",
    "WORKFORCE_DOMAIN_VERSION",
]