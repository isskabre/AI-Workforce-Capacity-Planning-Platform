"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.moving_average.estimator

Description:
    Implements the enterprise Moving Average forecasting estimator.

    The estimator learns the arithmetic mean of the most recent target
    observations defined by a configurable window size and repeats that
    value for each requested future period.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path
from typing import Any, Self

from src.forecast.algorithms.base.estimator import EnterpriseEstimator
from src.forecast.algorithms.base.serializer import EnterpriseSerializer


class MovingAverageEstimator(EnterpriseEstimator):
    """
    Enterprise estimator implementing a simple moving-average src.forecast.

    During fitting, the estimator retains the most recent ``window_size``
    target observations. Prediction repeats their arithmetic mean for the
    requested number of future records.
    """

    ESTIMATOR_NAME = "moving_average_estimator"
    FRAMEWORK = "native_python"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        window_size: int = 3,
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        if isinstance(window_size, bool) or not isinstance(
            window_size,
            int,
        ):
            raise ValueError(
                "window_size must be a positive integer."
            )

        if window_size <= 0:
            raise ValueError(
                "window_size must be greater than zero."
            )

        resolved_parameters = {
            **dict(parameters or {}),
            "window_size": window_size,
        }

        super().__init__(
            estimator_name=self.ESTIMATOR_NAME,
            framework=self.FRAMEWORK,
            version=self.VERSION,
            parameters=resolved_parameters,
        )

        self._window_size = window_size
        self._history: tuple[float, ...] = ()

    @property
    def window_size(self) -> int:
        """Return the number of recent observations used."""
        return self._window_size

    @property
    def history(self) -> tuple[float, ...]:
        """Return the retained moving-average window."""
        return self._history

    @property
    def moving_average(self) -> float | None:
        """Return the learned moving average when fitted."""
        if not self._history:
            return None

        return sum(self._history) / len(self._history)

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Fit the estimator using the most recent target observations.

        Args:
            features:
                Training feature records. The moving-average algorithm does
                not use their values, but their record count is validated.
            target:
                Ordered target observations.

        Returns:
            This fitted estimator.

        Raises:
            ValueError:
                If target data is invalid, insufficient, or does not match
                the feature-record count.
        """
        target_values = self._to_float_tuple(
            target,
            argument_name="target",
        )

        if len(target_values) < self.window_size:
            raise ValueError(
                "Training history is shorter than window_size. "
                f"Received {len(target_values)} observations for a "
                f"window_size of {self.window_size}."
            )

        feature_record_count = self._safe_length(features)

        if (
            feature_record_count is not None
            and feature_record_count != len(target_values)
        ):
            raise ValueError(
                "Feature and target record counts must match. "
                f"Received {feature_record_count} feature records and "
                f"{len(target_values)} target records."
            )

        self._history = target_values[-self.window_size :]

        self.mark_fitted(
            training_metadata={
                "training_records": len(target_values),
                "feature_records": feature_record_count,
                "window_size": self.window_size,
                "retained_observations": len(self._history),
                "learned_moving_average": self.moving_average,
            }
        )

        return self

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        """
        Repeat the learned moving average for each prediction record.

        Args:
            features:
                Prediction records or a positive integer prediction count.

        Returns:
            Ordered point forecasts.

        Raises:
            RuntimeError:
                If prediction is attempted before fitting.
            ValueError:
                If the prediction count is invalid.
        """
        if not self.fitted or self.moving_average is None:
            raise RuntimeError(
                "Moving Average estimator must be fitted before prediction."
            )

        prediction_count = self._resolve_prediction_count(
            features
        )
        forecast_value = self.moving_average

        return tuple(
            forecast_value
            for _ in range(prediction_count)
        )

    def serialize(self) -> Mapping[str, Any]:
        """Return serialization-safe estimator state."""
        return {
            "schema_version": "1.0",
            "estimator_name": self.estimator_name,
            "framework": self.framework,
            "version": self.version,
            "parameters": dict(self.parameters),
            "window_size": self.window_size,
            "history": list(self.history),
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(self.training_metadata),
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct an estimator from serialized state."""
        window_size = int(
            payload.get(
                "window_size",
                payload.get("parameters", {}).get(
                    "window_size",
                    3,
                ),
            )
        )

        estimator = cls(
            window_size=window_size,
            parameters=payload.get("parameters"),
        )

        estimator._initialized = bool(
            payload.get("initialized", False)
        )
        estimator._fitted = bool(
            payload.get("fitted", False)
        )
        estimator._feature_names = tuple(
            payload.get("feature_names", ())
        )
        estimator._target_name = payload.get("target_name")
        estimator._training_metadata = dict(
            payload.get("training_metadata", {})
        )
        estimator._history = tuple(
            float(value)
            for value in payload.get("history", ())
        )

        if estimator._fitted and not estimator._history:
            raise ValueError(
                "A fitted Moving Average estimator must contain history."
            )

        return estimator

    def save(
        self,
        destination: str | PathLike[str],
    ) -> None:
        """Persist estimator state as JSON."""
        EnterpriseSerializer.save_json(
            self.serialize(),
            Path(destination),
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
    ) -> Self:
        """Load estimator state from JSON."""
        payload = EnterpriseSerializer.load_json(
            Path(source)
        )

        return cls.deserialize(payload)

    def reset(self) -> None:
        """Reset runtime state and retained observations."""
        super().reset()
        self._history = ()

    @staticmethod
    def _safe_length(value: Any) -> int | None:
        """Return input length when available."""
        try:
            return len(value)
        except TypeError:
            return None

    @staticmethod
    def _to_float_tuple(
        values: Any,
        *,
        argument_name: str,
    ) -> tuple[float, ...]:
        """Convert iterable input to finite float values."""
        if values is None:
            raise ValueError(
                f"{argument_name} must not be None."
            )

        converted = (
            values.tolist()
            if hasattr(values, "tolist")
            else values
        )

        if isinstance(converted, (str, bytes)):
            raise ValueError(
                f"{argument_name} must be a numeric sequence."
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

        for value in result:
            if value != value:
                raise ValueError(
                    f"{argument_name} must not contain NaN."
                )

            if value in (
                float("inf"),
                float("-inf"),
            ):
                raise ValueError(
                    f"{argument_name} must contain finite values."
                )

        return result

    @staticmethod
    def _resolve_prediction_count(
        features: Any,
    ) -> int:
        """Resolve the number of requested forecasts."""
        if isinstance(features, bool):
            raise ValueError(
                "Prediction count must be a positive integer."
            )

        if isinstance(features, int):
            prediction_count = features
        else:
            try:
                prediction_count = len(features)
            except TypeError as exc:
                raise ValueError(
                    "Prediction features must have a length or be supplied "
                    "as a positive integer count."
                ) from exc

        if prediction_count <= 0:
            raise ValueError(
                "Prediction count must be greater than zero."
            )

        return prediction_count


__all__ = [
    "MovingAverageEstimator",
]