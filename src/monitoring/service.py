"""
Implementation 23.7 — Enterprise Monitoring Service

Application service coordinating execution metrics, health checks,
alerts, and platform observability.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .configuration import MonitoringConfiguration
from .exceptions import (
    MonitoringServiceError,
    MonitoringValidationError,
)
from .health import (
    HealthCheckCallable,
    MonitoringHealthService,
)
from .metrics import MonitoringMetricsService
from .models import (
    ExecutionRecord,
    MetricRecord,
    MonitoringAlert,
    PlatformHealthReport,
)


class EnterpriseMonitoringService:
    """
    Public application service for monitoring and observability.

    Responsibilities
    ----------------
    - Register component health checks.
    - Execute component and platform health checks.
    - Convert execution records into standard metrics.
    - Persist metrics in the active in-memory metrics service.
    - Calculate execution summaries.
    - Generate metric- and health-based alerts.
    - Expose a unified monitoring snapshot.
    """

    def __init__(
        self,
        *,
        configuration: MonitoringConfiguration | None = None,
        metrics_service: MonitoringMetricsService | None = None,
        health_service: MonitoringHealthService | None = None,
    ) -> None:
        """
        Initialize the enterprise monitoring service.
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
            raise MonitoringServiceError(
                "configuration must be a MonitoringConfiguration."
            )

        self._metrics_service = (
            metrics_service
            if metrics_service is not None
            else MonitoringMetricsService(
                configuration=self._configuration,
            )
        )

        if not isinstance(
            self._metrics_service,
            MonitoringMetricsService,
        ):
            raise MonitoringServiceError(
                "metrics_service must be a MonitoringMetricsService."
            )

        self._health_service = (
            health_service
            if health_service is not None
            else MonitoringHealthService(
                configuration=self._configuration,
            )
        )

        if not isinstance(
            self._health_service,
            MonitoringHealthService,
        ):
            raise MonitoringServiceError(
                "health_service must be a MonitoringHealthService."
            )

        if (
            self._metrics_service.configuration
            is not self._configuration
        ):
            raise MonitoringValidationError(
                "configuration and metrics_service must reference "
                "the same MonitoringConfiguration instance."
            )

        if (
            self._health_service.configuration
            is not self._configuration
        ):
            raise MonitoringValidationError(
                "configuration and health_service must reference "
                "the same MonitoringConfiguration instance."
            )

    # ---------------------------------------------------------
    # Health-check registration
    # ---------------------------------------------------------

    def register_health_check(
        self,
        *,
        component: str,
        health_check: HealthCheckCallable,
    ) -> None:
        """
        Register one component health check.
        """

        self._health_service.register(
            component=component,
            health_check=health_check,
        )

    def unregister_health_check(
        self,
        *,
        component: str,
    ) -> None:
        """
        Remove one component health check.
        """

        self._health_service.unregister(
            component=component,
        )

    # ---------------------------------------------------------
    # Execution monitoring
    # ---------------------------------------------------------

    def observe_executions(
        self,
        *,
        component: str,
        executions: Iterable[ExecutionRecord],
    ) -> dict[str, Any]:
        """
        Record and evaluate one collection of execution records.

        Returns a structured payload containing:

        - execution summary;
        - generated metric records;
        - generated monitoring alerts.
        """

        execution_tuple = self._validate_executions(
            executions=executions,
        )

        if component not in self._configuration.enabled_components:
            raise MonitoringValidationError(
                "component is not enabled for monitoring."
            )

        for execution in execution_tuple:
            if execution.component != component:
                raise MonitoringValidationError(
                    "Every execution component must match component."
                )

        try:
            metrics = self._metrics_service.metrics_from_executions(
                executions=execution_tuple,
            )

            if self._configuration.enable_metric_collection:
                self._metrics_service.record_many(
                    metrics=metrics,
                )

            summary = self._metrics_service.summarize_executions(
                executions=execution_tuple,
            )

            alerts = (
                self._metrics_service.evaluate_execution_alerts(
                    component=component,
                    summary=summary,
                )
            )

            return {
                "component": component,
                "summary": summary,
                "metrics": tuple(metrics),
                "alerts": tuple(alerts),
            }

        except MonitoringValidationError:
            raise

        except Exception as exc:
            raise MonitoringServiceError(
                "Execution monitoring failed."
            ) from exc

    def record_metric(
        self,
        *,
        metric: MetricRecord,
    ) -> MetricRecord:
        """
        Record one custom metric.
        """

        return self._metrics_service.record(
            metric=metric,
        )

    def record_metrics(
        self,
        *,
        metrics: Iterable[MetricRecord],
    ) -> tuple[MetricRecord, ...]:
        """
        Record multiple custom metrics.
        """

        return self._metrics_service.record_many(
            metrics=metrics,
        )

    # ---------------------------------------------------------
    # Health monitoring
    # ---------------------------------------------------------

    def check_platform_health(
        self,
    ) -> PlatformHealthReport:
        """
        Execute all enabled component health checks.
        """

        try:
            return self._health_service.check_all()

        except Exception as exc:
            from .exceptions import MonitoringHealthCheckError

            if isinstance(
                exc,
                (
                    MonitoringValidationError,
                    MonitoringHealthCheckError,
                ),
            ):
                raise

            raise MonitoringServiceError(
                "Platform health evaluation failed."
            ) from exc

    def evaluate_health_alerts(
        self,
        *,
        report: PlatformHealthReport,
    ) -> tuple[MonitoringAlert, ...]:
        """
        Generate alerts from one platform health report.
        """

        return self._health_service.alerts_from_health(
            report=report,
        )

    # ---------------------------------------------------------
    # Unified snapshot
    # ---------------------------------------------------------

    def build_snapshot(
        self,
        *,
        execution_observations: dict[
            str,
            Iterable[ExecutionRecord],
        ] | None = None,
        include_health: bool = True,
    ) -> dict[str, Any]:
        """
        Build one unified monitoring snapshot.

        Parameters
        ----------
        execution_observations:
            Optional mapping from component name to execution records.

        include_health:
            Whether platform health should be evaluated.

        Returns
        -------
        dict[str, Any]
            Serializable monitoring snapshot.
        """

        if execution_observations is None:
            execution_observations = {}

        if not isinstance(execution_observations, dict):
            raise MonitoringValidationError(
                "execution_observations must be a dictionary."
            )

        if not isinstance(include_health, bool):
            raise MonitoringValidationError(
                "include_health must be a boolean."
            )

        execution_payload: dict[str, Any] = {}
        all_alerts: list[MonitoringAlert] = []

        for component, executions in execution_observations.items():
            observation = self.observe_executions(
                component=component,
                executions=executions,
            )

            execution_payload[component] = {
                "summary": dict(observation["summary"]),
                "metrics": [
                    metric.as_dict()
                    for metric in observation["metrics"]
                ],
                "alerts": [
                    alert.as_dict()
                    for alert in observation["alerts"]
                ],
            }

            all_alerts.extend(observation["alerts"])

        health_report: PlatformHealthReport | None = None
        health_alerts: tuple[MonitoringAlert, ...] = ()

        if include_health:
            health_report = self.check_platform_health()

            health_alerts = self.evaluate_health_alerts(
                report=health_report,
            )

            all_alerts.extend(health_alerts)

        return {
            "monitoring_version": (
                self._configuration.monitoring_version
            ),
            "executions": execution_payload,
            "health": (
                health_report.as_dict()
                if health_report is not None
                else None
            ),
            "alerts": [
                alert.as_dict()
                for alert in all_alerts
            ],
            "recorded_metric_count": len(
                self._metrics_service.metrics
            ),
        }

    # ---------------------------------------------------------
    # State management
    # ---------------------------------------------------------

    def clear_metrics(self) -> None:
        """
        Clear all recorded in-memory metrics.
        """

        self._metrics_service.clear()

    @staticmethod
    def _validate_executions(
        *,
        executions: Iterable[ExecutionRecord],
    ) -> tuple[ExecutionRecord, ...]:
        """
        Validate and materialize execution records.
        """

        if isinstance(executions, (str, bytes)):
            raise MonitoringValidationError(
                "executions must be an iterable of ExecutionRecord "
                "objects."
            )

        try:
            execution_tuple = tuple(executions)
        except TypeError as exc:
            raise MonitoringValidationError(
                "executions must be iterable."
            ) from exc

        for execution in execution_tuple:
            if not isinstance(execution, ExecutionRecord):
                raise MonitoringValidationError(
                    "Every execution must be an ExecutionRecord."
                )

        return execution_tuple

    # ---------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------

    @property
    def configuration(self) -> MonitoringConfiguration:
        """
        Return the active monitoring configuration.
        """

        return self._configuration

    @property
    def metrics_service(self) -> MonitoringMetricsService:
        """
        Return the active metrics service.
        """

        return self._metrics_service

    @property
    def health_service(self) -> MonitoringHealthService:
        """
        Return the active health service.
        """

        return self._health_service


__all__ = [
    "EnterpriseMonitoringService",
]