# Databricks notebook source
# /// script
# [tool.databricks.environment]
# base_environment = "databricks_ai_v5"
# environment_version = "5"
# dependencies = [
#   "torch",
# ]
# ///
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Package Validation 2 — Release Remediation
# MAGIC **Platform release:** v3.0.0  
# MAGIC **Release remediation:** Implementation 28  
# MAGIC **Canonical namespace:** `src.*`  
# MAGIC **Primary finding:** ENG-001 — inconsistent Python import namespaces
# MAGIC
# MAGIC This copy preserves the historical validation coverage while
# MAGIC standardizing package identity and runtime bootstrap behavior.

# COMMAND ----------

# MAGIC %md
# MAGIC # Enterprise Forecast Platform — Package Validation 2
# MAGIC
# MAGIC Validates the remaining Enterprise Forecast Framework components using the corrected implementation roadmap:
# MAGIC
# MAGIC - **Implementation 11 — Enterprise Forecast Modeling Framework**
# MAGIC   - Modeling metrics contract
# MAGIC - **Implementation 13 — Enterprise Training Framework**
# MAGIC   - Trainer, orchestrator, callbacks, and package exports
# MAGIC - **Implementation 14 — Enterprise Evaluation Framework**
# MAGIC   - Evaluation metrics, evaluator, model comparison, and package exports
# MAGIC - **Implementation 15 — Enterprise Inference Framework**
# MAGIC   - Predictor, batch predictor, and package exports
# MAGIC - **Implementation 16 — Enterprise Model Registry**
# MAGIC   - Registry, catalog, semantic versioning, promotion, and package exports
# MAGIC
# MAGIC **Implementation 12 — Enterprise Forecast Algorithm Library** is validated in `99_package_validation`.

# COMMAND ----------

# MAGIC %pip install torch

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# ML Runtime Dependency Contract
# Platform release: v3.0.0
# =============================================================================

import importlib.util

torch_available = importlib.util.find_spec("torch") is not None

print("=" * 72)
print("ML RUNTIME DEPENDENCY VALIDATION")
print("=" * 72)
print("Platform release      : v3.0.0")
print("Canonical namespace   : src.*")
print("Implementation        : 28")
print(f"PyTorch available     : {torch_available}")

if not torch_available:
    raise RuntimeError(
        "PyTorch is required by the supported LSTM forecasting capability. "
        "Add 'torch' to the Databricks notebook Environment dependencies "
        "before running enterprise release validation."
    )

import torch

print(f"PyTorch version       : {torch.__version__}")
print("ML runtime status     : READY")
print("=" * 72)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# Canonical Repository Bootstrap
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

print("=" * 72)
print("CANONICAL REPOSITORY BOOTSTRAP")
print("=" * 72)
print(f"Repository root       : {repository_root}")
print(f"Canonical source root : {repository_root / 'src'}")
print("Canonical namespace   : src.*")
print("Bootstrap status      : PASSED")
print("=" * 72)

import src
import src.forecast as forecast

assert src.__name__ == "src"
assert forecast.__name__ == "src.forecast"

print("src package import    : PASSED")
print("src.forecast import   : PASSED")

# COMMAND ----------

import importlib
import sys

module_names = (
    "src.forecast.training.trainer",
    "src.forecast.algorithms.naive.model",
    "src.forecast.algorithms.naive.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.naive.model import (
    NaiveForecastModel,
)
from src.forecast.modeling.contexts import (
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastTrainingError,
)
from src.forecast.modeling.results import (
    ForecastTrainingResult,
)
from src.forecast.training.trainer import (
    EnterpriseForecastTrainer,
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

trainer = EnterpriseForecastTrainer()

assert isinstance(
    trainer,
    EnterpriseForecastTrainer,
)


# ----------------------------------------------------------
# Training context
# ----------------------------------------------------------

training_context = ForecastTrainingContext(
    training_dataset=[
        10.0,
        20.0,
        30.0,
    ],
    feature_columns=(),
    target_column="workload",
    forecast_horizon=1,
    experiment_id=(
        "implementation-13-trainer-validation"
    ),
    metadata={
        "environment": "validation",
    },
)


# ----------------------------------------------------------
# Successful training
# ----------------------------------------------------------

model = NaiveForecastModel()

assert model.state == ForecastModelState.CREATED

training_result = trainer.train(
    model=model,
    context=training_context,
)

assert isinstance(
    training_result,
    ForecastTrainingResult,
)

assert training_result.succeeded is True

assert model.state == ForecastModelState.TRAINED

assert model.training_context is training_context

assert model.estimator.fitted is True

assert model.estimator.last_value == 30.0


# ----------------------------------------------------------
# Existing-state protection
# ----------------------------------------------------------

try:
    trainer.train(
        model=model,
        context=training_context,
    )

except ForecastTrainingError as exc:
    assert (
        "not in the CREATED state"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an "
        "already-trained model."
    )


# ----------------------------------------------------------
# Explicit retraining
# ----------------------------------------------------------

retraining_context = ForecastTrainingContext(
    training_dataset=[
        40.0,
        50.0,
        60.0,
    ],
    feature_columns=(),
    target_column="workload",
    forecast_horizon=1,
    experiment_id=(
        "implementation-13-trainer-retraining"
    ),
)

retraining_result = trainer.train(
    model=model,
    context=retraining_context,
    reset_existing=True,
)

assert retraining_result.succeeded is True

assert model.state == ForecastModelState.TRAINED

assert model.training_context is retraining_context

assert model.estimator.fitted is True

assert model.estimator.last_value == 60.0


# ----------------------------------------------------------
# Invalid model
# ----------------------------------------------------------

try:
    trainer.train(
        model=None,
        context=training_context,
    )

except ForecastTrainingError as exc:
    assert "cannot be None" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastTrainingError for a null model."
    )


try:
    trainer.train(
        model="not-a-model",
        context=training_context,
    )

except ForecastTrainingError as exc:
    assert (
        "EnterpriseForecastModel"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an invalid model."
    )


# ----------------------------------------------------------
# Invalid context
# ----------------------------------------------------------

new_model = NaiveForecastModel()

try:
    trainer.train(
        model=new_model,
        context=None,
    )

except ForecastTrainingError as exc:
    assert "cannot be None" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastTrainingError for a null context."
    )


try:
    trainer.train(
        model=new_model,
        context={
            "training_dataset": [1.0, 2.0],
        },
    )

except ForecastTrainingError as exc:
    assert (
        "ForecastTrainingContext"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an invalid context."
    )


# ----------------------------------------------------------
# Invalid reset flag
# ----------------------------------------------------------

try:
    trainer.train(
        model=NaiveForecastModel(),
        context=training_context,
        reset_existing="yes",
    )

except ForecastTrainingError as exc:
    assert (
        "reset_existing must be a boolean"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an invalid reset flag."
    )


# ----------------------------------------------------------
# Underlying training failure
# ----------------------------------------------------------

failing_model = NaiveForecastModel()

failing_context = ForecastTrainingContext(
    training_dataset=[],
    target_column="workload",
    forecast_horizon=1,
)

try:
    trainer.train(
        model=failing_model,
        context=failing_context,
    )

except ForecastTrainingError as exc:
    assert exc.error_code == (
        "FORECAST_TRAINING_ERROR"
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an empty dataset."
    )


# ----------------------------------------------------------
# Trainer statelessness
# ----------------------------------------------------------

assert vars(trainer) == {}


print(
    "forecast/training/trainer.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from collections.abc import Mapping

module_names = (
    "src.forecast.training.orchestrator",
    "src.forecast.training.trainer",
    "src.forecast.algorithms.naive.model",
    "src.forecast.algorithms.naive.estimator",
    "src.forecast.algorithms.moving_average.model",
    "src.forecast.algorithms.moving_average.estimator",
)

for module_name in module_names:
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.algorithms.moving_average.model import (
    MovingAverageForecastModel,
)
from src.forecast.algorithms.naive.model import (
    NaiveForecastModel,
)
from src.forecast.modeling.contexts import (
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastTrainingError,
)
from src.forecast.modeling.results import (
    ForecastTrainingResult,
)
from src.forecast.training.orchestrator import (
    EnterpriseForecastTrainingOrchestrator,
)
from src.forecast.training.trainer import (
    EnterpriseForecastTrainer,
)


# ----------------------------------------------------------
# Construction and dependency injection
# ----------------------------------------------------------

orchestrator = EnterpriseForecastTrainingOrchestrator()

assert isinstance(
    orchestrator.trainer,
    EnterpriseForecastTrainer,
)

injected_trainer = EnterpriseForecastTrainer()

injected_orchestrator = (
    EnterpriseForecastTrainingOrchestrator(
        trainer=injected_trainer,
    )
)

assert injected_orchestrator.trainer is injected_trainer


try:
    EnterpriseForecastTrainingOrchestrator(
        trainer="invalid-trainer",
    )

except ForecastTrainingError as exc:
    assert (
        "EnterpriseForecastTrainer"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an invalid trainer."
    )


# ----------------------------------------------------------
# Single-model delegation
# ----------------------------------------------------------

single_model = NaiveForecastModel()

single_context = ForecastTrainingContext(
    training_dataset=[
        10.0,
        20.0,
        30.0,
    ],
    target_column="workload",
    forecast_horizon=1,
)

single_result = orchestrator.train(
    model=single_model,
    context=single_context,
)

assert isinstance(
    single_result,
    ForecastTrainingResult,
)

assert single_result.succeeded is True
assert single_model.state == ForecastModelState.TRAINED
assert single_model.estimator.last_value == 30.0


# ----------------------------------------------------------
# Multi-model training
# ----------------------------------------------------------

naive_model = NaiveForecastModel()

moving_average_model = MovingAverageForecastModel(
    window_size=3,
)

models = {
    "baseline_naive": naive_model,
    "baseline_moving_average": moving_average_model,
}

contexts = {
    "baseline_naive": ForecastTrainingContext(
        training_dataset=[
            100.0,
            110.0,
            120.0,
        ],
        target_column="workload",
        forecast_horizon=1,
        experiment_id="orchestrator-naive",
    ),
    "baseline_moving_average": ForecastTrainingContext(
        training_dataset=[
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
        ],
        target_column="workload",
        forecast_horizon=1,
        experiment_id="orchestrator-moving-average",
    ),
}

results = orchestrator.train_many(
    models=models,
    contexts=contexts,
)

assert isinstance(results, Mapping)

assert tuple(results) == (
    "baseline_naive",
    "baseline_moving_average",
)

assert all(
    isinstance(result, ForecastTrainingResult)
    for result in results.values()
)

assert all(
    result.succeeded
    for result in results.values()
)

assert naive_model.state == ForecastModelState.TRAINED

assert moving_average_model.state == (
    ForecastModelState.TRAINED
)

assert naive_model.estimator.last_value == 120.0

assert moving_average_model.estimator.history == (
    30.0,
    40.0,
    50.0,
)

assert moving_average_model.estimator.moving_average == 40.0


# Returned result mapping is read-only.
try:
    results["new_execution"] = single_result

except TypeError:
    pass

else:
    raise AssertionError(
        "Expected the orchestration result mapping to be read-only."
    )


# ----------------------------------------------------------
# Explicit multi-model retraining
# ----------------------------------------------------------

retraining_contexts = {
    "baseline_naive": ForecastTrainingContext(
        training_dataset=[
            200.0,
            210.0,
            220.0,
        ],
        target_column="workload",
        forecast_horizon=1,
    ),
    "baseline_moving_average": ForecastTrainingContext(
        training_dataset=[
            60.0,
            70.0,
            80.0,
            90.0,
        ],
        target_column="workload",
        forecast_horizon=1,
    ),
}

retraining_results = orchestrator.train_many(
    models=models,
    contexts=retraining_contexts,
    reset_existing=True,
)

assert all(
    result.succeeded
    for result in retraining_results.values()
)

assert naive_model.estimator.last_value == 220.0

assert moving_average_model.estimator.history == (
    70.0,
    80.0,
    90.0,
)

assert moving_average_model.estimator.moving_average == 80.0


# ----------------------------------------------------------
# Invalid collection requests
# ----------------------------------------------------------

try:
    orchestrator.train_many(
        models=[],
        contexts={},
    )

except ForecastTrainingError as exc:
    assert "models must be a mapping" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastTrainingError for invalid models."
    )


try:
    orchestrator.train_many(
        models={},
        contexts={},
    )

except ForecastTrainingError as exc:
    assert "at least one" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastTrainingError for empty models."
    )


try:
    orchestrator.train_many(
        models={
            "model_a": NaiveForecastModel(),
        },
        contexts={
            "model_b": ForecastTrainingContext(
                training_dataset=[1.0],
            ),
        },
    )

except ForecastTrainingError as exc:
    assert (
        "execution keys must match"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for mismatched keys."
    )


try:
    orchestrator.train_many(
        models={
            "invalid": "not-a-model",
        },
        contexts={
            "invalid": ForecastTrainingContext(
                training_dataset=[1.0],
            ),
        },
    )

except ForecastTrainingError as exc:
    assert (
        "EnterpriseForecastModel"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastTrainingError for an invalid model."
    )


# ----------------------------------------------------------
# Fail-fast orchestration behavior
# ----------------------------------------------------------

successful_before_failure = NaiveForecastModel()
failing_model = NaiveForecastModel()
not_executed_model = NaiveForecastModel()

failure_models = {
    "successful_execution": successful_before_failure,
    "failing_execution": failing_model,
    "not_executed": not_executed_model,
}

failure_contexts = {
    "successful_execution": ForecastTrainingContext(
        training_dataset=[
            1.0,
            2.0,
            3.0,
        ],
        target_column="workload",
    ),
    "failing_execution": ForecastTrainingContext(
        training_dataset=[],
        target_column="workload",
    ),
    "not_executed": ForecastTrainingContext(
        training_dataset=[
            7.0,
            8.0,
            9.0,
        ],
        target_column="workload",
    ),
}

try:
    orchestrator.train_many(
        models=failure_models,
        contexts=failure_contexts,
    )

except ForecastTrainingError as exc:
    assert (
        "orchestration failed"
        in str(exc)
    )

    assert isinstance(
        exc.__cause__,
        ForecastTrainingError,
    )

    assert exc.context[
        "execution_key"
    ] == "failing_execution"

    assert exc.context[
        "completed_executions"
    ] == (
        "successful_execution",
    )

else:
    raise AssertionError(
        "Expected fail-fast orchestration failure."
    )


assert successful_before_failure.state == (
    ForecastModelState.TRAINED
)

assert failing_model.state != ForecastModelState.TRAINED

assert not_executed_model.state == (
    ForecastModelState.CREATED
)


print(
    "forecast/training/orchestrator.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

for module_name in (
    "src.forecast.training.callbacks",
    "src.forecast.training",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.training.callbacks import (
    TrainingCallback,
)


callback = TrainingCallback()

assert callback.on_training_started(
    model=None,
    context=None,
) is None

assert callback.on_epoch_completed(
    epoch=1,
    metrics={},
) is None

assert callback.on_training_completed(
    model=None,
    artifact=None,
) is None

try:
    raise RuntimeError("training failed")

except RuntimeError as exc:

    assert callback.on_training_failed(
        model=None,
        exception=exc,
    ) is None

else:
    raise AssertionError(
        "Expected RuntimeError."
    )

print(
    "forecast/training/callbacks.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys

for module_name in (
    "src.forecast.training",
    "src.forecast.training.trainer",
    "src.forecast.training.orchestrator",
    "src.forecast.training.callbacks",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

import src.forecast.training as training


assert training.EnterpriseForecastTrainer is not None

assert (
    training.EnterpriseForecastTrainingOrchestrator
    is not None
)

assert training.TrainingCallback is not None


assert callable(
    training.EnterpriseForecastTrainer
)

assert callable(
    training.EnterpriseForecastTrainingOrchestrator
)

assert callable(
    training.TrainingCallback
)


assert set(training.__all__) == {
    "EnterpriseForecastTrainer",
    "EnterpriseForecastTrainingOrchestrator",
    "TrainingCallback",
}


print("src.forecast.training package import: PASSED")
print("src.forecast.training __init__.py validation: PASSED")

# COMMAND ----------

import importlib
import math
import sys
from dataclasses import FrozenInstanceError

module_name = "src.forecast.modeling.metrics"

sys.modules.pop(module_name, None)
importlib.invalidate_caches()

metrics_module = importlib.import_module(
    module_name
)

ForecastMetrics = metrics_module.ForecastMetrics


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

metrics = ForecastMetrics(
    mae=2.0,
    mse=5.0,
    rmse=math.sqrt(5.0),
    bias=-1.0,
    mape=10.0,
    smape=9.5,
    wape=8.0,
)

assert metrics.mae == 2.0
assert metrics.mse == 5.0
assert metrics.rmse == math.sqrt(5.0)
assert metrics.bias == -1.0
assert metrics.mape == 10.0
assert metrics.smape == 9.5
assert metrics.wape == 8.0


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

metrics_dict = metrics.to_dict()

assert metrics_dict == {
    "mae": 2.0,
    "mse": 5.0,
    "rmse": math.sqrt(5.0),
    "bias": -1.0,
    "mape": 10.0,
    "smape": 9.5,
    "wape": 8.0,
}

assert metrics.as_mapping() == metrics_dict

assert metrics.get("MAE") == 2.0
assert metrics.get(" rmse ") == math.sqrt(5.0)
assert metrics.get("bias") == -1.0


# ----------------------------------------------------------
# Metadata payload
# ----------------------------------------------------------

payload = metrics.with_metadata(
    {
        "model_key": "random_forest",
        "split": "validation",
    }
)

assert payload["metrics"] == metrics_dict

assert payload["metadata"] == {
    "model_key": "random_forest",
    "split": "validation",
}


# ----------------------------------------------------------
# Immutability
# ----------------------------------------------------------

try:
    metrics.mae = 99.0

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastMetrics must be immutable."
    )


# ----------------------------------------------------------
# Validation behavior
# ----------------------------------------------------------

try:
    ForecastMetrics(
        mae=float("nan"),
        mse=1.0,
        rmse=1.0,
        bias=0.0,
        mape=0.0,
        smape=0.0,
        wape=0.0,
    )

except ValueError as exc:
    assert "mae must be finite" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for NaN."
    )


try:
    ForecastMetrics(
        mae=True,
        mse=1.0,
        rmse=1.0,
        bias=0.0,
        mape=0.0,
        smape=0.0,
        wape=0.0,
    )

except TypeError as exc:
    assert "mae must be a numeric value" in str(exc)

else:
    raise AssertionError(
        "Expected TypeError for a boolean metric."
    )


try:
    metrics.get("unsupported")

except KeyError as exc:
    assert "Unsupported forecast metric" in str(exc)

else:
    raise AssertionError(
        "Expected KeyError for an unsupported metric."
    )


try:
    metrics.get(123)

except TypeError as exc:
    assert "metric_name must be a string" in str(exc)

else:
    raise AssertionError(
        "Expected TypeError for an invalid metric name."
    )


print(
    "forecast/modeling/metrics.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys

import numpy as np


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.evaluation.metrics",
    "src.forecast.modeling.metrics",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

from src.forecast.evaluation.metrics import (
    EnterpriseForecastMetrics,
)
from src.forecast.modeling.metrics import (
    ForecastMetrics,
)


# ----------------------------------------------------------
# Perfect predictions
# ----------------------------------------------------------

actual = [10.0, 20.0, 30.0]
predicted = [10.0, 20.0, 30.0]

perfect_metrics = EnterpriseForecastMetrics.evaluate(
    actual=actual,
    predicted=predicted,
)

assert isinstance(
    perfect_metrics,
    ForecastMetrics,
)

assert perfect_metrics.mae == 0.0
assert perfect_metrics.mse == 0.0
assert perfect_metrics.rmse == 0.0
assert perfect_metrics.bias == 0.0
assert perfect_metrics.mape == 0.0
assert perfect_metrics.smape == 0.0
assert perfect_metrics.wape == 0.0


# ----------------------------------------------------------
# Normal forecast evaluation
# ----------------------------------------------------------

actual = np.array(
    [100.0, 200.0, 300.0],
    dtype=float,
)

predicted = np.array(
    [110.0, 190.0, 320.0],
    dtype=float,
)

metrics = EnterpriseForecastMetrics.evaluate(
    actual=actual,
    predicted=predicted,
)

expected_mae = (
    10.0 + 10.0 + 20.0
) / 3.0

expected_mse = (
    100.0 + 100.0 + 400.0
) / 3.0

expected_rmse = math.sqrt(
    expected_mse
)

expected_bias = (
    10.0 - 10.0 + 20.0
) / 3.0

expected_mape = (
    (
        10.0 / 100.0
        + 10.0 / 200.0
        + 20.0 / 300.0
    )
    / 3.0
    * 100.0
)

expected_smape = (
    (
        200.0 * 10.0 / 210.0
        + 200.0 * 10.0 / 390.0
        + 200.0 * 20.0 / 620.0
    )
    / 3.0
)

expected_wape = (
    40.0 / 600.0 * 100.0
)

assert math.isclose(
    metrics.mae,
    expected_mae,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.mse,
    expected_mse,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.rmse,
    expected_rmse,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.bias,
    expected_bias,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.mape,
    expected_mape,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.smape,
    expected_smape,
    rel_tol=1e-12,
)

assert math.isclose(
    metrics.wape,
    expected_wape,
    rel_tol=1e-12,
)


# ----------------------------------------------------------
# Individual metric methods
# ----------------------------------------------------------

validated_actual, validated_predicted = (
    EnterpriseForecastMetrics.validate_inputs(
        actual,
        predicted,
    )
)

assert isinstance(
    validated_actual,
    np.ndarray,
)

assert isinstance(
    validated_predicted,
    np.ndarray,
)

assert validated_actual.dtype == np.float64
assert validated_predicted.dtype == np.float64

assert math.isclose(
    EnterpriseForecastMetrics.mae(
        validated_actual,
        validated_predicted,
    ),
    expected_mae,
    rel_tol=1e-12,
)

assert math.isclose(
    EnterpriseForecastMetrics.mse(
        validated_actual,
        validated_predicted,
    ),
    expected_mse,
    rel_tol=1e-12,
)

assert math.isclose(
    EnterpriseForecastMetrics.rmse(
        validated_actual,
        validated_predicted,
    ),
    expected_rmse,
    rel_tol=1e-12,
)

assert math.isclose(
    EnterpriseForecastMetrics.bias(
        validated_actual,
        validated_predicted,
    ),
    expected_bias,
    rel_tol=1e-12,
)


# ----------------------------------------------------------
# Zero-target handling
# ----------------------------------------------------------

zero_actual = np.array(
    [0.0, 100.0, 0.0],
)

zero_predicted = np.array(
    [10.0, 110.0, 0.0],
)

zero_metrics = EnterpriseForecastMetrics.evaluate(
    actual=zero_actual,
    predicted=zero_predicted,
)

assert math.isclose(
    zero_metrics.mape,
    10.0,
    rel_tol=1e-12,
)

assert math.isfinite(
    zero_metrics.smape
)

assert math.isfinite(
    zero_metrics.wape
)


# ----------------------------------------------------------
# All-zero denominator handling
# ----------------------------------------------------------

all_zero_metrics = EnterpriseForecastMetrics.evaluate(
    actual=[0.0, 0.0],
    predicted=[0.0, 0.0],
)

assert all_zero_metrics.mape == 0.0
assert all_zero_metrics.smape == 0.0
assert all_zero_metrics.wape == 0.0


# ----------------------------------------------------------
# Tuple input support
# ----------------------------------------------------------

tuple_metrics = EnterpriseForecastMetrics.evaluate(
    actual=(1.0, 2.0, 3.0),
    predicted=(1.0, 2.0, 4.0),
)

assert isinstance(
    tuple_metrics,
    ForecastMetrics,
)

assert tuple_metrics.mae > 0.0


# ----------------------------------------------------------
# Empty input rejection
# ----------------------------------------------------------

try:
    EnterpriseForecastMetrics.evaluate(
        actual=[],
        predicted=[],
    )

except ValueError as exc:
    assert "cannot be empty" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for empty inputs."
    )


# ----------------------------------------------------------
# Length mismatch rejection
# ----------------------------------------------------------

try:
    EnterpriseForecastMetrics.evaluate(
        actual=[1.0, 2.0],
        predicted=[1.0],
    )

except ValueError as exc:
    assert "identical lengths" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for mismatched lengths."
    )


# ----------------------------------------------------------
# Dimensionality validation
# ----------------------------------------------------------

try:
    EnterpriseForecastMetrics.evaluate(
        actual=[
            [1.0, 2.0],
            [3.0, 4.0],
        ],
        predicted=[
            [1.0, 2.0],
            [3.0, 4.0],
        ],
    )

except ValueError as exc:
    assert "one-dimensional" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for multidimensional input."
    )


# ----------------------------------------------------------
# Non-numeric input rejection
# ----------------------------------------------------------

try:
    EnterpriseForecastMetrics.evaluate(
        actual=["a", "b"],
        predicted=[1.0, 2.0],
    )

except (TypeError, ValueError):
    pass

else:
    raise AssertionError(
        "Expected failure for non-numeric input."
    )


# ----------------------------------------------------------
# Non-finite input rejection
# ----------------------------------------------------------

try:
    EnterpriseForecastMetrics.evaluate(
        actual=[1.0, float("nan")],
        predicted=[1.0, 2.0],
    )

except ValueError as exc:
    assert "non-finite" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for NaN input."
    )


try:
    EnterpriseForecastMetrics.evaluate(
        actual=[1.0, 2.0],
        predicted=[1.0, float("inf")],
    )

except ValueError as exc:
    assert "non-finite" in str(exc)

else:
    raise AssertionError(
        "Expected ValueError for infinite input."
    )


# ----------------------------------------------------------
# Statelessness
# ----------------------------------------------------------

assert vars(
    EnterpriseForecastMetrics()
) == {}


print(
    "forecast/evaluation/metrics.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
from dataclasses import FrozenInstanceError


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.evaluation.evaluator",
    "src.forecast.evaluation.metrics",
    "src.forecast.evaluation",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

evaluator_module = importlib.import_module(
    "src.forecast.evaluation.evaluator"
)

EnterpriseForecastEvaluator = (
    evaluator_module.EnterpriseForecastEvaluator
)

from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
)
from src.forecast.modeling.exceptions import (
    ForecastEvaluationError,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
)


# ----------------------------------------------------------
# Construction
# ----------------------------------------------------------

evaluator = EnterpriseForecastEvaluator()

assert isinstance(
    evaluator,
    EnterpriseForecastEvaluator,
)

assert vars(evaluator) == {}


# ----------------------------------------------------------
# Successful evaluation
# ----------------------------------------------------------

context = ForecastEvaluationContext(
    actual_values=[
        100.0,
        200.0,
        300.0,
    ],
    predicted_values=[
        110.0,
        190.0,
        320.0,
    ],
    metric="rmse",
    metadata={
        "dataset": "validation",
        "forecast_horizon": 7,
        "target_column": "order_line_count",
    },
)

result = evaluator.evaluate(
    model_name="random_forest",
    model_version="1.0.0",
    context=context,
)

assert isinstance(
    result,
    ForecastEvaluationResult,
)

assert result.model_name == "random_forest"
assert result.model_version == "1.0.0"

assert result.status == (
    ForecastExecutionStatus.SUCCESS
)

assert result.succeeded is True

assert result.primary_metric == "rmse"

expected_mse = (
    100.0
    + 100.0
    + 400.0
) / 3.0

expected_rmse = math.sqrt(
    expected_mse
)

assert math.isclose(
    result.primary_metric_value,
    expected_rmse,
    rel_tol=1e-12,
)

assert result.evaluation_records == 3

assert set(result.metrics) == {
    "mae",
    "mse",
    "rmse",
    "bias",
    "mape",
    "smape",
    "wape",
}

assert math.isclose(
    result.metrics["mse"],
    expected_mse,
    rel_tol=1e-12,
)

assert math.isclose(
    result.metrics["rmse"],
    expected_rmse,
    rel_tol=1e-12,
)

assert result.metadata["dataset"] == "validation"

assert result.metadata[
    "forecast_horizon"
] == 7

assert (
    result.metadata["target_column"]
    == "order_line_count"
)

assert (
    result.metadata["evaluation_timestamp"]
    == context.evaluation_timestamp.isoformat()
)


# ----------------------------------------------------------
# Residual diagnostics
# ----------------------------------------------------------

# Residuals: [-10, 10, -20]
assert math.isclose(
    result.residual_summary["mean"],
    -20.0 / 3.0,
    rel_tol=1e-12,
)

assert result.residual_summary[
    "minimum"
] == -20.0

assert result.residual_summary[
    "maximum"
] == 10.0

assert result.residual_summary[
    "standard_deviation"
] >= 0.0


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

result_payload = result.to_dict()

assert result_payload["model_name"] == (
    "random_forest"
)

assert result_payload["status"] == "SUCCESS"

assert result_payload["succeeded"] is True

assert result_payload["metrics"] == dict(
    result.metrics
)

assert result_payload["evaluation_records"] == 3


# ----------------------------------------------------------
# Result immutability
# ----------------------------------------------------------

try:
    result.model_name = "changed"

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastEvaluationResult must be immutable."
    )


# ----------------------------------------------------------
# Case-insensitive primary metric
# ----------------------------------------------------------

uppercase_context = ForecastEvaluationContext(
    actual_values=[
        10.0,
        20.0,
    ],
    predicted_values=[
        10.0,
        22.0,
    ],
    metric=" MAE ",
)

uppercase_result = evaluator.evaluate(
    model_name="naive_last_value",
    model_version="1.0.0",
    context=uppercase_context,
)

assert uppercase_result.primary_metric == "mae"

assert math.isclose(
    uppercase_result.primary_metric_value,
    1.0,
    rel_tol=1e-12,
)


# ----------------------------------------------------------
# Perfect predictions
# ----------------------------------------------------------

perfect_context = ForecastEvaluationContext(
    actual_values=[
        10.0,
        20.0,
        30.0,
    ],
    predicted_values=[
        10.0,
        20.0,
        30.0,
    ],
    metric="wape",
)

perfect_result = evaluator.evaluate(
    model_name="perfect_model",
    model_version="1.0.0",
    context=perfect_context,
)

assert perfect_result.primary_metric_value == 0.0

assert all(
    value == 0.0
    for value in perfect_result.metrics.values()
)

assert all(
    value == 0.0
    for value in (
        perfect_result.residual_summary["mean"],
        perfect_result.residual_summary["minimum"],
        perfect_result.residual_summary["maximum"],
        perfect_result.residual_summary[
            "standard_deviation"
        ],
    )
)


# ----------------------------------------------------------
# Invalid model identity
# ----------------------------------------------------------

try:
    evaluator.evaluate(
        model_name="",
        model_version="1.0.0",
        context=context,
    )

except ForecastEvaluationError as exc:
    assert "model_name must not be empty" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for an empty model name."
    )


try:
    evaluator.evaluate(
        model_name="random_forest",
        model_version="",
        context=context,
    )

except ForecastEvaluationError as exc:
    assert "model_version must not be empty" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for an empty model version."
    )


# ----------------------------------------------------------
# Invalid context
# ----------------------------------------------------------

try:
    evaluator.evaluate(
        model_name="random_forest",
        model_version="1.0.0",
        context=None,
    )

except ForecastEvaluationError as exc:
    assert "cannot be None" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for a null context."
    )


try:
    evaluator.evaluate(
        model_name="random_forest",
        model_version="1.0.0",
        context={
            "actual_values": [1.0],
            "predicted_values": [1.0],
        },
    )

except ForecastEvaluationError as exc:
    assert (
        "ForecastEvaluationContext"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for an invalid context."
    )


# ----------------------------------------------------------
# Unsupported metric
# ----------------------------------------------------------

unsupported_context = ForecastEvaluationContext(
    actual_values=[
        1.0,
        2.0,
    ],
    predicted_values=[
        1.0,
        2.0,
    ],
    metric="unsupported_metric",
)

try:
    evaluator.evaluate(
        model_name="random_forest",
        model_version="1.0.0",
        context=unsupported_context,
    )

except ForecastEvaluationError as exc:
    assert (
        "Unsupported primary evaluation metric"
        in str(exc)
    )

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for an unsupported metric."
    )


# ----------------------------------------------------------
# Metric execution failure wrapping
# ----------------------------------------------------------

invalid_values_context = ForecastEvaluationContext(
    actual_values=[],
    predicted_values=[],
    metric="mae",
)

try:
    evaluator.evaluate(
        model_name="random_forest",
        model_version="1.0.0",
        context=invalid_values_context,
    )

except ForecastEvaluationError as exc:
    assert (
        "Enterprise forecast evaluation failed"
        in str(exc)
    )

    assert isinstance(
        exc.__cause__,
        ValueError,
    )

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for invalid values."
    )


print(
    "forecast/evaluation/evaluator.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
from dataclasses import FrozenInstanceError


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.evaluation.comparison",
    "src.forecast.evaluation.evaluator",
    "src.forecast.evaluation.metrics",
    "src.forecast.evaluation",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

comparison_module = importlib.import_module(
    "src.forecast.evaluation.comparison"
)

EnterpriseForecastComparison = (
    comparison_module.EnterpriseForecastComparison
)

ForecastComparisonResult = (
    comparison_module.ForecastComparisonResult
)

from src.forecast.evaluation.evaluator import (
    EnterpriseForecastEvaluator,
)
from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
)
from src.forecast.modeling.exceptions import (
    ForecastEvaluationError,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
)


# ----------------------------------------------------------
# Build evaluation results
# ----------------------------------------------------------

evaluator = EnterpriseForecastEvaluator()

random_forest_result = evaluator.evaluate(
    model_name="random_forest",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
            300.0,
        ],
        predicted_values=[
            110.0,
            190.0,
            310.0,
        ],
        metric="rmse",
    ),
)

linear_regression_result = evaluator.evaluate(
    model_name="linear_regression",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
            300.0,
        ],
        predicted_values=[
            105.0,
            195.0,
            305.0,
        ],
        metric="rmse",
    ),
)

naive_result = evaluator.evaluate(
    model_name="naive_last_value",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
            300.0,
        ],
        predicted_values=[
            120.0,
            180.0,
            320.0,
        ],
        metric="rmse",
    ),
)


# ----------------------------------------------------------
# Construction and statelessness
# ----------------------------------------------------------

comparison = EnterpriseForecastComparison()

assert vars(comparison) == {}


# ----------------------------------------------------------
# Standard comparison
# ----------------------------------------------------------

comparison_result = comparison.compare(
    evaluations=[
        random_forest_result,
        naive_result,
        linear_regression_result,
    ],
    metric=" RMSE ",
    metadata={
        "dataset": "validation",
        "forecast_horizon": 7,
    },
)

assert isinstance(
    comparison_result,
    ForecastComparisonResult,
)

assert comparison_result.metric == "rmse"
assert comparison_result.total_models == 3

assert comparison_result.champion_model_name == (
    "linear_regression"
)

assert comparison_result.champion_model_version == (
    "1.0.0"
)

assert comparison_result.champion.model_name == (
    "linear_regression"
)

assert comparison_result.runner_up is not None

assert comparison_result.runner_up.model_name == (
    "random_forest"
)

assert tuple(
    result.model_name
    for result in comparison_result.ordered_results
) == (
    "linear_regression",
    "random_forest",
    "naive_last_value",
)

assert tuple(
    result.rank
    for result in comparison_result.ordered_results
) == (
    1,
    2,
    3,
)

assert tuple(
    result.champion
    for result in comparison_result.ordered_results
) == (
    True,
    False,
    False,
)

assert comparison_result.metadata == {
    "dataset": "validation",
    "forecast_horizon": 7,
}


# ----------------------------------------------------------
# Original results remain unchanged
# ----------------------------------------------------------

assert random_forest_result.rank is None
assert random_forest_result.champion is False

assert linear_regression_result.rank is None
assert linear_regression_result.champion is False

assert naive_result.rank is None
assert naive_result.champion is False


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

payload = comparison_result.to_dict()

assert payload["metric"] == "rmse"
assert payload["total_models"] == 3

assert payload["champion_model_name"] == (
    "linear_regression"
)

assert len(payload["ordered_results"]) == 3

assert payload["ordered_results"][0]["rank"] == 1

assert payload["ordered_results"][0][
    "champion"
] is True


# ----------------------------------------------------------
# Immutability
# ----------------------------------------------------------

try:
    comparison_result.metric = "mae"

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastComparisonResult must be immutable."
    )


# ----------------------------------------------------------
# Deterministic tie handling
# ----------------------------------------------------------

alpha_result = evaluator.evaluate(
    model_name="alpha_model",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            10.0,
            20.0,
        ],
        predicted_values=[
            11.0,
            19.0,
        ],
        metric="mae",
    ),
)

beta_result = evaluator.evaluate(
    model_name="beta_model",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            10.0,
            20.0,
        ],
        predicted_values=[
            9.0,
            21.0,
        ],
        metric="mae",
    ),
)

assert math.isclose(
    alpha_result.metrics["mae"],
    beta_result.metrics["mae"],
    rel_tol=1e-12,
)

tie_result = comparison.compare(
    evaluations=[
        beta_result,
        alpha_result,
    ],
    metric="mae",
)

assert tuple(
    result.model_name
    for result in tie_result.ordered_results
) == (
    "alpha_model",
    "beta_model",
)

assert tie_result.champion.model_name == (
    "alpha_model"
)


# ----------------------------------------------------------
# Absolute-bias ranking
# ----------------------------------------------------------

low_bias_result = evaluator.evaluate(
    model_name="low_bias",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            10.0,
            20.0,
        ],
        predicted_values=[
            11.0,
            21.0,
        ],
        metric="bias",
    ),
)

high_negative_bias_result = evaluator.evaluate(
    model_name="high_negative_bias",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            10.0,
            20.0,
        ],
        predicted_values=[
            5.0,
            15.0,
        ],
        metric="bias",
    ),
)

bias_comparison = comparison.compare(
    evaluations=[
        high_negative_bias_result,
        low_bias_result,
    ],
    metric="bias",
)

assert bias_comparison.champion.model_name == (
    "low_bias"
)


# ----------------------------------------------------------
# Single-model comparison
# ----------------------------------------------------------

single_result = comparison.compare(
    evaluations=[
        random_forest_result,
    ],
    metric="rmse",
)

assert single_result.total_models == 1
assert single_result.champion.rank == 1
assert single_result.champion.champion is True
assert single_result.runner_up is None


# ----------------------------------------------------------
# Empty comparison rejection
# ----------------------------------------------------------

try:
    comparison.compare(
        evaluations=[],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "At least one" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for empty evaluations."
    )


# ----------------------------------------------------------
# Unsupported metric rejection
# ----------------------------------------------------------

try:
    comparison.compare(
        evaluations=[
            random_forest_result,
        ],
        metric="unsupported",
    )

except ForecastEvaluationError as exc:
    assert "Unsupported comparison metric" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for unsupported metric."
    )


# ----------------------------------------------------------
# Duplicate model rejection
# ----------------------------------------------------------

duplicate_result = evaluator.evaluate(
    model_name="random_forest",
    model_version="2.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
        ],
        predicted_values=[
            100.0,
            200.0,
        ],
        metric="rmse",
    ),
)

try:
    comparison.compare(
        evaluations=[
            random_forest_result,
            duplicate_result,
        ],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "Duplicate model names" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for duplicate models."
    )


# ----------------------------------------------------------
# Invalid evaluation object rejection
# ----------------------------------------------------------

try:
    comparison.compare(
        evaluations=[
            random_forest_result,
            "invalid-result",
        ],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "ForecastEvaluationResult" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for invalid result."
    )


# ----------------------------------------------------------
# Failed evaluation rejection
# ----------------------------------------------------------

failed_result = ForecastEvaluationResult(
    model_name="failed_model",
    model_version="1.0.0",
    status=ForecastExecutionStatus.FAILED,
    metrics={
        "rmse": 99.0,
    },
)

try:
    comparison.compare(
        evaluations=[
            failed_result,
        ],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "Only successful" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for failed evaluation."
    )


# ----------------------------------------------------------
# Missing metric rejection
# ----------------------------------------------------------

missing_metric_result = ForecastEvaluationResult(
    model_name="missing_metric_model",
    model_version="1.0.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={
        "mae": 1.0,
    },
)

try:
    comparison.compare(
        evaluations=[
            missing_metric_result,
        ],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "missing the comparison metric" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for missing metric."
    )


# ----------------------------------------------------------
# Non-finite metric rejection
# ----------------------------------------------------------

non_finite_result = ForecastEvaluationResult(
    model_name="non_finite_model",
    model_version="1.0.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={
        "rmse": float("nan"),
    },
)

try:
    comparison.compare(
        evaluations=[
            non_finite_result,
        ],
        metric="rmse",
    )

except ForecastEvaluationError as exc:
    assert "must be finite" in str(exc)

else:
    raise AssertionError(
        "Expected ForecastEvaluationError for non-finite metric."
    )


print(
    "forecast/evaluation/comparison.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys


# ----------------------------------------------------------
# Fresh package import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.evaluation.comparison",
    "src.forecast.evaluation.evaluator",
    "src.forecast.evaluation.metrics",
    "src.forecast.evaluation",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

evaluation_package = importlib.import_module(
    "src.forecast.evaluation"
)


# ----------------------------------------------------------
# Public package exports
# ----------------------------------------------------------

expected_exports = {
    "EnterpriseForecastComparison",
    "EnterpriseForecastEvaluator",
    "EnterpriseForecastMetrics",
    "ForecastComparisonResult",
}

assert set(evaluation_package.__all__) == expected_exports

for export_name in expected_exports:
    assert hasattr(
        evaluation_package,
        export_name,
    ), (
        f"src.forecast.evaluation is missing public export: "
        f"{export_name}"
    )


# ----------------------------------------------------------
# Public import compatibility
# ----------------------------------------------------------

from src.forecast.evaluation import (
    EnterpriseForecastComparison,
    EnterpriseForecastEvaluator,
    EnterpriseForecastMetrics,
    ForecastComparisonResult,
)

from src.forecast.evaluation.comparison import (
    EnterpriseForecastComparison as DirectComparison,
)
from src.forecast.evaluation.comparison import (
    ForecastComparisonResult as DirectComparisonResult,
)
from src.forecast.evaluation.evaluator import (
    EnterpriseForecastEvaluator as DirectEvaluator,
)
from src.forecast.evaluation.metrics import (
    EnterpriseForecastMetrics as DirectMetrics,
)

assert EnterpriseForecastComparison is DirectComparison
assert ForecastComparisonResult is DirectComparisonResult
assert EnterpriseForecastEvaluator is DirectEvaluator
assert EnterpriseForecastMetrics is DirectMetrics


# ----------------------------------------------------------
# Service construction
# ----------------------------------------------------------

comparison = EnterpriseForecastComparison()
evaluator = EnterpriseForecastEvaluator()

assert vars(comparison) == {}
assert vars(evaluator) == {}


# ----------------------------------------------------------
# Metric engine availability
# ----------------------------------------------------------

metrics = EnterpriseForecastMetrics.evaluate(
    actual=[
        100.0,
        200.0,
        300.0,
    ],
    predicted=[
        110.0,
        190.0,
        310.0,
    ],
)

assert metrics.mae == 10.0
assert metrics.mse == 100.0
assert metrics.rmse == 10.0


# ----------------------------------------------------------
# End-to-end evaluation package workflow
# ----------------------------------------------------------

from src.forecast.modeling.contexts import (
    ForecastEvaluationContext,
)

linear_result = evaluator.evaluate(
    model_name="linear_regression",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
            300.0,
        ],
        predicted_values=[
            105.0,
            195.0,
            305.0,
        ],
        metric="rmse",
    ),
)

random_forest_result = evaluator.evaluate(
    model_name="random_forest",
    model_version="1.0.0",
    context=ForecastEvaluationContext(
        actual_values=[
            100.0,
            200.0,
            300.0,
        ],
        predicted_values=[
            110.0,
            190.0,
            310.0,
        ],
        metric="rmse",
    ),
)

comparison_result = comparison.compare(
    evaluations=[
        random_forest_result,
        linear_result,
    ],
    metric="rmse",
    metadata={
        "validation_scope": "evaluation_package",
    },
)

assert isinstance(
    comparison_result,
    ForecastComparisonResult,
)

assert comparison_result.total_models == 2

assert comparison_result.champion_model_name == (
    "linear_regression"
)

assert comparison_result.champion.rank == 1
assert comparison_result.champion.champion is True

assert comparison_result.runner_up is not None
assert comparison_result.runner_up.rank == 2
assert comparison_result.runner_up.champion is False

assert comparison_result.metadata == {
    "validation_scope": "evaluation_package",
}


# ----------------------------------------------------------
# Serialization boundary
# ----------------------------------------------------------

payload = comparison_result.to_dict()

assert payload["metric"] == "rmse"
assert payload["total_models"] == 2

assert payload["champion_model_name"] == (
    "linear_regression"
)

assert len(payload["ordered_results"]) == 2

assert payload["ordered_results"][0][
    "champion"
] is True


print(
    "forecast/evaluation/__init__.py validation: PASSED"
)

# COMMAND ----------

import importlib
import math
import sys
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from os import PathLike
from typing import Any, Self


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.inference.predictor",
    "src.forecast.inference",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

predictor_module = importlib.import_module(
    "src.forecast.inference.predictor"
)

EnterpriseForecastPredictor = (
    predictor_module.EnterpriseForecastPredictor
)


from src.forecast.modeling.artifacts import (
    ForecastArtifact,
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
    ForecastInferenceError,
    ForecastPredictionError,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


# ----------------------------------------------------------
# Validation model base
# ----------------------------------------------------------

class ValidationForecastModel(BaseForecastModel):
    """
    Minimal concrete model used to validate inference orchestration.

    The model intentionally implements the complete BaseForecastModel
    interface while keeping algorithm behavior deterministic.
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        multiplier: float,
        state: ForecastModelState = ForecastModelState.TRAINED,
        return_mode: str = "success",
    ) -> None:
        self._name = name
        self._version = version
        self._multiplier = multiplier
        self._state = state
        self._return_mode = return_mode

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def model_version(self) -> str:
        return self._version

    @property
    def model_category(self) -> ForecastModelCategory:
        return ForecastModelCategory.CUSTOM

    @property
    def capabilities(
        self,
    ) -> frozenset[ForecastModelCapability]:
        return frozenset(
            {
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.MULTI_STEP_FORECAST,
            }
        )

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
        )

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        if self._return_mode == "prediction_error":
            raise ForecastPredictionError(
                "Validation model prediction failed."
            )

        if self._return_mode == "generic_error":
            raise RuntimeError(
                "Unexpected validation failure."
            )

        if self._return_mode == "invalid_object":
            return "invalid-result"  # type: ignore[return-value]

        base_values = tuple(
            float(index + 1) * self._multiplier
            for index in range(context.forecast_horizon)
        )

        timestamps = tuple(
            context.prediction_timestamp
            + timedelta(days=index + 1)
            for index in range(context.forecast_horizon)
        )

        if self._return_mode == "failed_result":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.FAILED,
                forecast_horizon=context.forecast_horizon,
                error={
                    "message": "Validation failure",
                },
            )

        if self._return_mode == "wrong_model":
            return ForecastPredictionResult(
                model_name="wrong_model",
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=base_values,
                forecast_horizon=context.forecast_horizon,
                prediction_timestamps=timestamps,
            )

        if self._return_mode == "empty_predictions":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=(),
                forecast_horizon=context.forecast_horizon,
            )

        if self._return_mode == "non_finite":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=(
                    float("nan"),
                    *base_values[1:],
                ),
                forecast_horizon=context.forecast_horizon,
            )

        if self._return_mode == "wrong_horizon":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=base_values,
                forecast_horizon=(
                    context.forecast_horizon + 1
                ),
            )

        if self._return_mode == "bad_timestamps":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=base_values,
                forecast_horizon=context.forecast_horizon,
                prediction_timestamps=timestamps[:-1],
            )

        if self._return_mode == "bad_intervals":
            return ForecastPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                status=ForecastExecutionStatus.SUCCESS,
                predictions=base_values,
                forecast_horizon=context.forecast_horizon,
                prediction_timestamps=timestamps,
                lower_bounds=tuple(
                    value + 1.0
                    for value in base_values
                ),
                upper_bounds=tuple(
                    value + 2.0
                    for value in base_values
                ),
            )

        return ForecastPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            predictions=base_values,
            forecast_horizon=context.forecast_horizon,
            prediction_timestamps=timestamps,
            lower_bounds=tuple(
                value - 0.5
                for value in base_values
            ),
            upper_bounds=tuple(
                value + 0.5
                for value in base_values
            ),
            inference_duration_seconds=0.01,
            artifact_id=(
                f"{self.model_name}-artifact"
            ),
            metadata={
                **dict(context.metadata),
                "validation_model": self.model_name,
            },
        )

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        return ForecastEvaluationResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
        )

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        raise NotImplementedError(
            "Persistence is outside predictor validation."
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        raise NotImplementedError(
            "Loading is outside predictor validation."
        )

    def get_metadata(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "multiplier": self._multiplier,
        }


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_inference_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastInferenceError:
    try:
        callable_object()

    except ForecastInferenceError as exc:
        assert message_contains in str(exc)
        return exc

    else:
        raise AssertionError(
            "Expected ForecastInferenceError."
        )


# ----------------------------------------------------------
# Predictor construction and statelessness
# ----------------------------------------------------------

predictor = EnterpriseForecastPredictor()

assert vars(predictor) == {}


# ----------------------------------------------------------
# Shared prediction context
# ----------------------------------------------------------

prediction_timestamp = datetime(
    2026,
    8,
    2,
    3,
    0,
    tzinfo=timezone.utc,
)

prediction_context = ForecastPredictionContext(
    prediction_dataset={
        "latest_observation": 100.0,
    },
    forecast_horizon=3,
    prediction_timestamp=prediction_timestamp,
    model_version="1.0.0",
    metadata={
        "dataset": "inference_validation",
        "forecast_horizon": 3,
    },
)


# ----------------------------------------------------------
# Algorithm-independent successful prediction
# ----------------------------------------------------------

naive_model = ValidationForecastModel(
    name="naive_last_value",
    version="1.0.0",
    multiplier=10.0,
)

linear_model = ValidationForecastModel(
    name="linear_regression",
    version="1.0.0",
    multiplier=25.0,
)

naive_result = predictor.predict(
    model=naive_model,
    context=prediction_context,
)

linear_result = predictor.predict(
    model=linear_model,
    context=prediction_context,
)

assert isinstance(
    naive_result,
    ForecastPredictionResult,
)

assert isinstance(
    linear_result,
    ForecastPredictionResult,
)

assert naive_result.model_name == "naive_last_value"
assert linear_result.model_name == "linear_regression"

assert tuple(naive_result.predictions) == (
    10.0,
    20.0,
    30.0,
)

assert tuple(linear_result.predictions) == (
    25.0,
    50.0,
    75.0,
)

assert naive_result.forecast_horizon == 3
assert linear_result.forecast_horizon == 3

assert len(naive_result.prediction_timestamps) == 3
assert len(linear_result.prediction_timestamps) == 3

assert naive_result.succeeded is True
assert linear_result.succeeded is True

assert naive_result.artifact_id == (
    "naive_last_value-artifact"
)

assert linear_result.artifact_id == (
    "linear_regression-artifact"
)

assert naive_result.metadata == {
    "dataset": "inference_validation",
    "forecast_horizon": 3,
    "validation_model": "naive_last_value",
}

assert linear_result.metadata == {
    "dataset": "inference_validation",
    "forecast_horizon": 3,
    "validation_model": "linear_regression",
}


# ----------------------------------------------------------
# Prediction result serialization
# ----------------------------------------------------------

payload = naive_result.to_dict()

assert payload["model_name"] == "naive_last_value"
assert payload["model_version"] == "1.0.0"
assert payload["status"] == "SUCCESS"
assert payload["succeeded"] is True
assert payload["predictions"] == [
    10.0,
    20.0,
    30.0,
]
assert payload["forecast_horizon"] == 3
assert len(payload["prediction_timestamps"]) == 3
assert payload["lower_bounds"] == [
    9.5,
    19.5,
    29.5,
]
assert payload["upper_bounds"] == [
    10.5,
    20.5,
    30.5,
]


# ----------------------------------------------------------
# Invalid model rejection
# ----------------------------------------------------------

assert_inference_error(
    lambda: predictor.predict(
        model=None,  # type: ignore[arg-type]
        context=prediction_context,
    ),
    message_contains="cannot be None",
)

assert_inference_error(
    lambda: predictor.predict(
        model="invalid-model",  # type: ignore[arg-type]
        context=prediction_context,
    ),
    message_contains="BaseForecastModel",
)


# ----------------------------------------------------------
# Uninitialized and untrained model rejection
# ----------------------------------------------------------

created_model = ValidationForecastModel(
    name="created_model",
    version="1.0.0",
    multiplier=1.0,
    state=ForecastModelState.CREATED,
)

assert_inference_error(
    lambda: predictor.predict(
        model=created_model,
        context=prediction_context,
    ),
    message_contains="must be initialized",
)

initialized_model = ValidationForecastModel(
    name="initialized_model",
    version="1.0.0",
    multiplier=1.0,
    state=ForecastModelState.INITIALIZED,
)

assert_inference_error(
    lambda: predictor.predict(
        model=initialized_model,
        context=prediction_context,
    ),
    message_contains="must be trained",
)


# ----------------------------------------------------------
# Invalid context rejection
# ----------------------------------------------------------

assert_inference_error(
    lambda: predictor.predict(
        model=naive_model,
        context=None,  # type: ignore[arg-type]
    ),
    message_contains="cannot be None",
)

assert_inference_error(
    lambda: predictor.predict(
        model=naive_model,
        context="invalid-context",  # type: ignore[arg-type]
    ),
    message_contains="ForecastPredictionContext",
)

assert_inference_error(
    lambda: predictor.predict(
        model=naive_model,
        context=ForecastPredictionContext(
            prediction_dataset=None,
            forecast_horizon=3,
        ),
    ),
    message_contains="dataset cannot be None",
)

assert_inference_error(
    lambda: predictor.predict(
        model=naive_model,
        context=ForecastPredictionContext(
            prediction_dataset={
                "value": 1.0,
            },
            forecast_horizon=0,
        ),
    ),
    message_contains="greater than zero",
)

assert_inference_error(
    lambda: predictor.predict(
        model=naive_model,
        context=ForecastPredictionContext(
            prediction_dataset={
                "value": 1.0,
            },
            forecast_horizon=3,
            model_version="2.0.0",
        ),
    ),
    message_contains="does not match",
)


# ----------------------------------------------------------
# Invalid returned object rejection
# ----------------------------------------------------------

invalid_object_model = ValidationForecastModel(
    name="invalid_object_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="invalid_object",
)

assert_inference_error(
    lambda: predictor.predict(
        model=invalid_object_model,
        context=prediction_context,
    ),
    message_contains="incompatible prediction result",
)


# ----------------------------------------------------------
# Failed result rejection
# ----------------------------------------------------------

failed_result_model = ValidationForecastModel(
    name="failed_result_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="failed_result",
)

assert_inference_error(
    lambda: predictor.predict(
        model=failed_result_model,
        context=prediction_context,
    ),
    message_contains="unsuccessful prediction result",
)


# ----------------------------------------------------------
# Result identity validation
# ----------------------------------------------------------

wrong_model_result = ValidationForecastModel(
    name="identity_validation_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="wrong_model",
)

assert_inference_error(
    lambda: predictor.predict(
        model=wrong_model_result,
        context=prediction_context,
    ),
    message_contains="model_name does not match",
)


# ----------------------------------------------------------
# Prediction payload validation
# ----------------------------------------------------------

empty_prediction_model = ValidationForecastModel(
    name="empty_prediction_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="empty_predictions",
)

assert_inference_error(
    lambda: predictor.predict(
        model=empty_prediction_model,
        context=prediction_context,
    ),
    message_contains="cannot be empty",
)

non_finite_model = ValidationForecastModel(
    name="non_finite_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="non_finite",
)

assert_inference_error(
    lambda: predictor.predict(
        model=non_finite_model,
        context=prediction_context,
    ),
    message_contains="finite values",
)

wrong_horizon_model = ValidationForecastModel(
    name="wrong_horizon_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="wrong_horizon",
)

assert_inference_error(
    lambda: predictor.predict(
        model=wrong_horizon_model,
        context=prediction_context,
    ),
    message_contains="does not match",
)

bad_timestamp_model = ValidationForecastModel(
    name="bad_timestamp_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="bad_timestamps",
)

assert_inference_error(
    lambda: predictor.predict(
        model=bad_timestamp_model,
        context=prediction_context,
    ),
    message_contains="timestamp count",
)

bad_interval_model = ValidationForecastModel(
    name="bad_interval_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="bad_intervals",
)

assert_inference_error(
    lambda: predictor.predict(
        model=bad_interval_model,
        context=prediction_context,
    ),
    message_contains="must fall within",
)


# ----------------------------------------------------------
# Prediction exception translation
# ----------------------------------------------------------

prediction_error_model = ValidationForecastModel(
    name="prediction_error_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="prediction_error",
)

translated_prediction_error = assert_inference_error(
    lambda: predictor.predict(
        model=prediction_error_model,
        context=prediction_context,
    ),
    message_contains="prediction execution failed",
)

assert isinstance(
    translated_prediction_error.cause,
    ForecastPredictionError,
)

generic_error_model = ValidationForecastModel(
    name="generic_error_model",
    version="1.0.0",
    multiplier=1.0,
    return_mode="generic_error",
)

translated_generic_error = assert_inference_error(
    lambda: predictor.predict(
        model=generic_error_model,
        context=prediction_context,
    ),
    message_contains="inference failed",
)

assert isinstance(
    translated_generic_error.cause,
    RuntimeError,
)


print(
    "forecast/inference/predictor.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from collections.abc import Mapping
from datetime import timedelta
from os import PathLike
from typing import Any, Self


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.inference.batch_predictor",
    "src.forecast.inference.predictor",
    "src.forecast.inference",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

batch_module = importlib.import_module(
    "src.forecast.inference.batch_predictor"
)

EnterpriseForecastBatchPredictor = (
    batch_module.EnterpriseForecastBatchPredictor
)

ForecastBatchPredictionItem = (
    batch_module.ForecastBatchPredictionItem
)

ForecastBatchPredictionRequest = (
    batch_module.ForecastBatchPredictionRequest
)

ForecastBatchPredictionResult = (
    batch_module.ForecastBatchPredictionResult
)


from src.forecast.inference.predictor import (
    EnterpriseForecastPredictor,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifact,
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
    ForecastInferenceError,
    ForecastPredictionError,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


# ----------------------------------------------------------
# Concrete validation model
# ----------------------------------------------------------

class BatchValidationForecastModel(BaseForecastModel):
    """Deterministic model used for batch inference validation."""

    def __init__(
        self,
        *,
        name: str,
        version: str = "1.0.0",
        multiplier: float = 1.0,
        fail_prediction: bool = False,
    ) -> None:
        self._name = name
        self._version = version
        self._multiplier = multiplier
        self._fail_prediction = fail_prediction
        self._state = ForecastModelState.TRAINED

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def model_version(self) -> str:
        return self._version

    @property
    def model_category(self) -> ForecastModelCategory:
        return ForecastModelCategory.CUSTOM

    @property
    def capabilities(
        self,
    ) -> frozenset[ForecastModelCapability]:
        return frozenset(
            {
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.MULTI_STEP_FORECAST,
            }
        )

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
        )

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        if self._fail_prediction:
            raise ForecastPredictionError(
                "Batch validation prediction failed."
            )

        predictions = tuple(
            float(index + 1) * self._multiplier
            for index in range(
                context.forecast_horizon
            )
        )

        prediction_timestamps = tuple(
            context.prediction_timestamp
            + timedelta(days=index + 1)
            for index in range(
                context.forecast_horizon
            )
        )

        return ForecastPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            predictions=predictions,
            forecast_horizon=context.forecast_horizon,
            prediction_timestamps=prediction_timestamps,
            inference_duration_seconds=0.01,
            metadata=dict(context.metadata),
        )

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        return ForecastEvaluationResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
        )

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        raise NotImplementedError

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        raise NotImplementedError

    def get_metadata(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
        }


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_batch_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastInferenceError:
    try:
        callable_object()

    except ForecastInferenceError as exc:
        assert message_contains in str(exc)
        return exc

    else:
        raise AssertionError(
            "Expected ForecastInferenceError."
        )


# ----------------------------------------------------------
# Construction and dependency validation
# ----------------------------------------------------------

default_batch_predictor = (
    EnterpriseForecastBatchPredictor()
)

assert isinstance(
    default_batch_predictor._predictor,
    EnterpriseForecastPredictor,
)

injected_predictor = EnterpriseForecastPredictor()

batch_predictor = EnterpriseForecastBatchPredictor(
    predictor=injected_predictor,
)

assert batch_predictor._predictor is injected_predictor

assert_batch_error(
    lambda: EnterpriseForecastBatchPredictor(
        predictor="invalid-predictor",
    ),
    message_contains="EnterpriseForecastPredictor",
)


# ----------------------------------------------------------
# Build models and contexts
# ----------------------------------------------------------

naive_model = BatchValidationForecastModel(
    name="naive_last_value",
    multiplier=10.0,
)

linear_model = BatchValidationForecastModel(
    name="linear_regression",
    multiplier=25.0,
)

failed_model = BatchValidationForecastModel(
    name="failed_model",
    multiplier=1.0,
    fail_prediction=True,
)

context_one = ForecastPredictionContext(
    prediction_dataset={
        "latest_value": 100.0,
    },
    forecast_horizon=2,
    model_version="1.0.0",
    metadata={
        "scope": "request_one",
    },
)

context_two = ForecastPredictionContext(
    prediction_dataset={
        "latest_value": 200.0,
    },
    forecast_horizon=3,
    model_version="1.0.0",
    metadata={
        "scope": "request_two",
    },
)


# ----------------------------------------------------------
# Request contract validation
# ----------------------------------------------------------

request_one = ForecastBatchPredictionRequest(
    request_id="request-001",
    model=naive_model,
    context=context_one,
    metadata={
        "business_unit": "distribution",
    },
)

request_two = ForecastBatchPredictionRequest(
    request_id="request-002",
    model=linear_model,
    context=context_two,
    metadata={
        "business_unit": "distribution",
    },
)

assert request_one.request_id == "request-001"
assert request_one.metadata == {
    "business_unit": "distribution",
}

assert_batch_error(
    lambda: ForecastBatchPredictionRequest(
        request_id=" ",
        model=naive_model,
        context=context_one,
    ),
    message_contains="must not be empty",
)

assert_batch_error(
    lambda: ForecastBatchPredictionRequest(
        request_id="request-invalid",
        model=naive_model,
        context=context_one,
        metadata="invalid-metadata",
    ),
    message_contains="must be a mapping",
)


# ----------------------------------------------------------
# Successful ordered batch prediction
# ----------------------------------------------------------

successful_batch = batch_predictor.predict(
    requests=[
        request_one,
        request_two,
    ],
    fail_fast=True,
    metadata={
        "validation_scope": "successful_batch",
    },
)

assert isinstance(
    successful_batch,
    ForecastBatchPredictionResult,
)

assert successful_batch.total_requests == 2
assert successful_batch.successful_requests == 2
assert successful_batch.failed_requests == 0
assert successful_batch.succeeded is True
assert successful_batch.fail_fast is True

assert successful_batch.metadata == {
    "validation_scope": "successful_batch",
}

assert tuple(
    item.request_id
    for item in successful_batch.items
) == (
    "request-001",
    "request-002",
)

assert tuple(
    item.model_name
    for item in successful_batch.items
) == (
    "naive_last_value",
    "linear_regression",
)

assert all(
    item.succeeded
    for item in successful_batch.items
)

assert len(successful_batch.predictions) == 2
assert successful_batch.failures == ()

assert tuple(
    successful_batch.predictions[0].predictions
) == (
    10.0,
    20.0,
)

assert tuple(
    successful_batch.predictions[1].predictions
) == (
    25.0,
    50.0,
    75.0,
)

assert successful_batch.get_item(
    "request-001"
).prediction is successful_batch.items[0].prediction


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

payload = successful_batch.to_dict()

assert payload["total_requests"] == 2
assert payload["successful_requests"] == 2
assert payload["failed_requests"] == 0
assert payload["succeeded"] is True
assert payload["fail_fast"] is True
assert len(payload["items"]) == 2

assert payload["items"][0]["request_id"] == (
    "request-001"
)

assert payload["items"][0]["prediction"][
    "predictions"
] == [
    10.0,
    20.0,
]

assert payload["items"][0]["error"] is None


# ----------------------------------------------------------
# Continue-on-error behavior
# ----------------------------------------------------------

failed_request = ForecastBatchPredictionRequest(
    request_id="request-failed",
    model=failed_model,
    context=context_one,
    metadata={
        "expected_failure": True,
    },
)

continued_batch = batch_predictor.predict(
    requests=[
        request_one,
        failed_request,
        request_two,
    ],
    fail_fast=False,
    metadata={
        "validation_scope": "continue_on_error",
    },
)

assert continued_batch.total_requests == 3
assert continued_batch.successful_requests == 2
assert continued_batch.failed_requests == 1
assert continued_batch.succeeded is False
assert continued_batch.fail_fast is False

assert tuple(
    item.request_id
    for item in continued_batch.items
) == (
    "request-001",
    "request-failed",
    "request-002",
)

failed_item = continued_batch.get_item(
    "request-failed"
)

assert isinstance(
    failed_item,
    ForecastBatchPredictionItem,
)

assert failed_item.succeeded is False
assert failed_item.prediction is None
assert failed_item.error is not None

assert failed_item.error["error_type"] == (
    "ForecastInferenceError"
)

assert len(continued_batch.predictions) == 2
assert len(continued_batch.failures) == 1

continued_payload = continued_batch.to_dict()

assert continued_payload["failed_requests"] == 1
assert continued_payload["items"][1][
    "succeeded"
] is False
assert continued_payload["items"][1][
    "prediction"
] is None
assert continued_payload["items"][1][
    "error"
] is not None


# ----------------------------------------------------------
# Fail-fast behavior
# ----------------------------------------------------------

fail_fast_error = assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[
            request_one,
            failed_request,
            request_two,
        ],
        fail_fast=True,
    ),
    message_contains="Batch forecast inference failed",
)

assert isinstance(
    fail_fast_error.cause,
    ForecastInferenceError,
)

assert fail_fast_error.context[
    "request_id"
] == "request-failed"

assert fail_fast_error.context[
    "request_index"
] == 1

assert fail_fast_error.context[
    "completed_requests"
] == 1

assert fail_fast_error.context[
    "total_requests"
] == 3


# ----------------------------------------------------------
# Empty and invalid request collection rejection
# ----------------------------------------------------------

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[],
    ),
    message_contains="At least one",
)

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=None,
    ),
    message_contains="cannot be None",
)

assert_batch_error(
    lambda: batch_predictor.predict(
        requests="invalid-requests",
    ),
    message_contains="must be a sequence",
)

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[
            request_one,
            "invalid-request",
        ],
    ),
    message_contains="ForecastBatchPredictionRequest",
)


# ----------------------------------------------------------
# Duplicate request rejection
# ----------------------------------------------------------

duplicate_request = ForecastBatchPredictionRequest(
    request_id="REQUEST-001",
    model=linear_model,
    context=context_two,
)

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[
            request_one,
            duplicate_request,
        ],
    ),
    message_contains="Duplicate",
)


# ----------------------------------------------------------
# Invalid runtime options
# ----------------------------------------------------------

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[
            request_one,
        ],
        fail_fast="yes",
    ),
    message_contains="must be a boolean",
)

assert_batch_error(
    lambda: batch_predictor.predict(
        requests=[
            request_one,
        ],
        metadata="invalid-metadata",
    ),
    message_contains="must be a mapping",
)


# ----------------------------------------------------------
# Missing result item lookup
# ----------------------------------------------------------

try:
    successful_batch.get_item(
        "missing-request"
    )

except KeyError as exc:
    assert "missing-request" in str(exc)

else:
    raise AssertionError(
        "Expected KeyError for missing batch request."
    )


print(
    "forecast/inference/batch_predictor.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from collections.abc import Mapping
from datetime import timedelta
from os import PathLike
from typing import Any, Self


# ----------------------------------------------------------
# Fresh package import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.inference.batch_predictor",
    "src.forecast.inference.predictor",
    "src.forecast.inference",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

inference_package = importlib.import_module(
    "src.forecast.inference"
)


# ----------------------------------------------------------
# Expected public exports
# ----------------------------------------------------------

expected_exports = {
    "EnterpriseForecastBatchPredictor",
    "EnterpriseForecastPredictor",
    "ForecastBatchPredictionItem",
    "ForecastBatchPredictionRequest",
    "ForecastBatchPredictionResult",
}

assert set(inference_package.__all__) == expected_exports

for export_name in expected_exports:
    assert hasattr(
        inference_package,
        export_name,
    ), (
        "src.forecast.inference is missing public export: "
        f"{export_name}"
    )


# ----------------------------------------------------------
# Public import compatibility
# ----------------------------------------------------------

from src.forecast.inference import (
    EnterpriseForecastBatchPredictor,
    EnterpriseForecastPredictor,
    ForecastBatchPredictionItem,
    ForecastBatchPredictionRequest,
    ForecastBatchPredictionResult,
)

from src.forecast.inference.batch_predictor import (
    EnterpriseForecastBatchPredictor as DirectBatchPredictor,
)
from src.forecast.inference.batch_predictor import (
    ForecastBatchPredictionItem as DirectBatchItem,
)
from src.forecast.inference.batch_predictor import (
    ForecastBatchPredictionRequest as DirectBatchRequest,
)
from src.forecast.inference.batch_predictor import (
    ForecastBatchPredictionResult as DirectBatchResult,
)
from src.forecast.inference.predictor import (
    EnterpriseForecastPredictor as DirectPredictor,
)

assert EnterpriseForecastPredictor is DirectPredictor

assert (
    EnterpriseForecastBatchPredictor
    is DirectBatchPredictor
)

assert ForecastBatchPredictionItem is DirectBatchItem

assert ForecastBatchPredictionRequest is DirectBatchRequest

assert ForecastBatchPredictionResult is DirectBatchResult


# ----------------------------------------------------------
# Modeling imports used by validation model
# ----------------------------------------------------------

from src.forecast.modeling.artifacts import (
    ForecastArtifact,
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
from src.forecast.modeling.results import (
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastPredictionResult,
    ForecastTrainingResult,
)


# ----------------------------------------------------------
# Concrete validation model
# ----------------------------------------------------------

class InferencePackageValidationModel(
    BaseForecastModel
):
    """
    Deterministic concrete model for package-level inference validation.
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        multiplier: float,
    ) -> None:
        self._name = name
        self._version = version
        self._multiplier = multiplier
        self._state = ForecastModelState.TRAINED

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def model_version(self) -> str:
        return self._version

    @property
    def model_category(
        self,
    ) -> ForecastModelCategory:
        return ForecastModelCategory.CUSTOM

    @property
    def capabilities(
        self,
    ) -> frozenset[ForecastModelCapability]:
        return frozenset(
            {
                ForecastModelCapability.POINT_FORECAST,
                ForecastModelCapability.MULTI_STEP_FORECAST,
            }
        )

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
        )

    def predict(
        self,
        context: ForecastPredictionContext,
    ) -> ForecastPredictionResult:
        predictions = tuple(
            float(index + 1) * self._multiplier
            for index in range(
                context.forecast_horizon
            )
        )

        prediction_timestamps = tuple(
            context.prediction_timestamp
            + timedelta(days=index + 1)
            for index in range(
                context.forecast_horizon
            )
        )

        return ForecastPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
            predictions=predictions,
            forecast_horizon=context.forecast_horizon,
            prediction_timestamps=prediction_timestamps,
            inference_duration_seconds=0.01,
            metadata=dict(context.metadata),
        )

    def evaluate(
        self,
        context: ForecastEvaluationContext,
    ) -> ForecastEvaluationResult:
        return ForecastEvaluationResult(
            model_name=self.model_name,
            model_version=self.model_version,
            status=ForecastExecutionStatus.SUCCESS,
        )

    def save(
        self,
        destination: str | PathLike[str],
    ) -> ForecastArtifact:
        raise NotImplementedError(
            "Persistence is outside package validation."
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        raise NotImplementedError(
            "Loading is outside package validation."
        )

    def get_metadata(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "multiplier": self._multiplier,
        }


# ----------------------------------------------------------
# Service construction
# ----------------------------------------------------------

predictor = EnterpriseForecastPredictor()

batch_predictor = EnterpriseForecastBatchPredictor(
    predictor=predictor,
)

assert vars(predictor) == {}

assert batch_predictor._predictor is predictor


# ----------------------------------------------------------
# Single-request package workflow
# ----------------------------------------------------------

single_model = InferencePackageValidationModel(
    name="package_validation_model",
    version="1.0.0",
    multiplier=10.0,
)

single_context = ForecastPredictionContext(
    prediction_dataset={
        "latest_value": 100.0,
    },
    forecast_horizon=3,
    model_version="1.0.0",
    metadata={
        "validation_scope": "single_request",
    },
)

single_result = predictor.predict(
    model=single_model,
    context=single_context,
)

assert isinstance(
    single_result,
    ForecastPredictionResult,
)

assert single_result.model_name == (
    "package_validation_model"
)

assert single_result.model_version == "1.0.0"

assert single_result.succeeded is True

assert tuple(single_result.predictions) == (
    10.0,
    20.0,
    30.0,
)

assert single_result.forecast_horizon == 3

assert len(
    single_result.prediction_timestamps
) == 3

assert single_result.metadata == {
    "validation_scope": "single_request",
}


# ----------------------------------------------------------
# Batch package workflow
# ----------------------------------------------------------

first_model = InferencePackageValidationModel(
    name="naive_last_value",
    version="1.0.0",
    multiplier=5.0,
)

second_model = InferencePackageValidationModel(
    name="linear_regression",
    version="1.0.0",
    multiplier=20.0,
)

first_request = ForecastBatchPredictionRequest(
    request_id="package-request-001",
    model=first_model,
    context=ForecastPredictionContext(
        prediction_dataset={
            "latest_value": 50.0,
        },
        forecast_horizon=2,
        model_version="1.0.0",
        metadata={
            "request_scope": "first",
        },
    ),
    metadata={
        "model_family": "baseline",
    },
)

second_request = ForecastBatchPredictionRequest(
    request_id="package-request-002",
    model=second_model,
    context=ForecastPredictionContext(
        prediction_dataset={
            "latest_value": 200.0,
        },
        forecast_horizon=3,
        model_version="1.0.0",
        metadata={
            "request_scope": "second",
        },
    ),
    metadata={
        "model_family": "regression",
    },
)

batch_result = batch_predictor.predict(
    requests=[
        first_request,
        second_request,
    ],
    fail_fast=True,
    metadata={
        "validation_scope": "inference_package",
    },
)

assert isinstance(
    batch_result,
    ForecastBatchPredictionResult,
)

assert batch_result.total_requests == 2
assert batch_result.successful_requests == 2
assert batch_result.failed_requests == 0
assert batch_result.succeeded is True

assert batch_result.metadata == {
    "validation_scope": "inference_package",
}

assert tuple(
    item.request_id
    for item in batch_result.items
) == (
    "package-request-001",
    "package-request-002",
)

assert all(
    isinstance(
        item,
        ForecastBatchPredictionItem,
    )
    for item in batch_result.items
)

assert tuple(
    batch_result.predictions[0].predictions
) == (
    5.0,
    10.0,
)

assert tuple(
    batch_result.predictions[1].predictions
) == (
    20.0,
    40.0,
    60.0,
)

assert batch_result.get_item(
    "package-request-001"
).model_name == "naive_last_value"

assert batch_result.get_item(
    "package-request-002"
).model_name == "linear_regression"


# ----------------------------------------------------------
# Serialization boundary
# ----------------------------------------------------------

single_payload = single_result.to_dict()

assert single_payload["model_name"] == (
    "package_validation_model"
)

assert single_payload["status"] == "SUCCESS"

assert single_payload["predictions"] == [
    10.0,
    20.0,
    30.0,
]

batch_payload = batch_result.to_dict()

assert batch_payload["total_requests"] == 2
assert batch_payload["successful_requests"] == 2
assert batch_payload["failed_requests"] == 0
assert batch_payload["succeeded"] is True
assert len(batch_payload["items"]) == 2

assert batch_payload["items"][0][
    "request_id"
] == "package-request-001"

assert batch_payload["items"][0][
    "prediction"
]["predictions"] == [
    5.0,
    10.0,
]

assert batch_payload["items"][1][
    "request_id"
] == "package-request-002"

assert batch_payload["items"][1][
    "prediction"
]["predictions"] == [
    20.0,
    40.0,
    60.0,
]


print(
    "forecast/inference/__init__.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.model_registry.registry",
    "src.forecast.model_registry",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

registry_module = importlib.import_module(
    "src.forecast.model_registry.registry"
)

EnterpriseModelRegistry = (
    registry_module.EnterpriseModelRegistry
)

ForecastModelRegistration = (
    registry_module.ForecastModelRegistration
)


from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCategory,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_registry_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastRegistryError:
    try:
        callable_object()

    except ForecastRegistryError as exc:
        assert message_contains in str(exc)
        return exc

    else:
        raise AssertionError(
            "Expected ForecastRegistryError."
        )


# ----------------------------------------------------------
# Registry construction
# ----------------------------------------------------------

registry = EnterpriseModelRegistry()

assert registry.total_models == 0
assert registry.is_empty is True
assert registry.list_models() == ()

initial_payload = registry.to_dict()

assert initial_payload == {
    "total_models": 0,
    "is_empty": True,
    "registrations": [],
}


# ----------------------------------------------------------
# Build persisted artifact references
# ----------------------------------------------------------

linear_artifact = ForecastArtifact(
    model_name="linear_regression",
    model_version="1.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="linear_regression",
    storage_uri=(
        "s3://validation-models/"
        "linear_regression/1.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
        "rolling_mean_7",
    ),
    target_column="order_line_count",
    forecast_horizon=14,
    hyperparameters={
        "fit_intercept": True,
    },
    metrics={
        "rmse": 105.5,
        "wape": 8.25,
    },
    artifact_id="artifact-linear-001",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
    checksum="linear-checksum",
    training_dataset_id="forecast-dataset",
    training_dataset_version="2.3.0",
    experiment_id="experiment-001",
    run_id="run-linear-001",
    metadata={
        "source": "training_framework",
    },
)

random_forest_artifact = ForecastArtifact(
    model_name="random_forest",
    model_version="2.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="random_forest",
    storage_uri=(
        "s3://validation-models/"
        "random_forest/2.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
        "rolling_mean_7",
    ),
    target_column="order_line_count",
    forecast_horizon=14,
    hyperparameters={
        "n_estimators": 200,
    },
    metrics={
        "rmse": 92.0,
        "wape": 7.1,
    },
    artifact_id="artifact-rf-001",
    artifact_version="3",
    status=ForecastArtifactStatus.PERSISTED,
    checksum="rf-checksum",
    training_dataset_id="forecast-dataset",
    training_dataset_version="2.3.0",
    experiment_id="experiment-001",
    run_id="run-rf-001",
    metadata={
        "source": "training_framework",
    },
)

linear_v2_artifact = ForecastArtifact(
    model_name="linear_regression",
    model_version="2.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="linear_regression",
    storage_uri=(
        "s3://validation-models/"
        "linear_regression/2.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
        "rolling_mean_7",
        "day_of_week",
    ),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="artifact-linear-002",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
)


# ----------------------------------------------------------
# Standard registration
# ----------------------------------------------------------

linear_registration = registry.register(
    artifact=linear_artifact,
    primary_metric="rmse",
    primary_metric_value=105.5,
    metadata={
        "registered_by": "databricks_validation",
        "business_domain": "workforce_capacity",
    },
)

assert isinstance(
    linear_registration,
    ForecastModelRegistration,
)

assert linear_registration.model_name == (
    "linear_regression"
)
assert linear_registration.model_version == "1.0.0"

assert linear_registration.model_category == (
    ForecastModelCategory.MACHINE_LEARNING
)

assert linear_registration.algorithm == (
    "linear_regression"
)

assert linear_registration.artifact_id == (
    "artifact-linear-001"
)

assert linear_registration.storage_uri == (
    "s3://validation-models/"
    "linear_regression/1.0.0/model"
)

assert linear_registration.primary_metric == "rmse"
assert linear_registration.primary_metric_value == 105.5
assert linear_registration.forecast_horizon == 14

assert linear_registration.feature_columns == (
    "lag_1",
    "lag_7",
    "rolling_mean_7",
)

assert linear_registration.model_identity == (
    "linear_regression:1.0.0"
)

assert linear_registration.artifact_identity == (
    "artifact-linear-001:1"
)

assert linear_registration.metadata == {
    "source": "training_framework",
    "registered_by": "databricks_validation",
    "business_domain": "workforce_capacity",
}

assert registry.total_models == 1
assert registry.is_empty is False


# ----------------------------------------------------------
# Additional registrations
# ----------------------------------------------------------

random_forest_registration = registry.register(
    artifact=random_forest_artifact,
    primary_metric="wape",
    primary_metric_value=7.1,
)

linear_v2_registration = registry.register(
    artifact=linear_v2_artifact,
)

assert registry.total_models == 3

assert isinstance(
    random_forest_registration,
    ForecastModelRegistration,
)

assert isinstance(
    linear_v2_registration,
    ForecastModelRegistration,
)


# ----------------------------------------------------------
# Contains and retrieval
# ----------------------------------------------------------

assert registry.contains(
    model_name="linear_regression",
    model_version="1.0.0",
) is True

assert registry.contains(
    model_name=" LINEAR_REGRESSION ",
    model_version=" 1.0.0 ",
) is True

assert registry.contains(
    model_name="missing_model",
    model_version="1.0.0",
) is False

assert registry.contains_artifact(
    "artifact-rf-001"
) is True

assert registry.contains_artifact(
    "missing-artifact"
) is False

assert registry.get(
    model_name="linear_regression",
    model_version="1.0.0",
) is linear_registration

assert registry.get_by_artifact_id(
    "artifact-rf-001"
) is random_forest_registration


# ----------------------------------------------------------
# Deterministic inventory ordering
# ----------------------------------------------------------

all_registrations = registry.list_models()

assert tuple(
    (
        registration.model_name,
        registration.model_version,
    )
    for registration in all_registrations
) == (
    (
        "linear_regression",
        "1.0.0",
    ),
    (
        "linear_regression",
        "2.0.0",
    ),
    (
        "random_forest",
        "2.0.0",
    ),
)

linear_versions = registry.list_versions(
    "linear_regression"
)

assert tuple(
    registration.model_version
    for registration in linear_versions
) == (
    "1.0.0",
    "2.0.0",
)

assert registry.list_versions(
    "unknown_model"
) == ()


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

registration_payload = (
    linear_registration.to_dict()
)

assert registration_payload["model_name"] == (
    "linear_regression"
)

assert registration_payload["model_version"] == (
    "1.0.0"
)

assert registration_payload["model_category"] == (
    "MACHINE_LEARNING"
)

assert registration_payload["artifact_status"] == (
    "PERSISTED"
)

assert registration_payload["feature_columns"] == [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
]

assert registration_payload["primary_metric"] == "rmse"
assert registration_payload[
    "primary_metric_value"
] == 105.5

registry_payload = registry.to_dict()

assert registry_payload["total_models"] == 3
assert registry_payload["is_empty"] is False
assert len(registry_payload["registrations"]) == 3

assert registry_payload["registrations"][0][
    "model_name"
] == "linear_regression"


# ----------------------------------------------------------
# Registration immutability
# ----------------------------------------------------------

try:
    linear_registration.model_name = "modified"

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastModelRegistration must be immutable."
    )


# ----------------------------------------------------------
# Duplicate model identity rejection
# ----------------------------------------------------------

duplicate_model_artifact = ForecastArtifact(
    model_name="LINEAR_REGRESSION",
    model_version="1.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="linear_regression",
    storage_uri=(
        "s3://validation-models/"
        "duplicate/model"
    ),
    feature_columns=("lag_1",),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="artifact-duplicate-model",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
)

assert_registry_error(
    lambda: registry.register(
        artifact=duplicate_model_artifact,
    ),
    message_contains="already registered",
)


# ----------------------------------------------------------
# Duplicate artifact rejection
# ----------------------------------------------------------

duplicate_artifact_id = ForecastArtifact(
    model_name="new_model",
    model_version="1.0.0",
    model_category=ForecastModelCategory.CUSTOM,
    algorithm="new_model",
    storage_uri=(
        "s3://validation-models/new-model/model"
    ),
    feature_columns=("lag_1",),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="artifact-rf-001",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
)

assert_registry_error(
    lambda: registry.register(
        artifact=duplicate_artifact_id,
    ),
    message_contains="artifact is already registered",
)


# ----------------------------------------------------------
# Invalid artifact rejection
# ----------------------------------------------------------

assert_registry_error(
    lambda: registry.register(
        artifact=None,
    ),
    message_contains="cannot be None",
)

assert_registry_error(
    lambda: registry.register(
        artifact="invalid-artifact",
    ),
    message_contains="ForecastArtifact",
)

failed_artifact = ForecastArtifact(
    model_name="failed_model",
    model_version="1.0.0",
    model_category=ForecastModelCategory.CUSTOM,
    algorithm="failed_model",
    storage_uri=(
        "s3://validation-models/failed/model"
    ),
    feature_columns=("lag_1",),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="artifact-failed",
    artifact_version="1",
    status=ForecastArtifactStatus.FAILED,
)

assert_registry_error(
    lambda: registry.register(
        artifact=failed_artifact,
    ),
    message_contains="Failed forecast artifacts",
)


# ----------------------------------------------------------
# Primary metric consistency
# ----------------------------------------------------------

metric_test_artifact = ForecastArtifact(
    model_name="metric_test_model",
    model_version="1.0.0",
    model_category=ForecastModelCategory.CUSTOM,
    algorithm="metric_test",
    storage_uri=(
        "s3://validation-models/metric-test/model"
    ),
    feature_columns=("lag_1",),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="artifact-metric-test",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
)

assert_registry_error(
    lambda: registry.register(
        artifact=metric_test_artifact,
        primary_metric_value=5.0,
    ),
    message_contains="primary_metric is required",
)

assert_registry_error(
    lambda: registry.register(
        artifact=metric_test_artifact,
        primary_metric="rmse",
    ),
    message_contains="primary_metric_value is required",
)

assert_registry_error(
    lambda: registry.register(
        artifact=metric_test_artifact,
        primary_metric="rmse",
        primary_metric_value=float("nan"),
    ),
    message_contains="must be finite",
)


# ----------------------------------------------------------
# Unknown retrieval rejection
# ----------------------------------------------------------

assert_registry_error(
    lambda: registry.get(
        model_name="unknown_model",
        model_version="1.0.0",
    ),
    message_contains="is not registered",
)

assert_registry_error(
    lambda: registry.get_by_artifact_id(
        "unknown-artifact"
    ),
    message_contains="is not registered",
)


# ----------------------------------------------------------
# Removal
# ----------------------------------------------------------

removed_registration = registry.remove(
    model_name="linear_regression",
    model_version="2.0.0",
)

assert removed_registration is linear_v2_registration

assert registry.contains(
    model_name="linear_regression",
    model_version="2.0.0",
) is False

assert registry.contains_artifact(
    "artifact-linear-002"
) is False

assert registry.total_models == 2

assert_registry_error(
    lambda: registry.remove(
        model_name="linear_regression",
        model_version="2.0.0",
    ),
    message_contains="Cannot remove",
)


# ----------------------------------------------------------
# Clear registry
# ----------------------------------------------------------

registry.clear()

assert registry.total_models == 0
assert registry.is_empty is True
assert registry.list_models() == ()

assert registry.to_dict() == {
    "total_models": 0,
    "is_empty": True,
    "registrations": [],
}


print(
    "forecast/model_registry/registry.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.model_registry.catalog",
    "src.forecast.model_registry.registry",
    "src.forecast.model_registry",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

catalog_module = importlib.import_module(
    "src.forecast.model_registry.catalog"
)

EnterpriseModelCatalog = (
    catalog_module.EnterpriseModelCatalog
)

ForecastModelCatalogQuery = (
    catalog_module.ForecastModelCatalogQuery
)

ForecastModelCatalogResult = (
    catalog_module.ForecastModelCatalogResult
)


from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry,
    ForecastModelRegistration,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import (
    ForecastModelCategory,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_catalog_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastRegistryError:
    try:
        callable_object()

    except ForecastRegistryError as exc:
        assert message_contains in str(exc)
        return exc

    else:
        raise AssertionError(
            "Expected ForecastRegistryError."
        )


# ----------------------------------------------------------
# Registry and catalog construction
# ----------------------------------------------------------

registry = EnterpriseModelRegistry()

catalog = EnterpriseModelCatalog(
    registry=registry,
)

assert catalog.registry is registry

assert_catalog_error(
    lambda: EnterpriseModelCatalog(
        registry="invalid-registry",
    ),
    message_contains="EnterpriseModelRegistry",
)


# ----------------------------------------------------------
# Build registry artifacts
# ----------------------------------------------------------

base_timestamp = datetime(
    2026,
    8,
    2,
    4,
    0,
    tzinfo=timezone.utc,
)

linear_v1_artifact = ForecastArtifact(
    model_name="linear_regression",
    model_version="1.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="linear_regression",
    storage_uri=(
        "s3://validation-models/"
        "linear-regression/1.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
    ),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="catalog-linear-001",
    artifact_version="1",
    status=ForecastArtifactStatus.PERSISTED,
    metadata={
        "business_domain": "workforce_capacity",
        "environment": "development",
        "owner": "forecast_team",
    },
)

linear_v2_artifact = ForecastArtifact(
    model_name="linear_regression",
    model_version="2.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="linear_regression",
    storage_uri=(
        "s3://validation-models/"
        "linear-regression/2.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
        "rolling_mean_7",
    ),
    target_column="order_line_count",
    forecast_horizon=14,
    artifact_id="catalog-linear-002",
    artifact_version="1",
    status=ForecastArtifactStatus.REGISTERED,
    metadata={
        "business_domain": "workforce_capacity",
        "environment": "staging",
        "owner": "forecast_team",
    },
)

random_forest_artifact = ForecastArtifact(
    model_name="random_forest",
    model_version="1.0.0",
    model_category=(
        ForecastModelCategory.MACHINE_LEARNING
    ),
    algorithm="random_forest",
    storage_uri=(
        "s3://validation-models/"
        "random-forest/1.0.0/model"
    ),
    feature_columns=(
        "lag_1",
        "lag_7",
        "rolling_mean_7",
    ),
    target_column="order_line_count",
    forecast_horizon=7,
    artifact_id="catalog-rf-001",
    artifact_version="2",
    status=ForecastArtifactStatus.PERSISTED,
    metadata={
        "business_domain": "workforce_capacity",
        "environment": "development",
        "owner": "ml_platform",
    },
)

naive_artifact = ForecastArtifact(
    model_name="naive_last_value",
    model_version="1.0.0",
    model_category=ForecastModelCategory.BASELINE,
    algorithm="naive_last_value",
    storage_uri=(
        "s3://validation-models/"
        "naive-last-value/1.0.0/model"
    ),
    feature_columns=(),
    target_column="workload_units",
    forecast_horizon=7,
    artifact_id="catalog-naive-001",
    artifact_version="1",
    status=ForecastArtifactStatus.CHAMPION,
    metadata={
        "business_domain": "workforce_capacity",
        "environment": "production",
        "owner": "forecast_team",
    },
)


# ----------------------------------------------------------
# Register artifacts
# ----------------------------------------------------------

linear_v1 = registry.register(
    artifact=linear_v1_artifact,
    primary_metric="rmse",
    primary_metric_value=105.0,
)

linear_v2 = registry.register(
    artifact=linear_v2_artifact,
    primary_metric="rmse",
    primary_metric_value=92.0,
)

random_forest = registry.register(
    artifact=random_forest_artifact,
    primary_metric="wape",
    primary_metric_value=7.2,
)

naive = registry.register(
    artifact=naive_artifact,
    primary_metric="mae",
    primary_metric_value=130.0,
)

assert registry.total_models == 4


# ----------------------------------------------------------
# Empty query returns complete inventory
# ----------------------------------------------------------

complete_result = catalog.search()

assert isinstance(
    complete_result,
    ForecastModelCatalogResult,
)

assert complete_result.total_registry_models == 4
assert complete_result.total_matches == 4
assert complete_result.is_empty is False

assert tuple(
    registration.model_name
    for registration in complete_result.registrations
) == (
    "linear_regression",
    "linear_regression",
    "naive_last_value",
    "random_forest",
)

assert complete_result.first is linear_v1


# ----------------------------------------------------------
# Exact model identity filters
# ----------------------------------------------------------

linear_query = ForecastModelCatalogQuery(
    model_name=" LINEAR_REGRESSION ",
)

linear_result = catalog.search(
    linear_query
)

assert linear_result.total_matches == 2

assert tuple(
    registration.model_version
    for registration in linear_result.registrations
) == (
    "1.0.0",
    "2.0.0",
)

linear_v2_result = catalog.search(
    ForecastModelCatalogQuery(
        model_name="linear_regression",
        model_version="2.0.0",
    )
)

assert linear_v2_result.total_matches == 1
assert linear_v2_result.first is linear_v2


# ----------------------------------------------------------
# Category and algorithm filters
# ----------------------------------------------------------

machine_learning_result = catalog.search(
    ForecastModelCatalogQuery(
        model_category=(
            ForecastModelCategory.MACHINE_LEARNING
        ),
    )
)

assert machine_learning_result.total_matches == 3

baseline_result = catalog.search(
    ForecastModelCatalogQuery(
        model_category=ForecastModelCategory.BASELINE,
    )
)

assert baseline_result.total_matches == 1
assert baseline_result.first is naive

random_forest_result = catalog.search(
    ForecastModelCatalogQuery(
        algorithm="RANDOM_FOREST",
    )
)

assert random_forest_result.total_matches == 1
assert random_forest_result.first is random_forest


# ----------------------------------------------------------
# Artifact-status filter
# ----------------------------------------------------------

persisted_result = catalog.search(
    ForecastModelCatalogQuery(
        artifact_status=ForecastArtifactStatus.PERSISTED,
    )
)

assert persisted_result.total_matches == 2

assert tuple(
    registration.model_name
    for registration in persisted_result.registrations
) == (
    "linear_regression",
    "random_forest",
)

champion_result = catalog.search(
    ForecastModelCatalogQuery(
        artifact_status=ForecastArtifactStatus.CHAMPION,
    )
)

assert champion_result.total_matches == 1
assert champion_result.first is naive


# ----------------------------------------------------------
# Target and horizon filters
# ----------------------------------------------------------

order_line_result = catalog.search(
    ForecastModelCatalogQuery(
        target_column="ORDER_LINE_COUNT",
    )
)

assert order_line_result.total_matches == 3

seven_day_result = catalog.search(
    ForecastModelCatalogQuery(
        forecast_horizon=7,
    )
)

assert seven_day_result.total_matches == 2

assert {
    registration.model_name
    for registration in seven_day_result.registrations
} == {
    "naive_last_value",
    "random_forest",
}


# ----------------------------------------------------------
# Primary metric filter
# ----------------------------------------------------------

rmse_result = catalog.search(
    ForecastModelCatalogQuery(
        primary_metric="RMSE",
    )
)

assert rmse_result.total_matches == 2

assert all(
    registration.primary_metric == "rmse"
    for registration in rmse_result.registrations
)


# ----------------------------------------------------------
# Metadata subset filters
# ----------------------------------------------------------

development_result = catalog.search(
    ForecastModelCatalogQuery(
        metadata={
            "environment": "development",
        },
    )
)

assert development_result.total_matches == 2

forecast_team_result = catalog.search(
    ForecastModelCatalogQuery(
        metadata={
            "business_domain": "workforce_capacity",
            "owner": "forecast_team",
        },
    )
)

assert forecast_team_result.total_matches == 3

missing_metadata_result = catalog.search(
    ForecastModelCatalogQuery(
        metadata={
            "environment": "missing",
        },
    )
)

assert missing_metadata_result.total_matches == 0
assert missing_metadata_result.is_empty is True
assert missing_metadata_result.first is None


# ----------------------------------------------------------
# Combined filters use logical AND
# ----------------------------------------------------------

combined_result = catalog.search(
    ForecastModelCatalogQuery(
        model_name="linear_regression",
        artifact_status=ForecastArtifactStatus.REGISTERED,
        target_column="order_line_count",
        forecast_horizon=14,
        metadata={
            "environment": "staging",
        },
    )
)

assert combined_result.total_matches == 1
assert combined_result.first is linear_v2


# ----------------------------------------------------------
# Deterministic sorting
# ----------------------------------------------------------

metric_sorted = catalog.search(
    ForecastModelCatalogQuery(
        order_by="primary_metric_value",
    )
)

assert tuple(
    registration.model_name
    for registration in metric_sorted.registrations
) == (
    "random_forest",
    "linear_regression",
    "linear_regression",
    "naive_last_value",
)

assert tuple(
    registration.primary_metric_value
    for registration in metric_sorted.registrations
) == (
    7.2,
    92.0,
    105.0,
    130.0,
)

metric_descending = catalog.search(
    ForecastModelCatalogQuery(
        order_by="primary_metric_value",
        descending=True,
    )
)

assert tuple(
    registration.primary_metric_value
    for registration in metric_descending.registrations
) == (
    130.0,
    105.0,
    92.0,
    7.2,
)

algorithm_sorted = catalog.search(
    ForecastModelCatalogQuery(
        order_by="algorithm",
    )
)

assert tuple(
    registration.algorithm
    for registration in algorithm_sorted.registrations
) == (
    "linear_regression",
    "linear_regression",
    "naive_last_value",
    "random_forest",
)


# ----------------------------------------------------------
# Result limiting
# ----------------------------------------------------------

limited_result = catalog.search(
    ForecastModelCatalogQuery(
        order_by="primary_metric_value",
        limit=2,
    )
)

assert limited_result.total_registry_models == 4
assert limited_result.total_matches == 2

assert tuple(
    registration.model_name
    for registration in limited_result.registrations
) == (
    "random_forest",
    "linear_regression",
)


# ----------------------------------------------------------
# find_one behavior
# ----------------------------------------------------------

resolved_registration = catalog.find_one(
    ForecastModelCatalogQuery(
        model_name="random_forest",
        model_version="1.0.0",
    )
)

assert resolved_registration is random_forest

assert_catalog_error(
    lambda: catalog.find_one(
        ForecastModelCatalogQuery(
            model_name="missing_model",
        )
    ),
    message_contains="no registrations",
)

assert_catalog_error(
    lambda: catalog.find_one(
        ForecastModelCatalogQuery(
            model_name="linear_regression",
        )
    ),
    message_contains="multiple registrations",
)


# ----------------------------------------------------------
# Catalog dimensions
# ----------------------------------------------------------

assert catalog.list_categories() == (
    ForecastModelCategory.BASELINE,
    ForecastModelCategory.MACHINE_LEARNING,
)

assert catalog.list_algorithms() == (
    "linear_regression",
    "naive_last_value",
    "random_forest",
)

assert catalog.list_target_columns() == (
    "order_line_count",
    "workload_units",
)


# ----------------------------------------------------------
# Query serialization and immutability
# ----------------------------------------------------------

query_payload = combined_result.query.to_dict()

assert query_payload["model_name"] == (
    "linear_regression"
)

assert query_payload["artifact_status"] == (
    "REGISTERED"
)

assert query_payload["model_category"] is None

assert query_payload["metadata"] == {
    "environment": "staging",
}

try:
    combined_result.query.order_by = "algorithm"

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastModelCatalogQuery must be immutable."
    )


# ----------------------------------------------------------
# Result serialization
# ----------------------------------------------------------

result_payload = combined_result.to_dict()

assert result_payload["total_registry_models"] == 4
assert result_payload["total_matches"] == 1
assert result_payload["is_empty"] is False
assert len(result_payload["registrations"]) == 1

assert result_payload["registrations"][0][
    "model_name"
] == "linear_regression"

assert result_payload["registrations"][0][
    "model_version"
] == "2.0.0"


# ----------------------------------------------------------
# Invalid query rejection
# ----------------------------------------------------------

assert_catalog_error(
    lambda: catalog.search(
        query="invalid-query",
    ),
    message_contains="ForecastModelCatalogQuery",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        model_category="MACHINE_LEARNING",
    ),
    message_contains="model_category",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        artifact_status="PERSISTED",
    ),
    message_contains="artifact_status",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        forecast_horizon=0,
    ),
    message_contains="greater than zero",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        metadata="invalid-metadata",
    ),
    message_contains="must be a mapping",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        order_by="unsupported",
    ),
    message_contains="Unsupported catalog ordering",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        descending="yes",
    ),
    message_contains="must be a boolean",
)

assert_catalog_error(
    lambda: ForecastModelCatalogQuery(
        limit=0,
    ),
    message_contains="greater than zero",
)


# ----------------------------------------------------------
# Catalog remains read-only
# ----------------------------------------------------------

before_catalog_search = registry.to_dict()

catalog.search(
    ForecastModelCatalogQuery(
        model_category=(
            ForecastModelCategory.MACHINE_LEARNING
        ),
    )
)

after_catalog_search = registry.to_dict()

assert after_catalog_search == before_catalog_search


print(
    "forecast/model_registry/catalog.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from dataclasses import FrozenInstanceError
from typing import Any


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.model_registry.versioning",
    "src.forecast.model_registry.registry",
    "src.forecast.model_registry",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

versioning_module = importlib.import_module(
    "src.forecast.model_registry.versioning"
)

EnterpriseModelVersioning = (
    versioning_module.EnterpriseModelVersioning
)

ForecastModelVersion = (
    versioning_module.ForecastModelVersion
)

ForecastModelVersionEntry = (
    versioning_module.ForecastModelVersionEntry
)


from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry,
    ForecastModelRegistration,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import (
    ForecastModelCategory,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_versioning_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastRegistryError:
    try:
        callable_object()

    except ForecastRegistryError as exc:
        assert message_contains in str(exc)
        return exc

    else:
        raise AssertionError(
            "Expected ForecastRegistryError."
        )


# ----------------------------------------------------------
# Semantic-version parsing
# ----------------------------------------------------------

version_1_0_0 = ForecastModelVersion.parse(
    "1.0.0"
)

assert version_1_0_0.major == 1
assert version_1_0_0.minor == 0
assert version_1_0_0.patch == 0
assert version_1_0_0.to_string() == "1.0.0"
assert str(version_1_0_0) == "1.0.0"

assert ForecastModelVersion.parse(
    " 2.14.103 "
) == ForecastModelVersion(
    major=2,
    minor=14,
    patch=103,
)

assert ForecastModelVersion.parse(
    "10.0.0"
) > ForecastModelVersion.parse(
    "2.99.99"
)

assert ForecastModelVersion.parse(
    "1.10.0"
) > ForecastModelVersion.parse(
    "1.2.99"
)

assert ForecastModelVersion.parse(
    "1.0.10"
) > ForecastModelVersion.parse(
    "1.0.2"
)


# ----------------------------------------------------------
# Version bumping
# ----------------------------------------------------------

base_version = ForecastModelVersion.parse(
    "2.4.7"
)

assert base_version.bump_patch().to_string() == (
    "2.4.8"
)

assert base_version.bump_minor().to_string() == (
    "2.5.0"
)

assert base_version.bump_major().to_string() == (
    "3.0.0"
)


# ----------------------------------------------------------
# Version serialization
# ----------------------------------------------------------

assert base_version.to_dict() == {
    "version": "2.4.7",
    "major": 2,
    "minor": 4,
    "patch": 7,
}


# ----------------------------------------------------------
# Version immutability
# ----------------------------------------------------------

try:
    base_version.major = 99

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastModelVersion must be immutable."
    )


# ----------------------------------------------------------
# Invalid versions
# ----------------------------------------------------------

for empty_version in (
    "",
    " ",
):
    assert_versioning_error(
        lambda value=empty_version: (
            ForecastModelVersion.parse(value)
        ),
        message_contains="must not be empty",
    )


for malformed_version in (
    "1",
    "1.0",
    "1.0.0.0",
    "v1.0.0",
    "1.0.0-alpha",
    "1.0.0+build",
    "01.0.0",
    "1.01.0",
    "1.0.01",
    "-1.0.0",
    "a.b.c",
):
    assert_versioning_error(
        lambda value=malformed_version: (
            ForecastModelVersion.parse(value)
        ),
        message_contains="major.minor.patch",
    )


assert_versioning_error(
    lambda: ForecastModelVersion.parse(
        None
    ),
    message_contains="must be a string",
)

assert_versioning_error(
    lambda: ForecastModelVersion(
        major=True,
        minor=0,
        patch=0,
    ),
    message_contains="major must be an integer",
)

assert_versioning_error(
    lambda: ForecastModelVersion(
        major=-1,
        minor=0,
        patch=0,
    ),
    message_contains="cannot be negative",
)


# ----------------------------------------------------------
# Registry and versioning construction
# ----------------------------------------------------------

registry = EnterpriseModelRegistry()

versioning = EnterpriseModelVersioning(
    registry=registry,
)

assert versioning.registry is registry

assert_versioning_error(
    lambda: EnterpriseModelVersioning(
        registry="invalid-registry",
    ),
    message_contains="EnterpriseModelRegistry",
)


# ----------------------------------------------------------
# Artifact factory
# ----------------------------------------------------------

def create_artifact(
    *,
    model_name: str,
    model_version: str,
    artifact_id: str,
) -> ForecastArtifact:
    return ForecastArtifact(
        model_name=model_name,
        model_version=model_version,
        model_category=(
            ForecastModelCategory.MACHINE_LEARNING
        ),
        algorithm=model_name,
        storage_uri=(
            "s3://validation-models/"
            f"{model_name}/{model_version}/model"
        ),
        feature_columns=(
            "lag_1",
            "lag_7",
        ),
        target_column="order_line_count",
        forecast_horizon=14,
        artifact_id=artifact_id,
        artifact_version="1",
        status=ForecastArtifactStatus.PERSISTED,
    )


# ----------------------------------------------------------
# Register deliberately unordered versions
# ----------------------------------------------------------

registration_2_0_0 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="2.0.0",
        artifact_id="version-rf-200",
    )
)

registration_1_10_0 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="1.10.0",
        artifact_id="version-rf-1100",
    )
)

registration_1_2_10 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="1.2.10",
        artifact_id="version-rf-1210",
    )
)

registration_10_0_0 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="10.0.0",
        artifact_id="version-rf-1000",
    )
)

registration_1_2_2 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="1.2.2",
        artifact_id="version-rf-122",
    )
)

registration_1_0_0 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="1.0.0",
        artifact_id="version-rf-100",
    )
)

assert registry.total_models == 6


# ----------------------------------------------------------
# Semantic ordering
# ----------------------------------------------------------

ordered_versions = versioning.list_versions(
    "random_forest"
)

assert ordered_versions == (
    "1.0.0",
    "1.2.2",
    "1.2.10",
    "1.10.0",
    "2.0.0",
    "10.0.0",
)

entries = versioning.list_version_entries(
    "random_forest"
)

assert len(entries) == 6

assert all(
    isinstance(
        entry,
        ForecastModelVersionEntry,
    )
    for entry in entries
)

assert tuple(
    entry.version.to_string()
    for entry in entries
) == ordered_versions

assert entries[0].registration is (
    registration_1_0_0
)

assert entries[-1].registration is (
    registration_10_0_0
)


# ----------------------------------------------------------
# Version existence and retrieval
# ----------------------------------------------------------

assert versioning.version_exists(
    model_name="random_forest",
    model_version="1.2.10",
) is True

assert versioning.version_exists(
    model_name=" RANDOM_FOREST ",
    model_version=" 1.2.10 ",
) is True

assert versioning.version_exists(
    model_name="random_forest",
    model_version="3.0.0",
) is False

assert versioning.get_registration(
    model_name="random_forest",
    model_version="2.0.0",
) is registration_2_0_0


# ----------------------------------------------------------
# Latest and earliest resolution
# ----------------------------------------------------------

assert versioning.latest_version(
    "random_forest"
) == "10.0.0"

assert versioning.latest_registration(
    "random_forest"
) is registration_10_0_0

assert versioning.latest_entry(
    "random_forest"
).registration is registration_10_0_0

assert versioning.earliest_version(
    "random_forest"
) == "1.0.0"

assert versioning.earliest_registration(
    "random_forest"
) is registration_1_0_0

assert versioning.earliest_entry(
    "random_forest"
).registration is registration_1_0_0


# ----------------------------------------------------------
# Previous-version resolution
# ----------------------------------------------------------

assert versioning.previous_version(
    model_name="random_forest",
    model_version="1.0.0",
) is None

assert versioning.previous_registration(
    model_name="random_forest",
    model_version="1.0.0",
) is None

assert versioning.previous_version(
    model_name="random_forest",
    model_version="1.2.10",
) == "1.2.2"

assert versioning.previous_registration(
    model_name="random_forest",
    model_version="1.2.10",
) is registration_1_2_2

assert versioning.previous_version(
    model_name="random_forest",
    model_version="10.0.0",
) == "2.0.0"


# ----------------------------------------------------------
# Next-version resolution
# ----------------------------------------------------------

assert versioning.next_version(
    model_name="random_forest",
    model_version="1.0.0",
) == "1.2.2"

assert versioning.next_registration(
    model_name="random_forest",
    model_version="1.0.0",
) is registration_1_2_2

assert versioning.next_version(
    model_name="random_forest",
    model_version="1.10.0",
) == "2.0.0"

assert versioning.next_version(
    model_name="random_forest",
    model_version="10.0.0",
) is None

assert versioning.next_registration(
    model_name="random_forest",
    model_version="10.0.0",
) is None


# ----------------------------------------------------------
# Candidate version calculation
# ----------------------------------------------------------

assert versioning.next_patch_version(
    "random_forest"
) == "10.0.1"

assert versioning.next_minor_version(
    "random_forest"
) == "10.1.0"

assert versioning.next_major_version(
    "random_forest"
) == "11.0.0"

assert versioning.next_patch_version(
    "new_model"
) == "0.0.1"

assert versioning.next_minor_version(
    "new_model"
) == "0.1.0"

assert versioning.next_major_version(
    "new_model"
) == "1.0.0"


# ----------------------------------------------------------
# Version inventory serialization
# ----------------------------------------------------------

inventory = versioning.to_dict(
    "random_forest"
)

assert inventory["model_name"] == (
    "random_forest"
)

assert inventory["total_versions"] == 6
assert inventory["is_empty"] is False
assert inventory["earliest_version"] == "1.0.0"
assert inventory["latest_version"] == "10.0.0"
assert len(inventory["versions"]) == 6

assert inventory["versions"][0][
    "version"
]["version"] == "1.0.0"

assert inventory["versions"][-1][
    "registration"
]["model_version"] == "10.0.0"

empty_inventory = versioning.to_dict(
    "unknown_model"
)

assert empty_inventory == {
    "model_name": "unknown_model",
    "total_versions": 0,
    "is_empty": True,
    "earliest_version": None,
    "latest_version": None,
    "versions": [],
}


# ----------------------------------------------------------
# Unknown model and version behavior
# ----------------------------------------------------------

assert versioning.list_versions(
    "unknown_model"
) == ()

assert_versioning_error(
    lambda: versioning.latest_version(
        "unknown_model"
    ),
    message_contains="No registered versions",
)

assert_versioning_error(
    lambda: versioning.earliest_version(
        "unknown_model"
    ),
    message_contains="No registered versions",
)

assert_versioning_error(
    lambda: versioning.previous_version(
        model_name="random_forest",
        model_version="9.0.0",
    ),
    message_contains="not registered",
)

assert_versioning_error(
    lambda: versioning.next_version(
        model_name="random_forest",
        model_version="9.0.0",
    ),
    message_contains="not registered",
)


# ----------------------------------------------------------
# Invalid model and version inputs
# ----------------------------------------------------------

assert_versioning_error(
    lambda: versioning.list_versions(
        None
    ),
    message_contains="model_name must be a string",
)

assert_versioning_error(
    lambda: versioning.list_versions(
        " "
    ),
    message_contains="must not be empty",
)

assert_versioning_error(
    lambda: versioning.version_exists(
        model_name="random_forest",
        model_version="v1.0.0",
    ),
    message_contains="major.minor.patch",
)


# ----------------------------------------------------------
# Non-semantic registered version detection
# ----------------------------------------------------------

legacy_registry = EnterpriseModelRegistry()

legacy_registry.register(
    artifact=create_artifact(
        model_name="legacy_model",
        model_version="release-one",
        artifact_id="legacy-artifact",
    )
)

legacy_versioning = EnterpriseModelVersioning(
    registry=legacy_registry,
)

assert_versioning_error(
    lambda: legacy_versioning.list_versions(
        "legacy_model"
    ),
    message_contains="major.minor.patch",
)


# ----------------------------------------------------------
# Version-entry consistency
# ----------------------------------------------------------

assert_versioning_error(
    lambda: ForecastModelVersionEntry(
        version=ForecastModelVersion.parse(
            "9.9.9"
        ),
        registration=registration_1_0_0,
    ),
    message_contains="does not match",
)


# ----------------------------------------------------------
# Versioning remains read-only
# ----------------------------------------------------------

before_versioning_operations = registry.to_dict()

versioning.list_versions(
    "random_forest"
)
versioning.latest_version(
    "random_forest"
)
versioning.previous_version(
    model_name="random_forest",
    model_version="2.0.0",
)
versioning.next_major_version(
    "random_forest"
)

after_versioning_operations = registry.to_dict()

assert (
    after_versioning_operations
    == before_versioning_operations
)


print(
    "forecast/model_registry/versioning.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from dataclasses import FrozenInstanceError
from typing import Any


# ----------------------------------------------------------
# Fresh module import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.model_registry.promotion",
    "src.forecast.model_registry.versioning",
    "src.forecast.model_registry.registry",
    "src.forecast.model_registry",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

promotion_module = importlib.import_module(
    "src.forecast.model_registry.promotion"
)

EnterpriseModelPromotionService = (
    promotion_module.EnterpriseModelPromotionService
)

ForecastLifecycleState = (
    promotion_module.ForecastLifecycleState
)

ForecastPromotionAction = (
    promotion_module.ForecastPromotionAction
)

ForecastPromotionRecord = (
    promotion_module.ForecastPromotionRecord
)

ForecastPromotionResult = (
    promotion_module.ForecastPromotionResult
)


from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry,
)
from src.forecast.model_registry.versioning import (
    EnterpriseModelVersioning,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifact,
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import (
    ForecastModelCategory,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


# ----------------------------------------------------------
# Error assertion helper
# ----------------------------------------------------------

def assert_promotion_error(
    callable_object: Any,
    *,
    message_contains: str,
) -> ForecastRegistryError:
    try:
        callable_object()

    except ForecastRegistryError as exc:
        assert message_contains in str(exc)
        return exc

    raise AssertionError(
        "Expected ForecastRegistryError."
    )


# ----------------------------------------------------------
# Registry and service construction
# ----------------------------------------------------------

registry = EnterpriseModelRegistry()

versioning = EnterpriseModelVersioning(
    registry=registry,
)

promotion = EnterpriseModelPromotionService(
    registry=registry,
    versioning=versioning,
)

assert promotion.registry is registry
assert promotion.versioning is versioning

assert_promotion_error(
    lambda: EnterpriseModelPromotionService(
        registry="invalid-registry",
    ),
    message_contains="EnterpriseModelRegistry",
)

other_registry = EnterpriseModelRegistry()

assert_promotion_error(
    lambda: EnterpriseModelPromotionService(
        registry=registry,
        versioning=EnterpriseModelVersioning(
            registry=other_registry,
        ),
    ),
    message_contains="same instance",
)


# ----------------------------------------------------------
# Artifact factory
# ----------------------------------------------------------

def create_artifact(
    *,
    model_name: str,
    model_version: str,
    artifact_id: str,
    status: ForecastArtifactStatus = (
        ForecastArtifactStatus.PERSISTED
    ),
) -> ForecastArtifact:
    return ForecastArtifact(
        model_name=model_name,
        model_version=model_version,
        model_category=(
            ForecastModelCategory.MACHINE_LEARNING
        ),
        algorithm=model_name,
        storage_uri=(
            "s3://validation-models/"
            f"{model_name}/{model_version}/model"
        ),
        feature_columns=(
            "lag_1",
            "lag_7",
        ),
        target_column="order_line_count",
        forecast_horizon=14,
        artifact_id=artifact_id,
        artifact_version="1",
        status=status,
    )


# ----------------------------------------------------------
# Register model versions
# ----------------------------------------------------------

registration_v1 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="1.0.0",
        artifact_id="promotion-rf-100",
    )
)

registration_v2 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="2.0.0",
        artifact_id="promotion-rf-200",
    )
)

registration_v3 = registry.register(
    artifact=create_artifact(
        model_name="random_forest",
        model_version="3.0.0",
        artifact_id="promotion-rf-300",
    )
)

assert registry.total_models == 3


# ----------------------------------------------------------
# Initial lifecycle
# ----------------------------------------------------------

assert promotion.current_state(
    model_name="random_forest",
    model_version="1.0.0",
) == ForecastLifecycleState.REGISTERED

assert promotion.current_champion(
    "random_forest"
) is None


# ----------------------------------------------------------
# REGISTERED -> STAGING
# ----------------------------------------------------------

staging_result = promotion.promote_to_staging(
    model_name="random_forest",
    model_version="1.0.0",
    performed_by="databricks-validation",
    reason="Candidate passed validation.",
    metadata={
        "approval_ticket": "VAL-001",
    },
)

assert isinstance(
    staging_result,
    ForecastPromotionResult,
)

assert staging_result.success is True
assert staging_result.registration is registration_v1
assert staging_result.current_state == (
    ForecastLifecycleState.STAGING
)

assert staging_result.record.action == (
    ForecastPromotionAction.PROMOTE_TO_STAGING
)

assert staging_result.record.previous_state == (
    ForecastLifecycleState.REGISTERED
)

assert staging_result.record.new_state == (
    ForecastLifecycleState.STAGING
)

assert staging_result.record.performed_by == (
    "databricks-validation"
)

assert staging_result.record.metadata == {
    "approval_ticket": "VAL-001",
}


# ----------------------------------------------------------
# STAGING -> CHAMPION
# ----------------------------------------------------------

champion_result = promotion.promote_to_champion(
    model_name="random_forest",
    model_version="1.0.0",
    performed_by="databricks-validation",
    reason="Best validated model.",
)

assert champion_result.current_state == (
    ForecastLifecycleState.CHAMPION
)

assert promotion.current_champion(
    "random_forest"
) is registration_v1


# ----------------------------------------------------------
# One champion per model family
# ----------------------------------------------------------

promotion.promote_to_staging(
    model_name="random_forest",
    model_version="2.0.0",
)

assert_promotion_error(
    lambda: promotion.promote_to_champion(
        model_name="random_forest",
        model_version="2.0.0",
    ),
    message_contains="already has a champion",
)


# ----------------------------------------------------------
# Archive champion and promote next version
# ----------------------------------------------------------

archive_v1_result = promotion.archive(
    model_name="random_forest",
    model_version="1.0.0",
    reason="Superseded by version 2.0.0.",
)

assert archive_v1_result.current_state == (
    ForecastLifecycleState.ARCHIVED
)

assert promotion.current_champion(
    "random_forest"
) is None

champion_v2_result = promotion.promote_to_champion(
    model_name="random_forest",
    model_version="2.0.0",
)

assert champion_v2_result.current_state == (
    ForecastLifecycleState.CHAMPION
)

assert promotion.current_champion(
    "random_forest"
) is registration_v2


# ----------------------------------------------------------
# Prepare v3 and rollback to archived v1
# ----------------------------------------------------------

promotion.promote_to_staging(
    model_name="random_forest",
    model_version="3.0.0",
)

promotion.archive(
    model_name="random_forest",
    model_version="3.0.0",
)

rollback_result = promotion.rollback_champion(
    model_name="random_forest",
    performed_by="databricks-validation",
    reason="Version 2.0.0 production regression.",
)

assert rollback_result.registration is registration_v1

assert rollback_result.record.action == (
    ForecastPromotionAction.ROLLBACK_TO_CHAMPION
)

assert rollback_result.current_state == (
    ForecastLifecycleState.CHAMPION
)

assert promotion.current_state(
    model_name="random_forest",
    model_version="2.0.0",
) == ForecastLifecycleState.ARCHIVED

assert promotion.current_champion(
    "random_forest"
) is registration_v1


# ----------------------------------------------------------
# Archive and retire
# ----------------------------------------------------------

promotion.archive(
    model_name="random_forest",
    model_version="1.0.0",
)

retire_result = promotion.retire(
    model_name="random_forest",
    model_version="1.0.0",
)

assert retire_result.current_state == (
    ForecastLifecycleState.RETIRED
)

assert promotion.current_state(
    model_name="random_forest",
    model_version="1.0.0",
) == ForecastLifecycleState.RETIRED


# ----------------------------------------------------------
# Invalid lifecycle transitions
# ----------------------------------------------------------

# Version 2.0.0 is already ARCHIVED after rollback.
# Re-archiving an archived version is invalid.
assert_promotion_error(
    lambda: promotion.archive(
        model_name="random_forest",
        model_version="2.0.0",
    ),
    message_contains="Invalid model lifecycle transition",
)

# Version 1.0.0 is already RETIRED.
# A retired version cannot return to staging.
assert_promotion_error(
    lambda: promotion.promote_to_staging(
        model_name="random_forest",
        model_version="1.0.0",
    ),
    message_contains="Invalid model lifecycle transition",
)

# Version 3.0.0 is ARCHIVED.
# Direct promotion from ARCHIVED to CHAMPION is not allowed;
# restoration requires the rollback action.
assert_promotion_error(
    lambda: promotion.promote_to_champion(
        model_name="random_forest",
        model_version="3.0.0",
    ),
    message_contains="Invalid model lifecycle transition",
)


# ----------------------------------------------------------
# Promotion history
# ----------------------------------------------------------

v1_history = promotion.promotion_history(
    model_name="random_forest",
    model_version="1.0.0",
)

assert tuple(
    record.action
    for record in v1_history
) == (
    ForecastPromotionAction.PROMOTE_TO_STAGING,
    ForecastPromotionAction.PROMOTE_TO_CHAMPION,
    ForecastPromotionAction.ARCHIVE,
    ForecastPromotionAction.ROLLBACK_TO_CHAMPION,
    ForecastPromotionAction.ARCHIVE,
    ForecastPromotionAction.RETIRE,
)

family_history = promotion.promotion_history(
    model_name="random_forest",
)

assert len(family_history) >= len(v1_history)

assert all(
    isinstance(
        record,
        ForecastPromotionRecord,
    )
    for record in family_history
)


# ----------------------------------------------------------
# Serialization
# ----------------------------------------------------------

record_payload = staging_result.record.to_dict()

assert record_payload["model_name"] == (
    "random_forest"
)

assert record_payload["model_version"] == "1.0.0"

assert record_payload["action"] == (
    "PROMOTE_TO_STAGING"
)

assert record_payload["previous_state"] == (
    "REGISTERED"
)

assert record_payload["new_state"] == "STAGING"

result_payload = staging_result.to_dict()

assert result_payload["success"] is True
assert result_payload["current_state"] == "STAGING"

assert result_payload["registration"][
    "model_name"
] == "random_forest"

lifecycle_payload = promotion.to_dict(
    model_name="random_forest",
)

assert lifecycle_payload["model_name"] == (
    "random_forest"
)

assert lifecycle_payload["total_versions"] == 3
assert lifecycle_payload["champion_version"] is None
assert len(lifecycle_payload["versions"]) == 3


# ----------------------------------------------------------
# Immutable contracts
# ----------------------------------------------------------

try:
    staging_result.record.new_state = (
        ForecastLifecycleState.RETIRED
    )

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastPromotionRecord must be immutable."
    )

try:
    staging_result.current_state = (
        ForecastLifecycleState.RETIRED
    )

except FrozenInstanceError:
    pass

else:
    raise AssertionError(
        "ForecastPromotionResult must be immutable."
    )


# ----------------------------------------------------------
# Registration remains unchanged
# ----------------------------------------------------------

assert registration_v1.artifact_status == (
    ForecastArtifactStatus.PERSISTED
)

assert registration_v2.artifact_status == (
    ForecastArtifactStatus.PERSISTED
)

assert registration_v3.artifact_status == (
    ForecastArtifactStatus.PERSISTED
)


# ----------------------------------------------------------
# Unknown model handling
# ----------------------------------------------------------

assert_promotion_error(
    lambda: promotion.current_state(
        model_name="missing_model",
        model_version="1.0.0",
    ),
    message_contains="not registered",
)

assert_promotion_error(
    lambda: promotion.rollback_champion(
        model_name="missing_model",
    ),
    message_contains="does not have a champion",
)


# ----------------------------------------------------------
# Rollback without candidate
# ----------------------------------------------------------

single_registry = EnterpriseModelRegistry()

single_registration = single_registry.register(
    artifact=create_artifact(
        model_name="single_model",
        model_version="1.0.0",
        artifact_id="promotion-single-100",
    )
)

single_promotion = EnterpriseModelPromotionService(
    registry=single_registry,
)

single_promotion.promote_to_staging(
    model_name="single_model",
    model_version="1.0.0",
)

single_promotion.promote_to_champion(
    model_name="single_model",
    model_version="1.0.0",
)

assert_promotion_error(
    lambda: single_promotion.rollback_champion(
        model_name="single_model",
    ),
    message_contains="No archived previous version",
)


# ----------------------------------------------------------
# Invalid metadata
# ----------------------------------------------------------

new_registry = EnterpriseModelRegistry()

new_registry.register(
    artifact=create_artifact(
        model_name="metadata_model",
        model_version="1.0.0",
        artifact_id="promotion-metadata-100",
    )
)

new_promotion = EnterpriseModelPromotionService(
    registry=new_registry,
)

assert_promotion_error(
    lambda: new_promotion.promote_to_staging(
        model_name="metadata_model",
        model_version="1.0.0",
        metadata="invalid-metadata",
    ),
    message_contains="must be a mapping",
)


print(
    "forecast/model_registry/promotion.py validation: PASSED"
)

# COMMAND ----------

import importlib
import sys
from datetime import datetime, timezone


# ----------------------------------------------------------
# Fresh package import
# ----------------------------------------------------------

for module_name in (
    "src.forecast.model_registry.catalog",
    "src.forecast.model_registry.promotion",
    "src.forecast.model_registry.registry",
    "src.forecast.model_registry.versioning",
    "src.forecast.model_registry",
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()

model_registry_package = importlib.import_module(
    "src.forecast.model_registry"
)


# ----------------------------------------------------------
# Expected public exports
# ----------------------------------------------------------

expected_exports = {
    "EnterpriseModelCatalog",
    "EnterpriseModelPromotionService",
    "EnterpriseModelRegistry",
    "EnterpriseModelVersioning",
    "ForecastLifecycleState",
    "ForecastModelCatalogQuery",
    "ForecastModelCatalogResult",
    "ForecastModelRegistration",
    "ForecastModelVersion",
    "ForecastModelVersionEntry",
    "ForecastPromotionAction",
    "ForecastPromotionRecord",
    "ForecastPromotionResult",
}

assert set(model_registry_package.__all__) == expected_exports

for export_name in expected_exports:
    assert hasattr(
        model_registry_package,
        export_name,
    ), (
        "src.forecast.model_registry is missing public export: "
        f"{export_name}"
    )


# ----------------------------------------------------------
# Public package imports
# ----------------------------------------------------------

from src.forecast.model_registry import (
    EnterpriseModelCatalog,
    EnterpriseModelPromotionService,
    EnterpriseModelRegistry,
    EnterpriseModelVersioning,
    ForecastLifecycleState,
    ForecastModelCatalogQuery,
    ForecastModelCatalogResult,
    ForecastModelRegistration,
    ForecastModelVersion,
    ForecastModelVersionEntry,
    ForecastPromotionAction,
    ForecastPromotionRecord,
    ForecastPromotionResult,
)


# ----------------------------------------------------------
# Direct-import identity checks
# ----------------------------------------------------------

from src.forecast.model_registry.catalog import (
    EnterpriseModelCatalog as DirectCatalog,
    ForecastModelCatalogQuery as DirectCatalogQuery,
    ForecastModelCatalogResult as DirectCatalogResult,
)
from src.forecast.model_registry.promotion import (
    EnterpriseModelPromotionService as DirectPromotion,
    ForecastLifecycleState as DirectLifecycleState,
    ForecastPromotionAction as DirectPromotionAction,
    ForecastPromotionRecord as DirectPromotionRecord,
    ForecastPromotionResult as DirectPromotionResult,
)
from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry as DirectRegistry,
    ForecastModelRegistration as DirectRegistration,
)
from src.forecast.model_registry.versioning import (
    EnterpriseModelVersioning as DirectVersioning,
    ForecastModelVersion as DirectVersion,
    ForecastModelVersionEntry as DirectVersionEntry,
)

assert EnterpriseModelRegistry is DirectRegistry
assert ForecastModelRegistration is DirectRegistration

assert EnterpriseModelCatalog is DirectCatalog
assert ForecastModelCatalogQuery is DirectCatalogQuery
assert ForecastModelCatalogResult is DirectCatalogResult

assert EnterpriseModelVersioning is DirectVersioning
assert ForecastModelVersion is DirectVersion
assert ForecastModelVersionEntry is DirectVersionEntry

assert EnterpriseModelPromotionService is DirectPromotion
assert ForecastLifecycleState is DirectLifecycleState
assert ForecastPromotionAction is DirectPromotionAction
assert ForecastPromotionRecord is DirectPromotionRecord
assert ForecastPromotionResult is DirectPromotionResult


# ----------------------------------------------------------
# Service construction
# ----------------------------------------------------------

registry = EnterpriseModelRegistry()

catalog = EnterpriseModelCatalog(
    registry=registry,
)

versioning = EnterpriseModelVersioning(
    registry=registry,
)

promotion = EnterpriseModelPromotionService(
    registry=registry,
    versioning=versioning,
)

assert catalog.registry is registry
assert versioning.registry is registry
assert promotion.registry is registry
assert promotion.versioning is versioning


# ----------------------------------------------------------
# Contract construction
# ----------------------------------------------------------

query = ForecastModelCatalogQuery()

assert query.model_name is None
assert query.model_version is None
assert query.order_by == "model_name"
assert query.descending is False
assert query.limit is None

version = ForecastModelVersion.parse(
    "1.2.3"
)

assert version.major == 1
assert version.minor == 2
assert version.patch == 3
assert version.to_string() == "1.2.3"

record = ForecastPromotionRecord(
    model_name="demo_model",
    model_version="1.2.3",
    action=ForecastPromotionAction.PROMOTE_TO_STAGING,
    previous_state=ForecastLifecycleState.REGISTERED,
    new_state=ForecastLifecycleState.STAGING,
    promoted_at=datetime(
        2026,
        8,
        2,
        4,
        0,
        tzinfo=timezone.utc,
    ),
    performed_by="package-validation",
    reason="Validate public package contracts.",
)

assert record.model_name == "demo_model"
assert record.model_version == "1.2.3"
assert record.action == (
    ForecastPromotionAction.PROMOTE_TO_STAGING
)
assert record.previous_state == (
    ForecastLifecycleState.REGISTERED
)
assert record.new_state == (
    ForecastLifecycleState.STAGING
)


# ----------------------------------------------------------
# Empty service behavior
# ----------------------------------------------------------

assert registry.total_models == 0
assert registry.is_empty is True
assert registry.list_models() == ()

catalog_result = catalog.search()

assert isinstance(
    catalog_result,
    ForecastModelCatalogResult,
)
assert catalog_result.total_registry_models == 0
assert catalog_result.total_matches == 0
assert catalog_result.is_empty is True

assert versioning.list_versions(
    "unregistered_model"
) == ()

assert promotion.current_champion(
    "unregistered_model"
) is None


# ----------------------------------------------------------
# Serialization boundaries
# ----------------------------------------------------------

query_payload = query.to_dict()

assert query_payload["order_by"] == "model_name"
assert query_payload["descending"] is False
assert query_payload["limit"] is None

version_payload = version.to_dict()

assert version_payload == {
    "version": "1.2.3",
    "major": 1,
    "minor": 2,
    "patch": 3,
}

record_payload = record.to_dict()

assert record_payload["model_name"] == "demo_model"
assert record_payload["model_version"] == "1.2.3"
assert record_payload["action"] == "PROMOTE_TO_STAGING"
assert record_payload["previous_state"] == "REGISTERED"
assert record_payload["new_state"] == "STAGING"


print(
    "forecast/model_registry/__init__.py validation: PASSED"
)

# COMMAND ----------

# ============================================================
# Workforce Planning Models Validation
# ============================================================

from datetime import date

from src.workforce.models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)

capacity = WorkforceCapacity(
    planning_date=date.today(),
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
)

requirement = WorkforceRequirement(
    planning_date=date.today(),
    required_associates=45,
    expected_order_lines=48000,
    required_hours=450.0,
)

gap = WorkforceGap(
    planning_date=date.today(),
    available_associates=40,
    required_associates=45,
    shortage=5,
    overtime_required=True,
    recommended_overtime_hours=50.0,
)

assert capacity.available_associates == 40
assert requirement.required_associates == 45
assert gap.shortage == 5
assert gap.overtime_required is True

print("✅ Workforce models validation passed.")

# COMMAND ----------

# ============================================================
# Workforce Constants Validation
# ============================================================

from src.workforce.constants import (
    CAPACITY_STATUS_SHORTAGE,
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    RECOMMENDATION_REVIEW_OVERTIME,
    WORKFORCE_DOMAIN_VERSION,
)

assert WORKFORCE_DOMAIN_VERSION == "1.0.0"

assert DEFAULT_PRODUCTIVITY_LINES_PER_HOUR > 0
assert DEFAULT_SCHEDULED_HOURS == 10.0

assert 0 < DEFAULT_TARGET_UTILIZATION <= 1
assert 0 <= DEFAULT_SAFETY_BUFFER_RATIO < 1
assert 0 <= DEFAULT_FORECAST_CONFIDENCE <= 1

assert DEFAULT_MINIMUM_OVERTIME_HOURS == 5.0
assert DEFAULT_MAXIMUM_OVERTIME_HOURS == 10.0
assert (
    DEFAULT_MINIMUM_OVERTIME_HOURS
    <= DEFAULT_MAXIMUM_OVERTIME_HOURS
)

assert CAPACITY_STATUS_SHORTAGE == "SHORTAGE"
assert RECOMMENDATION_REVIEW_OVERTIME == "REVIEW_OVERTIME"

print("✅ Workforce constants validation passed.")

# COMMAND ----------

# ============================================================
# Workforce Exceptions Validation
# ============================================================

from src.workforce.exceptions import (
    WorkforceAvailabilityError,
    WorkforceCapacityError,
    WorkforceConfigurationError,
    WorkforceError,
    WorkforcePlanningError,
    WorkforceValidationError,
)

assert issubclass(WorkforceValidationError, WorkforceError)
assert issubclass(WorkforceConfigurationError, WorkforceError)
assert issubclass(WorkforceCapacityError, WorkforceError)
assert issubclass(WorkforceAvailabilityError, WorkforceError)
assert issubclass(WorkforcePlanningError, WorkforceError)

try:
    raise WorkforceValidationError("Invalid workforce input.")
except WorkforceError as exc:
    assert str(exc) == "Invalid workforce input."

try:
    raise WorkforcePlanningError("Planning execution failed.")
except WorkforceError as exc:
    assert str(exc) == "Planning execution failed."

print("✅ Workforce exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Workforce Package (__init__) Validation
# ============================================================

import importlib
from datetime import date

import src.workforce

# Refresh the package after editing __init__.py in Databricks.
importlib.reload(src.workforce)

from src.workforce import (
    DEFAULT_SCHEDULED_HOURS,
    RECOMMENDATION_NO_ACTION,
    WORKFORCE_DOMAIN_VERSION,
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceError,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)

assert WORKFORCE_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_SCHEDULED_HOURS == 10.0
assert RECOMMENDATION_NO_ACTION == "NO_ACTION"

capacity = WorkforceCapacity(
    planning_date=date.today(),
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

requirement = WorkforceRequirement(
    planning_date=date.today(),
    required_associates=45,
    expected_order_lines=48_000.0,
    required_hours=450.0,
)

gap = WorkforceGap(
    planning_date=date.today(),
    available_associates=40,
    required_associates=45,
    shortage=5,
    overtime_required=True,
    recommended_overtime_hours=50.0,
)

assert capacity.available_associates == 40
assert capacity.shift is ShiftType.SHIFT_1
assert requirement.required_associates == 45
assert gap.shortage == 5
assert issubclass(WorkforceError, Exception)

print("✅ Workforce package validation passed.")

# COMMAND ----------

# ============================================================
# Capacity Planning Configuration Validation
# ============================================================

import importlib

import src.planning.configuration

importlib.reload(src.planning.configuration)

from src.planning.configuration import (
    CapacityPlanningConfiguration,
    CapacityPlanningStrategy,
)
from src.workforce.exceptions import WorkforceConfigurationError


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = CapacityPlanningConfiguration()

assert configuration.productivity_lines_per_hour == 120.0
assert configuration.scheduled_hours == 10.0
assert configuration.target_utilization == 0.90
assert configuration.safety_buffer_ratio == 0.05
assert configuration.minimum_associates == 1
assert configuration.maximum_associates == 10_000
assert configuration.minimum_overtime_hours == 5.0
assert configuration.maximum_overtime_hours == 10.0
assert configuration.overtime_trigger_associate_gap == 1
assert configuration.default_forecast_confidence == 0.80
assert (
    configuration.planning_strategy
    is CapacityPlanningStrategy.STANDARD
)
assert configuration.configuration_version == "1.0.0"


# ------------------------------------------------------------
# Derived capacity properties
# ------------------------------------------------------------

assert configuration.productive_hours_per_associate == 9.0
assert configuration.effective_lines_per_associate == 1_080.0


# ------------------------------------------------------------
# Custom configuration
# ------------------------------------------------------------

custom_configuration = CapacityPlanningConfiguration(
    productivity_lines_per_hour=150.0,
    scheduled_hours=8.0,
    target_utilization=0.85,
    safety_buffer_ratio=0.10,
    minimum_associates=2,
    maximum_associates=500,
    minimum_overtime_hours=4.0,
    maximum_overtime_hours=8.0,
    overtime_trigger_associate_gap=2,
    default_forecast_confidence=0.90,
    planning_strategy=CapacityPlanningStrategy.CONSERVATIVE,
    configuration_version="1.1.0",
)

assert custom_configuration.productive_hours_per_associate == 6.8
assert custom_configuration.effective_lines_per_associate == 1_020.0


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

configuration_payload = custom_configuration.as_dict()

assert configuration_payload["planning_strategy"] == "CONSERVATIVE"
assert configuration_payload["configuration_version"] == "1.1.0"
assert configuration_payload["productivity_lines_per_hour"] == 150.0


# ------------------------------------------------------------
# Invalid configuration validation
# ------------------------------------------------------------

invalid_cases = [
    {
        "productivity_lines_per_hour": 0.0,
    },
    {
        "scheduled_hours": 0.0,
    },
    {
        "target_utilization": 1.1,
    },
    {
        "safety_buffer_ratio": -0.01,
    },
    {
        "minimum_associates": -1,
    },
    {
        "minimum_associates": 100,
        "maximum_associates": 50,
    },
    {
        "minimum_overtime_hours": 10.0,
        "maximum_overtime_hours": 5.0,
    },
    {
        "overtime_trigger_associate_gap": 0,
    },
    {
        "default_forecast_confidence": 1.1,
    },
    {
        "configuration_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        CapacityPlanningConfiguration(**invalid_arguments)
    except WorkforceConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected WorkforceConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Capacity planning configuration validation passed.")

# COMMAND ----------

# ============================================================
# Capacity Planning Calculations Validation
# ============================================================

import importlib
import math

import src.planning.calculations

importlib.reload(src.planning.calculations)

from src.planning.calculations import (
    calculate_associate_gap,
    calculate_associate_shortage,
    calculate_associate_surplus,
    calculate_available_capacity_lines,
    calculate_buffered_workload,
    calculate_capacity_utilization,
    calculate_required_associates,
    calculate_required_labor_hours,
)
from src.workforce.exceptions import WorkforceCapacityError


# ------------------------------------------------------------
# Standard capacity-planning scenario
# ------------------------------------------------------------

buffered_workload = calculate_buffered_workload(
    expected_order_lines=48_000.0,
    safety_buffer_ratio=0.05,
)

assert buffered_workload == 50_400.0


required_labor_hours = calculate_required_labor_hours(
    workload_lines=buffered_workload,
    productivity_lines_per_hour=120.0,
)

assert required_labor_hours == 420.0


required_associates = calculate_required_associates(
    required_labor_hours=required_labor_hours,
    productive_hours_per_associate=9.0,
    minimum_associates=1,
    maximum_associates=10_000,
)

assert required_associates == 47


available_capacity_lines = calculate_available_capacity_lines(
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    target_utilization=0.90,
)

assert available_capacity_lines == 43_200.0


associate_gap = calculate_associate_gap(
    required_associates=required_associates,
    available_associates=40,
)

assert associate_gap == 7


associate_shortage = calculate_associate_shortage(
    required_associates=required_associates,
    available_associates=40,
)

assert associate_shortage == 7


associate_surplus = calculate_associate_surplus(
    required_associates=required_associates,
    available_associates=40,
)

assert associate_surplus == 0


capacity_utilization = calculate_capacity_utilization(
    workload_lines=buffered_workload,
    available_capacity_lines=available_capacity_lines,
)

assert math.isclose(
    capacity_utilization,
    50_400.0 / 43_200.0,
    rel_tol=1e-12,
)


# ------------------------------------------------------------
# Surplus scenario
# ------------------------------------------------------------

assert (
    calculate_associate_gap(
        required_associates=35,
        available_associates=40,
    )
    == -5
)

assert (
    calculate_associate_shortage(
        required_associates=35,
        available_associates=40,
    )
    == 0
)

assert (
    calculate_associate_surplus(
        required_associates=35,
        available_associates=40,
    )
    == 5
)


# ------------------------------------------------------------
# Zero-workload behavior
# ------------------------------------------------------------

assert (
    calculate_buffered_workload(
        expected_order_lines=0.0,
        safety_buffer_ratio=0.05,
    )
    == 0.0
)

assert (
    calculate_required_labor_hours(
        workload_lines=0.0,
        productivity_lines_per_hour=120.0,
    )
    == 0.0
)

assert (
    calculate_capacity_utilization(
        workload_lines=0.0,
        available_capacity_lines=0.0,
    )
    == 0.0
)


# ------------------------------------------------------------
# Minimum-associate enforcement
# ------------------------------------------------------------

assert (
    calculate_required_associates(
        required_labor_hours=0.0,
        productive_hours_per_associate=9.0,
        minimum_associates=1,
        maximum_associates=100,
    )
    == 1
)


# ------------------------------------------------------------
# Invalid input validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: calculate_buffered_workload(
        expected_order_lines=-1.0,
        safety_buffer_ratio=0.05,
    ),
    lambda: calculate_buffered_workload(
        expected_order_lines=100.0,
        safety_buffer_ratio=1.0,
    ),
    lambda: calculate_required_labor_hours(
        workload_lines=100.0,
        productivity_lines_per_hour=0.0,
    ),
    lambda: calculate_required_associates(
        required_labor_hours=100.0,
        productive_hours_per_associate=0.0,
        minimum_associates=1,
        maximum_associates=100,
    ),
    lambda: calculate_required_associates(
        required_labor_hours=1_000.0,
        productive_hours_per_associate=1.0,
        minimum_associates=1,
        maximum_associates=100,
    ),
    lambda: calculate_available_capacity_lines(
        available_associates=-1,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        target_utilization=0.90,
    ),
    lambda: calculate_available_capacity_lines(
        available_associates=10,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        target_utilization=0.0,
    ),
    lambda: calculate_associate_gap(
        required_associates=10,
        available_associates=-1,
    ),
    lambda: calculate_capacity_utilization(
        workload_lines=100.0,
        available_capacity_lines=0.0,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except WorkforceCapacityError:
        pass
    else:
        raise AssertionError(
            "Expected WorkforceCapacityError."
        )


print("✅ Capacity planning calculations validation passed.")

# COMMAND ----------

# ============================================================
# Capacity Planning Engine Validation
# ============================================================

import importlib
from datetime import date

import src.planning.engine

importlib.reload(src.planning.engine)

from src.planning.configuration import (
    CapacityPlanningConfiguration,
)
from src.planning.engine import CapacityPlanningEngine
from src.workforce.exceptions import WorkforceValidationError
from src.workforce.models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceType,
)


planning_date = date.today()

configuration = CapacityPlanningConfiguration(
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    target_utilization=0.90,
    safety_buffer_ratio=0.05,
    minimum_associates=1,
    maximum_associates=10_000,
    minimum_overtime_hours=5.0,
    maximum_overtime_hours=10.0,
    overtime_trigger_associate_gap=1,
    default_forecast_confidence=0.80,
)

engine = CapacityPlanningEngine(
    configuration=configuration,
)


# ------------------------------------------------------------
# Shortage scenario
# ------------------------------------------------------------

shortage_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

requirement, gap = engine.evaluate(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    workforce_capacity=shortage_capacity,
    forecast_confidence=0.92,
)

assert requirement.planning_date == planning_date
assert requirement.required_associates == 47
assert requirement.expected_order_lines == 48_000.0
assert requirement.expected_workload_units == 50_400.0
assert requirement.required_hours == 420.0
assert requirement.confidence == 0.92

assert gap.available_associates == 40
assert gap.required_associates == 47
assert gap.shortage == 7
assert gap.overtime_required is True
assert gap.recommended_overtime_hours == 60.0


# ------------------------------------------------------------
# Sufficient-capacity scenario
# ------------------------------------------------------------

sufficient_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=50,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

sufficient_requirement, sufficient_gap = engine.evaluate(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    workforce_capacity=sufficient_capacity,
)

assert sufficient_requirement.required_associates == 47
assert sufficient_requirement.confidence == 0.80
assert sufficient_gap.shortage == 0
assert sufficient_gap.overtime_required is False
assert sufficient_gap.recommended_overtime_hours == 0.0


# ------------------------------------------------------------
# Zero-workload scenario
# ------------------------------------------------------------

zero_requirement, zero_gap = engine.evaluate(
    planning_date=planning_date,
    expected_order_lines=0.0,
    workforce_capacity=sufficient_capacity,
)

assert zero_requirement.required_associates == 1
assert zero_requirement.required_hours == 0.0
assert zero_gap.shortage == 0
assert zero_gap.overtime_required is False


# ------------------------------------------------------------
# Active configuration
# ------------------------------------------------------------

assert engine.configuration is configuration


# ------------------------------------------------------------
# Invalid request validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: engine.evaluate(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        workforce_capacity=shortage_capacity,
    ),
    lambda: engine.evaluate(
        planning_date=planning_date,
        expected_order_lines=100.0,
        workforce_capacity=shortage_capacity,
        forecast_confidence=1.1,
    ),
    lambda: engine.evaluate(
        planning_date=date(2026, 1, 1),
        expected_order_lines=100.0,
        workforce_capacity=shortage_capacity,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except WorkforceValidationError:
        pass
    else:
        raise AssertionError(
            "Expected WorkforceValidationError."
        )


print("✅ Capacity planning engine validation passed.")

# COMMAND ----------

# ============================================================
# Capacity Planning Reporting Validation
# ============================================================

import importlib
from datetime import date, datetime

import src.planning.reporting

importlib.reload(src.planning.reporting)

from src.planning.reporting import (
    CapacityPlanningReport,
    CapacityPlanningReporter,
)
from src.workforce.constants import (
    CAPACITY_STATUS_BALANCED,
    CAPACITY_STATUS_SHORTAGE,
    CAPACITY_STATUS_SURPLUS,
    RECOMMENDATION_NO_ACTION,
    RECOMMENDATION_REDUCE_STAFFING,
    RECOMMENDATION_REVIEW_OVERTIME,
)
from src.workforce.exceptions import WorkforceValidationError
from src.workforce.models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)


planning_date = date.today()

reporter = CapacityPlanningReporter()


# ------------------------------------------------------------
# Shortage report
# ------------------------------------------------------------

shortage_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

shortage_requirement = WorkforceRequirement(
    planning_date=planning_date,
    required_associates=47,
    expected_order_lines=48_000.0,
    expected_workload_units=50_400.0,
    required_hours=420.0,
    confidence=0.92,
)

shortage_gap = WorkforceGap(
    planning_date=planning_date,
    available_associates=40,
    required_associates=47,
    shortage=7,
    overtime_required=True,
    recommended_overtime_hours=60.0,
)

shortage_report = reporter.build(
    workforce_capacity=shortage_capacity,
    workforce_requirement=shortage_requirement,
    workforce_gap=shortage_gap,
)

assert isinstance(shortage_report, CapacityPlanningReport)
assert shortage_report.capacity_status == CAPACITY_STATUS_SHORTAGE
assert (
    shortage_report.recommendation
    == RECOMMENDATION_REVIEW_OVERTIME
)
assert shortage_report.associate_gap == 7
assert shortage_report.shortage == 7
assert shortage_report.surplus == 0
assert shortage_report.expected_order_lines == 48_000.0
assert shortage_report.buffered_workload_lines == 50_400.0
assert shortage_report.required_labor_hours == 420.0
assert shortage_report.forecast_confidence == 0.92
assert shortage_report.overtime_required is True
assert shortage_report.recommended_overtime_hours == 60.0
assert shortage_report.shift == "SHIFT_1"
assert shortage_report.workforce_type == "FULL_TIME"
assert isinstance(shortage_report.generated_at_utc, datetime)


# ------------------------------------------------------------
# Serializable report payload
# ------------------------------------------------------------

report_payload = shortage_report.as_dict()

assert report_payload["planning_date"] == planning_date.isoformat()
assert report_payload["capacity_status"] == "SHORTAGE"
assert report_payload["recommendation"] == "REVIEW_OVERTIME"
assert report_payload["report_version"] == "1.0.0"
assert isinstance(report_payload["generated_at_utc"], str)


# ------------------------------------------------------------
# Balanced report
# ------------------------------------------------------------

balanced_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_2,
    workforce_type=WorkforceType.TEMPORARY,
    available_associates=47,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
)

balanced_gap = WorkforceGap(
    planning_date=planning_date,
    available_associates=47,
    required_associates=47,
    shortage=0,
    overtime_required=False,
    recommended_overtime_hours=0.0,
)

balanced_report = reporter.build(
    workforce_capacity=balanced_capacity,
    workforce_requirement=shortage_requirement,
    workforce_gap=balanced_gap,
)

assert balanced_report.capacity_status == CAPACITY_STATUS_BALANCED
assert balanced_report.recommendation == RECOMMENDATION_NO_ACTION
assert balanced_report.associate_gap == 0
assert balanced_report.shortage == 0
assert balanced_report.surplus == 0


# ------------------------------------------------------------
# Surplus report
# ------------------------------------------------------------

surplus_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=52,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
)

surplus_gap = WorkforceGap(
    planning_date=planning_date,
    available_associates=52,
    required_associates=47,
    shortage=0,
    overtime_required=False,
    recommended_overtime_hours=0.0,
)

surplus_report = reporter.build(
    workforce_capacity=surplus_capacity,
    workforce_requirement=shortage_requirement,
    workforce_gap=surplus_gap,
)

assert surplus_report.capacity_status == CAPACITY_STATUS_SURPLUS
assert (
    surplus_report.recommendation
    == RECOMMENDATION_REDUCE_STAFFING
)
assert surplus_report.associate_gap == -5
assert surplus_report.shortage == 0
assert surplus_report.surplus == 5


# ------------------------------------------------------------
# Invalid reporting input
# ------------------------------------------------------------

mismatched_gap = WorkforceGap(
    planning_date=date(2026, 1, 1),
    available_associates=40,
    required_associates=47,
    shortage=7,
    overtime_required=True,
    recommended_overtime_hours=60.0,
)

try:
    reporter.build(
        workforce_capacity=shortage_capacity,
        workforce_requirement=shortage_requirement,
        workforce_gap=mismatched_gap,
    )
except WorkforceValidationError:
    pass
else:
    raise AssertionError(
        "Expected WorkforceValidationError for mismatched dates."
    )


print("✅ Capacity planning reporting validation passed.")

# COMMAND ----------

# ============================================================
# Capacity Planning Service Validation
# ============================================================

import importlib
from datetime import date

import src.planning.service

importlib.reload(src.planning.service)

from src.planning.configuration import (
    CapacityPlanningConfiguration,
)
from src.planning.engine import CapacityPlanningEngine
from src.planning.reporting import (
    CapacityPlanningReport,
    CapacityPlanningReporter,
)
from src.planning.service import CapacityPlanningService
from src.workforce.constants import (
    CAPACITY_STATUS_BALANCED,
    CAPACITY_STATUS_SHORTAGE,
    RECOMMENDATION_NO_ACTION,
    RECOMMENDATION_REVIEW_OVERTIME,
)
from src.workforce.exceptions import (
    WorkforceValidationError,
)
from src.workforce.models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceType,
)


planning_date = date.today()

configuration = CapacityPlanningConfiguration(
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    target_utilization=0.90,
    safety_buffer_ratio=0.05,
    minimum_associates=1,
    maximum_associates=10_000,
    minimum_overtime_hours=5.0,
    maximum_overtime_hours=10.0,
    overtime_trigger_associate_gap=1,
    default_forecast_confidence=0.80,
)

engine = CapacityPlanningEngine(
    configuration=configuration,
)

reporter = CapacityPlanningReporter()

service = CapacityPlanningService(
    configuration=configuration,
    engine=engine,
    reporter=reporter,
)


# ------------------------------------------------------------
# Dependency wiring
# ------------------------------------------------------------

assert service.configuration is configuration
assert service.engine is engine
assert service.reporter is reporter


# ------------------------------------------------------------
# Shortage planning scenario
# ------------------------------------------------------------

shortage_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

shortage_report = service.plan(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    workforce_capacity=shortage_capacity,
    forecast_confidence=0.92,
)

assert isinstance(shortage_report, CapacityPlanningReport)
assert shortage_report.capacity_status == CAPACITY_STATUS_SHORTAGE
assert (
    shortage_report.recommendation
    == RECOMMENDATION_REVIEW_OVERTIME
)
assert shortage_report.available_associates == 40
assert shortage_report.required_associates == 47
assert shortage_report.associate_gap == 7
assert shortage_report.shortage == 7
assert shortage_report.overtime_required is True
assert shortage_report.recommended_overtime_hours == 60.0
assert shortage_report.forecast_confidence == 0.92


# ------------------------------------------------------------
# Balanced planning scenario
# ------------------------------------------------------------

balanced_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_2,
    workforce_type=WorkforceType.TEMPORARY,
    available_associates=47,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
)

balanced_report = service.plan(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    workforce_capacity=balanced_capacity,
)

assert balanced_report.capacity_status == CAPACITY_STATUS_BALANCED
assert balanced_report.recommendation == RECOMMENDATION_NO_ACTION
assert balanced_report.associate_gap == 0
assert balanced_report.shortage == 0
assert balanced_report.overtime_required is False
assert balanced_report.forecast_confidence == 0.80


# ------------------------------------------------------------
# Default service construction
# ------------------------------------------------------------

default_service = CapacityPlanningService()

assert isinstance(
    default_service.configuration,
    CapacityPlanningConfiguration,
)
assert isinstance(
    default_service.engine,
    CapacityPlanningEngine,
)
assert isinstance(
    default_service.reporter,
    CapacityPlanningReporter,
)


# ------------------------------------------------------------
# Serializable output
# ------------------------------------------------------------

report_payload = shortage_report.as_dict()

assert report_payload["capacity_status"] == "SHORTAGE"
assert report_payload["required_associates"] == 47
assert report_payload["planning_date"] == planning_date.isoformat()


# ------------------------------------------------------------
# Invalid dependency wiring
# ------------------------------------------------------------

different_configuration = CapacityPlanningConfiguration(
    target_utilization=0.85,
)

try:
    CapacityPlanningService(
        configuration=different_configuration,
        engine=engine,
    )
except WorkforceValidationError:
    pass
else:
    raise AssertionError(
        "Expected WorkforceValidationError for inconsistent "
        "configuration and engine dependencies."
    )


# ------------------------------------------------------------
# Invalid planning request
# ------------------------------------------------------------

try:
    service.plan(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        workforce_capacity=shortage_capacity,
    )
except WorkforceValidationError:
    pass
else:
    raise AssertionError(
        "Expected WorkforceValidationError for negative workload."
    )


print("✅ Capacity planning service validation passed.")

# COMMAND ----------

# ============================================================
# Planning Package (__init__) Validation
# ============================================================

import importlib

import src.planning

importlib.reload(src.planning)

from src.planning import (
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    MAX_FORECAST_CONFIDENCE,
    MAXIMUM_ASSOCIATES,
    MAXIMUM_OVERTIME_HOURS,
    MIN_FORECAST_CONFIDENCE,
    MINIMUM_ASSOCIATES,
    MINIMUM_OVERTIME_HOURS,
    PLANNING_DOMAIN_VERSION,
    CapacityPlanningCalculationError,
    CapacityPlanningConfiguration,
    CapacityPlanningConfigurationError,
    CapacityPlanningEngine,
    CapacityPlanningEngineError,
    CapacityPlanningError,
    CapacityPlanningReport,
    CapacityPlanningReporter,
    CapacityPlanningReportingError,
    CapacityPlanningRequest,
    CapacityPlanningResult,
    CapacityPlanningService,
    CapacityPlanningServiceError,
    CapacityPlanningValidationError,
)

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert PLANNING_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert DEFAULT_FORECAST_CONFIDENCE == 0.80

assert MINIMUM_ASSOCIATES == 1
assert MAXIMUM_ASSOCIATES == 10_000

assert DEFAULT_PRODUCTIVITY_LINES_PER_HOUR == 120.0
assert DEFAULT_SCHEDULED_HOURS == 10.0

assert MINIMUM_OVERTIME_HOURS == 5.0
assert MAXIMUM_OVERTIME_HOURS == 10.0

assert DEFAULT_TARGET_UTILIZATION == 0.90
assert DEFAULT_SAFETY_BUFFER_RATIO == 0.05
assert DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP == 1


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    CapacityPlanningValidationError,
    CapacityPlanningError,
)
assert issubclass(
    CapacityPlanningConfigurationError,
    CapacityPlanningError,
)
assert issubclass(
    CapacityPlanningCalculationError,
    CapacityPlanningError,
)
assert issubclass(
    CapacityPlanningEngineError,
    CapacityPlanningError,
)
assert issubclass(
    CapacityPlanningReportingError,
    CapacityPlanningError,
)
assert issubclass(
    CapacityPlanningServiceError,
    CapacityPlanningError,
)


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

assert CapacityPlanningRequest is not None
assert CapacityPlanningResult is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert CapacityPlanningConfiguration is not None
assert CapacityPlanningEngine is not None
assert CapacityPlanningReport is not None
assert CapacityPlanningReporter is not None
assert CapacityPlanningService is not None


print("✅ Planning package validation passed.")

# COMMAND ----------

# ============================================================
# Planning Constants Validation
# ============================================================

import importlib

import src.planning.constants

importlib.reload(src.planning.constants)

from src.planning.constants import (
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    MAX_FORECAST_CONFIDENCE,
    MAXIMUM_ASSOCIATES,
    MAXIMUM_OVERTIME_HOURS,
    MIN_FORECAST_CONFIDENCE,
    MINIMUM_ASSOCIATES,
    MINIMUM_OVERTIME_HOURS,
    PLANNING_DOMAIN_VERSION,
)

assert PLANNING_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert 0.0 <= DEFAULT_FORECAST_CONFIDENCE <= 1.0

assert MINIMUM_ASSOCIATES == 1
assert MAXIMUM_ASSOCIATES > MINIMUM_ASSOCIATES

assert DEFAULT_PRODUCTIVITY_LINES_PER_HOUR > 0

assert DEFAULT_SCHEDULED_HOURS == 10.0

assert MINIMUM_OVERTIME_HOURS == 5.0
assert MAXIMUM_OVERTIME_HOURS == 10.0

assert (
    MINIMUM_OVERTIME_HOURS
    <= MAXIMUM_OVERTIME_HOURS
)

assert 0 < DEFAULT_TARGET_UTILIZATION <= 1
assert 0 <= DEFAULT_SAFETY_BUFFER_RATIO < 1

assert DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP == 1

print("✅ Planning constants validation passed.")

# COMMAND ----------

# ============================================================
# Planning Exceptions Validation
# ============================================================

import importlib

import src.planning.exceptions

importlib.reload(src.planning.exceptions)

from src.planning.exceptions import (
    CapacityPlanningCalculationError,
    CapacityPlanningConfigurationError,
    CapacityPlanningEngineError,
    CapacityPlanningError,
    CapacityPlanningReportingError,
    CapacityPlanningServiceError,
    CapacityPlanningValidationError,
)

from src.workforce.exceptions import WorkforceError


assert issubclass(
    CapacityPlanningError,
    WorkforceError,
)

assert issubclass(
    CapacityPlanningValidationError,
    CapacityPlanningError,
)

assert issubclass(
    CapacityPlanningConfigurationError,
    CapacityPlanningError,
)

assert issubclass(
    CapacityPlanningCalculationError,
    CapacityPlanningError,
)

assert issubclass(
    CapacityPlanningEngineError,
    CapacityPlanningError,
)

assert issubclass(
    CapacityPlanningReportingError,
    CapacityPlanningError,
)

assert issubclass(
    CapacityPlanningServiceError,
    CapacityPlanningError,
)


try:
    raise CapacityPlanningValidationError(
        "Invalid planning request."
    )
except CapacityPlanningError as exc:
    assert str(exc) == "Invalid planning request."


try:
    raise CapacityPlanningEngineError(
        "Planning engine failed."
    )
except CapacityPlanningError as exc:
    assert str(exc) == "Planning engine failed."


print("✅ Planning exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Planning Models Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.planning.models

importlib.reload(src.planning.models)

from src.planning.exceptions import (
    CapacityPlanningValidationError,
)
from src.planning.models import (
    CapacityPlanningRequest,
    CapacityPlanningResult,
)
from src.workforce.models import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)


planning_date = date.today()

capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
    metadata={"warehouse": "US38"},
)

request = CapacityPlanningRequest(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    workforce_capacity=capacity,
    forecast_confidence=0.92,
)

assert request.planning_date == planning_date
assert request.expected_order_lines == 48_000.0
assert request.forecast_confidence == 0.92

request_payload = request.as_dict()

assert request_payload["planning_date"] == planning_date.isoformat()
assert request_payload["shift"] == "SHIFT_1"
assert request_payload["workforce_type"] == "FULL_TIME"
assert request_payload["available_associates"] == 40
assert request_payload["metadata"]["warehouse"] == "US38"


requirement = WorkforceRequirement(
    planning_date=planning_date,
    required_associates=47,
    expected_order_lines=48_000.0,
    expected_workload_units=50_400.0,
    required_hours=420.0,
    confidence=0.92,
)

gap = WorkforceGap(
    planning_date=planning_date,
    available_associates=40,
    required_associates=47,
    shortage=7,
    overtime_required=True,
    recommended_overtime_hours=60.0,
)

generated_at_utc = datetime.now(timezone.utc)

result = CapacityPlanningResult(
    request=request,
    requirement=requirement,
    gap=gap,
    generated_at_utc=generated_at_utc,
)

assert result.planning_date == planning_date
assert result.available_associates == 40
assert result.required_associates == 47
assert result.associate_gap == 7
assert result.has_shortage is True
assert result.planning_version == "1.0.0"

result_payload = result.as_dict()

assert result_payload["planning_date"] == planning_date.isoformat()
assert result_payload["expected_order_lines"] == 48_000.0
assert result_payload["available_associates"] == 40
assert result_payload["required_associates"] == 47
assert result_payload["associate_gap"] == 7
assert result_payload["shortage"] == 7
assert result_payload["overtime_required"] is True
assert result_payload["recommended_overtime_hours"] == 60.0
assert result_payload["shift"] == "SHIFT_1"
assert result_payload["planning_version"] == "1.0.0"
assert result_payload["generated_at_utc"] == (
    generated_at_utc.isoformat()
)


# ------------------------------------------------------------
# Invalid request validation
# ------------------------------------------------------------

invalid_request_calls = [
    lambda: CapacityPlanningRequest(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        workforce_capacity=capacity,
    ),
    lambda: CapacityPlanningRequest(
        planning_date=planning_date,
        expected_order_lines=100.0,
        workforce_capacity=capacity,
        forecast_confidence=1.1,
    ),
    lambda: CapacityPlanningRequest(
        planning_date=date(2026, 1, 1),
        expected_order_lines=100.0,
        workforce_capacity=capacity,
    ),
]

for invalid_call in invalid_request_calls:
    try:
        invalid_call()
    except CapacityPlanningValidationError:
        pass
    else:
        raise AssertionError(
            "Expected CapacityPlanningValidationError."
        )


# ------------------------------------------------------------
# Invalid result consistency
# ------------------------------------------------------------

mismatched_gap = WorkforceGap(
    planning_date=date(2026, 1, 1),
    available_associates=40,
    required_associates=47,
    shortage=7,
    overtime_required=True,
    recommended_overtime_hours=60.0,
)

try:
    CapacityPlanningResult(
        request=request,
        requirement=requirement,
        gap=mismatched_gap,
        generated_at_utc=generated_at_utc,
    )
except CapacityPlanningValidationError:
    pass
else:
    raise AssertionError(
        "Expected CapacityPlanningValidationError for "
        "inconsistent planning dates."
    )


print("✅ Planning models validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Constants Validation
# ============================================================

import importlib

import src.overtime.constants

importlib.reload(src.overtime.constants)

from src.overtime.constants import (
    DEFAULT_CRITICAL_SHORTAGE_GAP,
    DEFAULT_HIGH_CONFIDENCE_THRESHOLD,
    DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_MANDATORY_OVERTIME_MAX_GAP,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_RECOMMENDATION_CONFIDENCE,
    DEFAULT_STANDARD_OVERTIME_HOURS,
    DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP,
    DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP,
    MAXIMUM_RECOMMENDATION_CONFIDENCE,
    MINIMUM_RECOMMENDATION_CONFIDENCE,
    OVERTIME_DOMAIN_VERSION,
    OVERTIME_TYPE_MANDATORY,
    OVERTIME_TYPE_NONE,
    OVERTIME_TYPE_VOLUNTARY,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW,
    RECOMMENDATION_MANDATORY_OVERTIME,
    RECOMMENDATION_NONE,
    RECOMMENDATION_OPERATIONAL_REVIEW,
    RECOMMENDATION_TEMPORARY_LABOR,
    RECOMMENDATION_VOLUNTARY_OVERTIME,
    STATUS_NOT_REQUIRED,
    STATUS_RECOMMENDED,
    STATUS_REQUIRED,
    STATUS_REVIEW_REQUIRED,
    SUPPORTED_OVERTIME_TYPES,
    SUPPORTED_RECOMMENDATION_PRIORITIES,
    SUPPORTED_RECOMMENDATION_STATUSES,
    SUPPORTED_RECOMMENDATION_TYPES,
)


# ------------------------------------------------------------
# Domain version
# ------------------------------------------------------------

assert OVERTIME_DOMAIN_VERSION == "1.0.0"


# ------------------------------------------------------------
# Overtime duration policy
# ------------------------------------------------------------

assert DEFAULT_MINIMUM_OVERTIME_HOURS == 5.0
assert DEFAULT_MAXIMUM_OVERTIME_HOURS == 10.0
assert DEFAULT_STANDARD_OVERTIME_HOURS == 5.0

assert (
    DEFAULT_MINIMUM_OVERTIME_HOURS
    <= DEFAULT_STANDARD_OVERTIME_HOURS
    <= DEFAULT_MAXIMUM_OVERTIME_HOURS
)


# ------------------------------------------------------------
# Recommendation thresholds
# ------------------------------------------------------------

assert DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP == 3
assert DEFAULT_MANDATORY_OVERTIME_MAX_GAP == 10
assert DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP == 11
assert DEFAULT_CRITICAL_SHORTAGE_GAP == 20

assert (
    DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP
    < DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP
)

assert (
    DEFAULT_MANDATORY_OVERTIME_MAX_GAP
    < DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP
)

assert (
    DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP
    < DEFAULT_CRITICAL_SHORTAGE_GAP
)


# ------------------------------------------------------------
# Confidence thresholds
# ------------------------------------------------------------

assert MINIMUM_RECOMMENDATION_CONFIDENCE == 0.0
assert MAXIMUM_RECOMMENDATION_CONFIDENCE == 1.0

assert (
    MINIMUM_RECOMMENDATION_CONFIDENCE
    <= DEFAULT_RECOMMENDATION_CONFIDENCE
    <= MAXIMUM_RECOMMENDATION_CONFIDENCE
)

assert (
    MINIMUM_RECOMMENDATION_CONFIDENCE
    <= DEFAULT_LOW_CONFIDENCE_THRESHOLD
    < DEFAULT_HIGH_CONFIDENCE_THRESHOLD
    <= MAXIMUM_RECOMMENDATION_CONFIDENCE
)


# ------------------------------------------------------------
# Supported recommendation values
# ------------------------------------------------------------

assert RECOMMENDATION_NONE in SUPPORTED_RECOMMENDATION_TYPES

assert (
    RECOMMENDATION_VOLUNTARY_OVERTIME
    in SUPPORTED_RECOMMENDATION_TYPES
)

assert (
    RECOMMENDATION_MANDATORY_OVERTIME
    in SUPPORTED_RECOMMENDATION_TYPES
)

assert (
    RECOMMENDATION_TEMPORARY_LABOR
    in SUPPORTED_RECOMMENDATION_TYPES
)

assert (
    RECOMMENDATION_FULL_TIME_HIRING_REVIEW
    in SUPPORTED_RECOMMENDATION_TYPES
)

assert (
    RECOMMENDATION_OPERATIONAL_REVIEW
    in SUPPORTED_RECOMMENDATION_TYPES
)


# ------------------------------------------------------------
# Supported priorities
# ------------------------------------------------------------

assert SUPPORTED_RECOMMENDATION_PRIORITIES == (
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
)


# ------------------------------------------------------------
# Supported statuses
# ------------------------------------------------------------

assert SUPPORTED_RECOMMENDATION_STATUSES == (
    STATUS_NOT_REQUIRED,
    STATUS_RECOMMENDED,
    STATUS_REQUIRED,
    STATUS_REVIEW_REQUIRED,
)


# ------------------------------------------------------------
# Supported overtime types
# ------------------------------------------------------------

assert SUPPORTED_OVERTIME_TYPES == (
    OVERTIME_TYPE_NONE,
    OVERTIME_TYPE_VOLUNTARY,
    OVERTIME_TYPE_MANDATORY,
)


# ------------------------------------------------------------
# Uniqueness
# ------------------------------------------------------------

assert len(SUPPORTED_RECOMMENDATION_TYPES) == len(
    set(SUPPORTED_RECOMMENDATION_TYPES)
)

assert len(SUPPORTED_RECOMMENDATION_PRIORITIES) == len(
    set(SUPPORTED_RECOMMENDATION_PRIORITIES)
)

assert len(SUPPORTED_RECOMMENDATION_STATUSES) == len(
    set(SUPPORTED_RECOMMENDATION_STATUSES)
)

assert len(SUPPORTED_OVERTIME_TYPES) == len(
    set(SUPPORTED_OVERTIME_TYPES)
)


print("✅ Overtime constants validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Exceptions Validation
# ============================================================

import importlib

import src.overtime.exceptions

importlib.reload(src.overtime.exceptions)

from src.overtime.exceptions import (
    OvertimeCapacityError,
    OvertimeConfigurationError,
    OvertimeEngineError,
    OvertimeError,
    OvertimePolicyError,
    OvertimeRecommendationError,
    OvertimeServiceError,
    OvertimeValidationError,
)


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    OvertimeValidationError,
    OvertimeError,
)

assert issubclass(
    OvertimeConfigurationError,
    OvertimeError,
)

assert issubclass(
    OvertimeRecommendationError,
    OvertimeError,
)

assert issubclass(
    OvertimeCapacityError,
    OvertimeError,
)

assert issubclass(
    OvertimePolicyError,
    OvertimeError,
)

assert issubclass(
    OvertimeEngineError,
    OvertimeError,
)

assert issubclass(
    OvertimeServiceError,
    OvertimeError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise OvertimeValidationError(
        "Invalid overtime request."
    )
except OvertimeError as exc:
    assert str(exc) == "Invalid overtime request."


try:
    raise OvertimeEngineError(
        "Recommendation engine failed."
    )
except OvertimeError as exc:
    assert str(exc) == "Recommendation engine failed."


try:
    raise OvertimePolicyError(
        "Policy violation."
    )
except OvertimeError as exc:
    assert str(exc) == "Policy violation."


print("✅ Overtime exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Models Validation
# ============================================================

import importlib
from datetime import date

import src.overtime.models

importlib.reload(src.overtime.models)

from src.overtime.exceptions import OvertimeValidationError
from src.overtime.models import (
    OvertimeRecommendation,
    OvertimeRequest,
    OvertimeType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)

planning_date = date.today()

# ------------------------------------------------------------
# Valid request
# ------------------------------------------------------------

request = OvertimeRequest(
    planning_date=planning_date,
    associate_gap=5,
    forecast_confidence=0.92,
)

assert request.associate_gap == 5

# ------------------------------------------------------------
# Valid recommendation
# ------------------------------------------------------------

recommendation = OvertimeRecommendation(
    planning_date=planning_date,
    recommendation=RecommendationType.MANDATORY_OVERTIME,
    priority=RecommendationPriority.HIGH,
    status=RecommendationStatus.REQUIRED,
    overtime_type=OvertimeType.MANDATORY,
    overtime_hours=10.0,
    associate_gap=5,
    forecast_confidence=0.92,
    rationale="Associate shortage requires mandatory overtime.",
)

assert recommendation.overtime_hours == 10.0
assert recommendation.priority is RecommendationPriority.HIGH
assert recommendation.status is RecommendationStatus.REQUIRED
assert recommendation.recommendation is (
    RecommendationType.MANDATORY_OVERTIME
)

# ------------------------------------------------------------
# Invalid request
# ------------------------------------------------------------

invalid_calls = [

    lambda: OvertimeRequest(
        planning_date=planning_date,
        associate_gap=-1,
        forecast_confidence=0.8,
    ),

    lambda: OvertimeRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=1.5,
    ),

    lambda: OvertimeRecommendation(
        planning_date=planning_date,
        recommendation=RecommendationType.NONE,
        priority=RecommendationPriority.LOW,
        status=RecommendationStatus.NOT_REQUIRED,
        overtime_type=OvertimeType.NONE,
        overtime_hours=-5.0,
        associate_gap=0,
        forecast_confidence=0.8,
        rationale="OK",
    ),

    lambda: OvertimeRecommendation(
        planning_date=planning_date,
        recommendation=RecommendationType.NONE,
        priority=RecommendationPriority.LOW,
        status=RecommendationStatus.NOT_REQUIRED,
        overtime_type=OvertimeType.NONE,
        overtime_hours=0.0,
        associate_gap=0,
        forecast_confidence=0.8,
        rationale="",
    ),
]

for invalid_call in invalid_calls:

    try:
        invalid_call()

    except OvertimeValidationError:
        pass

    else:
        raise AssertionError(
            "Expected OvertimeValidationError."
        )

print("✅ Overtime models validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Configuration Validation
# ============================================================

import importlib

import src.overtime.configuration

importlib.reload(src.overtime.configuration)

from src.overtime.configuration import OvertimeConfiguration
from src.overtime.exceptions import OvertimeConfigurationError


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = OvertimeConfiguration()

assert configuration.minimum_overtime_hours == 5.0
assert configuration.maximum_overtime_hours == 10.0
assert configuration.standard_overtime_hours == 5.0

assert configuration.voluntary_overtime_max_gap == 3
assert configuration.mandatory_overtime_max_gap == 10
assert configuration.temporary_labor_trigger_gap == 11
assert configuration.critical_shortage_gap == 20

assert configuration.default_recommendation_confidence == 0.80
assert configuration.low_confidence_threshold == 0.60
assert configuration.high_confidence_threshold == 0.85
assert configuration.configuration_version == "1.0.0"


# ------------------------------------------------------------
# Valid custom configuration
# ------------------------------------------------------------

custom_configuration = OvertimeConfiguration(
    minimum_overtime_hours=4.0,
    maximum_overtime_hours=8.0,
    standard_overtime_hours=6.0,
    voluntary_overtime_max_gap=4,
    mandatory_overtime_max_gap=12,
    temporary_labor_trigger_gap=13,
    critical_shortage_gap=25,
    default_recommendation_confidence=0.90,
    low_confidence_threshold=0.55,
    high_confidence_threshold=0.88,
    configuration_version="1.1.0",
)

assert custom_configuration.standard_overtime_hours == 6.0
assert custom_configuration.voluntary_overtime_max_gap == 4
assert custom_configuration.critical_shortage_gap == 25
assert custom_configuration.configuration_version == "1.1.0"


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

configuration_payload = custom_configuration.as_dict()

assert configuration_payload["minimum_overtime_hours"] == 4.0
assert configuration_payload["maximum_overtime_hours"] == 8.0
assert configuration_payload["critical_shortage_gap"] == 25
assert configuration_payload["configuration_version"] == "1.1.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "minimum_overtime_hours": 0.0,
    },
    {
        "maximum_overtime_hours": 0.0,
    },
    {
        "minimum_overtime_hours": 10.0,
        "maximum_overtime_hours": 5.0,
    },
    {
        "minimum_overtime_hours": 5.0,
        "maximum_overtime_hours": 10.0,
        "standard_overtime_hours": 12.0,
    },
    {
        "voluntary_overtime_max_gap": 0,
    },
    {
        "voluntary_overtime_max_gap": 12,
        "temporary_labor_trigger_gap": 11,
    },
    {
        "mandatory_overtime_max_gap": 11,
        "temporary_labor_trigger_gap": 11,
    },
    {
        "temporary_labor_trigger_gap": 20,
        "critical_shortage_gap": 20,
    },
    {
        "default_recommendation_confidence": 1.1,
    },
    {
        "low_confidence_threshold": 0.90,
        "high_confidence_threshold": 0.80,
    },
    {
        "configuration_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        OvertimeConfiguration(**invalid_arguments)
    except OvertimeConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected OvertimeConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Overtime configuration validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Recommendation Engine Validation
# ============================================================

import importlib
from datetime import date

import src.overtime.engine

importlib.reload(src.overtime.engine)

from src.overtime.configuration import OvertimeConfiguration
from src.overtime.engine import OvertimeRecommendationEngine
from src.overtime.exceptions import OvertimeValidationError
from src.overtime.models import (
    OvertimeRequest,
    OvertimeType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)


planning_date = date.today()

configuration = OvertimeConfiguration()

engine = OvertimeRecommendationEngine(
    configuration=configuration,
)

assert engine.configuration is configuration


# ------------------------------------------------------------
# No-shortage scenario
# ------------------------------------------------------------

no_action = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.90,
    ),
)

assert no_action.recommendation is RecommendationType.NONE
assert no_action.priority is RecommendationPriority.LOW
assert no_action.status is RecommendationStatus.NOT_REQUIRED
assert no_action.overtime_type is OvertimeType.NONE
assert no_action.overtime_hours == 0.0


# ------------------------------------------------------------
# Low-confidence scenario
# ------------------------------------------------------------

low_confidence = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.50,
    ),
)

assert (
    low_confidence.recommendation
    is RecommendationType.OPERATIONAL_REVIEW
)
assert (
    low_confidence.status
    is RecommendationStatus.REVIEW_REQUIRED
)
assert low_confidence.overtime_type is OvertimeType.NONE
assert low_confidence.overtime_hours == 0.0


# ------------------------------------------------------------
# Voluntary overtime scenario
# ------------------------------------------------------------

voluntary = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.90,
    ),
)

assert (
    voluntary.recommendation
    is RecommendationType.VOLUNTARY_OVERTIME
)
assert voluntary.priority is RecommendationPriority.MEDIUM
assert voluntary.status is RecommendationStatus.RECOMMENDED
assert voluntary.overtime_type is OvertimeType.VOLUNTARY
assert voluntary.overtime_hours == 15.0


# ------------------------------------------------------------
# Mandatory overtime scenario
# ------------------------------------------------------------

mandatory = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=7,
        forecast_confidence=0.92,
    ),
)

assert (
    mandatory.recommendation
    is RecommendationType.MANDATORY_OVERTIME
)
assert mandatory.priority is RecommendationPriority.HIGH
assert mandatory.status is RecommendationStatus.REQUIRED
assert mandatory.overtime_type is OvertimeType.MANDATORY
assert mandatory.overtime_hours == 35.0


# ------------------------------------------------------------
# Temporary labor scenario
# ------------------------------------------------------------

temporary_labor = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=15,
        forecast_confidence=0.90,
    ),
)

assert (
    temporary_labor.recommendation
    is RecommendationType.TEMPORARY_LABOR
)
assert temporary_labor.priority is RecommendationPriority.HIGH
assert temporary_labor.status is RecommendationStatus.REQUIRED
assert temporary_labor.overtime_type is OvertimeType.MANDATORY
assert temporary_labor.overtime_hours == 150.0


# ------------------------------------------------------------
# Critical shortage scenario
# ------------------------------------------------------------

critical = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=20,
        forecast_confidence=0.95,
    ),
)

assert (
    critical.recommendation
    is RecommendationType.FULL_TIME_HIRING_REVIEW
)
assert critical.priority is RecommendationPriority.CRITICAL
assert critical.status is RecommendationStatus.REVIEW_REQUIRED
assert critical.overtime_type is OvertimeType.MANDATORY
assert critical.overtime_hours == 200.0


# ------------------------------------------------------------
# Invalid request type
# ------------------------------------------------------------

try:
    engine.recommend(request="invalid")
except OvertimeValidationError:
    pass
else:
    raise AssertionError(
        "Expected OvertimeValidationError."
    )


print("✅ Overtime recommendation engine validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Recommendation Service Validation
# ============================================================

import importlib
from datetime import date

import src.overtime.service

importlib.reload(src.overtime.service)

from src.overtime.configuration import (
    OvertimeConfiguration,
)
from src.overtime.engine import (
    OvertimeRecommendationEngine,
)
from src.overtime.exceptions import (
    OvertimeValidationError,
)
from src.overtime.models import (
    OvertimeRequest,
    RecommendationType,
)
from src.overtime.service import (
    OvertimeRecommendationService,
)


configuration = OvertimeConfiguration()

engine = OvertimeRecommendationEngine(
    configuration=configuration,
)

service = OvertimeRecommendationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine


# ------------------------------------------------------------
# Valid recommendation
# ------------------------------------------------------------

recommendation = service.recommend(
    request=OvertimeRequest(
        planning_date=date.today(),
        associate_gap=2,
        forecast_confidence=0.90,
    ),
)

assert (
    recommendation.recommendation
    is RecommendationType.VOLUNTARY_OVERTIME
)


# ------------------------------------------------------------
# No shortage
# ------------------------------------------------------------

recommendation = service.recommend(
    request=OvertimeRequest(
        planning_date=date.today(),
        associate_gap=0,
        forecast_confidence=0.95,
    ),
)

assert (
    recommendation.recommendation
    is RecommendationType.NONE
)


# ------------------------------------------------------------
# Invalid request
# ------------------------------------------------------------

try:
    service.recommend(
        request="invalid",
    )
except OvertimeValidationError:
    pass
else:
    raise AssertionError(
        "Expected OvertimeValidationError."
    )


print("✅ Overtime recommendation service validation passed.")

# COMMAND ----------

# ============================================================
# Overtime Package (__init__) Validation
# ============================================================

import importlib

import src.overtime

importlib.reload(src.overtime)

from src.overtime import (
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    OVERTIME_DOMAIN_VERSION,
    OvertimeConfiguration,
    OvertimeEngineError,
    OvertimeError,
    OvertimeRecommendation,
    OvertimeRecommendationEngine,
    OvertimeRecommendationService,
    OvertimeRequest,
    OvertimeType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert OVERTIME_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_MINIMUM_OVERTIME_HOURS == 5.0
assert DEFAULT_MAXIMUM_OVERTIME_HOURS == 10.0


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    OvertimeEngineError,
    OvertimeError,
)


# ------------------------------------------------------------
# Models and enums
# ------------------------------------------------------------

assert OvertimeRequest is not None
assert OvertimeRecommendation is not None
assert OvertimeType is not None
assert RecommendationPriority is not None
assert RecommendationStatus is not None
assert RecommendationType is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert OvertimeConfiguration is not None
assert OvertimeRecommendationEngine is not None
assert OvertimeRecommendationService is not None


print("✅ Overtime package validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Constants Validation
# ============================================================

from src.staffing.constants import *

assert STAFFING_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert 0.0 <= DEFAULT_FORECAST_CONFIDENCE <= 1.0

assert MINIMUM_ASSOCIATE_GAP == 1
assert TEMPORARY_LABOR_TRIGGER_GAP > 0
assert FULL_TIME_HIRING_TRIGGER_GAP > TEMPORARY_LABOR_TRIGGER_GAP
assert CRITICAL_SHORTAGE_GAP > FULL_TIME_HIRING_TRIGGER_GAP

assert LOW_CONFIDENCE_THRESHOLD < HIGH_CONFIDENCE_THRESHOLD

assert RECOMMENDATION_NONE == "NONE"

assert len(SUPPORTED_RECOMMENDATION_TYPES) == len(
    set(SUPPORTED_RECOMMENDATION_TYPES)
)

assert len(SUPPORTED_RECOMMENDATION_PRIORITIES) == len(
    set(SUPPORTED_RECOMMENDATION_PRIORITIES)
)

assert len(SUPPORTED_RECOMMENDATION_STATUSES) == len(
    set(SUPPORTED_RECOMMENDATION_STATUSES)
)

print("✅ Staffing constants validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Exceptions Validation
# ============================================================

import importlib

import src.staffing.exceptions

importlib.reload(src.staffing.exceptions)

from src.staffing.exceptions import (
    StaffingConfigurationError,
    StaffingEngineError,
    StaffingError,
    StaffingServiceError,
    StaffingValidationError,
)

# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    StaffingValidationError,
    StaffingError,
)

assert issubclass(
    StaffingConfigurationError,
    StaffingError,
)

assert issubclass(
    StaffingEngineError,
    StaffingError,
)

assert issubclass(
    StaffingServiceError,
    StaffingError,
)

# ------------------------------------------------------------
# Exception Messages
# ------------------------------------------------------------

try:
    raise StaffingValidationError(
        "Invalid staffing request."
    )
except StaffingError as exc:
    assert str(exc) == "Invalid staffing request."

try:
    raise StaffingEngineError(
        "Staffing engine failed."
    )
except StaffingError as exc:
    assert str(exc) == "Staffing engine failed."

try:
    raise StaffingConfigurationError(
        "Invalid staffing configuration."
    )
except StaffingError as exc:
    assert str(exc) == "Invalid staffing configuration."

try:
    raise StaffingServiceError(
        "Staffing service failed."
    )
except StaffingError as exc:
    assert str(exc) == "Staffing service failed."

print("✅ Staffing exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Models Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.staffing.models

importlib.reload(src.staffing.models)

from src.staffing.exceptions import StaffingValidationError
from src.staffing.models import (
    StaffingRecommendation,
    StaffingRecommendationPriority,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
)


planning_date = date.today()


# ------------------------------------------------------------
# Valid shortage request
# ------------------------------------------------------------

shortage_request = StaffingRequest(
    planning_date=planning_date,
    associate_gap=12,
    forecast_confidence=0.92,
    recurring_shortage_days=18,
    recurring_surplus_days=0,
    overtime_dependency_days=15,
    planning_horizon_days=30,
)

assert shortage_request.has_shortage is True
assert shortage_request.has_surplus is False
assert shortage_request.associate_gap == 12

shortage_payload = shortage_request.as_dict()

assert shortage_payload["planning_date"] == planning_date.isoformat()
assert shortage_payload["recurring_shortage_days"] == 18
assert shortage_payload["planning_horizon_days"] == 30


# ------------------------------------------------------------
# Valid surplus request
# ------------------------------------------------------------

surplus_request = StaffingRequest(
    planning_date=planning_date,
    associate_gap=-6,
    forecast_confidence=0.88,
    recurring_shortage_days=0,
    recurring_surplus_days=20,
    overtime_dependency_days=0,
    planning_horizon_days=30,
)

assert surplus_request.has_shortage is False
assert surplus_request.has_surplus is True


# ------------------------------------------------------------
# Valid recommendation
# ------------------------------------------------------------

generated_at_utc = datetime.now(timezone.utc)

recommendation = StaffingRecommendation(
    planning_date=planning_date,
    recommendation=(
        StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
    ),
    priority=StaffingRecommendationPriority.HIGH,
    status=StaffingRecommendationStatus.REVIEW_REQUIRED,
    associate_gap=12,
    recommended_associates=12,
    forecast_confidence=0.92,
    rationale=(
        "Recurring workforce shortages and sustained overtime "
        "dependency require a full-time hiring review."
    ),
    generated_at_utc=generated_at_utc,
)

assert (
    recommendation.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)
assert recommendation.priority is StaffingRecommendationPriority.HIGH
assert (
    recommendation.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)
assert recommendation.recommended_associates == 12

recommendation_payload = recommendation.as_dict()

assert (
    recommendation_payload["recommendation"]
    == "FULL_TIME_HIRING_REVIEW"
)
assert recommendation_payload["priority"] == "HIGH"
assert recommendation_payload["status"] == "REVIEW_REQUIRED"
assert recommendation_payload["recommended_associates"] == 12
assert recommendation_payload["generated_at_utc"] == (
    generated_at_utc.isoformat()
)
assert recommendation_payload["recommendation_version"] == "1.0.0"


# ------------------------------------------------------------
# Invalid model validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: StaffingRequest(
        planning_date=planning_date,
        associate_gap=1.5,
        forecast_confidence=0.80,
    ),
    lambda: StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=1.1,
    ),
    lambda: StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.80,
        recurring_shortage_days=-1,
    ),
    lambda: StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.80,
        planning_horizon_days=0,
    ),
    lambda: StaffingRecommendation(
        planning_date=planning_date,
        recommendation=StaffingRecommendationType.NONE,
        priority=StaffingRecommendationPriority.LOW,
        status=StaffingRecommendationStatus.NOT_REQUIRED,
        associate_gap=0,
        recommended_associates=-1,
        forecast_confidence=0.80,
        rationale="No staffing action required.",
        generated_at_utc=generated_at_utc,
    ),
    lambda: StaffingRecommendation(
        planning_date=planning_date,
        recommendation=StaffingRecommendationType.NONE,
        priority=StaffingRecommendationPriority.LOW,
        status=StaffingRecommendationStatus.NOT_REQUIRED,
        associate_gap=0,
        recommended_associates=0,
        forecast_confidence=0.80,
        rationale="   ",
        generated_at_utc=generated_at_utc,
    ),
    lambda: StaffingRecommendation(
        planning_date=planning_date,
        recommendation=StaffingRecommendationType.NONE,
        priority=StaffingRecommendationPriority.LOW,
        status=StaffingRecommendationStatus.NOT_REQUIRED,
        associate_gap=0,
        recommended_associates=0,
        forecast_confidence=0.80,
        rationale="No staffing action required.",
        generated_at_utc=generated_at_utc,
        recommendation_version="   ",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except StaffingValidationError:
        pass
    else:
        raise AssertionError(
            "Expected StaffingValidationError."
        )


print("✅ Staffing models validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Configuration Validation
# ============================================================

import importlib

import src.staffing.configuration

importlib.reload(src.staffing.configuration)

from src.staffing.configuration import StaffingConfiguration
from src.staffing.exceptions import StaffingConfigurationError


configuration = StaffingConfiguration()

assert configuration.minimum_associate_gap == 1
assert configuration.temporary_labor_trigger_gap == 5
assert configuration.full_time_hiring_trigger_gap == 15
assert configuration.critical_shortage_gap == 25
assert configuration.minimum_recurring_shortage_days == 5
assert configuration.full_time_hiring_shortage_days == 15
assert configuration.minimum_recurring_surplus_days == 10
assert configuration.minimum_overtime_dependency_days == 10
assert configuration.default_forecast_confidence == 0.80
assert configuration.low_confidence_threshold == 0.60
assert configuration.high_confidence_threshold == 0.90
assert configuration.configuration_version == "1.0.0"


custom_configuration = StaffingConfiguration(
    minimum_associate_gap=2,
    temporary_labor_trigger_gap=6,
    full_time_hiring_trigger_gap=18,
    critical_shortage_gap=30,
    minimum_recurring_shortage_days=7,
    full_time_hiring_shortage_days=20,
    minimum_recurring_surplus_days=12,
    minimum_overtime_dependency_days=14,
    default_forecast_confidence=0.85,
    low_confidence_threshold=0.55,
    high_confidence_threshold=0.92,
    configuration_version="1.1.0",
)

assert custom_configuration.minimum_associate_gap == 2
assert custom_configuration.critical_shortage_gap == 30
assert custom_configuration.configuration_version == "1.1.0"

payload = custom_configuration.as_dict()

assert payload["temporary_labor_trigger_gap"] == 6
assert payload["full_time_hiring_shortage_days"] == 20
assert payload["configuration_version"] == "1.1.0"


invalid_cases = [
    {
        "minimum_associate_gap": 0,
    },
    {
        "minimum_associate_gap": 5,
        "temporary_labor_trigger_gap": 5,
    },
    {
        "temporary_labor_trigger_gap": 15,
        "full_time_hiring_trigger_gap": 15,
    },
    {
        "full_time_hiring_trigger_gap": 25,
        "critical_shortage_gap": 25,
    },
    {
        "minimum_recurring_shortage_days": -1,
    },
    {
        "minimum_recurring_shortage_days": 20,
        "full_time_hiring_shortage_days": 10,
    },
    {
        "default_forecast_confidence": 1.1,
    },
    {
        "low_confidence_threshold": 0.95,
        "high_confidence_threshold": 0.90,
    },
    {
        "configuration_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        StaffingConfiguration(**invalid_arguments)
    except StaffingConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected StaffingConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Staffing configuration validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Recommendation Engine Validation
# ============================================================

import importlib
from datetime import date

import src.staffing.engine

importlib.reload(src.staffing.engine)

from src.staffing.configuration import StaffingConfiguration
from src.staffing.engine import StaffingRecommendationEngine
from src.staffing.exceptions import StaffingValidationError
from src.staffing.models import (
    StaffingRecommendationPriority,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
)


planning_date = date.today()

configuration = StaffingConfiguration()

engine = StaffingRecommendationEngine(
    configuration=configuration,
)

assert engine.configuration is configuration


# ------------------------------------------------------------
# Balanced staffing
# ------------------------------------------------------------

balanced = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    ),
)

assert balanced.recommendation is StaffingRecommendationType.NONE
assert balanced.priority is StaffingRecommendationPriority.LOW
assert balanced.status is StaffingRecommendationStatus.NOT_REQUIRED
assert balanced.recommended_associates == 0


# ------------------------------------------------------------
# Low-confidence review
# ------------------------------------------------------------

low_confidence = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.50,
        recurring_shortage_days=10,
    ),
)

assert (
    low_confidence.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)
assert (
    low_confidence.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)


# ------------------------------------------------------------
# Cross-training scenario
# ------------------------------------------------------------

cross_train = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.90,
        recurring_shortage_days=2,
        overtime_dependency_days=0,
    ),
)

assert (
    cross_train.recommendation
    is StaffingRecommendationType.CROSS_TRAIN
)
assert cross_train.recommended_associates == 3


# ------------------------------------------------------------
# Temporary labor scenario
# ------------------------------------------------------------

temporary = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.90,
        recurring_shortage_days=7,
        overtime_dependency_days=2,
    ),
)

assert (
    temporary.recommendation
    is StaffingRecommendationType.TEMPORARY_LABOR
)
assert temporary.priority is StaffingRecommendationPriority.HIGH


# ------------------------------------------------------------
# Full-time hiring review
# ------------------------------------------------------------

hiring_review = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=12,
        forecast_confidence=0.92,
        recurring_shortage_days=18,
        overtime_dependency_days=15,
    ),
)

assert (
    hiring_review.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)
assert hiring_review.priority is StaffingRecommendationPriority.HIGH
assert (
    hiring_review.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)


# ------------------------------------------------------------
# Critical hiring scenario
# ------------------------------------------------------------

critical = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=25,
        forecast_confidence=0.95,
        recurring_shortage_days=20,
        overtime_dependency_days=20,
    ),
)

assert (
    critical.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING
)
assert critical.priority is StaffingRecommendationPriority.CRITICAL
assert critical.recommended_associates == 25


# ------------------------------------------------------------
# Short-term surplus
# ------------------------------------------------------------

surplus_realign = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=-5,
        forecast_confidence=0.90,
        recurring_surplus_days=3,
    ),
)

assert (
    surplus_realign.recommendation
    is StaffingRecommendationType.SHIFT_REALIGNMENT
)


# ------------------------------------------------------------
# Persistent surplus
# ------------------------------------------------------------

surplus_reduce = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=-8,
        forecast_confidence=0.90,
        recurring_surplus_days=15,
    ),
)

assert (
    surplus_reduce.recommendation
    is StaffingRecommendationType.WORKFORCE_REDUCTION
)
assert surplus_reduce.recommended_associates == 8


# ------------------------------------------------------------
# Invalid request type
# ------------------------------------------------------------

try:
    engine.recommend(request="invalid")
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Expected StaffingValidationError."
    )


print("✅ Staffing recommendation engine validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Recommendation Service Validation
# ============================================================

import importlib
from datetime import date

import src.staffing.service

importlib.reload(src.staffing.service)

from src.staffing.configuration import StaffingConfiguration
from src.staffing.engine import StaffingRecommendationEngine
from src.staffing.exceptions import StaffingValidationError
from src.staffing.models import (
    StaffingRecommendationType,
    StaffingRequest,
)
from src.staffing.service import StaffingRecommendationService


planning_date = date.today()

configuration = StaffingConfiguration()

engine = StaffingRecommendationEngine(
    configuration=configuration,
)

service = StaffingRecommendationService(
    configuration=configuration,
    engine=engine,
)


# ------------------------------------------------------------
# Dependency wiring
# ------------------------------------------------------------

assert service.configuration is configuration
assert service.engine is engine


# ------------------------------------------------------------
# Valid recommendation
# ------------------------------------------------------------

recommendation = service.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.90,
        recurring_shortage_days=7,
        overtime_dependency_days=2,
    ),
)

assert (
    recommendation.recommendation
    is StaffingRecommendationType.TEMPORARY_LABOR
)


# ------------------------------------------------------------
# Balanced staffing
# ------------------------------------------------------------

balanced_recommendation = service.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    ),
)

assert (
    balanced_recommendation.recommendation
    is StaffingRecommendationType.NONE
)


# ------------------------------------------------------------
# Default construction
# ------------------------------------------------------------

default_service = StaffingRecommendationService()

assert isinstance(
    default_service.configuration,
    StaffingConfiguration,
)
assert isinstance(
    default_service.engine,
    StaffingRecommendationEngine,
)


# ------------------------------------------------------------
# Invalid dependency wiring
# ------------------------------------------------------------

different_configuration = StaffingConfiguration(
    temporary_labor_trigger_gap=6,
    full_time_hiring_trigger_gap=18,
    critical_shortage_gap=30,
)

try:
    StaffingRecommendationService(
        configuration=different_configuration,
        engine=engine,
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Expected StaffingValidationError for inconsistent "
        "configuration and engine dependencies."
    )


# ------------------------------------------------------------
# Invalid request
# ------------------------------------------------------------

try:
    service.recommend(
        request="invalid",
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Expected StaffingValidationError."
    )


print("✅ Staffing recommendation service validation passed.")

# COMMAND ----------

# ============================================================
# Staffing Package (__init__) Validation
# ============================================================

import importlib

import src.staffing

importlib.reload(src.staffing)

from src.staffing import (
    CRITICAL_SHORTAGE_GAP,
    DEFAULT_FORECAST_CONFIDENCE,
    FULL_TIME_HIRING_TRIGGER_GAP,
    MINIMUM_ASSOCIATE_GAP,
    STAFFING_DOMAIN_VERSION,
    TEMPORARY_LABOR_TRIGGER_GAP,
    StaffingConfiguration,
    StaffingEngineError,
    StaffingError,
    StaffingRecommendation,
    StaffingRecommendationEngine,
    StaffingRecommendationPriority,
    StaffingRecommendationService,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert STAFFING_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_FORECAST_CONFIDENCE == 0.80
assert MINIMUM_ASSOCIATE_GAP == 1
assert TEMPORARY_LABOR_TRIGGER_GAP == 5
assert FULL_TIME_HIRING_TRIGGER_GAP == 15
assert CRITICAL_SHORTAGE_GAP == 25


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    StaffingEngineError,
    StaffingError,
)


# ------------------------------------------------------------
# Models and enums
# ------------------------------------------------------------

assert StaffingRequest is not None
assert StaffingRecommendation is not None
assert StaffingRecommendationType is not None
assert StaffingRecommendationPriority is not None
assert StaffingRecommendationStatus is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert StaffingConfiguration is not None
assert StaffingRecommendationEngine is not None
assert StaffingRecommendationService is not None


print("✅ Staffing package validation passed.")

# COMMAND ----------

# ============================================================
# Optimization Constants Validation
# ============================================================

import importlib

import src.optimization.constants

importlib.reload(src.optimization.constants)

from src.optimization.constants import *

assert OPTIMIZATION_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert 0.0 <= DEFAULT_FORECAST_CONFIDENCE <= 1.0

assert len(SUPPORTED_OPTIMIZATION_PRIORITIES) == len(
    set(SUPPORTED_OPTIMIZATION_PRIORITIES)
)

assert len(SUPPORTED_OPTIMIZATION_STATUSES) == len(
    set(SUPPORTED_OPTIMIZATION_STATUSES)
)

assert len(SUPPORTED_WORKFORCE_ACTIONS) == len(
    set(SUPPORTED_WORKFORCE_ACTIONS)
)

assert ACTION_NONE == "NONE"

print("✅ Optimization constants validation passed.")

# COMMAND ----------

# ============================================================
# Optimization Exceptions Validation
# ============================================================

import importlib

import src.optimization.exceptions

importlib.reload(src.optimization.exceptions)

from src.optimization.exceptions import (
    OptimizationConfigurationError,
    OptimizationConflictError,
    OptimizationEngineError,
    OptimizationError,
    OptimizationServiceError,
    OptimizationValidationError,
)


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    OptimizationValidationError,
    OptimizationError,
)

assert issubclass(
    OptimizationConfigurationError,
    OptimizationError,
)

assert issubclass(
    OptimizationConflictError,
    OptimizationError,
)

assert issubclass(
    OptimizationEngineError,
    OptimizationError,
)

assert issubclass(
    OptimizationServiceError,
    OptimizationError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise OptimizationValidationError(
        "Invalid optimization request."
    )
except OptimizationError as exc:
    assert str(exc) == "Invalid optimization request."


try:
    raise OptimizationConflictError(
        "Recommendation conflict detected."
    )
except OptimizationError as exc:
    assert str(exc) == "Recommendation conflict detected."


try:
    raise OptimizationEngineError(
        "Optimization engine failed."
    )
except OptimizationError as exc:
    assert str(exc) == "Optimization engine failed."


print("✅ Optimization exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Optimization Models Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.optimization.models

importlib.reload(src.optimization.models)

from src.optimization.exceptions import OptimizationValidationError
from src.optimization.models import (
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationDecision,
    WorkforceOptimizationRequest,
)


planning_date = date.today()


# ------------------------------------------------------------
# Valid optimization request
# ------------------------------------------------------------

request = WorkforceOptimizationRequest(
    planning_date=planning_date,
    associate_gap=8,
    forecast_confidence=0.92,
    overtime_recommended=True,
    temporary_labor_recommended=True,
    full_time_hiring_recommended=False,
    shift_realignment_recommended=False,
    cross_training_recommended=False,
    overtime_hours=40.0,
    recommended_associates=8,
)

assert request.associate_gap == 8
assert request.has_conflicting_actions is True

request_payload = request.as_dict()

assert request_payload["planning_date"] == planning_date.isoformat()
assert request_payload["overtime_recommended"] is True
assert request_payload["temporary_labor_recommended"] is True
assert request_payload["recommended_associates"] == 8


# ------------------------------------------------------------
# Valid optimization decision
# ------------------------------------------------------------

generated_at_utc = datetime.now(timezone.utc)

decision = WorkforceOptimizationDecision(
    planning_date=planning_date,
    action=WorkforceAction.TEMPORARY_LABOR,
    priority=OptimizationPriority.HIGH,
    status=OptimizationStatus.REVIEW,
    associate_gap=8,
    recommended_associates=8,
    overtime_hours=40.0,
    forecast_confidence=0.92,
    conflicting_actions_resolved=True,
    rationale=(
        "Temporary labor is the primary action while limited overtime "
        "is retained as an interim control."
    ),
    generated_at_utc=generated_at_utc,
)

assert decision.action is WorkforceAction.TEMPORARY_LABOR
assert decision.priority is OptimizationPriority.HIGH
assert decision.status is OptimizationStatus.REVIEW
assert decision.conflicting_actions_resolved is True

decision_payload = decision.as_dict()

assert decision_payload["action"] == "TEMPORARY_LABOR"
assert decision_payload["priority"] == "HIGH"
assert decision_payload["status"] == "REVIEW"
assert decision_payload["recommended_associates"] == 8
assert decision_payload["generated_at_utc"] == (
    generated_at_utc.isoformat()
)
assert decision_payload["decision_version"] == "1.0.0"


# ------------------------------------------------------------
# Balanced optimization decision
# ------------------------------------------------------------

balanced_decision = WorkforceOptimizationDecision(
    planning_date=planning_date,
    action=WorkforceAction.NONE,
    priority=OptimizationPriority.LOW,
    status=OptimizationStatus.OPTIMAL,
    associate_gap=0,
    recommended_associates=0,
    overtime_hours=0.0,
    forecast_confidence=0.95,
    conflicting_actions_resolved=False,
    rationale="No workforce action is required.",
    generated_at_utc=generated_at_utc,
)

assert balanced_decision.action is WorkforceAction.NONE


# ------------------------------------------------------------
# Invalid model validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=1.1,
    ),
    lambda: WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.80,
        overtime_recommended=True,
    ),
    lambda: WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.80,
        overtime_recommended=False,
        overtime_hours=10.0,
    ),
    lambda: WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.80,
        recommended_associates=-1,
    ),
    lambda: WorkforceOptimizationDecision(
        planning_date=planning_date,
        action=WorkforceAction.NONE,
        priority=OptimizationPriority.LOW,
        status=OptimizationStatus.OPTIMAL,
        associate_gap=0,
        recommended_associates=1,
        overtime_hours=0.0,
        forecast_confidence=0.80,
        conflicting_actions_resolved=False,
        rationale="Invalid no-action decision.",
        generated_at_utc=generated_at_utc,
    ),
    lambda: WorkforceOptimizationDecision(
        planning_date=planning_date,
        action=WorkforceAction.NONE,
        priority=OptimizationPriority.LOW,
        status=OptimizationStatus.OPTIMAL,
        associate_gap=0,
        recommended_associates=0,
        overtime_hours=0.0,
        forecast_confidence=0.80,
        conflicting_actions_resolved=False,
        rationale="   ",
        generated_at_utc=generated_at_utc,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except OptimizationValidationError:
        pass
    else:
        raise AssertionError(
            "Expected OptimizationValidationError."
        )


print("✅ Optimization models validation passed.")

# COMMAND ----------

# ============================================================
# Optimization Configuration Validation
# ============================================================

import importlib

import src.optimization.configuration

importlib.reload(src.optimization.configuration)

from src.optimization.configuration import (
    WorkforceOptimizationConfiguration,
)
from src.optimization.exceptions import (
    OptimizationConfigurationError,
)


configuration = WorkforceOptimizationConfiguration()

assert configuration.low_confidence_threshold == 0.60
assert configuration.high_confidence_threshold == 0.90
assert configuration.default_forecast_confidence == 0.80

assert configuration.overtime_priority_weight == 1
assert configuration.cross_training_priority_weight == 2
assert configuration.shift_realignment_priority_weight == 3
assert configuration.temporary_labor_priority_weight == 4
assert configuration.full_time_hiring_priority_weight == 5

assert configuration.critical_associate_gap == 20
assert configuration.configuration_version == "1.0.0"


custom_configuration = WorkforceOptimizationConfiguration(
    low_confidence_threshold=0.55,
    high_confidence_threshold=0.92,
    default_forecast_confidence=0.85,
    overtime_priority_weight=10,
    cross_training_priority_weight=20,
    shift_realignment_priority_weight=30,
    temporary_labor_priority_weight=40,
    full_time_hiring_priority_weight=50,
    critical_associate_gap=25,
    configuration_version="1.1.0",
)

assert custom_configuration.critical_associate_gap == 25
assert custom_configuration.configuration_version == "1.1.0"

payload = custom_configuration.as_dict()

assert payload["overtime_priority_weight"] == 10
assert payload["full_time_hiring_priority_weight"] == 50
assert payload["configuration_version"] == "1.1.0"


invalid_cases = [
    {
        "low_confidence_threshold": -0.1,
    },
    {
        "high_confidence_threshold": 1.1,
    },
    {
        "low_confidence_threshold": 0.95,
        "high_confidence_threshold": 0.90,
    },
    {
        "overtime_priority_weight": 0,
    },
    {
        "overtime_priority_weight": 1,
        "cross_training_priority_weight": 1,
    },
    {
        "overtime_priority_weight": 5,
        "cross_training_priority_weight": 4,
        "shift_realignment_priority_weight": 3,
        "temporary_labor_priority_weight": 2,
        "full_time_hiring_priority_weight": 1,
    },
    {
        "critical_associate_gap": 0,
    },
    {
        "configuration_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        WorkforceOptimizationConfiguration(
            **invalid_arguments
        )
    except OptimizationConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected OptimizationConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Optimization configuration validation passed.")

# COMMAND ----------

# ============================================================
# Workforce Optimization Engine Validation
# ============================================================

import importlib
from datetime import date

import src.optimization.engine

importlib.reload(src.optimization.engine)

from src.optimization.configuration import (
    WorkforceOptimizationConfiguration,
)
from src.optimization.engine import WorkforceOptimizationEngine
from src.optimization.exceptions import (
    OptimizationEngineError,
    OptimizationValidationError,
)
from src.optimization.models import (
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationRequest,
)


planning_date = date.today()

configuration = WorkforceOptimizationConfiguration()

engine = WorkforceOptimizationEngine(
    configuration=configuration,
)

assert engine.configuration is configuration


# ------------------------------------------------------------
# Balanced workforce
# ------------------------------------------------------------

balanced = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    ),
)

assert balanced.action is WorkforceAction.NONE
assert balanced.priority is OptimizationPriority.LOW
assert balanced.status is OptimizationStatus.OPTIMAL
assert balanced.recommended_associates == 0
assert balanced.overtime_hours == 0.0
assert balanced.conflicting_actions_resolved is False


# ------------------------------------------------------------
# Workforce surplus
# ------------------------------------------------------------

surplus = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=-5,
        forecast_confidence=0.90,
        shift_realignment_recommended=True,
    ),
)

assert surplus.action is WorkforceAction.NONE
assert surplus.priority is OptimizationPriority.LOW
assert surplus.status is OptimizationStatus.OPTIMAL
assert surplus.recommended_associates == 0


# ------------------------------------------------------------
# Low-confidence decision
# ------------------------------------------------------------

low_confidence = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=6,
        forecast_confidence=0.50,
        overtime_recommended=True,
        overtime_hours=30.0,
        recommended_associates=6,
    ),
)

assert low_confidence.action is WorkforceAction.NONE
assert low_confidence.priority is OptimizationPriority.MEDIUM
assert low_confidence.status is OptimizationStatus.REVIEW
assert low_confidence.recommended_associates == 0
assert low_confidence.overtime_hours == 0.0
assert low_confidence.conflicting_actions_resolved is False


# ------------------------------------------------------------
# Overtime-only decision
# ------------------------------------------------------------

overtime = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.90,
        overtime_recommended=True,
        overtime_hours=15.0,
        recommended_associates=3,
    ),
)

assert overtime.action is WorkforceAction.OVERTIME
assert overtime.priority is OptimizationPriority.HIGH
assert overtime.status is OptimizationStatus.ACCEPTABLE
assert overtime.associate_gap == 3
assert overtime.recommended_associates == 3
assert overtime.overtime_hours == 15.0
assert overtime.conflicting_actions_resolved is False


# ------------------------------------------------------------
# Cross-training decision
# ------------------------------------------------------------

cross_training = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.90,
        cross_training_recommended=True,
        recommended_associates=3,
    ),
)

assert cross_training.action is WorkforceAction.CROSS_TRAINING
assert cross_training.priority is OptimizationPriority.HIGH
assert cross_training.status is OptimizationStatus.ACCEPTABLE


# ------------------------------------------------------------
# Shift-realignment decision
# ------------------------------------------------------------

shift_realignment = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=4,
        forecast_confidence=0.90,
        shift_realignment_recommended=True,
        recommended_associates=4,
    ),
)

assert (
    shift_realignment.action
    is WorkforceAction.SHIFT_REALIGNMENT
)
assert shift_realignment.priority is OptimizationPriority.HIGH
assert shift_realignment.status is OptimizationStatus.ACCEPTABLE


# ------------------------------------------------------------
# Temporary labor resolves overtime conflict
# ------------------------------------------------------------

temporary_labor = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.92,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        overtime_hours=40.0,
        recommended_associates=8,
    ),
)

assert (
    temporary_labor.action
    is WorkforceAction.TEMPORARY_LABOR
)
assert temporary_labor.priority is OptimizationPriority.HIGH
assert temporary_labor.status is OptimizationStatus.ACCEPTABLE
assert temporary_labor.recommended_associates == 8
assert temporary_labor.overtime_hours == 40.0
assert temporary_labor.conflicting_actions_resolved is True


# ------------------------------------------------------------
# Full-time hiring resolves multiple conflicts
# ------------------------------------------------------------

full_time_hiring = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=15,
        forecast_confidence=0.94,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        full_time_hiring_recommended=True,
        shift_realignment_recommended=True,
        cross_training_recommended=True,
        overtime_hours=75.0,
        recommended_associates=15,
    ),
)

assert (
    full_time_hiring.action
    is WorkforceAction.FULL_TIME_HIRING
)
assert full_time_hiring.priority is OptimizationPriority.HIGH
assert full_time_hiring.status is OptimizationStatus.ACCEPTABLE
assert full_time_hiring.recommended_associates == 15
assert full_time_hiring.overtime_hours == 75.0
assert full_time_hiring.conflicting_actions_resolved is True


# ------------------------------------------------------------
# Critical shortage
# ------------------------------------------------------------

critical = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=20,
        forecast_confidence=0.95,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        full_time_hiring_recommended=True,
        overtime_hours=100.0,
        recommended_associates=20,
    ),
)

assert critical.action is WorkforceAction.FULL_TIME_HIRING
assert critical.priority is OptimizationPriority.CRITICAL
assert critical.status is OptimizationStatus.CRITICAL
assert critical.associate_gap == 20
assert critical.recommended_associates == 20
assert critical.conflicting_actions_resolved is True


# ------------------------------------------------------------
# Positive gap without a recommendation
# ------------------------------------------------------------

missing_action = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.90,
        recommended_associates=5,
    ),
)

assert missing_action.action is WorkforceAction.NONE
assert missing_action.priority is OptimizationPriority.MEDIUM
assert missing_action.status is OptimizationStatus.REVIEW
assert missing_action.recommended_associates == 0
assert missing_action.overtime_hours == 0.0


# ------------------------------------------------------------
# Invalid request type
# ------------------------------------------------------------

try:
    engine.optimize(
        request="invalid",
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OptimizationValidationError."
    )


# ------------------------------------------------------------
# Invalid configuration type
# ------------------------------------------------------------

try:
    WorkforceOptimizationEngine(
        configuration="invalid",
    )
except OptimizationEngineError:
    pass
else:
    raise AssertionError(
        "Expected OptimizationEngineError."
    )


print("✅ Workforce optimization engine validation passed.")

# COMMAND ----------

# ============================================================
# Workforce Optimization Service Validation
# ============================================================

import importlib
from datetime import date

import src.optimization.service

importlib.reload(src.optimization.service)

from src.optimization.configuration import (
    WorkforceOptimizationConfiguration,
)
from src.optimization.engine import (
    WorkforceOptimizationEngine,
)
from src.optimization.exceptions import (
    OptimizationServiceError,
    OptimizationValidationError,
)
from src.optimization.models import (
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationRequest,
)
from src.optimization.service import (
    WorkforceOptimizationService,
)


planning_date = date.today()

configuration = WorkforceOptimizationConfiguration()

engine = WorkforceOptimizationEngine(
    configuration=configuration,
)

service = WorkforceOptimizationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine


# ------------------------------------------------------------
# Balanced workload
# ------------------------------------------------------------

balanced = service.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    ),
)

assert balanced.action is WorkforceAction.NONE
assert balanced.priority is OptimizationPriority.LOW
assert balanced.status is OptimizationStatus.OPTIMAL


# ------------------------------------------------------------
# Temporary labor recommendation
# ------------------------------------------------------------

recommendation = service.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.90,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        overtime_hours=40.0,
        recommended_associates=8,
    ),
)

assert recommendation.action is WorkforceAction.TEMPORARY_LABOR
assert recommendation.priority is OptimizationPriority.HIGH
assert recommendation.status is OptimizationStatus.ACCEPTABLE
assert recommendation.conflicting_actions_resolved is True


# ------------------------------------------------------------
# Critical hiring recommendation
# ------------------------------------------------------------

critical = service.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=25,
        forecast_confidence=0.95,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        full_time_hiring_recommended=True,
        overtime_hours=100.0,
        recommended_associates=25,
    ),
)

assert critical.action is WorkforceAction.FULL_TIME_HIRING
assert critical.priority is OptimizationPriority.CRITICAL
assert critical.status is OptimizationStatus.CRITICAL


# ------------------------------------------------------------
# Invalid dependencies
# ------------------------------------------------------------

different_configuration = (
    WorkforceOptimizationConfiguration()
)

try:
    WorkforceOptimizationService(
        configuration=different_configuration,
        engine=engine,
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OptimizationValidationError for inconsistent "
        "configuration and engine."
    )


# ------------------------------------------------------------
# Invalid request
# ------------------------------------------------------------

try:
    service.optimize(
        request="invalid",
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OptimizationValidationError."
    )


# ------------------------------------------------------------
# Invalid engine
# ------------------------------------------------------------

try:
    WorkforceOptimizationService(
        configuration=configuration,
        engine="invalid",
    )
except OptimizationServiceError:
    pass
else:
    raise AssertionError(
        "Expected OptimizationServiceError."
    )


print("✅ Workforce optimization service validation passed.")

# COMMAND ----------

# ============================================================
# Optimization Package (__init__) Validation
# ============================================================

import importlib

import src.optimization

importlib.reload(src.optimization)

from src.optimization import (
    ACTION_FULL_TIME_HIRING,
    ACTION_NONE,
    ACTION_OVERTIME,
    ACTION_TEMPORARY_LABOR,
    DEFAULT_FORECAST_CONFIDENCE,
    OPTIMIZATION_DOMAIN_VERSION,
    OptimizationEngineError,
    OptimizationError,
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationConfiguration,
    WorkforceOptimizationDecision,
    WorkforceOptimizationEngine,
    WorkforceOptimizationRequest,
    WorkforceOptimizationService,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert OPTIMIZATION_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_FORECAST_CONFIDENCE == 0.80
assert ACTION_NONE == "NONE"
assert ACTION_OVERTIME == "OVERTIME"
assert ACTION_TEMPORARY_LABOR == "TEMPORARY_LABOR"
assert ACTION_FULL_TIME_HIRING == "FULL_TIME_HIRING"


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    OptimizationEngineError,
    OptimizationError,
)


# ------------------------------------------------------------
# Models and enums
# ------------------------------------------------------------

assert OptimizationPriority is not None
assert OptimizationStatus is not None
assert WorkforceAction is not None
assert WorkforceOptimizationRequest is not None
assert WorkforceOptimizationDecision is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert WorkforceOptimizationConfiguration is not None
assert WorkforceOptimizationEngine is not None
assert WorkforceOptimizationService is not None


print("✅ Optimization package validation passed.")

# COMMAND ----------

# ============================================================
# Orchestration Constants Validation
# ============================================================

import importlib

import src.orchestration.constants

importlib.reload(src.orchestration.constants)

from src.orchestration.constants import *

assert ORCHESTRATION_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert 0.0 <= DEFAULT_FORECAST_CONFIDENCE <= 1.0

# ------------------------------------------------------------
# Stages
# ------------------------------------------------------------

assert ORCHESTRATION_STAGES == (
    STAGE_FORECAST,
    STAGE_PLANNING,
    STAGE_OVERTIME,
    STAGE_STAFFING,
    STAGE_OPTIMIZATION,
    STAGE_COMPLETE,
)

assert EXECUTION_ORDER == (
    STAGE_FORECAST,
    STAGE_PLANNING,
    STAGE_OVERTIME,
    STAGE_STAFFING,
    STAGE_OPTIMIZATION,
)

# ------------------------------------------------------------
# Statuses
# ------------------------------------------------------------

assert STATUS_PENDING == "PENDING"
assert STATUS_RUNNING == "RUNNING"
assert STATUS_COMPLETED == "COMPLETED"
assert STATUS_FAILED == "FAILED"

assert len(SUPPORTED_ORCHESTRATION_STATUSES) == len(
    set(SUPPORTED_ORCHESTRATION_STATUSES)
)

# ------------------------------------------------------------
# Workflow Names
# ------------------------------------------------------------

assert WORKFLOW_ENTERPRISE_DECISION != ""
assert WORKFLOW_CAPACITY_PLANNING != ""

print("✅ Orchestration constants validation passed.")

# COMMAND ----------

# ============================================================
# Orchestration Exceptions Validation
# ============================================================

import importlib

import src.orchestration.exceptions

importlib.reload(src.orchestration.exceptions)

from src.orchestration.exceptions import (
    OrchestrationConfigurationError,
    OrchestrationDependencyError,
    OrchestrationEngineError,
    OrchestrationError,
    OrchestrationServiceError,
    OrchestrationStageError,
    OrchestrationValidationError,
)


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    OrchestrationValidationError,
    OrchestrationError,
)

assert issubclass(
    OrchestrationConfigurationError,
    OrchestrationError,
)

assert issubclass(
    OrchestrationDependencyError,
    OrchestrationError,
)

assert issubclass(
    OrchestrationStageError,
    OrchestrationError,
)

assert issubclass(
    OrchestrationEngineError,
    OrchestrationError,
)

assert issubclass(
    OrchestrationServiceError,
    OrchestrationError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise OrchestrationValidationError(
        "Invalid orchestration request."
    )
except OrchestrationError as exc:
    assert str(exc) == "Invalid orchestration request."


try:
    raise OrchestrationDependencyError(
        "Planning service is unavailable."
    )
except OrchestrationError as exc:
    assert str(exc) == "Planning service is unavailable."


try:
    raise OrchestrationStageError(
        "Optimization stage failed."
    )
except OrchestrationError as exc:
    assert str(exc) == "Optimization stage failed."


try:
    raise OrchestrationEngineError(
        "Orchestration engine failed."
    )
except OrchestrationError as exc:
    assert str(exc) == "Orchestration engine failed."


print("✅ Orchestration exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Orchestration Models Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.orchestration.models

importlib.reload(src.orchestration.models)

from src.orchestration.exceptions import (
    OrchestrationValidationError,
)
from src.orchestration.models import (
    EnterpriseDecisionRequest,
    EnterpriseDecisionResult,
    OrchestrationStage,
    OrchestrationStatus,
)


planning_date = date.today()


# ------------------------------------------------------------
# Valid request
# ------------------------------------------------------------

request = EnterpriseDecisionRequest(
    planning_date=planning_date,
    expected_order_lines=48_000.0,
    available_associates=40,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    forecast_confidence=0.92,
    recurring_shortage_days=18,
    recurring_surplus_days=0,
    overtime_dependency_days=15,
    planning_horizon_days=30,
)

assert request.expected_order_lines == 48_000.0
assert request.available_associates == 40
assert request.forecast_confidence == 0.92

request_payload = request.as_dict()

assert request_payload["planning_date"] == planning_date.isoformat()
assert request_payload["available_associates"] == 40
assert request_payload["planning_horizon_days"] == 30


# ------------------------------------------------------------
# Valid completed result
# ------------------------------------------------------------

generated_at_utc = datetime.now(timezone.utc)

result = EnterpriseDecisionResult(
    planning_date=planning_date,
    workflow_status=OrchestrationStatus.COMPLETED,
    completed_stage=OrchestrationStage.COMPLETE,
    expected_order_lines=48_000.0,
    available_associates=40,
    required_associates=47,
    associate_gap=7,
    overtime_recommendation="MANDATORY_OVERTIME",
    staffing_recommendation="FULL_TIME_HIRING_REVIEW",
    optimization_action="FULL_TIME_HIRING",
    optimization_priority="HIGH",
    optimization_status="ACCEPTABLE",
    overtime_hours=35.0,
    recommended_associates=7,
    forecast_confidence=0.92,
    rationale=(
        "Full-time hiring review selected as the primary enterprise "
        "workforce action."
    ),
    generated_at_utc=generated_at_utc,
)

assert result.workflow_status is OrchestrationStatus.COMPLETED
assert result.completed_stage is OrchestrationStage.COMPLETE
assert result.associate_gap == 7
assert result.optimization_action == "FULL_TIME_HIRING"

result_payload = result.as_dict()

assert result_payload["workflow_status"] == "COMPLETED"
assert result_payload["completed_stage"] == "complete"
assert result_payload["associate_gap"] == 7
assert result_payload["generated_at_utc"] == (
    generated_at_utc.isoformat()
)
assert result_payload["workflow_version"] == "1.0.0"


# ------------------------------------------------------------
# Invalid model validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        available_associates=40,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.90,
    ),
    lambda: EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=100.0,
        available_associates=-1,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.90,
    ),
    lambda: EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=100.0,
        available_associates=10,
        productivity_lines_per_hour=0.0,
        scheduled_hours=10.0,
        forecast_confidence=0.90,
    ),
    lambda: EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=100.0,
        available_associates=10,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=1.1,
    ),
    lambda: EnterpriseDecisionResult(
        planning_date=planning_date,
        workflow_status=OrchestrationStatus.COMPLETED,
        completed_stage=OrchestrationStage.OPTIMIZATION,
        expected_order_lines=48_000.0,
        available_associates=40,
        required_associates=47,
        associate_gap=7,
        overtime_recommendation="MANDATORY_OVERTIME",
        staffing_recommendation="FULL_TIME_HIRING_REVIEW",
        optimization_action="FULL_TIME_HIRING",
        optimization_priority="HIGH",
        optimization_status="ACCEPTABLE",
        overtime_hours=35.0,
        recommended_associates=7,
        forecast_confidence=0.92,
        rationale="Invalid completed workflow.",
        generated_at_utc=generated_at_utc,
    ),
    lambda: EnterpriseDecisionResult(
        planning_date=planning_date,
        workflow_status=OrchestrationStatus.COMPLETED,
        completed_stage=OrchestrationStage.COMPLETE,
        expected_order_lines=48_000.0,
        available_associates=40,
        required_associates=47,
        associate_gap=6,
        overtime_recommendation="MANDATORY_OVERTIME",
        staffing_recommendation="FULL_TIME_HIRING_REVIEW",
        optimization_action="FULL_TIME_HIRING",
        optimization_priority="HIGH",
        optimization_status="ACCEPTABLE",
        overtime_hours=35.0,
        recommended_associates=7,
        forecast_confidence=0.92,
        rationale="Invalid workforce gap.",
        generated_at_utc=generated_at_utc,
    ),
    lambda: EnterpriseDecisionResult(
        planning_date=planning_date,
        workflow_status=OrchestrationStatus.COMPLETED,
        completed_stage=OrchestrationStage.COMPLETE,
        expected_order_lines=48_000.0,
        available_associates=40,
        required_associates=47,
        associate_gap=7,
        overtime_recommendation="MANDATORY_OVERTIME",
        staffing_recommendation="FULL_TIME_HIRING_REVIEW",
        optimization_action="FULL_TIME_HIRING",
        optimization_priority="HIGH",
        optimization_status="ACCEPTABLE",
        overtime_hours=35.0,
        recommended_associates=7,
        forecast_confidence=0.92,
        rationale="   ",
        generated_at_utc=generated_at_utc,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except OrchestrationValidationError:
        pass
    else:
        raise AssertionError(
            "Expected OrchestrationValidationError."
        )


print("✅ Orchestration models validation passed.")

# COMMAND ----------

# ============================================================
# Orchestration Configuration Validation
# ============================================================

import importlib

import src.orchestration.configuration

importlib.reload(src.orchestration.configuration)

from src.orchestration.configuration import (
    EnterpriseOrchestrationConfiguration,
)
from src.orchestration.constants import (
    EXECUTION_ORDER,
)
from src.orchestration.exceptions import (
    OrchestrationConfigurationError,
)


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = EnterpriseOrchestrationConfiguration()

assert configuration.default_forecast_confidence == 0.80
assert configuration.enable_overtime_stage is True
assert configuration.enable_staffing_stage is True
assert configuration.enable_optimization_stage is True
assert configuration.fail_fast is True
assert configuration.execution_order == EXECUTION_ORDER
assert configuration.configuration_version == "1.0.0"


# ------------------------------------------------------------
# Valid custom configuration
# ------------------------------------------------------------

custom_configuration = EnterpriseOrchestrationConfiguration(
    default_forecast_confidence=0.90,
    enable_overtime_stage=True,
    enable_staffing_stage=True,
    enable_optimization_stage=False,
    fail_fast=False,
    execution_order=EXECUTION_ORDER,
    configuration_version="1.1.0",
)

assert custom_configuration.default_forecast_confidence == 0.90
assert custom_configuration.enable_optimization_stage is False
assert custom_configuration.fail_fast is False
assert custom_configuration.configuration_version == "1.1.0"


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

payload = custom_configuration.as_dict()

assert payload["default_forecast_confidence"] == 0.90
assert payload["enable_optimization_stage"] is False
assert payload["fail_fast"] is False
assert payload["execution_order"] == list(EXECUTION_ORDER)
assert payload["configuration_version"] == "1.1.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "default_forecast_confidence": -0.1,
    },
    {
        "default_forecast_confidence": 1.1,
    },
    {
        "enable_overtime_stage": "yes",
    },
    {
        "enable_staffing_stage": 1,
    },
    {
        "enable_optimization_stage": None,
    },
    {
        "fail_fast": "true",
    },
    {
        "execution_order": [],
    },
    {
        "execution_order": (
            "forecast",
            "planning",
            "overtime",
            "staffing",
            "staffing",
        ),
    },
    {
        "execution_order": (
            "planning",
            "forecast",
            "overtime",
            "staffing",
            "optimization",
        ),
    },
    {
        "configuration_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        EnterpriseOrchestrationConfiguration(
            **invalid_arguments
        )
    except OrchestrationConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected OrchestrationConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Orchestration configuration validation passed.")

# COMMAND ----------

# ============================================================
# Enterprise Decision Orchestration Engine Validation
# ============================================================

import importlib
from datetime import date

import src.orchestration.engine

importlib.reload(src.orchestration.engine)

from src.orchestration.configuration import (
    EnterpriseOrchestrationConfiguration,
)
from src.orchestration.engine import (
    EnterpriseDecisionOrchestrationEngine,
)
from src.orchestration.exceptions import (
    OrchestrationDependencyError,
    OrchestrationValidationError,
)
from src.orchestration.models import (
    EnterpriseDecisionRequest,
    OrchestrationStage,
    OrchestrationStatus,
)


planning_date = date.today()

configuration = EnterpriseOrchestrationConfiguration()

engine = EnterpriseDecisionOrchestrationEngine(
    configuration=configuration,
)

assert engine.configuration is configuration
assert engine.planning_service is not None
assert engine.overtime_service is not None
assert engine.staffing_service is not None
assert engine.optimization_service is not None


# ------------------------------------------------------------
# Balanced workforce workflow
# ------------------------------------------------------------

balanced_result = engine.execute(
    request=EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=10_000.0,
        available_associates=20,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.95,
        recurring_shortage_days=0,
        recurring_surplus_days=0,
        overtime_dependency_days=0,
        planning_horizon_days=30,
    )
)

assert (
    balanced_result.workflow_status
    is OrchestrationStatus.COMPLETED
)
assert (
    balanced_result.completed_stage
    is OrchestrationStage.COMPLETE
)
assert balanced_result.associate_gap <= 0
assert balanced_result.optimization_action == "NONE"
assert balanced_result.optimization_status == "OPTIMAL"


# ------------------------------------------------------------
# Workforce shortage workflow
# ------------------------------------------------------------

shortage_result = engine.execute(
    request=EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=48_000.0,
        available_associates=40,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.92,
        recurring_shortage_days=18,
        recurring_surplus_days=0,
        overtime_dependency_days=15,
        planning_horizon_days=30,
    )
)

assert (
    shortage_result.workflow_status
    is OrchestrationStatus.COMPLETED
)
assert (
    shortage_result.completed_stage
    is OrchestrationStage.COMPLETE
)

assert shortage_result.available_associates == 40
assert shortage_result.required_associates == 47
assert shortage_result.associate_gap == 7

assert (
    shortage_result.overtime_recommendation
    == "MANDATORY_OVERTIME"
)

assert (
    shortage_result.staffing_recommendation
    == "FULL_TIME_HIRING_REVIEW"
)

assert (
    shortage_result.optimization_action
    == "FULL_TIME_HIRING"
)

assert shortage_result.optimization_priority == "HIGH"
assert shortage_result.optimization_status == "ACCEPTABLE"
assert shortage_result.recommended_associates == 7
assert shortage_result.forecast_confidence == 0.92


# ------------------------------------------------------------
# Serializable result
# ------------------------------------------------------------

shortage_payload = shortage_result.as_dict()

assert shortage_payload["workflow_status"] == "COMPLETED"
assert shortage_payload["completed_stage"] == "complete"
assert shortage_payload["available_associates"] == 40
assert shortage_payload["required_associates"] == 47
assert shortage_payload["associate_gap"] == 7
assert shortage_payload["optimization_action"] == (
    "FULL_TIME_HIRING"
)
assert shortage_payload["workflow_version"] == "1.0.0"


# ------------------------------------------------------------
# Optimization-disabled workflow
# ------------------------------------------------------------

no_optimization_engine = (
    EnterpriseDecisionOrchestrationEngine(
        configuration=(
            EnterpriseOrchestrationConfiguration(
                enable_optimization_stage=False,
            )
        )
    )
)

no_optimization_result = no_optimization_engine.execute(
    request=EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=48_000.0,
        available_associates=40,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.92,
        recurring_shortage_days=18,
        overtime_dependency_days=15,
    )
)

assert (
    no_optimization_result.optimization_action
    == "NOT_EXECUTED"
)
assert (
    no_optimization_result.optimization_priority
    == "NOT_EXECUTED"
)
assert (
    no_optimization_result.optimization_status
    == "NOT_EXECUTED"
)


# ------------------------------------------------------------
# Invalid request type
# ------------------------------------------------------------

try:
    engine.execute(
        request="invalid",
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OrchestrationValidationError."
    )


# ------------------------------------------------------------
# Invalid dependency
# ------------------------------------------------------------

try:
    EnterpriseDecisionOrchestrationEngine(
        configuration=configuration,
        planning_service="invalid",
    )
except OrchestrationDependencyError:
    pass
else:
    raise AssertionError(
        "Expected OrchestrationDependencyError."
    )


print("✅ Enterprise decision orchestration engine validation passed.")

# COMMAND ----------

# ============================================================
# Enterprise Decision Orchestration Service Validation
# ============================================================

import importlib
from datetime import date

import src.orchestration.service

importlib.reload(src.orchestration.service)

from src.orchestration.configuration import (
    EnterpriseOrchestrationConfiguration,
)
from src.orchestration.engine import (
    EnterpriseDecisionOrchestrationEngine,
)
from src.orchestration.exceptions import (
    OrchestrationServiceError,
    OrchestrationValidationError,
)
from src.orchestration.models import (
    EnterpriseDecisionRequest,
    OrchestrationStage,
    OrchestrationStatus,
)
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)


configuration = EnterpriseOrchestrationConfiguration()

engine = EnterpriseDecisionOrchestrationEngine(
    configuration=configuration,
)

service = EnterpriseDecisionOrchestrationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine

result = service.execute(
    request=EnterpriseDecisionRequest(
        planning_date=date.today(),
        expected_order_lines=48_000.0,
        available_associates=40,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.92,
        recurring_shortage_days=18,
        recurring_surplus_days=0,
        overtime_dependency_days=15,
        planning_horizon_days=30,
    )
)

assert (
    result.workflow_status
    is OrchestrationStatus.COMPLETED
)

assert (
    result.completed_stage
    is OrchestrationStage.COMPLETE
)

assert result.associate_gap == 7

# ------------------------------------------------------------
# Invalid engine
# ------------------------------------------------------------

try:
    EnterpriseDecisionOrchestrationService(
        configuration=configuration,
        engine="invalid",
    )
except OrchestrationServiceError:
    pass
else:
    raise AssertionError(
        "Expected OrchestrationServiceError."
    )

# ------------------------------------------------------------
# Configuration mismatch
# ------------------------------------------------------------

try:
    EnterpriseDecisionOrchestrationService(
        configuration=EnterpriseOrchestrationConfiguration(),
        engine=engine,
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OrchestrationValidationError."
    )

# ------------------------------------------------------------
# Invalid request
# ------------------------------------------------------------

try:
    service.execute(
        request="invalid",
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Expected OrchestrationValidationError."
    )

print("✅ Enterprise decision orchestration service validation passed.")

# COMMAND ----------

# ============================================================
# Orchestration Package (__init__) Validation
# ============================================================

import importlib

import src.orchestration

importlib.reload(src.orchestration)

from src.orchestration import (
    EnterpriseOrchestrationConfiguration,
    EnterpriseDecisionOrchestrationEngine,
    EnterpriseDecisionOrchestrationService,
    EnterpriseDecisionRequest,
    EnterpriseDecisionResult,
    OrchestrationStage,
    OrchestrationStatus,
)

assert EnterpriseOrchestrationConfiguration is not None
assert EnterpriseDecisionOrchestrationEngine is not None
assert EnterpriseDecisionOrchestrationService is not None
assert EnterpriseDecisionRequest is not None
assert EnterpriseDecisionResult is not None
assert OrchestrationStage is not None
assert OrchestrationStatus is not None

print("✅ Orchestration package validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Constants Validation
# ============================================================

import importlib

import src.reporting.constants

importlib.reload(src.reporting.constants)

from src.reporting.constants import *

assert REPORTING_DOMAIN_VERSION == "1.0.0"

# ------------------------------------------------------------
# Formats
# ------------------------------------------------------------

assert DEFAULT_REPORT_FORMAT == REPORT_FORMAT_DICT

assert SUPPORTED_REPORT_FORMATS == (
    REPORT_FORMAT_JSON,
    REPORT_FORMAT_DICT,
    REPORT_FORMAT_TEXT,
)

# ------------------------------------------------------------
# Report Types
# ------------------------------------------------------------

assert DEFAULT_REPORT_TYPE == REPORT_TYPE_OPERATIONAL

assert SUPPORTED_REPORT_TYPES == (
    REPORT_TYPE_EXECUTIVE,
    REPORT_TYPE_OPERATIONAL,
    REPORT_TYPE_TECHNICAL,
)

# ------------------------------------------------------------
# Status
# ------------------------------------------------------------

assert SUPPORTED_REPORT_STATUSES == (
    REPORT_STATUS_SUCCESS,
    REPORT_STATUS_WARNING,
    REPORT_STATUS_ERROR,
)

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

assert DEFAULT_TIMEZONE == "UTC"

assert DEFAULT_REPORT_VERSION == "1.0.0"

assert MAX_REPORT_TITLE_LENGTH > 0

assert MAX_REPORT_SUMMARY_LENGTH > MAX_REPORT_TITLE_LENGTH

# ------------------------------------------------------------
# Sections
# ------------------------------------------------------------

assert DEFAULT_REPORT_SECTIONS == (
    SECTION_EXECUTIVE_SUMMARY,
    SECTION_FORECAST,
    SECTION_PLANNING,
    SECTION_OVERTIME,
    SECTION_STAFFING,
    SECTION_OPTIMIZATION,
    SECTION_METADATA,
)

# ------------------------------------------------------------
# Uniqueness
# ------------------------------------------------------------

assert len(SUPPORTED_REPORT_FORMATS) == len(
    set(SUPPORTED_REPORT_FORMATS)
)

assert len(SUPPORTED_REPORT_TYPES) == len(
    set(SUPPORTED_REPORT_TYPES)
)

assert len(SUPPORTED_REPORT_STATUSES) == len(
    set(SUPPORTED_REPORT_STATUSES)
)

assert len(DEFAULT_REPORT_SECTIONS) == len(
    set(DEFAULT_REPORT_SECTIONS)
)

print("✅ Reporting constants validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Exceptions Validation
# ============================================================

import importlib

import src.reporting.exceptions

importlib.reload(src.reporting.exceptions)

from src.reporting.exceptions import (
    ReportingConfigurationError,
    ReportingError,
    ReportingFormattingError,
    ReportingServiceError,
    ReportingValidationError,
)


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    ReportingValidationError,
    ReportingError,
)

assert issubclass(
    ReportingConfigurationError,
    ReportingError,
)

assert issubclass(
    ReportingFormattingError,
    ReportingError,
)

assert issubclass(
    ReportingServiceError,
    ReportingError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise ReportingValidationError(
        "Invalid reporting request."
    )
except ReportingError as exc:
    assert str(exc) == "Invalid reporting request."


try:
    raise ReportingConfigurationError(
        "Invalid reporting configuration."
    )
except ReportingError as exc:
    assert str(exc) == "Invalid reporting configuration."


try:
    raise ReportingFormattingError(
        "Report serialization failed."
    )
except ReportingError as exc:
    assert str(exc) == "Report serialization failed."


try:
    raise ReportingServiceError(
        "Reporting service failed."
    )
except ReportingError as exc:
    assert str(exc) == "Reporting service failed."


print("✅ Reporting exceptions validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Models Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.reporting.models

importlib.reload(src.reporting.models)

from src.reporting.exceptions import ReportingValidationError
from src.reporting.models import (
    DecisionReportRequest,
    EnterpriseDecisionReport,
    ReportFormat,
    ReportSection,
    ReportStatus,
    ReportType,
)


planning_date = date.today()
generated_at_utc = datetime.now(timezone.utc)


# ------------------------------------------------------------
# Valid report request
# ------------------------------------------------------------

request = DecisionReportRequest(
    report_type=ReportType.OPERATIONAL,
    report_format=ReportFormat.DICT,
    title="Daily Workforce Capacity Decision Report",
    include_metadata=True,
    include_rationale=True,
    include_empty_sections=False,
)

assert request.report_type is ReportType.OPERATIONAL
assert request.report_format is ReportFormat.DICT
assert request.include_metadata is True

request_payload = request.as_dict()

assert request_payload["report_type"] == "operational"
assert request_payload["report_format"] == "dict"
assert request_payload["include_rationale"] is True


# ------------------------------------------------------------
# Valid report sections
# ------------------------------------------------------------

executive_section = ReportSection(
    name="Executive Summary",
    content={
        "optimization_action": "FULL_TIME_HIRING",
        "optimization_priority": "HIGH",
        "optimization_status": "ACCEPTABLE",
    },
    order=0,
)

planning_section = ReportSection(
    name="Planning",
    content={
        "expected_order_lines": 48_000.0,
        "available_associates": 40,
        "required_associates": 47,
        "associate_gap": 7,
    },
    order=1,
)

assert executive_section.order == 0
assert planning_section.content["associate_gap"] == 7

section_payload = planning_section.as_dict()

assert section_payload["name"] == "Planning"
assert section_payload["order"] == 1
assert section_payload["content"]["required_associates"] == 47


# ------------------------------------------------------------
# Valid enterprise report
# ------------------------------------------------------------

report = EnterpriseDecisionReport(
    report_id="workforce-decision-2026-08-05",
    report_type=ReportType.OPERATIONAL,
    status=ReportStatus.SUCCESS,
    title="Daily Workforce Capacity Decision Report",
    summary=(
        "A seven-associate shortage was identified. Full-time hiring "
        "review is the primary enterprise workforce action."
    ),
    planning_date=planning_date,
    sections=(
        executive_section,
        planning_section,
    ),
    generated_at_utc=generated_at_utc,
    source_workflow_version="1.0.0",
    report_version="1.0.0",
    metadata={
        "workflow_status": "COMPLETED",
        "completed_stage": "complete",
    },
)

assert report.report_type is ReportType.OPERATIONAL
assert report.status is ReportStatus.SUCCESS
assert len(report.sections) == 2
assert report.sections[0].name == "Executive Summary"

report_payload = report.as_dict()

assert (
    report_payload["report_id"]
    == "workforce-decision-2026-08-05"
)
assert report_payload["report_type"] == "operational"
assert report_payload["status"] == "SUCCESS"
assert report_payload["planning_date"] == (
    planning_date.isoformat()
)
assert len(report_payload["sections"]) == 2
assert report_payload["sections"][1]["name"] == "Planning"
assert report_payload["source_workflow_version"] == "1.0.0"
assert report_payload["metadata"]["workflow_status"] == "COMPLETED"


# ------------------------------------------------------------
# Invalid model validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: DecisionReportRequest(
        report_type="operational",
        report_format=ReportFormat.DICT,
        title="Invalid report.",
    ),
    lambda: DecisionReportRequest(
        report_type=ReportType.OPERATIONAL,
        report_format="dict",
        title="Invalid report.",
    ),
    lambda: DecisionReportRequest(
        report_type=ReportType.OPERATIONAL,
        report_format=ReportFormat.DICT,
        title="   ",
    ),
    lambda: DecisionReportRequest(
        report_type=ReportType.OPERATIONAL,
        report_format=ReportFormat.DICT,
        title="Valid title",
        include_metadata="yes",
    ),
    lambda: ReportSection(
        name="",
        content={},
        order=0,
    ),
    lambda: ReportSection(
        name="Planning",
        content=[],
        order=0,
    ),
    lambda: ReportSection(
        name="Planning",
        content={},
        order=-1,
    ),
    lambda: EnterpriseDecisionReport(
        report_id="",
        report_type=ReportType.OPERATIONAL,
        status=ReportStatus.SUCCESS,
        title="Invalid report",
        summary="Invalid report identifier.",
        planning_date=planning_date,
        sections=(executive_section,),
        generated_at_utc=generated_at_utc,
        source_workflow_version="1.0.0",
    ),
    lambda: EnterpriseDecisionReport(
        report_id="invalid-sections",
        report_type=ReportType.OPERATIONAL,
        status=ReportStatus.SUCCESS,
        title="Invalid report",
        summary="No report sections.",
        planning_date=planning_date,
        sections=(),
        generated_at_utc=generated_at_utc,
        source_workflow_version="1.0.0",
    ),
    lambda: EnterpriseDecisionReport(
        report_id="duplicate-order",
        report_type=ReportType.OPERATIONAL,
        status=ReportStatus.SUCCESS,
        title="Invalid report",
        summary="Duplicate section order.",
        planning_date=planning_date,
        sections=(
            executive_section,
            ReportSection(
                name="Planning",
                content={},
                order=0,
            ),
        ),
        generated_at_utc=generated_at_utc,
        source_workflow_version="1.0.0",
    ),
    lambda: EnterpriseDecisionReport(
        report_id="unsorted-sections",
        report_type=ReportType.OPERATIONAL,
        status=ReportStatus.SUCCESS,
        title="Invalid report",
        summary="Sections are not sorted.",
        planning_date=planning_date,
        sections=(
            planning_section,
            executive_section,
        ),
        generated_at_utc=generated_at_utc,
        source_workflow_version="1.0.0",
    ),
    lambda: EnterpriseDecisionReport(
        report_id="empty-summary",
        report_type=ReportType.OPERATIONAL,
        status=ReportStatus.SUCCESS,
        title="Invalid report",
        summary="   ",
        planning_date=planning_date,
        sections=(executive_section,),
        generated_at_utc=generated_at_utc,
        source_workflow_version="1.0.0",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ReportingValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ReportingValidationError."
        )


print("✅ Reporting models validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Configuration Validation
# ============================================================

import importlib

import src.reporting.configuration

importlib.reload(src.reporting.configuration)

from src.reporting.configuration import ReportingConfiguration
from src.reporting.constants import DEFAULT_REPORT_SECTIONS
from src.reporting.exceptions import ReportingConfigurationError


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = ReportingConfiguration()

assert configuration.default_report_type == "operational"
assert configuration.default_report_format == "dict"
assert configuration.include_metadata is True
assert configuration.include_rationale is True
assert configuration.include_empty_sections is False
assert configuration.section_order == DEFAULT_REPORT_SECTIONS
assert configuration.indent_size == 4
assert configuration.report_version == "1.0.0"


# ------------------------------------------------------------
# Valid custom configuration
# ------------------------------------------------------------

custom_configuration = ReportingConfiguration(
    default_report_type="executive",
    default_report_format="json",
    include_metadata=False,
    include_rationale=True,
    include_empty_sections=True,
    section_order=(
        "Executive Summary",
        "Planning",
        "Optimization",
    ),
    indent_size=2,
    datetime_format="%Y-%m-%dT%H:%M:%SZ",
    maximum_title_length=150,
    maximum_summary_length=2000,
    report_version="1.1.0",
)

assert custom_configuration.default_report_type == "executive"
assert custom_configuration.default_report_format == "json"
assert custom_configuration.include_metadata is False
assert custom_configuration.include_empty_sections is True
assert custom_configuration.indent_size == 2
assert custom_configuration.report_version == "1.1.0"


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

payload = custom_configuration.as_dict()

assert payload["default_report_type"] == "executive"
assert payload["default_report_format"] == "json"
assert payload["section_order"] == [
    "Executive Summary",
    "Planning",
    "Optimization",
]
assert payload["indent_size"] == 2
assert payload["report_version"] == "1.1.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "default_report_type": "invalid",
    },
    {
        "default_report_format": "xml",
    },
    {
        "include_metadata": "yes",
    },
    {
        "include_rationale": 1,
    },
    {
        "include_empty_sections": None,
    },
    {
        "section_order": [],
    },
    {
        "section_order": (
            "Executive Summary",
            "Executive Summary",
        ),
    },
    {
        "section_order": (
            "Executive Summary",
            "",
        ),
    },
    {
        "indent_size": -1,
    },
    {
        "datetime_format": "   ",
    },
    {
        "maximum_title_length": 0,
    },
    {
        "maximum_summary_length": 100,
        "maximum_title_length": 200,
    },
    {
        "report_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        ReportingConfiguration(
            **invalid_arguments
        )
    except ReportingConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected ReportingConfigurationError for "
            f"{invalid_arguments}."
        )


print("✅ Reporting configuration validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Formatter Validation
# ============================================================

import importlib
import json
from datetime import date, datetime, timezone

import src.reporting.formatter

importlib.reload(src.reporting.formatter)

from src.reporting.configuration import ReportingConfiguration
from src.reporting.exceptions import ReportingValidationError
from src.reporting.formatter import (
    EnterpriseDecisionReportFormatter,
)
from src.reporting.models import (
    EnterpriseDecisionReport,
    ReportFormat,
    ReportSection,
    ReportStatus,
    ReportType,
)


planning_date = date.today()
generated_at_utc = datetime(
    2026,
    8,
    5,
    21,
    45,
    0,
    tzinfo=timezone.utc,
)

configuration = ReportingConfiguration(
    indent_size=2,
)

formatter = EnterpriseDecisionReportFormatter(
    configuration=configuration,
)

assert formatter.configuration is configuration


# ------------------------------------------------------------
# Test report
# ------------------------------------------------------------

report = EnterpriseDecisionReport(
    report_id="workforce-decision-2026-08-05",
    report_type=ReportType.OPERATIONAL,
    status=ReportStatus.SUCCESS,
    title="Daily Workforce Capacity Decision Report",
    summary=(
        "A seven-associate shortage was identified. "
        "Full-time hiring review is recommended."
    ),
    planning_date=planning_date,
    sections=(
        ReportSection(
            name="Executive Summary",
            content={
                "optimization_action": "FULL_TIME_HIRING",
                "optimization_priority": "HIGH",
                "optimization_status": "ACCEPTABLE",
            },
            order=0,
        ),
        ReportSection(
            name="Planning",
            content={
                "expected_order_lines": 48_000.0,
                "available_associates": 40,
                "required_associates": 47,
                "associate_gap": 7,
                "requires_action": True,
            },
            order=1,
        ),
    ),
    generated_at_utc=generated_at_utc,
    source_workflow_version="1.0.0",
    report_version="1.0.0",
    metadata={
        "workflow_status": "COMPLETED",
        "completed_stage": "complete",
    },
)


# ------------------------------------------------------------
# Dictionary formatting
# ------------------------------------------------------------

dictionary_output = formatter.format(
    report=report,
    report_format=ReportFormat.DICT,
)

assert isinstance(dictionary_output, dict)
assert (
    dictionary_output["report_id"]
    == "workforce-decision-2026-08-05"
)
assert dictionary_output["status"] == "SUCCESS"
assert len(dictionary_output["sections"]) == 2
assert (
    dictionary_output["sections"][1]["content"]
    ["associate_gap"]
    == 7
)


# ------------------------------------------------------------
# JSON formatting
# ------------------------------------------------------------

json_output = formatter.format(
    report=report,
    report_format=ReportFormat.JSON,
)

assert isinstance(json_output, str)

decoded_json = json.loads(json_output)

assert decoded_json["report_type"] == "operational"
assert decoded_json["status"] == "SUCCESS"
assert decoded_json["sections"][0]["name"] == (
    "Executive Summary"
)
assert decoded_json["metadata"]["workflow_status"] == (
    "COMPLETED"
)

assert "\n  " in json_output


# ------------------------------------------------------------
# Text formatting
# ------------------------------------------------------------

text_output = formatter.format(
    report=report,
    report_format=ReportFormat.TEXT,
)

assert isinstance(text_output, str)

assert (
    "Daily Workforce Capacity Decision Report"
    in text_output
)
assert "Report ID: workforce-decision-2026-08-05" in text_output
assert "Executive Summary" in text_output
assert "Optimization Action: FULL_TIME_HIRING" in text_output
assert "Expected Order Lines: 48,000" in text_output
assert "Requires Action: Yes" in text_output
assert "Workflow Status: COMPLETED" in text_output
assert "Source Workflow Version: 1.0.0" in text_output
assert "Report Version: 1.0.0" in text_output


# ------------------------------------------------------------
# Direct formatter methods
# ------------------------------------------------------------

assert formatter.to_dict(report=report) == dictionary_output
assert formatter.to_json(report=report) == json_output
assert formatter.to_text(report=report) == text_output


# ------------------------------------------------------------
# Invalid formatter configuration
# ------------------------------------------------------------

try:
    EnterpriseDecisionReportFormatter(
        configuration="invalid",
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Expected ReportingValidationError."
    )


# ------------------------------------------------------------
# Invalid report
# ------------------------------------------------------------

invalid_calls = [
    lambda: formatter.format(
        report="invalid",
        report_format=ReportFormat.DICT,
    ),
    lambda: formatter.format(
        report=report,
        report_format="json",
    ),
    lambda: formatter.to_dict(
        report="invalid",
    ),
    lambda: formatter.to_json(
        report="invalid",
    ),
    lambda: formatter.to_text(
        report="invalid",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ReportingValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ReportingValidationError."
        )


print("✅ Reporting formatter validation passed.")

# COMMAND ----------

# ============================================================
# Enterprise Decision Reporting Service Validation
# ============================================================

import importlib
import json
from datetime import date, datetime, timezone

import src.reporting.service

importlib.reload(src.reporting.service)

from src.orchestration.models import (
    EnterpriseDecisionResult,
    OrchestrationStage,
    OrchestrationStatus,
)
from src.reporting.configuration import ReportingConfiguration
from src.reporting.exceptions import (
    ReportingServiceError,
    ReportingValidationError,
)
from src.reporting.formatter import (
    EnterpriseDecisionReportFormatter,
)
from src.reporting.models import (
    DecisionReportRequest,
    EnterpriseDecisionReport,
    ReportFormat,
    ReportStatus,
    ReportType,
)
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


planning_date = date.today()

decision_result = EnterpriseDecisionResult(
    planning_date=planning_date,
    workflow_status=OrchestrationStatus.COMPLETED,
    completed_stage=OrchestrationStage.COMPLETE,
    expected_order_lines=48_000.0,
    available_associates=40,
    required_associates=47,
    associate_gap=7,
    overtime_recommendation="MANDATORY_OVERTIME",
    staffing_recommendation="FULL_TIME_HIRING_REVIEW",
    optimization_action="FULL_TIME_HIRING",
    optimization_priority="HIGH",
    optimization_status="ACCEPTABLE",
    overtime_hours=35.0,
    recommended_associates=7,
    forecast_confidence=0.92,
    rationale=(
        "Full-time hiring review selected as the primary "
        "enterprise workforce action."
    ),
    generated_at_utc=datetime.now(timezone.utc),
    workflow_version="1.0.0",
)

configuration = ReportingConfiguration()

formatter = EnterpriseDecisionReportFormatter(
    configuration=configuration,
)

service = EnterpriseDecisionReportingService(
    configuration=configuration,
    formatter=formatter,
)

assert service.configuration is configuration
assert service.formatter is formatter


# ------------------------------------------------------------
# Build structured report
# ------------------------------------------------------------

operational_request = DecisionReportRequest(
    report_type=ReportType.OPERATIONAL,
    report_format=ReportFormat.DICT,
    title="Daily Workforce Capacity Decision Report",
    include_metadata=True,
    include_rationale=True,
    include_empty_sections=False,
)

report = service.build_report(
    decision_result=decision_result,
    request=operational_request,
)

assert isinstance(report, EnterpriseDecisionReport)
assert report.report_type is ReportType.OPERATIONAL
assert report.status is ReportStatus.SUCCESS
assert report.planning_date == planning_date
assert report.source_workflow_version == "1.0.0"

section_names = tuple(
    section.name for section in report.sections
)

assert section_names == (
    "Executive Summary",
    "Forecast",
    "Planning",
    "Overtime",
    "Staffing",
    "Optimization",
    "Metadata",
)

assert report.sections[2].content["associate_gap"] == 7
assert (
    report.sections[5].content["action"]
    == "FULL_TIME_HIRING"
)


# ------------------------------------------------------------
# Dictionary output
# ------------------------------------------------------------

dictionary_output = service.generate(
    decision_result=decision_result,
    request=operational_request,
)

assert isinstance(dictionary_output, dict)
assert dictionary_output["report_type"] == "operational"
assert dictionary_output["status"] == "SUCCESS"
assert len(dictionary_output["sections"]) == 7
assert (
    dictionary_output["sections"][2]["content"]
    ["required_associates"]
    == 47
)


# ------------------------------------------------------------
# JSON output
# ------------------------------------------------------------

json_output = service.generate(
    decision_result=decision_result,
    request=DecisionReportRequest(
        report_type=ReportType.EXECUTIVE,
        report_format=ReportFormat.JSON,
        title="Executive Workforce Decision Brief",
        include_metadata=True,
        include_rationale=True,
    ),
)

assert isinstance(json_output, str)

decoded_json = json.loads(json_output)

assert decoded_json["report_type"] == "executive"
assert decoded_json["status"] == "SUCCESS"

executive_section_names = tuple(
    section["name"]
    for section in decoded_json["sections"]
)

assert executive_section_names == (
    "Executive Summary",
    "Planning",
    "Optimization",
    "Metadata",
)


# ------------------------------------------------------------
# Text output
# ------------------------------------------------------------

text_output = service.generate(
    decision_result=decision_result,
    request=DecisionReportRequest(
        report_type=ReportType.TECHNICAL,
        report_format=ReportFormat.TEXT,
        title="Technical Workforce Decision Report",
        include_metadata=True,
        include_rationale=True,
    ),
)

assert isinstance(text_output, str)
assert "Technical Workforce Decision Report" in text_output
assert "Expected Order Lines: 48,000" in text_output
assert "Associate Gap: 7" in text_output
assert "Action: FULL_TIME_HIRING" in text_output
assert "Workflow Status: COMPLETED" in text_output


# ------------------------------------------------------------
# Report without metadata or rationale
# ------------------------------------------------------------

minimal_report = service.build_report(
    decision_result=decision_result,
    request=DecisionReportRequest(
        report_type=ReportType.EXECUTIVE,
        report_format=ReportFormat.DICT,
        title="Minimal Executive Report",
        include_metadata=False,
        include_rationale=False,
    ),
)

minimal_section_names = tuple(
    section.name
    for section in minimal_report.sections
)

assert "Metadata" not in minimal_section_names

executive_content = minimal_report.sections[0].content
optimization_content = minimal_report.sections[2].content

assert "rationale" not in executive_content
assert "rationale" not in optimization_content
assert minimal_report.metadata == {}


# ------------------------------------------------------------
# Invalid dependencies
# ------------------------------------------------------------

try:
    EnterpriseDecisionReportingService(
        configuration="invalid",
    )
except ReportingServiceError:
    pass
else:
    raise AssertionError(
        "Expected ReportingServiceError."
    )


try:
    EnterpriseDecisionReportingService(
        configuration=configuration,
        formatter="invalid",
    )
except ReportingServiceError:
    pass
else:
    raise AssertionError(
        "Expected ReportingServiceError."
    )


different_configuration = ReportingConfiguration(
    indent_size=2,
)

try:
    EnterpriseDecisionReportingService(
        configuration=different_configuration,
        formatter=formatter,
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Expected ReportingValidationError for inconsistent "
        "configuration and formatter."
    )


# ------------------------------------------------------------
# Invalid requests
# ------------------------------------------------------------

invalid_calls = [
    lambda: service.build_report(
        decision_result="invalid",
        request=operational_request,
    ),
    lambda: service.build_report(
        decision_result=decision_result,
        request="invalid",
    ),
    lambda: service.generate(
        decision_result="invalid",
        request=operational_request,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ReportingValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ReportingValidationError."
        )


print("✅ Enterprise decision reporting service validation passed.")

# COMMAND ----------

# ============================================================
# Reporting Package (__init__) Validation
# ============================================================

import importlib

import src.reporting

importlib.reload(src.reporting)

from src.reporting import (
    DEFAULT_REPORT_FORMAT,
    DEFAULT_REPORT_TYPE,
    REPORTING_DOMAIN_VERSION,
    DecisionReportRequest,
    EnterpriseDecisionReport,
    EnterpriseDecisionReportFormatter,
    EnterpriseDecisionReportingService,
    ReportFormat,
    ReportSection,
    ReportStatus,
    ReportType,
    ReportingConfiguration,
    ReportingError,
    ReportingFormattingError,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert REPORTING_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_REPORT_TYPE == "operational"
assert DEFAULT_REPORT_FORMAT == "dict"


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    ReportingFormattingError,
    ReportingError,
)


# ------------------------------------------------------------
# Models and enums
# ------------------------------------------------------------

assert DecisionReportRequest is not None
assert EnterpriseDecisionReport is not None
assert ReportFormat is not None
assert ReportSection is not None
assert ReportStatus is not None
assert ReportType is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert ReportingConfiguration is not None
assert EnterpriseDecisionReportFormatter is not None
assert EnterpriseDecisionReportingService is not None


print("✅ Reporting package validation passed.")

# COMMAND ----------

# ============================================================
# Monitoring Constants Validation
# ============================================================

import importlib

import src.monitoring.constants

importlib.reload(src.monitoring.constants)

from src.monitoring.constants import *


# ------------------------------------------------------------
# Domain
# ------------------------------------------------------------

assert MONITORING_DOMAIN_NAME == (
    "enterprise-monitoring-observability"
)

assert MONITORING_DOMAIN_VERSION == "1.0.0"


# ------------------------------------------------------------
# Health statuses
# ------------------------------------------------------------

assert SUPPORTED_HEALTH_STATUSES == (
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_UNKNOWN,
)

assert len(SUPPORTED_HEALTH_STATUSES) == len(
    set(SUPPORTED_HEALTH_STATUSES)
)


# ------------------------------------------------------------
# Execution statuses
# ------------------------------------------------------------

assert SUPPORTED_EXECUTION_STATUSES == (
    EXECUTION_STATUS_PENDING,
    EXECUTION_STATUS_RUNNING,
    EXECUTION_STATUS_SUCCEEDED,
    EXECUTION_STATUS_FAILED,
    EXECUTION_STATUS_CANCELLED,
)

assert len(SUPPORTED_EXECUTION_STATUSES) == len(
    set(SUPPORTED_EXECUTION_STATUSES)
)


# ------------------------------------------------------------
# Severity levels
# ------------------------------------------------------------

assert SUPPORTED_SEVERITY_LEVELS == (
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_ERROR,
    SEVERITY_CRITICAL,
)

assert len(SUPPORTED_SEVERITY_LEVELS) == len(
    set(SUPPORTED_SEVERITY_LEVELS)
)


# ------------------------------------------------------------
# Metric types
# ------------------------------------------------------------

assert SUPPORTED_METRIC_TYPES == (
    METRIC_TYPE_COUNTER,
    METRIC_TYPE_GAUGE,
    METRIC_TYPE_TIMER,
    METRIC_TYPE_DISTRIBUTION,
)

assert len(SUPPORTED_METRIC_TYPES) == len(
    set(SUPPORTED_METRIC_TYPES)
)


# ------------------------------------------------------------
# Monitoring components
# ------------------------------------------------------------

assert COMPONENT_ORCHESTRATION in (
    SUPPORTED_MONITORING_COMPONENTS
)

assert COMPONENT_REPORTING in (
    SUPPORTED_MONITORING_COMPONENTS
)

assert COMPONENT_PLATFORM in (
    SUPPORTED_MONITORING_COMPONENTS
)

assert len(SUPPORTED_MONITORING_COMPONENTS) == len(
    set(SUPPORTED_MONITORING_COMPONENTS)
)


# ------------------------------------------------------------
# Thresholds
# ------------------------------------------------------------

assert MINIMUM_SUCCESS_RATE == 0.0

assert MAXIMUM_SUCCESS_RATE == 1.0

assert (
    MINIMUM_SUCCESS_RATE
    <= DEFAULT_CRITICAL_SUCCESS_RATE
    < DEFAULT_WARNING_SUCCESS_RATE
    <= MAXIMUM_SUCCESS_RATE
)

assert DEFAULT_WARNING_DURATION_MS > 0

assert (
    DEFAULT_CRITICAL_DURATION_MS
    > DEFAULT_WARNING_DURATION_MS
)

assert DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS > 0


# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

assert DEFAULT_MONITORING_VERSION == "1.0.0"

assert DEFAULT_TIMEZONE == "UTC"

assert DEFAULT_TIMESTAMP_FORMAT != ""


print("✅ Monitoring constants validation passed.")

# COMMAND ----------

# ============================================================
# Implementation 23.2 — Monitoring Exceptions Validation
# ============================================================

import importlib

import src.monitoring.exceptions

importlib.reload(src.monitoring.exceptions)

from src.monitoring.exceptions import (
    MonitoringConfigurationError,
    MonitoringError,
    MonitoringHealthCheckError,
    MonitoringMetricsError,
    MonitoringServiceError,
    MonitoringValidationError,
)


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(
    MonitoringValidationError,
    MonitoringError,
)

assert issubclass(
    MonitoringConfigurationError,
    MonitoringError,
)

assert issubclass(
    MonitoringMetricsError,
    MonitoringError,
)

assert issubclass(
    MonitoringHealthCheckError,
    MonitoringError,
)

assert issubclass(
    MonitoringServiceError,
    MonitoringError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise MonitoringValidationError(
        "Invalid monitoring request."
    )
except MonitoringError as exc:
    assert str(exc) == "Invalid monitoring request."


try:
    raise MonitoringConfigurationError(
        "Invalid monitoring configuration."
    )
except MonitoringError as exc:
    assert str(exc) == "Invalid monitoring configuration."


try:
    raise MonitoringMetricsError(
        "Metric aggregation failed."
    )
except MonitoringError as exc:
    assert str(exc) == "Metric aggregation failed."


try:
    raise MonitoringHealthCheckError(
        "Component health check failed."
    )
except MonitoringError as exc:
    assert str(exc) == "Component health check failed."


try:
    raise MonitoringServiceError(
        "Monitoring service failed."
    )
except MonitoringError as exc:
    assert str(exc) == "Monitoring service failed."


print(
    "✅ Implementation 23.2 — "
    "Monitoring exceptions validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.3 — Monitoring Models Validation
# ============================================================

import importlib
from datetime import datetime, timedelta, timezone

import src.monitoring.models

importlib.reload(src.monitoring.models)

from src.monitoring.exceptions import MonitoringValidationError
from src.monitoring.models import (
    ComponentHealth,
    ExecutionRecord,
    ExecutionStatus,
    HealthStatus,
    MetricRecord,
    MetricType,
    MonitoringAlert,
    PlatformHealthReport,
    SeverityLevel,
)


recorded_at_utc = datetime.now(timezone.utc)
completed_at_utc = recorded_at_utc + timedelta(seconds=2)


# ------------------------------------------------------------
# Metric record
# ------------------------------------------------------------

metric = MetricRecord(
    name="execution_duration_ms",
    metric_type=MetricType.TIMER,
    component="orchestration",
    value=2_000.0,
    recorded_at_utc=recorded_at_utc,
    unit="milliseconds",
    tags={
        "operation": "enterprise_decision",
        "environment": "development",
    },
)

assert metric.metric_type is MetricType.TIMER
assert metric.value == 2_000.0

metric_payload = metric.as_dict()

assert metric_payload["metric_type"] == "TIMER"
assert metric_payload["component"] == "orchestration"
assert metric_payload["unit"] == "milliseconds"
assert metric_payload["tags"]["environment"] == "development"


# ------------------------------------------------------------
# Execution record
# ------------------------------------------------------------

execution = ExecutionRecord(
    execution_id="execution-001",
    component="orchestration",
    operation="enterprise_decision",
    status=ExecutionStatus.SUCCEEDED,
    started_at_utc=recorded_at_utc,
    completed_at_utc=completed_at_utc,
    duration_ms=2_000.0,
    message="Enterprise decision completed.",
    metadata={
        "workflow_version": "1.0.0",
    },
)

assert execution.status is ExecutionStatus.SUCCEEDED
assert execution.duration_ms == 2_000.0

execution_payload = execution.as_dict()

assert execution_payload["status"] == "SUCCEEDED"
assert execution_payload["execution_id"] == "execution-001"
assert execution_payload["duration_ms"] == 2_000.0


# ------------------------------------------------------------
# Running execution
# ------------------------------------------------------------

running_execution = ExecutionRecord(
    execution_id="execution-002",
    component="reporting",
    operation="generate_report",
    status=ExecutionStatus.RUNNING,
    started_at_utc=recorded_at_utc,
)

assert running_execution.status is ExecutionStatus.RUNNING
assert running_execution.completed_at_utc is None
assert running_execution.duration_ms is None


# ------------------------------------------------------------
# Component health
# ------------------------------------------------------------

healthy_component = ComponentHealth(
    component="orchestration",
    status=HealthStatus.HEALTHY,
    checked_at_utc=recorded_at_utc,
    response_time_ms=15.5,
    message="Orchestration service is healthy.",
    details={
        "dependency_count": 4,
    },
)

degraded_component = ComponentHealth(
    component="reporting",
    status=HealthStatus.DEGRADED,
    checked_at_utc=recorded_at_utc,
    response_time_ms=250.0,
    message="Reporting service latency is elevated.",
)

assert healthy_component.is_available is True
assert degraded_component.is_available is True

health_payload = healthy_component.as_dict()

assert health_payload["status"] == "HEALTHY"
assert health_payload["is_available"] is True
assert health_payload["response_time_ms"] == 15.5


# ------------------------------------------------------------
# Monitoring alert
# ------------------------------------------------------------

alert = MonitoringAlert(
    alert_id="alert-001",
    component="reporting",
    severity=SeverityLevel.WARNING,
    title="Reporting latency warning",
    message="Report generation exceeded the warning threshold.",
    created_at_utc=recorded_at_utc,
    metric_name="execution_duration_ms",
    observed_value=6_000.0,
    threshold_value=5_000.0,
    metadata={
        "operation": "generate_report",
    },
)

assert alert.severity is SeverityLevel.WARNING
assert alert.observed_value == 6_000.0

alert_payload = alert.as_dict()

assert alert_payload["severity"] == "WARNING"
assert alert_payload["metric_name"] == "execution_duration_ms"
assert alert_payload["threshold_value"] == 5_000.0


# ------------------------------------------------------------
# Platform health report
# ------------------------------------------------------------

platform_report = PlatformHealthReport(
    status=HealthStatus.DEGRADED,
    components=(
        healthy_component,
        degraded_component,
    ),
    generated_at_utc=recorded_at_utc,
    monitoring_version="1.0.0",
)

assert platform_report.status is HealthStatus.DEGRADED
assert len(platform_report.components) == 2

platform_payload = platform_report.as_dict()

assert platform_payload["status"] == "DEGRADED"
assert len(platform_payload["components"]) == 2
assert platform_payload["monitoring_version"] == "1.0.0"

assert (
    PlatformHealthReport.resolve_status(
        components=(
            healthy_component,
            degraded_component,
        )
    )
    is HealthStatus.DEGRADED
)


# ------------------------------------------------------------
# Invalid model validation
# ------------------------------------------------------------

invalid_calls = [
    lambda: MetricRecord(
        name="",
        metric_type=MetricType.COUNTER,
        component="orchestration",
        value=1.0,
        recorded_at_utc=recorded_at_utc,
    ),
    lambda: MetricRecord(
        name="execution_count",
        metric_type=MetricType.COUNTER,
        component="invalid",
        value=1.0,
        recorded_at_utc=recorded_at_utc,
    ),
    lambda: MetricRecord(
        name="execution_count",
        metric_type=MetricType.COUNTER,
        component="orchestration",
        value=-1.0,
        recorded_at_utc=recorded_at_utc,
    ),
    lambda: ExecutionRecord(
        execution_id="execution-invalid",
        component="orchestration",
        operation="enterprise_decision",
        status=ExecutionStatus.SUCCEEDED,
        started_at_utc=recorded_at_utc,
    ),
    lambda: ExecutionRecord(
        execution_id="execution-invalid",
        component="orchestration",
        operation="enterprise_decision",
        status=ExecutionStatus.RUNNING,
        started_at_utc=recorded_at_utc,
        completed_at_utc=completed_at_utc,
    ),
    lambda: ExecutionRecord(
        execution_id="execution-invalid",
        component="orchestration",
        operation="enterprise_decision",
        status=ExecutionStatus.FAILED,
        started_at_utc=completed_at_utc,
        completed_at_utc=recorded_at_utc,
        duration_ms=1.0,
    ),
    lambda: ComponentHealth(
        component="invalid",
        status=HealthStatus.HEALTHY,
        checked_at_utc=recorded_at_utc,
        response_time_ms=1.0,
        message="Invalid component.",
    ),
    lambda: ComponentHealth(
        component="orchestration",
        status=HealthStatus.HEALTHY,
        checked_at_utc=recorded_at_utc,
        response_time_ms=-1.0,
        message="Invalid response time.",
    ),
    lambda: MonitoringAlert(
        alert_id="alert-invalid",
        component="reporting",
        severity=SeverityLevel.WARNING,
        title="Invalid alert",
        message="Observed value without metric name.",
        created_at_utc=recorded_at_utc,
        observed_value=10.0,
    ),
    lambda: PlatformHealthReport(
        status=HealthStatus.HEALTHY,
        components=(
            healthy_component,
            degraded_component,
        ),
        generated_at_utc=recorded_at_utc,
    ),
    lambda: PlatformHealthReport(
        status=HealthStatus.HEALTHY,
        components=(),
        generated_at_utc=recorded_at_utc,
    ),
    lambda: PlatformHealthReport(
        status=HealthStatus.HEALTHY,
        components=(
            healthy_component,
            healthy_component,
        ),
        generated_at_utc=recorded_at_utc,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except MonitoringValidationError:
        pass
    else:
        raise AssertionError(
            "Expected MonitoringValidationError."
        )


print(
    "✅ Implementation 23.3 — "
    "Monitoring models validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.4 — Monitoring Configuration Validation
# ============================================================

import importlib

import src.monitoring.configuration

importlib.reload(src.monitoring.configuration)

from src.monitoring.configuration import (
    MonitoringConfiguration,
)
from src.monitoring.constants import (
    SUPPORTED_MONITORING_COMPONENTS,
)
from src.monitoring.exceptions import (
    MonitoringConfigurationError,
)


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = MonitoringConfiguration()

assert configuration.enabled_components == (
    SUPPORTED_MONITORING_COMPONENTS
)

assert configuration.warning_success_rate == 0.95
assert configuration.critical_success_rate == 0.80

assert configuration.warning_duration_ms == 5_000.0
assert configuration.critical_duration_ms == 15_000.0

assert (
    configuration.health_check_timeout_seconds
    == 30.0
)

assert configuration.enable_metric_collection is True
assert configuration.enable_health_checks is True
assert configuration.enable_alert_generation is True
assert configuration.retain_execution_metadata is True
assert configuration.monitoring_version == "1.0.0"


# ------------------------------------------------------------
# Valid custom configuration
# ------------------------------------------------------------

custom_configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
    warning_success_rate=0.90,
    critical_success_rate=0.70,
    warning_duration_ms=3_000.0,
    critical_duration_ms=10_000.0,
    health_check_timeout_seconds=15.0,
    enable_metric_collection=True,
    enable_health_checks=True,
    enable_alert_generation=False,
    retain_execution_metadata=False,
    monitoring_version="1.1.0",
)

assert custom_configuration.enabled_components == (
    "orchestration",
    "reporting",
    "platform",
)

assert custom_configuration.warning_success_rate == 0.90
assert custom_configuration.critical_success_rate == 0.70
assert custom_configuration.enable_alert_generation is False
assert custom_configuration.retain_execution_metadata is False
assert custom_configuration.monitoring_version == "1.1.0"


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

payload = custom_configuration.as_dict()

assert payload["enabled_components"] == [
    "orchestration",
    "reporting",
    "platform",
]

assert payload["warning_success_rate"] == 0.90
assert payload["critical_duration_ms"] == 10_000.0
assert payload["enable_alert_generation"] is False
assert payload["monitoring_version"] == "1.1.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "enabled_components": [],
    },
    {
        "enabled_components": (
            "orchestration",
            "orchestration",
        ),
    },
    {
        "enabled_components": (
            "orchestration",
            "invalid",
        ),
    },
    {
        "warning_success_rate": -0.1,
    },
    {
        "warning_success_rate": 1.1,
    },
    {
        "critical_success_rate": 0.95,
        "warning_success_rate": 0.90,
    },
    {
        "warning_duration_ms": 0,
    },
    {
        "critical_duration_ms": 5_000.0,
        "warning_duration_ms": 5_000.0,
    },
    {
        "health_check_timeout_seconds": 0,
    },
    {
        "enable_metric_collection": "yes",
    },
    {
        "enable_health_checks": 1,
    },
    {
        "enable_alert_generation": None,
    },
    {
        "retain_execution_metadata": "true",
    },
    {
        "monitoring_version": "   ",
    },
]

for invalid_arguments in invalid_cases:
    try:
        MonitoringConfiguration(
            **invalid_arguments
        )
    except MonitoringConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected MonitoringConfigurationError for "
            f"{invalid_arguments}."
        )


print(
    "✅ Implementation 23.4 — "
    "Monitoring configuration validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.5 — Monitoring Metrics Validation
# ============================================================

import importlib
from datetime import datetime, timedelta, timezone

import src.monitoring.metrics

importlib.reload(src.monitoring.metrics)

from src.monitoring.configuration import MonitoringConfiguration
from src.monitoring.exceptions import (
    MonitoringMetricsError,
    MonitoringValidationError,
)
from src.monitoring.metrics import MonitoringMetricsService
from src.monitoring.models import (
    ExecutionRecord,
    ExecutionStatus,
    MetricRecord,
    MetricType,
    SeverityLevel,
)


started_at_utc = datetime.now(timezone.utc)

successful_execution = ExecutionRecord(
    execution_id="execution-success",
    component="orchestration",
    operation="enterprise_decision",
    status=ExecutionStatus.SUCCEEDED,
    started_at_utc=started_at_utc,
    completed_at_utc=(
        started_at_utc + timedelta(seconds=2)
    ),
    duration_ms=2_000.0,
)

failed_execution = ExecutionRecord(
    execution_id="execution-failure",
    component="orchestration",
    operation="enterprise_decision",
    status=ExecutionStatus.FAILED,
    started_at_utc=started_at_utc,
    completed_at_utc=(
        started_at_utc + timedelta(seconds=8)
    ),
    duration_ms=8_000.0,
    message="Execution failed.",
)


configuration = MonitoringConfiguration()

metrics_service = MonitoringMetricsService(
    configuration=configuration,
)

assert metrics_service.configuration is configuration
assert metrics_service.metrics == ()


# ------------------------------------------------------------
# Generate execution metrics
# ------------------------------------------------------------

generated_metrics = metrics_service.metrics_from_executions(
    executions=(
        successful_execution,
        failed_execution,
    )
)

assert len(generated_metrics) == 6

metric_names = tuple(
    metric.name
    for metric in generated_metrics
)

assert metric_names.count("execution_count") == 2
assert metric_names.count("success_count") == 1
assert metric_names.count("failure_count") == 1
assert metric_names.count("execution_duration_ms") == 2


# ------------------------------------------------------------
# Record metrics
# ------------------------------------------------------------

recorded = metrics_service.record_many(
    metrics=generated_metrics,
)

assert recorded == generated_metrics
assert metrics_service.metrics == generated_metrics


custom_metric = MetricRecord(
    name="component_availability",
    metric_type=MetricType.GAUGE,
    component="orchestration",
    value=1.0,
    recorded_at_utc=started_at_utc,
    unit="ratio",
)

assert (
    metrics_service.record(
        metric=custom_metric,
    )
    is custom_metric
)

assert len(metrics_service.metrics) == 7


# ------------------------------------------------------------
# Execution summary
# ------------------------------------------------------------

summary = metrics_service.summarize_executions(
    executions=(
        successful_execution,
        failed_execution,
    )
)

assert summary["execution_count"] == 2.0
assert summary["success_count"] == 1.0
assert summary["failure_count"] == 1.0
assert summary["success_rate"] == 0.5
assert summary["failure_rate"] == 0.5
assert summary["execution_duration_ms"] == 5_000.0


empty_summary = metrics_service.summarize_executions(
    executions=()
)

assert empty_summary["execution_count"] == 0.0
assert empty_summary["success_rate"] == 0.0


# ------------------------------------------------------------
# Metric aggregation
# ------------------------------------------------------------

aggregated = metrics_service.aggregate_metrics(
    metrics=generated_metrics,
)

assert aggregated["orchestration"]["execution_count"] == 2.0
assert aggregated["orchestration"]["success_count"] == 1.0
assert aggregated["orchestration"]["failure_count"] == 1.0

assert (
    aggregated["orchestration"]
    ["execution_duration_ms"]
    == 5_000.0
)


# ------------------------------------------------------------
# Alert evaluation
# ------------------------------------------------------------

alerts = metrics_service.evaluate_execution_alerts(
    component="orchestration",
    summary=summary,
)

assert len(alerts) == 2

assert alerts[0].severity is SeverityLevel.CRITICAL
assert alerts[0].metric_name == "success_rate"

assert alerts[1].severity is SeverityLevel.WARNING
assert alerts[1].metric_name == "execution_duration_ms"


healthy_alerts = metrics_service.evaluate_execution_alerts(
    component="orchestration",
    summary={
        "success_rate": 0.99,
        "execution_duration_ms": 1_000.0,
    },
)

assert healthy_alerts == ()


critical_latency_alerts = (
    metrics_service.evaluate_execution_alerts(
        component="orchestration",
        summary={
            "success_rate": 0.99,
            "execution_duration_ms": 20_000.0,
        },
    )
)

assert len(critical_latency_alerts) == 1
assert (
    critical_latency_alerts[0].severity
    is SeverityLevel.CRITICAL
)


# ------------------------------------------------------------
# Disabled metric collection
# ------------------------------------------------------------

disabled_metrics_service = MonitoringMetricsService(
    configuration=MonitoringConfiguration(
        enable_metric_collection=False,
    )
)

try:
    disabled_metrics_service.record(
        metric=custom_metric,
    )
except MonitoringMetricsError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringMetricsError."
    )


# ------------------------------------------------------------
# Disabled alerts
# ------------------------------------------------------------

disabled_alert_service = MonitoringMetricsService(
    configuration=MonitoringConfiguration(
        enable_alert_generation=False,
    )
)

assert (
    disabled_alert_service.evaluate_execution_alerts(
        component="orchestration",
        summary=summary,
    )
    == ()
)


# ------------------------------------------------------------
# Invalid inputs
# ------------------------------------------------------------

invalid_calls = [
    lambda: MonitoringMetricsService(
        configuration="invalid",
    ),
    lambda: metrics_service.record(
        metric="invalid",
    ),
    lambda: metrics_service.record_many(
        metrics=("invalid",),
    ),
    lambda: metrics_service.metrics_from_executions(
        executions=("invalid",),
    ),
    lambda: metrics_service.summarize_executions(
        executions=("invalid",),
    ),
    lambda: metrics_service.aggregate_metrics(
        metrics=("invalid",),
    ),
    lambda: metrics_service.evaluate_execution_alerts(
        component="invalid",
        summary=summary,
    ),
    lambda: metrics_service.evaluate_execution_alerts(
        component="orchestration",
        summary="invalid",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except MonitoringValidationError:
        pass
    else:
        raise AssertionError(
            "Expected MonitoringValidationError."
        )


# ------------------------------------------------------------
# Clear metrics
# ------------------------------------------------------------

metrics_service.clear()

assert metrics_service.metrics == ()


print(
    "✅ Implementation 23.5 — "
    "Monitoring metrics validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.6 — Monitoring Health Validation
# ============================================================

import importlib
from datetime import datetime, timezone

import src.monitoring.health

importlib.reload(src.monitoring.health)

from src.monitoring.configuration import MonitoringConfiguration
from src.monitoring.exceptions import (
    MonitoringHealthCheckError,
    MonitoringValidationError,
)
from src.monitoring.health import MonitoringHealthService
from src.monitoring.models import (
    ComponentHealth,
    HealthStatus,
    PlatformHealthReport,
    SeverityLevel,
)


configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
)

health_service = MonitoringHealthService(
    configuration=configuration,
)

assert health_service.configuration is configuration
assert health_service.registered_components == ()


# ------------------------------------------------------------
# Register health checks
# ------------------------------------------------------------

health_service.register(
    component="orchestration",
    health_check=lambda: True,
)

health_service.register(
    component="reporting",
    health_check=lambda: {
        "healthy": True,
        "degraded": True,
        "message": "Reporting latency is elevated.",
        "details": {
            "dependency": "formatter",
        },
    },
)

health_service.register(
    component="platform",
    health_check=lambda: False,
)

assert health_service.registered_components == (
    "orchestration",
    "reporting",
    "platform",
)


# ------------------------------------------------------------
# Individual health checks
# ------------------------------------------------------------

orchestration_health = health_service.check_component(
    component="orchestration",
)

assert isinstance(
    orchestration_health,
    ComponentHealth,
)

assert orchestration_health.status is HealthStatus.HEALTHY
assert orchestration_health.is_available is True


reporting_health = health_service.check_component(
    component="reporting",
)

assert reporting_health.status is HealthStatus.DEGRADED
assert reporting_health.is_available is True
assert (
    reporting_health.message
    == "Reporting latency is elevated."
)
assert (
    reporting_health.details["dependency"]
    == "formatter"
)


platform_health = health_service.check_component(
    component="platform",
)

assert platform_health.status is HealthStatus.UNHEALTHY
assert platform_health.is_available is False


# ------------------------------------------------------------
# Platform health report
# ------------------------------------------------------------

health_report = health_service.check_all()

assert isinstance(
    health_report,
    PlatformHealthReport,
)

assert health_report.status is HealthStatus.UNHEALTHY
assert len(health_report.components) == 3
assert health_report.monitoring_version == "1.0.0"


# ------------------------------------------------------------
# Health alerts
# ------------------------------------------------------------

alerts = health_service.alerts_from_health(
    report=health_report,
)

assert len(alerts) == 2

reporting_alert = next(
    alert
    for alert in alerts
    if alert.component == "reporting"
)

platform_alert = next(
    alert
    for alert in alerts
    if alert.component == "platform"
)

assert (
    reporting_alert.severity
    is SeverityLevel.WARNING
)

assert (
    platform_alert.severity
    is SeverityLevel.CRITICAL
)

assert (
    reporting_alert.metric_name
    == "component_availability"
)

assert platform_alert.observed_value == 0.0


# ------------------------------------------------------------
# Missing health check
# ------------------------------------------------------------

missing_configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
    ),
)

missing_service = MonitoringHealthService(
    configuration=missing_configuration,
)

missing_service.register(
    component="orchestration",
    health_check=lambda: True,
)

missing_health = missing_service.check_component(
    component="reporting",
)

assert missing_health.status is HealthStatus.UNKNOWN
assert missing_health.is_available is False
assert missing_health.details["registered"] is False


# ------------------------------------------------------------
# Failed health-check callable
# ------------------------------------------------------------

def failing_health_check():
    raise RuntimeError("Dependency unavailable.")


failure_service = MonitoringHealthService(
    configuration=MonitoringConfiguration(
        enabled_components=("orchestration",),
    )
)

failure_service.register(
    component="orchestration",
    health_check=failing_health_check,
)

failed_health = failure_service.check_component(
    component="orchestration",
)

assert failed_health.status is HealthStatus.UNHEALTHY
assert (
    failed_health.details["exception_type"]
    == "RuntimeError"
)
assert (
    failed_health.details["exception_message"]
    == "Dependency unavailable."
)


# ------------------------------------------------------------
# Unregister health check
# ------------------------------------------------------------

health_service.unregister(
    component="platform",
)

assert health_service.registered_components == (
    "orchestration",
    "reporting",
)


# ------------------------------------------------------------
# Disabled health checks
# ------------------------------------------------------------

disabled_service = MonitoringHealthService(
    configuration=MonitoringConfiguration(
        enabled_components=("orchestration",),
        enable_health_checks=False,
    )
)

try:
    disabled_service.check_component(
        component="orchestration",
    )
except MonitoringHealthCheckError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringHealthCheckError."
    )


# ------------------------------------------------------------
# Disabled alert generation
# ------------------------------------------------------------

disabled_alert_service = MonitoringHealthService(
    configuration=MonitoringConfiguration(
        enabled_components=("platform",),
        enable_alert_generation=False,
    )
)

disabled_alert_report = PlatformHealthReport(
    status=HealthStatus.UNHEALTHY,
    components=(
        ComponentHealth(
            component="platform",
            status=HealthStatus.UNHEALTHY,
            checked_at_utc=datetime.now(timezone.utc),
            response_time_ms=1.0,
            message="Platform unavailable.",
        ),
    ),
    generated_at_utc=datetime.now(timezone.utc),
)

assert (
    disabled_alert_service.alerts_from_health(
        report=disabled_alert_report,
    )
    == ()
)


# ------------------------------------------------------------
# Invalid inputs
# ------------------------------------------------------------

invalid_calls = [
    lambda: MonitoringHealthService(
        configuration="invalid",
    ),
    lambda: health_service.register(
        component="invalid",
        health_check=lambda: True,
    ),
    lambda: health_service.register(
        component="orchestration",
        health_check="invalid",
    ),
    lambda: health_service.check_component(
        component="invalid",
    ),
    lambda: health_service.alerts_from_health(
        report="invalid",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except MonitoringValidationError:
        pass
    else:
        raise AssertionError(
            "Expected MonitoringValidationError."
        )


# ------------------------------------------------------------
# Invalid health-check result
# ------------------------------------------------------------

invalid_result_service = MonitoringHealthService(
    configuration=MonitoringConfiguration(
        enabled_components=("orchestration",),
    )
)

invalid_result_service.register(
    component="orchestration",
    health_check=lambda: {
        "healthy": "yes",
    },
)

try:
    invalid_result_service.check_component(
        component="orchestration",
    )
except MonitoringHealthCheckError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringHealthCheckError."
    )


print(
    "✅ Implementation 23.6 — "
    "Monitoring health validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.7 — Enterprise Monitoring Service Validation
# ============================================================

import importlib
from datetime import datetime, timedelta, timezone

import src.monitoring.service

importlib.reload(src.monitoring.service)

from src.monitoring.configuration import MonitoringConfiguration
from src.monitoring.exceptions import (
    MonitoringServiceError,
    MonitoringValidationError,
)
from src.monitoring.health import MonitoringHealthService
from src.monitoring.metrics import MonitoringMetricsService
from src.monitoring.models import (
    ExecutionRecord,
    ExecutionStatus,
    HealthStatus,
    MetricRecord,
    MetricType,
)
from src.monitoring.service import EnterpriseMonitoringService


started_at_utc = datetime.now(timezone.utc)

configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
)

metrics_service = MonitoringMetricsService(
    configuration=configuration,
)

health_service = MonitoringHealthService(
    configuration=configuration,
)

service = EnterpriseMonitoringService(
    configuration=configuration,
    metrics_service=metrics_service,
    health_service=health_service,
)

assert service.configuration is configuration
assert service.metrics_service is metrics_service
assert service.health_service is health_service


# ------------------------------------------------------------
# Register health checks
# ------------------------------------------------------------

service.register_health_check(
    component="orchestration",
    health_check=lambda: True,
)

service.register_health_check(
    component="reporting",
    health_check=lambda: {
        "healthy": True,
        "degraded": True,
        "message": "Reporting latency is elevated.",
    },
)

service.register_health_check(
    component="platform",
    health_check=lambda: True,
)

assert service.health_service.registered_components == (
    "orchestration",
    "reporting",
    "platform",
)


# ------------------------------------------------------------
# Execution records
# ------------------------------------------------------------

successful_execution = ExecutionRecord(
    execution_id="orchestration-success",
    component="orchestration",
    operation="enterprise_decision",
    status=ExecutionStatus.SUCCEEDED,
    started_at_utc=started_at_utc,
    completed_at_utc=(
        started_at_utc + timedelta(seconds=2)
    ),
    duration_ms=2_000.0,
)

failed_execution = ExecutionRecord(
    execution_id="orchestration-failure",
    component="orchestration",
    operation="enterprise_decision",
    status=ExecutionStatus.FAILED,
    started_at_utc=started_at_utc,
    completed_at_utc=(
        started_at_utc + timedelta(seconds=8)
    ),
    duration_ms=8_000.0,
    message="Enterprise decision failed.",
)


# ------------------------------------------------------------
# Observe executions
# ------------------------------------------------------------

observation = service.observe_executions(
    component="orchestration",
    executions=(
        successful_execution,
        failed_execution,
    ),
)

assert observation["component"] == "orchestration"

assert observation["summary"]["execution_count"] == 2.0
assert observation["summary"]["success_count"] == 1.0
assert observation["summary"]["failure_count"] == 1.0
assert observation["summary"]["success_rate"] == 0.5

assert len(observation["metrics"]) == 6
assert len(observation["alerts"]) == 2

assert len(service.metrics_service.metrics) == 6


# ------------------------------------------------------------
# Record custom metric
# ------------------------------------------------------------

custom_metric = MetricRecord(
    name="component_availability",
    metric_type=MetricType.GAUGE,
    component="platform",
    value=1.0,
    recorded_at_utc=started_at_utc,
    unit="ratio",
)

assert (
    service.record_metric(
        metric=custom_metric,
    )
    is custom_metric
)

assert len(service.metrics_service.metrics) == 7


# ------------------------------------------------------------
# Platform health
# ------------------------------------------------------------

platform_health = service.check_platform_health()

assert platform_health.status is HealthStatus.DEGRADED
assert len(platform_health.components) == 3

health_alerts = service.evaluate_health_alerts(
    report=platform_health,
)

assert len(health_alerts) == 1
assert health_alerts[0].component == "reporting"


# ------------------------------------------------------------
# Unified monitoring snapshot
# ------------------------------------------------------------

service.clear_metrics()

snapshot = service.build_snapshot(
    execution_observations={
        "orchestration": (
            successful_execution,
            failed_execution,
        ),
    },
    include_health=True,
)

assert snapshot["monitoring_version"] == "1.0.0"

assert "orchestration" in snapshot["executions"]

assert (
    snapshot["executions"]["orchestration"]
    ["summary"]["success_rate"]
    == 0.5
)

assert snapshot["health"]["status"] == "DEGRADED"

assert len(snapshot["alerts"]) == 3

assert snapshot["recorded_metric_count"] == 6


# ------------------------------------------------------------
# Snapshot without health
# ------------------------------------------------------------

service.clear_metrics()

snapshot_without_health = service.build_snapshot(
    execution_observations={
        "orchestration": (
            successful_execution,
        ),
    },
    include_health=False,
)

assert snapshot_without_health["health"] is None
assert snapshot_without_health["alerts"] == []
assert snapshot_without_health["recorded_metric_count"] == 3


# ------------------------------------------------------------
# Unregister health check
# ------------------------------------------------------------

service.unregister_health_check(
    component="platform",
)

assert service.health_service.registered_components == (
    "orchestration",
    "reporting",
)


# ------------------------------------------------------------
# Invalid dependencies
# ------------------------------------------------------------

try:
    EnterpriseMonitoringService(
        configuration="invalid",
    )
except MonitoringServiceError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringServiceError."
    )


try:
    EnterpriseMonitoringService(
        configuration=configuration,
        metrics_service="invalid",
    )
except MonitoringServiceError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringServiceError."
    )


try:
    EnterpriseMonitoringService(
        configuration=configuration,
        health_service="invalid",
    )
except MonitoringServiceError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringServiceError."
    )


different_configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
    warning_duration_ms=4_000.0,
)

different_metrics_service = MonitoringMetricsService(
    configuration=different_configuration,
)

try:
    EnterpriseMonitoringService(
        configuration=configuration,
        metrics_service=different_metrics_service,
        health_service=health_service,
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Expected MonitoringValidationError for inconsistent "
        "configuration and metrics service."
    )


# ------------------------------------------------------------
# Invalid requests
# ------------------------------------------------------------

invalid_calls = [
    lambda: service.observe_executions(
        component="invalid",
        executions=(),
    ),
    lambda: service.observe_executions(
        component="orchestration",
        executions=("invalid",),
    ),
    lambda: service.observe_executions(
        component="reporting",
        executions=(successful_execution,),
    ),
    lambda: service.build_snapshot(
        execution_observations="invalid",
    ),
    lambda: service.build_snapshot(
        include_health="yes",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except MonitoringValidationError:
        pass
    else:
        raise AssertionError(
            "Expected MonitoringValidationError."
        )


print(
    "✅ Implementation 23.7 — "
    "Enterprise monitoring service validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 23.8 — Monitoring Package Validation
# ============================================================

import importlib

import src.monitoring

importlib.reload(src.monitoring)

from src.monitoring import (
    COMPONENT_ORCHESTRATION,
    COMPONENT_PLATFORM,
    COMPONENT_REPORTING,
    DEFAULT_MONITORING_VERSION,
    MONITORING_DOMAIN_VERSION,
    ComponentHealth,
    EnterpriseMonitoringService,
    ExecutionRecord,
    ExecutionStatus,
    HealthStatus,
    MetricRecord,
    MetricType,
    MonitoringAlert,
    MonitoringConfiguration,
    MonitoringError,
    MonitoringHealthService,
    MonitoringMetricsError,
    MonitoringMetricsService,
    PlatformHealthReport,
    SeverityLevel,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert MONITORING_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_MONITORING_VERSION == "1.0.0"

assert COMPONENT_ORCHESTRATION == "orchestration"
assert COMPONENT_REPORTING == "reporting"
assert COMPONENT_PLATFORM == "platform"


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    MonitoringMetricsError,
    MonitoringError,
)


# ------------------------------------------------------------
# Models and enums
# ------------------------------------------------------------

assert MetricRecord is not None
assert ExecutionRecord is not None
assert ComponentHealth is not None
assert MonitoringAlert is not None
assert PlatformHealthReport is not None

assert MetricType is not None
assert ExecutionStatus is not None
assert HealthStatus is not None
assert SeverityLevel is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert MonitoringConfiguration is not None
assert MonitoringMetricsService is not None
assert MonitoringHealthService is not None
assert EnterpriseMonitoringService is not None


print(
    "✅ Implementation 23.8 — "
    "Monitoring package validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.1 — Enterprise API Constants Validation
# ============================================================

import importlib

import src.api.constants

importlib.reload(src.api.constants)

from src.api.constants import *


# ------------------------------------------------------------
# Domain
# ------------------------------------------------------------

assert API_DOMAIN_NAME == "enterprise-api"
assert API_DOMAIN_VERSION == "1.0.0"
assert API_VERSION == "v1"
assert API_BASE_PATH == "/api/v1"


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------

assert ENDPOINT_HEALTH == "/api/v1/health"

assert (
    ENDPOINT_PLATFORM_HEALTH
    == "/api/v1/health/platform"
)

assert ENDPOINT_DECISION == "/api/v1/decisions"

assert (
    ENDPOINT_DECISION_REPORT
    == "/api/v1/decisions/report"
)

assert (
    ENDPOINT_MONITORING_SNAPSHOT
    == "/api/v1/monitoring/snapshot"
)

assert SUPPORTED_API_ENDPOINTS == (
    ENDPOINT_HEALTH,
    ENDPOINT_PLATFORM_HEALTH,
    ENDPOINT_DECISION,
    ENDPOINT_DECISION_REPORT,
    ENDPOINT_MONITORING_SNAPSHOT,
)

assert len(SUPPORTED_API_ENDPOINTS) == len(
    set(SUPPORTED_API_ENDPOINTS)
)


# ------------------------------------------------------------
# HTTP methods
# ------------------------------------------------------------

assert SUPPORTED_HTTP_METHODS == (
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
)

assert len(SUPPORTED_HTTP_METHODS) == len(
    set(SUPPORTED_HTTP_METHODS)
)


# ------------------------------------------------------------
# Route names
# ------------------------------------------------------------

assert ROUTE_HEALTH == "health"
assert ROUTE_PLATFORM_HEALTH == "platform_health"

assert ROUTE_DECISION == "enterprise_decision"

assert (
    ROUTE_DECISION_REPORT
    == "enterprise_decision_report"
)

assert (
    ROUTE_MONITORING_SNAPSHOT
    == "monitoring_snapshot"
)

assert len(SUPPORTED_ROUTE_NAMES) == len(
    set(SUPPORTED_ROUTE_NAMES)
)


# ------------------------------------------------------------
# API statuses
# ------------------------------------------------------------

assert SUPPORTED_API_STATUSES == (
    API_STATUS_SUCCESS,
    API_STATUS_ACCEPTED,
    API_STATUS_WARNING,
    API_STATUS_ERROR,
)

assert len(SUPPORTED_API_STATUSES) == len(
    set(SUPPORTED_API_STATUSES)
)


# ------------------------------------------------------------
# HTTP status codes
# ------------------------------------------------------------

assert HTTP_STATUS_OK == 200
assert HTTP_STATUS_CREATED == 201
assert HTTP_STATUS_ACCEPTED == 202
assert HTTP_STATUS_BAD_REQUEST == 400
assert HTTP_STATUS_NOT_FOUND == 404
assert HTTP_STATUS_CONFLICT == 409
assert HTTP_STATUS_UNPROCESSABLE_ENTITY == 422
assert HTTP_STATUS_INTERNAL_SERVER_ERROR == 500
assert HTTP_STATUS_SERVICE_UNAVAILABLE == 503

assert len(SUPPORTED_HTTP_STATUS_CODES) == len(
    set(SUPPORTED_HTTP_STATUS_CODES)
)


# ------------------------------------------------------------
# Content types
# ------------------------------------------------------------

assert DEFAULT_CONTENT_TYPE == CONTENT_TYPE_JSON

assert SUPPORTED_CONTENT_TYPES == (
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_TEXT,
)


# ------------------------------------------------------------
# Limits
# ------------------------------------------------------------

assert MINIMUM_PLANNING_HORIZON_DAYS == 1

assert (
    MAXIMUM_PLANNING_HORIZON_DAYS
    > MINIMUM_PLANNING_HORIZON_DAYS
)

assert MINIMUM_FORECAST_CONFIDENCE == 0.0
assert MAXIMUM_FORECAST_CONFIDENCE == 1.0

assert MAXIMUM_REQUEST_ID_LENGTH > 0
assert MAXIMUM_CORRELATION_ID_LENGTH > 0
assert MAXIMUM_ERROR_MESSAGE_LENGTH > 0


# ------------------------------------------------------------
# Operations
# ------------------------------------------------------------

assert (
    OPERATION_CREATE_DECISION
    in SUPPORTED_API_OPERATIONS
)

assert (
    OPERATION_CREATE_DECISION_REPORT
    in SUPPORTED_API_OPERATIONS
)

assert (
    OPERATION_BUILD_MONITORING_SNAPSHOT
    in SUPPORTED_API_OPERATIONS
)

assert len(SUPPORTED_API_OPERATIONS) == len(
    set(SUPPORTED_API_OPERATIONS)
)


# ------------------------------------------------------------
# Error codes
# ------------------------------------------------------------

assert ERROR_CODE_VALIDATION == "API_VALIDATION_ERROR"

assert (
    ERROR_CODE_ROUTE_NOT_FOUND
    == "API_ROUTE_NOT_FOUND"
)

assert ERROR_CODE_INTERNAL == "API_INTERNAL_ERROR"

assert len(SUPPORTED_API_ERROR_CODES) == len(
    set(SUPPORTED_API_ERROR_CODES)
)


print(
    "✅ Implementation 24.1 — "
    "Enterprise API constants validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.2 — Enterprise API Exceptions Validation
# ============================================================

import importlib

import src.api.exceptions

importlib.reload(src.api.exceptions)

from src.api.exceptions import *


# ------------------------------------------------------------
# Inheritance
# ------------------------------------------------------------

assert issubclass(APIValidationError, APIError)

assert issubclass(APIConfigurationError, APIError)

assert issubclass(APIMapperError, APIError)

assert issubclass(APIRouterError, APIError)

assert issubclass(
    APIRouteNotFoundError,
    APIRouterError,
)

assert issubclass(
    APIMethodNotAllowedError,
    APIRouterError,
)

assert issubclass(APIServiceError, APIError)

assert issubclass(APIInternalError, APIError)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise APIValidationError(
        "Invalid API request."
    )
except APIError as exc:
    assert str(exc) == "Invalid API request."


try:
    raise APIConfigurationError(
        "Invalid API configuration."
    )
except APIError as exc:
    assert str(exc) == "Invalid API configuration."


try:
    raise APIMapperError(
        "API mapping failed."
    )
except APIError as exc:
    assert str(exc) == "API mapping failed."


try:
    raise APIRouteNotFoundError(
        "Route not found."
    )
except APIRouterError as exc:
    assert str(exc) == "Route not found."


try:
    raise APIMethodNotAllowedError(
        "Method not allowed."
    )
except APIRouterError as exc:
    assert str(exc) == "Method not allowed."


try:
    raise APIServiceError(
        "API service failed."
    )
except APIError as exc:
    assert str(exc) == "API service failed."


try:
    raise APIInternalError(
        "Internal API error."
    )
except APIError as exc:
    assert str(exc) == "Internal API error."


print(
    "✅ Implementation 24.2 — "
    "Enterprise API exceptions validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.3 — Enterprise API Models Validation
# ============================================================

import importlib
from datetime import datetime

import src.api.models

importlib.reload(src.api.models)

from src.api.exceptions import APIValidationError
from src.api.models import *


timestamp = datetime.utcnow()


# ------------------------------------------------------------
# Valid request metadata
# ------------------------------------------------------------

request_metadata = APIRequestMetadata(
    request_id="REQ-001",
    correlation_id="CORR-001",
    source="unit-test",
    received_at_utc=timestamp,
)

assert request_metadata.request_id == "REQ-001"


# ------------------------------------------------------------
# Valid response metadata
# ------------------------------------------------------------

response_metadata = APIResponseMetadata(
    request_id="REQ-001",
    correlation_id="CORR-001",
    generated_at_utc=timestamp,
    processing_time_ms=25.5,
)

assert response_metadata.processing_time_ms == 25.5


# ------------------------------------------------------------
# API request
# ------------------------------------------------------------

request = APIRequest(
    operation="health_check",
    payload={"test": True},
    metadata=request_metadata,
)

assert request.operation == "health_check"


# ------------------------------------------------------------
# API response
# ------------------------------------------------------------

response = APIResponse(
    status="SUCCESS",
    http_status=200,
    payload={"ok": True},
    metadata=response_metadata,
)

assert response.http_status == 200


# ------------------------------------------------------------
# Health response
# ------------------------------------------------------------

health = APIHealthResponse(
    healthy=True,
    status="HEALTHY",
    components={
        "forecast": "healthy",
        "planning": "healthy",
    },
    checked_at_utc=timestamp,
)

assert health.healthy is True


# ------------------------------------------------------------
# Route definition
# ------------------------------------------------------------

route = APIRouteDefinition(
    name="health",
    path="/api/v1/health",
    method="GET",
    operation="health_check",
)

assert route.name == "health"


# ------------------------------------------------------------
# Invalid models
# ------------------------------------------------------------

invalid_calls = [

    lambda: APIRequestMetadata(
        request_id="",
        correlation_id="CORR",
        source="unit-test",
        received_at_utc=timestamp,
    ),

    lambda: APIResponseMetadata(
        request_id="REQ",
        correlation_id="CORR",
        generated_at_utc=timestamp,
        processing_time_ms=-1,
    ),

    lambda: APIRequest(
        operation="",
        payload={},
        metadata=request_metadata,
    ),

    lambda: APIResponse(
        status="",
        http_status=200,
        payload={},
        metadata=response_metadata,
    ),

    lambda: APIRouteDefinition(
        name="",
        path="/health",
        method="GET",
        operation="health_check",
    ),
]

for invalid_call in invalid_calls:

    try:
        invalid_call()

    except APIValidationError:
        pass

    else:
        raise AssertionError(
            "Expected APIValidationError."
        )


print(
    "✅ Implementation 24.3 — "
    "Enterprise API models validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.4 — Enterprise API Configuration Validation
# ============================================================

import importlib

import src.api.configuration

importlib.reload(src.api.configuration)

from src.api.configuration import APIConfiguration
from src.api.exceptions import APIConfigurationError


# ------------------------------------------------------------
# Valid configuration
# ------------------------------------------------------------

configuration = APIConfiguration()

assert configuration.api_version == "v1"

assert configuration.base_path == "/api"

assert configuration.default_content_type == "application/json"

assert configuration.request_timeout_seconds == 30

assert configuration.maximum_payload_size_bytes == 10_000_000

assert configuration.enable_health_endpoint

assert configuration.enable_platform_health_endpoint

assert configuration.enable_decision_endpoint

assert configuration.enable_decision_report_endpoint

assert configuration.enable_monitoring_endpoint

assert configuration.validate_requests

assert configuration.generate_metadata

assert configuration.configuration_version == "1.0.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [

    {
        "api_version": "",
    },

    {
        "base_path": "",
    },

    {
        "default_content_type": "",
    },

    {
        "request_timeout_seconds": 0,
    },

    {
        "maximum_payload_size_bytes": 0,
    },

    {
        "enable_health_endpoint": False,
        "enable_platform_health_endpoint": False,
        "enable_decision_endpoint": False,
        "enable_decision_report_endpoint": False,
        "enable_monitoring_endpoint": False,
    },

    {
        "configuration_version": "",
    },

]

for invalid_arguments in invalid_cases:

    try:

        APIConfiguration(
            **invalid_arguments
        )

    except APIConfigurationError:

        pass

    else:

        raise AssertionError(
            f"Expected APIConfigurationError for "
            f"{invalid_arguments}."
        )


print(
    "✅ Implementation 24.4 — "
    "Enterprise API configuration validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.5 — Enterprise API Mapper Validation
# ============================================================

import importlib
from datetime import datetime

import src.api.mapper

importlib.reload(src.api.mapper)

from src.api.exceptions import APIMapperError
from src.api.mapper import EnterpriseAPIMapper
from src.api.models import (
    APIHealthResponse,
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    APIResponseMetadata,
)


timestamp = datetime.utcnow()

mapper = EnterpriseAPIMapper()

request_metadata = APIRequestMetadata(
    request_id="REQ-1",
    correlation_id="CORR-1",
    source="unit-test",
    received_at_utc=timestamp,
)

response_metadata = APIResponseMetadata(
    request_id="REQ-1",
    correlation_id="CORR-1",
    generated_at_utc=timestamp,
    processing_time_ms=10.5,
)

request = APIRequest(
    operation="decision",
    payload={
        "forecast": 120
    },
    metadata=request_metadata,
)

response = APIResponse(
    status="SUCCESS",
    http_status=200,
    payload={
        "recommendation": "OVERTIME"
    },
    metadata=response_metadata,
)

health = APIHealthResponse(
    healthy=True,
    status="HEALTHY",
    components={
        "forecast": "healthy",
        "planning": "healthy",
    },
    checked_at_utc=timestamp,
)

# ------------------------------------------------------------
# Request
# ------------------------------------------------------------

payload = mapper.request_payload(request)

assert payload["forecast"] == 120


# ------------------------------------------------------------
# Response
# ------------------------------------------------------------

payload = mapper.response_payload(response)

assert payload["recommendation"] == "OVERTIME"


metadata = mapper.response_metadata(response)

assert metadata["request_id"] == "REQ-1"


# ------------------------------------------------------------
# Health
# ------------------------------------------------------------

health_payload = mapper.health_payload(
    health
)

assert health_payload["healthy"] is True

assert (
    health_payload["status"]
    == "HEALTHY"
)

assert (
    health_payload["components"]["forecast"]
    == "healthy"
)


# ------------------------------------------------------------
# Invalid calls
# ------------------------------------------------------------

invalid_calls = [

    lambda: mapper.request_payload(
        "invalid"
    ),

    lambda: mapper.response_payload(
        "invalid"
    ),

    lambda: mapper.response_metadata(
        "invalid"
    ),

    lambda: mapper.health_payload(
        "invalid"
    ),
]

for invalid_call in invalid_calls:

    try:

        invalid_call()

    except APIMapperError:

        pass

    else:

        raise AssertionError(
            "Expected APIMapperError."
        )


print(
    "✅ Implementation 24.5 — "
    "Enterprise API mapper validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.6 — Enterprise API Router Validation
# ============================================================

import importlib
from datetime import datetime, timezone

import src.api.router

importlib.reload(src.api.router)

from src.api.configuration import APIConfiguration
from src.api.constants import (
    API_STATUS_ERROR,
    API_STATUS_SUCCESS,
    ERROR_CODE_INTERNAL,
    ERROR_CODE_METHOD_NOT_ALLOWED,
    ERROR_CODE_ROUTE_NOT_FOUND,
    ERROR_CODE_VALIDATION,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
)
from src.api.exceptions import (
    APIRouteNotFoundError,
    APIRouterError,
    APIValidationError,
)
from src.api.models import (
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    APIResponseMetadata,
)
from src.api.router import EnterpriseAPIRouter


timestamp = datetime.now(timezone.utc)

configuration = APIConfiguration()

router = EnterpriseAPIRouter(
    configuration=configuration,
)

assert router.configuration is configuration

assert router.route_names == (
    ROUTE_HEALTH,
    ROUTE_PLATFORM_HEALTH,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_MONITORING_SNAPSHOT,
)

assert len(router.routes) == 5
assert router.registered_handler_names == ()


# ------------------------------------------------------------
# Route resolution
# ------------------------------------------------------------

health_route = router.resolve(
    path="/api/v1/health",
    method="GET",
)

assert health_route.name == ROUTE_HEALTH
assert health_route.operation == "health_check"

decision_route = router.resolve(
    path="/api/v1/decisions/",
    method="post",
)

assert decision_route.name == ROUTE_DECISION
assert decision_route.method == "POST"


# ------------------------------------------------------------
# Register valid handlers
# ------------------------------------------------------------

def health_handler(
    request: APIRequest,
) -> APIResponse:
    return APIResponse(
        status=API_STATUS_SUCCESS,
        http_status=HTTP_STATUS_OK,
        payload={
            "healthy": True,
            "status": "HEALTHY",
        },
        metadata=APIResponseMetadata(
            request_id=request.metadata.request_id,
            correlation_id=(
                request.metadata.correlation_id
            ),
            generated_at_utc=datetime.now(
                timezone.utc
            ),
            processing_time_ms=1.0,
        ),
    )


def decision_handler(
    request: APIRequest,
) -> APIResponse:
    return APIResponse(
        status=API_STATUS_SUCCESS,
        http_status=HTTP_STATUS_OK,
        payload={
            "decision": "OVERTIME",
        },
        metadata=APIResponseMetadata(
            request_id=request.metadata.request_id,
            correlation_id=(
                request.metadata.correlation_id
            ),
            generated_at_utc=datetime.now(
                timezone.utc
            ),
            processing_time_ms=2.0,
        ),
    )


router.register_handler(
    route_name=ROUTE_HEALTH,
    handler=health_handler,
)

router.register_handler(
    route_name=ROUTE_DECISION,
    handler=decision_handler,
)

assert router.registered_handler_names == (
    ROUTE_HEALTH,
    ROUTE_DECISION,
)


# ------------------------------------------------------------
# Successful health dispatch
# ------------------------------------------------------------

health_request = APIRequest(
    operation="health_check",
    payload={},
    metadata=APIRequestMetadata(
        request_id="REQ-HEALTH-001",
        correlation_id="CORR-HEALTH-001",
        source="validation",
        received_at_utc=timestamp,
    ),
)

health_response = router.dispatch(
    path="/api/v1/health",
    method="GET",
    request=health_request,
)

assert health_response.status == API_STATUS_SUCCESS
assert health_response.http_status == HTTP_STATUS_OK
assert health_response.payload["healthy"] is True

assert (
    health_response.metadata.request_id
    == "REQ-HEALTH-001"
)

assert (
    health_response.metadata.correlation_id
    == "CORR-HEALTH-001"
)


# ------------------------------------------------------------
# Successful decision dispatch
# ------------------------------------------------------------

decision_request = APIRequest(
    operation="create_enterprise_decision",
    payload={
        "expected_order_lines": 48_000.0,
    },
    metadata=APIRequestMetadata(
        request_id="REQ-DECISION-001",
        correlation_id="CORR-DECISION-001",
        source="validation",
        received_at_utc=timestamp,
    ),
)

decision_response = router.dispatch(
    path="/api/v1/decisions",
    method="POST",
    request=decision_request,
)

assert decision_response.status == API_STATUS_SUCCESS
assert decision_response.http_status == HTTP_STATUS_OK
assert decision_response.payload["decision"] == "OVERTIME"


# ------------------------------------------------------------
# Route not found response
# ------------------------------------------------------------

not_found_response = router.dispatch(
    path="/api/v1/unknown",
    method="GET",
    request=health_request,
)

assert not_found_response.status == API_STATUS_ERROR
assert (
    not_found_response.http_status
    == HTTP_STATUS_NOT_FOUND
)

assert (
    not_found_response.payload["error"]["code"]
    == ERROR_CODE_ROUTE_NOT_FOUND
)


# ------------------------------------------------------------
# Method not allowed response
# ------------------------------------------------------------

method_response = router.dispatch(
    path="/api/v1/health",
    method="POST",
    request=health_request,
)

assert method_response.status == API_STATUS_ERROR
assert (
    method_response.http_status
    == HTTP_STATUS_BAD_REQUEST
)

assert (
    method_response.payload["error"]["code"]
    == ERROR_CODE_METHOD_NOT_ALLOWED
)


# ------------------------------------------------------------
# Operation mismatch response
# ------------------------------------------------------------

mismatch_request = APIRequest(
    operation="create_enterprise_decision",
    payload={},
    metadata=APIRequestMetadata(
        request_id="REQ-MISMATCH",
        correlation_id="CORR-MISMATCH",
        source="validation",
        received_at_utc=timestamp,
    ),
)

mismatch_response = router.dispatch(
    path="/api/v1/health",
    method="GET",
    request=mismatch_request,
)

assert mismatch_response.status == API_STATUS_ERROR
assert (
    mismatch_response.http_status
    == HTTP_STATUS_BAD_REQUEST
)

assert (
    mismatch_response.payload["error"]["code"]
    == ERROR_CODE_VALIDATION
)


# ------------------------------------------------------------
# Missing handler response
# ------------------------------------------------------------

platform_request = APIRequest(
    operation="platform_health",
    payload={},
    metadata=APIRequestMetadata(
        request_id="REQ-PLATFORM",
        correlation_id="CORR-PLATFORM",
        source="validation",
        received_at_utc=timestamp,
    ),
)

missing_handler_response = router.dispatch(
    path="/api/v1/health/platform",
    method="GET",
    request=platform_request,
)

assert missing_handler_response.status == API_STATUS_ERROR

assert (
    missing_handler_response.http_status
    == HTTP_STATUS_INTERNAL_SERVER_ERROR
)

assert (
    missing_handler_response.payload["error"]["code"]
    == ERROR_CODE_INTERNAL
)


# ------------------------------------------------------------
# Invalid handler response
# ------------------------------------------------------------

def invalid_handler(
    request: APIRequest,
):
    return {
        "invalid": True,
    }


router.register_handler(
    route_name=ROUTE_PLATFORM_HEALTH,
    handler=invalid_handler,
)

invalid_handler_response = router.dispatch(
    path="/api/v1/health/platform",
    method="GET",
    request=platform_request,
)

assert (
    invalid_handler_response.http_status
    == HTTP_STATUS_INTERNAL_SERVER_ERROR
)

assert (
    invalid_handler_response.payload["error"]["code"]
    == ERROR_CODE_INTERNAL
)


# ------------------------------------------------------------
# Replace and unregister handler
# ------------------------------------------------------------

router.register_handler(
    route_name=ROUTE_HEALTH,
    handler=health_handler,
    replace=True,
)

router.unregister_handler(
    route_name=ROUTE_DECISION,
)

assert ROUTE_DECISION not in (
    router.registered_handler_names
)


# ------------------------------------------------------------
# Disabled route configuration
# ------------------------------------------------------------

limited_router = EnterpriseAPIRouter(
    configuration=APIConfiguration(
        enable_health_endpoint=True,
        enable_platform_health_endpoint=False,
        enable_decision_endpoint=False,
        enable_decision_report_endpoint=False,
        enable_monitoring_endpoint=False,
    ),
)

assert limited_router.route_names == (
    ROUTE_HEALTH,
)

try:
    limited_router.register_handler(
        route_name=ROUTE_DECISION,
        handler=decision_handler,
    )
except APIRouteNotFoundError:
    pass
else:
    raise AssertionError(
        "Expected APIRouteNotFoundError."
    )


# ------------------------------------------------------------
# Invalid construction and registration
# ------------------------------------------------------------

invalid_calls = [
    lambda: EnterpriseAPIRouter(
        configuration="invalid",
    ),
    lambda: router.register_handler(
        route_name="",
        handler=health_handler,
    ),
    lambda: router.register_handler(
        route_name=ROUTE_HEALTH,
        handler="invalid",
        replace=True,
    ),
    lambda: router.register_handler(
        route_name=ROUTE_HEALTH,
        handler=health_handler,
        replace="yes",
    ),
    lambda: router.resolve(
        path="api/v1/health",
        method="GET",
    ),
    lambda: router.resolve(
        path="/api/v1/health",
        method="",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except (
        APIRouterError,
        APIValidationError,
    ):
        pass
    else:
        raise AssertionError(
            "Expected API router exception."
        )


# ------------------------------------------------------------
# Invalid request type
# ------------------------------------------------------------

try:
    router.dispatch(
        path="/api/v1/health",
        method="GET",
        request="invalid",
    )
except APIValidationError:
    pass
else:
    raise AssertionError(
        "Expected APIValidationError."
    )


print(
    "✅ Implementation 24.6 — "
    "Enterprise API router validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.7 — Enterprise API Service Validation
# ============================================================

import importlib
from datetime import date, datetime, timezone

import src.api.service

importlib.reload(src.api.service)

from src.api.configuration import APIConfiguration
from src.api.constants import (
    API_STATUS_ERROR,
    API_STATUS_SUCCESS,
    ERROR_CODE_VALIDATION,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_OK,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
)
from src.api.exceptions import (
    APIServiceError,
    APIValidationError,
)
from src.api.mapper import EnterpriseAPIMapper
from src.api.models import (
    APIRequest,
    APIRequestMetadata,
)
from src.api.router import EnterpriseAPIRouter
from src.api.service import EnterpriseAPIService
from src.monitoring.configuration import (
    MonitoringConfiguration,
)
from src.monitoring.health import MonitoringHealthService
from src.monitoring.metrics import MonitoringMetricsService
from src.monitoring.service import EnterpriseMonitoringService
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


timestamp = datetime.now(timezone.utc)

api_configuration = APIConfiguration()

api_router = EnterpriseAPIRouter(
    configuration=api_configuration,
)

api_mapper = EnterpriseAPIMapper()


# ------------------------------------------------------------
# Monitoring dependency with deterministic health checks
# ------------------------------------------------------------

monitoring_configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
)

monitoring_metrics_service = MonitoringMetricsService(
    configuration=monitoring_configuration,
)

monitoring_health_service = MonitoringHealthService(
    configuration=monitoring_configuration,
)

monitoring_service = EnterpriseMonitoringService(
    configuration=monitoring_configuration,
    metrics_service=monitoring_metrics_service,
    health_service=monitoring_health_service,
)

monitoring_service.register_health_check(
    component="orchestration",
    health_check=lambda: True,
)

monitoring_service.register_health_check(
    component="reporting",
    health_check=lambda: True,
)

monitoring_service.register_health_check(
    component="platform",
    health_check=lambda: True,
)


# ------------------------------------------------------------
# Construct API service
# ------------------------------------------------------------

service = EnterpriseAPIService(
    configuration=api_configuration,
    router=api_router,
    mapper=api_mapper,
    orchestration_service=(
        EnterpriseDecisionOrchestrationService()
    ),
    reporting_service=(
        EnterpriseDecisionReportingService()
    ),
    monitoring_service=monitoring_service,
)

assert service.configuration is api_configuration
assert service.router is api_router
assert service.mapper is api_mapper
assert service.monitoring_service is monitoring_service

assert service.router.registered_handler_names == (
    ROUTE_HEALTH,
    ROUTE_PLATFORM_HEALTH,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_MONITORING_SNAPSHOT,
)


# ------------------------------------------------------------
# Request helper
# ------------------------------------------------------------

def build_request(
    *,
    operation,
    payload,
    request_id,
):
    return APIRequest(
        operation=operation,
        payload=payload,
        metadata=APIRequestMetadata(
            request_id=request_id,
            correlation_id=f"CORR-{request_id}",
            source="implementation-24.7-validation",
            received_at_utc=timestamp,
        ),
    )


# ------------------------------------------------------------
# Health endpoint
# ------------------------------------------------------------

health_response = service.handle(
    path="/api/v1/health",
    method="GET",
    request=build_request(
        operation="health_check",
        payload={},
        request_id="HEALTH-001",
    ),
)

assert health_response.status == API_STATUS_SUCCESS
assert health_response.http_status == HTTP_STATUS_OK
assert health_response.payload["healthy"] is True
assert health_response.payload["service"] == "enterprise-api"


# ------------------------------------------------------------
# Platform health endpoint
# ------------------------------------------------------------

platform_health_response = service.handle(
    path="/api/v1/health/platform",
    method="GET",
    request=build_request(
        operation="platform_health",
        payload={},
        request_id="PLATFORM-001",
    ),
)

assert platform_health_response.status == API_STATUS_SUCCESS
assert platform_health_response.http_status == HTTP_STATUS_OK
assert platform_health_response.payload["status"] == "HEALTHY"
assert platform_health_response.payload["healthy"] is True
assert len(platform_health_response.payload["components"]) == 3


# ------------------------------------------------------------
# Decision payload
# ------------------------------------------------------------

decision_payload = {
    "planning_date": date.today().isoformat(),
    "expected_order_lines": 48_000.0,
    "available_associates": 40,
    "productivity_lines_per_hour": 120.0,
    "scheduled_hours": 10.0,
    "forecast_confidence": 0.92,
    "recurring_shortage_days": 18,
    "recurring_surplus_days": 0,
    "overtime_dependency_days": 15,
    "planning_horizon_days": 30,
}


# ------------------------------------------------------------
# Enterprise decision endpoint
# ------------------------------------------------------------

decision_response = service.handle(
    path="/api/v1/decisions",
    method="POST",
    request=build_request(
        operation="create_enterprise_decision",
        payload=decision_payload,
        request_id="DECISION-001",
    ),
)

assert decision_response.status == API_STATUS_SUCCESS
assert decision_response.http_status == HTTP_STATUS_OK

assert decision_response.payload["available_associates"] == 40
assert decision_response.payload["required_associates"] == 47
assert decision_response.payload["associate_gap"] == 7

assert (
    decision_response.payload["optimization_action"]
    == "FULL_TIME_HIRING"
)

assert (
    decision_response.payload["workflow_status"]
    == "COMPLETED"
)


# ------------------------------------------------------------
# Decision report endpoint
# ------------------------------------------------------------

report_response = service.handle(
    path="/api/v1/decisions/report",
    method="POST",
    request=build_request(
        operation="create_enterprise_decision_report",
        payload={
            "decision": decision_payload,
            "report": {
                "report_type": "executive",
                "report_format": "dict",
                "title": "Executive Workforce Decision Brief",
                "include_metadata": True,
                "include_rationale": True,
            },
        },
        request_id="REPORT-001",
    ),
)

assert report_response.status == API_STATUS_SUCCESS
assert report_response.http_status == HTTP_STATUS_OK

assert report_response.payload["report_format"] == "dict"

assert (
    report_response.payload["decision"]["associate_gap"]
    == 7
)

assert (
    report_response.payload["report"]["report_type"]
    == "executive"
)

assert (
    report_response.payload["report"]["status"]
    == "SUCCESS"
)


# ------------------------------------------------------------
# Monitoring snapshot endpoint
# ------------------------------------------------------------

snapshot_response = service.handle(
    path="/api/v1/monitoring/snapshot",
    method="POST",
    request=build_request(
        operation="build_monitoring_snapshot",
        payload={
            "include_health": True,
        },
        request_id="MONITORING-001",
    ),
)

assert snapshot_response.status == API_STATUS_SUCCESS
assert snapshot_response.http_status == HTTP_STATUS_OK

assert snapshot_response.payload["monitoring_version"] == "1.0.0"
assert snapshot_response.payload["health"]["status"] == "HEALTHY"
assert snapshot_response.payload["executions"] == {}


# ------------------------------------------------------------
# Invalid decision payload
# ------------------------------------------------------------

invalid_decision_response = service.handle(
    path="/api/v1/decisions",
    method="POST",
    request=build_request(
        operation="create_enterprise_decision",
        payload={
            "planning_date": date.today().isoformat(),
        },
        request_id="DECISION-INVALID",
    ),
)

assert invalid_decision_response.status == API_STATUS_ERROR

assert (
    invalid_decision_response.http_status
    == HTTP_STATUS_BAD_REQUEST
)

assert (
    invalid_decision_response.payload["error"]["code"]
    == ERROR_CODE_VALIDATION
)


# ------------------------------------------------------------
# Invalid report payload
# ------------------------------------------------------------

invalid_report_response = service.handle(
    path="/api/v1/decisions/report",
    method="POST",
    request=build_request(
        operation="create_enterprise_decision_report",
        payload={
            "decision": decision_payload,
            "report": {
                "report_type": "invalid",
                "report_format": "dict",
            },
        },
        request_id="REPORT-INVALID",
    ),
)

assert invalid_report_response.status == API_STATUS_ERROR
assert (
    invalid_report_response.http_status
    == HTTP_STATUS_BAD_REQUEST
)


# ------------------------------------------------------------
# Invalid monitoring payload
# ------------------------------------------------------------

invalid_monitoring_response = service.handle(
    path="/api/v1/monitoring/snapshot",
    method="POST",
    request=build_request(
        operation="build_monitoring_snapshot",
        payload={
            "include_health": "yes",
        },
        request_id="MONITORING-INVALID",
    ),
)

assert invalid_monitoring_response.status == API_STATUS_ERROR
assert (
    invalid_monitoring_response.http_status
    == HTTP_STATUS_BAD_REQUEST
)


# ------------------------------------------------------------
# Invalid dependencies
# ------------------------------------------------------------

invalid_constructors = [
    lambda: EnterpriseAPIService(
        configuration="invalid",
    ),
    lambda: EnterpriseAPIService(
        configuration=api_configuration,
        router="invalid",
    ),
    lambda: EnterpriseAPIService(
        configuration=api_configuration,
        router=EnterpriseAPIRouter(
            configuration=api_configuration,
        ),
        mapper="invalid",
    ),
    lambda: EnterpriseAPIService(
        orchestration_service="invalid",
    ),
    lambda: EnterpriseAPIService(
        reporting_service="invalid",
    ),
    lambda: EnterpriseAPIService(
        monitoring_service="invalid",
    ),
]

for invalid_constructor in invalid_constructors:
    try:
        invalid_constructor()
    except APIServiceError:
        pass
    else:
        raise AssertionError(
            "Expected APIServiceError."
        )


# ------------------------------------------------------------
# Configuration mismatch
# ------------------------------------------------------------

different_api_configuration = APIConfiguration(
    request_timeout_seconds=45,
)

different_router = EnterpriseAPIRouter(
    configuration=different_api_configuration,
)

try:
    EnterpriseAPIService(
        configuration=api_configuration,
        router=different_router,
    )
except APIValidationError:
    pass
else:
    raise AssertionError(
        "Expected APIValidationError for inconsistent "
        "configuration and router."
    )


print(
    "✅ Implementation 24.7 — "
    "Enterprise API service validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 24.8 — Enterprise API Package Validation
# ============================================================

import importlib

import src.api

importlib.reload(src.api)

from src.api import (
    API_BASE_PATH,
    API_DOMAIN_VERSION,
    API_VERSION,
    ENDPOINT_DECISION,
    ENDPOINT_HEALTH,
    APIConfiguration,
    APIError,
    APIHealthResponse,
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    APIResponseMetadata,
    APIValidationError,
    APIRouteDefinition,
    EnterpriseAPIMapper,
    EnterpriseAPIRouter,
    EnterpriseAPIService,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert API_DOMAIN_VERSION == "1.0.0"
assert API_VERSION == "v1"
assert API_BASE_PATH == "/api/v1"
assert ENDPOINT_HEALTH == "/api/v1/health"
assert ENDPOINT_DECISION == "/api/v1/decisions"


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    APIValidationError,
    APIError,
)


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

assert APIRequestMetadata is not None
assert APIResponseMetadata is not None
assert APIRequest is not None
assert APIResponse is not None
assert APIHealthResponse is not None
assert APIRouteDefinition is not None


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert APIConfiguration is not None
assert EnterpriseAPIMapper is not None
assert EnterpriseAPIRouter is not None
assert EnterpriseAPIService is not None


print(
    "✅ Implementation 24.8 — "
    "Enterprise API package validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.1 — Enterprise Application Constants Validation
# ============================================================

import importlib

import src.application.constants

importlib.reload(src.application.constants)

from src.application.constants import *

# ------------------------------------------------------------
# Domain
# ------------------------------------------------------------

assert APPLICATION_DOMAIN_NAME == "application"
assert APPLICATION_DOMAIN_VERSION == "1.0.0"

# ------------------------------------------------------------
# Environments
# ------------------------------------------------------------

assert ENVIRONMENT_DEVELOPMENT == "development"
assert ENVIRONMENT_TEST == "test"
assert ENVIRONMENT_PRODUCTION == "production"

assert len(SUPPORTED_ENVIRONMENTS) == len(
    set(SUPPORTED_ENVIRONMENTS)
)

# ------------------------------------------------------------
# Bootstrap stages
# ------------------------------------------------------------

assert BOOTSTRAP_CONFIGURATION == "configuration"
assert BOOTSTRAP_DEPENDENCIES == "dependencies"
assert BOOTSTRAP_SERVICES == "services"
assert BOOTSTRAP_API == "api"
assert BOOTSTRAP_COMPLETE == "complete"

assert BOOTSTRAP_SEQUENCE == (
    BOOTSTRAP_CONFIGURATION,
    BOOTSTRAP_DEPENDENCIES,
    BOOTSTRAP_SERVICES,
    BOOTSTRAP_API,
    BOOTSTRAP_COMPLETE,
)

# ------------------------------------------------------------
# Container registrations
# ------------------------------------------------------------

assert SERVICE_FORECAST == "forecast"
assert SERVICE_PLANNING == "planning"
assert SERVICE_OPTIMIZATION == "optimization"
assert SERVICE_ORCHESTRATION == "orchestration"
assert SERVICE_REPORTING == "reporting"
assert SERVICE_MONITORING == "monitoring"
assert SERVICE_API == "api"

assert len(SUPPORTED_SERVICES) == len(
    set(SUPPORTED_SERVICES)
)

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

assert DEFAULT_CONFIGURATION_VERSION == "1.0.0"

print(
    "✅ Implementation 25.1 — "
    "Enterprise application constants validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.2 — Enterprise Application Exceptions Validation
# ============================================================

import importlib

import src.application.exceptions

importlib.reload(src.application.exceptions)

from src.application.exceptions import (
    ApplicationBootstrapError,
    ApplicationConfigurationError,
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationError,
    ApplicationFactoryError,
    ApplicationLifecycleError,
    ApplicationValidationError,
)


# ------------------------------------------------------------
# Exception hierarchy
# ------------------------------------------------------------

assert issubclass(
    ApplicationValidationError,
    ApplicationError,
)

assert issubclass(
    ApplicationConfigurationError,
    ApplicationError,
)

assert issubclass(
    ApplicationContainerError,
    ApplicationError,
)

assert issubclass(
    ApplicationDependencyError,
    ApplicationError,
)

assert issubclass(
    ApplicationFactoryError,
    ApplicationError,
)

assert issubclass(
    ApplicationBootstrapError,
    ApplicationError,
)

assert issubclass(
    ApplicationLifecycleError,
    ApplicationError,
)


# ------------------------------------------------------------
# Exception messages
# ------------------------------------------------------------

try:
    raise ApplicationValidationError(
        "Application validation failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Application validation failed."


try:
    raise ApplicationConfigurationError(
        "Application configuration failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Application configuration failed."


try:
    raise ApplicationContainerError(
        "Container registration failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Container registration failed."


try:
    raise ApplicationDependencyError(
        "Dependency resolution failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Dependency resolution failed."


try:
    raise ApplicationFactoryError(
        "Factory creation failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Factory creation failed."


try:
    raise ApplicationBootstrapError(
        "Bootstrap failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Bootstrap failed."


try:
    raise ApplicationLifecycleError(
        "Lifecycle operation failed."
    )
except ApplicationError as exc:
    assert str(exc) == "Lifecycle operation failed."


print(
    "✅ Implementation 25.2 — "
    "Enterprise application exceptions validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.3 — Enterprise Application Models Validation
# ============================================================

import importlib
from datetime import datetime, timedelta, timezone

import src.application.models

importlib.reload(src.application.models)

from src.application.exceptions import (
    ApplicationValidationError,
)
from src.application.models import (
    ApplicationBootstrapResult,
    ApplicationContext,
    ApplicationDescriptor,
    ApplicationEnvironment,
    ApplicationStatus,
    BootstrapEvent,
    BootstrapStage,
    ServiceRegistration,
)


started_at_utc = datetime.now(timezone.utc)

configuration_completed_at = (
    started_at_utc + timedelta(milliseconds=10)
)

dependencies_completed_at = (
    configuration_completed_at
    + timedelta(milliseconds=10)
)

services_completed_at = (
    dependencies_completed_at
    + timedelta(milliseconds=10)
)

api_completed_at = (
    services_completed_at
    + timedelta(milliseconds=10)
)

bootstrap_completed_at = (
    api_completed_at
    + timedelta(milliseconds=10)
)


# ------------------------------------------------------------
# Service registration
# ------------------------------------------------------------

class TestService:
    pass


test_service = TestService()

registration = ServiceRegistration(
    name="api",
    instance=test_service,
    registered_at_utc=started_at_utc,
    metadata={
        "version": "1.0.0",
    },
)

assert registration.name == "api"
assert registration.instance is test_service

registration_payload = registration.as_dict()

assert registration_payload["name"] == "api"
assert registration_payload["instance_type"] == "TestService"
assert registration_payload["metadata"]["version"] == "1.0.0"


# ------------------------------------------------------------
# Bootstrap events
# ------------------------------------------------------------

configuration_event = BootstrapEvent(
    stage=BootstrapStage.CONFIGURATION,
    started_at_utc=started_at_utc,
    completed_at_utc=configuration_completed_at,
    succeeded=True,
    message="Configuration loaded.",
)

dependencies_event = BootstrapEvent(
    stage=BootstrapStage.DEPENDENCIES,
    started_at_utc=configuration_completed_at,
    completed_at_utc=dependencies_completed_at,
    succeeded=True,
    message="Dependencies constructed.",
)

services_event = BootstrapEvent(
    stage=BootstrapStage.SERVICES,
    started_at_utc=dependencies_completed_at,
    completed_at_utc=services_completed_at,
    succeeded=True,
    message="Services registered.",
)

api_event = BootstrapEvent(
    stage=BootstrapStage.API,
    started_at_utc=services_completed_at,
    completed_at_utc=api_completed_at,
    succeeded=True,
    message="API service constructed.",
)

complete_event = BootstrapEvent(
    stage=BootstrapStage.COMPLETE,
    started_at_utc=api_completed_at,
    completed_at_utc=bootstrap_completed_at,
    succeeded=True,
    message="Application bootstrap completed.",
)

assert configuration_event.stage is BootstrapStage.CONFIGURATION
assert configuration_event.duration_ms == 10.0

event_payload = complete_event.as_dict()

assert event_payload["stage"] == "complete"
assert event_payload["succeeded"] is True
assert event_payload["duration_ms"] == 10.0


# ------------------------------------------------------------
# Application descriptor
# ------------------------------------------------------------

descriptor = ApplicationDescriptor(
    application_name="AI Workforce Capacity Planning Platform",
    application_version="3.0.0",
    environment=ApplicationEnvironment.DEVELOPMENT,
    status=ApplicationStatus.READY,
    created_at_utc=started_at_utc,
)

assert (
    descriptor.environment
    is ApplicationEnvironment.DEVELOPMENT
)

assert descriptor.status is ApplicationStatus.READY

descriptor_payload = descriptor.as_dict()

assert descriptor_payload["environment"] == "development"
assert descriptor_payload["status"] == "READY"


# ------------------------------------------------------------
# Bootstrap result
# ------------------------------------------------------------

bootstrap_result = ApplicationBootstrapResult(
    descriptor=descriptor,
    completed_stage=BootstrapStage.COMPLETE,
    events=(
        configuration_event,
        dependencies_event,
        services_event,
        api_event,
        complete_event,
    ),
    started_at_utc=started_at_utc,
    completed_at_utc=bootstrap_completed_at,
)

assert bootstrap_result.succeeded is True
assert bootstrap_result.duration_ms == 50.0
assert len(bootstrap_result.events) == 5

bootstrap_payload = bootstrap_result.as_dict()

assert bootstrap_payload["completed_stage"] == "complete"
assert bootstrap_payload["succeeded"] is True
assert bootstrap_payload["duration_ms"] == 50.0


# ------------------------------------------------------------
# Application context
# ------------------------------------------------------------

context = ApplicationContext(
    descriptor=descriptor,
    services=(registration,),
    bootstrap_result=bootstrap_result,
    metadata={
        "configuration_version": "1.0.0",
    },
)

assert context.descriptor is descriptor

assert (
    context.get_service(name="api")
    is test_service
)

context_payload = context.as_dict()

assert context_payload["descriptor"]["status"] == "READY"
assert context_payload["services"][0]["name"] == "api"
assert (
    context_payload["metadata"]["configuration_version"]
    == "1.0.0"
)


# ------------------------------------------------------------
# Failed bootstrap result
# ------------------------------------------------------------

failed_descriptor = ApplicationDescriptor(
    application_name="AI Workforce Capacity Planning Platform",
    application_version="3.0.0",
    environment=ApplicationEnvironment.TEST,
    status=ApplicationStatus.FAILED,
    created_at_utc=started_at_utc,
)

failed_event = BootstrapEvent(
    stage=BootstrapStage.DEPENDENCIES,
    started_at_utc=configuration_completed_at,
    completed_at_utc=dependencies_completed_at,
    succeeded=False,
    message="Dependency construction failed.",
)

failed_result = ApplicationBootstrapResult(
    descriptor=failed_descriptor,
    completed_stage=BootstrapStage.DEPENDENCIES,
    events=(
        configuration_event,
        failed_event,
    ),
    started_at_utc=started_at_utc,
    completed_at_utc=dependencies_completed_at,
    error_message="Dependency construction failed.",
)

assert failed_result.succeeded is False
assert failed_result.error_message != ""


# ------------------------------------------------------------
# Invalid models
# ------------------------------------------------------------

invalid_calls = [
    lambda: ServiceRegistration(
        name="invalid",
        instance=test_service,
        registered_at_utc=started_at_utc,
    ),
    lambda: ServiceRegistration(
        name="api",
        instance=None,
        registered_at_utc=started_at_utc,
    ),
    lambda: BootstrapEvent(
        stage="configuration",
        started_at_utc=started_at_utc,
        completed_at_utc=configuration_completed_at,
        succeeded=True,
        message="Invalid stage.",
    ),
    lambda: BootstrapEvent(
        stage=BootstrapStage.CONFIGURATION,
        started_at_utc=configuration_completed_at,
        completed_at_utc=started_at_utc,
        succeeded=True,
        message="Invalid timestamps.",
    ),
    lambda: ApplicationDescriptor(
        application_name="",
        application_version="3.0.0",
        environment=ApplicationEnvironment.TEST,
        status=ApplicationStatus.CREATED,
        created_at_utc=started_at_utc,
    ),
    lambda: ApplicationBootstrapResult(
        descriptor=descriptor,
        completed_stage=BootstrapStage.COMPLETE,
        events=(
            dependencies_event,
            configuration_event,
        ),
        started_at_utc=started_at_utc,
        completed_at_utc=bootstrap_completed_at,
    ),
    lambda: ApplicationBootstrapResult(
        descriptor=descriptor,
        completed_stage=BootstrapStage.API,
        events=(
            configuration_event,
            dependencies_event,
            services_event,
            api_event,
        ),
        started_at_utc=started_at_utc,
        completed_at_utc=api_completed_at,
    ),
    lambda: ApplicationContext(
        descriptor=failed_descriptor,
        services=(registration,),
        bootstrap_result=failed_result,
    ),
    lambda: ApplicationContext(
        descriptor=descriptor,
        services=(
            registration,
            registration,
        ),
        bootstrap_result=bootstrap_result,
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ApplicationValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ApplicationValidationError."
        )


# ------------------------------------------------------------
# Missing context service
# ------------------------------------------------------------

try:
    context.get_service(
        name="monitoring",
    )
except ApplicationValidationError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationValidationError."
    )


print(
    "✅ Implementation 25.3 — "
    "Enterprise application models validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.4 — Enterprise Application Configuration Validation
# ============================================================

import importlib

import src.application.configuration

importlib.reload(src.application.configuration)

from src.api.configuration import APIConfiguration
from src.application.configuration import (
    ApplicationConfiguration,
    DEFAULT_APPLICATION_NAME,
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_REQUIRED_SERVICES,
)
from src.application.exceptions import (
    ApplicationConfigurationError,
)
from src.application.models import (
    ApplicationEnvironment,
)
from src.monitoring.configuration import (
    MonitoringConfiguration,
)
from src.reporting.configuration import (
    ReportingConfiguration,
)


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = ApplicationConfiguration()

assert (
    configuration.application_name
    == DEFAULT_APPLICATION_NAME
)

assert (
    configuration.application_version
    == DEFAULT_APPLICATION_VERSION
)

assert (
    configuration.environment
    is ApplicationEnvironment.DEVELOPMENT
)

assert (
    configuration.required_services
    == DEFAULT_REQUIRED_SERVICES
)

assert isinstance(
    configuration.api,
    APIConfiguration,
)

assert isinstance(
    configuration.reporting,
    ReportingConfiguration,
)

assert isinstance(
    configuration.monitoring,
    MonitoringConfiguration,
)

assert configuration.fail_fast is True
assert configuration.validate_dependencies is True
assert configuration.enable_bootstrap_events is True
assert configuration.allow_service_replacement is False
assert configuration.configuration_version == "1.0.0"

assert configuration.environment_name == "development"
assert configuration.is_development is True
assert configuration.is_test is False
assert configuration.is_production is False

assert (
    configuration.requires_service(
        name="api",
    )
    is True
)


# ------------------------------------------------------------
# Valid custom configuration
# ------------------------------------------------------------

api_configuration = APIConfiguration(
    request_timeout_seconds=45,
)

reporting_configuration = ReportingConfiguration(
    default_report_type="executive",
    default_report_format="json",
)

monitoring_configuration = MonitoringConfiguration(
    enabled_components=(
        "orchestration",
        "reporting",
        "platform",
    ),
)

custom_configuration = ApplicationConfiguration(
    application_name="Enterprise Workforce Intelligence",
    application_version="3.1.0",
    environment=ApplicationEnvironment.TEST,
    required_services=(
        "planning",
        "optimization",
        "orchestration",
        "reporting",
        "monitoring",
        "api",
    ),
    api=api_configuration,
    reporting=reporting_configuration,
    monitoring=monitoring_configuration,
    fail_fast=False,
    validate_dependencies=True,
    enable_bootstrap_events=True,
    allow_service_replacement=True,
    configuration_version="1.1.0",
    metadata={
        "deployment": "databricks",
        "owner": "workforce-ai",
    },
)

assert (
    custom_configuration.environment
    is ApplicationEnvironment.TEST
)

assert custom_configuration.is_test is True
assert custom_configuration.is_development is False
assert custom_configuration.is_production is False

assert custom_configuration.api is api_configuration
assert (
    custom_configuration.reporting
    is reporting_configuration
)
assert (
    custom_configuration.monitoring
    is monitoring_configuration
)

assert custom_configuration.fail_fast is False
assert custom_configuration.allow_service_replacement is True


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

payload = custom_configuration.as_dict()

assert (
    payload["application_name"]
    == "Enterprise Workforce Intelligence"
)

assert payload["application_version"] == "3.1.0"
assert payload["environment"] == "test"

assert payload["required_services"] == [
    "planning",
    "optimization",
    "orchestration",
    "reporting",
    "monitoring",
    "api",
]

assert (
    payload["api"]["request_timeout_seconds"]
    == 45
)

assert (
    payload["reporting"]["default_report_type"]
    == "executive"
)

assert payload["monitoring"]["enabled_components"] == [
    "orchestration",
    "reporting",
    "platform",
]

assert payload["configuration_version"] == "1.1.0"

assert (
    payload["metadata"]["deployment"]
    == "databricks"
)


# ------------------------------------------------------------
# Dependency validation
# ------------------------------------------------------------

try:
    ApplicationConfiguration(
        required_services=(
            "api",
            "monitoring",
        ),
    )
except ApplicationConfigurationError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationConfigurationError for "
        "missing API dependencies."
    )


relaxed_configuration = ApplicationConfiguration(
    required_services=(
        "api",
    ),
    validate_dependencies=False,
)

assert relaxed_configuration.required_services == (
    "api",
)


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "application_name": "",
    },
    {
        "application_version": "   ",
    },
    {
        "environment": "development",
    },
    {
        "required_services": [],
    },
    {
        "required_services": (
            "api",
            "api",
        ),
        "validate_dependencies": False,
    },
    {
        "required_services": (
            "invalid",
        ),
        "validate_dependencies": False,
    },
    {
        "api": "invalid",
    },
    {
        "reporting": "invalid",
    },
    {
        "monitoring": "invalid",
    },
    {
        "fail_fast": "yes",
    },
    {
        "validate_dependencies": 1,
    },
    {
        "enable_bootstrap_events": None,
    },
    {
        "allow_service_replacement": "false",
    },
    {
        "configuration_version": "",
    },
    {
        "metadata": [],
    },
]

for invalid_arguments in invalid_cases:
    try:
        ApplicationConfiguration(
            **invalid_arguments
        )
    except ApplicationConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected ApplicationConfigurationError for "
            f"{invalid_arguments}."
        )


# ------------------------------------------------------------
# Invalid service lookup
# ------------------------------------------------------------

try:
    configuration.requires_service(
        name="invalid",
    )
except ApplicationConfigurationError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationConfigurationError."
    )


print(
    "✅ Implementation 25.4 — "
    "Enterprise application configuration validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.5 Part 1
# Enterprise Application Container
# ============================================================

import importlib

import src.application.container

importlib.reload(src.application.container)

from src.application.configuration import (
    ApplicationConfiguration,
)
from src.application.container import (
    EnterpriseApplicationContainer,
)

configuration = ApplicationConfiguration()

container = EnterpriseApplicationContainer(
    configuration=configuration,
)

assert container.configuration is configuration

assert container.service_count == 0

assert container.registered_services == ()

container.register_instance(
    name="planning",
    instance=object(),
)

assert container.service_count == 1

assert "planning" in container.registered_services

container.register_factory(
    name="monitoring",
    factory=lambda: object(),
)

assert container.service_count == 2

assert set(container.registered_services) == {
    "planning",
    "monitoring",
}

print(
    "✅ Implementation 25.5 Part 1 — "
    "Enterprise container registration validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.5 Part 2 —
# Enterprise Application Container Validation
# ============================================================

import importlib

import src.application.container

importlib.reload(src.application.container)

from src.application.configuration import (
    ApplicationConfiguration,
)
from src.application.container import (
    EnterpriseApplicationContainer,
)
from src.application.exceptions import (
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationValidationError,
)


configuration = ApplicationConfiguration(
    required_services=(
        "planning",
        "monitoring",
    ),
    validate_dependencies=False,
)

container = EnterpriseApplicationContainer(
    configuration=configuration,
)

assert container.configuration is configuration
assert container.service_count == 0
assert container.registered_services == ()
assert container.resolved_services == ()


# ------------------------------------------------------------
# Existing instance registration
# ------------------------------------------------------------

planning_instance = object()

container.register_instance(
    name="planning",
    instance=planning_instance,
    description="Planning service.",
)

assert container.service_count == 1
assert container.contains(name="planning") is True
assert container.is_resolved(name="planning") is True

assert (
    container.resolve(name="planning")
    is planning_instance
)

assert container.resolved_services == (
    "planning",
)


# ------------------------------------------------------------
# Singleton factory
# ------------------------------------------------------------

singleton_creation_count = {
    "count": 0,
}


def monitoring_factory():
    singleton_creation_count["count"] += 1
    return {
        "service": "monitoring",
        "sequence": singleton_creation_count["count"],
    }


container.register_factory(
    name="monitoring",
    factory=monitoring_factory,
    singleton=True,
    description="Monitoring singleton.",
)

assert container.is_resolved(name="monitoring") is False

monitoring_instance_1 = container.resolve(
    name="monitoring",
)

monitoring_instance_2 = container.resolve(
    name="monitoring",
)

assert monitoring_instance_1 is monitoring_instance_2
assert singleton_creation_count["count"] == 1

assert container.is_resolved(name="monitoring") is True

assert set(container.resolved_services) == {
    "planning",
    "monitoring",
}


# ------------------------------------------------------------
# Resolve required services
# ------------------------------------------------------------

required_services = (
    container.resolve_required_services()
)

assert required_services["planning"] is planning_instance
assert (
    required_services["monitoring"]
    is monitoring_instance_1
)


# ------------------------------------------------------------
# Transient factory
# ------------------------------------------------------------

container.register_factory(
    name="reporting",
    factory=lambda: object(),
    singleton=False,
)

reporting_instance_1 = container.resolve(
    name="reporting",
)

reporting_instance_2 = container.resolve(
    name="reporting",
)

assert reporting_instance_1 is not reporting_instance_2

assert container.is_resolved(name="reporting") is False


# ------------------------------------------------------------
# Duplicate registration
# ------------------------------------------------------------

try:
    container.register_instance(
        name="planning",
        instance=object(),
    )
except ApplicationContainerError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationContainerError."
    )


# ------------------------------------------------------------
# Explicit registration replacement
# ------------------------------------------------------------

replacement_planning_instance = object()

container.register_instance(
    name="planning",
    instance=replacement_planning_instance,
    replace=True,
)

assert (
    container.resolve(name="planning")
    is replacement_planning_instance
)


# ------------------------------------------------------------
# Configuration-level replacement policy
# ------------------------------------------------------------

replacement_configuration = ApplicationConfiguration(
    required_services=("planning",),
    validate_dependencies=False,
    allow_service_replacement=True,
)

replacement_container = (
    EnterpriseApplicationContainer(
        configuration=replacement_configuration,
    )
)

replacement_container.register_instance(
    name="planning",
    instance=object(),
)

second_instance = object()

replacement_container.register_instance(
    name="planning",
    instance=second_instance,
)

assert (
    replacement_container.resolve(name="planning")
    is second_instance
)


# ------------------------------------------------------------
# Missing service
# ------------------------------------------------------------

try:
    container.resolve(
        name="optimization",
    )
except ApplicationDependencyError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationDependencyError."
    )


try:
    container.is_resolved(
        name="optimization",
    )
except ApplicationDependencyError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationDependencyError."
    )


# ------------------------------------------------------------
# Factory returning None
# ------------------------------------------------------------

container.register_factory(
    name="optimization",
    factory=lambda: None,
)

try:
    container.resolve(
        name="optimization",
    )
except ApplicationDependencyError as exc:
    assert "returned None" in str(exc)
else:
    raise AssertionError(
        "Expected ApplicationDependencyError."
    )


# ------------------------------------------------------------
# Factory failure wrapping
# ------------------------------------------------------------

def failing_factory():
    raise RuntimeError(
        "Dependency unavailable."
    )


container.register_factory(
    name="orchestration",
    factory=failing_factory,
)

try:
    container.resolve(
        name="orchestration",
    )
except ApplicationDependencyError as exc:
    assert "Dependency unavailable." in str(exc)
else:
    raise AssertionError(
        "Expected ApplicationDependencyError."
    )


# ------------------------------------------------------------
# Circular dependency detection
# ------------------------------------------------------------

circular_configuration = ApplicationConfiguration(
    required_services=("planning",),
    validate_dependencies=False,
)

circular_container = (
    EnterpriseApplicationContainer(
        configuration=circular_configuration,
    )
)


def planning_factory():
    return circular_container.resolve(
        name="optimization",
    )


def optimization_factory():
    return circular_container.resolve(
        name="planning",
    )


circular_container.register_factory(
    name="planning",
    factory=planning_factory,
)

circular_container.register_factory(
    name="optimization",
    factory=optimization_factory,
)

try:
    circular_container.resolve(
        name="planning",
    )
except ApplicationDependencyError as exc:
    assert "Circular dependency detected" in str(exc)
    assert (
        "planning -> optimization -> planning"
        in str(exc)
    )
else:
    raise AssertionError(
        "Expected ApplicationDependencyError."
    )


# ------------------------------------------------------------
# Singleton reset
# ------------------------------------------------------------

previous_monitoring_instance = (
    container.resolve(name="monitoring")
)

container.reset_singletons()

assert container.is_resolved(name="monitoring") is False

new_monitoring_instance = container.resolve(
    name="monitoring",
)

assert (
    new_monitoring_instance
    is not previous_monitoring_instance
)

assert singleton_creation_count["count"] == 2

# Explicit instance registrations remain resolved.
assert container.is_resolved(name="planning") is True

assert (
    container.resolve(name="planning")
    is replacement_planning_instance
)


# ------------------------------------------------------------
# Service removal
# ------------------------------------------------------------

assert container.remove(name="reporting") is True

assert container.contains(name="reporting") is False

assert container.remove(name="reporting") is False


# ------------------------------------------------------------
# Invalid calls
# ------------------------------------------------------------

invalid_calls = [
    lambda: EnterpriseApplicationContainer(
        configuration="invalid",
    ),
    lambda: container.register_instance(
        name="",
        instance=object(),
    ),
    lambda: container.register_instance(
        name="api",
        instance=None,
    ),
    lambda: container.register_instance(
        name="api",
        instance=object(),
        description=None,
    ),
    lambda: container.register_instance(
        name="api",
        instance=object(),
        replace="yes",
    ),
    lambda: container.register_factory(
        name="api",
        factory="invalid",
    ),
    lambda: container.register_factory(
        name="api",
        factory=lambda: object(),
        singleton="yes",
    ),
    lambda: container.resolve(
        name="",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ApplicationValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ApplicationValidationError."
        )


# ------------------------------------------------------------
# Clear container
# ------------------------------------------------------------

container.clear()

assert container.service_count == 0
assert container.registered_services == ()
assert container.resolved_services == ()


print(
    "✅ Implementation 25.5 Part 2 — "
    "Enterprise application container validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.6
# Enterprise Application Factory
# ============================================================

import importlib

import src.application.factory
importlib.reload(src.application.factory)

from src.application.configuration import (
    ApplicationConfiguration,
)

from src.application.container import (
    EnterpriseApplicationContainer,
)

from src.application.factory import (
    EnterpriseApplicationFactory,
)

configuration = ApplicationConfiguration()

factory = EnterpriseApplicationFactory(
    configuration=configuration,
)

container = factory.build()

assert isinstance(
    container,
    EnterpriseApplicationContainer,
)

assert container.configuration is configuration

assert container.service_count > 0

assert len(container.registered_services) > 0

print(
    "✅ Implementation 25.6 Part 1 — "
    "Enterprise application factory creation validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.6 Part 2 —
# Enterprise Application Factory Dependency Wiring Validation
# ============================================================

import importlib

import src.application.factory

importlib.reload(src.application.factory)

from src.api.service import EnterpriseAPIService
from src.application.configuration import (
    ApplicationConfiguration,
)
from src.application.constants import (
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
)
from src.application.container import (
    EnterpriseApplicationContainer,
)
from src.application.factory import (
    EnterpriseApplicationFactory,
)
from src.monitoring.service import (
    EnterpriseMonitoringService,
)
from src.optimization.service import (
    WorkforceOptimizationService,
)
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.planning.service import (
    CapacityPlanningService,
)
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


configuration = ApplicationConfiguration()

factory = EnterpriseApplicationFactory(
    configuration=configuration,
)

container = factory.build()

assert isinstance(
    container,
    EnterpriseApplicationContainer,
)

expected_services = {
    SERVICE_PLANNING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_REPORTING,
    SERVICE_MONITORING,
    SERVICE_API,
}

assert set(container.registered_services) == expected_services
assert container.service_count == len(expected_services)


planning_service = container.resolve(
    name=SERVICE_PLANNING,
)

optimization_service = container.resolve(
    name=SERVICE_OPTIMIZATION,
)

orchestration_service = container.resolve(
    name=SERVICE_ORCHESTRATION,
)

reporting_service = container.resolve(
    name=SERVICE_REPORTING,
)

monitoring_service = container.resolve(
    name=SERVICE_MONITORING,
)

api_service = container.resolve(
    name=SERVICE_API,
)


assert isinstance(
    planning_service,
    CapacityPlanningService,
)

assert isinstance(
    optimization_service,
    WorkforceOptimizationService,
)

assert isinstance(
    orchestration_service,
    EnterpriseDecisionOrchestrationService,
)

assert isinstance(
    reporting_service,
    EnterpriseDecisionReportingService,
)

assert isinstance(
    monitoring_service,
    EnterpriseMonitoringService,
)

assert isinstance(
    api_service,
    EnterpriseAPIService,
)


assert (
    api_service.orchestration_service
    is orchestration_service
)

assert (
    api_service.reporting_service
    is reporting_service
)

assert (
    api_service.monitoring_service
    is monitoring_service
)

assert (
    api_service.configuration
    is configuration.api
)


for service_name in expected_services:
    first_instance = container.resolve(
        name=service_name,
    )

    second_instance = container.resolve(
        name=service_name,
    )

    assert first_instance is second_instance


resolved_required_services = (
    container.resolve_required_services()
)

assert set(resolved_required_services) == expected_services

assert set(container.resolved_services) == expected_services

assert factory.configuration is configuration


print(
    "✅ Implementation 25.6 Part 2 — "
    "Enterprise application factory dependency wiring "
    "validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.7 Part 1 —
# Enterprise Application Bootstrap Creation Validation
# ============================================================

import importlib

import src.application.bootstrap

importlib.reload(src.application.bootstrap)

from src.application.bootstrap import (
    EnterpriseApplicationBootstrap,
)
from src.application.configuration import (
    ApplicationConfiguration,
)
from src.application.factory import (
    EnterpriseApplicationFactory,
)


configuration = ApplicationConfiguration()

factory = EnterpriseApplicationFactory(
    configuration=configuration,
)

bootstrap = EnterpriseApplicationBootstrap(
    configuration=configuration,
    factory=factory,
)

assert bootstrap.configuration is configuration
assert bootstrap.factory is factory

assert bootstrap.container is None
assert bootstrap.context is None
assert bootstrap.last_result is None

assert bootstrap.has_started is False
assert bootstrap.is_ready is False


print(
    "✅ Implementation 25.7 Part 1 — "
    "Enterprise application bootstrap creation "
    "validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.7 Part 2 —
# Enterprise Application Bootstrap Lifecycle Validation
# ============================================================

import importlib

import src.application.bootstrap

importlib.reload(src.application.bootstrap)

from src.api.service import EnterpriseAPIService
from src.application.bootstrap import (
    EnterpriseApplicationBootstrap,
)
from src.application.configuration import (
    ApplicationConfiguration,
)
from src.application.constants import (
    BOOTSTRAP_SEQUENCE,
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
)
from src.application.container import (
    EnterpriseApplicationContainer,
)
from src.application.exceptions import (
    ApplicationBootstrapError,
    ApplicationLifecycleError,
    ApplicationValidationError,
)
from src.application.factory import (
    EnterpriseApplicationFactory,
)
from src.application.models import (
    ApplicationContext,
    ApplicationStatus,
    BootstrapStage,
)
from src.monitoring.service import (
    EnterpriseMonitoringService,
)
from src.optimization.service import (
    WorkforceOptimizationService,
)
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.planning.service import (
    CapacityPlanningService,
)
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


# ------------------------------------------------------------
# Successful application bootstrap
# ------------------------------------------------------------

configuration = ApplicationConfiguration()

factory = EnterpriseApplicationFactory(
    configuration=configuration,
)

bootstrap = EnterpriseApplicationBootstrap(
    configuration=configuration,
    factory=factory,
)

context = bootstrap.start()

assert isinstance(
    context,
    ApplicationContext,
)

assert bootstrap.has_started is True
assert bootstrap.is_ready is True

assert bootstrap.context is context

assert isinstance(
    bootstrap.container,
    EnterpriseApplicationContainer,
)

assert bootstrap.last_result is context.bootstrap_result

assert (
    context.descriptor.status
    is ApplicationStatus.READY
)

assert context.bootstrap_result.succeeded is True

assert (
    context.bootstrap_result.completed_stage
    is BootstrapStage.COMPLETE
)

assert tuple(
    event.stage.value
    for event in context.bootstrap_result.events
) == BOOTSTRAP_SEQUENCE

assert all(
    event.succeeded
    for event in context.bootstrap_result.events
)


# ------------------------------------------------------------
# Service registrations
# ------------------------------------------------------------

expected_services = {
    SERVICE_PLANNING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_REPORTING,
    SERVICE_MONITORING,
    SERVICE_API,
}

registered_names = {
    registration.name
    for registration in context.services
}

assert registered_names == expected_services


planning_service = context.get_service(
    name=SERVICE_PLANNING,
)

optimization_service = context.get_service(
    name=SERVICE_OPTIMIZATION,
)

orchestration_service = context.get_service(
    name=SERVICE_ORCHESTRATION,
)

reporting_service = context.get_service(
    name=SERVICE_REPORTING,
)

monitoring_service = context.get_service(
    name=SERVICE_MONITORING,
)

api_service = context.get_service(
    name=SERVICE_API,
)


assert isinstance(
    planning_service,
    CapacityPlanningService,
)

assert isinstance(
    optimization_service,
    WorkforceOptimizationService,
)

assert isinstance(
    orchestration_service,
    EnterpriseDecisionOrchestrationService,
)

assert isinstance(
    reporting_service,
    EnterpriseDecisionReportingService,
)

assert isinstance(
    monitoring_service,
    EnterpriseMonitoringService,
)

assert isinstance(
    api_service,
    EnterpriseAPIService,
)


# ------------------------------------------------------------
# Shared application dependencies
# ------------------------------------------------------------

assert (
    api_service.orchestration_service
    is orchestration_service
)

assert (
    api_service.reporting_service
    is reporting_service
)

assert (
    api_service.monitoring_service
    is monitoring_service
)

assert (
    api_service.configuration
    is configuration.api
)


# ------------------------------------------------------------
# Context serialization
# ------------------------------------------------------------

context_payload = context.as_dict()

assert (
    context_payload["descriptor"]["status"]
    == "READY"
)

assert (
    context_payload["bootstrap_result"]["succeeded"]
    is True
)

assert len(
    context_payload["bootstrap_result"]["events"]
) == 5

assert len(context_payload["services"]) == 6

assert (
    context_payload["metadata"]["configuration_version"]
    == "1.0.0"
)


# ------------------------------------------------------------
# Single-use lifecycle
# ------------------------------------------------------------

try:
    bootstrap.start()
except ApplicationLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationLifecycleError."
    )


# ------------------------------------------------------------
# Invalid bootstrap construction
# ------------------------------------------------------------

invalid_calls = [
    lambda: EnterpriseApplicationBootstrap(
        configuration="invalid",
    ),
    lambda: EnterpriseApplicationBootstrap(
        configuration=configuration,
        factory="invalid",
    ),
]

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except ApplicationValidationError:
        pass
    else:
        raise AssertionError(
            "Expected ApplicationValidationError."
        )


# ------------------------------------------------------------
# Configuration and factory mismatch
# ------------------------------------------------------------

different_configuration = ApplicationConfiguration(
    application_version="3.1.0",
)

different_factory = EnterpriseApplicationFactory(
    configuration=different_configuration,
)

try:
    EnterpriseApplicationBootstrap(
        configuration=configuration,
        factory=different_factory,
    )
except ApplicationValidationError:
    pass
else:
    raise AssertionError(
        "Expected ApplicationValidationError for "
        "configuration and factory mismatch."
    )


# ------------------------------------------------------------
# Failed bootstrap lifecycle
# ------------------------------------------------------------

class FailingApplicationFactory(
    EnterpriseApplicationFactory
):

    def build(self):
        raise RuntimeError(
            "Simulated dependency construction failure."
        )


failure_configuration = ApplicationConfiguration()

failure_factory = FailingApplicationFactory(
    configuration=failure_configuration,
)

failure_bootstrap = EnterpriseApplicationBootstrap(
    configuration=failure_configuration,
    factory=failure_factory,
)

try:
    failure_bootstrap.start()
except ApplicationBootstrapError as exc:
    assert (
        "Simulated dependency construction failure."
        in str(exc)
    )
else:
    raise AssertionError(
        "Expected ApplicationBootstrapError."
    )


assert failure_bootstrap.has_started is True
assert failure_bootstrap.is_ready is False
assert failure_bootstrap.context is None

assert failure_bootstrap.last_result is not None

assert (
    failure_bootstrap.last_result.descriptor.status
    is ApplicationStatus.FAILED
)

assert failure_bootstrap.last_result.succeeded is False

assert (
    failure_bootstrap.last_result.completed_stage
    is BootstrapStage.DEPENDENCIES
)

assert (
    failure_bootstrap.last_result.error_message
    == "Simulated dependency construction failure."
)

assert (
    failure_bootstrap.last_result.events[-1].succeeded
    is False
)


print(
    "✅ Implementation 25.7 Part 2 — "
    "Enterprise application bootstrap lifecycle "
    "validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 25.8 —
# Enterprise Application Package Validation
# ============================================================

import importlib

import src.application

importlib.reload(src.application)

from src.application import (
    APPLICATION_DOMAIN_NAME,
    APPLICATION_DOMAIN_VERSION,
    BOOTSTRAP_COMPLETE,
    BOOTSTRAP_SEQUENCE,
    DEFAULT_APPLICATION_NAME,
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_CONFIGURATION_VERSION,
    ENVIRONMENT_DEVELOPMENT,
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
    ApplicationBootstrapError,
    ApplicationBootstrapResult,
    ApplicationConfiguration,
    ApplicationConfigurationError,
    ApplicationContainerError,
    ApplicationContext,
    ApplicationDependencyError,
    ApplicationDescriptor,
    ApplicationEnvironment,
    ApplicationError,
    ApplicationFactoryError,
    ApplicationLifecycleError,
    ApplicationStatus,
    ApplicationValidationError,
    BootstrapEvent,
    BootstrapStage,
    EnterpriseApplicationBootstrap,
    EnterpriseApplicationContainer,
    EnterpriseApplicationFactory,
    ServiceRegistration,
)


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

assert APPLICATION_DOMAIN_NAME == "application"
assert APPLICATION_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_CONFIGURATION_VERSION == "1.0.0"

assert ENVIRONMENT_DEVELOPMENT == "development"

assert BOOTSTRAP_SEQUENCE[-1] == BOOTSTRAP_COMPLETE

assert SERVICE_PLANNING == "planning"
assert SERVICE_OPTIMIZATION == "optimization"
assert SERVICE_ORCHESTRATION == "orchestration"
assert SERVICE_REPORTING == "reporting"
assert SERVICE_MONITORING == "monitoring"
assert SERVICE_API == "api"


# ------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------

assert issubclass(
    ApplicationValidationError,
    ApplicationError,
)

assert issubclass(
    ApplicationConfigurationError,
    ApplicationError,
)

assert issubclass(
    ApplicationContainerError,
    ApplicationError,
)

assert issubclass(
    ApplicationDependencyError,
    ApplicationError,
)

assert issubclass(
    ApplicationFactoryError,
    ApplicationError,
)

assert issubclass(
    ApplicationBootstrapError,
    ApplicationError,
)

assert issubclass(
    ApplicationLifecycleError,
    ApplicationError,
)


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

assert ApplicationEnvironment is not None
assert BootstrapStage is not None
assert ApplicationStatus is not None

assert ServiceRegistration is not None
assert BootstrapEvent is not None
assert ApplicationDescriptor is not None
assert ApplicationBootstrapResult is not None
assert ApplicationContext is not None


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

assert ApplicationConfiguration is not None

assert (
    DEFAULT_APPLICATION_NAME
    == "AI Workforce Capacity Planning Platform"
)

assert DEFAULT_APPLICATION_VERSION == "3.0.0"


# ------------------------------------------------------------
# Components
# ------------------------------------------------------------

assert EnterpriseApplicationContainer is not None
assert EnterpriseApplicationFactory is not None
assert EnterpriseApplicationBootstrap is not None


# ------------------------------------------------------------
# End-to-end package smoke validation
# ------------------------------------------------------------

configuration = ApplicationConfiguration()

bootstrap = EnterpriseApplicationBootstrap(
    configuration=configuration,
)

context = bootstrap.start()

assert isinstance(
    context,
    ApplicationContext,
)

assert (
    context.descriptor.status
    is ApplicationStatus.READY
)

assert (
    context.bootstrap_result.completed_stage
    is BootstrapStage.COMPLETE
)

assert (
    context.get_service(
        name=SERVICE_API,
    )
    is not None
)


print(
    "✅ Implementation 25.8 — "
    "Enterprise application package validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.1 —
# Enterprise Platform Runner Constants Validation
# ============================================================

import importlib

import src.runner.constants

importlib.reload(src.runner.constants)

from src.runner.constants import *


# ------------------------------------------------------------
# Domain
# ------------------------------------------------------------

assert RUNNER_DOMAIN_NAME == "platform-runner"
assert RUNNER_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_RUNNER_VERSION == "1.0.0"


# ------------------------------------------------------------
# Runtime modes
# ------------------------------------------------------------

assert DEFAULT_RUNTIME_MODE == RUNTIME_MODE_APPLICATION

assert SUPPORTED_RUNTIME_MODES == (
    RUNTIME_MODE_APPLICATION,
    RUNTIME_MODE_API,
    RUNTIME_MODE_VALIDATION,
    RUNTIME_MODE_BATCH,
)

assert len(SUPPORTED_RUNTIME_MODES) == len(
    set(SUPPORTED_RUNTIME_MODES)
)


# ------------------------------------------------------------
# Runner statuses
# ------------------------------------------------------------

assert RUNNER_STATUS_CREATED == "CREATED"
assert RUNNER_STATUS_STARTING == "STARTING"
assert RUNNER_STATUS_RUNNING == "RUNNING"
assert RUNNER_STATUS_STOPPING == "STOPPING"
assert RUNNER_STATUS_STOPPED == "STOPPED"
assert RUNNER_STATUS_FAILED == "FAILED"

assert len(SUPPORTED_RUNNER_STATUSES) == len(
    set(SUPPORTED_RUNNER_STATUSES)
)


# ------------------------------------------------------------
# Startup sequence
# ------------------------------------------------------------

assert STARTUP_SEQUENCE == (
    STARTUP_STAGE_CONFIGURATION,
    STARTUP_STAGE_APPLICATION,
    STARTUP_STAGE_SERVICES,
    STARTUP_STAGE_HEALTH,
    STARTUP_STAGE_READY,
)

assert len(STARTUP_SEQUENCE) == len(
    set(STARTUP_SEQUENCE)
)


# ------------------------------------------------------------
# Shutdown sequence
# ------------------------------------------------------------

assert SHUTDOWN_SEQUENCE == (
    SHUTDOWN_STAGE_REQUESTED,
    SHUTDOWN_STAGE_SERVICES,
    SHUTDOWN_STAGE_CONTAINER,
    SHUTDOWN_STAGE_COMPLETE,
)

assert len(SHUTDOWN_SEQUENCE) == len(
    set(SHUTDOWN_SEQUENCE)
)


# ------------------------------------------------------------
# Shutdown reasons
# ------------------------------------------------------------

assert SHUTDOWN_REASON_REQUESTED == "requested"
assert SHUTDOWN_REASON_COMPLETED == "completed"
assert SHUTDOWN_REASON_FAILURE == "failure"
assert SHUTDOWN_REASON_INTERRUPT == "interrupt"

assert len(SUPPORTED_SHUTDOWN_REASONS) == len(
    set(SUPPORTED_SHUTDOWN_REASONS)
)


# ------------------------------------------------------------
# Exit codes
# ------------------------------------------------------------

assert EXIT_CODE_SUCCESS == 0
assert EXIT_CODE_CONFIGURATION_ERROR == 10
assert EXIT_CODE_STARTUP_ERROR == 20
assert EXIT_CODE_RUNTIME_ERROR == 30
assert EXIT_CODE_SHUTDOWN_ERROR == 40
assert EXIT_CODE_INTERRUPTED == 130

assert len(SUPPORTED_EXIT_CODES) == len(
    set(SUPPORTED_EXIT_CODES)
)


# ------------------------------------------------------------
# Defaults
# ------------------------------------------------------------

assert DEFAULT_APPLICATION_NAME == (
    "AI Workforce Capacity Planning Platform"
)

assert DEFAULT_APPLICATION_VERSION == "3.0.0"

assert DEFAULT_STARTUP_TIMEOUT_SECONDS > 0
assert DEFAULT_SHUTDOWN_TIMEOUT_SECONDS > 0

assert DEFAULT_HEALTH_CHECK_ON_STARTUP is True
assert DEFAULT_FAIL_ON_UNHEALTHY is True
assert DEFAULT_ENABLE_GRACEFUL_SHUTDOWN is True
assert DEFAULT_REGISTER_SIGNAL_HANDLERS is True


# ------------------------------------------------------------
# Signals
# ------------------------------------------------------------

assert SUPPORTED_SHUTDOWN_SIGNALS == (
    SIGNAL_INTERRUPT,
    SIGNAL_TERMINATE,
)

assert len(SUPPORTED_SHUTDOWN_SIGNALS) == len(
    set(SUPPORTED_SHUTDOWN_SIGNALS)
)


# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

assert DEFAULT_RUNNER_SOURCE == (
    "enterprise-platform-runner"
)

assert DEFAULT_TIMEZONE == "UTC"
assert DEFAULT_TIMESTAMP_FORMAT != ""
assert DEFAULT_CONFIGURATION_VERSION == "1.0.0"


print(
    "✅ Implementation 26.1 — "
    "Enterprise platform runner constants validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.2
# Enterprise Platform Runner Exceptions Validation
# ============================================================

import importlib

import src.runner.exceptions

importlib.reload(src.runner.exceptions)

from src.runner.exceptions import *


assert issubclass(
    RunnerValidationError,
    RunnerError,
)

assert issubclass(
    RunnerConfigurationError,
    RunnerError,
)

assert issubclass(
    RunnerStartupError,
    RunnerError,
)

assert issubclass(
    RunnerShutdownError,
    RunnerError,
)

assert issubclass(
    RunnerRuntimeError,
    RunnerError,
)

assert issubclass(
    RunnerExecutionError,
    RunnerError,
)

assert issubclass(
    RunnerLifecycleError,
    RunnerError,
)


try:
    raise RunnerValidationError(
        "Validation failed."
    )
except RunnerError as exc:
    assert str(exc) == "Validation failed."


try:
    raise RunnerConfigurationError(
        "Configuration failed."
    )
except RunnerError as exc:
    assert str(exc) == "Configuration failed."


try:
    raise RunnerStartupError(
        "Startup failed."
    )
except RunnerError as exc:
    assert str(exc) == "Startup failed."


try:
    raise RunnerShutdownError(
        "Shutdown failed."
    )
except RunnerError as exc:
    assert str(exc) == "Shutdown failed."


try:
    raise RunnerRuntimeError(
        "Runtime failed."
    )
except RunnerError as exc:
    assert str(exc) == "Runtime failed."


try:
    raise RunnerExecutionError(
        "Execution failed."
    )
except RunnerError as exc:
    assert str(exc) == "Execution failed."


try:
    raise RunnerLifecycleError(
        "Lifecycle failed."
    )
except RunnerError as exc:
    assert str(exc) == "Lifecycle failed."


print(
    "✅ Implementation 26.2 — "
    "Enterprise platform runner exceptions validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.3
# Enterprise Platform Runner Models Validation
# ============================================================

import importlib
from datetime import datetime

import src.runner.models

importlib.reload(src.runner.models)

from src.runner.models import *


timestamp = datetime.utcnow()

descriptor = RunnerDescriptor(
    name="enterprise-runner",
    version="1.0.0",
    runtime_mode="application",
    status=RunnerStatus.CREATED,
    started_at_utc=timestamp,
)

assert descriptor.name == "enterprise-runner"
assert descriptor.version == "1.0.0"
assert descriptor.runtime_mode == "application"
assert descriptor.status is RunnerStatus.CREATED
assert descriptor.started_at_utc is timestamp


result = RunnerExecutionResult(
    succeeded=True,
    descriptor=descriptor,
    completed_at_utc=timestamp,
    exit_code=0,
    message="Runner completed.",
)

assert result.succeeded is True
assert result.descriptor is descriptor
assert result.completed_at_utc is timestamp
assert result.exit_code == 0
assert result.message == "Runner completed."


assert RunnerStatus.CREATED.value == "CREATED"
assert RunnerStatus.RUNNING.value == "RUNNING"
assert RunnerStatus.STOPPED.value == "STOPPED"
assert RunnerStatus.FAILED.value == "FAILED"


invalid_calls = [
    lambda: RunnerDescriptor(
        name=1,
        version="1.0.0",
        runtime_mode="application",
        status=RunnerStatus.CREATED,
    ),
]

print(
    "✅ Implementation 26.3 — "
    "Enterprise platform runner models validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.4 —
# Enterprise Platform Runner Configuration Validation
# ============================================================

import importlib

import src.runner.configuration

importlib.reload(src.runner.configuration)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.constants import (
    DEFAULT_RUNNER_SOURCE,
    DEFAULT_RUNNER_VERSION,
    DEFAULT_RUNTIME_MODE,
    DEFAULT_SHUTDOWN_TIMEOUT_SECONDS,
    DEFAULT_STARTUP_TIMEOUT_SECONDS,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TIMEZONE,
)
from src.runner.exceptions import (
    RunnerConfigurationError,
)


# ------------------------------------------------------------
# Default configuration
# ------------------------------------------------------------

configuration = RunnerConfiguration()

assert configuration.runner_name == DEFAULT_RUNNER_SOURCE
assert configuration.runner_version == DEFAULT_RUNNER_VERSION
assert configuration.runtime_mode == DEFAULT_RUNTIME_MODE

assert configuration.timezone == DEFAULT_TIMEZONE
assert (
    configuration.timestamp_format
    == DEFAULT_TIMESTAMP_FORMAT
)

assert (
    configuration.startup_timeout_seconds
    == DEFAULT_STARTUP_TIMEOUT_SECONDS
)

assert (
    configuration.shutdown_timeout_seconds
    == DEFAULT_SHUTDOWN_TIMEOUT_SECONDS
)

assert configuration.health_check_interval_seconds == 30
assert configuration.max_retry_attempts == 3
assert configuration.retry_delay_seconds == 5

assert (
    configuration.graceful_shutdown_timeout_seconds
    == 30
)

assert configuration.health_check_on_startup is True
assert configuration.fail_on_unhealthy is True
assert configuration.enable_graceful_shutdown is True
assert configuration.enable_signal_handlers is True

assert configuration.enable_logging is True
assert configuration.enable_metrics is True
assert configuration.enable_validation is True

assert configuration.auto_startup is True
assert configuration.auto_shutdown is True

assert configuration.configuration_version == "1.0.0"

assert configuration.retries_enabled is True
assert configuration.graceful_shutdown_enabled is True


# ------------------------------------------------------------
# Custom configuration
# ------------------------------------------------------------

custom_configuration = RunnerConfiguration(
    runner_name="validation-runner",
    runner_version="1.1.0",
    runtime_mode="validation",
    startup_timeout_seconds=90,
    shutdown_timeout_seconds=45,
    health_check_interval_seconds=15,
    max_retry_attempts=0,
    retry_delay_seconds=0,
    graceful_shutdown_timeout_seconds=20,
    health_check_on_startup=False,
    fail_on_unhealthy=False,
    enable_graceful_shutdown=False,
    enable_signal_handlers=False,
    enable_logging=False,
    enable_metrics=False,
    enable_validation=True,
    auto_startup=False,
    auto_shutdown=False,
    configuration_version="1.1.0",
)

assert custom_configuration.runner_name == "validation-runner"
assert custom_configuration.runtime_mode == "validation"
assert custom_configuration.retries_enabled is False
assert (
    custom_configuration.graceful_shutdown_enabled
    is False
)


# ------------------------------------------------------------
# Serialization
# ------------------------------------------------------------

payload = custom_configuration.as_dict()

assert payload["runner_name"] == "validation-runner"
assert payload["runner_version"] == "1.1.0"
assert payload["runtime_mode"] == "validation"
assert payload["max_retry_attempts"] == 0
assert payload["enable_logging"] is False
assert payload["configuration_version"] == "1.1.0"


# ------------------------------------------------------------
# Invalid configurations
# ------------------------------------------------------------

invalid_cases = [
    {
        "runner_name": "",
    },
    {
        "runner_version": " ",
    },
    {
        "runtime_mode": "invalid",
    },
    {
        "timezone": "",
    },
    {
        "timestamp_format": "",
    },
    {
        "startup_timeout_seconds": 0,
    },
    {
        "shutdown_timeout_seconds": -1,
    },
    {
        "health_check_interval_seconds": 0,
    },
    {
        "max_retry_attempts": -1,
    },
    {
        "retry_delay_seconds": -1,
    },
    {
        "graceful_shutdown_timeout_seconds": 0,
    },
    {
        "enable_logging": "yes",
    },
    {
        "enable_metrics": 1,
    },
    {
        "enable_validation": None,
    },
    {
        "health_check_on_startup": "true",
    },
    {
        "fail_on_unhealthy": "true",
    },
    {
        "enable_graceful_shutdown": 1,
    },
    {
        "enable_signal_handlers": None,
    },
    {
        "auto_startup": "yes",
    },
    {
        "auto_shutdown": "yes",
    },
    {
        "configuration_version": "",
    },
]

for invalid_arguments in invalid_cases:
    try:
        RunnerConfiguration(
            **invalid_arguments
        )
    except RunnerConfigurationError:
        pass
    else:
        raise AssertionError(
            "Expected RunnerConfigurationError for "
            f"{invalid_arguments}."
        )


print(
    "✅ Implementation 26.4 — "
    "Enterprise platform runner configuration "
    "validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.5 Part 1 —
# Enterprise Runner Startup Validation
# ============================================================

import importlib

import src.runner.startup

importlib.reload(src.runner.startup)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.models import (
    RunnerExecutionResult,
    RunnerStatus,
)
from src.runner.startup import (
    EnterpriseRunnerStartup,
)


configuration = RunnerConfiguration()

startup = EnterpriseRunnerStartup(
    configuration=configuration,
)

assert startup.configuration is configuration
assert startup.started is False
assert startup.last_result is None

result = startup.start()

assert isinstance(
    result,
    RunnerExecutionResult,
)

assert result.succeeded is True

assert (
    result.descriptor.status
    is RunnerStatus.RUNNING
)

assert (
    result.descriptor.name
    == configuration.runner_name
)

assert (
    result.descriptor.version
    == configuration.runner_version
)

assert (
    result.descriptor.runtime_mode
    == configuration.runtime_mode
)

assert result.descriptor.started_at_utc is not None
assert result.exit_code == 0
assert result.message == "Runner started successfully."

assert startup.started is True
assert startup.last_result is result


print(
    "✅ Implementation 26.5 Part 1 — "
    "Enterprise runner startup validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.5 Part 2 —
# Enterprise Runner Startup Lifecycle Validation
# ============================================================

import importlib

import src.runner.startup

importlib.reload(src.runner.startup)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.exceptions import (
    RunnerConfigurationError,
    RunnerStartupError,
)
from src.runner.startup import (
    EnterpriseRunnerStartup,
)


# ------------------------------------------------------------
# Invalid configuration
# ------------------------------------------------------------

try:
    EnterpriseRunnerStartup(
        configuration="invalid",
    )
except RunnerConfigurationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerConfigurationError."
    )


# ------------------------------------------------------------
# Double startup
# ------------------------------------------------------------

startup = EnterpriseRunnerStartup(
    configuration=RunnerConfiguration(),
)

first_result = startup.start()

try:
    startup.start()
except RunnerStartupError:
    pass
else:
    raise AssertionError(
        "Expected RunnerStartupError."
    )

assert startup.last_result is first_result
assert startup.started is True


print(
    "✅ Implementation 26.5 Part 2 — "
    "Enterprise runner startup lifecycle validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.6 Part 1 —
# Enterprise Runner Shutdown Validation
# ============================================================

import importlib
from datetime import datetime, timezone

import src.runner.shutdown

importlib.reload(src.runner.shutdown)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.constants import (
    SHUTDOWN_REASON_COMPLETED,
)
from src.runner.models import (
    RunnerDescriptor,
    RunnerExecutionResult,
    RunnerStatus,
)
from src.runner.shutdown import (
    EnterpriseRunnerShutdown,
)


configuration = RunnerConfiguration()

shutdown = EnterpriseRunnerShutdown(
    configuration=configuration,
)

assert shutdown.configuration is configuration
assert shutdown.stopped is False
assert shutdown.shutdown_reason is None
assert shutdown.last_result is None


started_at_utc = datetime.now(timezone.utc)

running_descriptor = RunnerDescriptor(
    name=configuration.runner_name,
    version=configuration.runner_version,
    runtime_mode=configuration.runtime_mode,
    status=RunnerStatus.RUNNING,
    started_at_utc=started_at_utc,
)

result = shutdown.stop(
    descriptor=running_descriptor,
    reason=SHUTDOWN_REASON_COMPLETED,
)

assert isinstance(
    result,
    RunnerExecutionResult,
)

assert result.succeeded is True

assert (
    result.descriptor.status
    is RunnerStatus.STOPPED
)

assert result.descriptor.name == running_descriptor.name
assert result.descriptor.version == running_descriptor.version

assert (
    result.descriptor.runtime_mode
    == running_descriptor.runtime_mode
)

assert (
    result.descriptor.started_at_utc
    is started_at_utc
)

assert result.exit_code == 0

assert result.message == (
    "Runner stopped successfully "
    "with reason 'completed'."
)

assert shutdown.stopped is True

assert (
    shutdown.shutdown_reason
    == SHUTDOWN_REASON_COMPLETED
)

assert shutdown.last_result is result


print(
    "✅ Implementation 26.6 Part 1 — "
    "Enterprise runner shutdown validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.6 Part 2 —
# Enterprise Runner Shutdown Lifecycle Validation
# ============================================================

import importlib
from datetime import datetime, timezone

import src.runner.shutdown

importlib.reload(src.runner.shutdown)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.constants import (
    SHUTDOWN_REASON_REQUESTED,
)
from src.runner.exceptions import (
    RunnerConfigurationError,
    RunnerShutdownError,
    RunnerValidationError,
)
from src.runner.models import (
    RunnerDescriptor,
    RunnerStatus,
)
from src.runner.shutdown import (
    EnterpriseRunnerShutdown,
)


configuration = RunnerConfiguration()

running_descriptor = RunnerDescriptor(
    name=configuration.runner_name,
    version=configuration.runner_version,
    runtime_mode=configuration.runtime_mode,
    status=RunnerStatus.RUNNING,
    started_at_utc=datetime.now(timezone.utc),
)


# ------------------------------------------------------------
# Invalid configuration
# ------------------------------------------------------------

try:
    EnterpriseRunnerShutdown(
        configuration="invalid",
    )
except RunnerConfigurationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerConfigurationError."
    )


# ------------------------------------------------------------
# Invalid descriptor
# ------------------------------------------------------------

shutdown = EnterpriseRunnerShutdown(
    configuration=configuration,
)

try:
    shutdown.stop(
        descriptor="invalid",
    )
except RunnerValidationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerValidationError."
    )


# ------------------------------------------------------------
# Invalid runner state
# ------------------------------------------------------------

created_descriptor = RunnerDescriptor(
    name=configuration.runner_name,
    version=configuration.runner_version,
    runtime_mode=configuration.runtime_mode,
    status=RunnerStatus.CREATED,
)

try:
    shutdown.stop(
        descriptor=created_descriptor,
    )
except RunnerShutdownError:
    pass
else:
    raise AssertionError(
        "Expected RunnerShutdownError."
    )


# ------------------------------------------------------------
# Invalid shutdown reason
# ------------------------------------------------------------

try:
    shutdown.stop(
        descriptor=running_descriptor,
        reason="invalid",
    )
except RunnerValidationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerValidationError."
    )


# ------------------------------------------------------------
# Successful shutdown
# ------------------------------------------------------------

first_result = shutdown.stop(
    descriptor=running_descriptor,
    reason=SHUTDOWN_REASON_REQUESTED,
)

assert shutdown.stopped is True
assert shutdown.last_result is first_result
assert (
    shutdown.shutdown_reason
    == SHUTDOWN_REASON_REQUESTED
)


# ------------------------------------------------------------
# Duplicate shutdown
# ------------------------------------------------------------

try:
    shutdown.stop(
        descriptor=running_descriptor,
        reason=SHUTDOWN_REASON_REQUESTED,
    )
except RunnerShutdownError:
    pass
else:
    raise AssertionError(
        "Expected RunnerShutdownError."
    )

assert shutdown.last_result is first_result


print(
    "✅ Implementation 26.6 Part 2 — "
    "Enterprise runner shutdown lifecycle validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.7 Part 1 —
# Enterprise Platform Runner Service Validation
# ============================================================

import importlib

import src.runner.service

importlib.reload(src.runner.service)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.models import (
    RunnerExecutionResult,
    RunnerStatus,
)
from src.runner.service import (
    EnterprisePlatformRunnerService,
)
from src.runner.shutdown import (
    EnterpriseRunnerShutdown,
)
from src.runner.startup import (
    EnterpriseRunnerStartup,
)


configuration = RunnerConfiguration(
    auto_startup=True,
    auto_shutdown=False,
)

startup = EnterpriseRunnerStartup(
    configuration=configuration,
)

shutdown = EnterpriseRunnerShutdown(
    configuration=configuration,
)

service = EnterprisePlatformRunnerService(
    configuration=configuration,
    startup=startup,
    shutdown=shutdown,
)


# ------------------------------------------------------------
# Initial state
# ------------------------------------------------------------

assert service.configuration is configuration
assert service.startup is startup
assert service.shutdown is shutdown

assert service.active_descriptor is None
assert service.startup_result is None
assert service.shutdown_result is None

assert service.status is RunnerStatus.CREATED
assert service.is_created is True
assert service.is_running is False
assert service.is_stopped is False


# ------------------------------------------------------------
# Startup
# ------------------------------------------------------------

startup_result = service.start()

assert isinstance(
    startup_result,
    RunnerExecutionResult,
)

assert startup_result.succeeded is True

assert (
    startup_result.descriptor.status
    is RunnerStatus.RUNNING
)

assert service.startup_result is startup_result
assert service.active_descriptor is startup_result.descriptor

assert service.status is RunnerStatus.RUNNING
assert service.is_created is False
assert service.is_running is True
assert service.is_stopped is False


# ------------------------------------------------------------
# Shutdown
# ------------------------------------------------------------

shutdown_result = service.stop()

assert isinstance(
    shutdown_result,
    RunnerExecutionResult,
)

assert shutdown_result.succeeded is True

assert (
    shutdown_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert service.shutdown_result is shutdown_result

assert (
    service.active_descriptor
    is shutdown_result.descriptor
)

assert service.status is RunnerStatus.STOPPED
assert service.is_created is False
assert service.is_running is False
assert service.is_stopped is True


print(
    "✅ Implementation 26.7 Part 1 — "
    "Enterprise platform runner service validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 26.7 Part 2 —
# Enterprise Platform Runner Service Lifecycle Validation
# ============================================================

import importlib

import src.runner.service

importlib.reload(src.runner.service)

from src.runner.configuration import (
    RunnerConfiguration,
)
from src.runner.exceptions import (
    RunnerConfigurationError,
    RunnerLifecycleError,
    RunnerValidationError,
)
from src.runner.models import (
    RunnerStatus,
)
from src.runner.service import (
    EnterprisePlatformRunnerService,
)
from src.runner.shutdown import (
    EnterpriseRunnerShutdown,
)
from src.runner.startup import (
    EnterpriseRunnerStartup,
)


# ------------------------------------------------------------
# Invalid construction
# ------------------------------------------------------------

configuration = RunnerConfiguration()

invalid_calls = [
    lambda: EnterprisePlatformRunnerService(
        configuration="invalid",
    ),
    lambda: EnterprisePlatformRunnerService(
        configuration=configuration,
        startup="invalid",
    ),
    lambda: EnterprisePlatformRunnerService(
        configuration=configuration,
        shutdown="invalid",
    ),
]

expected_exceptions = (
    RunnerConfigurationError,
    RunnerValidationError,
)

for invalid_call in invalid_calls:
    try:
        invalid_call()
    except expected_exceptions:
        pass
    else:
        raise AssertionError(
            "Expected runner construction error."
        )


# ------------------------------------------------------------
# Configuration dependency mismatch
# ------------------------------------------------------------

different_configuration = RunnerConfiguration(
    runner_version="1.1.0",
)

different_startup = EnterpriseRunnerStartup(
    configuration=different_configuration,
)

try:
    EnterprisePlatformRunnerService(
        configuration=configuration,
        startup=different_startup,
    )
except RunnerValidationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerValidationError for startup mismatch."
    )


different_shutdown = EnterpriseRunnerShutdown(
    configuration=different_configuration,
)

try:
    EnterprisePlatformRunnerService(
        configuration=configuration,
        shutdown=different_shutdown,
    )
except RunnerValidationError:
    pass
else:
    raise AssertionError(
        "Expected RunnerValidationError for shutdown mismatch."
    )


# ------------------------------------------------------------
# Stop before startup
# ------------------------------------------------------------

service = EnterprisePlatformRunnerService(
    configuration=RunnerConfiguration(
        auto_shutdown=False,
    ),
)

try:
    service.stop()
except RunnerLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected RunnerLifecycleError."
    )


# ------------------------------------------------------------
# Duplicate startup
# ------------------------------------------------------------

service.start()

try:
    service.start()
except RunnerLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected RunnerLifecycleError."
    )


# ------------------------------------------------------------
# Duplicate shutdown
# ------------------------------------------------------------

service.stop()

try:
    service.stop()
except RunnerLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected RunnerLifecycleError."
    )


# ------------------------------------------------------------
# Restart after shutdown
# ------------------------------------------------------------

try:
    service.start()
except RunnerLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected RunnerLifecycleError."
    )


# ------------------------------------------------------------
# Auto-run without automatic shutdown
# ------------------------------------------------------------

running_configuration = RunnerConfiguration(
    auto_startup=True,
    auto_shutdown=False,
)

running_service = EnterprisePlatformRunnerService(
    configuration=running_configuration,
)

running_result = running_service.run()

assert running_result.succeeded is True
assert (
    running_result.descriptor.status
    is RunnerStatus.RUNNING
)

assert running_service.is_running is True
assert running_service.is_stopped is False


# ------------------------------------------------------------
# Auto-run with automatic shutdown
# ------------------------------------------------------------

completed_configuration = RunnerConfiguration(
    auto_startup=True,
    auto_shutdown=True,
)

completed_service = EnterprisePlatformRunnerService(
    configuration=completed_configuration,
)

completed_result = completed_service.run()

assert completed_result.succeeded is True

assert (
    completed_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert completed_service.startup_result is not None
assert completed_service.shutdown_result is completed_result
assert completed_service.is_stopped is True


# ------------------------------------------------------------
# Automatic startup disabled
# ------------------------------------------------------------

disabled_configuration = RunnerConfiguration(
    auto_startup=False,
)

disabled_service = EnterprisePlatformRunnerService(
    configuration=disabled_configuration,
)

try:
    disabled_service.run()
except RunnerLifecycleError:
    pass
else:
    raise AssertionError(
        "Expected RunnerLifecycleError."
    )


print(
    "✅ Implementation 26.7 Part 2 — "
    "Enterprise platform runner service lifecycle "
    "validation passed."
)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 26.8 — Enterprise Platform Runner Main
# Implementation 28 — Enterprise Release Remediation
# Platform release: v3.0.0
# Canonical namespace: src.*
# =============================================================================

import importlib
import sys


# -----------------------------------------------------------------------------
# Reset the runner namespace
#
# Earlier validation cells reload individual runner modules. That can leave
# multiple generations of RunnerConfiguration, RunnerExecutionResult, and
# related classes in memory.
#
# Release validation therefore rebuilds the complete src.runner namespace
# atomically before validating the public runner entry point.
# -----------------------------------------------------------------------------

runner_modules = [
    module_name
    for module_name in list(sys.modules)
    if (
        module_name == "src.runner"
        or module_name.startswith("src.runner.")
    )
]

for module_name in sorted(
    runner_modules,
    key=lambda value: value.count("."),
    reverse=True,
):
    sys.modules.pop(module_name, None)

importlib.invalidate_caches()


# -----------------------------------------------------------------------------
# Import one canonical generation of the runner package
# -----------------------------------------------------------------------------

runner_configuration_module = importlib.import_module(
    "src.runner.configuration"
)

runner_models_module = importlib.import_module(
    "src.runner.models"
)

runner_service_module = importlib.import_module(
    "src.runner.service"
)

runner_main_module = importlib.import_module(
    "src.runner.main"
)


RunnerConfiguration = (
    runner_configuration_module.RunnerConfiguration
)

RunnerExecutionResult = (
    runner_models_module.RunnerExecutionResult
)

EnterprisePlatformRunnerService = (
    runner_service_module.EnterprisePlatformRunnerService
)

EnterprisePlatformRunner = (
    runner_main_module.EnterprisePlatformRunner
)

main = runner_main_module.main


# -----------------------------------------------------------------------------
# Canonical class identity
# -----------------------------------------------------------------------------

assert (
    runner_main_module.RunnerConfiguration
    is RunnerConfiguration
)

assert (
    runner_main_module.EnterprisePlatformRunner
    is EnterprisePlatformRunner
)


# -----------------------------------------------------------------------------
# Runner construction
# -----------------------------------------------------------------------------

configuration = RunnerConfiguration()

runner = EnterprisePlatformRunner(
    configuration=configuration,
)

assert runner.configuration is configuration

assert isinstance(
    runner.configuration,
    RunnerConfiguration,
)

assert isinstance(
    runner.service,
    EnterprisePlatformRunnerService,
)


# -----------------------------------------------------------------------------
# Runner execution
# -----------------------------------------------------------------------------

result = runner.run()

assert isinstance(
    result,
    RunnerExecutionResult,
)

assert result.succeeded is True
assert result.exit_code == 0


# -----------------------------------------------------------------------------
# Public main entry point
# -----------------------------------------------------------------------------

assert callable(main)

main_exit_code = main()

assert main_exit_code == 0


# -----------------------------------------------------------------------------
# Final acceptance
# -----------------------------------------------------------------------------

print("=" * 72)
print("ENTERPRISE PLATFORM RUNNER MAIN VALIDATION")
print("=" * 72)

print("Platform release       : v3.0.0")
print("Canonical namespace    : src.*")
print("Implementation         : 26.8")
print("Release remediation    : 28")

print(
    f"Configuration          : "
    f"{type(configuration).__module__}."
    f"{type(configuration).__name__}"
)

print(
    f"Runner service         : "
    f"{type(runner.service).__module__}."
    f"{type(runner.service).__name__}"
)

print(
    f"Execution result       : "
    f"{type(result).__module__}."
    f"{type(result).__name__}"
)

print(f"Runner succeeded       : {result.succeeded}")
print(f"Runner exit code       : {result.exit_code}")
print(f"Main exit code         : {main_exit_code}")

print("Runner main status     : PASSED")
print("=" * 72)

# COMMAND ----------

# ============================================================
# Implementation 26.9
# Enterprise Runner Package
# ============================================================

import importlib

import src.runner
importlib.reload(src.runner)

from src.runner import *

assert RUNNER_PACKAGE_VERSION == "1.0.0"

configuration = RunnerConfiguration()

startup = EnterpriseRunnerStartup(
    configuration=configuration,
)

shutdown = EnterpriseRunnerShutdown(
    configuration=configuration,
)

service = EnterprisePlatformRunnerService(
    configuration=configuration,
)

runner = EnterprisePlatformRunner(
    configuration=configuration,
)

assert isinstance(
    configuration,
    RunnerConfiguration,
)

assert isinstance(
    startup,
    EnterpriseRunnerStartup,
)

assert isinstance(
    shutdown,
    EnterpriseRunnerShutdown,
)

assert isinstance(
    service,
    EnterprisePlatformRunnerService,
)

assert isinstance(
    runner,
    EnterprisePlatformRunner,
)

assert main() == 0

print(
    "✅ Implementation 26.9 — "
    "Enterprise runner package validation passed."
)

# COMMAND ----------

# ============================================================
# Implementation 28
# Release Gate 2 — Forecast Modeling Public API Validation
# ============================================================

import importlib

import src.forecast.modeling
importlib.reload(src.forecast.modeling)

from src.forecast import modeling


expected_exports = {
    # Core contracts
    "BaseForecastModel",
    "ForecastModelCapability",
    "ForecastModelCategory",
    "ForecastModelLifecycle",
    "ForecastModelMetadataProvider",
    "ForecastModelState",

    # Contexts and aliases
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
}

assert set(modeling.__all__) == expected_exports

for exported_name in modeling.__all__:
    assert hasattr(
        modeling,
        exported_name,
    ), f"Missing modeling export: {exported_name}"

    assert getattr(
        modeling,
        exported_name,
    ) is not None, (
        f"Modeling export resolved to None: {exported_name}"
    )

assert issubclass(
    modeling.BaseForecastModel,
    object,
)

assert callable(
    modeling.register_forecast_model,
)

print(
    "✅ Implementation 28 — "
    "Forecast modeling public API validation passed."
)

# COMMAND ----------

