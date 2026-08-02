"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.algorithms.random_forest.estimator

Description:
    Implements the enterprise Random Forest regression estimator.

    The estimator wraps scikit-learn RandomForestRegressor while preserving
    the standardized EnterpriseEstimator lifecycle, metadata, validation,
    serialization, persistence, and reset contracts used by the platform.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

import base64
import pickle
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Any, Self

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from forecast.algorithms.base.estimator import EnterpriseEstimator
from forecast.algorithms.base.serializer import EnterpriseSerializer


class RandomForestEstimator(EnterpriseEstimator):
    """
    Enterprise Random Forest regression estimator.

    The estimator supports deterministic ensemble training, batch prediction,
    feature-importance reporting, tree-level prediction dispersion, complete
    serialization, persistence, and restoration.

    Serialized model payloads must only be loaded from trusted internal
    artifact locations because the fitted scikit-learn estimator is stored
    using Python pickle serialization.
    """

    ESTIMATOR_NAME = "random_forest_estimator"
    FRAMEWORK = "scikit_learn"
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
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        self._validate_hyperparameters(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            bootstrap=bootstrap,
            random_state=random_state,
            n_jobs=n_jobs,
        )

        resolved_parameters = {
            **dict(parameters or {}),
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "max_features": max_features,
            "bootstrap": bootstrap,
            "random_state": random_state,
            "n_jobs": n_jobs,
        }

        super().__init__(
            estimator_name=self.ESTIMATOR_NAME,
            framework=self.FRAMEWORK,
            version=self.VERSION,
            parameters=resolved_parameters,
        )

        self._n_estimators = n_estimators
        self._max_depth = max_depth
        self._min_samples_split = min_samples_split
        self._min_samples_leaf = min_samples_leaf
        self._max_features = max_features
        self._bootstrap = bootstrap
        self._random_state = random_state
        self._n_jobs = n_jobs

        self._model: RandomForestRegressor | None = None
        self._feature_importances: tuple[float, ...] = ()
        self._feature_count: int | None = None

    # ------------------------------------------------------------------
    # Hyperparameters and learned state
    # ------------------------------------------------------------------

    @property
    def n_estimators(self) -> int:
        return self._n_estimators

    @property
    def max_depth(self) -> int | None:
        return self._max_depth

    @property
    def min_samples_split(self) -> int:
        return self._min_samples_split

    @property
    def min_samples_leaf(self) -> int:
        return self._min_samples_leaf

    @property
    def max_features(self) -> str | int | float | None:
        return self._max_features

    @property
    def bootstrap(self) -> bool:
        return self._bootstrap

    @property
    def random_state(self) -> int | None:
        return self._random_state

    @property
    def n_jobs(self) -> int | None:
        return self._n_jobs

    @property
    def model(self) -> RandomForestRegressor | None:
        """Return the fitted scikit-learn estimator."""
        return self._model

    @property
    def feature_importances(self) -> tuple[float, ...]:
        """Return normalized feature-importance values."""
        return self._feature_importances

    @property
    def feature_count(self) -> int | None:
        """Return the number of fitted input features."""
        return self._feature_count

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Fit the Random Forest regressor.

        Args:
            features:
                Two-dimensional numeric feature matrix.
            target:
                One-dimensional numeric target vector.

        Returns:
            This fitted estimator.

        Raises:
            ValueError:
                If feature or target data is invalid or incompatible.
        """
        feature_matrix = self._to_feature_matrix(features)
        target_vector = self._to_target_vector(target)

        record_count, feature_count = feature_matrix.shape

        if record_count != target_vector.shape[0]:
            raise ValueError(
                "Feature and target record counts must match. "
                f"Received {record_count} feature records and "
                f"{target_vector.shape[0]} target records."
            )

        if record_count < 2:
            raise ValueError(
                "Random Forest requires at least two training records."
            )

        model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            bootstrap=self.bootstrap,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
        )

        model.fit(
            feature_matrix,
            target_vector,
        )

        self._model = model
        self._feature_count = feature_count
        self._feature_importances = tuple(
            float(value)
            for value in model.feature_importances_
        )

        training_predictions = model.predict(feature_matrix)
        residuals = target_vector - training_predictions

        training_mse = float(
            np.mean(np.square(residuals))
        )
        training_rmse = float(
            np.sqrt(training_mse)
        )
        training_mae = float(
            np.mean(np.abs(residuals))
        )

        self.mark_fitted(
            training_metadata={
                "training_records": record_count,
                "feature_count": feature_count,
                "n_estimators": self.n_estimators,
                "max_depth": self.max_depth,
                "min_samples_split": self.min_samples_split,
                "min_samples_leaf": self.min_samples_leaf,
                "max_features": self.max_features,
                "bootstrap": self.bootstrap,
                "random_state": self.random_state,
                "training_mae": training_mae,
                "training_mse": training_mse,
                "training_rmse": training_rmse,
            }
        )

        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        """
        Generate ensemble-average predictions.
        """
        model = self._require_fitted_model()

        feature_matrix = self._to_feature_matrix(features)

        self._validate_prediction_feature_count(
            feature_matrix
        )

        predictions = model.predict(
            feature_matrix
        )

        return tuple(
            float(value)
            for value in predictions
        )

    def predict_with_dispersion(
        self,
        features: Any,
    ) -> tuple[
        tuple[float, ...],
        tuple[float, ...],
    ]:
        """
        Return ensemble predictions and tree-level standard deviations.

        Returns:
            A two-item tuple containing:

            1. Ensemble mean predictions.
            2. Standard deviation across individual tree predictions.
        """
        model = self._require_fitted_model()

        feature_matrix = self._to_feature_matrix(features)

        self._validate_prediction_feature_count(
            feature_matrix
        )

        tree_predictions = np.vstack(
            [
                tree.predict(feature_matrix)
                for tree in model.estimators_
            ]
        )

        means = np.mean(
            tree_predictions,
            axis=0,
        )

        standard_deviations = np.std(
            tree_predictions,
            axis=0,
        )

        return (
            tuple(float(value) for value in means),
            tuple(
                float(value)
                for value in standard_deviations
            ),
        )

    # ------------------------------------------------------------------
    # Serialization and persistence
    # ------------------------------------------------------------------

    def serialize(self) -> Mapping[str, Any]:
        """
        Return serialization-safe estimator state.

        The fitted scikit-learn model is encoded as a Base64 pickle payload.
        """
        model_blob = None

        if self._model is not None:
            serialized_model = pickle.dumps(
                self._model,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

            model_blob = base64.b64encode(
                serialized_model
            ).decode("ascii")

        return {
            "schema_version": "1.0",
            "estimator_name": self.estimator_name,
            "framework": self.framework,
            "version": self.version,
            "parameters": dict(self.parameters),
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "min_samples_split": self.min_samples_split,
            "min_samples_leaf": self.min_samples_leaf,
            "max_features": self.max_features,
            "bootstrap": self.bootstrap,
            "random_state": self.random_state,
            "n_jobs": self.n_jobs,
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(
                self.training_metadata
            ),
            "feature_importances": list(
                self.feature_importances
            ),
            "feature_count": self.feature_count,
            "model_blob": model_blob,
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """
        Reconstruct a Random Forest estimator from serialized state.
        """
        estimator = cls(
            n_estimators=int(
                payload.get("n_estimators", 200)
            ),
            max_depth=payload.get("max_depth"),
            min_samples_split=int(
                payload.get("min_samples_split", 2)
            ),
            min_samples_leaf=int(
                payload.get("min_samples_leaf", 1)
            ),
            max_features=payload.get(
                "max_features",
                1.0,
            ),
            bootstrap=bool(
                payload.get("bootstrap", True)
            ),
            random_state=payload.get(
                "random_state",
                42,
            ),
            n_jobs=payload.get("n_jobs", -1),
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
        estimator._feature_importances = tuple(
            float(value)
            for value in payload.get(
                "feature_importances",
                (),
            )
        )

        feature_count = payload.get(
            "feature_count"
        )

        estimator._feature_count = (
            int(feature_count)
            if feature_count is not None
            else None
        )

        model_blob = payload.get("model_blob")

        if model_blob is not None:
            try:
                model_bytes = base64.b64decode(
                    model_blob.encode("ascii")
                )

                restored_model = pickle.loads(
                    model_bytes
                )
            except Exception as exc:
                raise ValueError(
                    "Unable to deserialize the Random Forest model."
                ) from exc

            if not isinstance(
                restored_model,
                RandomForestRegressor,
            ):
                raise ValueError(
                    "Serialized model is not a RandomForestRegressor."
                )

            estimator._model = restored_model

        if estimator._fitted and estimator._model is None:
            raise ValueError(
                "A fitted Random Forest estimator must contain "
                "serialized model state."
            )

        if (
            estimator._fitted
            and estimator._feature_count is None
        ):
            raise ValueError(
                "A fitted Random Forest estimator must contain "
                "a feature count."
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
        """Reset runtime and fitted model state."""
        super().reset()

        self._model = None
        self._feature_importances = ()
        self._feature_count = None

    # ------------------------------------------------------------------
    # Internal validation
    # ------------------------------------------------------------------

    def _require_fitted_model(
        self,
    ) -> RandomForestRegressor:
        """Return the fitted model or raise a lifecycle error."""
        if not self.fitted or self._model is None:
            raise RuntimeError(
                "Random Forest estimator must be fitted "
                "before prediction."
            )

        return self._model

    def _validate_prediction_feature_count(
        self,
        feature_matrix: np.ndarray,
    ) -> None:
        """Validate prediction schema against fitted schema."""
        if self.feature_count is None:
            raise RuntimeError(
                "Random Forest fitted feature count is unavailable."
            )

        if feature_matrix.shape[1] != self.feature_count:
            raise ValueError(
                "Prediction feature count does not match the fitted "
                "feature count. "
                f"Received {feature_matrix.shape[1]} features; "
                f"expected {self.feature_count}."
            )

    @staticmethod
    def _to_feature_matrix(
        features: Any,
    ) -> np.ndarray:
        """Convert features into a finite two-dimensional float matrix."""
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
        """Convert target input into a finite one-dimensional vector."""
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

    @staticmethod
    def _validate_hyperparameters(
        *,
        n_estimators: int,
        max_depth: int | None,
        min_samples_split: int,
        min_samples_leaf: int,
        max_features: str | int | float | None,
        bootstrap: bool,
        random_state: int | None,
        n_jobs: int | None,
    ) -> None:
        """Validate supported Random Forest hyperparameters."""
        if (
            isinstance(n_estimators, bool)
            or not isinstance(n_estimators, int)
            or n_estimators <= 0
        ):
            raise ValueError(
                "n_estimators must be a positive integer."
            )

        if max_depth is not None and (
            isinstance(max_depth, bool)
            or not isinstance(max_depth, int)
            or max_depth <= 0
        ):
            raise ValueError(
                "max_depth must be None or a positive integer."
            )

        if (
            isinstance(min_samples_split, bool)
            or not isinstance(min_samples_split, int)
            or min_samples_split < 2
        ):
            raise ValueError(
                "min_samples_split must be an integer greater "
                "than or equal to two."
            )

        if (
            isinstance(min_samples_leaf, bool)
            or not isinstance(min_samples_leaf, int)
            or min_samples_leaf <= 0
        ):
            raise ValueError(
                "min_samples_leaf must be a positive integer."
            )

        valid_string_max_features = {
            "sqrt",
            "log2",
        }

        if isinstance(max_features, str):
            if max_features not in valid_string_max_features:
                raise ValueError(
                    "String max_features must be 'sqrt' or 'log2'."
                )

        elif isinstance(max_features, bool):
            raise ValueError(
                "max_features must be None, 'sqrt', 'log2', "
                "a positive integer, or a float in (0, 1]."
            )

        elif isinstance(max_features, int):
            if max_features <= 0:
                raise ValueError(
                    "Integer max_features must be positive."
                )

        elif isinstance(max_features, float):
            if not 0.0 < max_features <= 1.0:
                raise ValueError(
                    "Float max_features must be in the interval (0, 1]."
                )

        elif max_features is not None:
            raise ValueError(
                "Unsupported max_features value."
            )

        if not isinstance(bootstrap, bool):
            raise ValueError(
                "bootstrap must be a boolean."
            )

        if random_state is not None and (
            isinstance(random_state, bool)
            or not isinstance(random_state, int)
        ):
            raise ValueError(
                "random_state must be None or an integer."
            )

        if n_jobs is not None and (
            isinstance(n_jobs, bool)
            or not isinstance(n_jobs, int)
            or n_jobs == 0
        ):
            raise ValueError(
                "n_jobs must be None or a nonzero integer."
            )


__all__ = [
    "RandomForestEstimator",
]