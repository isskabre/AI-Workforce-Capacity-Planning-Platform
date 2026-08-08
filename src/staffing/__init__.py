"""
Enterprise Staffing Recommendation

Public API for the enterprise strategic staffing recommendation domain.

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
    CRITICAL_SHORTAGE_GAP,
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_RECOMMENDATION_CONFIDENCE,
    FULL_TIME_HIRING_TRIGGER_GAP,
    HIGH_CONFIDENCE_THRESHOLD,
    LOW_CONFIDENCE_THRESHOLD,
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
    MINIMUM_ASSOCIATE_GAP,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    RECOMMENDATION_CROSS_TRAIN,
    RECOMMENDATION_FULL_TIME_HIRING,
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW,
    RECOMMENDATION_NONE,
    RECOMMENDATION_SHIFT_REALIGNMENT,
    RECOMMENDATION_TEMPORARY_LABOR,
    RECOMMENDATION_WORKFORCE_REDUCTION,
    STAFFING_DOMAIN_VERSION,
    STATUS_APPROVED,
    STATUS_NOT_REQUIRED,
    STATUS_RECOMMENDED,
    STATUS_REVIEW_REQUIRED,
    SUPPORTED_RECOMMENDATION_PRIORITIES,
    SUPPORTED_RECOMMENDATION_STATUSES,
    SUPPORTED_RECOMMENDATION_TYPES,
    TEMPORARY_LABOR_TRIGGER_GAP,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    StaffingConfigurationError,
    StaffingEngineError,
    StaffingError,
    StaffingServiceError,
    StaffingValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    StaffingRecommendation,
    StaffingRecommendationPriority,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
)

# ============================================================
# Components
# ============================================================

from .configuration import StaffingConfiguration
from .engine import StaffingRecommendationEngine
from .service import StaffingRecommendationService


__all__ = [
    # Version
    "STAFFING_DOMAIN_VERSION",

    # Forecast confidence
    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    "LOW_CONFIDENCE_THRESHOLD",
    "HIGH_CONFIDENCE_THRESHOLD",

    # Staffing thresholds
    "MINIMUM_ASSOCIATE_GAP",
    "TEMPORARY_LABOR_TRIGGER_GAP",
    "FULL_TIME_HIRING_TRIGGER_GAP",
    "CRITICAL_SHORTAGE_GAP",

    # Recommendation values
    "RECOMMENDATION_NONE",
    "RECOMMENDATION_TEMPORARY_LABOR",
    "RECOMMENDATION_FULL_TIME_HIRING",
    "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
    "RECOMMENDATION_CROSS_TRAIN",
    "RECOMMENDATION_SHIFT_REALIGNMENT",
    "RECOMMENDATION_WORKFORCE_REDUCTION",

    # Priority values
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",
    "PRIORITY_HIGH",
    "PRIORITY_CRITICAL",

    # Status values
    "STATUS_NOT_REQUIRED",
    "STATUS_RECOMMENDED",
    "STATUS_REVIEW_REQUIRED",
    "STATUS_APPROVED",

    # Supported values
    "SUPPORTED_RECOMMENDATION_TYPES",
    "SUPPORTED_RECOMMENDATION_PRIORITIES",
    "SUPPORTED_RECOMMENDATION_STATUSES",

    # Exceptions
    "StaffingError",
    "StaffingValidationError",
    "StaffingConfigurationError",
    "StaffingEngineError",
    "StaffingServiceError",

    # Models and enums
    "StaffingRequest",
    "StaffingRecommendation",
    "StaffingRecommendationType",
    "StaffingRecommendationPriority",
    "StaffingRecommendationStatus",

    # Components
    "StaffingConfiguration",
    "StaffingRecommendationEngine",
    "StaffingRecommendationService",
]