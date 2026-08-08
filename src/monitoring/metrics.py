"""
Implementation 23.5 — Enterprise Monitoring Metrics

Metric recording, aggregation, success-rate calculation, duration
evaluation, and threshold-based alert generation for enterprise
monitoring and observability.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean
from typing import Iterable
from uuid import uuid4

from .configuration import MonitoringConfiguration
from .constants import (
    METRIC_EXECUTION_COUNT,
    METRIC_EXECUTION_DURATION_MS,
    METRIC_FAILURE_COUNT,
    METRIC_FAILURE_RATE,
    METRIC_SUCCESS_COUNT,
    METRIC_SUCCESS_RATE,
)
from .exceptions import (
    MonitoringMetricsError,
    MonitoringValidationError,
)
from .models import (
    ExecutionRecord,
    ExecutionStatus,
    MetricRecord,
    MetricType,
    MonitoringAlert,
    SeverityLevel,
)


class MonitoringMetricsService:
    """
    Record, aggregate, and evaluate monitoring metrics.

    The service is intentionally storage-agnostic. It operates on
    validated in-memory records and can later be integrated with Delta
    tables, MLflow, Prometheus, OpenTelemetry, or external monitoring
    platforms.
    """

    def __init__(
        self,
        *,
        configuration: MonitoringConfiguration | None = None,
    ) -> None:
        """
        Initialize the monitoring metrics service.
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

        self._metrics: list[MetricRecord] = []

    # ---------------------------------------------------------
    # Metric recording
    # ---------------------------------------------------------

    def record(
        self,
        *,
        metric: MetricRecord,
    ) -> MetricRecord:
        """
        Record one validated metric.
        """

        if not isinstance(metric, MetricRecord):
            raise MonitoringValidationError(
                "metric must be a MetricRecord."
            )

        if not self._configuration.enable_metric_collection:
            raise MonitoringMetricsError(
                "Metric collection is disabled."
            )

        self._metrics.append(metric)

        return metric

    def record_many(
        self,
        *,
        metrics: Iterable[MetricRecord],
    ) -> tuple[MetricRecord, ...]:
        """
        Record multiple validated metrics atomically.
        """

        if isinstance(metrics, (str, bytes)):
            raise MonitoringValidationError(
                "metrics must be an iterable of MetricRecord objects."
            )

        try:
            metric_tuple = tuple(metrics)
        except TypeError as exc:
            raise MonitoringValidationError(
                "metrics must be iterable."
            ) from exc

        for metric in metric_tuple:
            if not isinstance(metric, MetricRecord):
                raise MonitoringValidationError(
                    "Every metric must be a MetricRecord."
                )

        if not self._configuration.enable_metric_collection:
            raise MonitoringMetricsError(
                "Metric collection is disabled."
            )

        self._metrics.extend(metric_tuple)

        return metric_tuple

    # ---------------------------------------------------------
    # Execution metrics
    # ---------------------------------------------------------

    def metrics_from_executions(
        self,
        *,
        executions: Iterable[ExecutionRecord],
    ) -> tuple[MetricRecord, ...]:
        """
        Convert execution records into standard monitoring metrics.
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

        generated_metrics: list[MetricRecord] = []

        for execution in execution_tuple:
            timestamp = (
                execution.completed_at_utc
                if execution.completed_at_utc is not None
                else execution.started_at_utc
            )

            common_tags = {
                "execution_id": execution.execution_id,
                "operation": execution.operation,
                "status": execution.status.value,
            }

            generated_metrics.append(
                MetricRecord(
                    name=METRIC_EXECUTION_COUNT,
                    metric_type=MetricType.COUNTER,
                    component=execution.component,
                    value=1.0,
                    recorded_at_utc=timestamp,
                    unit="count",
                    tags=common_tags,
                )
            )

            if execution.status is ExecutionStatus.SUCCEEDED:
                generated_metrics.append(
                    MetricRecord(
                        name=METRIC_SUCCESS_COUNT,
                        metric_type=MetricType.COUNTER,
                        component=execution.component,
                        value=1.0,
                        recorded_at_utc=timestamp,
                        unit="count",
                        tags=common_tags,
                    )
                )

            if execution.status is ExecutionStatus.FAILED:
                generated_metrics.append(
                    MetricRecord(
                        name=METRIC_FAILURE_COUNT,
                        metric_type=MetricType.COUNTER,
                        component=execution.component,
                        value=1.0,
                        recorded_at_utc=timestamp,
                        unit="count",
                        tags=common_tags,
                    )
                )

            if execution.duration_ms is not None:
                generated_metrics.append(
                    MetricRecord(
                        name=METRIC_EXECUTION_DURATION_MS,
                        metric_type=MetricType.TIMER,
                        component=execution.component,
                        value=execution.duration_ms,
                        recorded_at_utc=timestamp,
                        unit="milliseconds",
                        tags=common_tags,
                    )
                )

        return tuple(generated_metrics)

    # ---------------------------------------------------------
    # Aggregation
    # ---------------------------------------------------------

    def summarize_executions(
        self,
        *,
        executions: Iterable[ExecutionRecord],
    ) -> dict[str, float]:
        """
        Calculate standard execution metrics.
        """

        try:
            execution_tuple = tuple(executions)
        except TypeError as exc:
            raise MonitoringValidationError(
                "executions must be iterable."
            ) from exc

        if not execution_tuple:
            return {
                METRIC_EXECUTION_COUNT: 0.0,
                METRIC_SUCCESS_COUNT: 0.0,
                METRIC_FAILURE_COUNT: 0.0,
                METRIC_SUCCESS_RATE: 0.0,
                METRIC_FAILURE_RATE: 0.0,
                METRIC_EXECUTION_DURATION_MS: 0.0,
            }

        for execution in execution_tuple:
            if not isinstance(execution, ExecutionRecord):
                raise MonitoringValidationError(
                    "Every execution must be an ExecutionRecord."
                )

        terminal_executions = tuple(
            execution
            for execution in execution_tuple
            if execution.status
            in {
                ExecutionStatus.SUCCEEDED,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
            }
        )

        success_count = sum(
            execution.status is ExecutionStatus.SUCCEEDED
            for execution in terminal_executions
        )

        failure_count = sum(
            execution.status is ExecutionStatus.FAILED
            for execution in terminal_executions
        )

        completed_count = len(terminal_executions)

        durations = [
            float(execution.duration_ms)
            for execution in terminal_executions
            if execution.duration_ms is not None
        ]

        success_rate = (
            success_count / completed_count
            if completed_count > 0
            else 0.0
        )

        failure_rate = (
            failure_count / completed_count
            if completed_count > 0
            else 0.0
        )

        average_duration_ms = (
            mean(durations)
            if durations
            else 0.0
        )

        return {
            METRIC_EXECUTION_COUNT: float(len(execution_tuple)),
            METRIC_SUCCESS_COUNT: float(success_count),
            METRIC_FAILURE_COUNT: float(failure_count),
            METRIC_SUCCESS_RATE: float(success_rate),
            METRIC_FAILURE_RATE: float(failure_rate),
            METRIC_EXECUTION_DURATION_MS: float(
                average_duration_ms
            ),
        }

    def aggregate_metrics(
        self,
        *,
        metrics: Iterable[MetricRecord] | None = None,
    ) -> dict[str, dict[str, float]]:
        """
        Aggregate metrics by component and metric name.

        Counter metrics are summed. Other metric types are averaged.
        """

        metric_tuple = (
            tuple(self._metrics)
            if metrics is None
            else tuple(metrics)
        )

        grouped_values: dict[
            tuple[str, str, MetricType],
            list[float],
        ] = defaultdict(list)

        for metric in metric_tuple:
            if not isinstance(metric, MetricRecord):
                raise MonitoringValidationError(
                    "Every metric must be a MetricRecord."
                )

            grouped_values[
                (
                    metric.component,
                    metric.name,
                    metric.metric_type,
                )
            ].append(float(metric.value))

        aggregated: dict[str, dict[str, float]] = {}

        for (
            component,
            metric_name,
            metric_type,
        ), values in grouped_values.items():
            component_metrics = aggregated.setdefault(
                component,
                {},
            )

            component_metrics[metric_name] = (
                float(sum(values))
                if metric_type is MetricType.COUNTER
                else float(mean(values))
            )

        return aggregated

    # ---------------------------------------------------------
    # Alert evaluation
    # ---------------------------------------------------------

    def evaluate_execution_alerts(
        self,
        *,
        component: str,
        summary: dict[str, float],
    ) -> tuple[MonitoringAlert, ...]:
        """
        Generate alerts from aggregated execution metrics.
        """

        if component not in self._configuration.enabled_components:
            raise MonitoringValidationError(
                "component is not enabled for monitoring."
            )

        if not isinstance(summary, dict):
            raise MonitoringValidationError(
                "summary must be a dictionary."
            )

        if not self._configuration.enable_alert_generation:
            return ()

        success_rate = float(
            summary.get(METRIC_SUCCESS_RATE, 0.0)
        )

        average_duration_ms = float(
            summary.get(
                METRIC_EXECUTION_DURATION_MS,
                0.0,
            )
        )

        alerts: list[MonitoringAlert] = []
        created_at_utc = datetime.now(timezone.utc)

        if success_rate < self._configuration.critical_success_rate:
            alerts.append(
                self._build_alert(
                    component=component,
                    severity=SeverityLevel.CRITICAL,
                    title="Critical execution success rate",
                    message=(
                        "Execution success rate is below the critical "
                        "monitoring threshold."
                    ),
                    metric_name=METRIC_SUCCESS_RATE,
                    observed_value=success_rate,
                    threshold_value=(
                        self._configuration
                        .critical_success_rate
                    ),
                    created_at_utc=created_at_utc,
                )
            )

        elif success_rate < self._configuration.warning_success_rate:
            alerts.append(
                self._build_alert(
                    component=component,
                    severity=SeverityLevel.WARNING,
                    title="Execution success rate warning",
                    message=(
                        "Execution success rate is below the warning "
                        "monitoring threshold."
                    ),
                    metric_name=METRIC_SUCCESS_RATE,
                    observed_value=success_rate,
                    threshold_value=(
                        self._configuration.warning_success_rate
                    ),
                    created_at_utc=created_at_utc,
                )
            )

        if (
            average_duration_ms
            >= self._configuration.critical_duration_ms
        ):
            alerts.append(
                self._build_alert(
                    component=component,
                    severity=SeverityLevel.CRITICAL,
                    title="Critical execution latency",
                    message=(
                        "Average execution duration exceeded the "
                        "critical latency threshold."
                    ),
                    metric_name=METRIC_EXECUTION_DURATION_MS,
                    observed_value=average_duration_ms,
                    threshold_value=(
                        self._configuration.critical_duration_ms
                    ),
                    created_at_utc=created_at_utc,
                )
            )

        elif (
            average_duration_ms
            >= self._configuration.warning_duration_ms
        ):
            alerts.append(
                self._build_alert(
                    component=component,
                    severity=SeverityLevel.WARNING,
                    title="Execution latency warning",
                    message=(
                        "Average execution duration exceeded the "
                        "warning latency threshold."
                    ),
                    metric_name=METRIC_EXECUTION_DURATION_MS,
                    observed_value=average_duration_ms,
                    threshold_value=(
                        self._configuration.warning_duration_ms
                    ),
                    created_at_utc=created_at_utc,
                )
            )

        return tuple(alerts)

    @staticmethod
    def _build_alert(
        *,
        component: str,
        severity: SeverityLevel,
        title: str,
        message: str,
        metric_name: str,
        observed_value: float,
        threshold_value: float,
        created_at_utc: datetime,
    ) -> MonitoringAlert:
        """
        Build one monitoring alert.
        """

        return MonitoringAlert(
            alert_id=(
                f"monitoring-alert-{uuid4().hex[:12]}"
            ),
            component=component,
            severity=severity,
            title=title,
            message=message,
            created_at_utc=created_at_utc,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold_value=threshold_value,
        )

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
    def metrics(self) -> tuple[MetricRecord, ...]:
        """
        Return recorded metrics as an immutable tuple.
        """

        return tuple(self._metrics)

    def clear(self) -> None:
        """
        Clear all recorded in-memory metrics.
        """

        self._metrics.clear()


__all__ = [
    "MonitoringMetricsService",
]