"""
AI Workforce Capacity Planning Platform
Implementation 15 - Enterprise Inference Framework

Module:
    forecast.inference.predictor

Description:
    Defines the model-agnostic enterprise forecast predictor responsible for
    validating inference requests, executing predictions through the
    BaseForecastModel contract, and validating standardized
    ForecastPredictionResult outputs.

Architecture:
    Enterprise Inference Framework

Version:
    2.7.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from src.forecast.modeling.contexts import (
    ForecastPredictionContext,
)
from src.forecast.modeling.contracts import (
    BaseForecastModel,
)
from src.forecast.modeling.exceptions import (
    ForecastInferenceError,
    ForecastPredictionError,
)
from src.forecast.modeling.results import (
    ForecastPredictionResult,
)


class EnterpriseForecastPredictor:
    """
    Stateless service for executing one enterprise forecast prediction.

    The predictor depends only on the ``BaseForecastModel`` abstraction.
    It does not know which statistical, machine-learning, deep-learning,
    baseline, or ensemble algorithm provides the prediction implementation.

    Responsibilities:
        - validate the forecasting model;
        - validate the prediction context;
        - confirm that the model is ready for inference;
        - delegate execution to ``BaseForecastModel.predict``;
        - validate the standardized prediction result;
        - translate execution failures into enterprise inference errors.

    The predictor intentionally does not:
        - train or initialize models;
        - load persisted artifacts;
        - resolve model registry entries;
        - calculate evaluation metrics;
        - compare models;
        - persist prediction outputs.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(
        self,
        *,
        model: BaseForecastModel,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        """
        Execute one forecast prediction request.

        Args:
            model:
                Initialized and trained enterprise forecasting model.

            context:
                Immutable prediction context containing the inference dataset,
                forecast horizon, execution timestamp, optional model version,
                and metadata.

        Returns:
            Validated ``ForecastPredictionResult`` returned by the model.

        Raises:
            ForecastInferenceError:
                If request validation fails, the model is not ready, model
                prediction fails, or the returned result violates the
                enterprise prediction contract.
        """
        self._validate_model(model)
        self._validate_context(
            context=context,
            model=model,
        )

        try:
            result = model.predict(context)

        except ForecastInferenceError:
            raise

        except ForecastPredictionError as exc:
            raise ForecastInferenceError(
                "Forecast model prediction execution failed.",
                context={
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "forecast_horizon": context.forecast_horizon,
                },
                cause=exc,
            ) from exc

        except Exception as exc:
            raise ForecastInferenceError(
                "Enterprise forecast inference failed.",
                context={
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "forecast_horizon": context.forecast_horizon,
                    "exception_type": type(exc).__name__,
                },
                cause=exc,
            ) from exc

        self._validate_prediction_result(
            result=result,
            model=model,
            context=context,
        )

        return result

    # ------------------------------------------------------------------
    # Model validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_model(
        model: BaseForecastModel,
    ) -> None:
        """
        Validate that the supplied model satisfies inference requirements.
        """
        if model is None:
            raise ForecastInferenceError(
                "Forecast model cannot be None.",
                context={
                    "argument": "model",
                },
            )

        if not isinstance(model, BaseForecastModel):
            raise ForecastInferenceError(
                "model must be a BaseForecastModel.",
                context={
                    "argument": "model",
                    "received_type": type(model).__name__,
                },
            )

        EnterpriseForecastPredictor._validate_required_string(
            value=model.model_name,
            field_name="model.model_name",
        )

        EnterpriseForecastPredictor._validate_required_string(
            value=model.model_version,
            field_name="model.model_version",
        )

        if not model.is_initialized:
            raise ForecastInferenceError(
                "Forecast model must be initialized before inference.",
                context={
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "model_state": model.state.value,
                },
            )

        if not model.is_trained:
            raise ForecastInferenceError(
                "Forecast model must be trained before inference.",
                context={
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "model_state": model.state.value,
                },
            )

    # ------------------------------------------------------------------
    # Context validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_context(
        *,
        context: ForecastPredictionContext,
        model: BaseForecastModel,
    ) -> None:
        """
        Validate the immutable prediction context.
        """
        if context is None:
            raise ForecastInferenceError(
                "Forecast prediction context cannot be None.",
                context={
                    "argument": "context",
                },
            )

        if not isinstance(
            context,
            ForecastPredictionContext,
        ):
            raise ForecastInferenceError(
                "context must be a ForecastPredictionContext.",
                context={
                    "argument": "context",
                    "received_type": type(context).__name__,
                },
            )

        if context.prediction_dataset is None:
            raise ForecastInferenceError(
                "Prediction dataset cannot be None.",
                context={
                    "argument": "context.prediction_dataset",
                    "model_name": model.model_name,
                },
            )

        if (
            isinstance(context.forecast_horizon, bool)
            or not isinstance(context.forecast_horizon, int)
        ):
            raise ForecastInferenceError(
                "Prediction forecast_horizon must be an integer.",
                context={
                    "argument": "context.forecast_horizon",
                    "received_type": type(
                        context.forecast_horizon
                    ).__name__,
                },
            )

        if context.forecast_horizon <= 0:
            raise ForecastInferenceError(
                "Prediction forecast_horizon must be greater than zero.",
                context={
                    "argument": "context.forecast_horizon",
                    "forecast_horizon": context.forecast_horizon,
                },
            )

        EnterpriseForecastPredictor._validate_timezone_aware_datetime(
            value=context.prediction_timestamp,
            field_name="context.prediction_timestamp",
        )

        if context.model_version is not None:
            EnterpriseForecastPredictor._validate_required_string(
                value=context.model_version,
                field_name="context.model_version",
            )

            if (
                context.model_version.strip()
                != model.model_version.strip()
            ):
                raise ForecastInferenceError(
                    "Prediction context model_version does not match the "
                    "supplied forecasting model.",
                    context={
                        "context_model_version": context.model_version,
                        "actual_model_version": model.model_version,
                        "model_name": model.model_name,
                    },
                )

        if not isinstance(context.metadata, Mapping):
            raise ForecastInferenceError(
                "Prediction context metadata must be a mapping.",
                context={
                    "argument": "context.metadata",
                    "received_type": type(
                        context.metadata
                    ).__name__,
                },
            )

    # ------------------------------------------------------------------
    # Result validation
    # ------------------------------------------------------------------

    @classmethod
    def _validate_prediction_result(
        cls,
        *,
        result: Any,
        model: BaseForecastModel,
        context: ForecastPredictionContext,
    ) -> None:
        """
        Validate the standardized prediction result returned by the model.
        """
        if not isinstance(result, ForecastPredictionResult):
            raise ForecastInferenceError(
                "Forecast model returned an incompatible prediction result.",
                context={
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "received_type": type(result).__name__,
                    "expected_type": (
                        ForecastPredictionResult.__name__
                    ),
                },
            )

        if not result.succeeded:
            raise ForecastInferenceError(
                "Forecast model returned an unsuccessful prediction result.",
                context={
                    "model_name": result.model_name,
                    "model_version": result.model_version,
                    "status": result.status.value,
                    "error": (
                        dict(result.error)
                        if result.error is not None
                        else None
                    ),
                },
            )

        cls._validate_required_string(
            value=result.model_name,
            field_name="result.model_name",
        )

        cls._validate_required_string(
            value=result.model_version,
            field_name="result.model_version",
        )

        if (
            result.model_name.strip()
            != model.model_name.strip()
        ):
            raise ForecastInferenceError(
                "Prediction result model_name does not match the forecasting "
                "model.",
                context={
                    "expected_model_name": model.model_name,
                    "returned_model_name": result.model_name,
                },
            )

        if (
            result.model_version.strip()
            != model.model_version.strip()
        ):
            raise ForecastInferenceError(
                "Prediction result model_version does not match the "
                "forecasting model.",
                context={
                    "model_name": model.model_name,
                    "expected_model_version": model.model_version,
                    "returned_model_version": result.model_version,
                },
            )

        if (
            isinstance(result.forecast_horizon, bool)
            or not isinstance(result.forecast_horizon, int)
        ):
            raise ForecastInferenceError(
                "Prediction result forecast_horizon must be an integer.",
                context={
                    "model_name": model.model_name,
                    "received_type": type(
                        result.forecast_horizon
                    ).__name__,
                },
            )

        if result.forecast_horizon <= 0:
            raise ForecastInferenceError(
                "Prediction result forecast_horizon must be greater than zero.",
                context={
                    "model_name": model.model_name,
                    "forecast_horizon": result.forecast_horizon,
                },
            )

        if (
            result.forecast_horizon
            != context.forecast_horizon
        ):
            raise ForecastInferenceError(
                "Prediction result forecast_horizon does not match the "
                "prediction context.",
                context={
                    "model_name": model.model_name,
                    "context_forecast_horizon": (
                        context.forecast_horizon
                    ),
                    "result_forecast_horizon": (
                        result.forecast_horizon
                    ),
                },
            )

        predictions = cls._validate_numeric_sequence(
            values=result.predictions,
            field_name="result.predictions",
            allow_empty=False,
        )

        if len(predictions) != result.forecast_horizon:
            raise ForecastInferenceError(
                "Prediction count does not match forecast_horizon.",
                context={
                    "model_name": model.model_name,
                    "prediction_count": len(predictions),
                    "forecast_horizon": result.forecast_horizon,
                },
            )

        timestamps = cls._validate_prediction_timestamps(
            timestamps=result.prediction_timestamps,
        )

        if timestamps and len(timestamps) != len(predictions):
            raise ForecastInferenceError(
                "Prediction timestamp count must match prediction count.",
                context={
                    "model_name": model.model_name,
                    "prediction_count": len(predictions),
                    "timestamp_count": len(timestamps),
                },
            )

        lower_bounds = cls._validate_optional_numeric_sequence(
            values=result.lower_bounds,
            field_name="result.lower_bounds",
            expected_length=len(predictions),
        )

        upper_bounds = cls._validate_optional_numeric_sequence(
            values=result.upper_bounds,
            field_name="result.upper_bounds",
            expected_length=len(predictions),
        )

        if (lower_bounds is None) != (upper_bounds is None):
            raise ForecastInferenceError(
                "Prediction lower_bounds and upper_bounds must either both "
                "be provided or both be omitted.",
                context={
                    "model_name": model.model_name,
                    "lower_bounds_provided": (
                        lower_bounds is not None
                    ),
                    "upper_bounds_provided": (
                        upper_bounds is not None
                    ),
                },
            )

        if lower_bounds is not None and upper_bounds is not None:
            cls._validate_prediction_intervals(
                predictions=predictions,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                model_name=model.model_name,
            )

        if result.inference_duration_seconds is not None:
            cls._validate_non_negative_finite_number(
                value=result.inference_duration_seconds,
                field_name=(
                    "result.inference_duration_seconds"
                ),
            )

        if result.artifact_id is not None:
            cls._validate_required_string(
                value=result.artifact_id,
                field_name="result.artifact_id",
            )

        cls._validate_required_string(
            value=result.result_id,
            field_name="result.result_id",
        )

        cls._validate_timezone_aware_datetime(
            value=result.generated_at,
            field_name="result.generated_at",
        )

        if not isinstance(result.metadata, Mapping):
            raise ForecastInferenceError(
                "Prediction result metadata must be a mapping.",
                context={
                    "model_name": model.model_name,
                    "received_type": type(
                        result.metadata
                    ).__name__,
                },
            )

        if not isinstance(result.warnings, tuple):
            raise ForecastInferenceError(
                "Prediction result warnings must be stored as a tuple.",
                context={
                    "model_name": model.model_name,
                    "received_type": type(
                        result.warnings
                    ).__name__,
                },
            )

        for index, warning in enumerate(result.warnings):
            if not isinstance(warning, str):
                raise ForecastInferenceError(
                    "Every prediction warning must be a string.",
                    context={
                        "model_name": model.model_name,
                        "warning_index": index,
                        "received_type": type(
                            warning
                        ).__name__,
                    },
                )

        if result.error is not None and not isinstance(
            result.error,
            Mapping,
        ):
            raise ForecastInferenceError(
                "Prediction result error details must be a mapping.",
                context={
                    "model_name": model.model_name,
                    "received_type": type(
                        result.error
                    ).__name__,
                },
            )

    # ------------------------------------------------------------------
    # Prediction sequence validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_numeric_sequence(
        *,
        values: Sequence[float],
        field_name: str,
        allow_empty: bool,
    ) -> tuple[float, ...]:
        """
        Validate and normalize one prediction-related numeric sequence.
        """
        if values is None:
            raise ForecastInferenceError(
                f"{field_name} cannot be None."
            )

        if isinstance(values, (str, bytes)):
            raise ForecastInferenceError(
                f"{field_name} must be a numeric sequence."
            )

        try:
            materialized_values = tuple(values)
        except TypeError as exc:
            raise ForecastInferenceError(
                f"{field_name} must be iterable.",
                cause=exc,
            ) from exc

        if not materialized_values and not allow_empty:
            raise ForecastInferenceError(
                f"{field_name} cannot be empty."
            )

        normalized_values: list[float] = []

        for index, value in enumerate(materialized_values):
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise ForecastInferenceError(
                    f"{field_name} must contain numeric values.",
                    context={
                        "index": index,
                        "received_type": type(value).__name__,
                    },
                )

            normalized_value = float(value)

            if not math.isfinite(normalized_value):
                raise ForecastInferenceError(
                    f"{field_name} must contain only finite values.",
                    context={
                        "index": index,
                        "value": repr(value),
                    },
                )

            normalized_values.append(normalized_value)

        return tuple(normalized_values)

    @classmethod
    def _validate_optional_numeric_sequence(
        cls,
        *,
        values: Sequence[float] | None,
        field_name: str,
        expected_length: int,
    ) -> tuple[float, ...] | None:
        """
        Validate an optional prediction interval sequence.
        """
        if values is None:
            return None

        normalized_values = cls._validate_numeric_sequence(
            values=values,
            field_name=field_name,
            allow_empty=False,
        )

        if len(normalized_values) != expected_length:
            raise ForecastInferenceError(
                f"{field_name} length must match prediction count.",
                context={
                    "expected_length": expected_length,
                    "actual_length": len(normalized_values),
                },
            )

        return normalized_values

    @classmethod
    def _validate_prediction_timestamps(
        cls,
        *,
        timestamps: Sequence[datetime],
    ) -> tuple[datetime, ...]:
        """
        Validate optional prediction timestamps.
        """
        if timestamps is None:
            raise ForecastInferenceError(
                "result.prediction_timestamps cannot be None."
            )

        if isinstance(timestamps, (str, bytes)):
            raise ForecastInferenceError(
                "result.prediction_timestamps must be a datetime sequence."
            )

        try:
            materialized_timestamps = tuple(timestamps)
        except TypeError as exc:
            raise ForecastInferenceError(
                "result.prediction_timestamps must be iterable.",
                cause=exc,
            ) from exc

        for index, timestamp in enumerate(
            materialized_timestamps
        ):
            cls._validate_timezone_aware_datetime(
                value=timestamp,
                field_name=(
                    "result.prediction_timestamps"
                    f"[{index}]"
                ),
            )

        return materialized_timestamps

    @staticmethod
    def _validate_prediction_intervals(
        *,
        predictions: tuple[float, ...],
        lower_bounds: tuple[float, ...],
        upper_bounds: tuple[float, ...],
        model_name: str,
    ) -> None:
        """
        Validate prediction interval ordering and point containment.
        """
        for index, (
            prediction,
            lower_bound,
            upper_bound,
        ) in enumerate(
            zip(
                predictions,
                lower_bounds,
                upper_bounds,
                strict=True,
            )
        ):
            if lower_bound > upper_bound:
                raise ForecastInferenceError(
                    "Prediction lower bound cannot exceed upper bound.",
                    context={
                        "model_name": model_name,
                        "index": index,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                    },
                )

            if not lower_bound <= prediction <= upper_bound:
                raise ForecastInferenceError(
                    "Point prediction must fall within its prediction "
                    "interval.",
                    context={
                        "model_name": model_name,
                        "index": index,
                        "lower_bound": lower_bound,
                        "prediction": prediction,
                        "upper_bound": upper_bound,
                    },
                )

    # ------------------------------------------------------------------
    # Generic validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_required_string(
        *,
        value: Any,
        field_name: str,
    ) -> None:
        """
        Validate one required non-empty string.
        """
        if not isinstance(value, str):
            raise ForecastInferenceError(
                f"{field_name} must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        if not value.strip():
            raise ForecastInferenceError(
                f"{field_name} must not be empty."
            )

    @staticmethod
    def _validate_timezone_aware_datetime(
        *,
        value: Any,
        field_name: str,
    ) -> None:
        """
        Validate one timezone-aware datetime.
        """
        if not isinstance(value, datetime):
            raise ForecastInferenceError(
                f"{field_name} must be a datetime.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ForecastInferenceError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _validate_non_negative_finite_number(
        *,
        value: Any,
        field_name: str,
    ) -> None:
        """
        Validate one non-negative finite numeric value.
        """
        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ForecastInferenceError(
                f"{field_name} must be numeric.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized_value = float(value)

        if not math.isfinite(normalized_value):
            raise ForecastInferenceError(
                f"{field_name} must be finite."
            )

        if normalized_value < 0.0:
            raise ForecastInferenceError(
                f"{field_name} cannot be negative."
            )


__all__ = [
    "EnterpriseForecastPredictor",
]