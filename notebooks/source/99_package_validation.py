# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Implementation 28 — Enterprise Release Validation
# MAGIC **Notebook:** `99_package_validation`  
# MAGIC **Platform release:** v3.0.0  
# MAGIC **Canonical namespace:** `src.*`  
# MAGIC **Release finding:** ENG-001 — Inconsistent Python import namespaces
# MAGIC
# MAGIC Remediated from the historical validation notebook.

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

# MAGIC %run ./00_project_setup

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# Bootstrap validation
# Platform release: v3.0.0
# Canonical namespace: src.*
# =============================================================================

from pathlib import Path
import sys

repository_root = Path.cwd()

while (
    repository_root.parent != repository_root
    and not (repository_root / "src").is_dir()
):
    repository_root = repository_root.parent

if not (repository_root / "src").is_dir():
    raise RuntimeError(
        "Unable to locate repository root containing src/."
    )

repository_root_str = str(repository_root)

if repository_root_str not in sys.path:
    sys.path.insert(0, repository_root_str)

print("Repository root:", repository_root)
print("Canonical source package:", repository_root / "src")

from src.bootstrap import bootstrap_project

bootstrap_project()

import src

assert src.__name__ == "src"

print("Bootstrap validation: PASSED")
print("Canonical namespace: src.*")

# COMMAND ----------

import torch

print("=" * 72)
print("PYTORCH RUNTIME VERIFICATION")
print("=" * 72)
print(f"PyTorch version : {torch.__version__}")
print(f"CUDA available  : {torch.cuda.is_available()}")
print("PyTorch status  : READY")
print("=" * 72)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# Machine Learning Runtime Dependencies
# =============================================================================

import importlib.util

TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None

print("=" * 72)
print("ML RUNTIME DEPENDENCY CHECK")
print("=" * 72)
print(f"PyTorch available : {TORCH_AVAILABLE}")

if not TORCH_AVAILABLE:
    raise RuntimeError(
        "PyTorch is required for complete Enterprise Forecast Algorithm "
        "validation. Configure the validation runtime with PyTorch before "
        "executing the LSTM validation suite."
    )

print("ML runtime status : READY")
print("=" * 72)

# COMMAND ----------

# Forecast package validation

from src.forecast import (
    DatasetSplit,
    ForecastDatasetBundle,
    ForecastDatasetMetadata,
    ForecastDatasetPersistence,
    ForecastDatasetService,
    ForecastDatasetSplitter,
    ForecastDatasetSummary,
    ForecastPersistenceResult,
)

print("=" * 70)
print("FORECAST PACKAGE VALIDATION")
print("=" * 70)

print("ForecastDatasetService      :", ForecastDatasetService)
print("ForecastDatasetSplitter     :", ForecastDatasetSplitter)
print("ForecastDatasetPersistence  :", ForecastDatasetPersistence)
print("ForecastDatasetBundle       :", ForecastDatasetBundle)
print("DatasetSplit                :", DatasetSplit)
print("ForecastPersistenceResult   :", ForecastPersistenceResult)

print("=" * 70)
print("Forecast package imports: PASSED")

# COMMAND ----------

from src.forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelLifecycle,
    ForecastModelMetadataProvider,
    ForecastModelState,
)

print("contracts.py import: PASSED")
print("Model states:", [state.value for state in ForecastModelState])
print("Model categories:", [category.value for category in ForecastModelCategory])
print(
    "Capability count:",
    len(ForecastModelCapability),
)

assert ForecastModelState.CREATED.value == "CREATED"
assert ForecastModelCategory.MACHINE_LEARNING.value == "MACHINE_LEARNING"
assert ForecastModelCapability.POINT_FORECAST.value == "POINT_FORECAST"
assert BaseForecastModel.__abstractmethods__

print("contracts.py validation: PASSED")

# COMMAND ----------

from src.forecast.modeling.contexts import (
    ForecastTrainingContext,
    ForecastPredictionContext,
    ForecastEvaluationContext,
)

training = ForecastTrainingContext(
    training_dataset="train",
    validation_dataset="validation",
    feature_columns=("orders", "weekday", "holiday"),
    target_column="workload",
    forecast_horizon=7,
)

prediction = ForecastPredictionContext(
    prediction_dataset="prediction",
    forecast_horizon=7,
)

evaluation = ForecastEvaluationContext(
    actual_values=[10, 20, 30],
    predicted_values=[11, 18, 29],
    metric="RMSE",
)

print("Training Context:", training)
print("Prediction Context:", prediction)
print("Evaluation Context:", evaluation)

assert training.forecast_horizon == 7
assert prediction.forecast_horizon == 7
assert evaluation.metric == "RMSE"

print("Training dict:", training.to_dict())

print("contexts.py validation: PASSED")

# COMMAND ----------

from datetime import datetime, timezone

from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import ForecastModelCategory


artifact = ForecastArtifact(
    model_name="enterprise_random_forest",
    model_version="1.0.0",
    model_category=ForecastModelCategory.MACHINE_LEARNING,
    algorithm="random_forest",
    storage_uri="s3://example/models/random_forest/v1",
    feature_columns=("weekday", "lag_1", "rolling_mean_7"),
    target_column="workload",
    forecast_horizon=7,
    hyperparameters={
        "n_estimators": 200,
        "random_state": 42,
    },
    metrics={
        "mae": 12.5,
        "rmse": 17.2,
    },
    status=ForecastArtifactStatus.PERSISTED,
    training_dataset_id="forecast_dataset",
    training_dataset_version="2.3.0",
    experiment_id="implementation-11-validation",
    trained_at=datetime.now(timezone.utc),
    metadata={
        "environment": "development",
    },
)

artifact_dict = artifact.to_dict()

print("Artifact:", artifact)
print("Artifact dictionary:", artifact_dict)

assert artifact.artifact_id
assert artifact.model_category == ForecastModelCategory.MACHINE_LEARNING
assert artifact.status == ForecastArtifactStatus.PERSISTED
assert artifact.forecast_horizon == 7
assert artifact_dict["model_category"] == "MACHINE_LEARNING"
assert artifact_dict["status"] == "PERSISTED"
assert artifact_dict["feature_columns"] == [
    "weekday",
    "lag_1",
    "rolling_mean_7",
]
assert artifact_dict["metrics"]["rmse"] == 17.2
assert artifact_dict["created_at"].endswith("+00:00")

print("artifacts.py validation: PASSED")

# COMMAND ----------

from src.forecast.modeling.configuration import (
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


configuration = EnterpriseForecastConfiguration(
    forecast=ForecastConfiguration(
        forecast_horizon_days=7,
        granularity=ForecastGranularity.DAILY,
        datetime_column="forecast_date",
        target_column="workload",
        feature_columns=(
            "weekday",
            "lag_1",
            "rolling_mean_7",
        ),
        minimum_training_records=180,
    ),
    training=TrainingConfiguration(
        enabled_models=(
            "naive_last_value",
            "linear_regression",
            "random_forest",
        ),
        cross_validation_folds=4,
        model_parameters={
            "random_forest": {
                "n_estimators": 200,
                "max_depth": 12,
            },
        },
    ),
    evaluation=EvaluationConfiguration(
        primary_metric=ForecastEvaluationMetric.WAPE,
        champion_selection_mode=ChampionSelectionMode.MINIMIZE,
    ),
    registry=RegistryConfiguration(
        enabled=True,
        registry_uri="s3://example/metadata/model-registry",
        artifact_root_uri="s3://example/models",
    ),
    runtime=RuntimeConfiguration(
        experiment_name="implementation-11-validation",
        execution_environment="development",
        execution_tags={
            "implementation": "11",
            "platform_version": "2.4.0",
        },
    ),
)

configuration_dict = configuration.to_dict()

print("Configuration:", configuration)
print("Configuration dictionary:", configuration_dict)

assert configuration.forecast.forecast_horizon_days == 7
assert configuration.forecast.granularity == ForecastGranularity.DAILY
assert configuration.training.cross_validation_folds == 4
assert configuration.evaluation.primary_metric == (
    ForecastEvaluationMetric.WAPE
)
assert configuration.registry.enabled is True
assert configuration.runtime.execution_environment == "development"

assert configuration_dict["forecast"]["granularity"] == "DAILY"
assert configuration_dict["evaluation"]["primary_metric"] == "WAPE"
assert configuration_dict["evaluation"][
    "champion_selection_mode"
] == "MINIMIZE"
assert configuration_dict["training"]["enabled_models"] == [
    "naive_last_value",
    "linear_regression",
    "random_forest",
]
assert configuration_dict["training"]["model_parameters"][
    "random_forest"
]["n_estimators"] == 200

assert (
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION
    .forecast.forecast_horizon_days
    == 14
)

print("configuration.py validation: PASSED")

# COMMAND ----------

from src.forecast.modeling.exceptions import (
    ForecastConfigurationError,
    ForecastModelingError,
    ForecastModelNotFoundError,
    ForecastPersistenceError,
    ForecastTrainingError,
    UnsupportedForecastModelError,
)


root_cause = ValueError("invalid training matrix")

training_error = ForecastTrainingError(
    "Random Forest training failed.",
    context={
        "model_name": "random_forest",
        "forecast_horizon": 7,
    },
    cause=root_cause,
)

error_dict = training_error.to_dict()

print("Training error:", training_error)
print("Training error dictionary:", error_dict)

assert isinstance(training_error, ForecastModelingError)
assert training_error.error_code == "FORECAST_TRAINING_ERROR"
assert training_error.context["model_name"] == "random_forest"
assert error_dict["error_type"] == "ForecastTrainingError"
assert error_dict["cause_type"] == "ValueError"
assert error_dict["cause_message"] == "invalid training matrix"

assert (
    ForecastConfigurationError("invalid").error_code
    == "FORECAST_CONFIGURATION_ERROR"
)
assert (
    ForecastPersistenceError("failed").error_code
    == "FORECAST_PERSISTENCE_ERROR"
)
assert (
    ForecastModelNotFoundError("missing").error_code
    == "FORECAST_MODEL_NOT_FOUND"
)
assert (
    UnsupportedForecastModelError("unsupported").error_code
    == "UNSUPPORTED_FORECAST_MODEL"
)

print("exceptions.py validation: PASSED")

# COMMAND ----------

from datetime import datetime, timezone

from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


training_result = ForecastTrainingResult(
    model_name="enterprise_random_forest",
    model_version="1.0.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={
        "mae": 12.5,
        "rmse": 17.2,
    },
    hyperparameters={
        "n_estimators": 200,
    },
    training_records=700,
    validation_records=150,
    training_duration_seconds=8.4,
    feature_columns=("weekday", "lag_1"),
    target_column="workload",
    forecast_horizon=7,
    completed_at=datetime.now(timezone.utc),
)

prediction_result = ForecastPredictionResult(
    model_name="enterprise_random_forest",
    model_version="1.0.0",
    status=ForecastExecutionStatus.SUCCESS,
    predictions=(101.0, 106.0, 111.0),
    forecast_horizon=3,
    prediction_timestamps=(
        datetime(2026, 8, 2, tzinfo=timezone.utc),
        datetime(2026, 8, 3, tzinfo=timezone.utc),
        datetime(2026, 8, 4, tzinfo=timezone.utc),
    ),
    lower_bounds=(95.0, 100.0, 104.0),
    upper_bounds=(108.0, 113.0, 119.0),
)

evaluation_result = ForecastEvaluationResult(
    model_name="enterprise_random_forest",
    model_version="1.0.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={
        "MAE": 12.5,
        "RMSE": 17.2,
        "WAPE": 8.1,
    },
    primary_metric="WAPE",
    primary_metric_value=8.1,
    evaluation_records=150,
    rank=1,
    champion=True,
    feature_importance={
        "lag_1": 0.68,
        "weekday": 0.32,
    },
)

training_dict = training_result.to_dict()
prediction_dict = prediction_result.to_dict()
evaluation_dict = evaluation_result.to_dict()

print("Training result:", training_result)
print("Prediction result:", prediction_result)
print("Evaluation result:", evaluation_result)

assert training_result.succeeded is True
assert prediction_result.succeeded is True
assert evaluation_result.succeeded is True

assert training_dict["status"] == "SUCCESS"
assert training_dict["metrics"]["rmse"] == 17.2
assert prediction_dict["predictions"] == [101.0, 106.0, 111.0]
assert prediction_dict["prediction_timestamps"][0].startswith(
    "2026-08-02"
)
assert evaluation_dict["primary_metric"] == "WAPE"
assert evaluation_dict["champion"] is True
assert evaluation_dict["feature_importance"]["lag_1"] == 0.68

failed_result = ForecastTrainingResult(
    model_name="failed_model",
    model_version="1.0.0",
    status=ForecastExecutionStatus.FAILED,
    error={
        "error_code": "FORECAST_TRAINING_ERROR",
        "message": "Training failed.",
    },
)

assert failed_result.succeeded is False
assert failed_result.to_dict()["error"]["error_code"] == (
    "FORECAST_TRAINING_ERROR"
)

print("results.py validation: PASSED")

# COMMAND ----------

from collections.abc import Mapping
from os import PathLike
from typing import Any, Self

from src.forecast.modeling.artifacts import ForecastArtifact
from src.forecast.modeling.configuration import (
    EnterpriseForecastConfiguration,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastConfigurationError,
    ForecastModelNotFoundError,
)
from src.forecast.modeling.factory import (
    ForecastModelFactory,
    register_forecast_model,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


class ValidationForecastModel(BaseForecastModel):
    """Minimal concrete model used only for factory validation."""

    def __init__(
        self,
        configuration: EnterpriseForecastConfiguration,
    ) -> None:
        self.configuration = configuration
        self._state = ForecastModelState.CREATED

    @property
    def model_name(self) -> str:
        return "validation_forecast_model"

    @property
    def model_version(self) -> str:
        return "1.0.0"

    @property
    def model_category(self) -> ForecastModelCategory:
        return ForecastModelCategory.BASELINE

    @property
    def capabilities(
        self,
    ) -> frozenset[ForecastModelCapability]:
        return frozenset({
            ForecastModelCapability.POINT_FORECAST,
        })

    @property
    def state(self) -> ForecastModelState:
        return self._state

    def initialize(self) -> None:
        self._state = ForecastModelState.INITIALIZED

    def train(
        self,
        context: ForecastTrainingContext,
    ) -> ForecastTrainingResult:
        self._state = ForecastModelState.TRAINED
        return ForecastTrainingResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            feature_columns=context.feature_columns,
            target_column=context.target_column,
            forecast_horizon=context.forecast_horizon,
        )

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        return ForecastPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            predictions=(100.0,),
            forecast_horizon=context.forecast_horizon,
        )

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        return ForecastEvaluationResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            metrics={context.metric: 0.0},
            primary_metric=context.metric,
            primary_metric_value=0.0,
        )

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        raise NotImplementedError(
            "Persistence is not required for factory validation."
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        raise NotImplementedError(
            "Loading is not required for factory validation."
        )

    def get_metadata(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
        }


ForecastModelFactory.clear()


@register_forecast_model(
    model_key="validation-model",
    display_name="Validation Forecast Model",
    category=ForecastModelCategory.BASELINE,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
    }),
    implementation_version="1.0.0",
    description="Factory validation model.",
)
def build_validation_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    return ValidationForecastModel(configuration)


