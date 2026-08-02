"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.algorithms.base.forecast_model

Description:
    Defines the reusable enterprise parent class implemented by every
    forecasting algorithm supported by the platform.

    The class provides common model identity, lifecycle state, metadata,
    execution-context tracking, capability reporting, and reset behavior.

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

from forecast.modeling.artifacts import ForecastArtifact
from forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


class EnterpriseForecastModel(BaseForecastModel, ABC):
    """
    Reusable enterprise parent class for forecasting algorithms.

    Concrete model adapters inherit this class and implement only their
    algorithm-specific training, prediction, evaluation, persistence, and
    serialization behavior.

    Attributes:
        model_key:
            Stable configuration and factory identifier.
        display_name:
            Human-readable model name.
        category:
            High-level forecasting model category.
        algorithm:
            Concrete algorithm identifier.
        version:
            Adapter implementation version.
        capabilities:
            Features supported by the forecasting implementation.
    """

    def __init__(
        self,
        *,
        model_key: str,
        display_name: str,
        category: ForecastModelCategory,
        algorithm: str,
        version: str = "1.0.0",
        capabilities: frozenset[ForecastModelCapability] | None = None,
    ) -> None:
        self._model_key = model_key
        self._display_name = display_name
        self._category = category
        self._algorithm = algorithm
        self._version = version
        self._capabilities = frozenset(capabilities or ())

        self._state = ForecastModelState.CREATED
        self._artifact: ForecastArtifact | None = None

        self._training_context: ForecastTrainingContext | None = None
        self._prediction_context: ForecastPredictionContext | None = None
        self._evaluation_context: ForecastEvaluationContext | None = None

    # ------------------------------------------------------------------
    # Enterprise identity
    # ------------------------------------------------------------------

    @property
    def model_key(self) -> str:
        """Return the stable factory and configuration identifier."""
        return self._model_key

    @property
    def display_name(self) -> str:
        """Return the human-readable model name."""
        return self._display_name

    @property
    def algorithm(self) -> str:
        """Return the concrete algorithm identifier."""
        return self._algorithm

    @property
    def version(self) -> str:
        """Return the adapter implementation version."""
        return self._version

    # ------------------------------------------------------------------
    # BaseForecastModel contract
    # ------------------------------------------------------------------

    @property
    def model_name(self) -> str:
        """Return the stable enterprise model name."""
        return self._display_name

    @property
    def model_version(self) -> str:
        """Return the forecasting implementation version."""
        return self._version

    @property
    def model_category(self) -> ForecastModelCategory:
        """Return the high-level forecasting model category."""
        return self._category

    @property
    def category(self) -> ForecastModelCategory:
        """Return the high-level forecasting model category."""
        return self._category

    @property
    def capabilities(self) -> frozenset[ForecastModelCapability]:
        """Return the capabilities supported by this model."""
        return self._capabilities

    @property
    def state(self) -> ForecastModelState:
        """Return the current lifecycle state."""
        return self._state

    # ------------------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------------------

    @property
    def artifact(self) -> ForecastArtifact | None:
        """Return the currently associated model artifact."""
        return self._artifact

    @property
    def training_context(self) -> ForecastTrainingContext | None:
        """Return the most recent training context."""
        return self._training_context

    @property
    def prediction_context(self) -> ForecastPredictionContext | None:
        """Return the most recent prediction context."""
        return self._prediction_context

    @property
    def evaluation_context(self) -> ForecastEvaluationContext | None:
        """Return the most recent evaluation context."""
        return self._evaluation_context

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the forecasting model.

        Concrete implementations may override this method when estimator or
        runtime initialization is required, but should preserve the lifecycle
        transition to ``INITIALIZED``.
        """
        self._state = ForecastModelState.INITIALIZED

    def reset(self) -> None:
        """Reset runtime state without changing model identity."""
        self._state = ForecastModelState.CREATED
        self._artifact = None
        self._training_context = None
        self._prediction_context = None
        self._evaluation_context = None

    def get_metadata(self) -> Mapping[str, Any]:
        """
        Return serialization-safe model metadata.

        Returns:
            Stable model identity, lifecycle state, and declared capabilities.
        """
        return {
            "model_key": self.model_key,
            "model_name": self.model_name,
            "display_name": self.display_name,
            "model_version": self.model_version,
            "model_category": self.model_category.value,
            "algorithm": self.algorithm,
            "state": self.state.value,
            "capabilities": sorted(
                capability.value for capability in self.capabilities
            ),
            "artifact_id": (
                self.artifact.artifact_id
                if self.artifact is not None
                else None
            ),
        }

    # ------------------------------------------------------------------
    # Algorithm-specific lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def train(
        self,
        context: ForecastTrainingContext,
    ) -> ForecastTrainingResult:
        """Train the concrete forecasting algorithm."""

    @abstractmethod
    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        """Generate predictions using the trained model."""

    @abstractmethod
    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        """Evaluate model predictions."""

    @abstractmethod
    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        """Persist the trained model and return artifact metadata."""

    @classmethod
    @abstractmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        """Load and return a persisted forecasting model."""

    @abstractmethod
    def serialize(self) -> Mapping[str, Any]:
        """Return serialization-safe algorithm state."""

    @classmethod
    @abstractmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct a forecasting model from serialized state."""


__all__ = [
    "EnterpriseForecastModel",
]