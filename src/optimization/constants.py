"""
Enterprise Workforce Optimization Constants

Shared constants for the enterprise workforce optimization framework.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

# ============================================================
# Version
# ============================================================

OPTIMIZATION_DOMAIN_VERSION = "1.0.0"

# ============================================================
# Forecast confidence
# ============================================================

MIN_FORECAST_CONFIDENCE = 0.0
MAX_FORECAST_CONFIDENCE = 1.0

DEFAULT_FORECAST_CONFIDENCE = 0.80

# ============================================================
# Optimization priorities
# ============================================================

OPTIMIZATION_PRIORITY_LOW = "LOW"
OPTIMIZATION_PRIORITY_MEDIUM = "MEDIUM"
OPTIMIZATION_PRIORITY_HIGH = "HIGH"
OPTIMIZATION_PRIORITY_CRITICAL = "CRITICAL"

SUPPORTED_OPTIMIZATION_PRIORITIES = (
    OPTIMIZATION_PRIORITY_LOW,
    OPTIMIZATION_PRIORITY_MEDIUM,
    OPTIMIZATION_PRIORITY_HIGH,
    OPTIMIZATION_PRIORITY_CRITICAL,
)

# ============================================================
# Optimization status
# ============================================================

OPTIMIZATION_STATUS_OPTIMAL = "OPTIMAL"
OPTIMIZATION_STATUS_ACCEPTABLE = "ACCEPTABLE"
OPTIMIZATION_STATUS_REVIEW = "REVIEW"
OPTIMIZATION_STATUS_CRITICAL = "CRITICAL"

SUPPORTED_OPTIMIZATION_STATUSES = (
    OPTIMIZATION_STATUS_OPTIMAL,
    OPTIMIZATION_STATUS_ACCEPTABLE,
    OPTIMIZATION_STATUS_REVIEW,
    OPTIMIZATION_STATUS_CRITICAL,
)

# ============================================================
# Workforce actions
# ============================================================

ACTION_NONE = "NONE"
ACTION_OVERTIME = "OVERTIME"
ACTION_TEMPORARY_LABOR = "TEMPORARY_LABOR"
ACTION_FULL_TIME_HIRING = "FULL_TIME_HIRING"
ACTION_SHIFT_REALIGNMENT = "SHIFT_REALIGNMENT"
ACTION_CROSS_TRAINING = "CROSS_TRAINING"

SUPPORTED_WORKFORCE_ACTIONS = (
    ACTION_NONE,
    ACTION_OVERTIME,
    ACTION_TEMPORARY_LABOR,
    ACTION_FULL_TIME_HIRING,
    ACTION_SHIFT_REALIGNMENT,
    ACTION_CROSS_TRAINING,
)

# ============================================================
# Public API
# ============================================================

__all__ = [
    "OPTIMIZATION_DOMAIN_VERSION",

    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",

    "OPTIMIZATION_PRIORITY_LOW",
    "OPTIMIZATION_PRIORITY_MEDIUM",
    "OPTIMIZATION_PRIORITY_HIGH",
    "OPTIMIZATION_PRIORITY_CRITICAL",
    "SUPPORTED_OPTIMIZATION_PRIORITIES",

    "OPTIMIZATION_STATUS_OPTIMAL",
    "OPTIMIZATION_STATUS_ACCEPTABLE",
    "OPTIMIZATION_STATUS_REVIEW",
    "OPTIMIZATION_STATUS_CRITICAL",
    "SUPPORTED_OPTIMIZATION_STATUSES",

    "ACTION_NONE",
    "ACTION_OVERTIME",
    "ACTION_TEMPORARY_LABOR",
    "ACTION_FULL_TIME_HIRING",
    "ACTION_SHIFT_REALIGNMENT",
    "ACTION_CROSS_TRAINING",
    "SUPPORTED_WORKFORCE_ACTIONS",
]