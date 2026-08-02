"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.algorithms.random_forest.model

Description:
    Implements the enterprise Random Forest forecasting model.

    The model orchestrates RandomForestEstimator through the standardized
    training, prediction, evaluation, persistence, serialization, artifact,
    exception, result, and lifecycle contracts defined by the platform.

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

from forecast.algorithms.base.forecast_model import EnterpriseForecastModel
from forecast.algorithms.base.serializer import EnterpriseSerializer
from forecast.algorithms.random_forest.estimator import (
    RandomForestEstimator,
)
from forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from forecast.modeling.exceptions import (
    ForecastEvaluationError,
    ForecastPersistenceError,
    ForecastPredictionError,
    ForecastStateError,
    ForecastTrainingError,
)
from forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


class RandomForestForecastModel(EnterpriseForecastModel):
    """
    Enterprise Random Forest regression forecasting model.

    Supported training dataset formats:

    1. Mapping:

       {
           "features": [[...], [...]],
           "target": [100.0, 110.0],
       }

    2. Two-item tuple:

       (
           [[...], [...]],
           [100.0, 110.0],
       )
    """

    MODEL_KEY = "random_forest"
    DISPLAY_NAME = "Random Forest Forecast"
    ALGORITHM = "random_forest"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        n_estimators: int = 200,
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        max_features: str | int | float | None = 1.0,
        bootstrap: bool = True,
        random_state: int | None = 42,
        n_jobs: int | None = -1,
        estimator_parameters: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            model_key=self.MODEL_KEY,
            display_name=self.DISPLAY_NAME,
            category=ForecastModelCategory.MACHINE_LEARNING,
            algorithm=self.ALGORITHM,
            version=self.VERSION,
            capabilities=frozenset({
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.MULTI_STEP_FORECAST,
                ForecastModelCapability.FEATURE_IMPORTANCE,
            }),
        )

        self._estimator_parameters = dict(
            estimator_parameters or {}
        )

        self._estimator = RandomForestEstimator(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            bootstrap=bootstrap,
            random_state=random_state,
            n_jobs=n_jobs,
            parameters=self._estimator_parameters,
        )

    @property
    def estimator(self) -> RandomForestEstimator:
        """Return the underlying Random Forest estimator."""
        return self._estimator

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        context: ForecastTrainingContext,
    ) -> ForecastTrainingResult:
        """Train the Random Forest model."""
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
                validation_records=self._dataset_record_count(
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
                    **dict(context.metadata),
                    "algorithm": self.algorithm,
                    "feature_importances": list(
                        self.estimator.feature_importances
                    ),
                    "training_mae": (
                        self.estimator.training_metadata.get(
                            "training_mae"
                        )
                    ),
                    "training_mse": (
                        self.estimator.training_metadata.get(
                            "training_mse"
                        )
                    ),
                    "training_rmse": (
                        self.estimator.training_metadata.get(
                            "training_rmse"
                        )
                    ),
                },
            )

        except ForecastTrainingError:
            self._state = ForecastModelState.FAILED
            raise
        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastTrainingError(
                "Random Forest forecast model training failed.",
                context={
                    "model_key": self.model_key,
                    "forecast_horizon": context.forecast_horizon,
                    "n_estimators": self.estimator.n_estimators,
                    "max_depth": self.estimator.max_depth,
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
        """Generate Random Forest forecasts."""
        if not self.estimator.fitted:
            raise ForecastStateError(
                "Random Forest forecast model must be trained or loaded "
                "before prediction.",
                context={
                    "model_key": self.model_key,
                    "state": self.state.value,
                },
            )

        timer_started = perf_counter()

        self._state = ForecastModelState.PREDICTING
        self._prediction_context = context

        try:
            predictions, dispersion = (
                self.estimator.predict_with_dispersion(
                    context.prediction_dataset
                )
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
                    "prediction_dispersion": list(dispersion),
                    "n_estimators": self.estimator.n_estimators,
                },
            )

        except ForecastStateError:
            raise
        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastPredictionError(
                "Random Forest forecast generation failed.",
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

        Supported metrics:
            MAE, MSE, RMSE, MAPE, SMAPE, WAPE, R2, and BIAS.
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

            feature_importance = {
                feature_name: importance
                for feature_name, importance in zip(
                    self.estimator.feature_names,
                    self.estimator.feature_importances,
                    strict=False,
                )
            }

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
                    "mean_residual": (
                        sum(residuals) / len(residuals)
                    ),
                    "minimum_residual": min(residuals),
                    "maximum_residual": max(residuals),
                },
                feature_importance=feature_importance,
                metadata={
                    **dict(context.metadata),
                    "algorithm": self.algorithm,
                    "n_estimators": self.estimator.n_estimators,
                },
            )

        except Exception as exc:
            self._state = ForecastModelState.FAILED

            raise ForecastEvaluationError(
                "Random Forest forecast evaluation failed.",
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
        """Persist complete model state as JSON."""
        if not self.estimator.fitted:
            raise ForecastStateError(
                "Random Forest forecast model must be trained before "
                "persistence.",
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
                hyperparameters=dict(
                    self.estimator.parameters
                ),
                metrics={
                    "training_mae": (
                        self.estimator.training_metadata.get(
                            "training_mae"
                        )
                    ),
                    "training_mse": (
                        self.estimator.training_metadata.get(
                            "training_mse"
                        )
                    ),
                    "training_rmse": (
                        self.estimator.training_metadata.get(
                            "training_rmse"
                        )
                    ),
                },
                artifact_version="1",
                status=ForecastArtifactStatus.PERSISTED,
                checksum=EnterpriseSerializer.checksum(
                    payload
                ),
                experiment_id=(
                    training_context.experiment_id
                    if training_context is not None
                    else None
                ),
                trained_at=datetime.now(timezone.utc),
                metadata={
                    "estimator_name": (
                        self.estimator.estimator_name
                    ),
                    "framework": self.estimator.framework,
                    "feature_importances": list(
                        self.estimator.feature_importances
                    ),
                    "feature_count": self.estimator.feature_count,
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
                "Random Forest model persistence failed.",
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
        """Load a persisted Random Forest model."""
        try:
            source_path = Path(source)

            payload = EnterpriseSerializer.load_json(
                source_path
            )

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
                target_column=(
                    model.estimator.target_name or ""
                ),
                forecast_horizon=int(
                    artifact_metadata.get(
                        "forecast_horizon",
                        1,
                    )
                ),
                hyperparameters=dict(
                    model.estimator.parameters
                ),
                status=ForecastArtifactStatus.PERSISTED,
                checksum=EnterpriseSerializer.checksum(
                    payload
                ),
                metadata={
                    **artifact_metadata,
                    "feature_importances": list(
                        model.estimator.feature_importances
                    ),
                },
            )

            return model

        except Exception as exc:
            raise ForecastPersistenceError(
                "Random Forest model loading failed.",
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
            "estimator": dict(
                self.estimator.serialize()
            ),
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct the model from serialized state."""
        estimator_payload = payload.get("estimator")

        if not isinstance(estimator_payload, Mapping):
            raise ValueError(
                "Serialized Random Forest model is missing estimator state."
            )

        model = cls(
            n_estimators=int(
                estimator_payload.get(
                    "n_estimators",
                    200,
                )
            ),
            max_depth=estimator_payload.get("max_depth"),
            min_samples_split=int(
                estimator_payload.get(
                    "min_samples_split",
                    2,
                )
            ),
            min_samples_leaf=int(
                estimator_payload.get(
                    "min_samples_leaf",
                    1,
                )
            ),
            max_features=estimator_payload.get(
                "max_features",
                1.0,
            ),
            bootstrap=bool(
                estimator_payload.get(
                    "bootstrap",
                    True,
                )
            ),
            random_state=estimator_payload.get(
                "random_state",
                42,
            ),
            n_jobs=estimator_payload.get(
                "n_jobs",
                -1,
            ),
            estimator_parameters=payload.get(
                "estimator_parameters"
            ),
        )

        model._estimator = (
            RandomForestEstimator.deserialize(
                estimator_payload
            )
        )

        model._state = ForecastModelState(
            payload.get(
                "state",
                ForecastModelState.CREATED.value,
            )
        )

        return model

    def reset(self) -> None:
        """Reset model and estimator runtime state."""
        super().reset()
        self.estimator.reset()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_training_data(
        training_dataset: Any,
    ) -> tuple[Any, Sequence[Any]]:
        if isinstance(training_dataset, Mapping):
            if "features" not in training_dataset:
                raise ValueError(
                    "Random Forest training dataset must contain "
                    "a 'features' key."
                )

            if "target" not in training_dataset:
                raise ValueError(
                    "Random Forest training dataset must contain "
                    "a 'target' key."
                )

            return (
                training_dataset["features"],
                training_dataset["target"],
            )

        if (
            isinstance(training_dataset, tuple)
            and len(training_dataset) == 2
        ):
            return (
                training_dataset[0],
                training_dataset[1],
            )

        raise ValueError(
            "Random Forest training dataset must be a mapping with "
            "'features' and 'target' keys or a two-item tuple."
        )

    @staticmethod
    def _dataset_record_count(
        dataset: Any,
    ) -> int:
        if dataset is None:
            return 0

        if isinstance(dataset, Mapping):
            if "target" in dataset:
                return len(dataset["target"])

            if "features" in dataset:
                return len(dataset["features"])

        if (
            isinstance(dataset, tuple)
            and len(dataset) == 2
        ):
            return len(dataset[1])

        try:
            return len(dataset)
        except TypeError:
            return 0

    @staticmethod
    def _to_float_tuple(
        values: Any,
        *,
        argument_name: str,
    ) -> tuple[float, ...]:
        if values is None:
            raise ValueError(
                f"{argument_name} must not be None."
            )

        converted = (
            values.tolist()
            if hasattr(values, "tolist")
            else values
        )

        try:
            result = tuple(
                float(value)
                for value in converted
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{argument_name} must contain numeric values."
            ) from exc

        if not result:
            raise ValueError(
                f"{argument_name} must contain at least one value."
            )

        if any(
            not math.isfinite(value)
            for value in result
        ):
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
        errors = tuple(
            actual - predicted
            for actual, predicted in zip(
                actual_values,
                predicted_values,
                strict=True,
            )
        )

        absolute_errors = tuple(
            abs(error)
            for error in errors
        )

        squared_errors = tuple(
            error**2
            for error in errors
        )

        if metric_name == "MAE":
            return sum(absolute_errors) / len(absolute_errors)

        if metric_name == "MSE":
            return sum(squared_errors) / len(squared_errors)

        if metric_name == "RMSE":
            return math.sqrt(
                sum(squared_errors) / len(squared_errors)
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
                    "MAPE cannot be calculated when all actual "
                    "values are zero."
                )

            return sum(eligible) / len(eligible)

        if metric_name == "SMAPE":
            values = tuple(
                (
                    0.0
                    if abs(actual) + abs(predicted) == 0.0
                    else (
                        200.0
                        * abs(actual - predicted)
                        / (
                            abs(actual)
                            + abs(predicted)
                        )
                    )
                )
                for actual, predicted in zip(
                    actual_values,
                    predicted_values,
                    strict=True,
                )
            )

            return sum(values) / len(values)

        if metric_name == "WAPE":
            denominator = sum(
                abs(value)
                for value in actual_values
            )

            if denominator == 0.0:
                raise ValueError(
                    "WAPE cannot be calculated when total actual "
                    "volume is zero."
                )

            return (
                sum(absolute_errors)
                / denominator
                * 100.0
            )

        if metric_name == "R2":
            actual_mean = (
                sum(actual_values)
                / len(actual_values)
            )

            total_sum_of_squares = sum(
                (actual - actual_mean) ** 2
                for actual in actual_values
            )

            if total_sum_of_squares == 0.0:
                raise ValueError(
                    "R2 cannot be calculated when actual values "
                    "have zero variance."
                )

            return (
                1.0
                - (
                    sum(squared_errors)
                    / total_sum_of_squares
                )
            )

        raise ValueError(
            f"Unsupported evaluation metric: {metric_name}."
        )


__all__ = [
    "RandomForestForecastModel",
]