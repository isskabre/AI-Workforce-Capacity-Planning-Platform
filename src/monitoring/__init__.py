"""
Implementation 23.8 — Enterprise Monitoring Package

Public API for the Enterprise Monitoring and Observability Framework.

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
    COMPONENT_FORECAST,
    COMPONENT_OPTIMIZATION,
    COMPONENT_ORCHESTRATION,
    COMPONENT_OVERTIME,
    COMPONENT_PLANNING,
    COMPONENT_PLATFORM,
    COMPONENT_REPORTING,
    COMPONENT_STAFFING,
    DEFAULT_CRITICAL_DURATION_MS,
    DEFAULT_CRITICAL_SUCCESS_RATE,
    DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
    DEFAULT_MONITORING_VERSION,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TIMEZONE,
    DEFAULT_WARNING_DURATION_MS,
    DEFAULT_WARNING_SUCCESS_RATE,
    EXECUTION_STATUS_CANCELLED,
    EXECUTION_STATUS_FAILED,
    EXECUTION_STATUS_PENDING,
    EXECUTION_STATUS_RUNNING,
    EXECUTION_STATUS_SUCCEEDED,
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_UNKNOWN,
    MAXIMUM_SUCCESS_RATE,
    METRIC_COMPONENT_AVAILABILITY,
    METRIC_EXECUTION_COUNT,
    METRIC_EXECUTION_DURATION_MS,
    METRIC_FAILURE_COUNT,
    METRIC_FAILURE_RATE,
    METRIC_HEALTH_CHECK_COUNT,
    METRIC_STAGE_DURATION_MS,
    METRIC_SUCCESS_COUNT,
    METRIC_SUCCESS_RATE,
    METRIC_TYPE_COUNTER,
    METRIC_TYPE_DISTRIBUTION,
    METRIC_TYPE_GAUGE,
    METRIC_TYPE_TIMER,
    MINIMUM_SUCCESS_RATE,
    MONITORING_DOMAIN_NAME,
    MONITORING_DOMAIN_VERSION,
    SEVERITY_CRITICAL,
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SUPPORTED_EXECUTION_STATUSES,
    SUPPORTED_HEALTH_STATUSES,
    SUPPORTED_METRIC_TYPES,
    SUPPORTED_MONITORING_COMPONENTS,
    SUPPORTED_SEVERITY_LEVELS,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    MonitoringConfigurationError,
    MonitoringError,
    MonitoringHealthCheckError,
    MonitoringMetricsError,
    MonitoringServiceError,
    MonitoringValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    ComponentHealth,
    ExecutionRecord,
    ExecutionStatus,
    HealthStatus,
    MetricRecord,
    MetricType,
    MonitoringAlert,
    PlatformHealthReport,
    SeverityLevel,
)

# ============================================================
# Components
# ============================================================

from .configuration import MonitoringConfiguration
from .health import (
    HealthCheckCallable,
    MonitoringHealthService,
)
from .metrics import MonitoringMetricsService
from .service import EnterpriseMonitoringService


__all__ = [
    # Domain
    "MONITORING_DOMAIN_NAME",
    "MONITORING_DOMAIN_VERSION",

    # Health constants
    "HEALTH_STATUS_HEALTHY",
    "HEALTH_STATUS_DEGRADED",
    "HEALTH_STATUS_UNHEALTHY",
    "HEALTH_STATUS_UNKNOWN",
    "SUPPORTED_HEALTH_STATUSES",

    # Execution constants
    "EXECUTION_STATUS_PENDING",
    "EXECUTION_STATUS_RUNNING",
    "EXECUTION_STATUS_SUCCEEDED",
    "EXECUTION_STATUS_FAILED",
    "EXECUTION_STATUS_CANCELLED",
    "SUPPORTED_EXECUTION_STATUSES",

    # Severity constants
    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "SEVERITY_ERROR",
    "SEVERITY_CRITICAL",
    "SUPPORTED_SEVERITY_LEVELS",

    # Metric type constants
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

    # Exceptions
    "MonitoringError",
    "MonitoringValidationError",
    "MonitoringConfigurationError",
    "MonitoringMetricsError",
    "MonitoringHealthCheckError",
    "MonitoringServiceError",

    # Models and enums
    "MetricRecord",
    "ExecutionRecord",
    "ComponentHealth",
    "MonitoringAlert",
    "PlatformHealthReport",
    "MetricType",
    "ExecutionStatus",
    "HealthStatus",
    "SeverityLevel",

    # Components
    "MonitoringConfiguration",
    "MonitoringMetricsService",
    "MonitoringHealthService",
    "HealthCheckCallable",
    "EnterpriseMonitoringService",
]