assert ForecastModelFactory.is_supported("validation_model")
assert ForecastModelFactory.is_supported("validation-model")
assert ForecastModelFactory.supported_models() == (
    "validation_model",
)

registration = ForecastModelFactory.get_registration(
    "validation_model"
)
registration_dict = registration.to_dict()

assert registration.model_key == "validation_model"
assert registration.category == ForecastModelCategory.BASELINE
assert registration_dict["category"] == "BASELINE"
assert registration_dict["capabilities"] == ["POINT_FORECAST"]

model = ForecastModelFactory.create("validation_model")

assert isinstance(model, BaseForecastModel)
assert model.model_name == "validation_forecast_model"
assert model.state == ForecastModelState.CREATED

model.initialize()

assert model.state == ForecastModelState.INITIALIZED
assert model.is_initialized is True

training_result = model.train(
    ForecastTrainingContext(
        training_dataset="training",
        feature_columns=("lag_1",),
        target_column="workload",
        forecast_horizon=7,
    )
)

assert training_result.succeeded is True
assert model.is_trained is True

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 1
assert catalog[0]["model_key"] == "validation_model"

try:
    ForecastModelFactory.create("missing_model")
except ForecastModelNotFoundError as exc:
    assert exc.error_code == "FORECAST_MODEL_NOT_FOUND"
else:
    raise AssertionError(
        "Expected ForecastModelNotFoundError."
    )

try:
    ForecastModelFactory.register(
        model_key="validation_model",
        builder=build_validation_model,
        display_name="Duplicate",
        category=ForecastModelCategory.BASELINE,
    )
except ForecastConfigurationError as exc:
    assert exc.error_code == "FORECAST_CONFIGURATION_ERROR"
else:
    raise AssertionError(
        "Expected ForecastConfigurationError."
    )

removed = ForecastModelFactory.unregister(
    "validation_model"
)

assert removed.model_key == "validation_model"
assert ForecastModelFactory.supported_models() == ()

print("factory.py validation: PASSED")

# COMMAND ----------

from src.forecast.modeling import (
    BaseForecastModel,
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION,
    EnterpriseForecastConfiguration,
    ForecastArtifact,
    ForecastConfiguration,
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastModelFactory,
    ForecastModelState,
    ForecastPredictionResult,
    ForecastTrainingContext,
    ForecastTrainingResult,
)


assert BaseForecastModel.__abstractmethods__
assert ForecastModelState.CREATED.value == "CREATED"
assert ForecastExecutionStatus.SUCCESS.value == "SUCCESS"
assert isinstance(
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION,
    EnterpriseForecastConfiguration,
)
assert (
    DEFAULT_ENTERPRISE_FORECAST_CONFIGURATION
    .forecast.forecast_horizon_days
    == 14
)
assert ForecastModelFactory.supported_models() == ()

training_context = ForecastTrainingContext(
    training_dataset="training",
    feature_columns=("lag_1",),
    target_column="workload",
    forecast_horizon=7,
)

assert training_context.forecast_horizon == 7

print("src.forecast.modeling package import: PASSED")
print("src.forecast.modeling __init__.py validation: PASSED")

# COMMAND ----------

import importlib
import inspect
import sys

module_name = "src.forecast.algorithms.base.forecast_model"

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

forecast_model_module = importlib.import_module(module_name)

EnterpriseForecastModel = (
    forecast_model_module.EnterpriseForecastModel
)

print("Loaded from:")
print(forecast_model_module.__file__)

print("\nAbstract methods:")
print(EnterpriseForecastModel.__abstractmethods__)

source = inspect.getsource(EnterpriseForecastModel)

assert "def model_name(self)" in source
assert "def model_version(self)" in source
assert "def model_category(self)" in source
assert "def capabilities(self)" in source
assert "def get_metadata(self)" in source

assert "model_name" not in EnterpriseForecastModel.__abstractmethods__
assert "model_version" not in EnterpriseForecastModel.__abstractmethods__
assert "model_category" not in EnterpriseForecastModel.__abstractmethods__
assert "capabilities" not in EnterpriseForecastModel.__abstractmethods__
assert "get_metadata" not in EnterpriseForecastModel.__abstractmethods__

print("Updated EnterpriseForecastModel source: PASSED")

# COMMAND ----------

import importlib
from collections.abc import Mapping
from os import PathLike
from typing import Any, Self

import src.forecast.algorithms.base.forecast_model as forecast_model_module

from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


# Reload because Databricks caches previously imported Python modules.
importlib.reload(forecast_model_module)

EnterpriseForecastModel = (
    forecast_model_module.EnterpriseForecastModel
)


class DummyForecastModel(EnterpriseForecastModel):
    """Concrete model used only for base-class validation."""

    def __init__(self) -> None:
        super().__init__(
            model_key="dummy",
            display_name="Dummy Model",
            category=ForecastModelCategory.BASELINE,
            algorithm="dummy",
            version="1.0.0",
            capabilities=frozenset({
                ForecastModelCapability.POINT_FORECAST,
            }),
        )

    def train(
        self,
        context: ForecastTrainingContext,
    ) -> ForecastTrainingResult:
        self._state = ForecastModelState.TRAINING
        self._training_context = context
        self._state = ForecastModelState.TRAINED

        return ForecastTrainingResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            training_records=1,
            feature_columns=context.feature_columns,
            target_column=context.target_column,
            forecast_horizon=context.forecast_horizon,
        )

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        self._state = ForecastModelState.PREDICTING
        self._prediction_context = context
        self._state = ForecastModelState.TRAINED

        return ForecastPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            predictions=(1.0, 2.0, 3.0),
            forecast_horizon=context.forecast_horizon,
        )

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        self._state = ForecastModelState.EVALUATING
        self._evaluation_context = context
        self._state = ForecastModelState.EVALUATED

        return ForecastEvaluationResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            metrics={
                context.metric: 0.0,
            },
            primary_metric=context.metric,
            primary_metric_value=0.0,
        )

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        artifact = ForecastArtifact(
            model_name=self.model_name,
            model_version=self.model_version,
            model_category=self.model_category,
            algorithm=self.algorithm,
            storage_uri=str(destination),
            feature_columns=(
                self.training_context.feature_columns
                if self.training_context is not None
                else ()
            ),
            target_column=(
                self.training_context.target_column
                if self.training_context is not None
                else ""
            ),
            forecast_horizon=(
                self.training_context.forecast_horizon
                if self.training_context is not None
                else 1
            ),
            status=ForecastArtifactStatus.PERSISTED,
        )

        self._artifact = artifact
        self._state = ForecastModelState.SAVED

        return artifact

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        model = cls()
        model._state = ForecastModelState.LOADED
        return model

    def serialize(self) -> Mapping[str, Any]:
        return {
            "model_key": self.model_key,
            "algorithm": self.algorithm,
            "version": self.version,
            "state": self.state.value,
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        model = cls()

        state_value = payload.get(
            "state",
            ForecastModelState.CREATED.value,
        )

        model._state = ForecastModelState(state_value)

        return model


print(
    "EnterpriseForecastModel abstract methods:",
    EnterpriseForecastModel.__abstractmethods__,
)

model = DummyForecastModel()

assert model.model_key == "dummy"
assert model.display_name == "Dummy Model"
assert model.model_name == "Dummy Model"
assert model.algorithm == "dummy"
assert model.model_version == "1.0.0"
assert model.model_category == ForecastModelCategory.BASELINE
assert model.state == ForecastModelState.CREATED
assert model.supports(
    ForecastModelCapability.POINT_FORECAST
)

model.initialize()

assert model.state == ForecastModelState.INITIALIZED
assert model.is_initialized is True

training_context = ForecastTrainingContext(
    training_dataset="train",
    feature_columns=("orders",),
    target_column="workload",
    forecast_horizon=7,
)

training_result = model.train(training_context)

assert training_result.succeeded is True
assert model.training_context is not None
assert model.training_context.forecast_horizon == 7
assert model.state == ForecastModelState.TRAINED
assert model.is_trained is True

prediction_context = ForecastPredictionContext(
    prediction_dataset="prediction",
    forecast_horizon=3,
)

prediction_result = model.predict(prediction_context)

assert prediction_result.succeeded is True
assert prediction_result.predictions == (1.0, 2.0, 3.0)
assert model.prediction_context is not None

evaluation_context = ForecastEvaluationContext(
    actual_values=(1.0, 2.0, 3.0),
    predicted_values=(1.0, 2.0, 3.0),
    metric="RMSE",
)

evaluation_result = model.evaluate(evaluation_context)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric_value == 0.0
assert model.evaluation_context is not None
assert model.state == ForecastModelState.EVALUATED

artifact = model.save(
    "s3://example/models/dummy/v1"
)

assert artifact.status == ForecastArtifactStatus.PERSISTED
assert artifact.storage_uri == "s3://example/models/dummy/v1"
assert model.artifact is not None
assert model.state == ForecastModelState.SAVED

metadata = model.get_metadata()

assert metadata["model_key"] == "dummy"
assert metadata["model_category"] == "BASELINE"
assert metadata["capabilities"] == ["POINT_FORECAST"]
assert metadata["artifact_id"] == artifact.artifact_id

payload = model.serialize()
restored_model = DummyForecastModel.deserialize(payload)

assert restored_model.model_key == "dummy"
assert restored_model.state == ForecastModelState.SAVED

loaded_model = DummyForecastModel.load(
    "s3://example/models/dummy/v1"
)

assert loaded_model.state == ForecastModelState.LOADED

model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None

print("forecast_model.py validation: PASSED")

# COMMAND ----------

import importlib
import sys
from collections.abc import Mapping
from os import PathLike
from typing import Any, Self

module_name = "src.forecast.algorithms.base.estimator"

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

estimator_module = importlib.import_module(module_name)
EnterpriseEstimator = estimator_module.EnterpriseEstimator


class DummyEnterpriseEstimator(EnterpriseEstimator):
    """Concrete estimator used only for package validation."""

    def __init__(self) -> None:
        super().__init__(
            estimator_name="dummy_estimator",
            framework="validation",
            version="1.0.0",
            parameters={
                "constant_prediction": 42.0,
            },
        )
        self._prediction_value = 42.0

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        feature_count = len(features)
        target_count = len(target)

        self.mark_fitted(
            training_metadata={
                "feature_record_count": feature_count,
                "target_record_count": target_count,
            }
        )

        return self

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        if not self.fitted:
            raise RuntimeError(
                "Estimator must be fitted before prediction."
            )

        return tuple(
            self._prediction_value
            for _ in range(len(features))
        )

    def serialize(self) -> Mapping[str, Any]:
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
            "prediction_value": self._prediction_value,
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        estimator = cls()

        estimator._prediction_value = float(
            payload.get("prediction_value", 42.0)
        )
        estimator._feature_names = tuple(
            payload.get("feature_names", ())
        )
        estimator._target_name = payload.get("target_name")
        estimator._initialized = bool(
            payload.get("initialized", False)
        )
        estimator._fitted = bool(
            payload.get("fitted", False)
        )
        estimator._training_metadata = dict(
            payload.get("training_metadata", {})
        )

        return estimator

    def save(
        self,
        destination: str | PathLike[str],
    ) -> None:
        self._training_metadata = {
            **self._training_metadata,
            "saved_to": str(destination),
        }

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
    ) -> Self:
        estimator = cls()
        estimator._initialized = True
        estimator._fitted = True
        estimator._training_metadata = {
            "loaded_from": str(source),
        }
        return estimator


print(
    "EnterpriseEstimator abstract methods:",
    EnterpriseEstimator.__abstractmethods__,
)

assert EnterpriseEstimator.__abstractmethods__ == frozenset({
    "fit",
    "predict",
    "serialize",
    "deserialize",
    "save",
    "load",
})

estimator = DummyEnterpriseEstimator()

assert estimator.estimator_name == "dummy_estimator"
assert estimator.framework == "validation"
assert estimator.version == "1.0.0"
assert estimator.parameters["constant_prediction"] == 42.0
assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.feature_names == ()
assert estimator.target_name is None

estimator.initialize(
    feature_names=(
        "lag_1",
        "rolling_mean_7",
    ),
    target_name="workload",
)

assert estimator.initialized is True
assert estimator.feature_names == (
    "lag_1",
    "rolling_mean_7",
)
assert estimator.target_name == "workload"

fitted_estimator = estimator.fit(
    features=[
        [10.0, 12.0],
        [11.0, 13.0],
        [12.0, 14.0],
    ],
    target=[
        100.0,
        110.0,
        120.0,
    ],
)

assert fitted_estimator is estimator
assert estimator.fitted is True
assert (
    estimator.training_metadata["feature_record_count"]
    == 3
)
assert (
    estimator.training_metadata["target_record_count"]
    == 3
)

predictions = estimator.predict(
    features=[
        [13.0, 15.0],
        [14.0, 16.0],
    ]
)

assert predictions == (42.0, 42.0)

metadata = estimator.get_metadata()

assert metadata["estimator_name"] == "dummy_estimator"
assert metadata["framework"] == "validation"
assert metadata["initialized"] is True
assert metadata["fitted"] is True
assert metadata["feature_names"] == [
    "lag_1",
    "rolling_mean_7",
]
assert metadata["target_name"] == "workload"

