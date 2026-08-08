"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.naive.model

Description:
    Implements the enterprise Naive Last-Value forecasting model.

    The model orchestrates the NaiveLastValueEstimator through the standard
    training, prediction, evaluation, persistence, serialization, artifact,
    result, and lifecycle contracts established by the platform.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from os import PathLike
from pathlib import Path
from time import perf_counter
from typing import Any, Self

from src.forecast.algorithms.base.forecast_model import EnterpriseForecastModel
from src.forecast.algorithms.base.serializer import EnterpriseSerializer
from src.forecast.algorithms.naive.estimator import NaiveLastValueEstimator
from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastEvaluationError,
    ForecastPersistenceError,
    ForecastPredictionError,
    ForecastStateError,
    ForecastTrainingError,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


class NaiveForecastModel(EnterpriseForecastModel):
    """
    Enterprise implementation of a Naive Last-Value forecast model.

    The final observed training target becomes the prediction for every
    requested future period. This deterministic baseline establishes the
    minimum performance that more advanced models must outperform.

    Expected training-dataset formats:

    1. Mapping with ``features`` and ``target`` keys:

       {
           "features": [[...], [...]],
           "target": [100.0, 110.0],
       }

    2. Two-item tuple:

       (
           [[...], [...]],
           [100.0, 110.0],
       )

    3. Target-only sequence:

       [100.0, 110.0, 120.0]

       In this case, placeholder feature records are generated because the
       naive estimator does not use predictor values.
    """

    MODEL_KEY = "naive_last_value"
    DISPLAY_NAME = "Naive Last-Value Forecast"
    ALGORITHM = "naive_last_value"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        estimator_parameters: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            model_key=self.MODEL_KEY,
            display_name=self.DISPLAY_NAME,
            category=ForecastModelCategory.BASELINE,
            algorithm=self.ALGORITHM,
            version=self.VERSION,
            capabilities=frozenset({
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.MULTI_STEP_FORECAST,
            }),
        )

        self._estimator_parameters = dict(
            estimator_parameters or {
                "strategy": "last_value",
            }
        )

        self._estimator = NaiveLastValueEstimator(
            parameters=self._estimator_parameters
        )

    @property
    def estimator(self) -> NaiveLastValueEstimator:
        """Return the underlying naive estimator."""
        return self._estimator

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        context: ForecastTrainingContext,
    ) -> ForecastTrainingResult:
        """
        Train the naive model using the final observed target value.

        Args:
            context:
                Standard enterprise training context.

        Returns:
            Standardized training result.

        Raises:
            ForecastTrainingError:
                If dataset extraction or estimator fitting fails.
        """
        started_at = datetime.now(timezone.utc)
        timer_started = perf_counter()

        self._state = ForecastModelState.TRAINING
        self._training_context = context

        try:
            features, target = self._extract_training_data(
                context.training_dataset
            )

            if not self.estimator.initialized:
                self.estimator.initialize(
                    feature_names=context.feature_columns,
                    target_name=context.target_column,
                )

            self.estimator.fit(
                features=features,
                target=target,
            )

            self._state = ForecastModelState.TRAINED

            return ForecastTrainingResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                hyperparameters=dict(self.estimator.parameters),
                training_records=len(target),
                validation_records=self._safe_length(
                    context.validation_dataset
                ),
                training_duration_seconds=(
                    perf_counter() - timer_started
                ),
                feature_columns=context.feature_columns,
                target_column=context.target_column,
                forecast_horizon=context.forecast_horizon,
                experiment_id=context.experiment_id,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                metadata={
                    "algorithm": self.algorithm,
                    "learned_last_value": self.estimator.last_value,
                },
            )

        except ForecastTrainingError:
            self._state = ForecastModelState.FAILED
            raise
        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastTrainingError(
                "Naive forecast model training failed.",
                context={
                    "model_key": self.model_key,
                    "target_column": context.target_column,
                    "forecast_horizon": context.forecast_horizon,
                },
                cause=exc,
            ) from exc

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        """
        Generate repeated last-value forecasts.

        The number of predictions is resolved from the prediction dataset.
        When the prediction dataset is an integer, it is treated as the
        requested prediction count.

        Args:
            context:
                Standard enterprise prediction context.

        Returns:
            Standardized prediction result.

        Raises:
            ForecastStateError:
                If the model has not been trained or loaded.
            ForecastPredictionError:
                If prediction fails.
        """
        if not self.estimator.fitted:
            raise ForecastStateError(
                "Naive forecast model must be trained or loaded before "
                "prediction.",
                context={
                    "model_key": self.model_key,
                    "state": self.state.value,
                },
            )

        timer_started = perf_counter()

        self._state = ForecastModelState.PREDICTING
        self._prediction_context = context

        try:
            predictions = self.estimator.predict(
                context.prediction_dataset
            )

            self._state = ForecastModelState.TRAINED

            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=(
                    context.model_version
                    or self.model_version
                ),
                status=ForecastExecutionStatus.SUCCESS,
                predictions=predictions,
                forecast_horizon=context.forecast_horizon,
                inference_duration_seconds=(
                    perf_counter() - timer_started
                ),
                artifact_id=(
                    self.artifact.artifact_id
                    if self.artifact is not None
                    else None
                ),
                metadata={
                    **dict(context.metadata),
                    "algorithm": self.algorithm,
                    "prediction_strategy": "last_value",
                },
            )

        except ForecastStateError:
            raise
        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastPredictionError(
                "Naive forecast generation failed.",
                context={
                    "model_key": self.model_key,
                    "forecast_horizon": context.forecast_horizon,
                },
                cause=exc,
            ) from exc

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        """
        Evaluate supplied actual and predicted values.

        Supported metrics are MAE, RMSE, MAPE, SMAPE, WAPE, and BIAS.
        Metric names are case-insensitive.

        Args:
            context:
                Standard enterprise evaluation context.

        Returns:
            Standardized evaluation result.

        Raises:
            ForecastEvaluationError:
                If values are incompatible or the metric is unsupported.
        """
        self._state = ForecastModelState.EVALUATING
        self._evaluation_context = context

        try:
            actual_values = self._to_float_tuple(
                context.actual_values,
                argument_name="actual_values",
            )
            predicted_values = self._to_float_tuple(
                context.predicted_values,
                argument_name="predicted_values",
            )

            if len(actual_values) != len(predicted_values):
                raise ValueError(
                    "Actual and predicted value counts must match."
                )

            if not actual_values:
                raise ValueError(
                    "Evaluation requires at least one observation."
                )

            metric_name = context.metric.strip().upper()
            metric_value = self._calculate_metric(
                metric_name=metric_name,
                actual_values=actual_values,
                predicted_values=predicted_values,
            )

            residuals = tuple(
                actual - predicted
                for actual, predicted in zip(
                    actual_values,
                    predicted_values,
                    strict=True,
                )
            )

            self._state = ForecastModelState.EVALUATED

            return ForecastEvaluationResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                metrics={
                    metric_name: metric_value,
                },
                primary_metric=metric_name,
                primary_metric_value=metric_value,
                evaluation_records=len(actual_values),
                residual_summary={
                    "mean_residual": sum(residuals) / len(residuals),
                    "minimum_residual": min(residuals),
                    "maximum_residual": max(residuals),
                },
                metadata={
                    **dict(context.metadata),
                    "algorithm": self.algorithm,
                },
            )

        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastEvaluationError(
                "Naive forecast evaluation failed.",
                context={
                    "model_key": self.model_key,
                    "metric": context.metric,
                },
                cause=exc,
            ) from exc

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        """
        Persist the complete model state as JSON.

        The destination must be a local or mounted filesystem path supported
        by ``pathlib.Path``. Direct ``s3://`` URI writing is intentionally not
        performed by this low-level adapter.

        Args:
            destination:
                JSON artifact destination.

        Returns:
            Standardized forecast artifact metadata.

        Raises:
            ForecastStateError:
                If the model has not been fitted.
            ForecastPersistenceError:
                If persistence fails.
        """
        if not self.estimator.fitted:
            raise ForecastStateError(
                "Naive forecast model must be trained before persistence.",
                context={
                    "model_key": self.model_key,
                    "state": self.state.value,
                },
            )

        self._state = ForecastModelState.SAVING

        try:
            destination_path = Path(destination)
            payload = self.serialize()

            EnterpriseSerializer.save_json(
                payload,
                destination_path,
            )

            training_context = self.training_context

            artifact = ForecastArtifact(
                model_name=self.model_name,
                model_version=self.model_version,
                model_category=self.model_category,
                algorithm=self.algorithm,
                storage_uri=str(destination_path),
                feature_columns=(
                    training_context.feature_columns
                    if training_context is not None
                    else self.estimator.feature_names
                ),
                target_column=(
                    training_context.target_column
                    if training_context is not None
                    else self.estimator.target_name or ""
                ),
                forecast_horizon=(
                    training_context.forecast_horizon
                    if training_context is not None
                    else 1
                ),
                hyperparameters=dict(self.estimator.parameters),
                artifact_version="1",
                status=ForecastArtifactStatus.PERSISTED,
                checksum=EnterpriseSerializer.checksum(payload),
                experiment_id=(
                    training_context.experiment_id
                    if training_context is not None
                    else None
                ),
                trained_at=datetime.now(timezone.utc),
                metadata={
                    "estimator_name": self.estimator.estimator_name,
                    "framework": self.estimator.framework,
                },
            )

            self._artifact = artifact
            self._state = ForecastModelState.SAVED

            return artifact

        except ForecastStateError:
            raise
        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastPersistenceError(
                "Naive forecast model persistence failed.",
                context={
                    "model_key": self.model_key,
                    "destination": str(destination),
                },
                cause=exc,
            ) from exc

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        """
        Load a persisted naive forecast model.

        Args:
            source:
                JSON artifact source.
            metadata:
                Optional additional load metadata.

        Returns:
            Loaded model.
        """
        try:
            source_path = Path(source)
            payload = EnterpriseSerializer.load_json(source_path)

            model = cls.deserialize(payload)
            model._state = ForecastModelState.LOADED

            artifact_metadata = dict(metadata or {})

            model._artifact = ForecastArtifact(
                model_name=model.model_name,
                model_version=model.model_version,
                model_category=model.model_category,
                algorithm=model.algorithm,
                storage_uri=str(source_path),
                feature_columns=model.estimator.feature_names,
                target_column=model.estimator.target_name or "",
                forecast_horizon=int(
                    artifact_metadata.get("forecast_horizon", 1)
                ),
                hyperparameters=dict(model.estimator.parameters),
                status=ForecastArtifactStatus.PERSISTED,
                checksum=EnterpriseSerializer.checksum(payload),
                metadata=artifact_metadata,
            )

            return model

        except Exception as exc:
            raise ForecastPersistenceError(
                "Naive forecast model loading failed.",
                context={
                    "source": str(source),
                },
                cause=exc,
            ) from exc

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def serialize(self) -> Mapping[str, Any]:
        """Return serialization-safe complete model state."""
        return {
            "schema_version": "1.0",
            "model_key": self.model_key,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_category": self.model_category.value,
            "algorithm": self.algorithm,
            "state": self.state.value,
            "estimator_parameters": dict(
                self._estimator_parameters
            ),
            "estimator": dict(self.estimator.serialize()),
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct a model from serialized state."""
        model = cls(
            estimator_parameters=payload.get(
                "estimator_parameters"
            )
        )

        estimator_payload = payload.get("estimator")

        if not isinstance(estimator_payload, Mapping):
            raise ValueError(
                "Serialized naive model is missing estimator state."
            )

        model._estimator = (
            NaiveLastValueEstimator.deserialize(
                estimator_payload
            )
        )

        state_value = payload.get(
            "state",
            ForecastModelState.CREATED.value,
        )

        model._state = ForecastModelState(state_value)

        return model

    def reset(self) -> None:
        """Reset model and estimator runtime state."""
        super().reset()
        self.estimator.reset()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_training_data(
        training_dataset: Any,
    ) -> tuple[Any, Sequence[Any]]:
        """Extract feature and target collections from supported formats."""
        if isinstance(training_dataset, Mapping):
            if "target" not in training_dataset:
                raise ValueError(
                    "Training dataset mapping must contain a 'target' key."
                )

            target = training_dataset["target"]
            features = training_dataset.get("features")

            if features is None:
                features = tuple(
                    () for _ in range(len(target))
                )

            return features, target

        if (
            isinstance(training_dataset, tuple)
            and len(training_dataset) == 2
        ):
            return (
                training_dataset[0],
                training_dataset[1],
            )

        if isinstance(training_dataset, (str, bytes)):
            raise ValueError(
                "Training dataset must not be a string."
            )

        try:
            target = tuple(training_dataset)
        except TypeError as exc:
            raise ValueError(
                "Unsupported training dataset format."
            ) from exc

        features = tuple(() for _ in target)

        return features, target

    @staticmethod
    def _safe_length(value: Any) -> int:
        """Return a record count when available."""
        if value is None:
            return 0

        try:
            return len(value)
        except TypeError:
            return 0

    @staticmethod
    def _to_float_tuple(
        values: Any,
        *,
        argument_name: str,
    ) -> tuple[float, ...]:
        """Convert an iterable into finite float values."""
        if values is None:
            raise ValueError(
                f"{argument_name} must not be None."
            )

        converted_values = (
            values.tolist()
            if hasattr(values, "tolist")
            else values
        )

        try:
            result = tuple(
                float(value)
                for value in converted_values
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{argument_name} must contain numeric values."
            ) from exc

        if any(not math.isfinite(value) for value in result):
            raise ValueError(
                f"{argument_name} must contain finite values."
            )

        return result

    @staticmethod
    def _calculate_metric(
        *,
        metric_name: str,
        actual_values: tuple[float, ...],
        predicted_values: tuple[float, ...],
    ) -> float:
        """Calculate a supported forecasting metric."""
        errors = tuple(
            actual - predicted
            for actual, predicted in zip(
                actual_values,
                predicted_values,
                strict=True,
            )
        )
        absolute_errors = tuple(abs(error) for error in errors)

        if metric_name == "MAE":
            return sum(absolute_errors) / len(absolute_errors)

        if metric_name == "RMSE":
            return math.sqrt(
                sum(error**2 for error in errors) / len(errors)
            )

        if metric_name == "BIAS":
            return sum(errors) / len(errors)

        if metric_name == "MAPE":
            eligible = tuple(
                abs((actual - predicted) / actual) * 100.0
                for actual, predicted in zip(
                    actual_values,
                    predicted_values,
                    strict=True,
                )
                if actual != 0.0
            )

            if not eligible:
                raise ValueError(
                    "MAPE cannot be calculated when all actual values "
                    "are zero."
                )

            return sum(eligible) / len(eligible)

        if metric_name == "SMAPE":
            components = tuple(
                (
                    0.0
                    if abs(actual) + abs(predicted) == 0.0
                    else (
                        200.0
                        * abs(actual - predicted)
                        / (abs(actual) + abs(predicted))
                    )
                )
                for actual, predicted in zip(
                    actual_values,
                    predicted_values,
                    strict=True,
                )
            )

            return sum(components) / len(components)

        if metric_name == "WAPE":
            denominator = sum(abs(value) for value in actual_values)

            if denominator == 0.0:
                raise ValueError(
                    "WAPE cannot be calculated when total actual volume "
                    "is zero."
                )

            return (
                sum(absolute_errors)
                / denominator
                * 100.0
            )

        raise ValueError(
            f"Unsupported evaluation metric: {metric_name}."
        )


__all__ = [
    "NaiveForecastModel",
]