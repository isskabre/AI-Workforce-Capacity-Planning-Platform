"""
Implementation 25.7 — Enterprise Application Bootstrap

Enterprise startup coordinator responsible for validating application
configuration, constructing the dependency container, resolving required
services, recording bootstrap lifecycle events, and producing the final
ready-to-use ApplicationContext.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, TypeVar

from .configuration import ApplicationConfiguration
from .constants import (
    SERVICE_API,
)
from .container import EnterpriseApplicationContainer
from .exceptions import (
    ApplicationBootstrapError,
    ApplicationLifecycleError,
    ApplicationValidationError,
)
from .factory import EnterpriseApplicationFactory
from .models import (
    ApplicationBootstrapResult,
    ApplicationContext,
    ApplicationDescriptor,
    ApplicationStatus,
    BootstrapEvent,
    BootstrapStage,
    ServiceRegistration,
)


T = TypeVar("T")


class EnterpriseApplicationBootstrap:
    """
    Coordinate the complete enterprise application startup lifecycle.

    Bootstrap sequence
    ------------------
    1. Validate application configuration.
    2. Build the dependency-injection container.
    3. Resolve non-API enterprise services.
    4. Resolve and initialize the API service.
    5. Produce the final ready ApplicationContext.

    The bootstrap instance is single-use. Calling ``start`` more than
    once raises ``ApplicationLifecycleError``.
    """

    def __init__(
        self,
        *,
        configuration: ApplicationConfiguration,
        factory: EnterpriseApplicationFactory | None = None,
    ) -> None:
        """
        Initialize the enterprise application bootstrap coordinator.
        """

        if not isinstance(
            configuration,
            ApplicationConfiguration,
        ):
            raise ApplicationValidationError(
                "configuration must be an "
                "ApplicationConfiguration."
            )

        self._configuration = configuration

        self._factory = (
            factory
            if factory is not None
            else EnterpriseApplicationFactory(
                configuration=configuration,
            )
        )

        if not isinstance(
            self._factory,
            EnterpriseApplicationFactory,
        ):
            raise ApplicationValidationError(
                "factory must be an "
                "EnterpriseApplicationFactory."
            )

        if self._factory.configuration is not configuration:
            raise ApplicationValidationError(
                "configuration and factory must reference the same "
                "ApplicationConfiguration instance."
            )

        self._started = False

        self._container: (
            EnterpriseApplicationContainer | None
        ) = None

        self._context: ApplicationContext | None = None

        self._last_result: (
            ApplicationBootstrapResult | None
        ) = None

    # ========================================================
    # Public lifecycle
    # ========================================================

    def start(
        self,
    ) -> ApplicationContext:
        """
        Execute the complete application bootstrap lifecycle.

        Returns
        -------
        ApplicationContext
            Fully initialized application context containing the ready
            application descriptor, service registrations, and bootstrap
            result.

        Raises
        ------
        ApplicationLifecycleError
            If bootstrap has already started.

        ApplicationBootstrapError
            If any bootstrap stage fails.
        """

        if self._started:
            raise ApplicationLifecycleError(
                "Application bootstrap has already been executed."
            )

        self._started = True

        bootstrap_started_at = datetime.now(timezone.utc)

        events: list[BootstrapEvent] = []

        active_stage = BootstrapStage.CONFIGURATION

        try:
            # ------------------------------------------------
            # Stage 1 — Configuration
            # ------------------------------------------------

            self._execute_stage(
                stage=BootstrapStage.CONFIGURATION,
                operation=self._validate_configuration,
                success_message=(
                    "Application configuration validated."
                ),
                events=events,
            )

            # ------------------------------------------------
            # Stage 2 — Dependencies
            # ------------------------------------------------

            active_stage = BootstrapStage.DEPENDENCIES

            container = self._execute_stage(
                stage=BootstrapStage.DEPENDENCIES,
                operation=self._factory.build,
                success_message=(
                    "Application dependency container constructed."
                ),
                events=events,
            )

            if not isinstance(
                container,
                EnterpriseApplicationContainer,
            ):
                raise ApplicationBootstrapError(
                    "Application factory must return an "
                    "EnterpriseApplicationContainer."
                )

            self._container = container

            # ------------------------------------------------
            # Stage 3 — Enterprise services
            # ------------------------------------------------

            active_stage = BootstrapStage.SERVICES

            resolved_services = self._execute_stage(
                stage=BootstrapStage.SERVICES,
                operation=lambda: self._resolve_core_services(
                    container=container,
                ),
                success_message=(
                    "Enterprise application services initialized."
                ),
                events=events,
            )

            # ------------------------------------------------
            # Stage 4 — API
            # ------------------------------------------------

            active_stage = BootstrapStage.API

            api_service = self._execute_stage(
                stage=BootstrapStage.API,
                operation=lambda: self._resolve_api_service(
                    container=container,
                ),
                success_message=(
                    "Enterprise API service initialized."
                ),
                events=events,
            )

            if api_service is not None:
                resolved_services[SERVICE_API] = api_service

            # ------------------------------------------------
            # Stage 5 — Complete
            # ------------------------------------------------

            active_stage = BootstrapStage.COMPLETE

            completion_metadata = {
                "registered_service_count": (
                    container.service_count
                ),
                "resolved_service_count": len(
                    resolved_services
                ),
                "environment": (
                    self._configuration.environment_name
                ),
            }

            self._execute_stage(
                stage=BootstrapStage.COMPLETE,
                operation=lambda: completion_metadata,
                success_message=(
                    "Application bootstrap completed."
                ),
                events=events,
            )

            completed_at_utc = datetime.now(timezone.utc)

            descriptor = ApplicationDescriptor(
                application_name=(
                    self._configuration.application_name
                ),
                application_version=(
                    self._configuration.application_version
                ),
                environment=self._configuration.environment,
                status=ApplicationStatus.READY,
                created_at_utc=bootstrap_started_at,
            )

            bootstrap_result = ApplicationBootstrapResult(
                descriptor=descriptor,
                completed_stage=BootstrapStage.COMPLETE,
                events=tuple(events),
                started_at_utc=bootstrap_started_at,
                completed_at_utc=completed_at_utc,
            )

            registrations = self._build_service_registrations(
                container=container,
                resolved_services=resolved_services,
            )

            context = ApplicationContext(
                descriptor=descriptor,
                services=registrations,
                bootstrap_result=bootstrap_result,
                metadata={
                    "configuration_version": (
                        self._configuration
                        .configuration_version
                    ),
                    "application_domain_version": "1.0.0",
                    "environment": (
                        self._configuration.environment_name
                    ),
                    **dict(self._configuration.metadata),
                },
            )

            self._last_result = bootstrap_result
            self._context = context

            return context

        except ApplicationLifecycleError:
            raise

        except Exception as exc:
            completed_at_utc = datetime.now(timezone.utc)

            failed_events = self._ensure_failed_event(
                events=events,
                stage=active_stage,
                error=exc,
            )

            failed_descriptor = ApplicationDescriptor(
                application_name=(
                    self._configuration.application_name
                ),
                application_version=(
                    self._configuration.application_version
                ),
                environment=self._configuration.environment,
                status=ApplicationStatus.FAILED,
                created_at_utc=bootstrap_started_at,
            )

            failed_result = ApplicationBootstrapResult(
                descriptor=failed_descriptor,
                completed_stage=failed_events[-1].stage,
                events=tuple(failed_events),
                started_at_utc=bootstrap_started_at,
                completed_at_utc=completed_at_utc,
                error_message=str(exc),
            )

            self._last_result = failed_result

            if isinstance(exc, ApplicationBootstrapError):
                raise

            raise ApplicationBootstrapError(
                f"Application bootstrap failed during "
                f"'{active_stage.value}': {exc}"
            ) from exc

    # ========================================================
    # Bootstrap stages
    # ========================================================

    def _validate_configuration(
        self,
    ) -> dict[str, Any]:
        """
        Validate root bootstrap configuration.
        """

        if not self._configuration.required_services:
            raise ApplicationBootstrapError(
                "Application configuration has no required services."
            )

        return {
            "application_name": (
                self._configuration.application_name
            ),
            "application_version": (
                self._configuration.application_version
            ),
            "environment": (
                self._configuration.environment_name
            ),
            "required_service_count": len(
                self._configuration.required_services
            ),
        }

    @staticmethod
    def _resolve_core_services(
        *,
        container: EnterpriseApplicationContainer,
    ) -> dict[str, Any]:
        """
        Resolve all required services except the API service.
        """

        resolved: dict[str, Any] = {}

        for service_name in (
            container.configuration.required_services
        ):
            if service_name == SERVICE_API:
                continue

            resolved[service_name] = container.resolve(
                name=service_name,
            )

        return resolved

    @staticmethod
    def _resolve_api_service(
        *,
        container: EnterpriseApplicationContainer,
    ) -> Any | None:
        """
        Resolve the API service when it is required.
        """

        if not container.configuration.requires_service(
            name=SERVICE_API,
        ):
            return None

        return container.resolve(
            name=SERVICE_API,
        )

    def _execute_stage(
        self,
        *,
        stage: BootstrapStage,
        operation: Callable[[], T],
        success_message: str,
        events: list[BootstrapEvent],
    ) -> T:
        """
        Execute one bootstrap stage and record its result.
        """

        if not isinstance(stage, BootstrapStage):
            raise ApplicationValidationError(
                "stage must be a BootstrapStage."
            )

        if not callable(operation):
            raise ApplicationValidationError(
                "operation must be callable."
            )

        if (
            not isinstance(success_message, str)
            or not success_message.strip()
        ):
            raise ApplicationValidationError(
                "success_message must not be empty."
            )

        started_at_utc = datetime.now(timezone.utc)
        started_at_counter = perf_counter()

        try:
            result = operation()

        except Exception as exc:
            completed_at_utc = datetime.now(timezone.utc)

            events.append(
                BootstrapEvent(
                    stage=stage,
                    started_at_utc=started_at_utc,
                    completed_at_utc=completed_at_utc,
                    succeeded=False,
                    message=str(exc),
                    metadata={
                        "exception_type": type(exc).__name__,
                        "duration_ms": max(
                            0.0,
                            (
                                perf_counter()
                                - started_at_counter
                            )
                            * 1_000.0,
                        ),
                    },
                )
            )

            raise

        completed_at_utc = datetime.now(timezone.utc)

        metadata: dict[str, Any] = {
            "duration_ms": max(
                0.0,
                (
                    perf_counter()
                    - started_at_counter
                )
                * 1_000.0,
            ),
        }

        if (
            self._configuration.enable_bootstrap_events
            and isinstance(result, dict)
        ):
            metadata.update(result)

        events.append(
            BootstrapEvent(
                stage=stage,
                started_at_utc=started_at_utc,
                completed_at_utc=completed_at_utc,
                succeeded=True,
                message=success_message,
                metadata=metadata,
            )
        )

        return result

    # ========================================================
    # Result construction
    # ========================================================

    @staticmethod
    def _build_service_registrations(
        *,
        container: EnterpriseApplicationContainer,
        resolved_services: dict[str, Any],
    ) -> tuple[ServiceRegistration, ...]:
        """
        Convert resolved services into public service registrations.
        """

        registered_at_utc = datetime.now(timezone.utc)

        registrations: list[ServiceRegistration] = []

        for service_name in container.registered_services:
            service_instance = resolved_services.get(
                service_name
            )

            if service_instance is None:
                service_instance = container.resolve(
                    name=service_name,
                )

            registrations.append(
                ServiceRegistration(
                    name=service_name,
                    instance=service_instance,
                    registered_at_utc=registered_at_utc,
                    metadata={
                        "singleton": True,
                        "resolved": True,
                    },
                )
            )

        return tuple(registrations)

    @staticmethod
    def _ensure_failed_event(
        *,
        events: list[BootstrapEvent],
        stage: BootstrapStage,
        error: Exception,
    ) -> list[BootstrapEvent]:
        """
        Ensure the failed bootstrap result ends with a failed event.
        """

        if (
            events
            and events[-1].stage is stage
            and not events[-1].succeeded
        ):
            return events

        timestamp = datetime.now(timezone.utc)

        events.append(
            BootstrapEvent(
                stage=stage,
                started_at_utc=timestamp,
                completed_at_utc=timestamp,
                succeeded=False,
                message=str(error),
                metadata={
                    "exception_type": type(error).__name__,
                },
            )
        )

        return events

    # ========================================================
    # Public state
    # ========================================================

    @property
    def configuration(
        self,
    ) -> ApplicationConfiguration:
        """
        Return the active application configuration.
        """

        return self._configuration

    @property
    def factory(
        self,
    ) -> EnterpriseApplicationFactory:
        """
        Return the active application factory.
        """

        return self._factory

    @property
    def container(
        self,
    ) -> EnterpriseApplicationContainer | None:
        """
        Return the constructed dependency container, if available.
        """

        return self._container

    @property
    def context(
        self,
    ) -> ApplicationContext | None:
        """
        Return the completed application context, if available.
        """

        return self._context

    @property
    def last_result(
        self,
    ) -> ApplicationBootstrapResult | None:
        """
        Return the latest successful or failed bootstrap result.
        """

        return self._last_result

    @property
    def has_started(
        self,
    ) -> bool:
        """
        Return whether bootstrap execution has started.
        """

        return self._started

    @property
    def is_ready(
        self,
    ) -> bool:
        """
        Return whether the application context is ready.
        """

        return (
            self._context is not None
            and self._context.descriptor.status
            is ApplicationStatus.READY
        )


__all__ = [
    "EnterpriseApplicationBootstrap",
]