"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.configuration

Description:
    Defines immutable, strongly typed configuration objects for enterprise
    forecast modeling, training, evaluation, registry, and runtime execution.

    These objects contain configuration only. Validation, orchestration,
    persistence, and model-specific execution remain the responsibility of
    their dedicated platform services.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import Any


class ForecastGranularity(StrEnum):
    """Supported business forecasting granularities."""

    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ForecastEvaluationMetric(StrEnum):
    """Standard forecasting evaluation metrics."""

    MAE = "MAE"
    RMSE = "RMSE"
    MAPE = "MAPE"
    SMAPE = "SMAPE"
    WAPE = "WAPE"
    R2 = "R2"
    BIAS = "BIAS"


class ChampionSelectionMode(StrEnum):
    """Supported champion-model selection strategies."""

    MINIMIZE = "MINIMIZE"
    MAXIMIZE = "MAXIMIZE"


def _serialize_value(value: Any) -> Any:
    """
    Convert supported configuration values into serializable structures.

    This helper intentionally performs shallow, predictable conversion rather
    than relying on ``dataclasses.asdict()``, which recursively deep-copies
    values and may fail for infrastructure-specific runtime objects.
    """
    if isinstance(value, StrEnum):
        return value.value

    if isinstance(value, tuple):
        return [_serialize_value(item) for item in value]

    if isinstance(value, Mapping):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()

    return value


