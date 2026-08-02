"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.factory

Description:
    Provides the centralized registry and factory responsible for discovering,
    registering, and creating enterprise forecasting model adapters.

    Training, evaluation, inference, and notebook orchestration must use this
    factory rather than instantiate concrete forecasting algorithms directly.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from forecast.modeling.configuration import (
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION,
    EnterpriseForecastConfiguration,
)
from forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
)
from forecast.modeling.exceptions import (
    ForecastConfigurationError,
    ForecastModelNotFoundError,
    ForecastModelingError,
)


ForecastModelBuilder = Callable[
    [EnterpriseForecastConfiguration],
    BaseForecastModel,
]


def _normalize_model_key(model_key: str) -> str:
    """
    Normalize a model identifier for registry lookup.

    Args:
        model_key:
            User-supplied or configuration-supplied model identifier.

    Returns:
        Lowercase, whitespace-normalized registry key.

    Raises:
        ForecastConfigurationError:
            If the supplied identifier is empty or invalid.
    """
    if not isinstance(model_key, str):
        raise ForecastConfigurationError(
            "Forecast model key must be a string.",
            context={
                "received_type": type(model_key).__name__,
            },
        )

    normalized_key = model_key.strip().lower().replace("-", "_").replace(
        " ",
        "_",
    )

    if not normalized_key:
        raise ForecastConfigurationError(
            "Forecast model key must not be empty."
        )

    return normalized_key


