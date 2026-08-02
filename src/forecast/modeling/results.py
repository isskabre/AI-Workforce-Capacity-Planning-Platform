"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.results

Description:
    Defines immutable, standardized result objects returned by enterprise
    forecast training, prediction, and evaluation operations.

    These result contracts provide consistent outputs across statistical,
    machine-learning, deep-learning, baseline, and ensemble model adapters.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from forecast.modeling.artifacts import ForecastArtifact


class ForecastExecutionStatus(StrEnum):
    """Standard execution outcomes for forecast modeling operations."""

    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


def _serialize_datetime(value: datetime | None) -> str | None:
    """Return an ISO-8601 timestamp when a datetime is available."""
    return value.isoformat() if value is not None else None


@dataclass(frozen=True, slots=True)
class ForecastTrainingResult:
    """
    Immutable result returned by model-training operations.

    Attributes:
        model_name:
            Stable enterprise model name.
        model_version:
            Forecast model implementation version.
        status:
            Overall training execution status.
        artifact:
            Optional persisted or in-memory artifact metadata.
        metrics:
            Training or validation metrics generated during training.
        hyperparameters:
            Effective hyperparameters used by the model.
        training_records:
            Number of records used for model fitting.
        validation_records:
            Number of records used for validation.
        training_duration_seconds:
            Total training duration in seconds.
        feature_columns:
            Ordered features used during training.
        target_column:
            Target variable predicted by the model.
        forecast_horizon:
            Number of future periods modeled.
        experiment_id:
            Optional enterprise experiment identifier.
        run_id:
            Optional experiment-tracking run identifier.
        result_id:
            Unique result identifier.
        started_at:
            UTC timestamp when training started.
        completed_at:
            Optional UTC timestamp when training completed.
        warnings:
            Non-fatal execution warnings.
        metadata:
            Additional serializable execution metadata.
        error:
            Optional serialized error details.
    """

    model_name: str
    model_version: str
    status: ForecastExecutionStatus
    artifact: ForecastArtifact | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)
    hyperparameters: Mapping[str, Any] = field(default_factory=dict)
    training_records: int = 0
    validation_records: int = 0
    training_duration_seconds: float | None = None
    feature_columns: tuple[str, ...] = ()
    target_column: str = ""
    forecast_horizon: int = 1
    experiment_id: str | None = None
    run_id: str | None = None
    result_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    error: Mapping[str, Any] | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether training completed successfully."""
        return self.status in {
            ForecastExecutionStatus.SUCCESS,
            ForecastExecutionStatus.PARTIAL_SUCCESS,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe training result."""
        return {
            "result_id": self.result_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "status": self.status.value,
            "succeeded": self.succeeded,
            "artifact": (
                self.artifact.to_dict()
                if self.artifact is not None
                else None
            ),
            "metrics": dict(self.metrics),
            "hyperparameters": dict(self.hyperparameters),
            "training_records": self.training_records,
            "validation_records": self.validation_records,
            "training_duration_seconds": self.training_duration_seconds,
            "feature_columns": list(self.feature_columns),
            "target_column": self.target_column,
            "forecast_horizon": self.forecast_horizon,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "started_at": _serialize_datetime(self.started_at),
            "completed_at": _serialize_datetime(self.completed_at),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
            "error": dict(self.error) if self.error is not None else None,
        }