payload = estimator.serialize()
restored_estimator = DummyEnterpriseEstimator.deserialize(
    payload
)

assert restored_estimator.estimator_name == (
    "dummy_estimator"
)
assert restored_estimator.initialized is True
assert restored_estimator.fitted is True
assert restored_estimator.feature_names == (
    "lag_1",
    "rolling_mean_7",
)
assert restored_estimator.target_name == "workload"
assert restored_estimator.predict([[1.0, 2.0]]) == (
    42.0,
)

estimator.save(
    "s3://example/models/dummy-estimator/v1"
)

assert estimator.training_metadata["saved_to"] == (
    "s3://example/models/dummy-estimator/v1"
)

loaded_estimator = DummyEnterpriseEstimator.load(
    "s3://example/models/dummy-estimator/v1"
)

assert loaded_estimator.initialized is True
assert loaded_estimator.fitted is True
assert loaded_estimator.training_metadata[
    "loaded_from"
] == "s3://example/models/dummy-estimator/v1"

estimator.reset()

assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.feature_names == ()
assert estimator.target_name is None
assert estimator.training_metadata == {}

try:
    estimator.predict([[1.0, 2.0]])
except RuntimeError as exc:
    assert str(exc) == (
        "Estimator must be fitted before prediction."
    )
else:
    raise AssertionError(
        "Expected RuntimeError for an unfitted estimator."
    )

print("estimator.py validation: PASSED")

# COMMAND ----------

from pathlib import Path
import tempfile

from src.forecast.algorithms.base.serializer import (
    EnterpriseSerializer,
)

payload = {
    "model": "random_forest",
    "version": "1.0.0",
    "metrics": {
        "rmse": 17.2,
        "mae": 12.5,
    },
}

# ----------------------------------------------------------
# dumps / loads
# ----------------------------------------------------------

json_string = EnterpriseSerializer.dumps(payload)

assert isinstance(
    json_string,
    str,
)

loaded = EnterpriseSerializer.loads(
    json_string
)

assert loaded == payload

# ----------------------------------------------------------
# checksum
# ----------------------------------------------------------

checksum = EnterpriseSerializer.checksum(
    payload
)

assert isinstance(
    checksum,
    str,
)

assert len(checksum) == 64

# ----------------------------------------------------------
# package
# ----------------------------------------------------------

package = EnterpriseSerializer.package(
    payload
)

assert package["payload"] == payload

assert package["checksum"] == checksum

# ----------------------------------------------------------
# save/load
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:

    file_path = (
        Path(directory)
        / "model.json"
    )

    EnterpriseSerializer.save_json(
        payload,
        file_path,
    )

    assert file_path.exists()

    restored = EnterpriseSerializer.load_json(
        file_path
    )

    assert restored == payload

print("serializer.py validation: PASSED")

# COMMAND ----------

import importlib
import sys

module_names = (
    "src.forecast.algorithms.base.estimator",
    "src.forecast.algorithms.base.forecast_model",
    "src.forecast.algorithms.base.serializer",
    "src.forecast.algorithms.base",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.base import (
    EnterpriseEstimator,
    EnterpriseForecastModel,
    EnterpriseSerializer,
)


assert EnterpriseEstimator.__name__ == "EnterpriseEstimator"
assert EnterpriseForecastModel.__name__ == (
    "EnterpriseForecastModel"
)
assert EnterpriseSerializer.__name__ == (
    "EnterpriseSerializer"
)

assert EnterpriseEstimator.__abstractmethods__ == frozenset({
    "fit",
    "predict",
    "serialize",
    "deserialize",
    "save",
    "load",
})

assert EnterpriseForecastModel.__abstractmethods__ == frozenset({
    "train",
    "predict",
    "evaluate",
    "save",
    "load",
    "serialize",
    "deserialize",
})

payload = {
    "framework": "enterprise-forecast-modeling",
    "version": "2.4.0",
}

serialized = EnterpriseSerializer.dumps(payload)
restored = EnterpriseSerializer.loads(serialized)

assert restored == payload

print("src.forecast.algorithms.base package import: PASSED")
print("src.forecast.algorithms.base __init__.py validation: PASSED")

# COMMAND ----------

import importlib
import sys
import tempfile
from pathlib import Path

module_name = "src.forecast.algorithms.naive.estimator"

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

naive_estimator_module = importlib.import_module(
    module_name
)

NaiveLastValueEstimator = (
    naive_estimator_module.NaiveLastValueEstimator
)


estimator = NaiveLastValueEstimator(
    parameters={
        "strategy": "last_value",
    }
)

assert estimator.estimator_name == (
    "naive_last_value_estimator"
)
assert estimator.framework == "native_python"
assert estimator.version == "1.0.0"
assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.last_value is None

estimator.initialize(
    feature_names=(
        "lag_1",
        "weekday",
    ),
    target_name="workload",
)

assert estimator.initialized is True
assert estimator.feature_names == (
    "lag_1",
    "weekday",
)
assert estimator.target_name == "workload"

fitted_estimator = estimator.fit(
    features=[
        [90.0, 1.0],
        [95.0, 2.0],
        [100.0, 3.0],
        [110.0, 4.0],
    ],
    target=[
        100.0,
        105.0,
        112.0,
        120.0,
    ],
)

assert fitted_estimator is estimator
assert estimator.fitted is True
assert estimator.last_value == 120.0
assert estimator.training_metadata[
    "training_records"
] == 4
assert estimator.training_metadata[
    "learned_last_value"
] == 120.0

predictions_from_records = estimator.predict(
    features=[
        [120.0, 5.0],
        [120.0, 6.0],
        [120.0, 7.0],
    ]
)

assert predictions_from_records == (
    120.0,
    120.0,
    120.0,
)

predictions_from_horizon = estimator.predict(7)

assert predictions_from_horizon == (
    120.0,
    120.0,
    120.0,
    120.0,
    120.0,
    120.0,
    120.0,
)

metadata = estimator.get_metadata()

assert metadata["estimator_name"] == (
    "naive_last_value_estimator"
)
assert metadata["framework"] == "native_python"
assert metadata["initialized"] is True
assert metadata["fitted"] is True
assert metadata["feature_names"] == [
    "lag_1",
    "weekday",
]
assert metadata["target_name"] == "workload"

payload = estimator.serialize()

assert payload["last_value"] == 120.0
assert payload["fitted"] is True
assert payload["parameters"]["strategy"] == (
    "last_value"
)

restored_estimator = (
    NaiveLastValueEstimator.deserialize(payload)
)

assert restored_estimator.initialized is True
assert restored_estimator.fitted is True
assert restored_estimator.last_value == 120.0
assert restored_estimator.feature_names == (
    "lag_1",
    "weekday",
)
assert restored_estimator.predict(2) == (
    120.0,
    120.0,
)

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "naive_estimator.json"
    )

    estimator.save(artifact_path)

    assert artifact_path.exists()

    loaded_estimator = (
        NaiveLastValueEstimator.load(
            artifact_path
        )
    )

    assert loaded_estimator.fitted is True
    assert loaded_estimator.last_value == 120.0
    assert loaded_estimator.predict(3) == (
        120.0,
        120.0,
        120.0,
    )

try:
    NaiveLastValueEstimator().fit(
        features=[],
        target=[],
    )
except ValueError as exc:
    assert str(exc) == (
        "Naive estimator requires at least one target value."
    )
else:
    raise AssertionError(
        "Expected ValueError for an empty target."
    )

try:
    NaiveLastValueEstimator().fit(
        features=[[1.0], [2.0]],
        target=[10.0],
    )
except ValueError as exc:
    assert "record counts must match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for mismatched records."
    )

unfitted_estimator = NaiveLastValueEstimator()

try:
    unfitted_estimator.predict(1)
except RuntimeError as exc:
    assert str(exc) == (
        "Naive estimator must be fitted before prediction."
    )
else:
    raise AssertionError(
        "Expected RuntimeError before fitting."
    )

estimator.reset()

assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.last_value is None
assert estimator.feature_names == ()
assert estimator.target_name is None

print("naive/estimator.py validation: PASSED")

# COMMAND ----------

import importlib
import sys
import tempfile
from pathlib import Path

module_names = (
    "src.forecast.algorithms.naive.model",
    "src.forecast.algorithms.naive.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.naive.model import NaiveForecastModel
from src.forecast.modeling.artifacts import ForecastArtifactStatus
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)


model = NaiveForecastModel()

assert model.model_key == "naive_last_value"
assert model.model_name == "Naive Last-Value Forecast"
assert model.algorithm == "naive_last_value"
assert model.model_category == ForecastModelCategory.BASELINE
assert model.state == ForecastModelState.CREATED
assert model.supports(
    ForecastModelCapability.POINT_FORECAST
)
assert model.supports(
    ForecastModelCapability.MULTI_STEP_FORECAST
)

training_context = ForecastTrainingContext(
    training_dataset={
        "features": [
            [90.0, 1.0],
            [95.0, 2.0],
            [100.0, 3.0],
            [110.0, 4.0],
        ],
        "target": [
            100.0,
            105.0,
            112.0,
            120.0,
        ],
    },
    validation_dataset={
        "features": [[120.0, 5.0]],
        "target": [120.0],
    },
    feature_columns=(
        "lag_1",
        "weekday",
    ),
    target_column="workload",
    forecast_horizon=7,
    experiment_id="implementation-11-naive-validation",
)

training_result = model.train(training_context)

assert training_result.succeeded is True
assert training_result.status.value == "SUCCESS"
assert training_result.training_records == 4
assert training_result.validation_records == 2
assert training_result.forecast_horizon == 7
assert training_result.metadata[
    "learned_last_value"
] == 120.0
assert model.training_context is training_context
assert model.estimator.fitted is True
assert model.estimator.last_value == 120.0
assert model.state == ForecastModelState.TRAINED

prediction_context = ForecastPredictionContext(
    prediction_dataset=[
        [120.0, 5.0],
        [120.0, 6.0],
        [120.0, 7.0],
    ],
    forecast_horizon=3,
    metadata={
        "scenario": "validation",
    },
)

prediction_result = model.predict(prediction_context)

assert prediction_result.succeeded is True
assert prediction_result.predictions == (
    120.0,
    120.0,
    120.0,
)
assert prediction_result.forecast_horizon == 3
assert prediction_result.metadata[
    "prediction_strategy"
] == "last_value"
assert model.prediction_context is prediction_context
assert model.state == ForecastModelState.TRAINED

evaluation_context = ForecastEvaluationContext(
    actual_values=(
        118.0,
        122.0,
        120.0,
    ),
    predicted_values=prediction_result.predictions,
    metric="MAE",
    metadata={
        "split": "validation",
    },
)

evaluation_result = model.evaluate(
    evaluation_context
)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric == "MAE"
assert evaluation_result.primary_metric_value == (
    4.0 / 3.0
)
assert evaluation_result.metrics["MAE"] == (
    4.0 / 3.0
)
assert evaluation_result.evaluation_records == 3
assert model.evaluation_context is evaluation_context
assert model.state == ForecastModelState.EVALUATED

payload = model.serialize()

assert payload["model_key"] == "naive_last_value"
assert payload["estimator"]["last_value"] == 120.0
assert payload["estimator"]["fitted"] is True

restored_model = NaiveForecastModel.deserialize(
    payload
)

assert restored_model.model_key == "naive_last_value"
assert restored_model.estimator.fitted is True
assert restored_model.estimator.last_value == 120.0
assert restored_model.state == ForecastModelState.EVALUATED
assert restored_model.predict(
    ForecastPredictionContext(
        prediction_dataset=2,
        forecast_horizon=2,
    )
).predictions == (
    120.0,
    120.0,
)

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "naive_model.json"
    )

    artifact = model.save(artifact_path)

    assert artifact_path.exists()
    assert artifact.status == (
        ForecastArtifactStatus.PERSISTED
    )
    assert artifact.storage_uri == str(artifact_path)
    assert artifact.algorithm == "naive_last_value"
    assert artifact.feature_columns == (
        "lag_1",
        "weekday",
    )
    assert artifact.target_column == "workload"
    assert artifact.forecast_horizon == 7
    assert artifact.checksum
    assert model.artifact is artifact
    assert model.state == ForecastModelState.SAVED

    loaded_model = NaiveForecastModel.load(
        artifact_path,
        metadata={
            "forecast_horizon": 7,
            "environment": "validation",
        },
    )

    assert loaded_model.state == ForecastModelState.LOADED
    assert loaded_model.estimator.fitted is True
    assert loaded_model.estimator.last_value == 120.0
    assert loaded_model.artifact is not None
    assert loaded_model.artifact.storage_uri == str(
        artifact_path
    )
    assert loaded_model.artifact.metadata[
        "environment"
    ] == "validation"

    loaded_prediction = loaded_model.predict(
        ForecastPredictionContext(
            prediction_dataset=3,
            forecast_horizon=3,
        )
    )

    assert loaded_prediction.predictions == (
        120.0,
        120.0,
        120.0,
    )

try:
    NaiveForecastModel().predict(
        ForecastPredictionContext(
            prediction_dataset=1,
        )
    )
except Exception as exc:
    assert "trained or loaded" in str(exc)
else:
    raise AssertionError(
        "Expected failure before model training."
    )

model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None
assert model.estimator.initialized is False
assert model.estimator.fitted is False
assert model.estimator.last_value is None

print("naive/model.py validation: PASSED")

# COMMAND ----------

import importlib
import sys

from src.forecast.modeling.factory import ForecastModelFactory


# Isolate this package-registration validation.
ForecastModelFactory.clear()

