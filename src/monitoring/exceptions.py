"""
Implementation 23.2 — Enterprise Monitoring Exceptions

Exception hierarchy for the Enterprise Monitoring and Observability
Framework.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


class MonitoringError(Exception):
    """
    Base exception for all monitoring and observability failures.
    """


class MonitoringValidationError(MonitoringError):
    """
    Raised when a monitoring request, metric, event, or health result
    is invalid.
    """


class MonitoringConfigurationError(MonitoringError):
    """
    Raised when monitoring configuration is invalid.
    """


class MonitoringMetricsError(MonitoringError):
    """
    Raised when metric recording, calculation, or aggregation fails.
    """


class MonitoringHealthCheckError(MonitoringError):
    """
    Raised when a component health check cannot be completed.
    """


class MonitoringServiceError(MonitoringError):
    """
    Raised when the monitoring service cannot complete execution.
    """


__all__ = [
    "MonitoringConfigurationError",
    "MonitoringError",
    "MonitoringHealthCheckError",
    "MonitoringMetricsError",
    "MonitoringServiceError",
    "MonitoringValidationError",
]