@dataclass(frozen=True, slots=True)
class ForecastPredictionResult:
    """
    Immutable result returned by model prediction operations.

    Attributes:
        model_name:
            Stable enterprise model name.
        model_version:
            Forecast model implementation or artifact version.
        status:
            Overall prediction execution status.
        predictions:
            Ordered point forecasts.
        forecast_horizon:
            Number of forecasted future periods.
        prediction_timestamps:
            Optional timestamps corresponding to forecast values.
        lower_bounds:
            Optional lower prediction interval values.
        upper_bounds:
            Optional upper prediction interval values.
        inference_duration_seconds:
            Prediction execution duration.
        artifact_id:
            Optional trained artifact identifier.
        result_id:
            Unique result identifier.
        generated_at:
            UTC timestamp when prediction output was created.
        metadata:
            Additional serializable prediction metadata.
        warnings:
            Non-fatal warnings.
        error:
            Optional serialized error details.
    """

    model_name: str
    model_version: str
    status: ForecastExecutionStatus
    predictions: Sequence[float] = ()
    forecast_horizon: int = 1
    prediction_timestamps: Sequence[datetime] = ()
    lower_bounds: Sequence[float] | None = None
    upper_bounds: Sequence[float] | None = None
    inference_duration_seconds: float | None = None
    artifact_id: str | None = None
    result_id: str = field(default_factory=lambda: str(uuid4()))
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    error: Mapping[str, Any] | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether prediction completed successfully."""
        return self.status in {
            ForecastExecutionStatus.SUCCESS,
            ForecastExecutionStatus.PARTIAL_SUCCESS,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe prediction result."""
        return {
            "result_id": self.result_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "status": self.status.value,
            "succeeded": self.succeeded,
            "predictions": list(self.predictions),
            "forecast_horizon": self.forecast_horizon,
            "prediction_timestamps": [
                value.isoformat()
                for value in self.prediction_timestamps
            ],
            "lower_bounds": (
                list(self.lower_bounds)
                if self.lower_bounds is not None
                else None
            ),
            "upper_bounds": (
                list(self.upper_bounds)
                if self.upper_bounds is not None
                else None
            ),
            "inference_duration_seconds": (
                self.inference_duration_seconds
            ),
            "artifact_id": self.artifact_id,
            "generated_at": self.generated_at.isoformat(),
            "metadata": dict(self.metadata),
            "warnings": list(self.warnings),
            "error": dict(self.error) if self.error is not None else None,
        }


@dataclass(frozen=True, slots=True)
class ForecastEvaluationResult:
    """
    Immutable result returned by forecast evaluation operations.

    Attributes:
        model_name:
            Stable enterprise model name.
        model_version:
            Model implementation or artifact version.
        status:
            Overall evaluation execution status.
        metrics:
            Standardized forecast metric values.
        primary_metric:
            Metric used for ranking.
        primary_metric_value:
            Calculated value of the primary metric.
        evaluation_records:
            Number of observations included in evaluation.
        rank:
            Optional rank assigned during model comparison.
        champion:
            Whether the model was selected as champion.
        residual_summary:
            Optional residual diagnostic values.
        feature_importance:
            Optional feature importance values.
        result_id:
            Unique result identifier.
        evaluated_at:
            UTC timestamp when evaluation completed.
        metadata:
            Additional serializable evaluation metadata.
        warnings:
            Non-fatal evaluation warnings.
        error:
            Optional serialized error details.
    """

    model_name: str
    model_version: str
    status: ForecastExecutionStatus
    metrics: Mapping[str, float] = field(default_factory=dict)
    primary_metric: str = ""
    primary_metric_value: float | None = None
    evaluation_records: int = 0
    rank: int | None = None
    champion: bool = False
    residual_summary: Mapping[str, float] = field(default_factory=dict)
    feature_importance: Mapping[str, float] = field(default_factory=dict)
    result_id: str = field(default_factory=lambda: str(uuid4()))
    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    error: Mapping[str, Any] | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether evaluation completed successfully."""
        return self.status in {
            ForecastExecutionStatus.SUCCESS,
            ForecastExecutionStatus.PARTIAL_SUCCESS,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe evaluation result."""
        return {
            "result_id": self.result_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "status": self.status.value,
            "succeeded": self.succeeded,
            "metrics": dict(self.metrics),
            "primary_metric": self.primary_metric,
            "primary_metric_value": self.primary_metric_value,
            "evaluation_records": self.evaluation_records,
            "rank": self.rank,
            "champion": self.champion,
            "residual_summary": dict(self.residual_summary),
            "feature_importance": dict(self.feature_importance),
            "evaluated_at": self.evaluated_at.isoformat(),
            "metadata": dict(self.metadata),
            "warnings": list(self.warnings),
            "error": dict(self.error) if self.error is not None else None,
        }


__all__ = [
    "ForecastEvaluationResult",
    "ForecastExecutionStatus",
    "ForecastPredictionResult",
    "ForecastTrainingResult",
]