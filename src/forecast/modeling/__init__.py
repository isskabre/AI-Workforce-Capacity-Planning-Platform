"""
AI Workforce Capacity Planning Platform
Implementation 11 — Enterprise Forecast Modeling Framework

Module:
    src.forecast.modeling

Description:
    Public package interface for the Enterprise Forecast Modeling Framework.

    This module exposes the stable contracts, configuration objects,
    artifacts, results, exceptions, metrics, and factory services intended
    for use by training, evaluation, inference, model registry,
    orchestration, and forecast algorithm adapters.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from .artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from .configuration import (
    ChampionSelectionMode,
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION,
    EnterpriseForecastConfiguration,
    EvaluationConfiguration,
    ForecastConfiguration,
    ForecastEvaluationMetric,
    ForecastGranularity,
    RegistryConfiguration,
    RuntimeConfiguration,
    TrainingConfiguration,
)
from .contexts import (
    DatasetLike,
    FeatureColumns,
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
    Metadata,
)
from .contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelLifecycle,
    ForecastModelMetadataProvider,
    ForecastModelState,
)
from .exceptions import (
    ForecastArtifactError,
    ForecastConfigurationError,
    ForecastContextError,
    ForecastDependencyError,
    ForecastEvaluationError,
    ForecastInferenceError,
    ForecastInitializationError,
    ForecastModelingError,
    ForecastModelNotFoundError,
    ForecastPersistenceError,
    ForecastPredictionError,
    ForecastRegistryError,
    ForecastStateError,
    ForecastTrainingError,
    UnsupportedForecastModelError,
)
from .factory import (
    ForecastModelBuilder,
    ForecastModelFactory,
    ForecastModelRegistration,
    register_forecast_model,
)
from .metrics import ForecastMetrics
from .results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


__all__ = [
    # Core contracts
    "BaseForecastModel",
    "ForecastModelCapability",
    "ForecastModelCategory",
    "ForecastModelLifecycle",
    "ForecastModelMetadataProvider",
    "ForecastModelState",

    # Contexts and shared aliases
    "DatasetLike",
    "FeatureColumns",
    "ForecastEvaluationContext",
    "ForecastPredictionContext",
    "ForecastTrainingContext",
    "Metadata",

    # Configuration
    "ChampionSelectionMode",
    "DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION",
    "EnterpriseForecastConfiguration",
    "EvaluationConfiguration",
    "ForecastConfiguration",
    "ForecastEvaluationMetric",
    "ForecastGranularity",
    "RegistryConfiguration",
    "RuntimeConfiguration",
    "TrainingConfiguration",

    # Artifacts and results
    "ForecastArtifact",
    "ForecastArtifactStatus",
    "ForecastEvaluationResult",
    "ForecastExecutionStatus",
    "ForecastPredictionResult",
    "ForecastTrainingResult",

    # Metrics
    "ForecastMetrics",

    # Factory
    "ForecastModelBuilder",
    "ForecastModelFactory",
    "ForecastModelRegistration",
    "register_forecast_model",

    # Exceptions
    "ForecastArtifactError",
    "ForecastConfigurationError",
    "ForecastContextError",
    "ForecastDependencyError",
    "ForecastEvaluationError",
    "ForecastInferenceError",
    "ForecastInitializationError",
    "ForecastModelingError",
    "ForecastModelNotFoundError",
    "ForecastPersistenceError",
    "ForecastPredictionError",
    "ForecastRegistryError",
    "ForecastStateError",
    "ForecastTrainingError",
    "UnsupportedForecastModelError",
]