@dataclass(frozen=True, slots=True)
class ForecastModelRegistration:
    """
    Immutable model registration stored by the forecast model factory.

    Attributes:
        model_key:
            Stable normalized algorithm identifier.
        builder:
            Callable that creates a concrete ``BaseForecastModel``.
        display_name:
            Human-readable algorithm name.
        category:
            High-level forecasting model category.
        capabilities:
            Declared model capabilities available before instantiation.
        implementation_version:
            Version of the registered adapter implementation.
        description:
            Optional human-readable algorithm description.
        metadata:
            Additional serializable registration metadata.
    """

    model_key: str
    builder: ForecastModelBuilder
    display_name: str
    category: ForecastModelCategory
    capabilities: frozenset[ForecastModelCapability]
    implementation_version: str = "1.0.0"
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serialization-safe registration representation.

        The builder callable is intentionally excluded because executable
        Python objects are not suitable for metadata persistence.
        """
        return {
            "model_key": self.model_key,
            "display_name": self.display_name,
            "category": self.category.value,
            "capabilities": sorted(
                capability.value for capability in self.capabilities
            ),
            "implementation_version": self.implementation_version,
            "description": self.description,
            "metadata": dict(self.metadata),
        }


class ForecastModelFactory:
    """
    Central enterprise registry and factory for forecasting model adapters.

    The factory maintains a process-local registry of forecasting model
    builders. Concrete algorithms register themselves using stable model keys.

    All downstream services must request models through this factory to avoid
    coupling orchestration code to algorithm-specific implementations.
    """

    _registry: dict[str, ForecastModelRegistration] = {}
    _lock = RLock()

    @classmethod
    def register(
        cls,
        *,
        model_key: str,
        builder: ForecastModelBuilder,
        display_name: str,
        category: ForecastModelCategory,
        capabilities: frozenset[ForecastModelCapability] | None = None,
        implementation_version: str = "1.0.0",
        description: str = "",
        metadata: Mapping[str, Any] | None = None,
        overwrite: bool = False,
    ) -> ForecastModelRegistration:
        """
        Register a forecasting model adapter.

        Args:
            model_key:
                Stable algorithm identifier used by configuration.
            builder:
                Callable accepting ``EnterpriseForecastConfiguration`` and
                returning a concrete ``BaseForecastModel``.
            display_name:
                Human-readable model name.
            category:
                High-level model category.
            capabilities:
                Capabilities available from the adapter.
            implementation_version:
                Registered adapter implementation version.
            description:
                Optional human-readable description.
            metadata:
                Optional serializable registration metadata.
            overwrite:
                Whether an existing registration may be replaced.

        Returns:
            Immutable registration stored by the factory.

        Raises:
            ForecastConfigurationError:
                If registration arguments are invalid or the key already
                exists and overwrite is disabled.
        """
        normalized_key = _normalize_model_key(model_key)

        if not callable(builder):
            raise ForecastConfigurationError(
                "Forecast model builder must be callable.",
                context={
                    "model_key": normalized_key,
                    "builder_type": type(builder).__name__,
                },
            )

        if not isinstance(display_name, str) or not display_name.strip():
            raise ForecastConfigurationError(
                "Forecast model display name must not be empty.",
                context={"model_key": normalized_key},
            )

        if not isinstance(category, ForecastModelCategory):
            raise ForecastConfigurationError(
                "Forecast model category is invalid.",
                context={
                    "model_key": normalized_key,
                    "received_type": type(category).__name__,
                },
            )

        normalized_capabilities = frozenset(capabilities or ())

        invalid_capabilities = [
            capability
            for capability in normalized_capabilities
            if not isinstance(capability, ForecastModelCapability)
        ]

        if invalid_capabilities:
            raise ForecastConfigurationError(
                "Forecast model capabilities contain invalid values.",
                context={
                    "model_key": normalized_key,
                    "invalid_capabilities": [
                        repr(value) for value in invalid_capabilities
                    ],
                },
            )

        registration = ForecastModelRegistration(
            model_key=normalized_key,
            builder=builder,
            display_name=display_name.strip(),
            category=category,
            capabilities=normalized_capabilities,
            implementation_version=implementation_version,
            description=description.strip(),
            metadata=dict(metadata or {}),
        )

        with cls._lock:
            if normalized_key in cls._registry and not overwrite:
                raise ForecastConfigurationError(
                    "Forecast model is already registered.",
                    context={
                        "model_key": normalized_key,
                    },
                )

            cls._registry[normalized_key] = registration

        return registration

    @classmethod
    def create(
        cls,
        model_key: str,
        configuration: EnterpriseForecastConfiguration | None = None,
    ) -> BaseForecastModel:
        """
        Create a forecasting model from its registered builder.

        Args:
            model_key:
                Registered forecasting algorithm identifier.
            configuration:
                Root enterprise forecast configuration. The default enterprise
                configuration is used when no configuration is supplied.

        Returns:
            Concrete forecasting model implementing ``BaseForecastModel``.

        Raises:
            ForecastModelNotFoundError:
                If no model is registered for the supplied identifier.
            ForecastModelingError:
                If the builder fails or returns an incompatible object.
        """
        normalized_key = _normalize_model_key(model_key)
        resolved_configuration = (
            configuration
            or DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION
        )

        registration = cls.get_registration(normalized_key)

        try:
            model = registration.builder(resolved_configuration)
        except ForecastModelingError:
            raise
        except Exception as exc:
            raise ForecastModelingError(
                "Forecast model construction failed.",
                error_code="FORECAST_MODEL_CONSTRUCTION_ERROR",
                context={
                    "model_key": normalized_key,
                    "display_name": registration.display_name,
                    "implementation_version": (
                        registration.implementation_version
                    ),
                },
                cause=exc,
            ) from exc

        if not isinstance(model, BaseForecastModel):
            raise ForecastModelingError(
                "Registered forecast model builder returned an incompatible "
                "object.",
                error_code="INVALID_FORECAST_MODEL_INSTANCE",
                context={
                    "model_key": normalized_key,
                    "returned_type": type(model).__name__,
                    "expected_type": BaseForecastModel.__name__,
                },
            )

        return model

    @classmethod
    def get_registration(
        cls,
        model_key: str,
    ) -> ForecastModelRegistration:
        """
        Return registration metadata for a model.

        Args:
            model_key:
                Registered algorithm identifier.

        Returns:
            Corresponding immutable model registration.

        Raises:
            ForecastModelNotFoundError:
                If the model key is not registered.
        """
        normalized_key = _normalize_model_key(model_key)

        with cls._lock:
            registration = cls._registry.get(normalized_key)

        if registration is None:
            raise ForecastModelNotFoundError(
                "Requested forecast model is not registered.",
                context={
                    "model_key": normalized_key,
                    "supported_models": cls.supported_models(),
                },
            )

        return registration

    @classmethod
    def is_supported(cls, model_key: str) -> bool:
        """
        Return whether a forecasting model is registered.

        Args:
            model_key:
                Forecasting algorithm identifier.

        Returns:
            ``True`` when the normalized model key exists in the registry.
        """
        normalized_key = _normalize_model_key(model_key)

        with cls._lock:
            return normalized_key in cls._registry

    @classmethod
    def supported_models(cls) -> tuple[str, ...]:
        """
        Return all registered model keys in deterministic order.

        Returns:
            Sorted tuple of registered forecasting model identifiers.
        """
        with cls._lock:
            return tuple(sorted(cls._registry))

    @classmethod
    def registrations(
        cls,
    ) -> tuple[ForecastModelRegistration, ...]:
        """
        Return all registered model descriptors.

        Returns:
            Registrations ordered by normalized model key.
        """
        with cls._lock:
            return tuple(
                cls._registry[key]
                for key in sorted(cls._registry)
            )

    @classmethod
    def catalog(cls) -> tuple[dict[str, Any], ...]:
        """
        Return serialization-safe model catalog entries.

        Returns:
            Tuple containing metadata for every registered model.
        """
        return tuple(
            registration.to_dict()
            for registration in cls.registrations()
        )

    @classmethod
    def unregister(cls, model_key: str) -> ForecastModelRegistration:
        """
        Remove and return an existing model registration.

        This method is primarily intended for tests, controlled plugin
        lifecycle management, and optional dependency handling.

        Args:
            model_key:
                Forecasting algorithm identifier.

        Returns:
            Removed model registration.

        Raises:
            ForecastModelNotFoundError:
                If the supplied model is not registered.
        """
        normalized_key = _normalize_model_key(model_key)

        with cls._lock:
            registration = cls._registry.pop(normalized_key, None)

        if registration is None:
            raise ForecastModelNotFoundError(
                "Cannot unregister an unknown forecast model.",
                context={
                    "model_key": normalized_key,
                },
            )

        return registration

    @classmethod
    def clear(cls) -> None:
        """
        Remove all model registrations.

        This operation should be used only by isolated validation or unit-test
        environments. Production orchestration should not clear the registry.
        """
        with cls._lock:
            cls._registry.clear()


def register_forecast_model(
    *,
    model_key: str,
    display_name: str,
    category: ForecastModelCategory,
    capabilities: frozenset[ForecastModelCapability] | None = None,
    implementation_version: str = "1.0.0",
    description: str = "",
    metadata: Mapping[str, Any] | None = None,
    overwrite: bool = False,
) -> Callable[[ForecastModelBuilder], ForecastModelBuilder]:
    """
    Decorator that registers a forecasting model builder.

    Example:
        ```python
        @register_forecast_model(
            model_key="random_forest",
            display_name="Random Forest",
            category=ForecastModelCategory.MACHINE_LEARNING,
            capabilities=frozenset({
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.FEATURE_IMPORTANCE,
            }),
        )
        def build_random_forest(
            configuration: EnterpriseForecastConfiguration,
        ) -> BaseForecastModel:
            return RandomForestForecastModel(configuration)
        ```

    Returns:
        Decorator preserving the original builder callable.
    """

    def decorator(
        builder: ForecastModelBuilder,
    ) -> ForecastModelBuilder:
        ForecastModelFactory.register(
            model_key=model_key,
            builder=builder,
            display_name=display_name,
            category=category,
            capabilities=capabilities,
            implementation_version=implementation_version,
            description=description,
            metadata=metadata,
            overwrite=overwrite,
        )
        return builder

    return decorator


__all__ = [
    "ForecastModelBuilder",
    "ForecastModelFactory",
    "ForecastModelRegistration",
    "register_forecast_model",
]