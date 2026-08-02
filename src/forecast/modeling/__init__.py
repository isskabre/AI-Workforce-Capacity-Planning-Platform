"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling

Description:
    Public package interface for the Enterprise Forecast Modeling Framework.

    This module exposes the stable contracts, configuration objects,
    artifacts, results, exceptions, and factory services intended for use by
    training, evaluation, inference, registry, orchestration, and algorithm
    adapters.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from forecast.modeling.configuration import (
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
from forecast.modeling.contexts import (
    DatasetLike,
    FeatureColumns,
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
    Metadata,
)
from forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelLifecycle,
    ForecastModelMetadataProvider,
    ForecastModelState,
)
from forecast.modeling.exceptions import (
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
from forecast.modeling.factory import (
    ForecastModelBuilder,
    ForecastModelFactory,
    ForecastModelRegistration,
    register_forecast_model,
)
from forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)
from .metrics import ForecastMetrics

__all__ = [
    "BaseForecastModel",
    "ChampionSelectionMode",
    "DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION",
    "DatasetLike",
    "EnterpriseForecastConfiguration",
    "EvaluationConfiguration",
    "FeatureColumns",
    "ForecastArtifact",
    "ForecastArtifactError",
    "ForecastArtifactStatus",
    "ForecastConfiguration",
    "ForecastConfigurationError",
    "ForecastContextError",
    "ForecastDependencyError",
    "ForecastEvaluationContext",
    "ForecastEvaluationError",
    "ForecastEvaluationMetric",
    "ForecastEvaluationResult",
    "ForecastExecutionStatus",
    "ForecastGranularity",
    "ForecastInferenceError",
    "ForecastInitializationError",
    "ForecastModelBuilder",
    "ForecastModelCapability",
    "ForecastModelCategory",
    "ForecastModelFactory",
    "ForecastModelLifecycle",
    "ForecastModelMetadataProvider",
    "ForecastModelingError",
    "ForecastModelNotFoundError",
    "ForecastModelRegistration",
    "ForecastModelState",
    "ForecastPersistenceError",
    "ForecastPredictionContext",
    "ForecastPredictionError",
    "ForecastPredictionResult",
    "ForecastRegistryError",
    "ForecastStateError",
    "ForecastTrainingContext",
    "ForecastTrainingError",
    "ForecastTrainingResult",
    "Metadata",
    "RegistryConfiguration",
    "RuntimeConfiguration",
    "TrainingConfiguration",
    "UnsupportedForecastModelError",
    "register_forecast_model",
    "ForecastMetrics",
]