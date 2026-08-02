"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.artifacts

Description:
    Defines immutable artifact metadata produced by trained forecasting
    models.

    Forecast artifacts provide the standardized boundary between model
    training, persistence, model registration, lineage, and inference.
    This module contains metadata only and does not serialize or load
    executable model objects.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from forecast.modeling.contracts import ForecastModelCategory


class ForecastArtifactStatus(StrEnum):
    """Lifecycle states for a persisted forecasting artifact."""

    CREATED = "CREATED"
    PERSISTED = "PERSISTED"
    REGISTERED = "REGISTERED"
    CHAMPION = "CHAMPION"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ForecastArtifact:
    """
    Immutable metadata describing a trained forecasting model artifact.

    The artifact records the information required to identify, govern,
    reproduce, register, and load a trained forecasting model. It does not
    contain the executable estimator itself.

    Attributes:
        model_name:
            Stable enterprise name of the forecasting implementation.
        model_version:
            Version of the forecasting implementation.
        model_category:
            High-level category of the forecasting algorithm.
        algorithm:
            Concrete algorithm identifier, such as ``random_forest``.
        storage_uri:
            Platform-independent URI of the persisted model artifact.
        feature_columns:
            Ordered feature columns used during training.
        target_column:
            Target variable predicted by the model.
        forecast_horizon:
            Number of future periods predicted by the model.
        hyperparameters:
            Effective hyperparameters used for training.
        metrics:
            Evaluation metrics associated with the trained artifact.
        artifact_id:
            Globally unique identifier for this trained artifact.
        artifact_version:
            Version assigned to this particular trained artifact.
        status:
            Current artifact lifecycle status.
        checksum:
            Optional integrity checksum for the persisted model.
        training_dataset_id:
            Optional identifier of the training dataset.
        training_dataset_version:
            Optional version of the training dataset.
        experiment_id:
            Optional experiment or execution identifier.
        run_id:
            Optional experiment-tracking run identifier.
        created_at:
            UTC timestamp when the artifact metadata was created.
        trained_at:
            Optional UTC timestamp when training completed.
        registered_at:
            Optional UTC timestamp when registry registration completed.
        metadata:
            Additional serializable enterprise metadata.
    """

    model_name: str
    model_version: str
    model_category: ForecastModelCategory
    algorithm: str
    storage_uri: str
    feature_columns: tuple[str, ...]
    target_column: str
    forecast_horizon: int
    hyperparameters: Mapping[str, Any] = field(default_factory=dict)
    metrics: Mapping[str, float] = field(default_factory=dict)
    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    artifact_version: str = "1"
    status: ForecastArtifactStatus = ForecastArtifactStatus.CREATED
    checksum: str | None = None
    training_dataset_id: str | None = None
    training_dataset_version: str | None = None
    experiment_id: str | None = None
    run_id: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    trained_at: datetime | None = None
    registered_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serialization-safe artifact representation.

        Returns:
            Dictionary containing primitive values suitable for JSON,
            metadata persistence, model registry storage, or audit logging.
        """
        return {
            "artifact_id": self.artifact_id,
            "artifact_version": self.artifact_version,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_category": self.model_category.value,
            "algorithm": self.algorithm,
            "status": self.status.value,
            "storage_uri": self.storage_uri,
            "checksum": self.checksum,
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "forecast_horizon": self.forecast_horizon,
            "hyperparameters": dict(self.hyperparameters),
            "metrics": dict(self.metrics),
            "training_dataset_id": self.training_dataset_id,
            "training_dataset_version": self.training_dataset_version,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat(),
            "trained_at": (
                self.trained_at.isoformat()
                if self.trained_at is not None
                else None
            ),
            "registered_at": (
                self.registered_at.isoformat()
                if self.registered_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "ForecastArtifact",
    "ForecastArtifactStatus",
]