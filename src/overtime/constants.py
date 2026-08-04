"""
Enterprise Overtime Recommendation — Constants

Centralized constants used by the Enterprise Overtime Recommendation
Engine.

The module contains no decision logic. It defines stable domain values,
default policy thresholds, supported recommendation categories, and
version metadata shared across the overtime package.
"""

from __future__ import annotations


# ============================================================
# Domain Version
# ============================================================

OVERTIME_DOMAIN_VERSION = "1.0.0"


# ============================================================
# Overtime Duration Policy
# ============================================================

DEFAULT_MINIMUM_OVERTIME_HOURS = 5.0

DEFAULT_MAXIMUM_OVERTIME_HOURS = 10.0

DEFAULT_STANDARD_OVERTIME_HOURS = 5.0


# ============================================================
# Recommendation Thresholds
# ============================================================

DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP = 3

DEFAULT_MANDATORY_OVERTIME_MAX_GAP = 10

DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP = 11

DEFAULT_CRITICAL_SHORTAGE_GAP = 20


# ============================================================
# Confidence Thresholds
# ============================================================

MINIMUM_RECOMMENDATION_CONFIDENCE = 0.0

MAXIMUM_RECOMMENDATION_CONFIDENCE = 1.0

DEFAULT_RECOMMENDATION_CONFIDENCE = 0.80

DEFAULT_HIGH_CONFIDENCE_THRESHOLD = 0.85

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# Recommendation Types
# ============================================================

RECOMMENDATION_NONE = "NONE"

RECOMMENDATION_VOLUNTARY_OVERTIME = "VOLUNTARY_OVERTIME"

RECOMMENDATION_MANDATORY_OVERTIME = "MANDATORY_OVERTIME"

RECOMMENDATION_TEMPORARY_LABOR = "TEMPORARY_LABOR"

RECOMMENDATION_FULL_TIME_HIRING_REVIEW = (
    "FULL_TIME_HIRING_REVIEW"
)

RECOMMENDATION_OPERATIONAL_REVIEW = "OPERATIONAL_REVIEW"


# ============================================================
# Recommendation Priorities
# ============================================================

PRIORITY_LOW = "LOW"

PRIORITY_MEDIUM = "MEDIUM"

PRIORITY_HIGH = "HIGH"

PRIORITY_CRITICAL = "CRITICAL"


# ============================================================
# Recommendation Statuses
# ============================================================

STATUS_NOT_REQUIRED = "NOT_REQUIRED"

STATUS_RECOMMENDED = "RECOMMENDED"

STATUS_REQUIRED = "REQUIRED"

STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"


# ============================================================
# Overtime Types
# ============================================================

OVERTIME_TYPE_NONE = "NONE"

OVERTIME_TYPE_VOLUNTARY = "VOLUNTARY"

OVERTIME_TYPE_MANDATORY = "MANDATORY"


# ============================================================
# Supported Domain Values
# ============================================================

SUPPORTED_RECOMMENDATION_TYPES = (
    RECOMMENDATION_NONE,
    RECOMMENDATION_VOLUNTARY_OVERTIME,
    RECOMMENDATION_MANDATORY_OVERTIME,
    RECOMMENDATION_TEMPORARY_LABOR,
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW,
    RECOMMENDATION_OPERATIONAL_REVIEW,
)

SUPPORTED_RECOMMENDATION_PRIORITIES = (
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
)

SUPPORTED_RECOMMENDATION_STATUSES = (
    STATUS_NOT_REQUIRED,
    STATUS_RECOMMENDED,
    STATUS_REQUIRED,
    STATUS_REVIEW_REQUIRED,
)

SUPPORTED_OVERTIME_TYPES = (
    OVERTIME_TYPE_NONE,
    OVERTIME_TYPE_VOLUNTARY,
    OVERTIME_TYPE_MANDATORY,
)


# ============================================================
# Public API
# ============================================================

__all__ = [
    "DEFAULT_CRITICAL_SHORTAGE_GAP",
    "DEFAULT_HIGH_CONFIDENCE_THRESHOLD",
    "DEFAULT_LOW_CONFIDENCE_THRESHOLD",
    "DEFAULT_MANDATORY_OVERTIME_MAX_GAP",
    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    "DEFAULT_STANDARD_OVERTIME_HOURS",
    "DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP",
    "DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP",
    "MAXIMUM_RECOMMENDATION_CONFIDENCE",
    "MINIMUM_RECOMMENDATION_CONFIDENCE",
    "OVERTIME_DOMAIN_VERSION",
    "OVERTIME_TYPE_MANDATORY",
    "OVERTIME_TYPE_NONE",
    "OVERTIME_TYPE_VOLUNTARY",
    "PRIORITY_CRITICAL",
    "PRIORITY_HIGH",
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",
    "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
    "RECOMMENDATION_MANDATORY_OVERTIME",
    "RECOMMENDATION_NONE",
    "RECOMMENDATION_OPERATIONAL_REVIEW",
    "RECOMMENDATION_TEMPORARY_LABOR",
    "RECOMMENDATION_VOLUNTARY_OVERTIME",
    "STATUS_NOT_REQUIRED",
    "STATUS_RECOMMENDED",
    "STATUS_REQUIRED",
    "STATUS_REVIEW_REQUIRED",
    "SUPPORTED_OVERTIME_TYPES",
    "SUPPORTED_RECOMMENDATION_PRIORITIES",
    "SUPPORTED_RECOMMENDATION_STATUSES",
    "SUPPORTED_RECOMMENDATION_TYPES",
]