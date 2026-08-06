"""
Implementation 23.4 — Enterprise Monitoring Configuration

Validated configuration contract for enterprise monitoring,
observability, health checks, metrics, and alert thresholds.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import (
    DEFAULT_CRITICAL_DURATION_MS,
    DEFAULT_CRITICAL_SUCCESS_RATE,
    DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
    DEFAULT_MONITORING_VERSION,
    DEFAULT_WARNING_DURATION_MS,
    DEFAULT_WARNING_SUCCESS_RATE,
    MAXIMUM_SUCCESS_RATE,
    MINIMUM_SUCCESS_RATE,
    SUPPORTED_MONITORING_COMPONENTS,
)
from .exceptions import MonitoringConfigurationError


@dataclass(frozen=True, slots=True)
class MonitoringConfiguration:
    """
    Enterprise monitoring policy configuration.

    Parameters
    ----------
    enabled_components:
        Components included in monitoring and health checks.

    warning_success_rate:
        Success-rate threshold below which warning status is raised.

    critical_success_rate:
        Success-rate threshold below which critical status is raised.

    warning_duration_ms:
        Execution duration threshold for warning alerts.

    critical_duration_ms:
        Execution duration threshold for critical alerts.

    health_check_timeout_seconds:
        Maximum allowed health-check duration.

    enable_metric_collection:
        Whether metric recording is enabled.

    enable_health_checks:
        Whether component health checks are enabled.

    enable_alert_generation:
        Whether monitoring alerts are generated.

    retain_execution_metadata:
        Whether execution metadata is preserved.

    monitoring_version:
        Semantic version of the monitoring configuration.
    """

    enabled_components: tuple[str, ...] = (
        SUPPORTED_MONITORING_COMPONENTS
    )

    warning_success_rate: float = (
        DEFAULT_WARNING_SUCCESS_RATE
    )

    critical_success_rate: float = (
        DEFAULT_CRITICAL_SUCCESS_RATE
    )

    warning_duration_ms: float = (
        DEFAULT_WARNING_DURATION_MS
    )

    critical_duration_ms: float = (
        DEFAULT_CRITICAL_DURATION_MS
    )

    health_check_timeout_seconds: float = (
        DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS
    )

    enable_metric_collection: bool = True

    enable_health_checks: bool = True

    enable_alert_generation: bool = True

    retain_execution_metadata: bool = True

    monitoring_version: str = DEFAULT_MONITORING_VERSION

    def __post_init__(self) -> None:
        """
        Validate the complete monitoring configuration.
        """

        if not isinstance(self.enabled_components, tuple):
            raise MonitoringConfigurationError(
                "enabled_components must be a tuple."
            )

        if not self.enabled_components:
            raise MonitoringConfigurationError(
                "enabled_components must not be empty."
            )

        if len(self.enabled_components) != len(
            set(self.enabled_components)
        ):
            raise MonitoringConfigurationError(
                "enabled_components must not contain duplicates."
            )

        for component in self.enabled_components:
            if component not in SUPPORTED_MONITORING_COMPONENTS:
                raise MonitoringConfigurationError(
                    f"Unsupported monitoring component: {component}."
                )

        self._validate_rate(
            name="warning_success_rate",
            value=self.warning_success_rate,
        )

        self._validate_rate(
            name="critical_success_rate",
            value=self.critical_success_rate,
        )

        if (
            self.critical_success_rate
            >= self.warning_success_rate
        ):
            raise MonitoringConfigurationError(
                "critical_success_rate must be less than "
                "warning_success_rate."
            )

        self._validate_positive_number(
            name="warning_duration_ms",
            value=self.warning_duration_ms,
        )

        self._validate_positive_number(
            name="critical_duration_ms",
            value=self.critical_duration_ms,
        )

        if (
            self.critical_duration_ms
            <= self.warning_duration_ms
        ):
            raise MonitoringConfigurationError(
                "critical_duration_ms must exceed "
                "warning_duration_ms."
            )

        self._validate_positive_number(
            name="health_check_timeout_seconds",
            value=self.health_check_timeout_seconds,
        )

        boolean_fields = {
            "enable_metric_collection": (
                self.enable_metric_collection
            ),
            "enable_health_checks": self.enable_health_checks,
            "enable_alert_generation": (
                self.enable_alert_generation
            ),
            "retain_execution_metadata": (
                self.retain_execution_metadata
            ),
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise MonitoringConfigurationError(
                    f"{field_name} must be a boolean."
                )

        if (
            not isinstance(self.monitoring_version, str)
            or not self.monitoring_version.strip()
        ):
            raise MonitoringConfigurationError(
                "monitoring_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        payload = asdict(self)
        payload["enabled_components"] = list(
            self.enabled_components
        )

        return payload

    @staticmethod
    def _validate_rate(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate a monitoring success-rate threshold.
        """

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not MINIMUM_SUCCESS_RATE
            <= float(value)
            <= MAXIMUM_SUCCESS_RATE
        ):
            raise MonitoringConfigurationError(
                f"{name} must be between "
                f"{MINIMUM_SUCCESS_RATE} and "
                f"{MAXIMUM_SUCCESS_RATE}."
            )

    @staticmethod
    def _validate_positive_number(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate a positive numeric configuration value.
        """

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or value <= 0
        ):
            raise MonitoringConfigurationError(
                f"{name} must be greater than 0."
            )


__all__ = [
    "MonitoringConfiguration",
]