class ConfigurationMixin:
    """Shared serialization behavior for immutable configuration objects."""

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serialization-safe dictionary representation.

        Returns:
            Configuration fields converted to primitive Python structures.
        """
        return {
            configuration_field.name: _serialize_value(
                getattr(self, configuration_field.name)
            )
            for configuration_field in fields(self)
        }


@dataclass(frozen=True, slots=True)
class ForecastConfiguration(ConfigurationMixin):
    """
    Business-level forecast configuration.

    Attributes:
        forecast_horizon_days:
            Number of future daily periods to predict.
        granularity:
            Forecast time granularity.
        datetime_column:
            Chronological ordering column.
        target_column:
            Business target predicted by the models.
        feature_columns:
            Ordered approved feature columns.
        grouping_columns:
            Optional entity or hierarchy columns.
        minimum_training_records:
            Minimum acceptable training observations.
        maximum_training_records:
            Optional maximum observations used during training.
    """

    forecast_horizon_days: int = 14
    granularity: ForecastGranularity = ForecastGranularity.DAILY
    datetime_column: str = "forecast_date"
    target_column: str = "workload"
    feature_columns: tuple[str, ...] = ()
    grouping_columns: tuple[str, ...] = ()
    minimum_training_records: int = 90
    maximum_training_records: int | None = None


@dataclass(frozen=True, slots=True)
class TrainingConfiguration(ConfigurationMixin):
    """
    Model-training configuration.

    Attributes:
        enabled_models:
            Ordered algorithm identifiers eligible for execution.
        random_seed:
            Reproducibility seed used by compatible algorithms.
        training_ratio:
            Proportion assigned to training.
        validation_ratio:
            Proportion assigned to validation.
        test_ratio:
            Proportion assigned to testing.
        cross_validation_folds:
            Number of time-aware cross-validation folds.
        shuffle_training:
            Whether compatible model adapters may shuffle observations.
            Time-series pipelines should normally keep this disabled.
        enable_hyperparameter_tuning:
            Whether tuning is enabled.
        max_training_time_minutes:
            Optional training time limit.
        parallel_training:
            Whether independent algorithms may train concurrently.
        model_parameters:
            Per-model hyperparameter mappings.
    """

    enabled_models: tuple[str, ...] = (
        "naive_last_value",
        "linear_regression",
        "random_forest",
    )
    random_seed: int = 42
    training_ratio: float = 0.70
    validation_ratio: float = 0.15
    test_ratio: float = 0.15
    cross_validation_folds: int = 3
    shuffle_training: bool = False
    enable_hyperparameter_tuning: bool = False
    max_training_time_minutes: int | None = None
    parallel_training: bool = False
    model_parameters: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class EvaluationConfiguration(ConfigurationMixin):
    """
    Forecast evaluation and ranking configuration.

    Attributes:
        primary_metric:
            Metric used for model ranking.
        secondary_metrics:
            Additional metrics calculated for analysis.
        champion_selection_mode:
            Whether the primary metric is minimized or maximized.
        maximum_acceptable_mape:
            Optional business-quality threshold.
        maximum_acceptable_wape:
            Optional business-quality threshold.
        store_predictions:
            Whether row-level predictions are retained.
        generate_evaluation_report:
            Whether evaluation reports are generated.
        generate_feature_importance:
            Whether compatible models produce feature importance.
        generate_residual_analysis:
            Whether residual diagnostics are generated.
    """

    primary_metric: ForecastEvaluationMetric = (
        ForecastEvaluationMetric.WAPE
    )
    secondary_metrics: tuple[ForecastEvaluationMetric, ...] = (
        ForecastEvaluationMetric.MAE,
        ForecastEvaluationMetric.RMSE,
        ForecastEvaluationMetric.MAPE,
        ForecastEvaluationMetric.SMAPE,
        ForecastEvaluationMetric.BIAS,
    )
    champion_selection_mode: ChampionSelectionMode = (
        ChampionSelectionMode.MINIMIZE
    )
    maximum_acceptable_mape: float | None = None
    maximum_acceptable_wape: float | None = None
    store_predictions: bool = True
    generate_evaluation_report: bool = True
    generate_feature_importance: bool = True
    generate_residual_analysis: bool = True


@dataclass(frozen=True, slots=True)
class RegistryConfiguration(ConfigurationMixin):
    """
    Forecast model registry configuration.

    Attributes:
        enabled:
            Whether trained model artifacts are registered.
        registry_uri:
            Enterprise model-registry location.
        artifact_root_uri:
            Root location for persisted trained model artifacts.
        model_version_prefix:
            Prefix applied to generated artifact versions.
        retain_previous_versions:
            Whether historical versions remain available.
        enable_model_lineage:
            Whether dataset, configuration, and execution lineage is recorded.
        store_training_artifacts:
            Whether model binaries and supporting assets are persisted.
    """

    enabled: bool = True
    registry_uri: str = ""
    artifact_root_uri: str = ""
    model_version_prefix: str = "v"
    retain_previous_versions: bool = True
    enable_model_lineage: bool = True
    store_training_artifacts: bool = True


@dataclass(frozen=True, slots=True)
class RuntimeConfiguration(ConfigurationMixin):
    """
    Forecast framework runtime configuration.

    Attributes:
        experiment_name:
            Stable enterprise experiment name.
        execution_environment:
            Runtime environment such as development, test, or production.
        logging_enabled:
            Whether execution logging is enabled.
        save_checkpoints:
            Whether intermediate execution checkpoints are persisted.
        cache_predictions:
            Whether prediction outputs may be cached.
        retrain_if_dataset_changes:
            Whether changed dataset fingerprints trigger retraining.
        fail_fast:
            Whether execution stops after the first critical failure.
        execution_tags:
            Additional execution metadata.
    """

    experiment_name: str = "enterprise-forecast-modeling"
    execution_environment: str = "development"
    logging_enabled: bool = True
    save_checkpoints: bool = True
    cache_predictions: bool = False
    retrain_if_dataset_changes: bool = True
    fail_fast: bool = True
    execution_tags: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EnterpriseForecastConfiguration(ConfigurationMixin):
    """
    Root configuration contract for the Forecast Modeling Framework.

    This aggregate is passed through orchestration rather than passing
    independent configuration objects to every service.
    """

    forecast: ForecastConfiguration = field(
        default_factory=ForecastConfiguration
    )
    training: TrainingConfiguration = field(
        default_factory=TrainingConfiguration
    )
    evaluation: EvaluationConfiguration = field(
        default_factory=EvaluationConfiguration
    )
    registry: RegistryConfiguration = field(
        default_factory=RegistryConfiguration
    )
    runtime: RuntimeConfiguration = field(
        default_factory=RuntimeConfiguration
    )


DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION = (
    EnterpriseForecastConfiguration()
)


__all__ = [
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
]