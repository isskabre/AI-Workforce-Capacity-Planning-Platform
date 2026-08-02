"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.contracts

Description:
    Defines the abstract contracts and protocols implemented by every
    forecasting algorithm in the Enterprise Forecast Modeling Framework.

    The contract layer is intentionally independent of Spark, Pandas,
    scikit-learn, MLflow, Databricks, and algorithm-specific libraries.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from enum import StrEnum
from os import PathLike
from typing import TYPE_CHECKING, Any, Protocol, Self, runtime_checkable

if TYPE_CHECKING:
    from forecast.modeling.artifacts import ForecastArtifact
    from forecast.modeling.contexts import (
        ForecastEvaluationContext,
        ForecastPredictionContext,
        ForecastTrainingContext,
    )
    from forecast.modeling.results import (
        ForecastEvaluationResult,
        ForecastPredictionResult,
        ForecastTrainingResult,
    )


class ForecastModelState(StrEnum):
    """Lifecycle states supported by an enterprise forecasting model."""

    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    EVALUATING = "EVALUATING"
    EVALUATED = "EVALUATED"
    SAVING = "SAVING"
    SAVED = "SAVED"
    LOADING = "LOADING"
    LOADED = "LOADED"
    PREDICTING = "PREDICTING"
    FAILED = "FAILED"


class ForecastModelCategory(StrEnum):
    """High-level forecasting model categories."""

    BASELINE = "BASELINE"
    STATISTICAL = "STATISTICAL"
    MACHINE_LEARNING = "MACHINE_LEARNING"
    DEEP_LEARNING = "DEEP_LEARNING"
    ENSEMBLE = "ENSEMBLE"
    CUSTOM = "CUSTOM"


class ForecastModelCapability(StrEnum):
    """Optional capabilities exposed by forecasting implementations."""

    POINT_FORECAST = "POINT_FORECAST"
    PROBABILISTIC_FORECAST = "PROBABILISTIC_FORECAST"
    PREDICTION_INTERVALS = "PREDICTION_INTERVALS"
    FEATURE_IMPORTANCE = "FEATURE_IMPORTANCE"
    EXPLAINABILITY = "EXPLAINABILITY"
    INCREMENTAL_TRAINING = "INCREMENTAL_TRAINING"
    MULTI_STEP_FORECAST = "MULTI_STEP_FORECAST"
    MULTIVARIATE_INPUT = "MULTIVARIATE_INPUT"
    HYPERPARAMETER_TUNING = "HYPERPARAMETER_TUNING"


@runtime_checkable
class ForecastModelMetadataProvider(Protocol):
    """
    Protocol for objects that expose forecasting-model metadata.

    Registry, evaluation, inference, and observability services may depend
    on this protocol without depending on a concrete model implementation.
    """

    @property
    def model_name(self) -> str:
        """Return the stable enterprise model name."""
        ...

    @property
    def model_version(self) -> str:
        """Return the model implementation version."""
        ...

    @property
    def model_category(self) -> ForecastModelCategory:
        """Return the model category."""
        ...

    @property
    def capabilities(self) -> frozenset[ForecastModelCapability]:
        """Return the model capabilities."""
        ...

    def get_metadata(self) -> Mapping[str, Any]:
        """Return serializable model metadata."""
        ...


@runtime_checkable
class ForecastModelLifecycle(Protocol):
    """
    Protocol representing the minimum lifecycle behavior of a forecast model.

    This protocol supports structural typing for services that require only
    lifecycle operations and do not need the full abstract model interface.
    """

    @property
    def state(self) -> ForecastModelState:
        """Return the current lifecycle state."""
        ...

    @property
    def is_initialized(self) -> bool:
        """Return whether initialization completed successfully."""
        ...

    @property
    def is_trained(self) -> bool:
        """Return whether training completed successfully."""
        ...

    def initialize(self) -> None:
        """Initialize implementation-specific resources."""
        ...

    def save(self, destination: str | PathLike[str]) -> "ForecastArtifact":
        """Persist the trained model and return its artifact."""
        ...

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        """Load a persisted model implementation."""
        ...


