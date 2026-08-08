"""
Enterprise Staffing Recommendation Constants

Enterprise constants for strategic staffing recommendation decisions.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

# ============================================================================
# Domain
# ============================================================================

STAFFING_DOMAIN_VERSION = "1.0.0"

# ============================================================================
# Forecast Confidence
# ============================================================================

MIN_FORECAST_CONFIDENCE = 0.0
MAX_FORECAST_CONFIDENCE = 1.0

DEFAULT_FORECAST_CONFIDENCE = 0.80

# ============================================================================
# Staffing Thresholds
# ============================================================================

MINIMUM_ASSOCIATE_GAP = 1

TEMPORARY_LABOR_TRIGGER_GAP = 5
FULL_TIME_HIRING_TRIGGER_GAP = 15
CRITICAL_SHORTAGE_GAP = 25

DEFAULT_RECOMMENDATION_CONFIDENCE = 0.80

LOW_CONFIDENCE_THRESHOLD = 0.60
HIGH_CONFIDENCE_THRESHOLD = 0.90

# ============================================================================
# Recommendation Types
# ============================================================================

RECOMMENDATION_NONE = "NONE"

RECOMMENDATION_TEMPORARY_LABOR = "TEMPORARY_LABOR"

RECOMMENDATION_FULL_TIME_HIRING = "FULL_TIME_HIRING"

RECOMMENDATION_FULL_TIME_HIRING_REVIEW = (
    "FULL_TIME_HIRING_REVIEW"
)

RECOMMENDATION_CROSS_TRAIN = "CROSS_TRAIN"

RECOMMENDATION_SHIFT_REALIGNMENT = (
    "SHIFT_REALIGNMENT"
)

RECOMMENDATION_WORKFORCE_REDUCTION = (
    "WORKFORCE_REDUCTION"
)

# ============================================================================
# Recommendation Priority
# ============================================================================

PRIORITY_LOW = "LOW"

PRIORITY_MEDIUM = "MEDIUM"

PRIORITY_HIGH = "HIGH"

PRIORITY_CRITICAL = "CRITICAL"

# ============================================================================
# Recommendation Status
# ============================================================================

STATUS_NOT_REQUIRED = "NOT_REQUIRED"

STATUS_RECOMMENDED = "RECOMMENDED"

STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"

STATUS_APPROVED = "APPROVED"

# ============================================================================
# Supported Collections
# ============================================================================

SUPPORTED_RECOMMENDATION_TYPES = (
    RECOMMENDATION_NONE,
    RECOMMENDATION_TEMPORARY_LABOR,
    RECOMMENDATION_FULL_TIME_HIRING,
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW,
    RECOMMENDATION_CROSS_TRAIN,
    RECOMMENDATION_SHIFT_REALIGNMENT,
    RECOMMENDATION_WORKFORCE_REDUCTION,
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
    STATUS_REVIEW_REQUIRED,
    STATUS_APPROVED,
)