"""
Enterprise Workforce Optimization

Public API for the enterprise workforce optimization domain.

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
    ACTION_CROSS_TRAINING,
    ACTION_FULL_TIME_HIRING,
    ACTION_NONE,
    ACTION_OVERTIME,
    ACTION_SHIFT_REALIGNMENT,
    ACTION_TEMPORARY_LABOR,
    DEFAULT_FORECAST_CONFIDENCE,
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
    OPTIMIZATION_DOMAIN_VERSION,
    OPTIMIZATION_PRIORITY_CRITICAL,
    OPTIMIZATION_PRIORITY_HIGH,
    OPTIMIZATION_PRIORITY_LOW,
    OPTIMIZATION_PRIORITY_MEDIUM,
    OPTIMIZATION_STATUS_ACCEPTABLE,
    OPTIMIZATION_STATUS_CRITICAL,
    OPTIMIZATION_STATUS_OPTIMAL,
    OPTIMIZATION_STATUS_REVIEW,
    SUPPORTED_OPTIMIZATION_PRIORITIES,
    SUPPORTED_OPTIMIZATION_STATUSES,
    SUPPORTED_WORKFORCE_ACTIONS,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    OptimizationConfigurationError,
    OptimizationConflictError,
    OptimizationEngineError,
    OptimizationError,
    OptimizationServiceError,
    OptimizationValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationDecision,
    WorkforceOptimizationRequest,
)

# ============================================================
# Components
# ============================================================

from .configuration import WorkforceOptimizationConfiguration
from .engine import WorkforceOptimizationEngine
from .service import WorkforceOptimizationService


__all__ = [
    # Version
    "OPTIMIZATION_DOMAIN_VERSION",

    # Forecast confidence
    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",

    # Priority constants
    "OPTIMIZATION_PRIORITY_LOW",
    "OPTIMIZATION_PRIORITY_MEDIUM",
    "OPTIMIZATION_PRIORITY_HIGH",
    "OPTIMIZATION_PRIORITY_CRITICAL",
    "SUPPORTED_OPTIMIZATION_PRIORITIES",

    # Status constants
    "OPTIMIZATION_STATUS_OPTIMAL",
    "OPTIMIZATION_STATUS_ACCEPTABLE",
    "OPTIMIZATION_STATUS_REVIEW",
    "OPTIMIZATION_STATUS_CRITICAL",
    "SUPPORTED_OPTIMIZATION_STATUSES",

    # Workforce action constants
    "ACTION_NONE",
    "ACTION_OVERTIME",
    "ACTION_TEMPORARY_LABOR",
    "ACTION_FULL_TIME_HIRING",
    "ACTION_SHIFT_REALIGNMENT",
    "ACTION_CROSS_TRAINING",
    "SUPPORTED_WORKFORCE_ACTIONS",

    # Exceptions
    "OptimizationError",
    "OptimizationValidationError",
    "OptimizationConfigurationError",
    "OptimizationConflictError",
    "OptimizationEngineError",
    "OptimizationServiceError",

    # Models and enums
    "OptimizationPriority",
    "OptimizationStatus",
    "WorkforceAction",
    "WorkforceOptimizationRequest",
    "WorkforceOptimizationDecision",

    # Components
    "WorkforceOptimizationConfiguration",
    "WorkforceOptimizationEngine",
    "WorkforceOptimizationService",
]