class BaseForecastModel(
    ABC,
    ForecastModelMetadataProvider,
):
    """
    Abstract base contract for all enterprise forecasting algorithms.

    Concrete implementations may wrap statistical, machine-learning,
    deep-learning, baseline, or ensemble forecasting algorithms. Every
    implementation must expose the same lifecycle and execution interface.

    The abstract contract deliberately does not prescribe:

    - the underlying machine-learning library;
    - the in-memory dataset representation;
    - the persistence technology;
    - the experiment-tracking platform;
    - the deployment environment.

    Those concerns belong to concrete adapters and orchestration services.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Return the stable enterprise model name.

        The value should remain stable across training executions and should
        uniquely identify the algorithm implementation within the platform.
        """

    @property
    @abstractmethod
    def model_version(self) -> str:
        """
        Return the implementation version.

        This version identifies the code-level forecasting implementation,
        not an individual trained artifact version.
        """

    @property
    @abstractmethod
    def model_category(self) -> ForecastModelCategory:
        """Return the high-level model category."""

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[ForecastModelCapability]:
        """
        Return the capabilities supported by this implementation.

        Capabilities allow orchestration and downstream services to determine
        compatibility without relying on concrete model classes.
        """

    @property
    @abstractmethod
    def state(self) -> ForecastModelState:
        """Return the current lifecycle state."""

    @property
    def is_initialized(self) -> bool:
        """Return whether the model has completed initialization."""
        return self.state in {
            ForecastModelState.INITIALIZED,
            ForecastModelState.TRAINING,
            ForecastModelState.TRAINED,
            ForecastModelState.EVALUATING,
            ForecastModelState.EVALUATED,
            ForecastModelState.SAVING,
            ForecastModelState.SAVED,
            ForecastModelState.PREDICTING,
        }

    @property
    def is_trained(self) -> bool:
        """Return whether the model has completed training."""
        return self.state in {
            ForecastModelState.TRAINED,
            ForecastModelState.EVALUATING,
            ForecastModelState.EVALUATED,
            ForecastModelState.SAVING,
            ForecastModelState.SAVED,
            ForecastModelState.PREDICTING,
        }

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize implementation-specific resources.

        Initialization may prepare an estimator, configure runtime state, or
        resolve optional dependencies. It must not train the model.
        """

    @abstractmethod
    def train(
        self,
        context: "ForecastTrainingContext",
    ) -> "ForecastTrainingResult":
        """
        Train the forecasting model.

        Args:
            context:
                Immutable training context containing model-ready datasets,
                feature definitions, target information, runtime configuration,
                and experiment metadata.

        Returns:
            A standardized enterprise training result.
        """

    @abstractmethod
    def predict(
        self,
        context: "ForecastPredictionContext",
    ) -> "ForecastPredictionResult":
        """
        Generate forecasts using a trained model.

        Args:
            context:
                Immutable prediction context containing inference inputs and
                forecast execution metadata.

        Returns:
            A standardized enterprise prediction result.
        """

    @abstractmethod
    def evaluate(
        self,
        context: "ForecastEvaluationContext",
    ) -> "ForecastEvaluationResult":
        """
        Evaluate forecasts against observed values.

        Args:
            context:
                Immutable evaluation context containing actual values,
                predicted values, metrics, and evaluation metadata.

        Returns:
            A standardized enterprise evaluation result.
        """

    @abstractmethod
    def save(
        self,
        destination: str | PathLike[str],
    ) -> "ForecastArtifact":
        """
        Persist the trained model.

        Args:
            destination:
                Platform-independent artifact destination.

        Returns:
            A standardized artifact describing the persisted model.

        Raises:
            Exception:
                Concrete implementations should raise a framework-specific
                persistence exception when persistence fails.
        """

    @classmethod
    @abstractmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        """
        Load a persisted model.

        Args:
            source:
                Platform-independent artifact source.
            metadata:
                Optional artifact or registry metadata required to reconstruct
                the model.

        Returns:
            A loaded forecasting model implementation.
        """

    @abstractmethod
    def get_metadata(self) -> Mapping[str, Any]:
        """
        Return serializable implementation metadata.

        The returned mapping must not contain active model objects, Spark
        objects, open file handles, or non-serializable runtime resources.
        """

    def supports(self, capability: ForecastModelCapability) -> bool:
        """
        Return whether the model supports a capability.

        Args:
            capability:
                Capability to evaluate.

        Returns:
            ``True`` when the capability is declared by the model.
        """
        return capability in self.capabilities


__all__ = [
    "BaseForecastModel",
    "ForecastModelCapability",
    "ForecastModelCategory",
    "ForecastModelLifecycle",
    "ForecastModelMetadataProvider",
    "ForecastModelState",
]