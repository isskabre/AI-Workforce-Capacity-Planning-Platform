"""
Implementation 23.3 — Enterprise Monitoring Models

Typed domain contracts for execution monitoring, metric collection,
health checks, alerts, and platform observability.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping

from .constants import (
    SUPPORTED_EXECUTION_STATUSES,
    SUPPORTED_HEALTH_STATUSES,
    SUPPORTED_METRIC_TYPES,
    SUPPORTED_MONITORING_COMPONENTS,
    SUPPORTED_SEVERITY_LEVELS,
)
from .exceptions import MonitoringValidationError


# ============================================================
# Enumerations
# ============================================================

class HealthStatus(str, Enum):
    """
    Supported component and platform health statuses.
    """

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class ExecutionStatus(str, Enum):
    """
    Supported execution lifecycle statuses.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SeverityLevel(str, Enum):
    """
    Supported monitoring severity levels.
    """

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(str, Enum):
    """
    Supported monitoring metric types.
    """

    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    TIMER = "TIMER"
    DISTRIBUTION = "DISTRIBUTION"


# ============================================================
# Metric Record
# ============================================================

@dataclass(frozen=True, slots=True)
class MetricRecord:
    """
    One immutable monitoring metric observation.

    Parameters
    ----------
    name:
        Stable metric name.

    metric_type:
        Counter, gauge, timer, or distribution.

    component:
        Platform component that emitted the metric.

    value:
        Numeric metric value.

    recorded_at_utc:
        UTC metric timestamp.

    unit:
        Optional unit such as milliseconds, count, or ratio.

    tags:
        Optional dimensions used for filtering and aggregation.
    """

    name: str

    metric_type: MetricType

    component: str

    value: float

    recorded_at_utc: datetime

    unit: str = ""

    tags: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the metric record.
        """

        if not isinstance(self.name, str) or not self.name.strip():
            raise MonitoringValidationError(
                "Metric name must not be empty."
            )

        if not isinstance(self.metric_type, MetricType):
            raise MonitoringValidationError(
                "metric_type must be a MetricType."
            )

        if self.metric_type.value not in SUPPORTED_METRIC_TYPES:
            raise MonitoringValidationError(
                "Unsupported metric_type."
            )

        if (
            not isinstance(self.component, str)
            or self.component not in SUPPORTED_MONITORING_COMPONENTS
        ):
            raise MonitoringValidationError(
                "component is not supported."
            )

        if (
            not isinstance(self.value, (int, float))
            or isinstance(self.value, bool)
            or not isfinite(float(self.value))
        ):
            raise MonitoringValidationError(
                "Metric value must be a finite numeric value."
            )

        if not isinstance(self.recorded_at_utc, datetime):
            raise MonitoringValidationError(
                "recorded_at_utc must be a datetime."
            )

        if not isinstance(self.unit, str):
            raise MonitoringValidationError(
                "unit must be a string."
            )

        if not isinstance(self.tags, Mapping):
            raise MonitoringValidationError(
                "tags must be a mapping."
            )

        for key, value in self.tags.items():
            if (
                not isinstance(key, str)
                or not key.strip()
                or not isinstance(value, str)
            ):
                raise MonitoringValidationError(
                    "Metric tags must contain non-empty string keys "
                    "and string values."
                )

        if (
            self.metric_type is MetricType.COUNTER
            and self.value < 0
        ):
            raise MonitoringValidationError(
                "Counter metrics must be non-negative."
            )

        if (
            self.metric_type is MetricType.TIMER
            and self.value < 0
        ):
            raise MonitoringValidationError(
                "Timer metrics must be non-negative."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the metric as a serializable dictionary.
        """

        return {
            "name": self.name,
            "metric_type": self.metric_type.value,
            "component": self.component,
            "value": float(self.value),
            "recorded_at_utc": self.recorded_at_utc.isoformat(),
            "unit": self.unit,
            "tags": dict(self.tags),
        }


