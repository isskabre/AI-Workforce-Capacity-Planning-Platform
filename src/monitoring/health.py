"""
Implementation 23.6 — Enterprise Monitoring Health Checks

Component health evaluation, platform health aggregation, timeout
assessment, and health-based alert generation for the Enterprise
Monitoring and Observability Framework.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4

from .configuration import MonitoringConfiguration
from .exceptions import (
    MonitoringHealthCheckError,
    MonitoringValidationError,
)
from .models import (
    ComponentHealth,
    HealthStatus,
    MonitoringAlert,
    PlatformHealthReport,
    SeverityLevel,
)


HealthCheckCallable = Callable[[], bool | Mapping[str, Any]]


class MonitoringHealthService:
    """
    Execute component health checks and build platform health reports.

    Health checks remain dependency-agnostic. Any callable that returns
    either a boolean or a mapping can be registered and evaluated.

    Boolean return values
    ---------------------
    True:
        Component is healthy.

    False:
        Component is unhealthy.

    Mapping return values
    ---------------------
    A mapping may contain:

    - ``healthy``: required boolean health flag
    - ``degraded``: optional boolean degraded-state flag
    - ``message``: optional health explanation
    - ``details``: optional structured diagnostic mapping
    """

    def __init__(
        self,
        *,
        configuration: MonitoringConfiguration | None = None,
    ) -> None:
        """
        Initialize the monitoring health service.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else MonitoringConfiguration()
        )

        if not isinstance(
            self._configuration,
            MonitoringConfiguration,
        ):
            raise MonitoringValidationError(
                "configuration must be a MonitoringConfiguration."
            )

        self._health_checks: dict[str, HealthCheckCallable] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        *,
        component: str,
        health_check: HealthCheckCallable,
    ) -> None:
        """
        Register one component health-check callable.
        """

        self._validate_component(component)

        if not callable(health_check):
            raise MonitoringValidationError(
                "health_check must be callable."
            )

        self._health_checks[component] = health_check

    def unregister(
        self,
        *,
        component: str,
    ) -> None:
        """
        Remove one registered component health check.
        """

        self._validate_component(component)

        self._health_checks.pop(component, None)

    # ---------------------------------------------------------
    # Component health
    # ---------------------------------------------------------

    def check_component(
        self,
        *,
        component: str,
    ) -> ComponentHealth:
        """
        Execute one registered component health check.
        """

        self._validate_component(component)

        if not self._configuration.enable_health_checks:
            raise MonitoringHealthCheckError(
                "Health checks are disabled."
            )

        health_check = self._health_checks.get(component)

        if health_check is None:
            return ComponentHealth(
                component=component,
                status=HealthStatus.UNKNOWN,
                checked_at_utc=datetime.now(timezone.utc),
                response_time_ms=0.0,
                message="No health check is registered.",
                details={
                    "registered": False,
                },
            )

        started_at = perf_counter()

        try:
            raw_result = health_check()

        except Exception as exc:
            response_time_ms = (
                perf_counter() - started_at
            ) * 1_000.0

            return ComponentHealth(
                component=component,
                status=HealthStatus.UNHEALTHY,
                checked_at_utc=datetime.now(timezone.utc),
                response_time_ms=response_time_ms,
                message="Health check execution failed.",
                details={
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                },
            )

        response_time_ms = (
            perf_counter() - started_at
        ) * 1_000.0

        return self._build_component_health(
            component=component,
            raw_result=raw_result,
            response_time_ms=response_time_ms,
        )

    def check_all(self) -> PlatformHealthReport:
        """
        Execute all enabled component health checks.
        """

        if not self._configuration.enable_health_checks:
            raise MonitoringHealthCheckError(
                "Health checks are disabled."
            )

        component_health = tuple(
            self.check_component(component=component)
            for component in self._configuration.enabled_components
        )

        overall_status = PlatformHealthReport.resolve_status(
            components=component_health,
        )

        return PlatformHealthReport(
            status=overall_status,
            components=component_health,
            generated_at_utc=datetime.now(timezone.utc),
            monitoring_version=(
                self._configuration.monitoring_version
            ),
        )

    # ---------------------------------------------------------
    # Alert generation
    # ---------------------------------------------------------

    def alerts_from_health(
        self,
        *,
        report: PlatformHealthReport,
    ) -> tuple[MonitoringAlert, ...]:
        """
        Generate alerts from degraded or unhealthy components.
        """

        if not isinstance(report, PlatformHealthReport):
            raise MonitoringValidationError(
                "report must be a PlatformHealthReport."
            )

        if not self._configuration.enable_alert_generation:
            return ()

        alerts: list[MonitoringAlert] = []

        for component_health in report.components:
            if component_health.status is HealthStatus.HEALTHY:
                continue

            severity = self._severity_for_health_status(
                status=component_health.status,
            )

            alerts.append(
                MonitoringAlert(
                    alert_id=(
                        f"health-alert-{uuid4().hex[:12]}"
                    ),
                    component=component_health.component,
                    severity=severity,
                    title=(
                        f"{component_health.component.title()} "
                        "health status"
                    ),
                    message=component_health.message,
                    created_at_utc=report.generated_at_utc,
                    metric_name="component_availability",
                    observed_value=(
                        1.0
                        if component_health.is_available
                        else 0.0
                    ),
                    threshold_value=1.0,
                    metadata={
                        "health_status": (
                            component_health.status.value
                        ),
                        "response_time_ms": (
                            component_health.response_time_ms
                        ),
                    },
                )
            )

        return tuple(alerts)

    # ---------------------------------------------------------
    # Health result construction
    # ---------------------------------------------------------

    def _build_component_health(
        self,
        *,
        component: str,
        raw_result: bool | Mapping[str, Any],
        response_time_ms: float,
    ) -> ComponentHealth:
        """
        Convert one raw health-check result into ComponentHealth.
        """

        timed_out = (
            response_time_ms
            > self._configuration.health_check_timeout_seconds
            * 1_000.0
        )

        if timed_out:
            return ComponentHealth(
                component=component,
                status=HealthStatus.UNHEALTHY,
                checked_at_utc=datetime.now(timezone.utc),
                response_time_ms=response_time_ms,
                message="Health check exceeded the configured timeout.",
                details={
                    "timeout_seconds": (
                        self._configuration
                        .health_check_timeout_seconds
                    ),
                },
            )

        if isinstance(raw_result, bool):
            return ComponentHealth(
                component=component,
                status=(
                    HealthStatus.HEALTHY
                    if raw_result
                    else HealthStatus.UNHEALTHY
                ),
                checked_at_utc=datetime.now(timezone.utc),
                response_time_ms=response_time_ms,
                message=(
                    "Component health check passed."
                    if raw_result
                    else "Component health check failed."
                ),
                details={},
            )

        if not isinstance(raw_result, Mapping):
            raise MonitoringHealthCheckError(
                "Health check must return a boolean or mapping."
            )

        healthy = raw_result.get("healthy")

        if not isinstance(healthy, bool):
            raise MonitoringHealthCheckError(
                "Health-check mapping must include boolean 'healthy'."
            )

        degraded = raw_result.get("degraded", False)

        if not isinstance(degraded, bool):
            raise MonitoringHealthCheckError(
                "'degraded' must be a boolean."
            )

        message = raw_result.get(
            "message",
            (
                "Component health check passed."
                if healthy
                else "Component health check failed."
            ),
        )

        if not isinstance(message, str) or not message.strip():
            raise MonitoringHealthCheckError(
                "Health-check message must be a non-empty string."
            )

        details = raw_result.get("details", {})

        if not isinstance(details, Mapping):
            raise MonitoringHealthCheckError(
                "Health-check details must be a mapping."
            )

        if healthy and degraded:
            status = HealthStatus.DEGRADED
        elif healthy:
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.UNHEALTHY

        return ComponentHealth(
            component=component,
            status=status,
            checked_at_utc=datetime.now(timezone.utc),
            response_time_ms=response_time_ms,
            message=message,
            details=dict(details),
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _validate_component(
        self,
        component: str,
    ) -> None:
        """
        Validate an enabled monitoring component.
        """

        if (
            not isinstance(component, str)
            or component
            not in self._configuration.enabled_components
        ):
            raise MonitoringValidationError(
                "component is not enabled for monitoring."
            )

    @staticmethod
    def _severity_for_health_status(
        *,
        status: HealthStatus,
    ) -> SeverityLevel:
        """
        Map health status to alert severity.
        """

        if status is HealthStatus.UNHEALTHY:
            return SeverityLevel.CRITICAL

        if status is HealthStatus.DEGRADED:
            return SeverityLevel.WARNING

        if status is HealthStatus.UNKNOWN:
            return SeverityLevel.ERROR

        return SeverityLevel.INFO

    # ---------------------------------------------------------
    # State and dependencies
    # ---------------------------------------------------------

    @property
    def configuration(self) -> MonitoringConfiguration:
        """
        Return the active monitoring configuration.
        """

        return self._configuration

    @property
    def registered_components(self) -> tuple[str, ...]:
        """
        Return registered component names.
        """

        return tuple(self._health_checks)


__all__ = [
    "HealthCheckCallable",
    "MonitoringHealthService",
]