"""
Enterprise Overtime Recommendation

Public API for the enterprise overtime recommendation domain.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

# ============================================================
# Constants
# ============================================================

from .constants import (
    DEFAULT_CRITICAL_SHORTAGE_GAP,
    DEFAULT_HIGH_CONFIDENCE_THRESHOLD,
    DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_MANDATORY_OVERTIME_MAX_GAP,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_RECOMMENDATION_CONFIDENCE,
    DEFAULT_STANDARD_OVERTIME_HOURS,
    DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP,
    DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP,
    MAXIMUM_RECOMMENDATION_CONFIDENCE,
    MINIMUM_RECOMMENDATION_CONFIDENCE,
    OVERTIME_DOMAIN_VERSION,
    OVERTIME_TYPE_MANDATORY,
    OVERTIME_TYPE_NONE,
    OVERTIME_TYPE_VOLUNTARY,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW,
    RECOMMENDATION_MANDATORY_OVERTIME,
    RECOMMENDATION_NONE,
    RECOMMENDATION_OPERATIONAL_REVIEW,
    RECOMMENDATION_TEMPORARY_LABOR,
    RECOMMENDATION_VOLUNTARY_OVERTIME,
    STATUS_NOT_REQUIRED,
    STATUS_RECOMMENDED,
    STATUS_REQUIRED,
    STATUS_REVIEW_REQUIRED,
    SUPPORTED_OVERTIME_TYPES,
    SUPPORTED_RECOMMENDATION_PRIORITIES,
    SUPPORTED_RECOMMENDATION_STATUSES,
    SUPPORTED_RECOMMENDATION_TYPES,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    OvertimeCapacityError,
    OvertimeConfigurationError,
    OvertimeEngineError,
    OvertimeError,
    OvertimePolicyError,
    OvertimeRecommendationError,
    OvertimeServiceError,
    OvertimeValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    OvertimeRecommendation,
    OvertimeRequest,
    OvertimeType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)

# ============================================================
# Components
# ============================================================

from .configuration import OvertimeConfiguration
from .engine import OvertimeRecommendationEngine
from .service import OvertimeRecommendationService


__all__ = [
    # Version
    "OVERTIME_DOMAIN_VERSION",

    # Duration policy
    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_STANDARD_OVERTIME_HOURS",

    # Thresholds
    "DEFAULT_CRITICAL_SHORTAGE_GAP",
    "DEFAULT_MANDATORY_OVERTIME_MAX_GAP",
    "DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP",
    "DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP",

    # Confidence
    "DEFAULT_HIGH_CONFIDENCE_THRESHOLD",
    "DEFAULT_LOW_CONFIDENCE_THRESHOLD",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    "MAXIMUM_RECOMMENDATION_CONFIDENCE",
    "MINIMUM_RECOMMENDATION_CONFIDENCE",

    # Constant recommendation values
    "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
    "RECOMMENDATION_MANDATORY_OVERTIME",
    "RECOMMENDATION_NONE",
    "RECOMMENDATION_OPERATIONAL_REVIEW",
    "RECOMMENDATION_TEMPORARY_LABOR",
    "RECOMMENDATION_VOLUNTARY_OVERTIME",

    # Priorities
    "PRIORITY_CRITICAL",
    "PRIORITY_HIGH",
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",

    # Statuses
    "STATUS_NOT_REQUIRED",
    "STATUS_RECOMMENDED",
    "STATUS_REQUIRED",
    "STATUS_REVIEW_REQUIRED",

    # Overtime types
    "OVERTIME_TYPE_MANDATORY",
    "OVERTIME_TYPE_NONE",
    "OVERTIME_TYPE_VOLUNTARY",

    # Supported values
    "SUPPORTED_OVERTIME_TYPES",
    "SUPPORTED_RECOMMENDATION_PRIORITIES",
    "SUPPORTED_RECOMMENDATION_STATUSES",
    "SUPPORTED_RECOMMENDATION_TYPES",

    # Exceptions
    "OvertimeCapacityError",
    "OvertimeConfigurationError",
    "OvertimeEngineError",
    "OvertimeError",
    "OvertimePolicyError",
    "OvertimeRecommendationError",
    "OvertimeServiceError",
    "OvertimeValidationError",

    # Models and enums
    "OvertimeRecommendation",
    "OvertimeRequest",
    "OvertimeType",
    "RecommendationPriority",
    "RecommendationStatus",
    "RecommendationType",

    # Components
    "OvertimeConfiguration",
    "OvertimeRecommendationEngine",
    "OvertimeRecommendationService",
]