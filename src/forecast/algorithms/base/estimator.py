"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    forecast.algorithms.base.estimator

Description:
    Defines the framework-independent enterprise estimator contract used by
    forecasting algorithm adapters.

    An estimator encapsulates the underlying statistical, machine-learning,
    or deep-learning engine while exposing standardized initialization,
    fitting, prediction, metadata, persistence, and serialization behavior.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from os import PathLike
from typing import Any, Self


class EnterpriseEstimator(ABC):
    """
    Framework-independent base class for forecasting estimators.

    Concrete implementations may wrap scikit-learn, XGBoost, LightGBM,
    PyTorch, TensorFlow, Prophet, statsmodels, or custom estimators without
    exposing framework-specific behavior to the forecasting model layer.
    """

    def __init__(
        self,
        *,
        estimator_name: str,
        framework: str,
        version: str = "1.0.0",
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        self._estimator_name = estimator_name
        self._framework = framework
        self._version = version
        self._parameters = dict(parameters or {})

        self._initialized = False
        self._fitted = False

        self._feature_names: tuple[str, ...] = ()
        self._target_name: str | None = None
        self._training_metadata: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def estimator_name(self) -> str:
        """Return the stable estimator name."""
        return self._estimator_name

    @property
    def framework(self) -> str:
        """Return the underlying estimator framework."""
        return self._framework

    @property
    def version(self) -> str:
        """Return the estimator adapter version."""
        return self._version

    @property
    def parameters(self) -> Mapping[str, Any]:
        """Return a copy of the configured estimator parameters."""
        return dict(self._parameters)

    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------

    @property
    def initialized(self) -> bool:
        """Return whether estimator metadata has been initialized."""
        return self._initialized

    @property
    def fitted(self) -> bool:
        """Return whether fitting completed successfully."""
        return self._fitted

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return ordered feature names used for fitting."""
        return self._feature_names

    @property
    def target_name(self) -> str | None:
        """Return the configured target name."""
        return self._target_name

    @property
    def training_metadata(self) -> Mapping[str, Any]:
        """Return a copy of estimator training metadata."""
        return dict(self._training_metadata)

    # ------------------------------------------------------------------
    # Shared lifecycle
    # ------------------------------------------------------------------

    def initialize(
        self,
        *,
        feature_names: tuple[str, ...],
        target_name: str,
    ) -> None:
        """
        Initialize estimator feature and target metadata.

        Args:
            feature_names:
                Ordered model input columns.
            target_name:
                Target variable predicted by the estimator.
        """
        self._feature_names = tuple(feature_names)
        self._target_name = target_name
        self._initialized = True

    def mark_fitted(
        self,
        *,
        training_metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Mark fitting as successfully completed.

        Concrete estimators should call this only after their underlying
        estimator has completed fitting without error.
        """
        self._fitted = True
        self._training_metadata = dict(training_metadata or {})

    def reset(self) -> None:
        """
        Reset runtime and training state without changing estimator identity.
        """
        self._initialized = False
        self._fitted = False
        self._feature_names = ()
        self._target_name = None
        self._training_metadata = {}

    def get_metadata(self) -> Mapping[str, Any]:
        """
        Return serialization-safe estimator metadata.
        """
        return {
            "estimator_name": self.estimator_name,
            "framework": self.framework,
            "version": self.version,
            "parameters": dict(self.parameters),
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(self.training_metadata),
        }

    # ------------------------------------------------------------------
    # Concrete estimator contract
    # ------------------------------------------------------------------

    @abstractmethod
    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Fit the underlying estimator and return this adapter.
        """

    @abstractmethod
    def predict(
        self,
        features: Any,
    ) -> Any:
        """
        Generate predictions using the fitted estimator.
        """

    @abstractmethod
    def serialize(self) -> Mapping[str, Any]:
        """
        Return serialization-safe estimator state.
        """

    @classmethod
    @abstractmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """
        Reconstruct an estimator from serialized state.
        """

    @abstractmethod
    def save(
        self,
        destination: str | PathLike[str],
    ) -> None:
        """
        Persist the estimator to a platform-independent destination.
        """

    @classmethod
    @abstractmethod
    def load(
        cls,
        source: str | PathLike[str],
    ) -> Self:
        """
        Load and return a persisted estimator.
        """


__all__ = [
    "EnterpriseEstimator",
]