module_names = (
    "src.forecast.algorithms.naive",
    "src.forecast.algorithms.naive.model",
    "src.forecast.algorithms.naive.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

naive_package = importlib.import_module(
    "src.forecast.algorithms.naive"
)

NaiveForecastModel = naive_package.NaiveForecastModel
NaiveLastValueEstimator = (
    naive_package.NaiveLastValueEstimator
)
build_naive_last_value_model = (
    naive_package.build_naive_last_value_model
)


# ----------------------------------------------------------
# Package exports
# ----------------------------------------------------------

assert NaiveForecastModel.__name__ == (
    "NaiveForecastModel"
)
assert NaiveLastValueEstimator.__name__ == (
    "NaiveLastValueEstimator"
)
assert callable(build_naive_last_value_model)


# ----------------------------------------------------------
# Factory registration
# ----------------------------------------------------------

assert ForecastModelFactory.is_supported(
    "naive_last_value"
)

assert ForecastModelFactory.is_supported(
    "naive-last-value"
)

assert ForecastModelFactory.supported_models() == (
    "naive_last_value",
)

registration = (
    ForecastModelFactory.get_registration(
        "naive_last_value"
    )
)

registration_dict = registration.to_dict()

assert registration.model_key == "naive_last_value"
assert registration.display_name == (
    "Naive Last-Value Forecast"
)
assert registration.category.value == "BASELINE"
assert registration.implementation_version == "1.0.0"

assert registration_dict["capabilities"] == [
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert registration_dict["metadata"][
    "framework"
] == "native_python"

assert registration_dict["metadata"][
    "algorithm_family"
] == "baseline"


# ----------------------------------------------------------
# Factory model creation
# ----------------------------------------------------------

factory_model = ForecastModelFactory.create(
    "naive_last_value"
)

assert isinstance(
    factory_model,
    NaiveForecastModel,
)
assert factory_model.model_key == "naive_last_value"
assert factory_model.algorithm == "naive_last_value"
assert factory_model.estimator.estimator_name == (
    "naive_last_value_estimator"
)


# ----------------------------------------------------------
# Catalog
# ----------------------------------------------------------

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 1
assert catalog[0]["model_key"] == (
    "naive_last_value"
)
assert catalog[0]["category"] == "BASELINE"


# ----------------------------------------------------------
# Reload idempotency
# ----------------------------------------------------------

reloaded_package = importlib.reload(
    naive_package
)

assert reloaded_package.NaiveForecastModel is not None
assert ForecastModelFactory.supported_models() == (
    "naive_last_value",
)


print("src.forecast.algorithms.naive package import: PASSED")
print("Naive factory registration: PASSED")
print("src.forecast.algorithms.naive __init__.py validation: PASSED")

# COMMAND ----------

import importlib
import sys
import tempfile
from pathlib import Path

module_name = (
    "src.forecast.algorithms.moving_average.estimator"
)

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

moving_average_module = importlib.import_module(
    module_name
)

MovingAverageEstimator = (
    moving_average_module.MovingAverageEstimator
)


# ----------------------------------------------------------
# Construction and identity
# ----------------------------------------------------------

estimator = MovingAverageEstimator(
    window_size=3,
)

assert estimator.estimator_name == (
    "moving_average_estimator"
)
assert estimator.framework == "native_python"
assert estimator.version == "1.0.0"
assert estimator.window_size == 3
assert estimator.parameters["window_size"] == 3
assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.history == ()
assert estimator.moving_average is None


# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------

estimator.initialize(
    feature_names=(
        "lag_1",
        "weekday",
    ),
    target_name="workload",
)

assert estimator.initialized is True
assert estimator.feature_names == (
    "lag_1",
    "weekday",
)
assert estimator.target_name == "workload"


# ----------------------------------------------------------
# Fit
# ----------------------------------------------------------

fitted_estimator = estimator.fit(
    features=[
        [1.0, 1.0],
        [2.0, 2.0],
        [3.0, 3.0],
        [4.0, 4.0],
        [5.0, 5.0],
    ],
    target=[
        10.0,
        20.0,
        30.0,
        40.0,
        50.0,
    ],
)

assert fitted_estimator is estimator
assert estimator.fitted is True
assert estimator.history == (
    30.0,
    40.0,
    50.0,
)
assert estimator.moving_average == 40.0
assert estimator.training_metadata[
    "training_records"
] == 5
assert estimator.training_metadata[
    "window_size"
] == 3
assert estimator.training_metadata[
    "learned_moving_average"
] == 40.0


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

prediction_from_records = estimator.predict(
    [
        [100.0],
        [101.0],
        [102.0],
    ]
)

assert prediction_from_records == (
    40.0,
    40.0,
    40.0,
)

prediction_from_count = estimator.predict(4)

assert prediction_from_count == (
    40.0,
    40.0,
    40.0,
    40.0,
)


# ----------------------------------------------------------
# Metadata and serialization
# ----------------------------------------------------------

metadata = estimator.get_metadata()

assert metadata["estimator_name"] == (
    "moving_average_estimator"
)
assert metadata["framework"] == "native_python"
assert metadata["initialized"] is True
assert metadata["fitted"] is True
assert metadata["feature_names"] == [
    "lag_1",
    "weekday",
]
assert metadata["target_name"] == "workload"

payload = estimator.serialize()

assert payload["window_size"] == 3
assert payload["history"] == [
    30.0,
    40.0,
    50.0,
]
assert payload["fitted"] is True

restored = MovingAverageEstimator.deserialize(
    payload
)

assert restored.window_size == 3
assert restored.initialized is True
assert restored.fitted is True
assert restored.history == (
    30.0,
    40.0,
    50.0,
)
assert restored.moving_average == 40.0
assert restored.predict(2) == (
    40.0,
    40.0,
)


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "moving_average_estimator.json"
    )

    estimator.save(artifact_path)

    assert artifact_path.exists()

    loaded = MovingAverageEstimator.load(
        artifact_path
    )

    assert loaded.window_size == 3
    assert loaded.fitted is True
    assert loaded.history == (
        30.0,
        40.0,
        50.0,
    )
    assert loaded.moving_average == 40.0
    assert loaded.predict(3) == (
        40.0,
        40.0,
        40.0,
    )


# ----------------------------------------------------------
# Failure validation
# ----------------------------------------------------------

try:
    MovingAverageEstimator(
        window_size=0
    )
except ValueError as exc:
    assert "greater than zero" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for window_size=0."
    )

try:
    MovingAverageEstimator(
        window_size=3
    ).fit(
        features=[
            [1.0],
            [2.0],
        ],
        target=[
            10.0,
            20.0,
        ],
    )
except ValueError as exc:
    assert "shorter than window_size" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for insufficient history."
    )

try:
    MovingAverageEstimator(
        window_size=2
    ).fit(
        features=[
            [1.0],
            [2.0],
            [3.0],
        ],
        target=[
            10.0,
            20.0,
        ],
    )
except ValueError as exc:
    assert "record counts must match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for mismatched records."
    )

unfitted = MovingAverageEstimator(
    window_size=2
)

try:
    unfitted.predict(1)
except RuntimeError as exc:
    assert str(exc) == (
        "Moving Average estimator must be fitted before prediction."
    )
else:
    raise AssertionError(
        "Expected RuntimeError before fitting."
    )


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

estimator.reset()

assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.feature_names == ()
assert estimator.target_name is None
assert estimator.training_metadata == {}
assert estimator.history == ()
assert estimator.moving_average is None

