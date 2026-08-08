"""
Enterprise Capacity Planning Constants

Shared constants used across the enterprise capacity planning domain.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

# ============================================================
# Domain
# ============================================================

PLANNING_DOMAIN_VERSION = "1.0.0"

# ============================================================
# Forecast Confidence
# ============================================================

MIN_FORECAST_CONFIDENCE = 0.0
MAX_FORECAST_CONFIDENCE = 1.0

DEFAULT_FORECAST_CONFIDENCE = 0.80

# ============================================================
# Workforce Constraints
# ============================================================

MINIMUM_ASSOCIATES = 1
MAXIMUM_ASSOCIATES = 10_000

# ============================================================
# Productivity
# ============================================================

DEFAULT_PRODUCTIVITY_LINES_PER_HOUR = 120.0

# ============================================================
# Scheduling
# ============================================================

DEFAULT_SCHEDULED_HOURS = 10.0

MINIMUM_OVERTIME_HOURS = 5.0
MAXIMUM_OVERTIME_HOURS = 10.0

# ============================================================
# Capacity Planning
# ============================================================

DEFAULT_TARGET_UTILIZATION = 0.90

DEFAULT_SAFETY_BUFFER_RATIO = 0.05

DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP = 1

# ============================================================
# Public API
# ============================================================

__all__ = [
    "PLANNING_DOMAIN_VERSION",
    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",
    "MINIMUM_ASSOCIATES",
    "MAXIMUM_ASSOCIATES",
    "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
    "DEFAULT_SCHEDULED_HOURS",
    "MINIMUM_OVERTIME_HOURS",
    "MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_TARGET_UTILIZATION",
    "DEFAULT_SAFETY_BUFFER_RATIO",
    "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",
]