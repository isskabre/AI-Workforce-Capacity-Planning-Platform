"""
Implementation 26.6 — Enterprise Platform Runner Shutdown

Enterprise shutdown manager responsible for transitioning the platform
runner to a stopped state and returning an immutable execution result.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from datetime import datetime, timezone

from .configuration import RunnerConfiguration
from .constants import (
    EXIT_CODE_SUCCESS,
    SHUTDOWN_REASON_COMPLETED,
    SUPPORTED_SHUTDOWN_REASONS,
)
from .exceptions import (
    RunnerConfigurationError,
    RunnerShutdownError,
    RunnerValidationError,
)
from .models import (
    RunnerDescriptor,
    RunnerExecutionResult,
    RunnerStatus,
)


class EnterpriseRunnerShutdown:
    """
    Enterprise shutdown manager for the platform runner.

    The shutdown manager is single-use. A second shutdown attempt raises
    ``RunnerShutdownError``.
    """

    def __init__(
        self,
        *,
        configuration: RunnerConfiguration,
    ) -> None:
        """
        Initialize the enterprise runner shutdown manager.
        """

        if not isinstance(
            configuration,
            RunnerConfiguration,
        ):
            raise RunnerConfigurationError(
                "configuration must be a RunnerConfiguration."
            )

        self._configuration = configuration
        self._stopped = False
        self._last_result: RunnerExecutionResult | None = None
        self._shutdown_reason: str | None = None

    # ========================================================
    # Public lifecycle
    # ========================================================

    def stop(
        self,
        *,
        descriptor: RunnerDescriptor,
        reason: str = SHUTDOWN_REASON_COMPLETED,
    ) -> RunnerExecutionResult:
        """
        Execute enterprise runner shutdown.

        Parameters
        ----------
        descriptor:
            Descriptor representing the currently running platform
            runner.

        reason:
            Supported shutdown reason.

        Returns
        -------
        RunnerExecutionResult
            Immutable successful shutdown result.
        """

        if self._stopped:
            raise RunnerShutdownError(
                "Runner shutdown has already been executed."
            )

        if not isinstance(
            descriptor,
            RunnerDescriptor,
        ):
            raise RunnerValidationError(
                "descriptor must be a RunnerDescriptor."
            )

        if descriptor.status is not RunnerStatus.RUNNING:
            raise RunnerShutdownError(
                "Runner must be in RUNNING status before shutdown."
            )

        if (
            not isinstance(reason, str)
            or reason not in SUPPORTED_SHUTDOWN_REASONS
        ):
            raise RunnerValidationError(
                "reason must be a supported shutdown reason."
            )

        stopped_descriptor = RunnerDescriptor(
            name=descriptor.name,
            version=descriptor.version,
            runtime_mode=descriptor.runtime_mode,
            status=RunnerStatus.STOPPED,
            started_at_utc=descriptor.started_at_utc,
        )

        result = RunnerExecutionResult(
            succeeded=True,
            descriptor=stopped_descriptor,
            completed_at_utc=datetime.now(timezone.utc),
            exit_code=EXIT_CODE_SUCCESS,
            message=(
                "Runner stopped successfully "
                f"with reason '{reason}'."
            ),
        )

        self._stopped = True
        self._shutdown_reason = reason
        self._last_result = result

        return result

    # ========================================================
    # Public state
    # ========================================================

    @property
    def configuration(
        self,
    ) -> RunnerConfiguration:
        """
        Return the active runner configuration.
        """

        return self._configuration

    @property
    def stopped(
        self,
    ) -> bool:
        """
        Return whether shutdown has completed.
        """

        return self._stopped

    @property
    def shutdown_reason(
        self,
    ) -> str | None:
        """
        Return the recorded shutdown reason.
        """

        return self._shutdown_reason

    @property
    def last_result(
        self,
    ) -> RunnerExecutionResult | None:
        """
        Return the latest shutdown result.
        """

        return self._last_result


__all__ = [
    "EnterpriseRunnerShutdown",
]