# ============================================================
# Execution Record
# ============================================================

@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    """
    Immutable record describing one monitored execution.

    Parameters
    ----------
    execution_id:
        Stable execution identifier.

    component:
        Monitored platform component.

    operation:
        Business or technical operation executed.

    status:
        Execution lifecycle status.

    started_at_utc:
        UTC execution start time.

    completed_at_utc:
        Optional UTC completion time.

    duration_ms:
        Optional execution duration.

    message:
        Optional operational message.

    metadata:
        Optional execution metadata.
    """

    execution_id: str

    component: str

    operation: str

    status: ExecutionStatus

    started_at_utc: datetime

    completed_at_utc: datetime | None = None

    duration_ms: float | None = None

    message: str = ""

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the execution record.
        """

        if (
            not isinstance(self.execution_id, str)
            or not self.execution_id.strip()
        ):
            raise MonitoringValidationError(
                "execution_id must not be empty."
            )

        if (
            not isinstance(self.component, str)
            or self.component not in SUPPORTED_MONITORING_COMPONENTS
        ):
            raise MonitoringValidationError(
                "component is not supported."
            )

        if (
            not isinstance(self.operation, str)
            or not self.operation.strip()
        ):
            raise MonitoringValidationError(
                "operation must not be empty."
            )

        if not isinstance(self.status, ExecutionStatus):
            raise MonitoringValidationError(
                "status must be an ExecutionStatus."
            )

        if self.status.value not in SUPPORTED_EXECUTION_STATUSES:
            raise MonitoringValidationError(
                "Unsupported execution status."
            )

        if not isinstance(self.started_at_utc, datetime):
            raise MonitoringValidationError(
                "started_at_utc must be a datetime."
            )

        if (
            self.completed_at_utc is not None
            and not isinstance(self.completed_at_utc, datetime)
        ):
            raise MonitoringValidationError(
                "completed_at_utc must be a datetime or None."
            )

        if (
            self.completed_at_utc is not None
            and self.completed_at_utc < self.started_at_utc
        ):
            raise MonitoringValidationError(
                "completed_at_utc cannot be earlier than "
                "started_at_utc."
            )

        if self.duration_ms is not None:
            if (
                not isinstance(self.duration_ms, (int, float))
                or isinstance(self.duration_ms, bool)
                or not isfinite(float(self.duration_ms))
                or self.duration_ms < 0
            ):
                raise MonitoringValidationError(
                    "duration_ms must be a non-negative finite value "
                    "or None."
                )

        if (
            self.completed_at_utc is None
            and self.duration_ms is not None
        ):
            raise MonitoringValidationError(
                "duration_ms requires completed_at_utc."
            )

        if self.status in {
            ExecutionStatus.SUCCEEDED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        }:
            if self.completed_at_utc is None:
                raise MonitoringValidationError(
                    "Terminal execution statuses require "
                    "completed_at_utc."
                )

        if self.status in {
            ExecutionStatus.PENDING,
            ExecutionStatus.RUNNING,
        }:
            if self.completed_at_utc is not None:
                raise MonitoringValidationError(
                    "Non-terminal execution statuses cannot have "
                    "completed_at_utc."
                )

        if not isinstance(self.message, str):
            raise MonitoringValidationError(
                "message must be a string."
            )

        if not isinstance(self.metadata, Mapping):
            raise MonitoringValidationError(
                "metadata must be a mapping."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the execution record as a serializable dictionary.
        """

        return {
            "execution_id": self.execution_id,
            "component": self.component,
            "operation": self.operation,
            "status": self.status.value,
            "started_at_utc": self.started_at_utc.isoformat(),
            "completed_at_utc": (
                self.completed_at_utc.isoformat()
                if self.completed_at_utc is not None
                else None
            ),
            "duration_ms": (
                float(self.duration_ms)
                if self.duration_ms is not None
                else None
            ),
            "message": self.message,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Component Health
# ============================================================

@dataclass(frozen=True, slots=True)
class ComponentHealth:
    """
    Immutable component health-check result.

    Parameters
    ----------
    component:
        Monitored platform component.

    status:
        Current health status.

    checked_at_utc:
        UTC health-check timestamp.

    response_time_ms:
        Time required to complete the health check.

    message:
        Human-readable health explanation.

    details:
        Optional structured health details.
    """

    component: str

    status: HealthStatus

    checked_at_utc: datetime

    response_time_ms: float

    message: str

    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the component health result.
        """

        if (
            not isinstance(self.component, str)
            or self.component not in SUPPORTED_MONITORING_COMPONENTS
        ):
            raise MonitoringValidationError(
                "component is not supported."
            )

        if not isinstance(self.status, HealthStatus):
            raise MonitoringValidationError(
                "status must be a HealthStatus."
            )

        if self.status.value not in SUPPORTED_HEALTH_STATUSES:
            raise MonitoringValidationError(
                "Unsupported health status."
            )

        if not isinstance(self.checked_at_utc, datetime):
            raise MonitoringValidationError(
                "checked_at_utc must be a datetime."
            )

        if (
            not isinstance(self.response_time_ms, (int, float))
            or isinstance(self.response_time_ms, bool)
            or not isfinite(float(self.response_time_ms))
            or self.response_time_ms < 0
        ):
            raise MonitoringValidationError(
                "response_time_ms must be a non-negative finite value."
            )

        if not isinstance(self.message, str) or not self.message.strip():
            raise MonitoringValidationError(
                "Health message must not be empty."
            )

        if not isinstance(self.details, Mapping):
            raise MonitoringValidationError(
                "details must be a mapping."
            )

    @property
    def is_available(self) -> bool:
        """
        Return whether the component is operationally available.
        """

        return self.status in {
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
        }

    def as_dict(self) -> dict[str, Any]:
        """
        Return the health result as a serializable dictionary.
        """

        return {
            "component": self.component,
            "status": self.status.value,
            "checked_at_utc": self.checked_at_utc.isoformat(),
            "response_time_ms": float(self.response_time_ms),
            "message": self.message,
            "is_available": self.is_available,
            "details": dict(self.details),
        }


# ============================================================
# Monitoring Alert
# ============================================================

@dataclass(frozen=True, slots=True)
class MonitoringAlert:
    """
    Immutable monitoring alert contract.

    Parameters
    ----------
    alert_id:
        Stable alert identifier.

    component:
        Component associated with the alert.

    severity:
        Alert severity level.

    title:
        Concise alert title.

    message:
        Detailed alert description.

    created_at_utc:
        UTC alert creation timestamp.

    metric_name:
        Optional triggering metric.

    observed_value:
        Optional observed metric value.

    threshold_value:
        Optional policy threshold.

    metadata:
        Optional alert metadata.
    """

    alert_id: str

    component: str

    severity: SeverityLevel

    title: str

    message: str

    created_at_utc: datetime

    metric_name: str = ""

    observed_value: float | None = None

    threshold_value: float | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the monitoring alert.
        """

        if (
            not isinstance(self.alert_id, str)
            or not self.alert_id.strip()
        ):
            raise MonitoringValidationError(
                "alert_id must not be empty."
            )

        if (
            not isinstance(self.component, str)
            or self.component not in SUPPORTED_MONITORING_COMPONENTS
        ):
            raise MonitoringValidationError(
                "component is not supported."
            )

        if not isinstance(self.severity, SeverityLevel):
            raise MonitoringValidationError(
                "severity must be a SeverityLevel."
            )

        if self.severity.value not in SUPPORTED_SEVERITY_LEVELS:
            raise MonitoringValidationError(
                "Unsupported severity level."
            )

        if not isinstance(self.title, str) or not self.title.strip():
            raise MonitoringValidationError(
                "Alert title must not be empty."
            )

        if not isinstance(self.message, str) or not self.message.strip():
            raise MonitoringValidationError(
                "Alert message must not be empty."
            )

        if not isinstance(self.created_at_utc, datetime):
            raise MonitoringValidationError(
                "created_at_utc must be a datetime."
            )

        if not isinstance(self.metric_name, str):
            raise MonitoringValidationError(
                "metric_name must be a string."
            )

        optional_numeric_fields = {
            "observed_value": self.observed_value,
            "threshold_value": self.threshold_value,
        }

        for field_name, field_value in optional_numeric_fields.items():
            if field_value is not None:
                if (
                    not isinstance(field_value, (int, float))
                    or isinstance(field_value, bool)
                    or not isfinite(float(field_value))
                ):
                    raise MonitoringValidationError(
                        f"{field_name} must be a finite numeric value "
                        "or None."
                    )

        if (
            not self.metric_name
            and (
                self.observed_value is not None
                or self.threshold_value is not None
            )
        ):
            raise MonitoringValidationError(
                "Metric values require metric_name."
            )

        if not isinstance(self.metadata, Mapping):
            raise MonitoringValidationError(
                "metadata must be a mapping."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the alert as a serializable dictionary.
        """

        return {
            "alert_id": self.alert_id,
            "component": self.component,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "created_at_utc": self.created_at_utc.isoformat(),
            "metric_name": self.metric_name,
            "observed_value": (
                float(self.observed_value)
                if self.observed_value is not None
                else None
            ),
            "threshold_value": (
                float(self.threshold_value)
                if self.threshold_value is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Platform Health Report
# ============================================================

@dataclass(frozen=True, slots=True)
class PlatformHealthReport:
    """
    Aggregated platform health report.

    Parameters
    ----------
    status:
        Overall platform health status.

    components:
        Ordered component health results.

    generated_at_utc:
        UTC report-generation timestamp.

    monitoring_version:
        Monitoring contract version.
    """

    status: HealthStatus

    components: tuple[ComponentHealth, ...]

    generated_at_utc: datetime

    monitoring_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the platform health report.
        """

        if not isinstance(self.status, HealthStatus):
            raise MonitoringValidationError(
                "status must be a HealthStatus."
            )

        if not isinstance(self.components, tuple):
            raise MonitoringValidationError(
                "components must be a tuple."
            )

        if not self.components:
            raise MonitoringValidationError(
                "Platform health report must include at least one "
                "component."
            )

        for component in self.components:
            if not isinstance(component, ComponentHealth):
                raise MonitoringValidationError(
                    "Every component must be a ComponentHealth."
                )

        component_names = tuple(
            component.component
            for component in self.components
        )

        if len(component_names) != len(set(component_names)):
            raise MonitoringValidationError(
                "Platform health components must be unique."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise MonitoringValidationError(
                "generated_at_utc must be a datetime."
            )

        if (
            not isinstance(self.monitoring_version, str)
            or not self.monitoring_version.strip()
        ):
            raise MonitoringValidationError(
                "monitoring_version must not be empty."
            )

        expected_status = self.resolve_status(
            components=self.components,
        )

        if self.status is not expected_status:
            raise MonitoringValidationError(
                "Platform status is inconsistent with component "
                "health results."
            )

    @staticmethod
    def resolve_status(
        *,
        components: tuple[ComponentHealth, ...],
    ) -> HealthStatus:
        """
        Resolve overall platform health from component statuses.
        """

        statuses = {
            component.status
            for component in components
        }

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        if HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN

        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def as_dict(self) -> dict[str, Any]:
        """
        Return the platform health report as a dictionary.
        """

        return {
            "status": self.status.value,
            "components": [
                component.as_dict()
                for component in self.components
            ],
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "monitoring_version": self.monitoring_version,
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "ComponentHealth",
    "ExecutionRecord",
    "ExecutionStatus",
    "HealthStatus",
    "MetricRecord",
    "MetricType",
    "MonitoringAlert",
    "PlatformHealthReport",
    "SeverityLevel",
]