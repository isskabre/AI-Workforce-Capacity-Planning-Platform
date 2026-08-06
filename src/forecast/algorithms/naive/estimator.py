"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.naive.estimator

Description:
    Implements the Naive Last-Value forecasting estimator.

    The estimator learns the final observed target value from the training
    sequence and repeats that value for every requested future period. It
    provides the baseline against which all more advanced forecasting models
    are evaluated.

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


class NaiveLastValueEstimator(EnterpriseEstimator):
    """
    Enterprise estimator implementing a last-observation baseline.

    Training stores the final valid target value. Prediction repeats that
    value for the number of requested prediction records.

    This estimator is intentionally deterministic and contains no external
    machine-learning dependency.
    """

    ESTIMATOR_NAME = "naive_last_value_estimator"
    FRAMEWORK = "native_python"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            estimator_name=self.ESTIMATOR_NAME,
            framework=self.FRAMEWORK,
            version=self.VERSION,
            parameters=parameters,
        )

        self._last_value: float | None = None

    @property
    def last_value(self) -> float | None:
        """Return the final target value learned during fitting."""
        return self._last_value

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Fit the estimator using the final observed target value.

        Args:
            features:
                Training feature records. They are retained only for record
                count metadata because this baseline does not use predictors.
            target:
                Ordered target observations.

        Returns:
            This fitted estimator.

        Raises:
            ValueError:
                If the target is missing, empty, or its final value cannot be
                converted to a finite float.
        """
        target_values = self._to_sequence(
            target,
            argument_name="target",
        )

        if not target_values:
            raise ValueError(
                "Naive estimator requires at least one target value."
            )

        last_value = self._to_float(
            target_values[-1],
            argument_name="final target value",
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

        self._last_value = last_value

        self.mark_fitted(
            training_metadata={
                "training_records": len(target_values),
                "feature_records": feature_record_count,
                "learned_last_value": last_value,
            }
        )

        return self

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        """
        Repeat the learned value for every prediction record.

        Args:
            features:
                Prediction records or an integer prediction count.

        Returns:
            Ordered point forecasts.

        Raises:
            RuntimeError:
                If prediction is attempted before fitting.
            ValueError:
                If the requested prediction count is invalid.
        """
        if not self.fitted or self._last_value is None:
            raise RuntimeError(
                "Naive estimator must be fitted before prediction."
            )

        prediction_count = self._resolve_prediction_count(features)

        return tuple(
            self._last_value
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
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(self.training_metadata),
            "last_value": self.last_value,
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """
        Reconstruct an estimator from serialized state.

        Args:
            payload:
                Serialized estimator mapping.

        Returns:
            Reconstructed estimator.
        """
        estimator = cls(
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

        last_value = payload.get("last_value")

        estimator._last_value = (
            float(last_value)
            if last_value is not None
            else None
        )

        return estimator

    def save(
        self,
        destination: str | PathLike[str],
    ) -> None:
        """
        Persist estimator state as JSON.

        Args:
            destination:
                Local or mounted filesystem destination.
        """
        EnterpriseSerializer.save_json(
            self.serialize(),
            Path(destination),
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
    ) -> Self:
        """
        Load estimator state from JSON.

        Args:
            source:
                Local or mounted filesystem source.

        Returns:
            Restored estimator.
        """
        payload = EnterpriseSerializer.load_json(
            Path(source)
        )

        return cls.deserialize(payload)

    def reset(self) -> None:
        """Reset estimator state, including the learned target value."""
        super().reset()
        self._last_value = None

    @staticmethod
    def _safe_length(value: Any) -> int | None:
        """Return length when supported, otherwise ``None``."""
        try:
            return len(value)
        except TypeError:
            return None

    @staticmethod
    def _to_sequence(
        value: Any,
        *,
        argument_name: str,
    ) -> Sequence[Any]:
        """
        Convert common one-dimensional inputs into a sequence.

        Supports Python sequences and objects exposing ``tolist()``, including
        common NumPy and Pandas objects.
        """
        if value is None:
            raise ValueError(
                f"{argument_name} must not be None."
            )

        converted = (
            value.tolist()
            if hasattr(value, "tolist")
            else value
        )

        if isinstance(converted, (str, bytes)):
            raise ValueError(
                f"{argument_name} must be a numeric sequence."
            )

        if not isinstance(converted, Sequence):
            try:
                converted = tuple(converted)
            except TypeError as exc:
                raise ValueError(
                    f"{argument_name} must be iterable."
                ) from exc

        return converted

    @staticmethod
    def _to_float(
        value: Any,
        *,
        argument_name: str,
    ) -> float:
        """Convert a value to a finite float."""
        try:
            converted = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{argument_name} must be numeric."
            ) from exc

        if converted != converted:
            raise ValueError(
                f"{argument_name} must not be NaN."
            )

        if converted in (float("inf"), float("-inf")):
            raise ValueError(
                f"{argument_name} must be finite."
            )

        return converted

    @staticmethod
    def _resolve_prediction_count(features: Any) -> int:
        """Resolve the number of forecasts requested."""
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
    "NaiveLastValueEstimator",
]