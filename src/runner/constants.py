"""
Implementation 26.1 — Enterprise Platform Runner Constants

Centralized constants for the platform execution lifecycle, startup,
shutdown, runtime modes, exit codes, and runner metadata.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


# ============================================================
# Domain
# ============================================================

RUNNER_DOMAIN_NAME = "platform-runner"

RUNNER_DOMAIN_VERSION = "1.0.0"

DEFAULT_RUNNER_VERSION = "1.0.0"


# ============================================================
# Runtime Modes
# ============================================================

RUNTIME_MODE_APPLICATION = "application"

RUNTIME_MODE_API = "api"

RUNTIME_MODE_VALIDATION = "validation"

RUNTIME_MODE_BATCH = "batch"

SUPPORTED_RUNTIME_MODES = (
    RUNTIME_MODE_APPLICATION,
    RUNTIME_MODE_API,
    RUNTIME_MODE_VALIDATION,
    RUNTIME_MODE_BATCH,
)

DEFAULT_RUNTIME_MODE = RUNTIME_MODE_APPLICATION


# ============================================================
# Runner Statuses
# ============================================================

RUNNER_STATUS_CREATED = "CREATED"

RUNNER_STATUS_STARTING = "STARTING"

RUNNER_STATUS_RUNNING = "RUNNING"

RUNNER_STATUS_STOPPING = "STOPPING"

RUNNER_STATUS_STOPPED = "STOPPED"

RUNNER_STATUS_FAILED = "FAILED"

SUPPORTED_RUNNER_STATUSES = (
    RUNNER_STATUS_CREATED,
    RUNNER_STATUS_STARTING,
    RUNNER_STATUS_RUNNING,
    RUNNER_STATUS_STOPPING,
    RUNNER_STATUS_STOPPED,
    RUNNER_STATUS_FAILED,
)


# ============================================================
# Startup Stages
# ============================================================

STARTUP_STAGE_CONFIGURATION = "configuration"

STARTUP_STAGE_APPLICATION = "application"

STARTUP_STAGE_SERVICES = "services"

STARTUP_STAGE_HEALTH = "health"

STARTUP_STAGE_READY = "ready"

STARTUP_SEQUENCE = (
    STARTUP_STAGE_CONFIGURATION,
    STARTUP_STAGE_APPLICATION,
    STARTUP_STAGE_SERVICES,
    STARTUP_STAGE_HEALTH,
    STARTUP_STAGE_READY,
)


# ============================================================
# Shutdown Stages
# ============================================================

SHUTDOWN_STAGE_REQUESTED = "requested"

SHUTDOWN_STAGE_SERVICES = "services"

SHUTDOWN_STAGE_CONTAINER = "container"

SHUTDOWN_STAGE_COMPLETE = "complete"

SHUTDOWN_SEQUENCE = (
    SHUTDOWN_STAGE_REQUESTED,
    SHUTDOWN_STAGE_SERVICES,
    SHUTDOWN_STAGE_CONTAINER,
    SHUTDOWN_STAGE_COMPLETE,
)


# ============================================================
# Shutdown Reasons
# ============================================================

SHUTDOWN_REASON_REQUESTED = "requested"

SHUTDOWN_REASON_COMPLETED = "completed"

SHUTDOWN_REASON_FAILURE = "failure"

SHUTDOWN_REASON_INTERRUPT = "interrupt"

SUPPORTED_SHUTDOWN_REASONS = (
    SHUTDOWN_REASON_REQUESTED,
    SHUTDOWN_REASON_COMPLETED,
    SHUTDOWN_REASON_FAILURE,
    SHUTDOWN_REASON_INTERRUPT,
)


# ============================================================
# Exit Codes
# ============================================================

EXIT_CODE_SUCCESS = 0

EXIT_CODE_CONFIGURATION_ERROR = 10

EXIT_CODE_STARTUP_ERROR = 20

EXIT_CODE_RUNTIME_ERROR = 30

EXIT_CODE_SHUTDOWN_ERROR = 40

EXIT_CODE_INTERRUPTED = 130

SUPPORTED_EXIT_CODES = (
    EXIT_CODE_SUCCESS,
    EXIT_CODE_CONFIGURATION_ERROR,
    EXIT_CODE_STARTUP_ERROR,
    EXIT_CODE_RUNTIME_ERROR,
    EXIT_CODE_SHUTDOWN_ERROR,
    EXIT_CODE_INTERRUPTED,
)


# ============================================================
# Runtime Defaults
# ============================================================

DEFAULT_APPLICATION_NAME = (
    "AI Workforce Capacity Planning Platform"
)

DEFAULT_APPLICATION_VERSION = "3.0.0"

DEFAULT_STARTUP_TIMEOUT_SECONDS = 120

DEFAULT_SHUTDOWN_TIMEOUT_SECONDS = 60

DEFAULT_HEALTH_CHECK_ON_STARTUP = True

DEFAULT_FAIL_ON_UNHEALTHY = True

DEFAULT_ENABLE_GRACEFUL_SHUTDOWN = True

DEFAULT_REGISTER_SIGNAL_HANDLERS = True


# ============================================================
# Signal Names
# ============================================================

SIGNAL_INTERRUPT = "SIGINT"

SIGNAL_TERMINATE = "SIGTERM"

SUPPORTED_SHUTDOWN_SIGNALS = (
    SIGNAL_INTERRUPT,
    SIGNAL_TERMINATE,
)


# ============================================================
# Metadata
# ============================================================

DEFAULT_RUNNER_SOURCE = "enterprise-platform-runner"

DEFAULT_TIMEZONE = "UTC"

DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

DEFAULT_CONFIGURATION_VERSION = "1.0.0"


# ============================================================
# Public API
# ============================================================

__all__ = [
    # Domain
    "RUNNER_DOMAIN_NAME",
    "RUNNER_DOMAIN_VERSION",
    "DEFAULT_RUNNER_VERSION",

    # Runtime modes
    "RUNTIME_MODE_APPLICATION",
    "RUNTIME_MODE_API",
    "RUNTIME_MODE_VALIDATION",
    "RUNTIME_MODE_BATCH",
    "SUPPORTED_RUNTIME_MODES",
    "DEFAULT_RUNTIME_MODE",

    # Runner statuses
    "RUNNER_STATUS_CREATED",
    "RUNNER_STATUS_STARTING",
    "RUNNER_STATUS_RUNNING",
    "RUNNER_STATUS_STOPPING",
    "RUNNER_STATUS_STOPPED",
    "RUNNER_STATUS_FAILED",
    "SUPPORTED_RUNNER_STATUSES",

    # Startup
    "STARTUP_STAGE_CONFIGURATION",
    "STARTUP_STAGE_APPLICATION",
    "STARTUP_STAGE_SERVICES",
    "STARTUP_STAGE_HEALTH",
    "STARTUP_STAGE_READY",
    "STARTUP_SEQUENCE",

    # Shutdown
    "SHUTDOWN_STAGE_REQUESTED",
    "SHUTDOWN_STAGE_SERVICES",
    "SHUTDOWN_STAGE_CONTAINER",
    "SHUTDOWN_STAGE_COMPLETE",
    "SHUTDOWN_SEQUENCE",

    # Shutdown reasons
    "SHUTDOWN_REASON_REQUESTED",
    "SHUTDOWN_REASON_COMPLETED",
    "SHUTDOWN_REASON_FAILURE",
    "SHUTDOWN_REASON_INTERRUPT",
    "SUPPORTED_SHUTDOWN_REASONS",

    # Exit codes
    "EXIT_CODE_SUCCESS",
    "EXIT_CODE_CONFIGURATION_ERROR",
    "EXIT_CODE_STARTUP_ERROR",
    "EXIT_CODE_RUNTIME_ERROR",
    "EXIT_CODE_SHUTDOWN_ERROR",
    "EXIT_CODE_INTERRUPTED",
    "SUPPORTED_EXIT_CODES",

    # Defaults
    "DEFAULT_APPLICATION_NAME",
    "DEFAULT_APPLICATION_VERSION",
    "DEFAULT_STARTUP_TIMEOUT_SECONDS",
    "DEFAULT_SHUTDOWN_TIMEOUT_SECONDS",
    "DEFAULT_HEALTH_CHECK_ON_STARTUP",
    "DEFAULT_FAIL_ON_UNHEALTHY",
    "DEFAULT_ENABLE_GRACEFUL_SHUTDOWN",
    "DEFAULT_REGISTER_SIGNAL_HANDLERS",

    # Signals
    "SIGNAL_INTERRUPT",
    "SIGNAL_TERMINATE",
    "SUPPORTED_SHUTDOWN_SIGNALS",

    # Metadata
    "DEFAULT_RUNNER_SOURCE",
    "DEFAULT_TIMEZONE",
    "DEFAULT_TIMESTAMP_FORMAT",
    "DEFAULT_CONFIGURATION_VERSION",
]