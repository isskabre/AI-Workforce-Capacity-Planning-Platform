"""
Implementation 26.4 — Enterprise Platform Runner Configuration

Validated immutable configuration for the enterprise platform runner.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import (
    DEFAULT_CONFIGURATION_VERSION,
    DEFAULT_ENABLE_GRACEFUL_SHUTDOWN,
    DEFAULT_FAIL_ON_UNHEALTHY,
    DEFAULT_HEALTH_CHECK_ON_STARTUP,
    DEFAULT_REGISTER_SIGNAL_HANDLERS,
    DEFAULT_RUNNER_SOURCE,
    DEFAULT_RUNNER_VERSION,
    DEFAULT_RUNTIME_MODE,
    DEFAULT_SHUTDOWN_TIMEOUT_SECONDS,
    DEFAULT_STARTUP_TIMEOUT_SECONDS,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TIMEZONE,
    SUPPORTED_RUNTIME_MODES,
)
from .exceptions import RunnerConfigurationError


@dataclass(frozen=True, slots=True)
class RunnerConfiguration:
    """
    Immutable configuration for the Enterprise Platform Runner.

    Parameters
    ----------
    runner_name:
        Stable runner identity.

    runner_version:
        Semantic version of the runner implementation.

    runtime_mode:
        Active execution mode.

    timezone:
        Runtime time-zone identifier.

    timestamp_format:
        Timestamp formatting contract.

    startup_timeout_seconds:
        Maximum permitted startup duration.

    shutdown_timeout_seconds:
        Maximum permitted shutdown duration.

    health_check_interval_seconds:
        Interval between recurring health checks.

    max_retry_attempts:
        Maximum retry count for recoverable runner operations.

    retry_delay_seconds:
        Delay between retry attempts.

    graceful_shutdown_timeout_seconds:
        Time allowed for graceful resource cleanup.

    health_check_on_startup:
        Whether startup must execute a platform health check.

    fail_on_unhealthy:
        Whether an unhealthy startup result fails the runner.

    enable_graceful_shutdown:
        Whether graceful shutdown behavior is enabled.

    enable_signal_handlers:
        Whether supported operating-system signals are registered.

    enable_logging:
        Whether runner logging is enabled.

    enable_metrics:
        Whether runtime metrics collection is enabled.

    enable_validation:
        Whether runtime input and lifecycle validation is enabled.

    auto_startup:
        Whether the runner automatically executes startup.

    auto_shutdown:
        Whether the runner automatically shuts down after execution.

    configuration_version:
        Semantic version of this configuration contract.
    """

    runner_name: str = DEFAULT_RUNNER_SOURCE

    runner_version: str = DEFAULT_RUNNER_VERSION

    runtime_mode: str = DEFAULT_RUNTIME_MODE

    timezone: str = DEFAULT_TIMEZONE

    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT

    startup_timeout_seconds: int = (
        DEFAULT_STARTUP_TIMEOUT_SECONDS
    )

    shutdown_timeout_seconds: int = (
        DEFAULT_SHUTDOWN_TIMEOUT_SECONDS
    )

    health_check_interval_seconds: int = 30

    max_retry_attempts: int = 3

    retry_delay_seconds: int = 5

    graceful_shutdown_timeout_seconds: int = 30

    health_check_on_startup: bool = (
        DEFAULT_HEALTH_CHECK_ON_STARTUP
    )

    fail_on_unhealthy: bool = DEFAULT_FAIL_ON_UNHEALTHY

    enable_graceful_shutdown: bool = (
        DEFAULT_ENABLE_GRACEFUL_SHUTDOWN
    )

    enable_signal_handlers: bool = (
        DEFAULT_REGISTER_SIGNAL_HANDLERS
    )

    enable_logging: bool = True

    enable_metrics: bool = True

    enable_validation: bool = True

    auto_startup: bool = True

    auto_shutdown: bool = True

    configuration_version: str = (
        DEFAULT_CONFIGURATION_VERSION
    )

    def __post_init__(self) -> None:
        """
        Validate the complete runner configuration.
        """

        self._validate_non_empty_string(
            field_name="runner_name",
            value=self.runner_name,
        )

        self._validate_non_empty_string(
            field_name="runner_version",
            value=self.runner_version,
        )

        self._validate_non_empty_string(
            field_name="runtime_mode",
            value=self.runtime_mode,
        )

        if self.runtime_mode not in SUPPORTED_RUNTIME_MODES:
            raise RunnerConfigurationError(
                f"Unsupported runtime_mode: "
                f"{self.runtime_mode}."
            )

        self._validate_non_empty_string(
            field_name="timezone",
            value=self.timezone,
        )

        self._validate_non_empty_string(
            field_name="timestamp_format",
            value=self.timestamp_format,
        )

        self._validate_positive_integer(
            field_name="startup_timeout_seconds",
            value=self.startup_timeout_seconds,
        )

        self._validate_positive_integer(
            field_name="shutdown_timeout_seconds",
            value=self.shutdown_timeout_seconds,
        )

        self._validate_positive_integer(
            field_name="health_check_interval_seconds",
            value=self.health_check_interval_seconds,
        )

        self._validate_non_negative_integer(
            field_name="max_retry_attempts",
            value=self.max_retry_attempts,
        )

        self._validate_non_negative_integer(
            field_name="retry_delay_seconds",
            value=self.retry_delay_seconds,
        )

        self._validate_positive_integer(
            field_name="graceful_shutdown_timeout_seconds",
            value=self.graceful_shutdown_timeout_seconds,
        )

        boolean_fields = {
            "health_check_on_startup": (
                self.health_check_on_startup
            ),
            "fail_on_unhealthy": self.fail_on_unhealthy,
            "enable_graceful_shutdown": (
                self.enable_graceful_shutdown
            ),
            "enable_signal_handlers": (
                self.enable_signal_handlers
            ),
            "enable_logging": self.enable_logging,
            "enable_metrics": self.enable_metrics,
            "enable_validation": self.enable_validation,
            "auto_startup": self.auto_startup,
            "auto_shutdown": self.auto_shutdown,
        }

        for field_name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise RunnerConfigurationError(
                    f"{field_name} must be a boolean."
                )

        self._validate_non_empty_string(
            field_name="configuration_version",
            value=self.configuration_version,
        )

    @staticmethod
    def _validate_non_empty_string(
        *,
        field_name: str,
        value: Any,
    ) -> None:
        """
        Validate a required non-empty string.
        """

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise RunnerConfigurationError(
                f"{field_name} must be a non-empty string."
            )

    @staticmethod
    def _validate_positive_integer(
        *,
        field_name: str,
        value: Any,
    ) -> None:
        """
        Validate a positive integer field.
        """

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise RunnerConfigurationError(
                f"{field_name} must be a positive integer."
            )

    @staticmethod
    def _validate_non_negative_integer(
        *,
        field_name: str,
        value: Any,
    ) -> None:
        """
        Validate a non-negative integer field.
        """

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise RunnerConfigurationError(
                f"{field_name} must be a non-negative integer."
            )

    @property
    def retries_enabled(self) -> bool:
        """
        Return whether retry behavior is enabled.
        """

        return self.max_retry_attempts > 0

    @property
    def graceful_shutdown_enabled(self) -> bool:
        """
        Return whether graceful shutdown is active.
        """

        return self.enable_graceful_shutdown

    def as_dict(self) -> dict[str, Any]:
        """
        Return a serializable configuration representation.
        """

        return {
            "runner_name": self.runner_name,
            "runner_version": self.runner_version,
            "runtime_mode": self.runtime_mode,
            "timezone": self.timezone,
            "timestamp_format": self.timestamp_format,
            "startup_timeout_seconds": (
                self.startup_timeout_seconds
            ),
            "shutdown_timeout_seconds": (
                self.shutdown_timeout_seconds
            ),
            "health_check_interval_seconds": (
                self.health_check_interval_seconds
            ),
            "max_retry_attempts": self.max_retry_attempts,
            "retry_delay_seconds": self.retry_delay_seconds,
            "graceful_shutdown_timeout_seconds": (
                self.graceful_shutdown_timeout_seconds
            ),
            "health_check_on_startup": (
                self.health_check_on_startup
            ),
            "fail_on_unhealthy": self.fail_on_unhealthy,
            "enable_graceful_shutdown": (
                self.enable_graceful_shutdown
            ),
            "enable_signal_handlers": (
                self.enable_signal_handlers
            ),
            "enable_logging": self.enable_logging,
            "enable_metrics": self.enable_metrics,
            "enable_validation": self.enable_validation,
            "auto_startup": self.auto_startup,
            "auto_shutdown": self.auto_shutdown,
            "configuration_version": (
                self.configuration_version
            ),
        }


__all__ = [
    "RunnerConfiguration",
]