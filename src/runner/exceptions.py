"""
Implementation 26.2 — Enterprise Platform Runner Exceptions
"""

from __future__ import annotations


class RunnerError(Exception):
    """Base runner exception."""


class RunnerValidationError(RunnerError):
    """Raised when runner validation fails."""


class RunnerConfigurationError(RunnerError):
    """Raised when runner configuration is invalid."""


class RunnerStartupError(RunnerError):
    """Raised during startup."""


class RunnerShutdownError(RunnerError):
    """Raised during shutdown."""


class RunnerRuntimeError(RunnerError):
    """Raised during runtime."""


class RunnerExecutionError(RunnerError):
    """Raised while executing the runner."""


class RunnerLifecycleError(RunnerError):
    """Raised for lifecycle failures."""


__all__ = [
    "RunnerError",
    "RunnerValidationError",
    "RunnerConfigurationError",
    "RunnerStartupError",
    "RunnerShutdownError",
    "RunnerRuntimeError",
    "RunnerExecutionError",
    "RunnerLifecycleError",
]