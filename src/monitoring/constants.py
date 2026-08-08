"""
Enterprise Monitoring and Observability Constants

Centralized constants for platform health, execution monitoring,
metrics collection, and observability.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


# ============================================================
# Domain
# ============================================================

MONITORING_DOMAIN_NAME = "enterprise-monitoring-observability"

MONITORING_DOMAIN_VERSION = "1.0.0"


# ============================================================
# Health Statuses
# ============================================================

HEALTH_STATUS_HEALTHY = "HEALTHY"

HEALTH_STATUS_DEGRADED = "DEGRADED"

HEALTH_STATUS_UNHEALTHY = "UNHEALTHY"

HEALTH_STATUS_UNKNOWN = "UNKNOWN"

SUPPORTED_HEALTH_STATUSES = (
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_UNKNOWN,
)


# ============================================================
# Execution Statuses
# ============================================================

EXECUTION_STATUS_PENDING = "PENDING"

EXECUTION_STATUS_RUNNING = "RUNNING"

EXECUTION_STATUS_SUCCEEDED = "SUCCEEDED"

EXECUTION_STATUS_FAILED = "FAILED"

EXECUTION_STATUS_CANCELLED = "CANCELLED"

SUPPORTED_EXECUTION_STATUSES = (
    EXECUTION_STATUS_PENDING,
    EXECUTION_STATUS_RUNNING,
    EXECUTION_STATUS_SUCCEEDED,
    EXECUTION_STATUS_FAILED,
    EXECUTION_STATUS_CANCELLED,
)


# ============================================================
# Severity Levels
# ============================================================

SEVERITY_INFO = "INFO"

SEVERITY_WARNING = "WARNING"

SEVERITY_ERROR = "ERROR"

SEVERITY_CRITICAL = "CRITICAL"

SUPPORTED_SEVERITY_LEVELS = (
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_ERROR,
    SEVERITY_CRITICAL,
)


# ============================================================
# Metric Types
# ============================================================

METRIC_TYPE_COUNTER = "COUNTER"

METRIC_TYPE_GAUGE = "GAUGE"

METRIC_TYPE_TIMER = "TIMER"

METRIC_TYPE_DISTRIBUTION = "DISTRIBUTION"

SUPPORTED_METRIC_TYPES = (
    METRIC_TYPE_COUNTER,
    METRIC_TYPE_GAUGE,
    METRIC_TYPE_TIMER,
    METRIC_TYPE_DISTRIBUTION,
)


# ============================================================
# Metric Names
# ============================================================

METRIC_EXECUTION_COUNT = "execution_count"

METRIC_EXECUTION_DURATION_MS = "execution_duration_ms"

METRIC_SUCCESS_COUNT = "success_count"

METRIC_FAILURE_COUNT = "failure_count"

METRIC_SUCCESS_RATE = "success_rate"

METRIC_FAILURE_RATE = "failure_rate"

METRIC_STAGE_DURATION_MS = "stage_duration_ms"

METRIC_HEALTH_CHECK_COUNT = "health_check_count"

METRIC_COMPONENT_AVAILABILITY = "component_availability"


# ============================================================
# Monitoring Components
# ============================================================

COMPONENT_FORECAST = "forecast"

COMPONENT_PLANNING = "planning"

COMPONENT_OVERTIME = "overtime"

COMPONENT_STAFFING = "staffing"

COMPONENT_OPTIMIZATION = "optimization"

COMPONENT_ORCHESTRATION = "orchestration"

COMPONENT_REPORTING = "reporting"

COMPONENT_PLATFORM = "platform"

SUPPORTED_MONITORING_COMPONENTS = (
    COMPONENT_FORECAST,
    COMPONENT_PLANNING,
    COMPONENT_OVERTIME,
    COMPONENT_STAFFING,
    COMPONENT_OPTIMIZATION,
    COMPONENT_ORCHESTRATION,
    COMPONENT_REPORTING,
    COMPONENT_PLATFORM,
)


# ============================================================
# Thresholds
# ============================================================

MINIMUM_SUCCESS_RATE = 0.0

MAXIMUM_SUCCESS_RATE = 1.0

DEFAULT_WARNING_SUCCESS_RATE = 0.95

DEFAULT_CRITICAL_SUCCESS_RATE = 0.80

DEFAULT_WARNING_DURATION_MS = 5_000.0

DEFAULT_CRITICAL_DURATION_MS = 15_000.0

DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS = 30.0


# ============================================================
# Metadata
# ============================================================

DEFAULT_MONITORING_VERSION = "1.0.0"

DEFAULT_TIMEZONE = "UTC"

DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


# ============================================================
# Public API
# ============================================================

__all__ = [
    # Domain
    "MONITORING_DOMAIN_NAME",
    "MONITORING_DOMAIN_VERSION",

    # Health
    "HEALTH_STATUS_HEALTHY",
    "HEALTH_STATUS_DEGRADED",
    "HEALTH_STATUS_UNHEALTHY",
    "HEALTH_STATUS_UNKNOWN",
    "SUPPORTED_HEALTH_STATUSES",

    # Execution
    "EXECUTION_STATUS_PENDING",
    "EXECUTION_STATUS_RUNNING",
    "EXECUTION_STATUS_SUCCEEDED",
    "EXECUTION_STATUS_FAILED",
    "EXECUTION_STATUS_CANCELLED",
    "SUPPORTED_EXECUTION_STATUSES",

    # Severity
    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "SEVERITY_ERROR",
    "SEVERITY_CRITICAL",
    "SUPPORTED_SEVERITY_LEVELS",

    # Metric types
    "METRIC_TYPE_COUNTER",
    "METRIC_TYPE_GAUGE",
    "METRIC_TYPE_TIMER",
    "METRIC_TYPE_DISTRIBUTION",
    "SUPPORTED_METRIC_TYPES",

    # Metric names
    "METRIC_EXECUTION_COUNT",
    "METRIC_EXECUTION_DURATION_MS",
    "METRIC_SUCCESS_COUNT",
    "METRIC_FAILURE_COUNT",
    "METRIC_SUCCESS_RATE",
    "METRIC_FAILURE_RATE",
    "METRIC_STAGE_DURATION_MS",
    "METRIC_HEALTH_CHECK_COUNT",
    "METRIC_COMPONENT_AVAILABILITY",

    # Components
    "COMPONENT_FORECAST",
    "COMPONENT_PLANNING",
    "COMPONENT_OVERTIME",
    "COMPONENT_STAFFING",
    "COMPONENT_OPTIMIZATION",
    "COMPONENT_ORCHESTRATION",
    "COMPONENT_REPORTING",
    "COMPONENT_PLATFORM",
    "SUPPORTED_MONITORING_COMPONENTS",

    # Thresholds
    "MINIMUM_SUCCESS_RATE",
    "MAXIMUM_SUCCESS_RATE",
    "DEFAULT_WARNING_SUCCESS_RATE",
    "DEFAULT_CRITICAL_SUCCESS_RATE",
    "DEFAULT_WARNING_DURATION_MS",
    "DEFAULT_CRITICAL_DURATION_MS",
    "DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS",

    # Metadata
    "DEFAULT_MONITORING_VERSION",
    "DEFAULT_TIMEZONE",
    "DEFAULT_TIMESTAMP_FORMAT",
]