"""
Implementation 25.3 — Enterprise Application Models

Typed contracts for application identity, lifecycle state, service
registration, bootstrap events, and final application context.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from .constants import (
    BOOTSTRAP_SEQUENCE,
    SUPPORTED_ENVIRONMENTS,
    SUPPORTED_SERVICES,
)
from .exceptions import ApplicationValidationError


# ============================================================
# Enumerations
# ============================================================

class ApplicationEnvironment(str, Enum):
    """
    Supported application runtime environments.
    """

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class BootstrapStage(str, Enum):
    """
    Supported application bootstrap stages.
    """

    CONFIGURATION = "configuration"
    DEPENDENCIES = "dependencies"
    SERVICES = "services"
    API = "api"
    COMPLETE = "complete"


class ApplicationStatus(str, Enum):
    """
    Application lifecycle status.
    """

    CREATED = "CREATED"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    READY = "READY"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


# ============================================================
# Service Registration
# ============================================================

@dataclass(frozen=True, slots=True)
class ServiceRegistration:
    """
    Immutable dependency-container service registration.

    Parameters
    ----------
    name:
        Stable service registration name.

    instance:
        Constructed service instance.

    registered_at_utc:
        UTC registration timestamp.

    metadata:
        Optional registration metadata.
    """

    name: str

    instance: Any

    registered_at_utc: datetime

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the service registration.
        """

        if (
            not isinstance(self.name, str)
            or self.name not in SUPPORTED_SERVICES
        ):
            raise ApplicationValidationError(
                "Service name is not supported."
            )

        if self.instance is None:
            raise ApplicationValidationError(
                "Service instance must not be None."
            )

        if not isinstance(self.registered_at_utc, datetime):
            raise ApplicationValidationError(
                "registered_at_utc must be a datetime."
            )

        if not isinstance(self.metadata, Mapping):
            raise ApplicationValidationError(
                "metadata must be a mapping."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return serializable registration metadata.

        The service instance itself is represented by its class name
        rather than serialized.
        """

        return {
            "name": self.name,
            "instance_type": type(self.instance).__name__,
            "registered_at_utc": (
                self.registered_at_utc.isoformat()
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Bootstrap Event
# ============================================================

@dataclass(frozen=True, slots=True)
class BootstrapEvent:
    """
    Immutable record for one application bootstrap stage.

    Parameters
    ----------
    stage:
        Bootstrap stage represented by the event.

    started_at_utc:
        UTC stage start time.

    completed_at_utc:
        UTC stage completion time.

    succeeded:
        Whether the stage completed successfully.

    message:
        Human-readable stage result.

    metadata:
        Optional structured stage metadata.
    """

    stage: BootstrapStage

    started_at_utc: datetime

    completed_at_utc: datetime

    succeeded: bool

    message: str

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the bootstrap event.
        """

        if not isinstance(self.stage, BootstrapStage):
            raise ApplicationValidationError(
                "stage must be a BootstrapStage."
            )

        if self.stage.value not in BOOTSTRAP_SEQUENCE:
            raise ApplicationValidationError(
                "Unsupported bootstrap stage."
            )

        if not isinstance(self.started_at_utc, datetime):
            raise ApplicationValidationError(
                "started_at_utc must be a datetime."
            )

        if not isinstance(self.completed_at_utc, datetime):
            raise ApplicationValidationError(
                "completed_at_utc must be a datetime."
            )

        if self.completed_at_utc < self.started_at_utc:
            raise ApplicationValidationError(
                "completed_at_utc cannot be earlier than "
                "started_at_utc."
            )

        if not isinstance(self.succeeded, bool):
            raise ApplicationValidationError(
                "succeeded must be a boolean."
            )

        if (
            not isinstance(self.message, str)
            or not self.message.strip()
        ):
            raise ApplicationValidationError(
                "Bootstrap event message must not be empty."
            )

        if not isinstance(self.metadata, Mapping):
            raise ApplicationValidationError(
                "metadata must be a mapping."
            )

    @property
    def duration_ms(self) -> float:
        """
        Return stage duration in milliseconds.
        """

        return (
            self.completed_at_utc
            - self.started_at_utc
        ).total_seconds() * 1_000.0

    def as_dict(self) -> dict[str, Any]:
        """
        Return the event as a serializable dictionary.
        """

        return {
            "stage": self.stage.value,
            "started_at_utc": self.started_at_utc.isoformat(),
            "completed_at_utc": (
                self.completed_at_utc.isoformat()
            ),
            "duration_ms": self.duration_ms,
            "succeeded": self.succeeded,
            "message": self.message,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Application Descriptor
# ============================================================

@dataclass(frozen=True, slots=True)
class ApplicationDescriptor:
    """
    Enterprise application identity and lifecycle descriptor.

    Parameters
    ----------
    application_name:
        Stable application name.

    application_version:
        Application semantic version.

    environment:
        Active runtime environment.

    status:
        Current application lifecycle status.

    created_at_utc:
        UTC descriptor creation timestamp.
    """

    application_name: str

    application_version: str

    environment: ApplicationEnvironment

    status: ApplicationStatus

    created_at_utc: datetime

    def __post_init__(self) -> None:
        """
        Validate the application descriptor.
        """

        if (
            not isinstance(self.application_name, str)
            or not self.application_name.strip()
        ):
            raise ApplicationValidationError(
                "application_name must not be empty."
            )

        if (
            not isinstance(self.application_version, str)
            or not self.application_version.strip()
        ):
            raise ApplicationValidationError(
                "application_version must not be empty."
            )

        if not isinstance(
            self.environment,
            ApplicationEnvironment,
        ):
            raise ApplicationValidationError(
                "environment must be an ApplicationEnvironment."
            )

        if self.environment.value not in SUPPORTED_ENVIRONMENTS:
            raise ApplicationValidationError(
                "Unsupported application environment."
            )

        if not isinstance(self.status, ApplicationStatus):
            raise ApplicationValidationError(
                "status must be an ApplicationStatus."
            )

        if not isinstance(self.created_at_utc, datetime):
            raise ApplicationValidationError(
                "created_at_utc must be a datetime."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the descriptor as a serializable dictionary.
        """

        return {
            "application_name": self.application_name,
            "application_version": self.application_version,
            "environment": self.environment.value,
            "status": self.status.value,
            "created_at_utc": self.created_at_utc.isoformat(),
        }


# ============================================================
# Bootstrap Result
# ============================================================

@dataclass(frozen=True, slots=True)
class ApplicationBootstrapResult:
    """
    Final application bootstrap result.

    Parameters
    ----------
    descriptor:
        Final application descriptor.

    completed_stage:
        Last successfully completed bootstrap stage.

    events:
        Ordered bootstrap-stage events.

    started_at_utc:
        UTC bootstrap start time.

    completed_at_utc:
        UTC bootstrap completion time.

    error_message:
        Failure explanation when bootstrap did not succeed.
    """

    descriptor: ApplicationDescriptor

    completed_stage: BootstrapStage

    events: tuple[BootstrapEvent, ...]

    started_at_utc: datetime

    completed_at_utc: datetime

    error_message: str = ""

    def __post_init__(self) -> None:
        """
        Validate the bootstrap result.
        """

        if not isinstance(
            self.descriptor,
            ApplicationDescriptor,
        ):
            raise ApplicationValidationError(
                "descriptor must be an ApplicationDescriptor."
            )

        if not isinstance(
            self.completed_stage,
            BootstrapStage,
        ):
            raise ApplicationValidationError(
                "completed_stage must be a BootstrapStage."
            )

        if not isinstance(self.events, tuple):
            raise ApplicationValidationError(
                "events must be a tuple."
            )

        if not self.events:
            raise ApplicationValidationError(
                "Bootstrap result must contain at least one event."
            )

        for event in self.events:
            if not isinstance(event, BootstrapEvent):
                raise ApplicationValidationError(
                    "Every event must be a BootstrapEvent."
                )

        stage_values = tuple(
            event.stage.value
            for event in self.events
        )

        expected_positions = tuple(
            BOOTSTRAP_SEQUENCE.index(stage)
            for stage in stage_values
        )

        if expected_positions != tuple(
            sorted(expected_positions)
        ):
            raise ApplicationValidationError(
                "Bootstrap events must follow bootstrap sequence."
            )

        if len(stage_values) != len(set(stage_values)):
            raise ApplicationValidationError(
                "Bootstrap event stages must be unique."
            )

        if (
            self.events[-1].stage
            is not self.completed_stage
        ):
            raise ApplicationValidationError(
                "completed_stage must match the final event stage."
            )

        if not isinstance(self.started_at_utc, datetime):
            raise ApplicationValidationError(
                "started_at_utc must be a datetime."
            )

        if not isinstance(self.completed_at_utc, datetime):
            raise ApplicationValidationError(
                "completed_at_utc must be a datetime."
            )

        if self.completed_at_utc < self.started_at_utc:
            raise ApplicationValidationError(
                "completed_at_utc cannot be earlier than "
                "started_at_utc."
            )

        if not isinstance(self.error_message, str):
            raise ApplicationValidationError(
                "error_message must be a string."
            )

        if self.descriptor.status is ApplicationStatus.READY:
            if self.completed_stage is not BootstrapStage.COMPLETE:
                raise ApplicationValidationError(
                    "READY applications must complete the final "
                    "bootstrap stage."
                )

            if self.error_message:
                raise ApplicationValidationError(
                    "READY applications cannot have an error message."
                )

            if not all(event.succeeded for event in self.events):
                raise ApplicationValidationError(
                    "READY applications require successful events."
                )

        if self.descriptor.status is ApplicationStatus.FAILED:
            if not self.error_message.strip():
                raise ApplicationValidationError(
                    "FAILED applications require an error message."
                )

            if all(event.succeeded for event in self.events):
                raise ApplicationValidationError(
                    "FAILED applications require a failed event."
                )

    @property
    def succeeded(self) -> bool:
        """
        Return whether application bootstrap completed successfully.
        """

        return (
            self.descriptor.status
            is ApplicationStatus.READY
        )

    @property
    def duration_ms(self) -> float:
        """
        Return total bootstrap duration in milliseconds.
        """

        return (
            self.completed_at_utc
            - self.started_at_utc
        ).total_seconds() * 1_000.0

    def as_dict(self) -> dict[str, Any]:
        """
        Return the bootstrap result as a serializable dictionary.
        """

        return {
            "descriptor": self.descriptor.as_dict(),
            "completed_stage": self.completed_stage.value,
            "events": [
                event.as_dict()
                for event in self.events
            ],
            "started_at_utc": self.started_at_utc.isoformat(),
            "completed_at_utc": (
                self.completed_at_utc.isoformat()
            ),
            "duration_ms": self.duration_ms,
            "succeeded": self.succeeded,
            "error_message": self.error_message,
        }


# ============================================================
# Application Context
# ============================================================

@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """
    Fully constructed enterprise application context.

    Parameters
    ----------
    descriptor:
        Application identity and lifecycle descriptor.

    services:
        Immutable service registrations.

    bootstrap_result:
        Completed application bootstrap result.

    metadata:
        Optional application metadata.
    """

    descriptor: ApplicationDescriptor

    services: tuple[ServiceRegistration, ...]

    bootstrap_result: ApplicationBootstrapResult

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the application context.
        """

        if not isinstance(
            self.descriptor,
            ApplicationDescriptor,
        ):
            raise ApplicationValidationError(
                "descriptor must be an ApplicationDescriptor."
            )

        if self.descriptor.status is not ApplicationStatus.READY:
            raise ApplicationValidationError(
                "Application context requires READY status."
            )

        if not isinstance(self.services, tuple):
            raise ApplicationValidationError(
                "services must be a tuple."
            )

        if not self.services:
            raise ApplicationValidationError(
                "Application context must contain services."
            )

        for registration in self.services:
            if not isinstance(
                registration,
                ServiceRegistration,
            ):
                raise ApplicationValidationError(
                    "Every service must be a ServiceRegistration."
                )

        service_names = tuple(
            registration.name
            for registration in self.services
        )

        if len(service_names) != len(set(service_names)):
            raise ApplicationValidationError(
                "Application service names must be unique."
            )

        if not isinstance(
            self.bootstrap_result,
            ApplicationBootstrapResult,
        ):
            raise ApplicationValidationError(
                "bootstrap_result must be an "
                "ApplicationBootstrapResult."
            )

        if not self.bootstrap_result.succeeded:
            raise ApplicationValidationError(
                "Application context requires successful bootstrap."
            )

        if (
            self.bootstrap_result.descriptor
            != self.descriptor
        ):
            raise ApplicationValidationError(
                "Context and bootstrap descriptors must match."
            )

        if not isinstance(self.metadata, Mapping):
            raise ApplicationValidationError(
                "metadata must be a mapping."
            )

    def get_service(
        self,
        *,
        name: str,
    ) -> Any:
        """
        Resolve one service instance by registration name.
        """

        for registration in self.services:
            if registration.name == name:
                return registration.instance

        raise ApplicationValidationError(
            f"Service '{name}' is not registered."
        )

    def as_dict(self) -> dict[str, Any]:
        """
        Return serializable application-context metadata.
        """

        return {
            "descriptor": self.descriptor.as_dict(),
            "services": [
                registration.as_dict()
                for registration in self.services
            ],
            "bootstrap_result": (
                self.bootstrap_result.as_dict()
            ),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "ApplicationBootstrapResult",
    "ApplicationContext",
    "ApplicationDescriptor",
    "ApplicationEnvironment",
    "ApplicationStatus",
    "BootstrapEvent",
    "BootstrapStage",
    "ServiceRegistration",
]