"""
Enterprise Capacity Planning

Public API for the enterprise capacity planning domain.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

# ============================================================
# Constants
# ============================================================

from .constants import (
    PLANNING_DOMAIN_VERSION,
    MIN_FORECAST_CONFIDENCE,
    MAX_FORECAST_CONFIDENCE,
    DEFAULT_FORECAST_CONFIDENCE,
    MINIMUM_ASSOCIATES,
    MAXIMUM_ASSOCIATES,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SCHEDULED_HOURS,
    MINIMUM_OVERTIME_HOURS,
    MAXIMUM_OVERTIME_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    CapacityPlanningError,
    CapacityPlanningValidationError,
    CapacityPlanningConfigurationError,
    CapacityPlanningCalculationError,
    CapacityPlanningEngineError,
    CapacityPlanningReportingError,
    CapacityPlanningServiceError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    CapacityPlanningRequest,
    CapacityPlanningResult,
)

# ============================================================
# Components
# ============================================================

from .configuration import CapacityPlanningConfiguration
from .engine import CapacityPlanningEngine
from .reporting import (
    CapacityPlanningReport,
    CapacityPlanningReporter,
)
from .service import CapacityPlanningService


__all__ = [
    # Constants
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

    # Exceptions
    "CapacityPlanningError",
    "CapacityPlanningValidationError",
    "CapacityPlanningConfigurationError",
    "CapacityPlanningCalculationError",
    "CapacityPlanningEngineError",
    "CapacityPlanningReportingError",
    "CapacityPlanningServiceError",

    # Models
    "CapacityPlanningRequest",
    "CapacityPlanningResult",

    # Components
    "CapacityPlanningConfiguration",
    "CapacityPlanningEngine",
    "CapacityPlanningReport",
    "CapacityPlanningReporter",
    "CapacityPlanningService",
]