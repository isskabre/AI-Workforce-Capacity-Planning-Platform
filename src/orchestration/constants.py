"""
Enterprise Decision Orchestration Constants.

Defines immutable constants shared across the enterprise decision
orchestration framework.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

# ============================================================
# Domain
# ============================================================

ORCHESTRATION_DOMAIN_NAME = "enterprise-decision-orchestration"
ORCHESTRATION_DOMAIN_VERSION = "1.0.0"

# ============================================================
# Forecast Confidence
# ============================================================

MIN_FORECAST_CONFIDENCE = 0.0
MAX_FORECAST_CONFIDENCE = 1.0

DEFAULT_FORECAST_CONFIDENCE = 0.80

# ============================================================
# Workflow Stages
# ============================================================

STAGE_FORECAST = "forecast"
STAGE_PLANNING = "planning"
STAGE_OVERTIME = "overtime"
STAGE_STAFFING = "staffing"
STAGE_OPTIMIZATION = "optimization"
STAGE_COMPLETE = "complete"

ORCHESTRATION_STAGES = (
    STAGE_FORECAST,
    STAGE_PLANNING,
    STAGE_OVERTIME,
    STAGE_STAFFING,
    STAGE_OPTIMIZATION,
    STAGE_COMPLETE,
)

# ============================================================
# Workflow Status
# ============================================================

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"

SUPPORTED_ORCHESTRATION_STATUSES = (
    STATUS_PENDING,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_FAILED,
)

# ============================================================
# Workflow Names
# ============================================================

WORKFLOW_ENTERPRISE_DECISION = (
    "enterprise_workforce_decision"
)

WORKFLOW_CAPACITY_PLANNING = (
    "capacity_planning_pipeline"
)

# ============================================================
# Execution Order
# ============================================================

EXECUTION_ORDER = (
    STAGE_FORECAST,
    STAGE_PLANNING,
    STAGE_OVERTIME,
    STAGE_STAFFING,
    STAGE_OPTIMIZATION,
)

# ============================================================
# Package Exports
# ============================================================

__all__ = [
    "DEFAULT_FORECAST_CONFIDENCE",
    "EXECUTION_ORDER",
    "MAX_FORECAST_CONFIDENCE",
    "MIN_FORECAST_CONFIDENCE",
    "ORCHESTRATION_DOMAIN_NAME",
    "ORCHESTRATION_DOMAIN_VERSION",
    "ORCHESTRATION_STAGES",
    "STAGE_COMPLETE",
    "STAGE_FORECAST",
    "STAGE_OPTIMIZATION",
    "STAGE_OVERTIME",
    "STAGE_PLANNING",
    "STAGE_STAFFING",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_PENDING",
    "STATUS_RUNNING",
    "SUPPORTED_ORCHESTRATION_STATUSES",
    "WORKFLOW_CAPACITY_PLANNING",
    "WORKFLOW_ENTERPRISE_DECISION",
]