"""
AI Workforce Capacity Planning Platform
Implementation 16 - Enterprise Model Registry Framework

Module:
    forecast.model_registry.registry

Description:
    Defines the core enterprise forecast model registry responsible for
    registering, retrieving, listing, and removing immutable references to
    persisted forecast model artifacts.

    The registry stores governance metadata and artifact references only.
    It never stores active Python model objects, estimators, Spark objects,
    or complete training and evaluation result objects.

Architecture:
    Enterprise Model Registry Framework

Version:
    2.8.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

from forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from forecast.modeling.contracts import (
    ForecastModelCategory,
)
from forecast.modeling.exceptions import (
    ForecastRegistryError,
)


@dataclass(frozen=True, slots=True)
class ForecastModelRegistration:
    """
    Immutable registry record for one persisted forecast model artifact.

    The registration contract deliberately stores only metadata and artifact
    references. Executable forecasting models remain outside the registry and
    are reconstructed later through model-loading infrastructure.

    Attributes:
        model_name:
            Stable enterprise model name.

        model_version:
            Forecast model implementation version.

        model_category:
            High-level forecasting model category.

        algorithm:
            Concrete forecasting algorithm identifier.

        artifact_id:
            Globally unique trained artifact identifier.

        artifact_version:
            Version assigned to the trained artifact.

        storage_uri:
            Platform-independent location of the persisted model artifact.

        artifact_status:
            Artifact lifecycle status at registration time.

        target_column:
            Business target predicted by the registered model.

        feature_columns:
            Ordered feature columns used during training.

        forecast_horizon:
            Number of future periods modeled by the artifact.

        primary_metric:
            Optional canonical metric used to assess or select the model.

        primary_metric_value:
            Optional finite value associated with ``primary_metric``.

        registration_id:
            Globally unique registry-record identifier.

        registered_at:
            UTC timestamp when the registry record was created.

        training_dataset_id:
            Optional source training-dataset identifier.

        training_dataset_version:
            Optional source training-dataset version.

        experiment_id:
            Optional experiment identifier.

        run_id:
            Optional experiment-tracking run identifier.

        checksum:
            Optional integrity checksum for the persisted artifact.

        metadata:
            Additional serializable registry metadata.
    """

    model_name: str
    model_version: str
    model_category: ForecastModelCategory
    algorithm: str
    artifact_id: str
    artifact_version: str
    storage_uri: str
    artifact_status: ForecastArtifactStatus
    target_column: str
    feature_columns: tuple[str, ...]
    forecast_horizon: int
    primary_metric: str | None = None
    primary_metric_value: float | None = None
    registration_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    training_dataset_id: str | None = None
    training_dataset_version: str | None = None
    experiment_id: str | None = None
    run_id: str | None = None
    checksum: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize the immutable registration record."""
        normalized_model_name = self._validate_required_string(
            self.model_name,
            field_name="model_name",
        )
        normalized_model_version = self._validate_required_string(
            self.model_version,
            field_name="model_version",
        )
        normalized_algorithm = self._validate_required_string(
            self.algorithm,
            field_name="algorithm",
        )
        normalized_artifact_id = self._validate_required_string(
            self.artifact_id,
            field_name="artifact_id",
        )
        normalized_artifact_version = self._validate_required_string(
            self.artifact_version,
            field_name="artifact_version",
        )
        normalized_storage_uri = self._validate_required_string(
            self.storage_uri,
            field_name="storage_uri",
        )
        normalized_target_column = self._validate_required_string(
            self.target_column,
            field_name="target_column",
        )
        normalized_registration_id = self._validate_required_string(
            self.registration_id,
            field_name="registration_id",
        )

        if not isinstance(
            self.model_category,
            ForecastModelCategory,
        ):
            raise ForecastRegistryError(
                "Registration model_category is invalid.",
                context={
                    "received_type": type(
                        self.model_category
                    ).__name__,
                },
            )

        if not isinstance(
            self.artifact_status,
            ForecastArtifactStatus,
        ):
            raise ForecastRegistryError(
                "Registration artifact_status is invalid.",
                context={
                    "received_type": type(
                        self.artifact_status
                    ).__name__,
                },
            )

        if self.artifact_status == ForecastArtifactStatus.FAILED:
            raise ForecastRegistryError(
                "Failed forecast artifacts cannot be registered.",
                context={
                    "artifact_id": normalized_artifact_id,
                    "model_name": normalized_model_name,
                },
            )

        normalized_features = self._validate_feature_columns(
            self.feature_columns
        )

        if (
            isinstance(self.forecast_horizon, bool)
            or not isinstance(self.forecast_horizon, int)
        ):
            raise ForecastRegistryError(
                "Registration forecast_horizon must be an integer.",
                context={
                    "received_type": type(
                        self.forecast_horizon
                    ).__name__,
                },
            )

        if self.forecast_horizon <= 0:
            raise ForecastRegistryError(
                "Registration forecast_horizon must be greater than zero.",
                context={
                    "forecast_horizon": self.forecast_horizon,
                },
            )

        normalized_primary_metric = self._normalize_optional_string(
            self.primary_metric,
            field_name="primary_metric",
        )

        normalized_primary_metric_value = (
            self._validate_optional_finite_number(
                self.primary_metric_value,
                field_name="primary_metric_value",
            )
        )

        if (
            normalized_primary_metric is None
            and normalized_primary_metric_value is not None
        ):
            raise ForecastRegistryError(
                "primary_metric is required when "
                "primary_metric_value is supplied."
            )

        if (
            normalized_primary_metric is not None
            and normalized_primary_metric_value is None
        ):
            raise ForecastRegistryError(
                "primary_metric_value is required when "
                "primary_metric is supplied."
            )

        self._validate_timezone_aware_datetime(
            self.registered_at,
            field_name="registered_at",
        )

        normalized_metadata = self._validate_metadata(
            self.metadata
        )

        object.__setattr__(
            self,
            "model_name",
            normalized_model_name,
        )
        object.__setattr__(
            self,
            "model_version",
            normalized_model_version,
        )
        object.__setattr__(
            self,
            "algorithm",
            normalized_algorithm,
        )
        object.__setattr__(
            self,
            "artifact_id",
            normalized_artifact_id,
        )
        object.__setattr__(
            self,
            "artifact_version",
            normalized_artifact_version,
        )
        object.__setattr__(
            self,
            "storage_uri",
            normalized_storage_uri,
        )
        object.__setattr__(
            self,
            "target_column",
            normalized_target_column,
        )
        object.__setattr__(
            self,
            "feature_columns",
            normalized_features,
        )
        object.__setattr__(
            self,
            "primary_metric",
            normalized_primary_metric,
        )
        object.__setattr__(
            self,
            "primary_metric_value",
            normalized_primary_metric_value,
        )
        object.__setattr__(
            self,
            "registration_id",
            normalized_registration_id,
        )
        object.__setattr__(
            self,
            "training_dataset_id",
            self._normalize_optional_string(
                self.training_dataset_id,
                field_name="training_dataset_id",
            ),
        )
        object.__setattr__(
            self,
            "training_dataset_version",
            self._normalize_optional_string(
                self.training_dataset_version,
                field_name="training_dataset_version",
            ),
        )
        object.__setattr__(
            self,
            "experiment_id",
            self._normalize_optional_string(
                self.experiment_id,
                field_name="experiment_id",
            ),
        )
        object.__setattr__(
            self,
            "run_id",
            self._normalize_optional_string(
                self.run_id,
                field_name="run_id",
            ),
        )
        object.__setattr__(
            self,
            "checksum",
            self._normalize_optional_string(
                self.checksum,
                field_name="checksum",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            normalized_metadata,
        )

    @property
    def model_identity(self) -> str:
        """Return the stable registered model identity."""
        return f"{self.model_name}:{self.model_version}"

    @property
    def artifact_identity(self) -> str:
        """Return the stable trained-artifact identity."""
        return f"{self.artifact_id}:{self.artifact_version}"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe registry record."""
        return {
            "registration_id": self.registration_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_identity": self.model_identity,
            "model_category": self.model_category.value,
            "algorithm": self.algorithm,
            "artifact_id": self.artifact_id,
            "artifact_version": self.artifact_version,
            "artifact_identity": self.artifact_identity,
            "artifact_status": self.artifact_status.value,
            "storage_uri": self.storage_uri,
            "checksum": self.checksum,
            "target_column": self.target_column,
            "feature_columns": list(self.feature_columns),
            "forecast_horizon": self.forecast_horizon,
            "primary_metric": self.primary_metric,
            "primary_metric_value": self.primary_metric_value,
            "training_dataset_id": self.training_dataset_id,
            "training_dataset_version": (
                self.training_dataset_version
            ),
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "registered_at": self.registered_at.isoformat(),
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def _validate_required_string(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        """Validate one required non-empty string."""
        if not isinstance(value, str):
            raise ForecastRegistryError(
                f"{field_name} must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = value.strip()

        if not normalized:
            raise ForecastRegistryError(
                f"{field_name} must not be empty."
            )

        return normalized

    @staticmethod
    def _normalize_optional_string(
        value: Any,
        *,
        field_name: str,
    ) -> str | None:
        """Normalize one optional string."""
        if value is None:
            return None

        return ForecastModelRegistration._validate_required_string(
            value,
            field_name=field_name,
        )

    @staticmethod
    def _validate_feature_columns(
        feature_columns: Any,
    ) -> tuple[str, ...]:
        """Validate ordered feature-column names."""
        if not isinstance(feature_columns, tuple):
            raise ForecastRegistryError(
                "feature_columns must be stored as a tuple.",
                context={
                    "received_type": type(
                        feature_columns
                    ).__name__,
                },
            )

        normalized: list[str] = []
        seen: set[str] = set()

        for index, feature_name in enumerate(feature_columns):
            normalized_name = (
                ForecastModelRegistration._validate_required_string(
                    feature_name,
                    field_name=f"feature_columns[{index}]",
                )
            )

            normalized_key = normalized_name.lower()

            if normalized_key in seen:
                raise ForecastRegistryError(
                    "feature_columns cannot contain duplicates.",
                    context={
                        "feature_column": normalized_name,
                        "index": index,
                    },
                )

            normalized.append(normalized_name)
            seen.add(normalized_key)

        return tuple(normalized)

    @staticmethod
    def _validate_optional_finite_number(
        value: Any,
        *,
        field_name: str,
    ) -> float | None:
        """Validate one optional finite numeric value."""
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ForecastRegistryError(
                f"{field_name} must be numeric.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = float(value)

        if not math.isfinite(normalized):
            raise ForecastRegistryError(
                f"{field_name} must be finite."
            )

        return normalized

    @staticmethod
    def _validate_timezone_aware_datetime(
        value: Any,
        *,
        field_name: str,
    ) -> None:
        """Validate one timezone-aware datetime."""
        if not isinstance(value, datetime):
            raise ForecastRegistryError(
                f"{field_name} must be a datetime.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ForecastRegistryError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _validate_metadata(
        metadata: Any,
    ) -> dict[str, Any]:
        """Validate and copy registry metadata."""
        if not isinstance(metadata, Mapping):
            raise ForecastRegistryError(
                "Registration metadata must be a mapping.",
                context={
                    "received_type": type(metadata).__name__,
                },
            )

        return dict(metadata)


class EnterpriseModelRegistry:
    """
    Thread-safe in-memory registry of forecast model artifact references.

    The registry maintains one immutable registration per normalized
    ``model_name`` and ``model_version`` pair.

    It intentionally does not:

    - store live forecasting model objects;
    - load or deserialize model artifacts;
    - assign aliases;
    - select champions;
    - promote models between lifecycle environments;
    - persist registry state.

    Those concerns belong to model-loading, catalog, versioning, promotion,
    and persistence modules.
    """

    def __init__(self) -> None:
        """Initialize an empty instance-local registry."""
        self._registrations: dict[
            tuple[str, str],
            ForecastModelRegistration,
        ] = {}
        self._artifact_index: dict[
            str,
            tuple[str, str],
        ] = {}
        self._lock = RLock()

    @property
    def total_models(self) -> int:
        """Return the total number of registered model versions."""
        with self._lock:
            return len(self._registrations)

    @property
    def is_empty(self) -> bool:
        """Return whether the registry contains no registrations."""
        return self.total_models == 0

    def register(
        self,
        *,
        artifact: ForecastArtifact,
        primary_metric: str | None = None,
        primary_metric_value: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastModelRegistration:
        """
        Register one persisted forecast artifact.

        Args:
            artifact:
                Immutable artifact metadata produced by model persistence.

            primary_metric:
                Optional canonical metric associated with model selection.

            primary_metric_value:
                Optional finite value associated with ``primary_metric``.

            metadata:
                Optional registry-specific governance metadata.

        Returns:
            Immutable ``ForecastModelRegistration``.

        Raises:
            ForecastRegistryError:
                If the artifact or registration request is invalid, or if the
                model identity or artifact identifier is already registered.
        """
        self._validate_artifact(artifact)

        registration = ForecastModelRegistration(
            model_name=artifact.model_name,
            model_version=artifact.model_version,
            model_category=artifact.model_category,
            algorithm=artifact.algorithm,
            artifact_id=artifact.artifact_id,
            artifact_version=artifact.artifact_version,
            storage_uri=artifact.storage_uri,
            artifact_status=artifact.status,
            target_column=artifact.target_column,
            feature_columns=artifact.feature_columns,
            forecast_horizon=artifact.forecast_horizon,
            primary_metric=primary_metric,
            primary_metric_value=primary_metric_value,
            training_dataset_id=artifact.training_dataset_id,
            training_dataset_version=(
                artifact.training_dataset_version
            ),
            experiment_id=artifact.experiment_id,
            run_id=artifact.run_id,
            checksum=artifact.checksum,
            metadata={
                **dict(artifact.metadata),
                **dict(metadata or {}),
            },
        )

        key = self._build_key(
            model_name=registration.model_name,
            model_version=registration.model_version,
        )

        with self._lock:
            if key in self._registrations:
                raise ForecastRegistryError(
                    "Forecast model version is already registered.",
                    context={
                        "model_name": registration.model_name,
                        "model_version": registration.model_version,
                    },
                )

            if registration.artifact_id in self._artifact_index:
                existing_key = self._artifact_index[
                    registration.artifact_id
                ]

                raise ForecastRegistryError(
                    "Forecast artifact is already registered.",
                    context={
                        "artifact_id": registration.artifact_id,
                        "existing_model_name": existing_key[0],
                        "existing_model_version": existing_key[1],
                    },
                )

            self._registrations[key] = registration
            self._artifact_index[
                registration.artifact_id
            ] = key

        return registration

    def contains(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> bool:
        """Return whether a model version is registered."""
        key = self._build_key(
            model_name=model_name,
            model_version=model_version,
        )

        with self._lock:
            return key in self._registrations

    def contains_artifact(
        self,
        artifact_id: str,
    ) -> bool:
        """Return whether an artifact identifier is registered."""
        normalized_artifact_id = (
            ForecastModelRegistration._validate_required_string(
                artifact_id,
                field_name="artifact_id",
            )
        )

        with self._lock:
            return normalized_artifact_id in self._artifact_index

    def get(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelRegistration:
        """
        Retrieve one registration by model identity.

        Raises:
            ForecastRegistryError:
                If the requested model version is not registered.
        """
        key = self._build_key(
            model_name=model_name,
            model_version=model_version,
        )

        with self._lock:
            registration = self._registrations.get(key)

        if registration is None:
            raise ForecastRegistryError(
                "Forecast model version is not registered.",
                context={
                    "model_name": model_name,
                    "model_version": model_version,
                },
            )

        return registration

    def get_by_artifact_id(
        self,
        artifact_id: str,
    ) -> ForecastModelRegistration:
        """
        Retrieve one registration by artifact identifier.

        Raises:
            ForecastRegistryError:
                If the artifact identifier is not registered.
        """
        normalized_artifact_id = (
            ForecastModelRegistration._validate_required_string(
                artifact_id,
                field_name="artifact_id",
            )
        )

        with self._lock:
            key = self._artifact_index.get(
                normalized_artifact_id
            )

            registration = (
                self._registrations.get(key)
                if key is not None
                else None
            )

        if registration is None:
            raise ForecastRegistryError(
                "Forecast artifact is not registered.",
                context={
                    "artifact_id": normalized_artifact_id,
                },
            )

        return registration

    def list_models(
        self,
    ) -> tuple[ForecastModelRegistration, ...]:
        """
        Return all registrations in deterministic order.

        Ordering:
            1. normalized model name;
            2. normalized model version;
            3. registration identifier.
        """
        with self._lock:
            registrations = tuple(
                self._registrations.values()
            )

        return tuple(
            sorted(
                registrations,
                key=lambda registration: (
                    registration.model_name.lower(),
                    registration.model_version.lower(),
                    registration.registration_id,
                ),
            )
        )

    def list_versions(
        self,
        model_name: str,
    ) -> tuple[ForecastModelRegistration, ...]:
        """Return all registered versions of one model."""
        normalized_model_name = self._normalize_identity_value(
            model_name,
            field_name="model_name",
        )

        with self._lock:
            matching = tuple(
                registration
                for key, registration
                in self._registrations.items()
                if key[0] == normalized_model_name
            )

        return tuple(
            sorted(
                matching,
                key=lambda registration: (
                    registration.model_version.lower(),
                    registration.registration_id,
                ),
            )
        )

    def remove(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelRegistration:
        """
        Remove and return one registration.

        Raises:
            ForecastRegistryError:
                If the requested model version is not registered.
        """
        key = self._build_key(
            model_name=model_name,
            model_version=model_version,
        )

        with self._lock:
            registration = self._registrations.pop(
                key,
                None,
            )

            if registration is not None:
                self._artifact_index.pop(
                    registration.artifact_id,
                    None,
                )

        if registration is None:
            raise ForecastRegistryError(
                "Cannot remove an unregistered forecast model version.",
                context={
                    "model_name": model_name,
                    "model_version": model_version,
                },
            )

        return registration

    def clear(self) -> None:
        """
        Remove all registry records.

        This operation is intended for controlled validation, test isolation,
        or explicitly managed registry resets.
        """
        with self._lock:
            self._registrations.clear()
            self._artifact_index.clear()

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe registry inventory."""
        registrations = self.list_models()

        return {
            "total_models": len(registrations),
            "is_empty": len(registrations) == 0,
            "registrations": [
                registration.to_dict()
                for registration in registrations
            ],
        }

    @staticmethod
    def _validate_artifact(
        artifact: Any,
    ) -> None:
        """Validate the artifact supplied for registration."""
        if artifact is None:
            raise ForecastRegistryError(
                "Forecast artifact cannot be None.",
                context={
                    "argument": "artifact",
                },
            )

        if not isinstance(artifact, ForecastArtifact):
            raise ForecastRegistryError(
                "artifact must be a ForecastArtifact.",
                context={
                    "received_type": type(artifact).__name__,
                },
            )

        if artifact.status == ForecastArtifactStatus.FAILED:
            raise ForecastRegistryError(
                "Failed forecast artifacts cannot be registered.",
                context={
                    "artifact_id": artifact.artifact_id,
                    "model_name": artifact.model_name,
                },
            )

    @classmethod
    def _build_key(
        cls,
        *,
        model_name: str,
        model_version: str,
    ) -> tuple[str, str]:
        """Build the normalized model-identity registry key."""
        return (
            cls._normalize_identity_value(
                model_name,
                field_name="model_name",
            ),
            cls._normalize_identity_value(
                model_version,
                field_name="model_version",
            ),
        )

    @staticmethod
    def _normalize_identity_value(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        """Normalize a model identity component for registry lookup."""
        normalized = (
            ForecastModelRegistration._validate_required_string(
                value,
                field_name=field_name,
            )
        )

        return normalized.lower()


__all__ = [
    "EnterpriseModelRegistry",
    "ForecastModelRegistration",
]