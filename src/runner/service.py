"""
Implementation 26.7 — Enterprise Platform Runner Service

Enterprise application service that coordinates the complete runner
lifecycle through startup, runtime state management, and shutdown.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from .configuration import RunnerConfiguration
from .constants import (
    SHUTDOWN_REASON_COMPLETED,
)
from .exceptions import (
    RunnerConfigurationError,
    RunnerLifecycleError,
    RunnerRuntimeError,
    RunnerValidationError,
)
from .models import (
    RunnerDescriptor,
    RunnerExecutionResult,
    RunnerStatus,
)
from .shutdown import EnterpriseRunnerShutdown
from .startup import EnterpriseRunnerStartup


class EnterprisePlatformRunnerService:
    """
    Coordinate the enterprise platform runner lifecycle.

    Responsibilities
    ----------------
    - Execute runner startup.
    - Preserve the active runner descriptor.
    - Expose current lifecycle state.
    - Execute graceful runner shutdown.
    - Prevent invalid lifecycle transitions.
    """

    def __init__(
        self,
        *,
        configuration: RunnerConfiguration,
        startup: EnterpriseRunnerStartup | None = None,
        shutdown: EnterpriseRunnerShutdown | None = None,
    ) -> None:
        """
        Initialize the enterprise platform runner service.
        """

        if not isinstance(
            configuration,
            RunnerConfiguration,
        ):
            raise RunnerConfigurationError(
                "configuration must be a RunnerConfiguration."
            )

        self._configuration = configuration

        self._startup = (
            startup
            if startup is not None
            else EnterpriseRunnerStartup(
                configuration=configuration,
            )
        )

        if not isinstance(
            self._startup,
            EnterpriseRunnerStartup,
        ):
            raise RunnerValidationError(
                "startup must be an EnterpriseRunnerStartup."
            )

        if self._startup.configuration is not configuration:
            raise RunnerValidationError(
                "configuration and startup must reference the same "
                "RunnerConfiguration instance."
            )

        self._shutdown = (
            shutdown
            if shutdown is not None
            else EnterpriseRunnerShutdown(
                configuration=configuration,
            )
        )

        if not isinstance(
            self._shutdown,
            EnterpriseRunnerShutdown,
        ):
            raise RunnerValidationError(
                "shutdown must be an EnterpriseRunnerShutdown."
            )

        if self._shutdown.configuration is not configuration:
            raise RunnerValidationError(
                "configuration and shutdown must reference the same "
                "RunnerConfiguration instance."
            )

        self._active_descriptor: RunnerDescriptor | None = None
        self._startup_result: RunnerExecutionResult | None = None
        self._shutdown_result: RunnerExecutionResult | None = None

    # ========================================================
    # Public lifecycle
    # ========================================================

    def start(
        self,
    ) -> RunnerExecutionResult:
        """
        Start the enterprise platform runner.

        Returns
        -------
        RunnerExecutionResult
            Successful startup result.

        Raises
        ------
        RunnerLifecycleError
            If the runner is already running or has already stopped.
        """

        if self.is_running:
            raise RunnerLifecycleError(
                "Runner is already running."
            )

        if self.is_stopped:
            raise RunnerLifecycleError(
                "A stopped runner service cannot be restarted."
            )

        try:
            result = self._startup.start()

        except Exception as exc:
            if isinstance(
                exc,
                (
                    RunnerLifecycleError,
                    RunnerRuntimeError,
                ),
            ):
                raise

            raise RunnerRuntimeError(
                f"Runner startup failed: {exc}"
            ) from exc

        if not isinstance(
            result,
            RunnerExecutionResult,
        ):
            raise RunnerRuntimeError(
                "Runner startup must return a "
                "RunnerExecutionResult."
            )

        if not result.succeeded:
            raise RunnerRuntimeError(
                "Runner startup did not succeed."
            )

        if (
            result.descriptor.status
            is not RunnerStatus.RUNNING
        ):
            raise RunnerRuntimeError(
                "Successful runner startup must return "
                "RUNNING status."
            )

        self._startup_result = result
        self._active_descriptor = result.descriptor

        return result

    def stop(
        self,
        *,
        reason: str = SHUTDOWN_REASON_COMPLETED,
    ) -> RunnerExecutionResult:
        """
        Stop the enterprise platform runner.

        Parameters
        ----------
        reason:
            Supported shutdown reason.

        Returns
        -------
        RunnerExecutionResult
            Successful shutdown result.

        Raises
        ------
        RunnerLifecycleError
            If the runner has not started or is already stopped.
        """

        if self._active_descriptor is None:
            raise RunnerLifecycleError(
                "Runner must be started before shutdown."
            )

        if self.is_stopped:
            raise RunnerLifecycleError(
                "Runner has already been stopped."
            )

        if not self.is_running:
            raise RunnerLifecycleError(
                "Runner must be in RUNNING status before shutdown."
            )

        try:
            result = self._shutdown.stop(
                descriptor=self._active_descriptor,
                reason=reason,
            )

        except Exception as exc:
            if isinstance(
                exc,
                (
                    RunnerLifecycleError,
                    RunnerValidationError,
                ),
            ):
                raise

            raise RunnerRuntimeError(
                f"Runner shutdown failed: {exc}"
            ) from exc

        if not isinstance(
            result,
            RunnerExecutionResult,
        ):
            raise RunnerRuntimeError(
                "Runner shutdown must return a "
                "RunnerExecutionResult."
            )

        if not result.succeeded:
            raise RunnerRuntimeError(
                "Runner shutdown did not succeed."
            )

        if (
            result.descriptor.status
            is not RunnerStatus.STOPPED
        ):
            raise RunnerRuntimeError(
                "Successful runner shutdown must return "
                "STOPPED status."
            )

        self._shutdown_result = result
        self._active_descriptor = result.descriptor

        return result

    def run(
        self,
    ) -> RunnerExecutionResult:
        """
        Execute the configured runner lifecycle.

        When ``auto_shutdown`` is enabled, this method starts and then
        immediately performs an orderly shutdown. Otherwise, it returns
        the startup result and leaves the runner active.
        """

        if not self._configuration.auto_startup:
            raise RunnerLifecycleError(
                "Automatic startup is disabled."
            )

        startup_result = self.start()

        if not self._configuration.auto_shutdown:
            return startup_result

        return self.stop(
            reason=SHUTDOWN_REASON_COMPLETED,
        )

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
    def startup(
        self,
    ) -> EnterpriseRunnerStartup:
        """
        Return the startup manager.
        """

        return self._startup

    @property
    def shutdown(
        self,
    ) -> EnterpriseRunnerShutdown:
        """
        Return the shutdown manager.
        """

        return self._shutdown

    @property
    def active_descriptor(
        self,
    ) -> RunnerDescriptor | None:
        """
        Return the current runner descriptor.
        """

        return self._active_descriptor

    @property
    def startup_result(
        self,
    ) -> RunnerExecutionResult | None:
        """
        Return the successful startup result.
        """

        return self._startup_result

    @property
    def shutdown_result(
        self,
    ) -> RunnerExecutionResult | None:
        """
        Return the successful shutdown result.
        """

        return self._shutdown_result

    @property
    def status(
        self,
    ) -> RunnerStatus:
        """
        Return the current runner status.
        """

        if self._active_descriptor is None:
            return RunnerStatus.CREATED

        return self._active_descriptor.status

    @property
    def is_created(
        self,
    ) -> bool:
        """
        Return whether the runner has not started.
        """

        return self.status is RunnerStatus.CREATED

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Return whether the runner is active.
        """

        return self.status is RunnerStatus.RUNNING

    @property
    def is_stopped(
        self,
    ) -> bool:
        """
        Return whether the runner has stopped.
        """

        return self.status is RunnerStatus.STOPPED


__all__ = [
    "EnterprisePlatformRunnerService",
]