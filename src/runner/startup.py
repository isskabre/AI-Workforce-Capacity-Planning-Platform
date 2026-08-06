"""
Implementation 26.5 — Enterprise Platform Runner Startup

Enterprise startup manager responsible for initializing the platform
runner and returning an immutable runner execution result.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from datetime import datetime, timezone

from .configuration import RunnerConfiguration
from .constants import EXIT_CODE_SUCCESS
from .exceptions import (
    RunnerConfigurationError,
    RunnerStartupError,
)
from .models import (
    RunnerDescriptor,
    RunnerExecutionResult,
    RunnerStatus,
)


class EnterpriseRunnerStartup:
    """
    Enterprise startup manager for the platform runner.
    """

    def __init__(
        self,
        *,
        configuration: RunnerConfiguration,
    ) -> None:
        """
        Initialize the runner startup manager.
        """

        if not isinstance(
            configuration,
            RunnerConfiguration,
        ):
            raise RunnerConfigurationError(
                "configuration must be a RunnerConfiguration."
            )

        self._configuration = configuration
        self._started = False
        self._last_result: RunnerExecutionResult | None = None

    @property
    def configuration(
        self,
    ) -> RunnerConfiguration:
        """
        Return the active runner configuration.
        """

        return self._configuration

    @property
    def started(
        self,
    ) -> bool:
        """
        Return whether startup has completed.
        """

        return self._started

    @property
    def last_result(
        self,
    ) -> RunnerExecutionResult | None:
        """
        Return the latest startup result.
        """

        return self._last_result

    def start(
        self,
    ) -> RunnerExecutionResult:
        """
        Execute enterprise runner startup.
        """

        if self._started:
            raise RunnerStartupError(
                "Runner startup has already been executed."
            )

        started_at_utc = datetime.now(timezone.utc)

        descriptor = RunnerDescriptor(
            name=self._configuration.runner_name,
            version=self._configuration.runner_version,
            runtime_mode=self._configuration.runtime_mode,
            status=RunnerStatus.RUNNING,
            started_at_utc=started_at_utc,
        )

        result = RunnerExecutionResult(
            succeeded=True,
            descriptor=descriptor,
            completed_at_utc=datetime.now(timezone.utc),
            exit_code=EXIT_CODE_SUCCESS,
            message="Runner started successfully.",
        )

        self._started = True
        self._last_result = result

        return result


__all__ = [
    "EnterpriseRunnerStartup",
]