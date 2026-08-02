"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.algorithms.linear_regression.estimator

Description:
    Implements a framework-independent multivariate linear-regression
    forecasting estimator.

    The estimator uses NumPy least-squares optimization to learn an intercept
    and one coefficient per input feature. It exposes the standardized
    EnterpriseEstimator lifecycle, metadata, serialization, persistence,
    validation, and reset contracts.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path
from typing import Any, Self

import numpy as np

from forecast.algorithms.base.estimator import EnterpriseEstimator
from forecast.algorithms.base.serializer import EnterpriseSerializer


class LinearRegressionEstimator(EnterpriseEstimator):
    """
    Enterprise ordinary least-squares linear-regression estimator.

    The fitted relationship is:

        prediction = intercept + Σ(coefficient_i × feature_i)

    An intercept column is included by default.
    """

    ESTIMATOR_NAME = "linear_regression_estimator"
    FRAMEWORK = "numpy"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        fit_intercept: bool = True,
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(fit_intercept, bool):
            raise ValueError(
                "fit_intercept must be a boolean."
            )

        resolved_parameters = {
            **dict(parameters or {}),
            "fit_intercept": fit_intercept,
        }

        super().__init__(
            estimator_name=self.ESTIMATOR_NAME,
            framework=self.FRAMEWORK,
            version=self.VERSION,
            parameters=resolved_parameters,
        )

        self._fit_intercept = fit_intercept
        self._intercept = 0.0
        self._coefficients: tuple[float, ...] = ()
        self._rank: int | None = None
        self._residual_sum_of_squares: float | None = None

    # ------------------------------------------------------------------
    # Learned state
    # ------------------------------------------------------------------

    @property
    def fit_intercept(self) -> bool:
        """Return whether the model includes an intercept."""
        return self._fit_intercept

    @property
    def intercept(self) -> float:
        """Return the learned intercept."""
        return self._intercept

    @property
    def coefficients(self) -> tuple[float, ...]:
        """Return learned feature coefficients in input-column order."""
        return self._coefficients

    @property
    def rank(self) -> int | None:
        """Return the rank of the fitted design matrix."""
        return self._rank

    @property
    def residual_sum_of_squares(self) -> float | None:
        """Return the training residual sum of squares when available."""
        return self._residual_sum_of_squares

    # ------------------------------------------------------------------
    # Training and prediction
    # ------------------------------------------------------------------

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Fit ordinary least squares using NumPy.

        Args:
            features:
                Two-dimensional numeric feature matrix.
            target:
                One-dimensional numeric target vector.

        Returns:
            This fitted estimator.

        Raises:
            ValueError:
                If inputs are empty, nonnumeric, nonfinite, incompatible,
                or structurally invalid.
        """
        feature_matrix = self._to_feature_matrix(
            features
        )
        target_vector = self._to_target_vector(
            target
        )

        record_count, feature_count = (
            feature_matrix.shape
        )

        if record_count != target_vector.shape[0]:
            raise ValueError(
                "Feature and target record counts must match. "
                f"Received {record_count} feature records and "
                f"{target_vector.shape[0]} target records."
            )

        if record_count < 2:
            raise ValueError(
                "Linear Regression requires at least two training records."
            )

        design_matrix = feature_matrix

        if self.fit_intercept:
            design_matrix = np.column_stack(
                (
                    np.ones(record_count),
                    feature_matrix,
                )
            )

        solution, residuals, rank, _ = np.linalg.lstsq(
            design_matrix,
            target_vector,
            rcond=None,
        )

        if self.fit_intercept:
            self._intercept = float(solution[0])
            coefficient_values = solution[1:]
        else:
            self._intercept = 0.0
            coefficient_values = solution

        self._coefficients = tuple(
            float(value)
            for value in coefficient_values
        )

        self._rank = int(rank)

        if residuals.size:
            self._residual_sum_of_squares = float(
                residuals[0]
            )
        else:
            fitted_values = (
                design_matrix @ solution
            )
            residual_vector = (
                target_vector - fitted_values
            )
            self._residual_sum_of_squares = float(
                residual_vector @ residual_vector
            )

        self.mark_fitted(
            training_metadata={
                "training_records": record_count,
                "feature_count": feature_count,
                "fit_intercept": self.fit_intercept,
                "rank": self.rank,
                "residual_sum_of_squares": (
                    self.residual_sum_of_squares
                ),
            }
        )

        return self

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        """
        Generate predictions from a fitted regression estimator.
        """
        if not self.fitted:
            raise RuntimeError(
                "Linear Regression estimator must be fitted "
                "before prediction."
            )

        feature_matrix = self._to_feature_matrix(
            features
        )

        if (
            feature_matrix.shape[1]
            != len(self.coefficients)
        ):
            raise ValueError(
                "Prediction feature count does not match the fitted "
                "coefficient count. "
                f"Received {feature_matrix.shape[1]} features; "
                f"expected {len(self.coefficients)}."
            )

        coefficient_vector = np.asarray(
            self.coefficients,
            dtype=float,
        )

        predictions = (
            feature_matrix @ coefficient_vector
            + self.intercept
        )

        return tuple(
            float(value)
            for value in predictions
        )

    # ------------------------------------------------------------------
    # Serialization and persistence
    # ------------------------------------------------------------------

    def serialize(self) -> Mapping[str, Any]:
        """Return serialization-safe estimator state."""
        return {
            "schema_version": "1.0",
            "estimator_name": self.estimator_name,
            "framework": self.framework,
            "version": self.version,
            "parameters": dict(self.parameters),
            "fit_intercept": self.fit_intercept,
            "intercept": self.intercept,
            "coefficients": list(self.coefficients),
            "rank": self.rank,
            "residual_sum_of_squares": (
                self.residual_sum_of_squares
            ),
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(
                self.training_metadata
            ),
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct an estimator from serialized state."""
        estimator = cls(
            fit_intercept=bool(
                payload.get("fit_intercept", True)
            ),
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
        estimator._target_name = payload.get(
            "target_name"
        )
        estimator._training_metadata = dict(
            payload.get("training_metadata", {})
        )

        estimator._intercept = float(
            payload.get("intercept", 0.0)
        )
        estimator._coefficients = tuple(
            float(value)
            for value in payload.get(
                "coefficients",
                (),
            )
        )

        rank = payload.get("rank")
        estimator._rank = (
            int(rank)
            if rank is not None
            else None
        )

        residual_sum = payload.get(
            "residual_sum_of_squares"
        )
        estimator._residual_sum_of_squares = (
            float(residual_sum)
            if residual_sum is not None
            else None
        )

        if (
            estimator._fitted
            and not estimator._coefficients
        ):
            raise ValueError(
                "A fitted Linear Regression estimator must "
                "contain coefficients."
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

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset runtime state and all learned parameters."""
        super().reset()

        self._intercept = 0.0
        self._coefficients = ()
        self._rank = None
        self._residual_sum_of_squares = None

    # ------------------------------------------------------------------
    # Internal validation
    # ------------------------------------------------------------------

    @staticmethod
    def _to_feature_matrix(
        features: Any,
    ) -> np.ndarray:
        """Convert input features into a finite 2-D float matrix."""
        if features is None:
            raise ValueError(
                "features must not be None."
            )

        try:
            matrix = np.asarray(
                features,
                dtype=float,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "features must contain numeric values."
            ) from exc

        if matrix.ndim == 1:
            matrix = matrix.reshape(-1, 1)

        if matrix.ndim != 2:
            raise ValueError(
                "features must be a two-dimensional matrix."
            )

        if matrix.shape[0] == 0:
            raise ValueError(
                "features must contain at least one record."
            )

        if matrix.shape[1] == 0:
            raise ValueError(
                "features must contain at least one column."
            )

        if not np.isfinite(matrix).all():
            raise ValueError(
                "features must contain only finite values."
            )

        return matrix

    @staticmethod
    def _to_target_vector(
        target: Any,
    ) -> np.ndarray:
        """Convert target input into a finite 1-D float vector."""
        if target is None:
            raise ValueError(
                "target must not be None."
            )

        try:
            vector = np.asarray(
                target,
                dtype=float,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "target must contain numeric values."
            ) from exc

        if vector.ndim == 2 and vector.shape[1] == 1:
            vector = vector.reshape(-1)

        if vector.ndim != 1:
            raise ValueError(
                "target must be one-dimensional."
            )

        if vector.size == 0:
            raise ValueError(
                "target must contain at least one value."
            )

        if not np.isfinite(vector).all():
            raise ValueError(
                "target must contain only finite values."
            )

        return vector


__all__ = [
    "LinearRegressionEstimator",
]