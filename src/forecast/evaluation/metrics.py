"""
AI Workforce Capacity Planning Platform
Implementation 13 - Enterprise Evaluation Framework

Module:
    forecast.evaluation.metrics

Description:
    Provides the canonical, model-agnostic forecasting metric calculation
    engine used throughout evaluation, comparison, reporting, registry,
    monitoring, and API layers.

Architecture:
    Enterprise Evaluation Framework

Version:
    2.6.0
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

from forecast.modeling.metrics import ForecastMetrics


class EnterpriseForecastMetrics:
    """
    Stateless calculation engine for standardized forecasting metrics.

    The engine accepts one-dimensional numeric sequences, validates and
    normalizes them to NumPy float64 arrays, and returns the immutable
    ``ForecastMetrics`` domain contract.
    """

    # ------------------------------------------------------------------
    # Aggregate evaluation
    # ------------------------------------------------------------------

    @classmethod
    def evaluate(
        cls,
        *,
        actual: Sequence[float] | np.ndarray,
        predicted: Sequence[float] | np.ndarray,
    ) -> ForecastMetrics:
        """
        Calculate the complete standardized forecast metric collection.

        Args:
            actual:
                Observed target values.

            predicted:
                Forecast values aligned with ``actual``.

        Returns:
            Immutable ``ForecastMetrics`` value object.

        Raises:
            TypeError:
                If inputs cannot be converted to numeric arrays.

            ValueError:
                If inputs are empty, multidimensional, misaligned, or contain
                non-finite values.
        """
        actual_array, predicted_array = cls.validate_inputs(
            actual=actual,
            predicted=predicted,
        )

        mse_value = cls.mse(
            actual_array,
            predicted_array,
        )

        return ForecastMetrics(
            mae=cls.mae(
                actual_array,
                predicted_array,
            ),
            mse=mse_value,
            rmse=math.sqrt(mse_value),
            bias=cls.bias(
                actual_array,
                predicted_array,
            ),
            mape=cls.mape(
                actual_array,
                predicted_array,
            ),
            smape=cls.smape(
                actual_array,
                predicted_array,
            ),
            wape=cls.wape(
                actual_array,
                predicted_array,
            ),
        )

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    @classmethod
    def validate_inputs(
        cls,
        actual: Sequence[float] | np.ndarray,
        predicted: Sequence[float] | np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Validate and normalize forecast evaluation inputs.

        Returns:
            Tuple containing aligned one-dimensional float64 arrays.
        """
        actual_array = cls._to_numpy(
            values=actual,
            argument_name="actual",
        )

        predicted_array = cls._to_numpy(
            values=predicted,
            argument_name="predicted",
        )

        if actual_array.size == 0:
            raise ValueError(
                "actual cannot be empty."
            )

        if predicted_array.size == 0:
            raise ValueError(
                "predicted cannot be empty."
            )

        if actual_array.size != predicted_array.size:
            raise ValueError(
                "actual and predicted must have identical lengths."
            )

        if not np.isfinite(actual_array).all():
            raise ValueError(
                "actual contains non-finite values."
            )

        if not np.isfinite(predicted_array).all():
            raise ValueError(
                "predicted contains non-finite values."
            )

        return actual_array, predicted_array

    @staticmethod
    def _to_numpy(
        *,
        values: Sequence[float] | np.ndarray,
        argument_name: str,
    ) -> np.ndarray:
        """Convert one numeric input collection to a float64 NumPy array."""
        if values is None:
            raise TypeError(
                f"{argument_name} cannot be None."
            )

        if isinstance(values, (str, bytes)):
            raise TypeError(
                f"{argument_name} must be a numeric sequence."
            )

        try:
            array = np.asarray(
                values,
                dtype=np.float64,
            )

        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{argument_name} must contain numeric values."
            ) from exc

        if array.ndim != 1:
            raise ValueError(
                f"{argument_name} must be one-dimensional."
            )

        return array

    # ------------------------------------------------------------------
    # Individual metrics
    # ------------------------------------------------------------------

    @staticmethod
    def mae(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """Return mean absolute error."""
        return float(
            np.mean(
                np.abs(actual - predicted)
            )
        )

    @staticmethod
    def mse(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """Return mean squared error."""
        return float(
            np.mean(
                np.square(actual - predicted)
            )
        )

    @classmethod
    def rmse(
        cls,
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """Return root mean squared error."""
        return math.sqrt(
            cls.mse(
                actual,
                predicted,
            )
        )

    @staticmethod
    def bias(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Return mean prediction error.

        Positive values indicate overprediction. Negative values indicate
        underprediction.
        """
        return float(
            np.mean(
                predicted - actual
            )
        )

    @staticmethod
    def mape(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Return mean absolute percentage error.

        Records with zero actual values are excluded from the denominator.
        When all actual values are zero, ``0.0`` is returned.
        """
        valid_mask = actual != 0.0

        if not np.any(valid_mask):
            return 0.0

        return float(
            np.mean(
                np.abs(
                    (
                        actual[valid_mask]
                        - predicted[valid_mask]
                    )
                    / actual[valid_mask]
                )
            )
            * 100.0
        )

    @staticmethod
    def smape(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Return symmetric mean absolute percentage error.

        Records where both actual and predicted values equal zero are excluded.
        """
        denominator = (
            np.abs(actual)
            + np.abs(predicted)
        )

        valid_mask = denominator != 0.0

        if not np.any(valid_mask):
            return 0.0

        return float(
            np.mean(
                200.0
                * np.abs(
                    actual[valid_mask]
                    - predicted[valid_mask]
                )
                / denominator[valid_mask]
            )
        )

    @staticmethod
    def wape(
        actual: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Return weighted absolute percentage error.

        When the sum of absolute actual values equals zero, ``0.0`` is
        returned.
        """
        denominator = float(
            np.sum(
                np.abs(actual)
            )
        )

        if denominator == 0.0:
            return 0.0

        numerator = float(
            np.sum(
                np.abs(actual - predicted)
            )
        )

        return (
            numerator
            / denominator
            * 100.0
        )


__all__ = [
    "EnterpriseForecastMetrics",
]