"""
Implementation 25.5 — Enterprise Application Container

Thread-safe dependency injection container for registering, resolving,
and managing enterprise application services.

The container supports:

- Existing-instance registrations
- Singleton and transient factories
- Lazy service construction
- Circular dependency detection
- Factory failure isolation
- Registration replacement policies
- Singleton lifecycle reset
- Service removal and container clearing

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable

from .configuration import ApplicationConfiguration
from .exceptions import (
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationValidationError,
)


ServiceFactory = Callable[[], Any]


# ============================================================
# Internal registration contract
# ============================================================

@dataclass(slots=True)
class _ServiceRegistration:
    """
    Internal dependency-container registration.

    Parameters
    ----------
    name:
        Stable service registration name.

    factory:
        Callable used to construct the service.

    singleton:
        Whether the factory result is cached.

    instance:
        Cached singleton or explicitly registered instance.

    instance_registration:
        Whether the service was registered as an existing instance.

    description:
        Optional human-readable service description.
    """

    name: str

    factory: ServiceFactory

    singleton: bool

    instance: Any = None

    instance_registration: bool = False

    description: str = ""

    @property
    def is_resolved(self) -> bool:
        """
        Return whether the registration currently has an instance.
        """

        return self.instance is not None


# ============================================================
# Enterprise container
# ============================================================

class EnterpriseApplicationContainer:
    """
    Thread-safe enterprise dependency injection container.

    The container stores service registrations and resolves services
    lazily. Singleton factories are evaluated once and cached, while
    transient factories are evaluated on every resolution.

    Circular dependencies are detected through a resolution stack.
    """

    def __init__(
        self,
        *,
        configuration: ApplicationConfiguration,
    ) -> None:
        """
        Initialize the enterprise application container.
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

        self._registrations: dict[
            str,
            _ServiceRegistration,
        ] = {}

        self._resolution_stack: list[str] = []

        self._lock = RLock()

    # ========================================================
    # Registration
    # ========================================================

    def register_instance(
        self,
        *,
        name: str,
        instance: Any,
        description: str = "",
        replace: bool = False,
    ) -> None:
        """
        Register an existing singleton service instance.

        Parameters
        ----------
        name:
            Stable service name.

        instance:
            Existing service instance.

        description:
            Optional service description.

        replace:
            Whether an existing registration may be replaced.
        """

        self._validate_name(name)

        if instance is None:
            raise ApplicationValidationError(
                "instance must not be None."
            )

        self._validate_description(description)
        self._validate_replace(replace)

        with self._lock:
            self._ensure_registration_allowed(
                name=name,
                replace=replace,
            )

            self._registrations[name] = (
                _ServiceRegistration(
                    name=name,
                    factory=lambda: instance,
                    singleton=True,
                    instance=instance,
                    instance_registration=True,
                    description=description,
                )
            )

    def register_factory(
        self,
        *,
        name: str,
        factory: ServiceFactory,
        singleton: bool = True,
        description: str = "",
        replace: bool = False,
    ) -> None:
        """
        Register a lazy service factory.

        Parameters
        ----------
        name:
            Stable service name.

        factory:
            Zero-argument callable used to construct the service.

        singleton:
            Whether the constructed service should be cached.

        description:
            Optional service description.

        replace:
            Whether an existing registration may be replaced.
        """

        self._validate_name(name)

        if not callable(factory):
            raise ApplicationValidationError(
                "factory must be callable."
            )

        if not isinstance(singleton, bool):
            raise ApplicationValidationError(
                "singleton must be a boolean."
            )

        self._validate_description(description)
        self._validate_replace(replace)

        with self._lock:
            self._ensure_registration_allowed(
                name=name,
                replace=replace,
            )

            self._registrations[name] = (
                _ServiceRegistration(
                    name=name,
                    factory=factory,
                    singleton=singleton,
                    instance=None,
                    instance_registration=False,
                    description=description,
                )
            )

    # ========================================================
    # Resolution
    # ========================================================

    def resolve(
        self,
        *,
        name: str,
    ) -> Any:
        """
        Resolve one registered service.

        Singleton services are constructed once and cached. Transient
        services are constructed for every call.

        Raises
        ------
        ApplicationDependencyError
            If the service is missing, circular, returns ``None``, or
            its factory raises an exception.
        """

        self._validate_name(name)

        with self._lock:
            registration = self._registrations.get(name)

            if registration is None:
                raise ApplicationDependencyError(
                    f"Service '{name}' is not registered."
                )

            if (
                registration.singleton
                and registration.instance is not None
            ):
                return registration.instance

            if name in self._resolution_stack:
                dependency_chain = (
                    *self._resolution_stack,
                    name,
                )

                raise ApplicationDependencyError(
                    "Circular dependency detected: "
                    f"{' -> '.join(dependency_chain)}."
                )

            self._resolution_stack.append(name)

            try:
                instance = registration.factory()

                if instance is None:
                    raise ApplicationDependencyError(
                        f"Factory for service '{name}' "
                        "returned None."
                    )

                if registration.singleton:
                    registration.instance = instance

                return instance

            except ApplicationDependencyError:
                raise

            except Exception as exc:
                raise ApplicationDependencyError(
                    f"Factory for service '{name}' failed: "
                    f"{exc}"
                ) from exc

            finally:
                if (
                    self._resolution_stack
                    and self._resolution_stack[-1] == name
                ):
                    self._resolution_stack.pop()
                elif name in self._resolution_stack:
                    self._resolution_stack.remove(name)

    def resolve_required_services(
        self,
    ) -> dict[str, Any]:
        """
        Resolve every service required by application configuration.

        Returns
        -------
        dict[str, Any]
            Mapping of required service names to resolved instances.
        """

        resolved: dict[str, Any] = {}

        for service_name in (
            self._configuration.required_services
        ):
            resolved[service_name] = self.resolve(
                name=service_name,
            )

        return resolved

    # ========================================================
    # Registration state
    # ========================================================

    def contains(
        self,
        *,
        name: str,
    ) -> bool:
        """
        Return whether a service registration exists.
        """

        self._validate_name(name)

        with self._lock:
            return name in self._registrations

    def is_resolved(
        self,
        *,
        name: str,
    ) -> bool:
        """
        Return whether a registration currently has an instance.

        Transient registrations always return ``False`` because their
        instances are not cached.
        """

        self._validate_name(name)

        with self._lock:
            registration = self._registrations.get(name)

            if registration is None:
                raise ApplicationDependencyError(
                    f"Service '{name}' is not registered."
                )

            return registration.is_resolved

    # ========================================================
    # Removal and lifecycle
    # ========================================================

    def remove(
        self,
        *,
        name: str,
    ) -> bool:
        """
        Remove one service registration.

        Returns
        -------
        bool
            ``True`` when a registration was removed; otherwise
            ``False``.
        """

        self._validate_name(name)

        with self._lock:
            return (
                self._registrations.pop(name, None)
                is not None
            )

    def reset_singletons(self) -> None:
        """
        Clear factory-created singleton instances.

        Explicitly registered instances remain available because the
        container does not own their construction lifecycle.
        """

        with self._lock:
            for registration in (
                self._registrations.values()
            ):
                if (
                    registration.singleton
                    and not registration.instance_registration
                ):
                    registration.instance = None

            self._resolution_stack.clear()

    def clear(self) -> None:
        """
        Remove every service registration and resolution state.
        """

        with self._lock:
            self._registrations.clear()
            self._resolution_stack.clear()

    # ========================================================
    # Validation helpers
    # ========================================================

    @staticmethod
    def _validate_name(
        name: Any,
    ) -> None:
        """
        Validate a service registration name.
        """

        if (
            not isinstance(name, str)
            or not name.strip()
        ):
            raise ApplicationValidationError(
                "Service name must be a non-empty string."
            )

    @staticmethod
    def _validate_description(
        description: Any,
    ) -> None:
        """
        Validate an optional service description.
        """

        if not isinstance(description, str):
            raise ApplicationValidationError(
                "description must be a string."
            )

    @staticmethod
    def _validate_replace(
        replace: Any,
    ) -> None:
        """
        Validate the explicit replacement flag.
        """

        if not isinstance(replace, bool):
            raise ApplicationValidationError(
                "replace must be a boolean."
            )

    def _ensure_registration_allowed(
        self,
        *,
        name: str,
        replace: bool,
    ) -> None:
        """
        Enforce registration replacement policy.
        """

        if name not in self._registrations:
            return

        replacement_allowed = (
            replace
            or self._configuration
            .allow_service_replacement
        )

        if not replacement_allowed:
            raise ApplicationContainerError(
                f"Service '{name}' is already registered."
            )

    # ========================================================
    # Public state
    # ========================================================

    @property
    def configuration(
        self,
    ) -> ApplicationConfiguration:
        """
        Return the application configuration.
        """

        return self._configuration

    @property
    def registered_services(
        self,
    ) -> tuple[str, ...]:
        """
        Return registered service names in sorted order.
        """

        with self._lock:
            return tuple(
                sorted(self._registrations)
            )

    @property
    def resolved_services(
        self,
    ) -> tuple[str, ...]:
        """
        Return names of registrations with cached instances.
        """

        with self._lock:
            return tuple(
                sorted(
                    name
                    for name, registration
                    in self._registrations.items()
                    if registration.is_resolved
                )
            )

    @property
    def service_count(
        self,
    ) -> int:
        """
        Return the number of registered services.
        """

        with self._lock:
            return len(self._registrations)


__all__ = [
    "EnterpriseApplicationContainer",
    "ServiceFactory",
]