print(
    "moving_average/estimator.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
import tempfile
from pathlib import Path

module_names = (
    "src.forecast.algorithms.moving_average.model",
    "src.forecast.algorithms.moving_average.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.moving_average.model import (
    MovingAverageForecastModel,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifactStatus,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

model = MovingAverageForecastModel(
    window_size=3
)

assert model.model_key == "moving_average"
assert model.model_name == "Moving Average Forecast"
assert model.algorithm == "moving_average"
assert model.model_category == (
    ForecastModelCategory.STATISTICAL
)
assert model.window_size == 3
assert model.state == ForecastModelState.CREATED

assert model.supports(
    ForecastModelCapability.POINT_FORECAST
)
assert model.supports(
    ForecastModelCapability.MULTI_STEP_FORECAST
)


# ----------------------------------------------------------
# Training
# ----------------------------------------------------------

training_context = ForecastTrainingContext(
    training_dataset={
        "features": [
            [10.0, 1.0],
            [20.0, 2.0],
            [30.0, 3.0],
            [40.0, 4.0],
            [50.0, 5.0],
        ],
        "target": [
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
        ],
    },
    validation_dataset={
        "features": [
            [60.0, 6.0],
            [70.0, 7.0],
        ],
        "target": [
            60.0,
            70.0,
        ],
    },
    feature_columns=(
        "lag_1",
        "weekday",
    ),
    target_column="workload",
    forecast_horizon=7,
    experiment_id=(
        "implementation-11-moving-average-validation"
    ),
    metadata={
        "environment": "validation",
    },
)

training_result = model.train(
    training_context
)

assert training_result.succeeded is True
assert training_result.status.value == "SUCCESS"
assert training_result.training_records == 5
assert training_result.validation_records == 2
assert training_result.forecast_horizon == 7

assert training_result.metadata[
    "window_size"
] == 3

assert training_result.metadata[
    "retained_history"
] == [
    30.0,
    40.0,
    50.0,
]

assert training_result.metadata[
    "learned_moving_average"
] == 40.0

assert model.training_context is training_context
assert model.estimator.fitted is True
assert model.estimator.history == (
    30.0,
    40.0,
    50.0,
)
assert model.estimator.moving_average == 40.0
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

prediction_context = ForecastPredictionContext(
    prediction_dataset=[
        [60.0, 6.0],
        [70.0, 7.0],
        [80.0, 1.0],
    ],
    forecast_horizon=3,
    metadata={
        "scenario": "validation",
    },
)

prediction_result = model.predict(
    prediction_context
)

assert prediction_result.succeeded is True
assert prediction_result.predictions == (
    40.0,
    40.0,
    40.0,
)
assert prediction_result.forecast_horizon == 3
assert prediction_result.metadata[
    "prediction_strategy"
] == "moving_average"
assert prediction_result.metadata[
    "window_size"
] == 3
assert prediction_result.metadata[
    "forecast_value"
] == 40.0

assert model.prediction_context is prediction_context
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Evaluation
# ----------------------------------------------------------

evaluation_context = ForecastEvaluationContext(
    actual_values=(
        38.0,
        42.0,
        40.0,
    ),
    predicted_values=(
        40.0,
        40.0,
        40.0,
    ),
    metric="MAE",
    metadata={
        "split": "validation",
    },
)

evaluation_result = model.evaluate(
    evaluation_context
)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric == "MAE"
assert evaluation_result.primary_metric_value == (
    4.0 / 3.0
)
assert evaluation_result.metrics["MAE"] == (
    4.0 / 3.0
)
assert evaluation_result.evaluation_records == 3
assert evaluation_result.metadata[
    "window_size"
] == 3
assert model.evaluation_context is evaluation_context
assert model.state == ForecastModelState.EVALUATED


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

payload = model.serialize()

assert payload["model_key"] == "moving_average"
assert payload["window_size"] == 3
assert payload["estimator"]["history"] == [
    30.0,
    40.0,
    50.0,
]
assert payload["estimator"]["fitted"] is True

restored_model = (
    MovingAverageForecastModel.deserialize(
        payload
    )
)

assert restored_model.model_key == "moving_average"
assert restored_model.window_size == 3
assert restored_model.estimator.fitted is True
assert restored_model.estimator.history == (
    30.0,
    40.0,
    50.0,
)
assert restored_model.estimator.moving_average == 40.0
assert restored_model.state == (
    ForecastModelState.EVALUATED
)

restored_prediction = restored_model.predict(
    ForecastPredictionContext(
        prediction_dataset=2,
        forecast_horizon=2,
    )
)

assert restored_prediction.predictions == (
    40.0,
    40.0,
)


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "moving_average_model.json"
    )

    artifact = model.save(
        artifact_path
    )

    assert artifact_path.exists()
    assert artifact.status == (
        ForecastArtifactStatus.PERSISTED
    )
    assert artifact.storage_uri == str(
        artifact_path
    )
    assert artifact.algorithm == "moving_average"
    assert artifact.feature_columns == (
        "lag_1",
        "weekday",
    )
    assert artifact.target_column == "workload"
    assert artifact.forecast_horizon == 7
    assert artifact.hyperparameters[
        "window_size"
    ] == 3
    assert artifact.checksum
    assert model.artifact is artifact
    assert model.state == ForecastModelState.SAVED

    loaded_model = (
        MovingAverageForecastModel.load(
            artifact_path,
            metadata={
                "forecast_horizon": 7,
                "environment": "validation",
            },
        )
    )

    assert loaded_model.state == (
        ForecastModelState.LOADED
    )
    assert loaded_model.window_size == 3
    assert loaded_model.estimator.fitted is True
    assert loaded_model.estimator.history == (
        30.0,
        40.0,
        50.0,
    )
    assert loaded_model.estimator.moving_average == 40.0
    assert loaded_model.artifact is not None
    assert loaded_model.artifact.storage_uri == str(
        artifact_path
    )
    assert loaded_model.artifact.metadata[
        "environment"
    ] == "validation"

    loaded_prediction = loaded_model.predict(
        ForecastPredictionContext(
            prediction_dataset=3,
            forecast_horizon=3,
        )
    )

    assert loaded_prediction.predictions == (
        40.0,
        40.0,
        40.0,
    )


# ----------------------------------------------------------
# Failure behavior
# ----------------------------------------------------------

try:
    MovingAverageForecastModel(
        window_size=3
    ).predict(
        ForecastPredictionContext(
            prediction_dataset=1,
        )
    )
except Exception as exc:
    assert "trained or loaded" in str(exc)
else:
    raise AssertionError(
        "Expected failure before model training."
    )

from src.forecast.modeling.exceptions import ForecastTrainingError


try:
    MovingAverageForecastModel(
        window_size=4
    ).train(
        ForecastTrainingContext(
            training_dataset=[
                10.0,
                20.0,
                30.0,
            ],
            target_column="workload",
        )
    )

except ForecastTrainingError as exc:
    assert exc.error_code == "FORECAST_TRAINING_ERROR"
    assert "Moving Average forecast model training failed" in str(exc)

    assert isinstance(
        exc.__cause__,
        ValueError,
    )
    assert "shorter than window_size" in str(
        exc.__cause__
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for insufficient history."
    )

# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None
assert model.estimator.initialized is False
assert model.estimator.fitted is False
assert model.estimator.history == ()
assert model.estimator.moving_average is None

print(
    "moving_average/model.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

from src.forecast.modeling.factory import (
    ForecastModelFactory,
)


# ----------------------------------------------------------
# Isolate and rebuild completed registrations
# ----------------------------------------------------------

ForecastModelFactory.clear()

module_names = (
    "src.forecast.algorithms.naive",
    "src.forecast.algorithms.moving_average",
    "src.forecast.algorithms.moving_average.model",
    "src.forecast.algorithms.moving_average.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

naive_package = importlib.import_module(
    "src.forecast.algorithms.naive"
)

moving_average_package = importlib.import_module(
    "src.forecast.algorithms.moving_average"
)


MovingAverageForecastModel = (
    moving_average_package.MovingAverageForecastModel
)

MovingAverageEstimator = (
    moving_average_package.MovingAverageEstimator
)

build_moving_average_model = (
    moving_average_package.build_moving_average_model
)

DEFAULT_WINDOW_SIZE = (
    moving_average_package.DEFAULT_WINDOW_SIZE
)


# ----------------------------------------------------------
# Package exports
# ----------------------------------------------------------

assert MovingAverageForecastModel.__name__ == (
    "MovingAverageForecastModel"
)

assert MovingAverageEstimator.__name__ == (
    "MovingAverageEstimator"
)

assert callable(build_moving_average_model)

assert DEFAULT_WINDOW_SIZE == 3


# ----------------------------------------------------------
# Factory registration
# ----------------------------------------------------------

assert ForecastModelFactory.is_supported(
    "moving_average"
)

assert ForecastModelFactory.is_supported(
    "moving-average"
)

assert ForecastModelFactory.is_supported(
    "naive_last_value"
)

assert ForecastModelFactory.supported_models() == (
    "moving_average",
    "naive_last_value",
)


registration = (
    ForecastModelFactory.get_registration(
        "moving_average"
    )
)

registration_dict = registration.to_dict()

assert registration.model_key == "moving_average"

assert registration.display_name == (
    "Moving Average Forecast"
)

assert registration.category.value == (
    "STATISTICAL"
)

assert registration.implementation_version == (
    "1.0.0"
)

assert registration_dict["capabilities"] == [
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert registration_dict["metadata"][
    "framework"
] == "native_python"

assert registration_dict["metadata"][
    "algorithm_family"
] == "statistical"

assert registration_dict["metadata"][
    "default_window_size"
] == 3


# ----------------------------------------------------------
# Factory creation using default configuration
# ----------------------------------------------------------

factory_model = ForecastModelFactory.create(
    "moving_average"
)

assert isinstance(
    factory_model,
    MovingAverageForecastModel,
)

assert factory_model.model_key == (
    "moving_average"
)

assert factory_model.algorithm == (
    "moving_average"
)

assert factory_model.window_size == 3

assert factory_model.estimator.estimator_name == (
    "moving_average_estimator"
)

assert factory_model.estimator.parameters[
    "window_size"
] == 3


# ----------------------------------------------------------
# Alias creation
# ----------------------------------------------------------

alias_model = ForecastModelFactory.create(
    "moving-average"
)

assert isinstance(
    alias_model,
    MovingAverageForecastModel,
)

assert alias_model.window_size == 3


# ----------------------------------------------------------
# Catalog
# ----------------------------------------------------------

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 2

catalog_by_key = {
    item["model_key"]: item
    for item in catalog
}

assert set(catalog_by_key) == {
    "moving_average",
    "naive_last_value",
}

assert catalog_by_key[
    "moving_average"
]["category"] == "STATISTICAL"

assert catalog_by_key[
    "naive_last_value"
]["category"] == "BASELINE"


# ----------------------------------------------------------
# Reload idempotency
# ----------------------------------------------------------

reloaded_package = importlib.reload(
    moving_average_package
)

assert (
    reloaded_package.MovingAverageForecastModel
    is not None
)

assert ForecastModelFactory.supported_models() == (
    "moving_average",
    "naive_last_value",
)


print(
    "src.forecast.algorithms.moving_average "
    "package import: PASSED"
)

print(
    "Moving Average factory registration: PASSED"
)

print(
    "src.forecast.algorithms.moving_average "
    "__init__.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
import tempfile
from pathlib import Path

module_name = (
    "src.forecast.algorithms.linear_regression.estimator"
)

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

linear_regression_module = importlib.import_module(
    module_name
)

LinearRegressionEstimator = (
    linear_regression_module.LinearRegressionEstimator
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

estimator = LinearRegressionEstimator(
    fit_intercept=True,
)

assert estimator.estimator_name == (
    "linear_regression_estimator"
)
assert estimator.framework == "numpy"
assert estimator.version == "1.0.0"
assert estimator.fit_intercept is True
assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.intercept == 0.0
assert estimator.coefficients == ()
assert estimator.rank is None
assert estimator.residual_sum_of_squares is None


# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------

estimator.initialize(
    feature_names=(
        "lag_1",
        "weekday",
    ),
    target_name="workload",
)

assert estimator.initialized is True
assert estimator.feature_names == (
    "lag_1",
    "weekday",
)
assert estimator.target_name == "workload"


# ----------------------------------------------------------
# Fit
#
# y = 5 + 2*x1 + 3*x2
# ----------------------------------------------------------

features = [
    [1.0, 0.0],
    [2.0, 1.0],
    [3.0, 0.0],
    [4.0, 1.0],
    [5.0, 0.0],
    [6.0, 1.0],
]

target = [
    7.0,
    12.0,
    11.0,
    16.0,
    15.0,
    20.0,
]

fitted_estimator = estimator.fit(
    features=features,
    target=target,
)

assert fitted_estimator is estimator
assert estimator.fitted is True

assert math.isclose(
    estimator.intercept,
    5.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert len(estimator.coefficients) == 2

assert math.isclose(
    estimator.coefficients[0],
    2.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    estimator.coefficients[1],
    3.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert estimator.rank == 3

assert math.isclose(
    estimator.residual_sum_of_squares,
    0.0,
    abs_tol=1e-20,
)

assert estimator.training_metadata[
    "training_records"
] == 6

assert estimator.training_metadata[
    "feature_count"
] == 2


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

predictions = estimator.predict(
    [
        [7.0, 0.0],
        [8.0, 1.0],
    ]
)

assert len(predictions) == 2

assert math.isclose(
    predictions[0],
    19.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    predictions[1],
    24.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)


# ----------------------------------------------------------
# Metadata and serialization
# ----------------------------------------------------------

metadata = estimator.get_metadata()

assert metadata["estimator_name"] == (
    "linear_regression_estimator"
)
assert metadata["framework"] == "numpy"
assert metadata["initialized"] is True
assert metadata["fitted"] is True
assert metadata["feature_names"] == [
    "lag_1",
    "weekday",
]
assert metadata["target_name"] == "workload"

payload = estimator.serialize()

assert payload["fit_intercept"] is True
assert len(payload["coefficients"]) == 2
assert payload["fitted"] is True

restored = LinearRegressionEstimator.deserialize(
    payload
)

assert restored.initialized is True
assert restored.fitted is True
assert restored.feature_names == (
    "lag_1",
    "weekday",
)

assert math.isclose(
    restored.intercept,
    5.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

restored_predictions = restored.predict(
    [
        [7.0, 0.0],
        [8.0, 1.0],
    ]
)

assert math.isclose(
    restored_predictions[0],
    19.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    restored_predictions[1],
    24.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "linear_regression_estimator.json"
    )

    estimator.save(
        artifact_path
    )

    assert artifact_path.exists()

    loaded = LinearRegressionEstimator.load(
        artifact_path
    )

    assert loaded.fitted is True

    assert math.isclose(
        loaded.intercept,
        5.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )

    loaded_prediction = loaded.predict(
        [[9.0, 0.0]]
    )

    assert math.isclose(
        loaded_prediction[0],
        23.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


# ----------------------------------------------------------
# Failure behavior
# ----------------------------------------------------------

unfitted = LinearRegressionEstimator()

try:
    unfitted.predict([[1.0]])
except RuntimeError as exc:
    assert "must be fitted" in str(exc)
else:
    raise AssertionError(
        "Expected RuntimeError before fitting."
    )

try:
    LinearRegressionEstimator().fit(
        features=[
            [1.0],
            [2.0],
            [3.0],
        ],
        target=[
            10.0,
            20.0,
        ],
    )
except ValueError as exc:
    assert "record counts must match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for mismatched records."
    )

try:
    LinearRegressionEstimator().fit(
        features=[[1.0]],
        target=[10.0],
    )
except ValueError as exc:
    assert "at least two training records" in str(
        exc
    )
else:
    raise AssertionError(
        "Expected ValueError for insufficient records."
    )

try:
    estimator.predict(
        [[1.0, 2.0, 3.0]]
    )
except ValueError as exc:
    assert "feature count does not match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for incompatible features."
    )


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

estimator.reset()

assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.feature_names == ()
assert estimator.target_name is None
assert estimator.training_metadata == {}
assert estimator.intercept == 0.0
assert estimator.coefficients == ()
assert estimator.rank is None
assert estimator.residual_sum_of_squares is None

print(
    "linear_regression/estimator.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
import tempfile
from pathlib import Path

module_names = (
    "src.forecast.algorithms.linear_regression.model",
    "src.forecast.algorithms.linear_regression.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.linear_regression.model import (
    LinearRegressionForecastModel,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifactStatus,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastTrainingError,
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

model = LinearRegressionForecastModel(
    fit_intercept=True
)

assert model.model_key == "linear_regression"
assert model.model_name == "Linear Regression Forecast"
assert model.algorithm == "linear_regression"
assert model.model_category == (
    ForecastModelCategory.MACHINE_LEARNING
)
assert model.fit_intercept is True
assert model.state == ForecastModelState.CREATED

assert model.supports(
    ForecastModelCapability.POINT_FORECAST
)
assert model.supports(
    ForecastModelCapability.MULTI_STEP_FORECAST
)


# ----------------------------------------------------------
# Training
#
# y = 5 + 2*x1 + 3*x2
# ----------------------------------------------------------

training_context = ForecastTrainingContext(
    training_dataset={
        "features": [
            [1.0, 0.0],
            [2.0, 1.0],
            [3.0, 0.0],
            [4.0, 1.0],
            [5.0, 0.0],
            [6.0, 1.0],
        ],
        "target": [
            7.0,
            12.0,
            11.0,
            16.0,
            15.0,
            20.0,
        ],
    },
    validation_dataset={
        "features": [
            [7.0, 0.0],
            [8.0, 1.0],
        ],
        "target": [
            19.0,
            24.0,
        ],
    },
    feature_columns=(
        "lag_1",
        "weekday_indicator",
    ),
    target_column="workload",
    forecast_horizon=2,
    experiment_id=(
        "implementation-11-linear-regression-validation"
    ),
    metadata={
        "environment": "validation",
    },
)

training_result = model.train(
    training_context
)

assert training_result.succeeded is True
assert training_result.status.value == "SUCCESS"
assert training_result.training_records == 6
assert training_result.validation_records == 2
assert training_result.forecast_horizon == 2

assert math.isclose(
    training_result.metadata["intercept"],
    5.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert len(
    training_result.metadata["coefficients"]
) == 2

assert math.isclose(
    training_result.metadata["coefficients"][0],
    2.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    training_result.metadata["coefficients"][1],
    3.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert model.training_context is training_context
assert model.estimator.fitted is True
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

prediction_context = ForecastPredictionContext(
    prediction_dataset=[
        [7.0, 0.0],
        [8.0, 1.0],
    ],
    forecast_horizon=2,
    metadata={
        "scenario": "validation",
    },
)

prediction_result = model.predict(
    prediction_context
)

assert prediction_result.succeeded is True
assert len(prediction_result.predictions) == 2

assert math.isclose(
    prediction_result.predictions[0],
    19.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    prediction_result.predictions[1],
    24.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert prediction_result.forecast_horizon == 2
assert model.prediction_context is prediction_context
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Evaluation
# ----------------------------------------------------------

evaluation_context = ForecastEvaluationContext(
    actual_values=(
        19.0,
        24.0,
    ),
    predicted_values=(
        prediction_result.predictions
    ),
    metric="RMSE",
    metadata={
        "split": "validation",
    },
)

evaluation_result = model.evaluate(
    evaluation_context
)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric == "RMSE"

assert math.isclose(
    evaluation_result.primary_metric_value,
    0.0,
    abs_tol=1e-9,
)

assert math.isclose(
    evaluation_result.metrics["RMSE"],
    0.0,
    abs_tol=1e-9,
)

assert evaluation_result.evaluation_records == 2

assert math.isclose(
    evaluation_result.feature_importance[
        "lag_1"
    ],
    2.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert math.isclose(
    evaluation_result.feature_importance[
        "weekday_indicator"
    ],
    3.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert model.evaluation_context is evaluation_context
assert model.state == ForecastModelState.EVALUATED


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

payload = model.serialize()

assert payload["model_key"] == "linear_regression"
assert payload["fit_intercept"] is True
assert payload["estimator"]["fitted"] is True
assert len(payload["estimator"]["coefficients"]) == 2

restored_model = (
    LinearRegressionForecastModel.deserialize(
        payload
    )
)

assert restored_model.model_key == (
    "linear_regression"
)
assert restored_model.fit_intercept is True
assert restored_model.estimator.fitted is True
assert restored_model.state == (
    ForecastModelState.EVALUATED
)

restored_prediction = restored_model.predict(
    ForecastPredictionContext(
        prediction_dataset=[
            [9.0, 0.0],
        ],
        forecast_horizon=1,
    )
)

assert math.isclose(
    restored_prediction.predictions[0],
    23.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "linear_regression_model.json"
    )

    artifact = model.save(
        artifact_path
    )

    assert artifact_path.exists()

    assert artifact.status == (
        ForecastArtifactStatus.PERSISTED
    )

    assert artifact.storage_uri == str(
        artifact_path
    )

    assert artifact.algorithm == (
        "linear_regression"
    )

    assert artifact.feature_columns == (
        "lag_1",
        "weekday_indicator",
    )

    assert artifact.target_column == "workload"
    assert artifact.forecast_horizon == 2
    assert artifact.hyperparameters[
        "fit_intercept"
    ] is True
    assert artifact.checksum
    assert model.artifact is artifact
    assert model.state == ForecastModelState.SAVED

    loaded_model = (
        LinearRegressionForecastModel.load(
            artifact_path,
            metadata={
                "forecast_horizon": 2,
                "environment": "validation",
            },
        )
    )

    assert loaded_model.state == (
        ForecastModelState.LOADED
    )
    assert loaded_model.fit_intercept is True
    assert loaded_model.estimator.fitted is True
    assert loaded_model.artifact is not None

    assert loaded_model.artifact.storage_uri == str(
        artifact_path
    )

    assert loaded_model.artifact.metadata[
        "environment"
    ] == "validation"

    loaded_prediction = loaded_model.predict(
        ForecastPredictionContext(
            prediction_dataset=[
                [10.0, 1.0],
            ],
            forecast_horizon=1,
        )
    )

    assert math.isclose(
        loaded_prediction.predictions[0],
        28.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


# ----------------------------------------------------------
# Failure behavior
# ----------------------------------------------------------

try:
    LinearRegressionForecastModel().predict(
        ForecastPredictionContext(
            prediction_dataset=[
                [1.0, 0.0],
            ],
        )
    )
except Exception as exc:
    assert "trained or loaded" in str(exc)
else:
    raise AssertionError(
        "Expected failure before model training."
    )

try:
    LinearRegressionForecastModel().train(
        ForecastTrainingContext(
            training_dataset={
                "features": [
                    [1.0],
                    [2.0],
                    [3.0],
                ],
                "target": [
                    10.0,
                    20.0,
                ],
            },
            feature_columns=("lag_1",),
            target_column="workload",
        )
    )
except ForecastTrainingError as exc:
    assert exc.error_code == (
        "FORECAST_TRAINING_ERROR"
    )

    assert (
        "Linear Regression forecast model training failed"
        in str(exc)
    )

    assert isinstance(
        exc.__cause__,
        ValueError,
    )

    assert "record counts must match" in str(
        exc.__cause__
    )
else:
    raise AssertionError(
        "Expected ForecastTrainingError for mismatched records."
    )


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None
assert model.estimator.initialized is False
assert model.estimator.fitted is False
assert model.estimator.intercept == 0.0
assert model.estimator.coefficients == ()
assert model.estimator.rank is None
assert (
    model.estimator.residual_sum_of_squares
    is None
)

print(
    "linear_regression/model.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

from src.forecast.modeling.factory import (
    ForecastModelFactory,
)


# ----------------------------------------------------------
# Isolate and rebuild completed registrations
# ----------------------------------------------------------

ForecastModelFactory.clear()

module_names = (
    "src.forecast.algorithms.naive",
    "src.forecast.algorithms.moving_average",
    "src.forecast.algorithms.linear_regression",
    "src.forecast.algorithms.linear_regression.model",
    "src.forecast.algorithms.linear_regression.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

naive_package = importlib.import_module(
    "src.forecast.algorithms.naive"
)

moving_average_package = importlib.import_module(
    "src.forecast.algorithms.moving_average"
)

linear_regression_package = importlib.import_module(
    "src.forecast.algorithms.linear_regression"
)


LinearRegressionForecastModel = (
    linear_regression_package.LinearRegressionForecastModel
)

LinearRegressionEstimator = (
    linear_regression_package.LinearRegressionEstimator
)

build_linear_regression_model = (
    linear_regression_package.build_linear_regression_model
)

DEFAULT_FIT_INTERCEPT = (
    linear_regression_package.DEFAULT_FIT_INTERCEPT
)


# ----------------------------------------------------------
# Package exports
# ----------------------------------------------------------

assert LinearRegressionForecastModel.__name__ == (
    "LinearRegressionForecastModel"
)

assert LinearRegressionEstimator.__name__ == (
    "LinearRegressionEstimator"
)

assert callable(build_linear_regression_model)

assert DEFAULT_FIT_INTERCEPT is True


# ----------------------------------------------------------
# Factory registration
# ----------------------------------------------------------

assert ForecastModelFactory.is_supported(
    "linear_regression"
)

assert ForecastModelFactory.is_supported(
    "linear-regression"
)

assert ForecastModelFactory.is_supported(
    "moving_average"
)

assert ForecastModelFactory.is_supported(
    "naive_last_value"
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "moving_average",
    "naive_last_value",
)


registration = (
    ForecastModelFactory.get_registration(
        "linear_regression"
    )
)

registration_dict = registration.to_dict()

assert registration.model_key == (
    "linear_regression"
)

assert registration.display_name == (
    "Linear Regression Forecast"
)

assert registration.category.value == (
    "MACHINE_LEARNING"
)

assert registration.implementation_version == (
    "1.0.0"
)

assert registration_dict["capabilities"] == [
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert registration_dict["metadata"][
    "framework"
] == "numpy"

assert registration_dict["metadata"][
    "algorithm_family"
] == "machine_learning"

assert registration_dict["metadata"][
    "default_fit_intercept"
] is True


# ----------------------------------------------------------
# Default factory creation
# ----------------------------------------------------------

factory_model = ForecastModelFactory.create(
    "linear_regression"
)

assert isinstance(
    factory_model,
    LinearRegressionForecastModel,
)

assert factory_model.model_key == (
    "linear_regression"
)

assert factory_model.algorithm == (
    "linear_regression"
)

assert factory_model.fit_intercept is True

assert factory_model.estimator.estimator_name == (
    "linear_regression_estimator"
)

assert factory_model.estimator.parameters[
    "fit_intercept"
] is True


# ----------------------------------------------------------
# Alias creation
# ----------------------------------------------------------

alias_model = ForecastModelFactory.create(
    "linear-regression"
)

assert isinstance(
    alias_model,
    LinearRegressionForecastModel,
)

assert alias_model.fit_intercept is True


# ----------------------------------------------------------
# Catalog
# ----------------------------------------------------------

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 3

catalog_by_key = {
    item["model_key"]: item
    for item in catalog
}

assert set(catalog_by_key) == {
    "linear_regression",
    "moving_average",
    "naive_last_value",
}

assert catalog_by_key[
    "linear_regression"
]["category"] == "MACHINE_LEARNING"

assert catalog_by_key[
    "moving_average"
]["category"] == "STATISTICAL"

assert catalog_by_key[
    "naive_last_value"
]["category"] == "BASELINE"


# ----------------------------------------------------------
# Reload idempotency
# ----------------------------------------------------------

reloaded_package = importlib.reload(
    linear_regression_package
)

assert (
    reloaded_package.LinearRegressionForecastModel
    is not None
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "moving_average",
    "naive_last_value",
)


print(
    "src.forecast.algorithms.linear_regression "
    "package import: PASSED"
)

print(
    "Linear Regression factory registration: PASSED"
)

print(
    "src.forecast.algorithms.linear_regression "
    "__init__.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
import tempfile
from pathlib import Path

module_name = (
    "src.forecast.algorithms.random_forest.estimator"
)

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

random_forest_module = importlib.import_module(
    module_name
)

RandomForestEstimator = (
    random_forest_module.RandomForestEstimator
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

estimator = RandomForestEstimator(
    n_estimators=50,
    max_depth=6,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features=1.0,
    bootstrap=True,
    random_state=42,
    n_jobs=1,
)

assert estimator.estimator_name == (
    "random_forest_estimator"
)
assert estimator.framework == "scikit_learn"
assert estimator.version == "1.0.0"
assert estimator.n_estimators == 50
assert estimator.max_depth == 6
assert estimator.min_samples_split == 2
assert estimator.min_samples_leaf == 1
assert estimator.max_features == 1.0
assert estimator.bootstrap is True
assert estimator.random_state == 42
assert estimator.n_jobs == 1
assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.model is None
assert estimator.feature_importances == ()
assert estimator.feature_count is None


# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------

estimator.initialize(
    feature_names=(
        "lag_1",
        "weekday_indicator",
    ),
    target_name="workload",
)

assert estimator.initialized is True
assert estimator.feature_names == (
    "lag_1",
    "weekday_indicator",
)
assert estimator.target_name == "workload"


# ----------------------------------------------------------
# Fit
# ----------------------------------------------------------

features = [
    [1.0, 0.0],
    [2.0, 1.0],
    [3.0, 0.0],
    [4.0, 1.0],
    [5.0, 0.0],
    [6.0, 1.0],
    [7.0, 0.0],
    [8.0, 1.0],
    [9.0, 0.0],
    [10.0, 1.0],
]

target = [
    12.0,
    18.0,
    16.0,
    24.0,
    22.0,
    30.0,
    28.0,
    36.0,
    34.0,
    42.0,
]

fitted_estimator = estimator.fit(
    features=features,
    target=target,
)

assert fitted_estimator is estimator
assert estimator.fitted is True
assert estimator.model is not None
assert estimator.feature_count == 2
assert len(estimator.feature_importances) == 2

assert math.isclose(
    sum(estimator.feature_importances),
    1.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
)

assert estimator.training_metadata[
    "training_records"
] == 10

assert estimator.training_metadata[
    "feature_count"
] == 2

assert estimator.training_metadata[
    "n_estimators"
] == 50

assert estimator.training_metadata[
    "training_rmse"
] >= 0.0


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

prediction_features = [
    [11.0, 0.0],
    [12.0, 1.0],
]

predictions = estimator.predict(
    prediction_features
)

assert len(predictions) == 2

assert all(
    math.isfinite(value)
    for value in predictions
)

assert predictions[1] >= predictions[0]


# ----------------------------------------------------------
# Prediction dispersion
# ----------------------------------------------------------

mean_predictions, prediction_std = (
    estimator.predict_with_dispersion(
        prediction_features
    )
)

assert len(mean_predictions) == 2
assert len(prediction_std) == 2

for direct, ensemble_mean in zip(
    predictions,
    mean_predictions,
    strict=True,
):
    assert math.isclose(
        direct,
        ensemble_mean,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

assert all(
    value >= 0.0
    for value in prediction_std
)


# ----------------------------------------------------------
# Metadata and serialization
# ----------------------------------------------------------

metadata = estimator.get_metadata()

assert metadata["estimator_name"] == (
    "random_forest_estimator"
)
assert metadata["framework"] == "scikit_learn"
assert metadata["initialized"] is True
assert metadata["fitted"] is True
assert metadata["feature_names"] == [
    "lag_1",
    "weekday_indicator",
]
assert metadata["target_name"] == "workload"

payload = estimator.serialize()

assert payload["n_estimators"] == 50
assert payload["max_depth"] == 6
assert payload["fitted"] is True
assert payload["feature_count"] == 2
assert len(payload["feature_importances"]) == 2
assert isinstance(payload["model_blob"], str)
assert len(payload["model_blob"]) > 0


# ----------------------------------------------------------
# Deserialization
# ----------------------------------------------------------

restored = RandomForestEstimator.deserialize(
    payload
)

assert restored.initialized is True
assert restored.fitted is True
assert restored.n_estimators == 50
assert restored.max_depth == 6
assert restored.feature_count == 2
assert len(restored.feature_importances) == 2
assert restored.model is not None

restored_predictions = restored.predict(
    prediction_features
)

for original, restored_value in zip(
    predictions,
    restored_predictions,
    strict=True,
):
    assert math.isclose(
        original,
        restored_value,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "random_forest_estimator.json"
    )

    estimator.save(
        artifact_path
    )

    assert artifact_path.exists()

    loaded = RandomForestEstimator.load(
        artifact_path
    )

    assert loaded.fitted is True
    assert loaded.model is not None
    assert loaded.feature_count == 2
    assert loaded.n_estimators == 50
    assert loaded.max_depth == 6

    loaded_predictions = loaded.predict(
        prediction_features
    )

    for original, loaded_value in zip(
        predictions,
        loaded_predictions,
        strict=True,
    ):
        assert math.isclose(
            original,
            loaded_value,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


# ----------------------------------------------------------
# Failure behavior
# ----------------------------------------------------------

unfitted = RandomForestEstimator(
    n_estimators=10,
    random_state=42,
    n_jobs=1,
)

try:
    unfitted.predict([[1.0, 0.0]])
except RuntimeError as exc:
    assert "must be fitted" in str(exc)
else:
    raise AssertionError(
        "Expected RuntimeError before fitting."
    )

try:
    RandomForestEstimator(
        n_estimators=0
    )
except ValueError as exc:
    assert "positive integer" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for n_estimators=0."
    )

try:
    RandomForestEstimator(
        max_depth=0
    )
except ValueError as exc:
    assert "positive integer" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for max_depth=0."
    )

try:
    RandomForestEstimator(
        n_estimators=10,
        n_jobs=1,
    ).fit(
        features=[
            [1.0],
            [2.0],
            [3.0],
        ],
        target=[
            10.0,
            20.0,
        ],
    )
except ValueError as exc:
    assert "record counts must match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for mismatched records."
    )

try:
    estimator.predict(
        [[1.0, 2.0, 3.0]]
    )
except ValueError as exc:
    assert "feature count does not match" in str(exc)
else:
    raise AssertionError(
        "Expected ValueError for incompatible features."
    )


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

estimator.reset()

assert estimator.initialized is False
assert estimator.fitted is False
assert estimator.feature_names == ()
assert estimator.target_name is None
assert estimator.training_metadata == {}
assert estimator.model is None
assert estimator.feature_importances == ()
assert estimator.feature_count is None

print(
    "random_forest/estimator.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
import tempfile
from pathlib import Path

module_names = (
    "src.forecast.algorithms.random_forest.model",
    "src.forecast.algorithms.random_forest.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.random_forest.model import (
    RandomForestForecastModel,
)
from src.forecast.modeling.artifacts import ForecastArtifactStatus
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.exceptions import ForecastTrainingError


model = RandomForestForecastModel(
    n_estimators=50,
    max_depth=6,
    random_state=42,
    n_jobs=1,
)

assert model.model_key == "random_forest"
assert model.model_name == "Random Forest Forecast"
assert model.algorithm == "random_forest"
assert model.model_category == (
    ForecastModelCategory.MACHINE_LEARNING
)
assert model.state == ForecastModelState.CREATED

assert model.supports(
    ForecastModelCapability.POINT_FORECAST
)
assert model.supports(
    ForecastModelCapability.MULTI_STEP_FORECAST
)
assert model.supports(
    ForecastModelCapability.FEATURE_IMPORTANCE
)


training_context = ForecastTrainingContext(
    training_dataset={
        "features": [
            [1.0, 0.0],
            [2.0, 1.0],
            [3.0, 0.0],
            [4.0, 1.0],
            [5.0, 0.0],
            [6.0, 1.0],
            [7.0, 0.0],
            [8.0, 1.0],
            [9.0, 0.0],
            [10.0, 1.0],
        ],
        "target": [
            12.0,
            18.0,
            16.0,
            24.0,
            22.0,
            30.0,
            28.0,
            36.0,
            34.0,
            42.0,
        ],
    },
    validation_dataset={
        "features": [
            [11.0, 0.0],
            [12.0, 1.0],
        ],
        "target": [
            40.0,
            48.0,
        ],
    },
    feature_columns=(
        "lag_1",
        "weekday_indicator",
    ),
    target_column="workload",
    forecast_horizon=2,
    experiment_id="implementation-11-random-forest-validation",
)

training_result = model.train(training_context)

assert training_result.succeeded is True
assert training_result.training_records == 10
assert training_result.validation_records == 2
assert len(
    training_result.metadata["feature_importances"]
) == 2
assert model.estimator.fitted is True
assert model.state == ForecastModelState.TRAINED


prediction_result = model.predict(
    ForecastPredictionContext(
        prediction_dataset=[
            [11.0, 0.0],
            [12.0, 1.0],
        ],
        forecast_horizon=2,
    )
)

assert prediction_result.succeeded is True
assert len(prediction_result.predictions) == 2
assert all(
    math.isfinite(value)
    for value in prediction_result.predictions
)
assert len(
    prediction_result.metadata[
        "prediction_dispersion"
    ]
) == 2
assert model.state == ForecastModelState.TRAINED


evaluation_result = model.evaluate(
    ForecastEvaluationContext(
        actual_values=(
            40.0,
            48.0,
        ),
        predicted_values=(
            prediction_result.predictions
        ),
        metric="RMSE",
    )
)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric == "RMSE"
assert evaluation_result.primary_metric_value >= 0.0
assert len(
    evaluation_result.feature_importance
) == 2
assert model.state == ForecastModelState.EVALUATED


payload = model.serialize()

assert payload["model_key"] == "random_forest"
assert payload["estimator"]["fitted"] is True
assert isinstance(
    payload["estimator"]["model_blob"],
    str,
)

restored_model = (
    RandomForestForecastModel.deserialize(
        payload
    )
)

assert restored_model.estimator.fitted is True
assert restored_model.state == (
    ForecastModelState.EVALUATED
)

restored_prediction = restored_model.predict(
    ForecastPredictionContext(
        prediction_dataset=[
            [11.0, 0.0],
        ],
        forecast_horizon=1,
    )
)

assert math.isclose(
    restored_prediction.predictions[0],
    prediction_result.predictions[0],
    rel_tol=1e-12,
    abs_tol=1e-12,
)


with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "random_forest_model.json"
    )

    artifact = model.save(
        artifact_path
    )

    assert artifact_path.exists()
    assert artifact.status == (
        ForecastArtifactStatus.PERSISTED
    )
    assert artifact.algorithm == "random_forest"
    assert artifact.feature_columns == (
        "lag_1",
        "weekday_indicator",
    )
    assert artifact.target_column == "workload"
    assert artifact.forecast_horizon == 2
    assert artifact.hyperparameters[
        "n_estimators"
    ] == 50
    assert artifact.checksum
    assert model.state == ForecastModelState.SAVED

    loaded_model = (
        RandomForestForecastModel.load(
            artifact_path,
            metadata={
                "forecast_horizon": 2,
                "environment": "validation",
            },
        )
    )

    assert loaded_model.state == (
        ForecastModelState.LOADED
    )
    assert loaded_model.estimator.fitted is True
    assert loaded_model.artifact is not None
    assert loaded_model.artifact.metadata[
        "environment"
    ] == "validation"

    loaded_prediction = loaded_model.predict(
        ForecastPredictionContext(
            prediction_dataset=[
                [11.0, 0.0],
            ],
            forecast_horizon=1,
        )
    )

    assert math.isclose(
        loaded_prediction.predictions[0],
        prediction_result.predictions[0],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


try:
    RandomForestForecastModel(
        n_estimators=10,
        n_jobs=1,
    ).predict(
        ForecastPredictionContext(
            prediction_dataset=[
                [1.0, 0.0],
            ]
        )
    )
except Exception as exc:
    assert "trained or loaded" in str(exc)
else:
    raise AssertionError(
        "Expected failure before model training."
    )


try:
    RandomForestForecastModel(
        n_estimators=10,
        n_jobs=1,
    ).train(
        ForecastTrainingContext(
            training_dataset={
                "features": [
                    [1.0],
                    [2.0],
                    [3.0],
                ],
                "target": [
                    10.0,
                    20.0,
                ],
            },
            feature_columns=("lag_1",),
            target_column="workload",
        )
    )
except ForecastTrainingError as exc:
    assert exc.error_code == (
        "FORECAST_TRAINING_ERROR"
    )
    assert isinstance(
        exc.__cause__,
        ValueError,
    )
    assert "record counts must match" in str(
        exc.__cause__
    )
else:
    raise AssertionError(
        "Expected ForecastTrainingError for mismatched records."
    )


model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None
assert model.estimator.initialized is False
assert model.estimator.fitted is False
assert model.estimator.model is None
assert model.estimator.feature_importances == ()
assert model.estimator.feature_count is None

print(
    "random_forest/model.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

from src.forecast.modeling.factory import ForecastModelFactory


ForecastModelFactory.clear()

module_names = (
    "src.forecast.algorithms.naive",
    "src.forecast.algorithms.moving_average",
    "src.forecast.algorithms.linear_regression",
    "src.forecast.algorithms.random_forest",
    "src.forecast.algorithms.random_forest.model",
    "src.forecast.algorithms.random_forest.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

importlib.import_module(
    "src.forecast.algorithms.naive"
)
importlib.import_module(
    "src.forecast.algorithms.moving_average"
)
importlib.import_module(
    "src.forecast.algorithms.linear_regression"
)

random_forest_package = importlib.import_module(
    "src.forecast.algorithms.random_forest"
)

RandomForestEstimator = (
    random_forest_package.RandomForestEstimator
)
RandomForestForecastModel = (
    random_forest_package.RandomForestForecastModel
)
build_random_forest_model = (
    random_forest_package.build_random_forest_model
)

assert RandomForestEstimator is not None
assert RandomForestForecastModel is not None
assert callable(build_random_forest_model)

assert ForecastModelFactory.is_supported(
    "random_forest"
)
assert ForecastModelFactory.is_supported(
    "random-forest"
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "moving_average",
    "naive_last_value",
    "random_forest",
)

registration = ForecastModelFactory.get_registration(
    "random_forest"
)

registration_dict = registration.to_dict()

assert registration.model_key == "random_forest"
assert registration.display_name == "Random Forest Forecast"
assert registration.category.value == "MACHINE_LEARNING"
assert registration.implementation_version == "1.0.0"

assert registration_dict["capabilities"] == [
    "FEATURE_IMPORTANCE",
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert registration_dict["metadata"][
    "framework"
] == "scikit_learn"

factory_model = ForecastModelFactory.create(
    "random_forest"
)

assert isinstance(
    factory_model,
    RandomForestForecastModel,
)
assert factory_model.model_key == "random_forest"
assert factory_model.estimator.n_estimators == 200
assert factory_model.estimator.random_state == 42

alias_model = ForecastModelFactory.create(
    "random-forest"
)

assert isinstance(
    alias_model,
    RandomForestForecastModel,
)

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 4

catalog_by_key = {
    item["model_key"]: item
    for item in catalog
}

assert set(catalog_by_key) == {
    "linear_regression",
    "moving_average",
    "naive_last_value",
    "random_forest",
}

assert catalog_by_key[
    "random_forest"
]["category"] == "MACHINE_LEARNING"

reloaded_package = importlib.reload(
    random_forest_package
)

assert (
    reloaded_package.RandomForestForecastModel
    is not None
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "moving_average",
    "naive_last_value",
    "random_forest",
)

print(
    "src.forecast.algorithms.random_forest package import: PASSED"
)
print(
    "Random Forest factory registration: PASSED"
)
print(
    "src.forecast.algorithms.random_forest __init__.py validation: PASSED"
)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# Canonical forecast package identity
# Platform release: v3.0.0
# Canonical namespace: src.*
# =============================================================================

import src.forecast as forecast

assert forecast.__name__ == "src.forecast"

print("src.forecast package import: PASSED")
print("src.forecast loaded from:", forecast.__file__)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# LSTM dependency and import validation
# Platform release: v3.0.0
# Canonical namespace: src.*
# =============================================================================

import importlib
import importlib.util
import sys


# -----------------------------------------------------------------------------
# Optional dependency contract
# -----------------------------------------------------------------------------

torch_available = importlib.util.find_spec("torch") is not None

print("=" * 72)
print("LSTM DEPENDENCY VALIDATION")
print("=" * 72)
print("Platform release      : v3.0.0")
print("Canonical namespace   : src.*")
print("Implementation        : 28")
print(f"PyTorch available     : {torch_available}")


# -----------------------------------------------------------------------------
# Validate LSTM package when PyTorch is available
# -----------------------------------------------------------------------------

if torch_available:

    for module_name in (
        "src.forecast.algorithms.lstm.estimator",
        "src.forecast.algorithms.lstm",
    ):
        sys.modules.pop(module_name, None)

    importlib.invalidate_caches()

    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    lstm_module = importlib.import_module(
        "src.forecast.algorithms.lstm.estimator"
    )

    LSTMEstimator = lstm_module.LSTMEstimator

    assert LSTMEstimator is not None
    assert torch is not None
    assert nn is not None
    assert DataLoader is not None
    assert TensorDataset is not None

    print(f"PyTorch version       : {torch.__version__}")
    print(f"LSTM module           : {lstm_module.__name__}")
    print(f"Loaded from           : {lstm_module.__file__}")
    print("LSTM import status    : PASSED")

else:

    print(
        "LSTM validation      : SKIPPED "
        "(optional PyTorch dependency unavailable)"
    )


print("=" * 72)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# LSTM estimator behavioral validation
# Platform release: v3.0.0
# Canonical namespace: src.*
# =============================================================================

import importlib.util
import math


torch_available = importlib.util.find_spec("torch") is not None

print("=" * 72)
print("LSTM ESTIMATOR BEHAVIORAL VALIDATION")
print("=" * 72)
print("Platform release      : v3.0.0")
print("Canonical namespace   : src.*")
print("Implementation        : 28")
print(f"PyTorch available     : {torch_available}")


if torch_available:

    from src.forecast.algorithms.lstm.estimator import LSTMEstimator

    estimator = LSTMEstimator(
        hidden_size=8,
        num_layers=1,
        dropout=0.0,
        learning_rate=0.01,
        epochs=10,
        batch_size=4,
        device="cpu",
    )

    features = [
        [[1.0, 0.0], [2.0, 1.0], [3.0, 0.0]],
        [[2.0, 1.0], [3.0, 0.0], [4.0, 1.0]],
        [[3.0, 0.0], [4.0, 1.0], [5.0, 0.0]],
        [[4.0, 1.0], [5.0, 0.0], [6.0, 1.0]],
        [[5.0, 0.0], [6.0, 1.0], [7.0, 0.0]],
        [[6.0, 1.0], [7.0, 0.0], [8.0, 1.0]],
        [[7.0, 0.0], [8.0, 1.0], [9.0, 0.0]],
        [[8.0, 1.0], [9.0, 0.0], [10.0, 1.0]],
    ]

    target = [
        8.0,
        11.0,
        12.0,
        15.0,
        16.0,
        19.0,
        20.0,
        23.0,
    ]

    fitted_estimator = estimator.fit(
        features=features,
        target=target,
    )

    assert fitted_estimator is estimator
    assert estimator.fitted is True
    assert estimator.model is not None

    assert estimator.input_size == 2
    assert estimator.sequence_length == 3
    assert estimator.resolved_device == "cpu"

    assert len(estimator.feature_mean) == 2
    assert len(estimator.feature_std) == 2

    assert len(estimator.training_loss_history) == 10

    assert all(
        math.isfinite(value)
        for value in estimator.training_loss_history
    )

    assert estimator.training_metadata["training_records"] == 8
    assert estimator.training_metadata["sequence_length"] == 3

    print("Estimator fit          : PASSED")
    print("Training metadata      : PASSED")
    print("Training loss history  : PASSED")
    print("LSTM estimator status  : PASSED")

else:

    raise RuntimeError(
        "PyTorch is required for the enterprise LSTM validation suite."
    )


print("=" * 72)

# COMMAND ----------

import importlib
import math
import sys
import tempfile
from pathlib import Path

module_names = (
    "src.forecast.algorithms.lstm.model",
    "src.forecast.algorithms.lstm.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.lstm.model import (
    LSTMForecastModel,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifactStatus,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
    ForecastPredictionContext,
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelCapability,
    ForecastModelCategory,
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastTrainingError,
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

model = LSTMForecastModel(
    hidden_size=8,
    num_layers=1,
    dropout=0.0,
    learning_rate=0.01,
    epochs=10,
    batch_size=4,
    weight_decay=0.0,
    gradient_clip_norm=1.0,
    random_state=42,
    device="cpu",
)

assert model.model_key == "lstm"
assert model.model_name == "LSTM Forecast"
assert model.algorithm == "lstm"

assert model.model_category == (
    ForecastModelCategory.DEEP_LEARNING
)

assert model.state == ForecastModelState.CREATED

assert model.supports(
    ForecastModelCapability.MULTI_STEP_FORECAST
)


# ----------------------------------------------------------
# Training data
# ----------------------------------------------------------

training_features = [
    [[1.0, 0.0], [2.0, 1.0], [3.0, 0.0]],
    [[2.0, 1.0], [3.0, 0.0], [4.0, 1.0]],
    [[3.0, 0.0], [4.0, 1.0], [5.0, 0.0]],
    [[4.0, 1.0], [5.0, 0.0], [6.0, 1.0]],
    [[5.0, 0.0], [6.0, 1.0], [7.0, 0.0]],
    [[6.0, 1.0], [7.0, 0.0], [8.0, 1.0]],
    [[7.0, 0.0], [8.0, 1.0], [9.0, 0.0]],
    [[8.0, 1.0], [9.0, 0.0], [10.0, 1.0]],
]

training_target = [
    8.0,
    11.0,
    12.0,
    15.0,
    16.0,
    19.0,
    20.0,
    23.0,
]

validation_features = [
    [[9.0, 0.0], [10.0, 1.0], [11.0, 0.0]],
    [[10.0, 1.0], [11.0, 0.0], [12.0, 1.0]],
]

validation_target = [
    24.0,
    27.0,
]


training_context = ForecastTrainingContext(
    training_dataset={
        "features": training_features,
        "target": training_target,
    },
    validation_dataset={
        "features": validation_features,
        "target": validation_target,
    },
    feature_columns=(
        "workload_value",
        "weekday_indicator",
    ),
    target_column="workload",
    forecast_horizon=2,
    experiment_id=(
        "implementation-11-lstm-validation"
    ),
    metadata={
        "environment": "validation",
    },
)


# ----------------------------------------------------------
# Training
# ----------------------------------------------------------

training_result = model.train(
    training_context
)

assert training_result.succeeded is True
assert training_result.status.value == "SUCCESS"
assert training_result.training_records == 8
assert training_result.validation_records == 2
assert training_result.forecast_horizon == 2

assert training_result.metadata[
    "framework"
] == "pytorch"

assert training_result.metadata[
    "resolved_device"
] == "cpu"

assert training_result.metadata[
    "input_size"
] == 2

assert training_result.metadata[
    "sequence_length"
] == 3

assert training_result.metadata[
    "hidden_size"
] == 8

assert training_result.metadata[
    "num_layers"
] == 1

assert training_result.metadata[
    "epochs"
] == 10

assert math.isfinite(
    training_result.metadata[
        "final_training_loss"
    ]
)

assert model.training_context is training_context
assert model.estimator.fitted is True
assert model.estimator.model is not None
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Prediction
# ----------------------------------------------------------

prediction_context = ForecastPredictionContext(
    prediction_dataset=validation_features,
    forecast_horizon=2,
    metadata={
        "scenario": "validation",
    },
)

prediction_result = model.predict(
    prediction_context
)

assert prediction_result.succeeded is True
assert len(prediction_result.predictions) == 2

assert all(
    math.isfinite(value)
    for value in prediction_result.predictions
)

assert prediction_result.metadata[
    "framework"
] == "pytorch"

assert prediction_result.metadata[
    "resolved_device"
] == "cpu"

assert prediction_result.metadata[
    "sequence_length"
] == 3

assert prediction_result.metadata[
    "input_size"
] == 2

assert model.prediction_context is prediction_context
assert model.state == ForecastModelState.TRAINED


# ----------------------------------------------------------
# Evaluation
# ----------------------------------------------------------

evaluation_context = ForecastEvaluationContext(
    actual_values=validation_target,
    predicted_values=(
        prediction_result.predictions
    ),
    metric="RMSE",
    metadata={
        "split": "validation",
    },
)

evaluation_result = model.evaluate(
    evaluation_context
)

assert evaluation_result.succeeded is True
assert evaluation_result.primary_metric == "RMSE"

assert evaluation_result.primary_metric_value >= 0.0

assert math.isfinite(
    evaluation_result.primary_metric_value
)

assert evaluation_result.evaluation_records == 2

assert evaluation_result.feature_importance == {}

assert evaluation_result.metadata[
    "framework"
] == "pytorch"

assert evaluation_result.metadata[
    "sequence_length"
] == 3

assert model.evaluation_context is evaluation_context
assert model.state == ForecastModelState.EVALUATED


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

payload = model.serialize()

assert payload["model_key"] == "lstm"
assert payload["algorithm"] == "lstm"
assert payload["estimator"]["fitted"] is True
assert payload["estimator"]["input_size"] == 2
assert payload["estimator"]["sequence_length"] == 3

assert isinstance(
    payload["estimator"]["model_blob"],
    str,
)

assert len(
    payload["estimator"]["model_blob"]
) > 0


restored_model = LSTMForecastModel.deserialize(
    payload
)

assert restored_model.model_key == "lstm"
assert restored_model.estimator.fitted is True
assert restored_model.estimator.model is not None
assert restored_model.estimator.input_size == 2

assert restored_model.estimator.sequence_length == 3

assert restored_model.state == (
    ForecastModelState.EVALUATED
)


restored_prediction = restored_model.predict(
    ForecastPredictionContext(
        prediction_dataset=validation_features,
        forecast_horizon=2,
    )
)

for original, restored_value in zip(
    prediction_result.predictions,
    restored_prediction.predictions,
    strict=True,
):
    assert math.isclose(
        original,
        restored_value,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

with tempfile.TemporaryDirectory() as directory:
    artifact_path = (
        Path(directory)
        / "lstm_model.json"
    )

    artifact = model.save(
        artifact_path
    )

    assert artifact_path.exists()

    assert artifact.status == (
        ForecastArtifactStatus.PERSISTED
    )

    assert artifact.algorithm == "lstm"

    assert artifact.feature_columns == (
        "workload_value",
        "weekday_indicator",
    )

    assert artifact.target_column == "workload"
    assert artifact.forecast_horizon == 2

    assert artifact.hyperparameters[
        "hidden_size"
    ] == 8

    assert artifact.hyperparameters[
        "num_layers"
    ] == 1

    assert artifact.hyperparameters[
        "epochs"
    ] == 10

    assert artifact.checksum
    assert model.artifact is artifact

    assert model.state == (
        ForecastModelState.SAVED
    )


    loaded_model = LSTMForecastModel.load(
        artifact_path,
        metadata={
            "forecast_horizon": 2,
            "environment": "validation",
        },
    )

    assert loaded_model.state == (
        ForecastModelState.LOADED
    )

    assert loaded_model.estimator.fitted is True
    assert loaded_model.estimator.model is not None
    assert loaded_model.estimator.input_size == 2

    assert (
        loaded_model.estimator.sequence_length
        == 3
    )

    assert loaded_model.artifact is not None

    assert loaded_model.artifact.metadata[
        "environment"
    ] == "validation"


    loaded_prediction = loaded_model.predict(
        ForecastPredictionContext(
            prediction_dataset=validation_features,
            forecast_horizon=2,
        )
    )

    for original, loaded_value in zip(
        prediction_result.predictions,
        loaded_prediction.predictions,
        strict=True,
    ):
        assert math.isclose(
            original,
            loaded_value,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )


# ----------------------------------------------------------
# Failure behavior
# ----------------------------------------------------------

try:
    LSTMForecastModel(
        epochs=1,
        device="cpu",
    ).predict(
        ForecastPredictionContext(
            prediction_dataset=[
                [[1.0, 0.0]],
            ],
        )
    )

except Exception as exc:
    assert "trained or loaded" in str(exc)

else:
    raise AssertionError(
        "Expected failure before model training."
    )


try:
    LSTMForecastModel(
        hidden_size=4,
        epochs=1,
        batch_size=2,
        device="cpu",
    ).train(
        ForecastTrainingContext(
            training_dataset={
                "features": [
                    [[1.0]],
                    [[2.0]],
                    [[3.0]],
                ],
                "target": [
                    10.0,
                    20.0,
                ],
            },
            feature_columns=("lag_1",),
            target_column="workload",
        )
    )

except ForecastTrainingError as exc:
    assert exc.error_code == (
        "FORECAST_TRAINING_ERROR"
    )

    assert (
        "LSTM forecast model training failed"
        in str(exc)
    )

    assert isinstance(
        exc.__cause__,
        ValueError,
    )

    assert "record counts must match" in str(
        exc.__cause__
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for mismatched records."
    )


# ----------------------------------------------------------
# Reset
# ----------------------------------------------------------

model.reset()

assert model.state == ForecastModelState.CREATED
assert model.training_context is None
assert model.prediction_context is None
assert model.evaluation_context is None
assert model.artifact is None

assert model.estimator.initialized is False
assert model.estimator.fitted is False
assert model.estimator.model is None
assert model.estimator.input_size is None
assert model.estimator.sequence_length is None
assert model.estimator.resolved_device is None
assert model.estimator.feature_mean == ()
assert model.estimator.feature_std == ()
assert model.estimator.training_loss_history == ()

print(
    "lstm/model.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

import torch

from src.forecast.modeling.factory import (
    ForecastModelFactory,
)


# ----------------------------------------------------------
# Runtime dependency
# ----------------------------------------------------------

assert torch.__version__

print(
    "PyTorch dependency available:",
    torch.__version__,
)


# ----------------------------------------------------------
# Rebuild complete algorithm registry
# ----------------------------------------------------------

ForecastModelFactory.clear()

module_names = (
    "src.forecast.algorithms.naive",
    "src.forecast.algorithms.moving_average",
    "src.forecast.algorithms.linear_regression",
    "src.forecast.algorithms.random_forest",
    "src.forecast.algorithms.lstm",
    "src.forecast.algorithms.lstm.model",
    "src.forecast.algorithms.lstm.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()


# ----------------------------------------------------------
# Import existing algorithm packages
# ----------------------------------------------------------

importlib.import_module(
    "src.forecast.algorithms.naive"
)

importlib.import_module(
    "src.forecast.algorithms.moving_average"
)

importlib.import_module(
    "src.forecast.algorithms.linear_regression"
)

importlib.import_module(
    "src.forecast.algorithms.random_forest"
)

lstm_package = importlib.import_module(
    "src.forecast.algorithms.lstm"
)


# ----------------------------------------------------------
# Public package exports
# ----------------------------------------------------------

LSTMEstimator = lstm_package.LSTMEstimator
LSTMForecastModel = (
    lstm_package.LSTMForecastModel
)
build_lstm_model = (
    lstm_package.build_lstm_model
)

assert LSTMEstimator is not None
assert LSTMForecastModel is not None
assert callable(build_lstm_model)

assert lstm_package.DEFAULT_LSTM_PARAMETERS[
    "hidden_size"
] == 32

assert lstm_package.DEFAULT_LSTM_PARAMETERS[
    "num_layers"
] == 1

assert lstm_package.DEFAULT_LSTM_PARAMETERS[
    "epochs"
] == 20

assert lstm_package.DEFAULT_LSTM_PARAMETERS[
    "device"
] == "auto"


# ----------------------------------------------------------
# Factory support
# ----------------------------------------------------------

assert ForecastModelFactory.is_supported(
    "lstm"
)

assert ForecastModelFactory.is_supported(
    "LSTM"
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "lstm",
    "moving_average",
    "naive_last_value",
    "random_forest",
)


# ----------------------------------------------------------
# Registration metadata
# ----------------------------------------------------------

registration = (
    ForecastModelFactory.get_registration(
        "lstm"
    )
)

registration_dict = registration.to_dict()

assert registration.model_key == "lstm"

assert registration.display_name == (
    "LSTM Forecast"
)

assert registration.category.value == (
    "DEEP_LEARNING"
)

assert registration.implementation_version == (
    "1.0.0"
)

assert registration_dict["capabilities"] == [
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert registration_dict["metadata"][
    "framework"
] == "pytorch"

assert registration_dict["metadata"][
    "algorithm_family"
] == "deep_learning"

assert registration_dict["metadata"][
    "default_hidden_size"
] == 32

assert registration_dict["metadata"][
    "default_epochs"
] == 20


# ----------------------------------------------------------
# Factory construction
# ----------------------------------------------------------

factory_model = ForecastModelFactory.create(
    "lstm"
)

assert isinstance(
    factory_model,
    LSTMForecastModel,
)

assert factory_model.model_key == "lstm"

assert factory_model.estimator.hidden_size == 32

assert factory_model.estimator.num_layers == 1

assert factory_model.estimator.epochs == 20

assert factory_model.estimator.batch_size == 32

assert factory_model.estimator.random_state == 42

assert factory_model.estimator.requested_device == (
    "auto"
)

assert factory_model.estimator.scale_features is True

assert factory_model.estimator.scale_target is True


# ----------------------------------------------------------
# Case-normalized factory creation
# ----------------------------------------------------------

normalized_model = ForecastModelFactory.create(
    "LSTM"
)

assert isinstance(
    normalized_model,
    LSTMForecastModel,
)

assert normalized_model.model_key == "lstm"


# ----------------------------------------------------------
# Catalog
# ----------------------------------------------------------

catalog = ForecastModelFactory.catalog()

assert len(catalog) == 5

catalog_by_key = {
    item["model_key"]: item
    for item in catalog
}

assert set(catalog_by_key) == {
    "linear_regression",
    "lstm",
    "moving_average",
    "naive_last_value",
    "random_forest",
}

assert catalog_by_key[
    "lstm"
]["category"] == "DEEP_LEARNING"

assert catalog_by_key[
    "lstm"
]["capabilities"] == [
    "MULTI_STEP_FORECAST",
    "POINT_FORECAST",
]

assert catalog_by_key[
    "lstm"
]["metadata"]["framework"] == "pytorch"


# ----------------------------------------------------------
# Reload idempotency
# ----------------------------------------------------------

reloaded_package = importlib.reload(
    lstm_package
)

assert reloaded_package.LSTMEstimator is not None

assert (
    reloaded_package.LSTMForecastModel
    is not None
)

assert callable(
    reloaded_package.build_lstm_model
)

assert ForecastModelFactory.supported_models() == (
    "linear_regression",
    "lstm",
    "moving_average",
    "naive_last_value",
    "random_forest",
)


print(
    "src.forecast.algorithms.lstm package import: PASSED"
)

print(
    "LSTM factory registration: PASSED"
)

print(
    "src.forecast.algorithms.lstm __init__.py validation: PASSED"
)

# COMMAND ----------

import importlib.util

assert importlib.util.find_spec(
    "src.forecast.algorithms.base"
) is not None

assert importlib.util.find_spec(
    "src.forecast.base"
) is None

from src.forecast.algorithms.base import (
    EnterpriseEstimator,
    EnterpriseForecastModel,
    EnterpriseSerializer,
)

print("Canonical algorithm base package: PASSED")
print("Obsolete forecast.base package removed: PASSED")

# COMMAND ----------

