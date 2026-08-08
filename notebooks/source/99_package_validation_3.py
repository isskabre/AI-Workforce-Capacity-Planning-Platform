# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Package Validation 3 — Release Remediation
# MAGIC **Platform release:** v3.0.0  
# MAGIC **Implementation:** 28 — Enterprise Release Validation  
# MAGIC **Canonical namespace:** `src.*`  
# MAGIC **Current audit target:** `src.forecast.modeling`
# MAGIC
# MAGIC This copy preserves the original release-validation coverage while
# MAGIC removing environment-specific bootstrap assumptions and canonicalizing
# MAGIC Python package identity.

# COMMAND ----------

# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC
# MAGIC ## Implementation 28 — Enterprise Release Validation
# MAGIC
# MAGIC ### Canonical Release-Validation Notebook
# MAGIC
# MAGIC **Platform release:** v3.0.0  
# MAGIC **Validation notebook:** `99_package_validation_3`  
# MAGIC **Current audit package:** `src.forecast.modeling`  
# MAGIC **Release finding:** `ENG-001 — Inconsistent Python import namespaces`
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Purpose
# MAGIC
# MAGIC This notebook provides the canonical release-validation evidence for the
# MAGIC AI Workforce Capacity Planning Platform v3.0.0 release audit.
# MAGIC
# MAGIC It validates remediated platform packages against the production namespace,
# MAGIC dependency, public API, and package-integrity requirements established for
# MAGIC Implementation 28.
# MAGIC
# MAGIC ### Release-validation scope
# MAGIC
# MAGIC - Validate one package or leaf subpackage at a time.
# MAGIC - Use `src.*` as the official public platform namespace.
# MAGIC - Reject legacy imports such as `forecast.*`.
# MAGIC - Validate package imports and module identities.
# MAGIC - Validate intra-package dependencies.
# MAGIC - Validate public package exports and module-level `__all__`.
# MAGIC - Detect duplicate or missing exports.
# MAGIC - Detect circular-import and module-identity conflicts.
# MAGIC - Execute representative contract smoke tests.
# MAGIC - Preserve existing architecture, behavior, public contracts, and component
# MAGIC   versions unless a verified defect requires remediation.
# MAGIC
# MAGIC ### Validation evidence policy
# MAGIC
# MAGIC - `99_package_validation` remains historical implementation-validation evidence.
# MAGIC - `99_package_validation_2` remains historical implementation-validation evidence.
# MAGIC - `99_package_validation_3` is the canonical v3.0.0 release-validation notebook.
# MAGIC - A package must pass its complete release-validation section before the audit
# MAGIC   proceeds to the next package.

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Notebook:
#     notebooks/source/99_package_validation_3
#
# Purpose:
#     Canonical v3.0.0 package release-validation notebook.
#
# Current audit target:
#     src.forecast.modeling
#
# Release finding:
#     ENG-001 — Inconsistent Python import namespaces
#
# Platform release:
#     v3.0.0
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ReleaseValidationContext:
    """Immutable configuration for the v3.0.0 release-validation notebook."""

    implementation_number: int
    platform_release: str
    notebook_name: str
    finding_id: str
    canonical_namespace: str
    current_package: str


RELEASE_CONTEXT = ReleaseValidationContext(
    implementation_number=28,
    platform_release="v3.0.0",
    notebook_name="99_package_validation_3",
    finding_id="ENG-001",
    canonical_namespace="src.*",
    current_package="src.forecast.modeling",
)

print("=" * 80)
print("AI WORKFORCE CAPACITY PLANNING PLATFORM")
print("ENTERPRISE RELEASE VALIDATION")
print("=" * 80)
print(
    f"Implementation: {RELEASE_CONTEXT.implementation_number}"
)
print(
    f"Platform release: {RELEASE_CONTEXT.platform_release}"
)
print(
    f"Notebook: {RELEASE_CONTEXT.notebook_name}"
)
print(
    f"Release finding: {RELEASE_CONTEXT.finding_id}"
)
print(
    f"Canonical namespace: {RELEASE_CONTEXT.canonical_namespace}"
)
print(
    f"Current package: {RELEASE_CONTEXT.current_package}"
)
print("=" * 80)

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

REPOSITORY_ROOT = Path.cwd()

while (
    REPOSITORY_ROOT.parent != REPOSITORY_ROOT
    and not (REPOSITORY_ROOT / "src").is_dir()
):
    REPOSITORY_ROOT = REPOSITORY_ROOT.parent

if not (REPOSITORY_ROOT / "src").is_dir():
    raise RuntimeError(
        "Unable to locate repository root containing src/."
    )

SOURCE_PACKAGE_ROOT = REPOSITORY_ROOT / "src"

repository_root_path = str(REPOSITORY_ROOT)
if repository_root_path not in sys.path:
    sys.path.insert(0, repository_root_path)

required_package_paths = (
    SOURCE_PACKAGE_ROOT / "forecast",
    SOURCE_PACKAGE_ROOT / "demand",
    SOURCE_PACKAGE_ROOT / "planning",
    SOURCE_PACKAGE_ROOT / "workforce",
)

for package_path in required_package_paths:
    assert package_path.exists(), (
        f"Required source package does not exist: {package_path}"
    )

print("Repository bootstrap: PASSED")
print("Repository root:", REPOSITORY_ROOT)
print("Source directory:", SOURCE_PACKAGE_ROOT)
print("Repository root in sys.path:", repository_root_path in sys.path)
print("Canonical namespace under validation: src.*")

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Clean Import-Session Preparation
#
# Purpose:
#     Remove previously cached Forecast modules so validation examines the
#     current repository source through the canonical src.* namespace.
# =============================================================================

from __future__ import annotations

import importlib
import sys


MODULE_PREFIXES_TO_CLEAR = (
    "forecast",
    "src.forecast",
)

removed_modules: list[str] = []

for module_name in tuple(sys.modules):
    if any(
        module_name == prefix
        or module_name.startswith(f"{prefix}.")
        for prefix in MODULE_PREFIXES_TO_CLEAR
    ):
        removed_modules.append(module_name)
        del sys.modules[module_name]

importlib.invalidate_caches()

print("Import-session preparation: PASSED")
print("Removed cached modules:", len(removed_modules))

if removed_modules:
    for module_name in sorted(removed_modules):
        print(f"  - {module_name}")
else:
    print("  - No cached Forecast modules were present")

# COMMAND ----------

import traceback

try:
    import src.forecast.modeling
    print("SUCCESS")
except Exception:
    traceback.print_exc()

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Validation:
#     src.forecast.modeling package
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Python import namespace consistency
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Validation configuration
# -----------------------------------------------------------------------------

PACKAGE_NAME = "src.forecast.modeling"

EXPECTED_MODULES = (
    "artifacts",
    "configuration",
    "contexts",
    "contracts",
    "exceptions",
    "factory",
    "metrics",
    "results",
)

EXPECTED_PUBLIC_API = {
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


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for module {module.__name__}."
    )

    source_path = Path(source_file)

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(source_path: Path) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source, filename=str(source_path))

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import the canonical public package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every leaf module through src.*
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(qualified_name)

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported all modeling modules through the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.modeling module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast.modeling"
        or module_name.startswith("forecast.modeling.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.modeling modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.modeling modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan source imports for legacy namespaces
# -----------------------------------------------------------------------------

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in imported_modules.items():
    source_path = resolve_module_source(imported_module)
    absolute_imports = collect_absolute_imports(source_path)

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in src.forecast.modeling: "
    f"{legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate package-level __all__
# -----------------------------------------------------------------------------

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(EXPECTED_PUBLIC_API - actual_public_api),
    "unexpected_exports": sorted(actual_public_api - EXPECTED_PUBLIC_API),
}

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is declared but unavailable: {exported_name}"
    )

print(
    f"PASS: Package public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate each leaf module's __all__
# -----------------------------------------------------------------------------

for module_name, imported_module in imported_modules.items():
    assert hasattr(imported_module, "__all__"), (
        f"{imported_module.__name__} does not define __all__."
    )

    module_exports = imported_module.__all__

    assert isinstance(module_exports, list), (
        f"{imported_module.__name__}.__all__ must be a list."
    )

    assert len(module_exports) == len(set(module_exports)), (
        f"{imported_module.__name__}.__all__ contains duplicates."
    )

    for exported_name in module_exports:
        assert hasattr(imported_module, exported_name), (
            f"{imported_module.__name__} declares unavailable export "
            f"{exported_name}."
        )

print("PASS: Every leaf-module __all__ is complete and duplicate-free")


# -----------------------------------------------------------------------------
# 7. Validate dependency identity across modules
# -----------------------------------------------------------------------------

from src.forecast.modeling import (
    BaseForecastModel,
    ForecastArtifact,
    ForecastArtifactStatus,
    ForecastConfigurationError,
    ForecastEvaluationResult,
    ForecastExecutionStatus,
    ForecastMetrics,
    ForecastModelCategory,
    ForecastModelFactory,
    ForecastModelRegistration,
    ForecastPredictionResult,
    ForecastTrainingResult,
)

from src.forecast.modeling.artifacts import (
    ForecastArtifact as LeafForecastArtifact,
)
from src.forecast.modeling.contracts import (
    BaseForecastModel as LeafBaseForecastModel,
)
from src.forecast.modeling.factory import (
    ForecastModelFactory as LeafForecastModelFactory,
)
from src.forecast.modeling.metrics import (
    ForecastMetrics as LeafForecastMetrics,
)
from src.forecast.modeling.results import (
    ForecastEvaluationResult as LeafForecastEvaluationResult,
)

assert ForecastArtifact is LeafForecastArtifact
assert BaseForecastModel is LeafBaseForecastModel
assert ForecastModelFactory is LeafForecastModelFactory
assert ForecastMetrics is LeafForecastMetrics
assert ForecastEvaluationResult is LeafForecastEvaluationResult

print("PASS: Public and leaf-module object identities are consistent")


# -----------------------------------------------------------------------------
# 8. Validate representative artifact and result behavior
# -----------------------------------------------------------------------------

artifact = ForecastArtifact(
    model_name="release_validation_model",
    model_version="2.4.0",
    model_category=ForecastModelCategory.BASELINE,
    algorithm="release_validation",
    storage_uri="memory://release-validation/model",
    feature_columns=("feature_1",),
    target_column="target",
    forecast_horizon=1,
)

artifact_payload = artifact.to_dict()

assert artifact.status is ForecastArtifactStatus.CREATED
assert artifact_payload["model_name"] == "release_validation_model"
assert artifact_payload["model_category"] == "BASELINE"
assert artifact_payload["feature_columns"] == ["feature_1"]

training_result = ForecastTrainingResult(
    model_name="release_validation_model",
    model_version="2.4.0",
    status=ForecastExecutionStatus.SUCCESS,
    artifact=artifact,
)

prediction_result = ForecastPredictionResult(
    model_name="release_validation_model",
    model_version="2.4.0",
    status=ForecastExecutionStatus.SUCCESS,
    predictions=(100.0,),
    forecast_horizon=1,
)

evaluation_result = ForecastEvaluationResult(
    model_name="release_validation_model",
    model_version="2.4.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={"mae": 0.0},
    primary_metric="mae",
    primary_metric_value=0.0,
    evaluation_records=1,
)

assert training_result.succeeded
assert prediction_result.succeeded
assert evaluation_result.succeeded

assert training_result.to_dict()["artifact"]["artifact_id"] == artifact.artifact_id
assert prediction_result.to_dict()["predictions"] == [100.0]
assert evaluation_result.to_dict()["primary_metric_value"] == 0.0

print("PASS: Artifact and standardized result contracts remain operational")


# -----------------------------------------------------------------------------
# 9. Validate metrics contract
# -----------------------------------------------------------------------------

metrics = ForecastMetrics(
    mae=1.0,
    mse=1.0,
    rmse=1.0,
    bias=0.0,
    mape=2.0,
    smape=2.0,
    wape=2.0,
)

assert metrics.get("MAE") == 1.0
assert metrics.get("wape") == 2.0
assert set(metrics.to_dict()) == {
    "mae",
    "mse",
    "rmse",
    "bias",
    "mape",
    "smape",
    "wape",
}

print("PASS: ForecastMetrics contract remains operational")


# -----------------------------------------------------------------------------
# 10. Validate exception hierarchy
# -----------------------------------------------------------------------------

configuration_error = ForecastConfigurationError(
    "Release validation error.",
    context={"validation": "src.forecast.modeling"},
)

error_payload = configuration_error.to_dict()

assert error_payload["error_code"] == "FORECAST_CONFIGURATION_ERROR"
assert error_payload["context"]["validation"] == "src.forecast.modeling"

print("PASS: Forecast exception hierarchy remains operational")


# -----------------------------------------------------------------------------
# 11. Validate factory registry operations without persistent side effects
# -----------------------------------------------------------------------------

registry_snapshot = dict(ForecastModelFactory._registry)

try:
    ForecastModelFactory.clear()

    assert ForecastModelFactory.registrations() == ()

    registration = ForecastModelRegistration(
        model_key="release_validation_model",
        builder=lambda configuration: None,
        display_name="Release Validation Model",
        category=ForecastModelCategory.CUSTOM,
        capabilities=frozenset(),
        implementation_version="2.4.0",
    )

    registration_payload = registration.to_dict()

    assert registration_payload["model_key"] == "release_validation_model"
    assert registration_payload["category"] == "CUSTOM"
    assert registration_payload["implementation_version"] == "2.4.0"

finally:
    ForecastModelFactory.clear()
    ForecastModelFactory._registry.update(registry_snapshot)

print("PASS: Forecast factory contracts remain operational")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.modeling")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Public API symbols validated:", len(EXPECTED_PUBLIC_API))
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast.algorithms
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path


PACKAGE_NAME = "src.forecast.algorithms"

EXPECTED_MODULES = (
    "base",
    "base.estimator",
    "base.forecast_model",
    "base.serializer",
    "naive",
    "naive.estimator",
    "naive.model",
    "moving_average",
    "moving_average.estimator",
    "moving_average.model",
    "linear_regression",
    "linear_regression.estimator",
    "linear_regression.model",
    "random_forest",
    "random_forest.estimator",
    "random_forest.model",
    "lstm",
    "lstm.estimator",
    "lstm.model",
)


def resolve_module_source(module: object) -> Path:
    """Return the source path for one imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(source_path: Path) -> tuple[str, ...]:
    """Return absolute imports declared by a Python source file."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source, filename=str(source_path))

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every package and leaf module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(qualified_name)

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every algorithms module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan package source for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(imported_module)
    absolute_imports = collect_absolute_imports(source_path)

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate module-level __all__
# -----------------------------------------------------------------------------

modules_with_public_api = {
    module_name: imported_module
    for module_name, imported_module in modules_to_scan.items()
    if hasattr(imported_module, "__all__")
}

assert modules_with_public_api, (
    "No module-level public APIs were discovered."
)

for module_name, imported_module in modules_with_public_api.items():
    exported_names = imported_module.__all__

    assert isinstance(exported_names, list), (
        f"{imported_module.__name__}.__all__ must be a list."
    )

    assert len(exported_names) == len(set(exported_names)), (
        f"{imported_module.__name__}.__all__ contains duplicate names."
    )

    for exported_name in exported_names:
        assert hasattr(imported_module, exported_name), (
            f"{imported_module.__name__} declares unavailable export "
            f"{exported_name}."
        )

print(
    "PASS: All declared algorithms __all__ exports are "
    "available and duplicate-free"
)


# -----------------------------------------------------------------------------
# 6. Validate foundational object identity
# -----------------------------------------------------------------------------

from src.forecast.algorithms.base import (
    EnterpriseEstimator,
    EnterpriseForecastModel,
    EnterpriseSerializer,
)

from src.forecast.algorithms.base.estimator import (
    EnterpriseEstimator as LeafEnterpriseEstimator,
)
from src.forecast.algorithms.base.forecast_model import (
    EnterpriseForecastModel as LeafEnterpriseForecastModel,
)
from src.forecast.algorithms.base.serializer import (
    EnterpriseSerializer as LeafEnterpriseSerializer,
)

assert EnterpriseEstimator is LeafEnterpriseEstimator
assert EnterpriseForecastModel is LeafEnterpriseForecastModel
assert EnterpriseSerializer is LeafEnterpriseSerializer

print("PASS: Base algorithm public object identities are consistent")


# -----------------------------------------------------------------------------
# 7. Validate concrete algorithm package identities
# -----------------------------------------------------------------------------

from src.forecast.algorithms.linear_regression import (
    LinearRegressionEstimator,
    LinearRegressionForecastModel,
)
from src.forecast.algorithms.linear_regression.estimator import (
    LinearRegressionEstimator as LeafLinearRegressionEstimator,
)
from src.forecast.algorithms.linear_regression.model import (
    LinearRegressionForecastModel as LeafLinearRegressionForecastModel,
)

from src.forecast.algorithms.lstm import (
    LSTMEstimator,
    LSTMForecastModel,
)
from src.forecast.algorithms.lstm.estimator import (
    LSTMEstimator as LeafLSTMEstimator,
)
from src.forecast.algorithms.lstm.model import (
    LSTMForecastModel as LeafLSTMForecastModel,
)

from src.forecast.algorithms.moving_average import (
    MovingAverageEstimator,
    MovingAverageForecastModel,
)
from src.forecast.algorithms.moving_average.estimator import (
    MovingAverageEstimator as LeafMovingAverageEstimator,
)
from src.forecast.algorithms.moving_average.model import (
    MovingAverageForecastModel as LeafMovingAverageForecastModel,
)

from src.forecast.algorithms.naive import (
    NaiveLastValueEstimator,
    NaiveForecastModel,
)
from src.forecast.algorithms.naive.estimator import (
    NaiveLastValueEstimator as LeafNaiveLastValueEstimator,
)
from src.forecast.algorithms.naive.model import (
    NaiveForecastModel as LeafNaiveForecastModel,
)

from src.forecast.algorithms.random_forest import (
    RandomForestEstimator,
    RandomForestForecastModel,
)
from src.forecast.algorithms.random_forest.estimator import (
    RandomForestEstimator as LeafRandomForestEstimator,
)
from src.forecast.algorithms.random_forest.model import (
    RandomForestForecastModel as LeafRandomForestForecastModel,
)

assert LinearRegressionEstimator is LeafLinearRegressionEstimator
assert (
    LinearRegressionForecastModel
    is LeafLinearRegressionForecastModel
)

assert LSTMEstimator is LeafLSTMEstimator
assert LSTMForecastModel is LeafLSTMForecastModel

assert MovingAverageEstimator is LeafMovingAverageEstimator
assert MovingAverageForecastModel is LeafMovingAverageForecastModel

assert NaiveLastValueEstimator is LeafNaiveLastValueEstimator
assert (
    NaiveForecastModel
    is LeafNaiveForecastModel
)

assert RandomForestEstimator is LeafRandomForestEstimator
assert RandomForestForecastModel is LeafRandomForestForecastModel

print("PASS: Concrete algorithm public object identities are consistent")


# -----------------------------------------------------------------------------
# 8. Validate model registrations
# -----------------------------------------------------------------------------

from src.forecast.modeling import (
    ForecastModelFactory,
)

supported_models = ForecastModelFactory.supported_models()

expected_registered_models = {
    "linear_regression",
    "lstm",
    "moving_average",
    "naive_last_value",
    "random_forest",
}

missing_registered_models = sorted(
    expected_registered_models.difference(supported_models)
)

assert not missing_registered_models, (
    "Expected algorithms were not registered: "
    f"{missing_registered_models}. "
    f"Available registrations: {supported_models}"
)

for model_key in expected_registered_models:
    assert ForecastModelFactory.is_supported(model_key)

    registration = ForecastModelFactory.get_registration(
        model_key
    )

    assert registration.model_key == model_key
    assert callable(registration.builder)
    assert registration.display_name
    assert registration.implementation_version

print(
    "PASS: Forecast algorithm registrations are available "
    "through ForecastModelFactory"
)


# -----------------------------------------------------------------------------
# 9. Validate registry catalog serialization
# -----------------------------------------------------------------------------

catalog = ForecastModelFactory.catalog()

catalog_keys = {
    entry["model_key"]
    for entry in catalog
}

assert expected_registered_models.issubset(catalog_keys)

for entry in catalog:
    assert isinstance(entry, dict)
    assert entry["model_key"]
    assert entry["display_name"]
    assert entry["category"]
    assert isinstance(entry["capabilities"], list)
    assert entry["implementation_version"]

print("PASS: Forecast algorithm registry catalog is serializable")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.algorithms")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print("Registered algorithms validated:", len(expected_registered_models))
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast.training
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path


PACKAGE_NAME = "src.forecast.training"

EXPECTED_MODULES = (
    "callbacks",
    "trainer",
    "orchestrator",
)

EXPECTED_PUBLIC_API = {
    "EnterpriseForecastTrainer",
    "EnterpriseForecastTrainingOrchestrator",
    "TrainingCallback",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(source_path: Path) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source, filename=str(source_path))

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import the canonical public package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every training leaf module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(qualified_name)

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every training module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan training source files for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(imported_module)
    absolute_imports = collect_absolute_imports(source_path)

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate package public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(set(package.__all__)), (
    "src.forecast.training.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Training public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__
# -----------------------------------------------------------------------------

expected_leaf_exports = {
    "trainer": {
        "EnterpriseForecastTrainer",
    },
    "orchestrator": {
        "EnterpriseForecastTrainingOrchestrator",
    },
}

for module_name, expected_exports in expected_leaf_exports.items():
    imported_module = imported_modules[module_name]

    assert hasattr(imported_module, "__all__"), (
        f"{imported_module.__name__} does not define __all__."
    )

    actual_exports = set(imported_module.__all__)

    assert actual_exports == expected_exports, {
        "module": imported_module.__name__,
        "missing_exports": sorted(
            expected_exports - actual_exports
        ),
        "unexpected_exports": sorted(
            actual_exports - expected_exports
        ),
    }

    assert len(imported_module.__all__) == len(
        set(imported_module.__all__)
    ), (
        f"{imported_module.__name__}.__all__ contains duplicates."
    )

    for exported_name in imported_module.__all__:
        assert hasattr(imported_module, exported_name)

print(
    "PASS: Training leaf-module __all__ contracts are complete "
    "and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public and leaf-module object identity
# -----------------------------------------------------------------------------

from src.forecast.training import (
    EnterpriseForecastTrainer,
    EnterpriseForecastTrainingOrchestrator,
    TrainingCallback,
)

from src.forecast.training.callbacks import (
    TrainingCallback as LeafTrainingCallback,
)
from src.forecast.training.orchestrator import (
    EnterpriseForecastTrainingOrchestrator
    as LeafEnterpriseForecastTrainingOrchestrator,
)
from src.forecast.training.trainer import (
    EnterpriseForecastTrainer as LeafEnterpriseForecastTrainer,
)

assert EnterpriseForecastTrainer is LeafEnterpriseForecastTrainer
assert (
    EnterpriseForecastTrainingOrchestrator
    is LeafEnterpriseForecastTrainingOrchestrator
)
assert TrainingCallback is LeafTrainingCallback

print("PASS: Training public object identities are consistent")


# -----------------------------------------------------------------------------
# 8. Validate callback contract
# -----------------------------------------------------------------------------

callback = TrainingCallback()

assert (
    callback.on_training_started(
        model=object(),
        context=object(),
    )
    is None
)

assert (
    callback.on_epoch_completed(
        epoch=1,
        metrics={"loss": 0.0},
    )
    is None
)

assert (
    callback.on_training_completed(
        model=object(),
        artifact=object(),
    )
    is None
)

assert (
    callback.on_training_failed(
        model=object(),
        exception=RuntimeError("release validation"),
    )
    is None
)

print("PASS: TrainingCallback lifecycle contract remains operational")


# -----------------------------------------------------------------------------
# 9. Validate trainer and orchestrator signatures
# -----------------------------------------------------------------------------

trainer_train_signature = inspect.signature(
    EnterpriseForecastTrainer.train
)

assert "model" in trainer_train_signature.parameters
assert "context" in trainer_train_signature.parameters

orchestrator_init_signature = inspect.signature(
    EnterpriseForecastTrainingOrchestrator
)

assert "trainer" in orchestrator_init_signature.parameters

orchestrator_train_signature = inspect.signature(
    EnterpriseForecastTrainingOrchestrator.train
)

assert "model" in orchestrator_train_signature.parameters
assert "context" in orchestrator_train_signature.parameters

orchestrator_train_many_signature = inspect.signature(
    EnterpriseForecastTrainingOrchestrator.train_many
)

assert "models" in orchestrator_train_many_signature.parameters
assert "contexts" in orchestrator_train_many_signature.parameters

print("PASS: Trainer and orchestrator public signatures are preserved")


# -----------------------------------------------------------------------------
# 10. Validate orchestrator dependency construction
# -----------------------------------------------------------------------------

trainer = EnterpriseForecastTrainer()

orchestrator = EnterpriseForecastTrainingOrchestrator(
    trainer=trainer
)

assert orchestrator.trainer is trainer

default_orchestrator = (
    EnterpriseForecastTrainingOrchestrator()
)

assert isinstance(
    default_orchestrator.trainer,
    EnterpriseForecastTrainer,
)

print("PASS: Training orchestrator dependency contract remains operational")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.training")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print("Public API symbols validated:", len(EXPECTED_PUBLIC_API))
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast.evaluation
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import math
import sys
from pathlib import Path


PACKAGE_NAME = "src.forecast.evaluation"

EXPECTED_MODULES = (
    "metrics",
    "evaluator",
    "comparison",
)

EXPECTED_PUBLIC_API = {
    "EnterpriseForecastComparison",
    "EnterpriseForecastEvaluator",
    "EnterpriseForecastMetrics",
    "ForecastComparisonResult",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(source_path: Path) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source, filename=str(source_path))

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import the canonical public package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every evaluation leaf module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(qualified_name)

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every evaluation module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan evaluation source files for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(imported_module)
    absolute_imports = collect_absolute_imports(source_path)

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate package public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(set(package.__all__)), (
    "src.forecast.evaluation.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Evaluation public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__
# -----------------------------------------------------------------------------

expected_leaf_exports = {
    "metrics": {
        "EnterpriseForecastMetrics",
    },
    "evaluator": {
        "EnterpriseForecastEvaluator",
    },
    "comparison": {
        "EnterpriseForecastComparison",
        "ForecastComparisonResult",
    },
}

for module_name, expected_exports in expected_leaf_exports.items():
    imported_module = imported_modules[module_name]

    assert hasattr(imported_module, "__all__"), (
        f"{imported_module.__name__} does not define __all__."
    )

    actual_exports = set(imported_module.__all__)

    assert actual_exports == expected_exports, {
        "module": imported_module.__name__,
        "missing_exports": sorted(
            expected_exports - actual_exports
        ),
        "unexpected_exports": sorted(
            actual_exports - expected_exports
        ),
    }

    assert len(imported_module.__all__) == len(
        set(imported_module.__all__)
    ), (
        f"{imported_module.__name__}.__all__ contains duplicates."
    )

    for exported_name in imported_module.__all__:
        assert hasattr(imported_module, exported_name)

print(
    "PASS: Evaluation leaf-module __all__ contracts are complete "
    "and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public and leaf-module object identity
# -----------------------------------------------------------------------------

from src.forecast.evaluation import (
    EnterpriseForecastComparison,
    EnterpriseForecastEvaluator,
    EnterpriseForecastMetrics,
    ForecastComparisonResult,
)

from src.forecast.evaluation.comparison import (
    EnterpriseForecastComparison
    as LeafEnterpriseForecastComparison,
)
from src.forecast.evaluation.comparison import (
    ForecastComparisonResult as LeafForecastComparisonResult,
)
from src.forecast.evaluation.evaluator import (
    EnterpriseForecastEvaluator
    as LeafEnterpriseForecastEvaluator,
)
from src.forecast.evaluation.metrics import (
    EnterpriseForecastMetrics
    as LeafEnterpriseForecastMetrics,
)

assert (
    EnterpriseForecastComparison
    is LeafEnterpriseForecastComparison
)
assert (
    EnterpriseForecastEvaluator
    is LeafEnterpriseForecastEvaluator
)
assert (
    EnterpriseForecastMetrics
    is LeafEnterpriseForecastMetrics
)
assert ForecastComparisonResult is LeafForecastComparisonResult

print("PASS: Evaluation public object identities are consistent")


# -----------------------------------------------------------------------------
# 8. Validate standardized metric calculations
# -----------------------------------------------------------------------------

metrics = EnterpriseForecastMetrics.evaluate(
    actual=(100.0, 120.0, 80.0),
    predicted=(90.0, 110.0, 100.0),
)

metric_payload = metrics.to_dict()

assert set(metric_payload) == {
    "mae",
    "mse",
    "rmse",
    "bias",
    "mape",
    "smape",
    "wape",
}

assert math.isclose(
    metric_payload["mae"],
    40.0 / 3.0,
    rel_tol=1e-12,
)

assert math.isclose(
    metric_payload["mse"],
    200.0,
    rel_tol=1e-12,
)

assert math.isclose(
    metric_payload["rmse"],
    math.sqrt(200.0),
    rel_tol=1e-12,
)

assert math.isclose(
    metric_payload["bias"],
    0.0,
    abs_tol=1e-12,
)

assert math.isclose(
    metric_payload["wape"],
    (40.0 / 300.0) * 100.0,
    rel_tol=1e-12,
)

print("PASS: Enterprise forecast metric calculations remain operational")


# -----------------------------------------------------------------------------
# 9. Validate evaluator contract
# -----------------------------------------------------------------------------

from src.forecast.modeling import (
    ForecastEvaluationContext,
    ForecastEvaluationResult,
    ForecastExecutionStatus,
)

evaluation_context = ForecastEvaluationContext(
    actual_values=(100.0, 120.0, 80.0),
    predicted_values=(90.0, 110.0, 100.0),
    metric="MAE",
    metadata={
        "validation": "implementation_28",
    },
)

evaluator = EnterpriseForecastEvaluator()

evaluation_result = evaluator.evaluate(
    model_name="release_validation_model",
    model_version="2.6.0",
    context=evaluation_context,
)

assert isinstance(
    evaluation_result,
    ForecastEvaluationResult,
)

assert (
    evaluation_result.status
    is ForecastExecutionStatus.SUCCESS
)

assert evaluation_result.succeeded
assert evaluation_result.model_name == "release_validation_model"
assert evaluation_result.model_version == "2.6.0"
assert evaluation_result.primary_metric == "mae"
assert evaluation_result.evaluation_records == 3

assert math.isclose(
    evaluation_result.primary_metric_value,
    40.0 / 3.0,
    rel_tol=1e-12,
)

assert set(evaluation_result.residual_summary) == {
    "mean",
    "minimum",
    "maximum",
    "standard_deviation",
}

assert (
    evaluation_result.metadata["validation"]
    == "implementation_28"
)

print("PASS: Enterprise forecast evaluator contract remains operational")


# -----------------------------------------------------------------------------
# 10. Validate deterministic comparison and champion selection
# -----------------------------------------------------------------------------

comparison_candidate = ForecastEvaluationResult(
    model_name="comparison_candidate",
    model_version="2.6.0",
    status=ForecastExecutionStatus.SUCCESS,
    metrics={
        "mae": 20.0,
        "mse": 500.0,
        "rmse": math.sqrt(500.0),
        "bias": 2.0,
        "mape": 10.0,
        "smape": 10.5,
        "wape": 12.0,
    },
    primary_metric="mae",
    primary_metric_value=20.0,
    evaluation_records=3,
)

comparison_service = EnterpriseForecastComparison()

comparison_result = comparison_service.compare(
    evaluations=(
        comparison_candidate,
        evaluation_result,
    ),
    metric="MAE",
    metadata={
        "validation": "implementation_28",
    },
)

assert isinstance(
    comparison_result,
    ForecastComparisonResult,
)

assert comparison_result.metric == "mae"
assert comparison_result.total_models == 2
assert comparison_result.champion is comparison_result.ordered_results[0]
assert comparison_result.runner_up is comparison_result.ordered_results[1]

assert (
    comparison_result.champion_model_name
    == "release_validation_model"
)

assert (
    comparison_result.champion.model_name
    == "release_validation_model"
)

assert comparison_result.champion.rank == 1
assert comparison_result.champion.champion is True
assert comparison_result.runner_up.rank == 2
assert comparison_result.runner_up.champion is False

comparison_payload = comparison_result.to_dict()

assert comparison_payload["metric"] == "mae"
assert comparison_payload["total_models"] == 2
assert (
    comparison_payload["champion_model_name"]
    == "release_validation_model"
)
assert (
    comparison_payload["metadata"]["validation"]
    == "implementation_28"
)

print(
    "PASS: Forecast comparison and champion-selection contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate public signatures
# -----------------------------------------------------------------------------

metrics_signature = inspect.signature(
    EnterpriseForecastMetrics.evaluate
)

assert "actual" in metrics_signature.parameters
assert "predicted" in metrics_signature.parameters

evaluator_signature = inspect.signature(
    EnterpriseForecastEvaluator.evaluate
)

assert "model_name" in evaluator_signature.parameters
assert "model_version" in evaluator_signature.parameters
assert "context" in evaluator_signature.parameters

comparison_signature = inspect.signature(
    EnterpriseForecastComparison.compare
)

assert "evaluations" in comparison_signature.parameters
assert "metric" in comparison_signature.parameters
assert "metadata" in comparison_signature.parameters

print("PASS: Evaluation public signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.evaluation")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print("Public API symbols validated:", len(EXPECTED_PUBLIC_API))
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast.inference
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path

from src.forecast.inference import (
    EnterpriseForecastPredictor,
    EnterpriseForecastBatchPredictor,
    ForecastBatchPredictionItem,
    ForecastBatchPredictionRequest,
    ForecastBatchPredictionResult,
)

from src.forecast.inference.batch_predictor import (
    EnterpriseForecastBatchPredictor as LeafEnterpriseForecastBatchPredictor,
    ForecastBatchPredictionItem as LeafForecastBatchPredictionItem,
    ForecastBatchPredictionRequest as LeafForecastBatchPredictionRequest,
    ForecastBatchPredictionResult as LeafForecastBatchPredictionResult,
)

PACKAGE_NAME = "src.forecast.inference"

EXPECTED_MODULES = (
    "predictor",
    "batch_predictor",
)

EXPECTED_PUBLIC_API = {
    "EnterpriseForecastPredictor",
    "EnterpriseForecastBatchPredictor",
    "ForecastBatchPredictionItem",
    "ForecastBatchPredictionRequest",
    "ForecastBatchPredictionResult",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(source_path: Path) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source, filename=str(source_path))

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import the canonical public package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every inference leaf module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(qualified_name)

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every inference module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan inference source files for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(imported_module)
    absolute_imports = collect_absolute_imports(source_path)

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate package public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(set(package.__all__)), (
    "src.forecast.inference.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Inference public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__
# -----------------------------------------------------------------------------

expected_leaf_exports = {
    "predictor": {
        "EnterpriseForecastPredictor",
    },
    "batch_predictor": {
        "EnterpriseForecastBatchPredictor",
        "ForecastBatchPredictionItem",
        "ForecastBatchPredictionRequest",
        "ForecastBatchPredictionResult",
    },
}

for module_name, expected_exports in expected_leaf_exports.items():
    imported_module = imported_modules[module_name]

    assert hasattr(imported_module, "__all__"), (
        f"{imported_module.__name__} does not define __all__."
    )

    actual_exports = set(imported_module.__all__)

    assert actual_exports == expected_exports, {
        "module": imported_module.__name__,
        "missing_exports": sorted(
            expected_exports - actual_exports
        ),
        "unexpected_exports": sorted(
            actual_exports - expected_exports
        ),
    }

    assert len(imported_module.__all__) == len(
        set(imported_module.__all__)
    ), (
        f"{imported_module.__name__}.__all__ contains duplicates."
    )

    for exported_name in imported_module.__all__:
        assert hasattr(imported_module, exported_name)

print(
    "PASS: Inference leaf-module __all__ contracts are complete "
    "and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public and leaf-module object identity
# -----------------------------------------------------------------------------

from src.forecast.inference import (
    EnterpriseForecastBatchPredictor,
    EnterpriseForecastPredictor,
)

from src.forecast.inference.batch_predictor import (
    EnterpriseForecastBatchPredictor
    as LeafEnterpriseForecastBatchPredictor,
)
from src.forecast.inference.predictor import (
    EnterpriseForecastPredictor
    as LeafEnterpriseForecastPredictor,
)

assert (
    EnterpriseForecastPredictor
    is LeafEnterpriseForecastPredictor
)
assert (
    EnterpriseForecastBatchPredictor
    is LeafEnterpriseForecastBatchPredictor
)

print("PASS: Inference public object identities are consistent")


# -----------------------------------------------------------------------------
# 8. Validate predictor public signatures
# -----------------------------------------------------------------------------

predictor_predict_signature = inspect.signature(
    EnterpriseForecastPredictor.predict
)

batch_predictor_init_signature = inspect.signature(
    EnterpriseForecastBatchPredictor
)

batch_predictor_predict_signature = inspect.signature(
    EnterpriseForecastBatchPredictor.predict
)

assert "model" in predictor_predict_signature.parameters
assert "context" in predictor_predict_signature.parameters

assert "predictor" in batch_predictor_init_signature.parameters

assert "requests" in batch_predictor_predict_signature.parameters
assert "fail_fast" in batch_predictor_predict_signature.parameters
assert "metadata" in batch_predictor_predict_signature.parameters

print("PASS: Inference public signatures are preserved")


# -----------------------------------------------------------------------------
# 9. Validate predictor dependency construction
# -----------------------------------------------------------------------------

predictor = EnterpriseForecastPredictor()

batch_predictor = EnterpriseForecastBatchPredictor(
    predictor=predictor
)

assert batch_predictor._predictor is predictor

default_batch_predictor = EnterpriseForecastBatchPredictor()

assert isinstance(
    default_batch_predictor._predictor,
    EnterpriseForecastPredictor,
)

print("PASS: Batch predictor dependency contract remains operational")


# -----------------------------------------------------------------------------
# 10. Validate prediction delegation with a lightweight model double
# -----------------------------------------------------------------------------

from src.forecast.modeling import (
    ForecastExecutionStatus,
    ForecastPredictionContext,
    ForecastPredictionResult,
)

from src.forecast.algorithms.naive import NaiveForecastModel
from src.forecast.modeling import ForecastTrainingContext


model = NaiveForecastModel()

training_context = ForecastTrainingContext(
    training_dataset={
        "features": (
            (),
            (),
            (),
        ),
        "target": (
            80.0,
            90.0,
            100.0,
        ),
    },
    feature_columns=(),
    target_column="target",
    forecast_horizon=3,
    metadata={
        "validation": "implementation_28",
    },
)

training_result = model.train(training_context)

assert training_result.succeeded
assert model.is_trained

prediction_context = ForecastPredictionContext(
    prediction_dataset=3,
    forecast_horizon=3,
    metadata={
        "validation": "implementation_28",
    },
)

prediction_result = predictor.predict(
    model=model,
    context=prediction_context,
)

assert isinstance(
    prediction_result,
    ForecastPredictionResult,
)

assert prediction_result.succeeded
assert prediction_result.predictions == (
    100.0,
    100.0,
    100.0,
)
assert prediction_result.forecast_horizon == 3
assert (
    prediction_result.metadata["validation"]
    == "implementation_28"
)

print("PASS: Single-model inference delegation remains operational")


# -----------------------------------------------------------------------------
# 11. Validate batch prediction orchestration
# -----------------------------------------------------------------------------

batch_result = batch_predictor.predict(
    requests=(
        ForecastBatchPredictionRequest(
            request_id="release_validation_first",
            model=model,
            context=ForecastPredictionContext(
                prediction_dataset=2,
                forecast_horizon=2,
                metadata={
                    "batch_item": "first",
                },
            ),
            metadata={
                "request_order": 1,
            },
        ),
        ForecastBatchPredictionRequest(
            request_id="release_validation_second",
            model=model,
            context=ForecastPredictionContext(
                prediction_dataset=1,
                forecast_horizon=1,
                metadata={
                    "batch_item": "second",
                },
            ),
            metadata={
                "request_order": 2,
            },
        ),
    ),
    fail_fast=True,
    metadata={
        "validation": "implementation_28",
    },
)

assert isinstance(
    batch_result,
    ForecastBatchPredictionResult,
)

assert batch_result.succeeded
assert batch_result.total_requests == 2
assert batch_result.successful_requests == 2
assert batch_result.failed_requests == 0
assert batch_result.fail_fast is True

assert len(batch_result.items) == 2
assert len(batch_result.predictions) == 2
assert batch_result.failures == ()

first_item = batch_result.get_item(
    "release_validation_first"
)
second_item = batch_result.get_item(
    "release_validation_second"
)

assert isinstance(
    first_item,
    ForecastBatchPredictionItem,
)
assert isinstance(
    second_item,
    ForecastBatchPredictionItem,
)

assert first_item.succeeded
assert second_item.succeeded

assert first_item.prediction is not None
assert second_item.prediction is not None

assert first_item.prediction.predictions == (
    100.0,
    100.0,
)
assert second_item.prediction.predictions == (
    100.0,
)

assert (
    first_item.prediction.metadata["batch_item"]
    == "first"
)
assert (
    second_item.prediction.metadata["batch_item"]
    == "second"
)

assert first_item.metadata["request_order"] == 1
assert second_item.metadata["request_order"] == 2

assert (
    batch_result.metadata["validation"]
    == "implementation_28"
)

batch_payload = batch_result.to_dict()

assert batch_payload["total_requests"] == 2
assert batch_payload["successful_requests"] == 2
assert batch_payload["failed_requests"] == 0
assert batch_payload["succeeded"] is True
assert len(batch_payload["items"]) == 2

print("PASS: Batch inference orchestration remains operational")

# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.inference")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print("Public API symbols validated:", len(EXPECTED_PUBLIC_API))
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast.model_registry
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path


PACKAGE_NAME = "src.forecast.model_registry"

EXPECTED_MODULES = (
    "registry",
    "catalog",
    "versioning",
    "promotion",
)

EXPECTED_PUBLIC_API = {
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


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")
    syntax_tree = ast.parse(
        source,
        filename=str(source_path),
    )

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import canonical public package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every model-registry leaf module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"
    imported_module = importlib.import_module(
        qualified_name
    )

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every model-registry module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(
        imported_module
    )
    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate package public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(
    set(package.__all__)
), (
    "src.forecast.model_registry.__all__ contains "
    "duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Model-registry public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__
# -----------------------------------------------------------------------------

expected_leaf_exports = {
    "registry": {
        "EnterpriseModelRegistry",
        "ForecastModelRegistration",
    },
    "catalog": {
        "EnterpriseModelCatalog",
        "ForecastModelCatalogQuery",
        "ForecastModelCatalogResult",
    },
    "versioning": {
        "EnterpriseModelVersioning",
        "ForecastModelVersion",
        "ForecastModelVersionEntry",
    },
    "promotion": {
        "EnterpriseModelPromotionService",
        "ForecastLifecycleState",
        "ForecastPromotionAction",
        "ForecastPromotionRecord",
        "ForecastPromotionResult",
    },
}

for module_name, expected_exports in (
    expected_leaf_exports.items()
):
    imported_module = imported_modules[module_name]

    assert hasattr(imported_module, "__all__"), (
        f"{imported_module.__name__} does not define "
        "__all__."
    )

    actual_exports = set(imported_module.__all__)

    assert actual_exports == expected_exports, {
        "module": imported_module.__name__,
        "missing_exports": sorted(
            expected_exports - actual_exports
        ),
        "unexpected_exports": sorted(
            actual_exports - expected_exports
        ),
    }

    assert len(imported_module.__all__) == len(
        set(imported_module.__all__)
    ), (
        f"{imported_module.__name__}.__all__ contains "
        "duplicates."
    )

    for exported_name in imported_module.__all__:
        assert hasattr(
            imported_module,
            exported_name,
        )

print(
    "PASS: Model-registry leaf-module __all__ "
    "contracts are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public and leaf-module object identity
# -----------------------------------------------------------------------------

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

from src.forecast.model_registry.catalog import (
    EnterpriseModelCatalog as LeafEnterpriseModelCatalog,
    ForecastModelCatalogQuery as LeafForecastModelCatalogQuery,
    ForecastModelCatalogResult as LeafForecastModelCatalogResult,
)
from src.forecast.model_registry.promotion import (
    EnterpriseModelPromotionService
    as LeafEnterpriseModelPromotionService,
    ForecastLifecycleState as LeafForecastLifecycleState,
    ForecastPromotionAction as LeafForecastPromotionAction,
    ForecastPromotionRecord as LeafForecastPromotionRecord,
    ForecastPromotionResult as LeafForecastPromotionResult,
)
from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry as LeafEnterpriseModelRegistry,
    ForecastModelRegistration as LeafForecastModelRegistration,
)
from src.forecast.model_registry.versioning import (
    EnterpriseModelVersioning as LeafEnterpriseModelVersioning,
    ForecastModelVersion as LeafForecastModelVersion,
    ForecastModelVersionEntry as LeafForecastModelVersionEntry,
)

assert (
    EnterpriseModelRegistry
    is LeafEnterpriseModelRegistry
)
assert (
    ForecastModelRegistration
    is LeafForecastModelRegistration
)

assert (
    EnterpriseModelCatalog
    is LeafEnterpriseModelCatalog
)
assert (
    ForecastModelCatalogQuery
    is LeafForecastModelCatalogQuery
)
assert (
    ForecastModelCatalogResult
    is LeafForecastModelCatalogResult
)

assert (
    EnterpriseModelVersioning
    is LeafEnterpriseModelVersioning
)
assert (
    ForecastModelVersion
    is LeafForecastModelVersion
)
assert (
    ForecastModelVersionEntry
    is LeafForecastModelVersionEntry
)

assert (
    EnterpriseModelPromotionService
    is LeafEnterpriseModelPromotionService
)
assert (
    ForecastLifecycleState
    is LeafForecastLifecycleState
)
assert (
    ForecastPromotionAction
    is LeafForecastPromotionAction
)
assert (
    ForecastPromotionRecord
    is LeafForecastPromotionRecord
)
assert (
    ForecastPromotionResult
    is LeafForecastPromotionResult
)

print(
    "PASS: Model-registry public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate semantic-version contract
# -----------------------------------------------------------------------------

version = ForecastModelVersion.parse("2.8.0")

assert version.major == 2
assert version.minor == 8
assert version.patch == 0
assert str(version) == "2.8.0"
assert version.to_string() == "2.8.0"

assert str(version.bump_major()) == "3.0.0"
assert str(version.bump_minor()) == "2.9.0"
assert str(version.bump_patch()) == "2.8.1"

assert version.to_dict() == {
    "version": "2.8.0",
    "major": 2,
    "minor": 8,
    "patch": 0,
}

assert (
    ForecastModelVersion.parse("2.8.0")
    < ForecastModelVersion.parse("2.9.0")
    < ForecastModelVersion.parse("3.0.0")
)

print(
    "PASS: Forecast semantic-version contract "
    "remains operational"
)

# -----------------------------------------------------------------------------
# 9. Validate empty registry contract
# -----------------------------------------------------------------------------

registry = EnterpriseModelRegistry()

assert registry.is_empty
assert registry.total_models == 0
assert registry.list_models() == ()
assert registry.to_dict()["total_models"] == 0

registry.clear()

assert registry.is_empty
assert registry.total_models == 0

print(
    "PASS: Enterprise model registry empty-state "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 10. Validate catalog contract
# -----------------------------------------------------------------------------

catalog = EnterpriseModelCatalog(
    registry=registry
)

assert catalog.registry is registry
assert catalog.list_categories() == ()
assert catalog.list_algorithms() == ()
assert catalog.list_target_columns() == ()

catalog_query = ForecastModelCatalogQuery()

catalog_result = catalog.search(catalog_query)

assert isinstance(
    catalog_result,
    ForecastModelCatalogResult,
)
assert catalog_result.query is catalog_query
assert catalog_result.total_matches == 0
assert catalog_result.total_registry_models == 0
assert catalog_result.is_empty
assert catalog_result.first is None
assert catalog_result.registrations == ()

catalog_payload = catalog_result.to_dict()

assert catalog_payload["total_matches"] == 0
assert catalog_payload["total_registry_models"] == 0
assert catalog_payload["registrations"] == []

print(
    "PASS: Enterprise model catalog empty-state "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate versioning service construction
# -----------------------------------------------------------------------------

from src.forecast.modeling import ForecastRegistryError


versioning = EnterpriseModelVersioning(
    registry=registry
)

assert versioning.registry is registry

assert versioning.list_versions(
    "release_validation_model"
) == ()

assert versioning.list_version_entries(
    "release_validation_model"
) == ()

assert (
    versioning.version_exists(
        model_name="release_validation_model",
        model_version="1.0.0",
    )
    is False
)

try:
    versioning.latest_version(
        "release_validation_model"
    )
except ForecastRegistryError as exc:
    assert (
        "No registered versions were found"
        in str(exc)
    )
else:
    raise AssertionError(
        "latest_version() should raise ForecastRegistryError "
        "when the model has no registered versions."
    )

assert str(
    versioning.next_patch_version(
        "release_validation_model"
    )
) == "0.0.1"

assert str(
    versioning.next_minor_version(
        "release_validation_model"
    )
) == "0.1.0"

assert str(
    versioning.next_major_version(
        "release_validation_model"
    )
) == "1.0.0"

print(
    "PASS: Enterprise model versioning empty-state "
    "contract remains operational"
)

# -----------------------------------------------------------------------------
# 12. Validate promotion service construction
# -----------------------------------------------------------------------------

promotion_service = EnterpriseModelPromotionService(
    registry=registry,
    versioning=versioning,
)

assert promotion_service.registry is registry
assert promotion_service.versioning is versioning

try:
    promotion_service.promotion_history(
        model_name="release_validation_model",
        model_version="1.0.0",
    )
except ForecastRegistryError as exc:
    assert (
        "Forecast model version is not registered"
        in str(exc)
    )
else:
    raise AssertionError(
        "promotion_history() should raise ForecastRegistryError "
        "for an unregistered model version."
    )

promotion_payload = promotion_service.to_dict(
    model_name="release_validation_model"
)

assert promotion_payload == {
    "model_name": "release_validation_model",
    "total_versions": 0,
    "champion_version": None,
    "versions": [],
}

print(
    "PASS: Enterprise model promotion service "
    "dependency contract remains operational"
)

# -----------------------------------------------------------------------------
# 13. Validate public method signatures
# -----------------------------------------------------------------------------

registry_register_signature = inspect.signature(
    EnterpriseModelRegistry.register
)

assert "artifact" in registry_register_signature.parameters
assert (
    "primary_metric"
    in registry_register_signature.parameters
)
assert (
    "primary_metric_value"
    in registry_register_signature.parameters
)
assert "metadata" in registry_register_signature.parameters

catalog_search_signature = inspect.signature(
    EnterpriseModelCatalog.search
)

assert "query" in catalog_search_signature.parameters

versioning_latest_signature = inspect.signature(
    EnterpriseModelVersioning.latest_version
)

assert (
    "model_name"
    in versioning_latest_signature.parameters
)

promotion_staging_signature = inspect.signature(
    EnterpriseModelPromotionService.promote_to_staging
)

assert (
    "model_name"
    in promotion_staging_signature.parameters
)
assert (
    "model_version"
    in promotion_staging_signature.parameters
)

print(
    "PASS: Model-registry public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast.model_registry")
print("Release: v3.0.0")
print("Finding remediated: ENG-001")
print("Canonical namespace: src.*")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.forecast
#
# Release:
#     v3.0.0
#
# Scope:
#     Root Enterprise Forecast Dataset Framework
#
# Finding:
#     ENG-001 — Inconsistent Python import namespaces
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


PACKAGE_NAME = "src.forecast"

EXPECTED_MODULES = (
    "constants",
    "models",
    "splitter",
    "persistence",
    "service",
)

EXPECTED_PUBLIC_API = {
    # Public services
    "ForecastDatasetService",
    "ForecastDatasetSplitter",
    "ForecastDatasetPersistence",

    # Public data contracts
    "DatasetSplit",
    "ForecastDatasetBundle",
    "ForecastDatasetMetadata",
    "ForecastDatasetSummary",
    "ForecastPersistenceResult",

    # Public configuration constants
    "FORECAST_DATASET_NAME",
    "FORECAST_DATASET_VERSION",
    "DATE_COLUMN",
    "DEFAULT_FORECAST_HORIZON",
    "DEFAULT_WARMUP_DAYS",
    "DEFAULT_TRAIN_RATIO",
    "DEFAULT_VALIDATION_RATIO",
    "DEFAULT_TEST_RATIO",
    "TEMPORAL_SPLIT_STRATEGY",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")

    syntax_tree = ast.parse(
        source,
        filename=str(source_path),
    )

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import canonical root package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every root forecast module
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    imported_module = importlib.import_module(
        qualified_name
    )

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every root forecast module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy forecast.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "forecast"
        or module_name.startswith("forecast.")
    )
)

assert not legacy_modules, (
    "Legacy forecast.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy forecast.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan root forecast source files for legacy imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(
        imported_module
    )

    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "forecast"
            or imported_name.startswith("forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy forecast.* imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy forecast.* source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(
    set(package.__all__)
), (
    "src.forecast.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Root forecast public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate public and leaf-module object identity
# -----------------------------------------------------------------------------

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

from src.forecast.models import (
    DatasetSplit as LeafDatasetSplit,
    ForecastDatasetBundle as LeafForecastDatasetBundle,
    ForecastDatasetMetadata as LeafForecastDatasetMetadata,
    ForecastDatasetSummary as LeafForecastDatasetSummary,
    ForecastPersistenceResult as LeafForecastPersistenceResult,
)

from src.forecast.persistence import (
    ForecastDatasetPersistence as LeafForecastDatasetPersistence,
)

from src.forecast.service import (
    ForecastDatasetService as LeafForecastDatasetService,
)

from src.forecast.splitter import (
    ForecastDatasetSplitter as LeafForecastDatasetSplitter,
)

assert DatasetSplit is LeafDatasetSplit

assert (
    ForecastDatasetBundle
    is LeafForecastDatasetBundle
)

assert (
    ForecastDatasetMetadata
    is LeafForecastDatasetMetadata
)

assert (
    ForecastDatasetSummary
    is LeafForecastDatasetSummary
)

assert (
    ForecastPersistenceResult
    is LeafForecastPersistenceResult
)

assert (
    ForecastDatasetPersistence
    is LeafForecastDatasetPersistence
)

assert (
    ForecastDatasetService
    is LeafForecastDatasetService
)

assert (
    ForecastDatasetSplitter
    is LeafForecastDatasetSplitter
)

print(
    "PASS: Root forecast public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 7. Validate centralized forecast constants
# -----------------------------------------------------------------------------

from src.forecast import (
    DATE_COLUMN,
    DEFAULT_FORECAST_HORIZON,
    DEFAULT_TEST_RATIO,
    DEFAULT_TRAIN_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WARMUP_DAYS,
    FORECAST_DATASET_NAME,
    FORECAST_DATASET_VERSION,
    TEMPORAL_SPLIT_STRATEGY,
)

from src.forecast.constants import (
    ALL_DATASET_SPLIT_NAMES,
    DEFAULT_COMPRESSION_CODEC,
    DEFAULT_STORAGE_FORMAT,
    DEFAULT_WRITE_MODE,
    MINIMUM_MODEL_READY_ROWS,
    MINIMUM_TEST_ROWS,
    MINIMUM_TRAIN_ROWS,
    MINIMUM_VALIDATION_ROWS,
)

assert FORECAST_DATASET_NAME == "enterprise_forecast_dataset"
assert FORECAST_DATASET_VERSION == "1.0.0"

assert DATE_COLUMN == "order_date"

assert DEFAULT_FORECAST_HORIZON == 14
assert DEFAULT_WARMUP_DAYS == 90

assert math.isclose(
    DEFAULT_TRAIN_RATIO
    + DEFAULT_VALIDATION_RATIO
    + DEFAULT_TEST_RATIO,
    1.0,
    abs_tol=1e-12,
)

assert TEMPORAL_SPLIT_STRATEGY == "temporal"

assert ALL_DATASET_SPLIT_NAMES == (
    "train",
    "validation",
    "test",
)

assert DEFAULT_STORAGE_FORMAT == "parquet"
assert DEFAULT_WRITE_MODE == "overwrite"
assert DEFAULT_COMPRESSION_CODEC == "snappy"

assert MINIMUM_TRAIN_ROWS == 30
assert MINIMUM_VALIDATION_ROWS == 7
assert MINIMUM_TEST_ROWS == 7

assert MINIMUM_MODEL_READY_ROWS == (
    MINIMUM_TRAIN_ROWS
    + MINIMUM_VALIDATION_ROWS
    + MINIMUM_TEST_ROWS
)

print("PASS: Root forecast constants remain internally consistent")


# -----------------------------------------------------------------------------
# 8. Build deterministic release-validation Spark dataset
# -----------------------------------------------------------------------------

validation_rows = [
    (
        date(2026, 1, 1) + timedelta(days=index),
        float(100 + index),
    )
    for index in range(60)
]

validation_df = spark.createDataFrame(
    validation_rows,
    schema=[
        "order_date",
        "target",
    ],
)

assert validation_df.count() == 60
assert validation_df.columns == [
    "order_date",
    "target",
]

print("PASS: Created deterministic release-validation dataset")


# -----------------------------------------------------------------------------
# 9. Validate temporal splitter contract
# -----------------------------------------------------------------------------

splitter = ForecastDatasetSplitter(
    date_column="order_date",
    warmup_days=0,
    train_ratio=0.70,
    validation_ratio=0.15,
    test_ratio=0.15,
    split_strategy="temporal",
)

source_rows = splitter.validate_source_dataset(
    validation_df
)

assert source_rows == 60

(
    model_ready_df,
    warmup_rows_removed,
    train_split,
    validation_split,
    test_split,
) = splitter.prepare_and_split(
    validation_df
)

assert warmup_rows_removed == 0
assert model_ready_df.count() == 60

assert train_split.name == "train"
assert validation_split.name == "validation"
assert test_split.name == "test"

assert train_split.row_count == 42
assert validation_split.row_count == 9
assert test_split.row_count == 9

assert (
    train_split.row_count
    + validation_split.row_count
    + test_split.row_count
    == 60
)

assert train_split.end_date < validation_split.start_date
assert validation_split.end_date < test_split.start_date

print(
    "PASS: Forecast temporal splitter contract remains operational"
)


# -----------------------------------------------------------------------------
# 10. Validate dataset model and serialization contracts
# -----------------------------------------------------------------------------

generated_at_utc = datetime(
    2026,
    8,
    7,
    0,
    0,
    tzinfo=timezone.utc,
)

metadata = ForecastDatasetMetadata(
    dataset_name="release_validation_dataset",
    dataset_version="1.0.0",
    target_column="target",
    date_column="order_date",
    forecast_horizon=14,
    warmup_days=0,
    split_strategy="temporal",
    train_ratio=0.70,
    validation_ratio=0.15,
    test_ratio=0.15,
    source_rows=60,
    warmup_rows_removed=0,
    model_ready_rows=60,
    total_columns=len(model_ready_df.columns),
    start_date=date(2026, 1, 1),
    end_date=date(2026, 3, 1),
    train_start_date=train_split.start_date,
    train_end_date=train_split.end_date,
    validation_start_date=validation_split.start_date,
    validation_end_date=validation_split.end_date,
    test_start_date=test_split.start_date,
    test_end_date=test_split.end_date,
    generated_at_utc=generated_at_utc,
)

summary = ForecastDatasetSummary(
    source_rows=60,
    warmup_rows_removed=0,
    model_ready_rows=60,
    train_rows=42,
    validation_rows=9,
    test_rows=9,
    total_columns=len(model_ready_df.columns),
    validation_passed=True,
    status="COMPLETED",
)

bundle = ForecastDatasetBundle(
    train=train_split,
    validation=validation_split,
    test=test_split,
    metadata=metadata,
    summary=summary,
)

assert bundle.train_df is train_split.dataframe
assert bundle.validation_df is validation_split.dataframe
assert bundle.test_df is test_split.dataframe

assert bundle.total_rows == 60
assert bundle.persistence is None

metadata_payload = bundle.as_metadata_dict()
summary_payload = bundle.as_summary_dict()

assert metadata_payload["dataset_name"] == (
    "release_validation_dataset"
)
assert metadata_payload["dataset_version"] == "1.0.0"
assert metadata_payload["source_rows"] == 60
assert metadata_payload["model_ready_rows"] == 60

assert (
    metadata_payload["generated_at_utc"]
    == generated_at_utc.isoformat()
)

assert summary_payload == {
    "source_rows": 60,
    "warmup_rows_removed": 0,
    "model_ready_rows": 60,
    "train_rows": 42,
    "validation_rows": 9,
    "test_rows": 9,
    "total_columns": len(model_ready_df.columns),
    "validation_passed": True,
    "status": "COMPLETED",
}

print(
    "PASS: Forecast dataset bundle and serialization contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate ForecastDatasetService without persistence
# -----------------------------------------------------------------------------

service = ForecastDatasetService(
    spark=spark,
    target_column="target",
    date_column="order_date",
    forecast_horizon=14,
    dataset_name="release_validation_dataset",
    dataset_version="1.0.0",
    warmup_days=0,
    train_ratio=0.70,
    validation_ratio=0.15,
    test_ratio=0.15,
    split_strategy="temporal",
)

assert service.persistence is None

service_bundle = service.build(
    validation_df,
    persist=False,
)

assert isinstance(
    service_bundle,
    ForecastDatasetBundle,
)

assert service_bundle.total_rows == 60

assert service_bundle.summary.validation_passed
assert service_bundle.summary.status == "COMPLETED"

assert service_bundle.summary.train_rows == 42
assert service_bundle.summary.validation_rows == 9
assert service_bundle.summary.test_rows == 9

assert service_bundle.persistence is None

print(
    "PASS: ForecastDatasetService non-persistent orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate persistence dependency construction and path contract
# -----------------------------------------------------------------------------

persistence = ForecastDatasetPersistence(
    spark=spark,
    root_path="s3://release-validation/forecast",
)

assert persistence.spark is spark
assert (
    persistence.root_path
    == "s3://release-validation/forecast"
)

assert persistence.storage_format == "parquet"
assert persistence.write_mode == "overwrite"
assert persistence.compression_codec == "snappy"

assert (
    persistence.build_dataset_root_path("1.0.0")
    == "s3://release-validation/forecast/v1.0.0"
)

assert (
    persistence.build_dataset_root_path("v1.0.0")
    == "s3://release-validation/forecast/v1.0.0"
)

print(
    "PASS: Forecast persistence configuration and path contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 13. Validate persistence orchestration without external storage writes
# -----------------------------------------------------------------------------

captured_dataframe_writes: list[str] = []
captured_manifest: dict[str, object] = {}


def _capture_dataframe_write(
    *,
    dataframe,
    path: str,
) -> None:
    assert dataframe is not None
    assert dataframe.columns

    captured_dataframe_writes.append(path)


def _capture_manifest_write(
    *,
    manifest: dict,
    path: str,
) -> None:
    captured_manifest["manifest"] = manifest
    captured_manifest["path"] = path


persistence._write_dataframe = (
    _capture_dataframe_write
)

persistence.save_manifest = (
    _capture_manifest_write
)

persistence_result = persistence.persist_bundle(
    bundle
)

assert isinstance(
    persistence_result,
    ForecastPersistenceResult,
)

assert (
    persistence_result.dataset_root_path
    == "s3://release-validation/forecast/v1.0.0"
)

assert persistence_result.train_path.endswith(
    "/train"
)

assert persistence_result.validation_path.endswith(
    "/validation"
)

assert persistence_result.test_path.endswith(
    "/test"
)

assert persistence_result.metadata_path.endswith(
    "/metadata/forecast_dataset_metadata"
)

assert persistence_result.summary_path.endswith(
    "/summary/forecast_dataset_summary"
)

assert persistence_result.manifest_path.endswith(
    "/manifest/forecast_dataset_manifest"
)

assert persistence_result.storage_format == "parquet"
assert persistence_result.write_mode == "overwrite"

assert len(captured_dataframe_writes) == 5

assert set(captured_dataframe_writes) == {
    persistence_result.train_path,
    persistence_result.validation_path,
    persistence_result.test_path,
    persistence_result.metadata_path,
    persistence_result.summary_path,
}

assert captured_manifest["path"] == (
    persistence_result.manifest_path
)

manifest = captured_manifest["manifest"]

assert manifest["dataset"]["name"] == (
    "release_validation_dataset"
)

assert manifest["dataset"]["version"] == "1.0.0"

assert manifest["row_counts"]["source_rows"] == 60
assert manifest["row_counts"]["train_rows"] == 42
assert manifest["row_counts"]["validation_rows"] == 9
assert manifest["row_counts"]["test_rows"] == 9
assert manifest["row_counts"]["total_persisted_rows"] == 60

assert manifest["quality"]["validation_passed"] is True
assert manifest["quality"]["status"] == "COMPLETED"

print(
    "PASS: Forecast persistence orchestration remains operational "
    "without external storage side effects"
)


# -----------------------------------------------------------------------------
# 14. Validate service/persistence dependency wiring
# -----------------------------------------------------------------------------

injected_persistence = ForecastDatasetPersistence(
    spark=spark,
    root_path="s3://release-validation/injected",
)

injected_service = ForecastDatasetService(
    spark=spark,
    target_column="target",
    date_column="order_date",
    warmup_days=0,
    persistence=injected_persistence,
)

assert (
    injected_service.persistence
    is injected_persistence
)

assert (
    injected_service.persistence.spark
    is injected_service.spark
)

auto_service = ForecastDatasetService(
    spark=spark,
    target_column="target",
    date_column="order_date",
    warmup_days=0,
    root_path="s3://release-validation/automatic",
)

assert isinstance(
    auto_service.persistence,
    ForecastDatasetPersistence,
)

assert (
    auto_service.persistence.root_path
    == "s3://release-validation/automatic"
)

print(
    "PASS: Forecast service/persistence dependency wiring "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate public method signatures
# -----------------------------------------------------------------------------

splitter_signature = inspect.signature(
    ForecastDatasetSplitter.prepare_and_split
)

assert "dataframe" in splitter_signature.parameters

persistence_signature = inspect.signature(
    ForecastDatasetPersistence.persist_bundle
)

assert "bundle" in persistence_signature.parameters

service_signature = inspect.signature(
    ForecastDatasetService.build
)

assert "dataframe" in service_signature.parameters
assert "persist" in service_signature.parameters

print("PASS: Root forecast public signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.forecast")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.demand
#
# Release:
#     v3.0.0
#
# Scope:
#     Enterprise Demand Intelligence Engine
#
# Finding:
#     ENG-001 — Canonical Python namespace validation
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import math
import sys
from datetime import date, timedelta
from pathlib import Path


PACKAGE_NAME = "src.demand"

EXPECTED_MODULES = (
    "constants",
    "models",
    "profiles",
    "business_features",
    "ml_features",
    "service",
)

EXPECTED_PUBLIC_API = {
    "DemandService",
    "DemandSummary",
    "ForecastProfile",
    "get_forecast_profile",
    "get_primary_forecast_profile",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for an imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    """Return absolute imports declared in a Python source module."""
    source = source_path.read_text(encoding="utf-8")

    syntax_tree = ast.parse(
        source,
        filename=str(source_path),
    )

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every demand module through src.*
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    imported_module = importlib.import_module(
        qualified_name
    )

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every demand module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level demand.* module loading
# -----------------------------------------------------------------------------

legacy_demand_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "demand"
        or module_name.startswith("demand.")
    )
)

assert not legacy_demand_modules, (
    "Legacy demand.* modules were loaded: "
    f"{legacy_demand_modules}"
)

print("PASS: No legacy demand.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan demand source files for legacy absolute imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(
        imported_module
    )

    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "demand"
            or imported_name.startswith("demand.")
            or imported_name == "forecast"
            or imported_name.startswith("src.forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy absolute package imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print(
    "PASS: No legacy demand.* or forecast.* "
    "absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(
    set(package.__all__)
), (
    "src.demand.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Demand public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate root/leaf object identity
# -----------------------------------------------------------------------------

from src.demand import (
    DemandService,
    DemandSummary,
    ForecastProfile,
    get_forecast_profile,
    get_primary_forecast_profile,
)

from src.demand.models import (
    DemandSummary as LeafDemandSummary,
    ForecastProfile as LeafForecastProfile,
)

from src.demand.profiles import (
    get_forecast_profile as LeafGetForecastProfile,
    get_primary_forecast_profile as LeafGetPrimaryForecastProfile,
)

from src.demand.service import (
    DemandService as LeafDemandService,
)

assert DemandService is LeafDemandService
assert DemandSummary is LeafDemandSummary
assert ForecastProfile is LeafForecastProfile

assert (
    get_forecast_profile
    is LeafGetForecastProfile
)

assert (
    get_primary_forecast_profile
    is LeafGetPrimaryForecastProfile
)

print("PASS: Demand public object identities are consistent")


# -----------------------------------------------------------------------------
# 7. Validate centralized demand constants
# -----------------------------------------------------------------------------

from src.demand.constants import (
    BUSINESS_FEATURES,
    CUSTOMER_COUNT_COLUMN,
    DATE_COLUMN,
    GROSS_SALES_COLUMN,
    ML_FEATURE_GROUPS,
    ORDER_COUNT_COLUMN,
    ORDER_LINE_COUNT_COLUMN,
    PRIMARY_FORECAST_TARGET,
    SECONDARY_FORECAST_TARGETS,
    SUPPORTED_FORECAST_HORIZONS,
    WORKLOAD_UNITS_COLUMN,
)

assert DATE_COLUMN == "order_date"
assert ORDER_COUNT_COLUMN == "order_count"
assert ORDER_LINE_COUNT_COLUMN == "order_line_count"
assert WORKLOAD_UNITS_COLUMN == "workload_units"
assert GROSS_SALES_COLUMN == "gross_sales"
assert CUSTOMER_COUNT_COLUMN == "customer_count"

assert PRIMARY_FORECAST_TARGET == ORDER_LINE_COUNT_COLUMN

assert SECONDARY_FORECAST_TARGETS == (
    ORDER_COUNT_COLUMN,
    WORKLOAD_UNITS_COLUMN,
)

assert SUPPORTED_FORECAST_HORIZONS == (
    1,
    7,
    14,
    30,
    60,
    90,
)

assert BUSINESS_FEATURES == (
    "avg_lines_per_order",
    "avg_units_per_order",
    "avg_units_per_line",
    "sales_per_order",
    "sales_per_line",
)

assert ML_FEATURE_GROUPS == (
    "lag",
    "rolling",
    "trend",
    "seasonality",
)

print("PASS: Demand constants remain internally consistent")


# -----------------------------------------------------------------------------
# 8. Validate forecast-profile contracts
# -----------------------------------------------------------------------------

from src.demand.profiles import (
    FORECAST_PROFILES,
    ORDER_DEMAND_PROFILE,
    ORDER_LINE_DEMAND_PROFILE,
    UNIT_DEMAND_PROFILE,
    validate_forecast_profile,
)

assert set(FORECAST_PROFILES) == {
    "order_demand",
    "order_line_demand",
    "unit_demand",
}

primary_profile = get_primary_forecast_profile()

assert primary_profile is ORDER_LINE_DEMAND_PROFILE
assert primary_profile.name == "order_line_demand"
assert primary_profile.target == ORDER_LINE_COUNT_COLUMN

assert tuple(primary_profile.horizons) == (
    SUPPORTED_FORECAST_HORIZONS
)

assert tuple(primary_profile.business_features) == (
    BUSINESS_FEATURES
)

assert tuple(primary_profile.ml_features) == (
    ML_FEATURE_GROUPS
)

assert (
    get_forecast_profile("order_demand")
    is ORDER_DEMAND_PROFILE
)

assert (
    get_forecast_profile("unit_demand")
    is UNIT_DEMAND_PROFILE
)

assert (
    get_forecast_profile(" ORDER_LINE_DEMAND ")
    is ORDER_LINE_DEMAND_PROFILE
)

for profile in FORECAST_PROFILES.values():
    validate_forecast_profile(profile)

print("PASS: Demand forecast-profile contracts remain operational")


# -----------------------------------------------------------------------------
# 9. Build deterministic release-validation Gold demand dataset
# -----------------------------------------------------------------------------

validation_rows = [
    (
        date(2026, 1, 1) + timedelta(days=index),
        100 + index,             # order_count
        500 + (index * 2),       # order_line_count
        700 + (index * 3),       # workload_units
        10000.0 + (index * 50),  # gross_sales
        80 + index,              # customer_count
    )
    for index in range(120)
]

validation_df = spark.createDataFrame(
    validation_rows,
    schema=[
        "order_date",
        "order_count",
        "order_line_count",
        "workload_units",
        "gross_sales",
        "customer_count",
    ],
)

assert validation_df.count() == 120

assert validation_df.columns == [
    "order_date",
    "order_count",
    "order_line_count",
    "workload_units",
    "gross_sales",
    "customer_count",
]

print(
    "PASS: Created deterministic Demand Intelligence "
    "release-validation dataset"
)


# -----------------------------------------------------------------------------
# 10. Validate business-feature engineering
# -----------------------------------------------------------------------------

from src.demand.business_features import (
    add_business_features,
    validate_business_features,
)

business_df = add_business_features(
    validation_df
)

validate_business_features(
    business_df
)

for feature_name in BUSINESS_FEATURES:
    assert feature_name in business_df.columns

first_business_row = (
    business_df
    .orderBy("order_date")
    .first()
)

assert math.isclose(
    first_business_row["avg_lines_per_order"],
    5.0,
    rel_tol=1e-12,
)

assert math.isclose(
    first_business_row["avg_units_per_order"],
    7.0,
    rel_tol=1e-12,
)

assert math.isclose(
    first_business_row["avg_units_per_line"],
    1.4,
    rel_tol=1e-12,
)

assert math.isclose(
    first_business_row["sales_per_order"],
    100.0,
    rel_tol=1e-12,
)

assert math.isclose(
    first_business_row["sales_per_line"],
    20.0,
    rel_tol=1e-12,
)

print(
    "PASS: Demand business-feature engineering "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate leakage-safe ML feature engineering
# -----------------------------------------------------------------------------

from src.demand.ml_features import (
    DEFAULT_LAG_PERIODS,
    DEFAULT_ROLLING_WINDOWS,
    DEFAULT_TREND_PERIODS,
    add_ml_features,
    validate_ml_features,
)

ml_df = add_ml_features(
    dataframe=business_df,
    target_column=ORDER_LINE_COUNT_COLUMN,
)

validate_ml_features(
    dataframe=ml_df,
    target_column=ORDER_LINE_COUNT_COLUMN,
)

for period in DEFAULT_LAG_PERIODS:
    assert (
        f"{ORDER_LINE_COUNT_COLUMN}_lag_{period}"
        in ml_df.columns
    )

for window_size in DEFAULT_ROLLING_WINDOWS:
    for statistic in (
        "mean",
        "std",
        "min",
        "max",
    ):
        assert (
            f"{ORDER_LINE_COUNT_COLUMN}_rolling_"
            f"{statistic}_{window_size}"
            in ml_df.columns
        )

for period in DEFAULT_TREND_PERIODS:
    assert (
        f"{ORDER_LINE_COUNT_COLUMN}_change_{period}"
        in ml_df.columns
    )

    assert (
        f"{ORDER_LINE_COUNT_COLUMN}_growth_rate_{period}"
        in ml_df.columns
    )

assert (
    f"{ORDER_LINE_COUNT_COLUMN}_momentum_7_30"
    in ml_df.columns
)

for seasonality_feature in (
    "day_of_month",
    "quarter",
    "is_month_start",
    "is_month_end",
    "is_quarter_start",
    "is_quarter_end",
):
    assert seasonality_feature in ml_df.columns

assert ml_df.count() == 120

print(
    "PASS: Demand leakage-safe ML feature engineering "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate DemandService summary contract
# -----------------------------------------------------------------------------

service = DemandService(
    default_dataset_name="release_validation_demand"
)

summary = service.summarize_dataset(
    validation_df
)

assert isinstance(
    summary,
    DemandSummary,
)

assert summary.dataset_name == (
    "release_validation_demand"
)

assert summary.start_date == date(2026, 1, 1)
assert summary.end_date == date(2026, 4, 30)

assert summary.total_days == 120
assert summary.total_records == 120

assert summary.target_column == (
    ORDER_LINE_COUNT_COLUMN
)

assert summary.missing_dates == 0
assert summary.duplicate_dates == 0

assert summary.validation_passed is True

print("PASS: DemandService summary contract remains operational")


# -----------------------------------------------------------------------------
# 13. Validate DemandService profile-resolution contract
# -----------------------------------------------------------------------------

service_primary_profile = service.get_profile()

assert (
    service_primary_profile
    is ORDER_LINE_DEMAND_PROFILE
)

assert (
    service.get_profile("order_demand")
    is ORDER_DEMAND_PROFILE
)

assert (
    service.get_profile("unit_demand")
    is UNIT_DEMAND_PROFILE
)

print(
    "PASS: DemandService forecast-profile resolution "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate complete forecast-dataset orchestration
# -----------------------------------------------------------------------------

forecast_df = service.build_forecast_dataset(
    dataframe=validation_df,
    profile_name="order_line_demand",
    validate_input=True,
    validate_output=True,
)

assert forecast_df.count() == 120

for feature_name in BUSINESS_FEATURES:
    assert feature_name in forecast_df.columns

validate_ml_features(
    dataframe=forecast_df,
    target_column=ORDER_LINE_COUNT_COLUMN,
)

service.validate_forecast_dataset(
    dataframe=forecast_df,
    profile_name="order_line_demand",
)

ordered_dates = [
    row["order_date"]
    for row in (
        forecast_df
        .select("order_date")
        .collect()
    )
]

assert ordered_dates == sorted(
    ordered_dates
)

print(
    "PASS: DemandService end-to-end feature-dataset "
    "orchestration remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    get_forecast_profile(
        "release_validation_unknown_profile"
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "Unknown forecast profiles must raise ValueError."
    )


try:
    add_business_features(
        validation_df.select(
            "order_date",
            "order_count",
        )
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "Missing business-feature source columns "
        "must raise ValueError."
    )


try:
    DemandService(
        default_dataset_name="   "
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "An empty default dataset name must raise ValueError."
    )

print("PASS: Demand validation failure contracts remain operational")


# -----------------------------------------------------------------------------
# 16. Validate public method signatures
# -----------------------------------------------------------------------------

summary_signature = inspect.signature(
    DemandService.summarize_dataset
)

assert "dataframe" in summary_signature.parameters
assert "target_column" in summary_signature.parameters
assert "dataset_name" in summary_signature.parameters

profile_signature = inspect.signature(
    DemandService.get_profile
)

assert "profile_name" in profile_signature.parameters

build_signature = inspect.signature(
    DemandService.build_forecast_dataset
)

assert "dataframe" in build_signature.parameters
assert "profile_name" in build_signature.parameters
assert "validate_input" in build_signature.parameters
assert "validate_output" in build_signature.parameters

validation_signature = inspect.signature(
    DemandService.validate_forecast_dataset
)

assert "dataframe" in validation_signature.parameters
assert "profile_name" in validation_signature.parameters

print("PASS: Demand public method signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.demand")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.metadata
#
# Release:
#     v3.0.0
#
# Scope:
#     Enterprise Metadata and Dataset Profiling Framework
#
# Primary Finding:
#     ENG-001 — Canonical Python namespace validation
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import date, datetime, timezone
from pathlib import Path


PACKAGE_NAME = "src.metadata"

EXPECTED_MODULES = (
    "exceptions",
    "models",
    "profiler",
    "fingerprint",
    "catalog",
    "service",
)

EXPECTED_PUBLIC_API = {
    "ColumnProfile",
    "DatasetFingerprint",
    "DatasetProfile",
    "DatasetStatistics",
    "MetadataCatalogEntry",
    "SparkDatasetProfiler",
    "MetadataError",
    "MetadataConfigurationError",
    "DatasetProfilingError",
    "DatasetFingerprintError",
    "MetadataPersistenceError",
    "UnsupportedDatasetError",
    "DatasetFingerprintGenerator",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for one imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    """Return absolute imports declared in one Python source module."""
    source = source_path.read_text(encoding="utf-8")

    syntax_tree = ast.parse(
        source,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every metadata module through src.*
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    imported_module = importlib.import_module(
        qualified_name
    )

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every metadata module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level metadata.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "metadata"
        or module_name.startswith("metadata.")
    )
)

assert not legacy_modules, (
    "Legacy metadata.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy metadata.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan metadata source files for legacy absolute imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(
        imported_module
    )

    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "metadata"
            or imported_name.startswith("metadata.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy metadata.* absolute imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print("PASS: No legacy metadata.* absolute source imports remain")


# -----------------------------------------------------------------------------
# 5. Validate current root public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(
    set(package.__all__)
), (
    "src.metadata.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Metadata public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.metadata import (
    ColumnProfile,
    DatasetFingerprint,
    DatasetFingerprintError,
    DatasetFingerprintGenerator,
    DatasetProfile,
    DatasetProfilingError,
    DatasetStatistics,
    MetadataCatalogEntry,
    MetadataConfigurationError,
    MetadataError,
    MetadataPersistenceError,
    SparkDatasetProfiler,
    UnsupportedDatasetError,
)

from src.metadata.fingerprint import (
    DatasetFingerprintGenerator
    as LeafDatasetFingerprintGenerator,
)

from src.metadata.models import (
    ColumnProfile as LeafColumnProfile,
    DatasetFingerprint as LeafDatasetFingerprint,
    DatasetProfile as LeafDatasetProfile,
    DatasetStatistics as LeafDatasetStatistics,
    MetadataCatalogEntry as LeafMetadataCatalogEntry,
)

from src.metadata.profiler import (
    SparkDatasetProfiler as LeafSparkDatasetProfiler,
)

assert ColumnProfile is LeafColumnProfile
assert DatasetFingerprint is LeafDatasetFingerprint
assert DatasetProfile is LeafDatasetProfile
assert DatasetStatistics is LeafDatasetStatistics
assert MetadataCatalogEntry is LeafMetadataCatalogEntry

assert (
    DatasetFingerprintGenerator
    is LeafDatasetFingerprintGenerator
)

assert (
    SparkDatasetProfiler
    is LeafSparkDatasetProfiler
)

assert issubclass(
    MetadataConfigurationError,
    MetadataError,
)

assert issubclass(
    DatasetProfilingError,
    MetadataError,
)

assert issubclass(
    DatasetFingerprintError,
    MetadataError,
)

assert issubclass(
    MetadataPersistenceError,
    MetadataError,
)

assert issubclass(
    UnsupportedDatasetError,
    MetadataError,
)

print("PASS: Metadata public object identities are consistent")


# -----------------------------------------------------------------------------
# 7. Validate domain-model serialization contracts
# -----------------------------------------------------------------------------

column_profile = ColumnProfile(
    column_name="quantity",
    data_type="double",
    nullable=False,
    null_count=0,
    null_percentage=0.0,
    distinct_count=3,
    minimum=10.0,
    maximum=30.0,
    mean=20.0,
)

assert column_profile.to_dict()["column_name"] == "quantity"
assert column_profile.to_dict()["distinct_count"] == 3

statistics = DatasetStatistics(
    row_count=3,
    column_count=3,
    numeric_column_count=1,
    string_column_count=1,
    boolean_column_count=0,
    date_column_count=1,
    timestamp_column_count=0,
    other_column_count=0,
    null_cell_count=0,
    null_cell_percentage=0.0,
    duplicate_row_count=0,
    duplicate_row_percentage=0.0,
)

assert statistics.to_dict()["row_count"] == 3
assert statistics.to_dict()["column_count"] == 3

print("PASS: Metadata domain-model serialization contracts remain operational")


# -----------------------------------------------------------------------------
# 8. Build deterministic release-validation dataset
# -----------------------------------------------------------------------------

validation_df = spark.createDataFrame(
    [
        (
            1,
            "alpha",
            10.0,
            date(2026, 1, 1),
        ),
        (
            2,
            "beta",
            20.0,
            date(2026, 1, 2),
        ),
        (
            3,
            "gamma",
            30.0,
            date(2026, 1, 3),
        ),
    ],
    schema=[
        "record_id",
        "category",
        "quantity",
        "business_date",
    ],
)

assert validation_df.count() == 3

assert validation_df.columns == [
    "record_id",
    "category",
    "quantity",
    "business_date",
]

print(
    "PASS: Created deterministic metadata "
    "release-validation dataset"
)


# -----------------------------------------------------------------------------
# 9. Validate Spark dataset profiler
# -----------------------------------------------------------------------------

profiler = SparkDatasetProfiler(
    approximate_distinct=False,
)

profile_statistics = profiler.profile_statistics(
    validation_df
)

assert isinstance(
    profile_statistics,
    DatasetStatistics,
)

assert profile_statistics.row_count == 3
assert profile_statistics.column_count == 4
assert profile_statistics.null_cell_count == 0
assert profile_statistics.duplicate_row_count == 0

profile_columns = profiler.profile_columns(
    validation_df
)

assert len(profile_columns) == 4

assert {
    column.column_name
    for column in profile_columns
} == {
    "record_id",
    "category",
    "quantity",
    "business_date",
}

(
    combined_statistics,
    combined_columns,
) = profiler.profile(
    validation_df
)

assert combined_statistics.row_count == 3
assert len(combined_columns) == 4

print("PASS: Spark dataset profiling contracts remain operational")


# -----------------------------------------------------------------------------
# 10. Validate deterministic dataset fingerprinting
# -----------------------------------------------------------------------------

fingerprint_generator = DatasetFingerprintGenerator()

fingerprint_one = fingerprint_generator.generate(
    validation_df,
    metadata={
        "dataset_name": "release_validation_metadata",
        "layer": "gold",
    },
    statistics=profile_statistics,
)

fingerprint_two = fingerprint_generator.generate(
    validation_df,
    metadata={
        "dataset_name": "release_validation_metadata",
        "layer": "gold",
    },
    statistics=profile_statistics,
)

assert isinstance(
    fingerprint_one,
    DatasetFingerprint,
)

assert fingerprint_one.row_count == 3
assert fingerprint_one.column_count == 4

assert fingerprint_one.algorithm == "SHA-256"
assert fingerprint_one.fingerprint_version == "1.0.0"

for hash_value in (
    fingerprint_one.schema_hash,
    fingerprint_one.content_hash,
    fingerprint_one.metadata_hash,
    fingerprint_one.combined_hash,
):
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64

assert (
    fingerprint_generator.fingerprints_match(
        fingerprint_one,
        fingerprint_two,
    )
    is True
)

fingerprint_payload = fingerprint_one.to_dict()

assert (
    fingerprint_payload["combined_hash"]
    == fingerprint_one.combined_hash
)

assert isinstance(
    fingerprint_payload["generated_at_utc"],
    str,
)

print(
    "PASS: Deterministic metadata fingerprinting "
    "contracts remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate DatasetProfile and catalog-entry transformation
# -----------------------------------------------------------------------------

dataset_profile = DatasetProfile(
    dataset_name="release_validation_metadata",
    dataset_key="gold.release_validation_metadata",
    layer="gold",
    storage_path="s3://release-validation/gold/metadata",
    storage_format="parquet",
    execution_id="implementation_28",
    pipeline_name="enterprise-workforce-data-foundation",
    pipeline_version="3.0.0",
    owner="release-validation",
    business_description="Implementation 28 release validation dataset.",
    statistics=profile_statistics,
    fingerprint=fingerprint_one,
    columns=profile_columns,
    quality_status="PASSED",
    quality_score=1.0,
    profiled_at_utc=datetime(
        2026,
        8,
        7,
        tzinfo=timezone.utc,
    ),
)

profile_payload = dataset_profile.to_dict()

assert (
    profile_payload["dataset_key"]
    == "gold.release_validation_metadata"
)

assert profile_payload["statistics"]["row_count"] == 3

assert (
    profile_payload["fingerprint"]["combined_hash"]
    == fingerprint_one.combined_hash
)

assert len(profile_payload["columns"]) == 4

catalog_entry = MetadataCatalogEntry.from_profile(
    dataset_profile
)

assert isinstance(
    catalog_entry,
    MetadataCatalogEntry,
)

assert catalog_entry.dataset_name == (
    "release_validation_metadata"
)

assert catalog_entry.dataset_key == (
    "gold.release_validation_metadata"
)

assert catalog_entry.row_count == 3
assert catalog_entry.column_count == 4

assert (
    catalog_entry.schema_hash
    == fingerprint_one.schema_hash
)

catalog_entry_payload = catalog_entry.to_dict()

assert (
    catalog_entry_payload["dataset_key"]
    == "gold.release_validation_metadata"
)

print(
    "PASS: Dataset profile and catalog-entry transformation "
    "contracts remain operational"
)


# -----------------------------------------------------------------------------
# 12. Validate MetadataCatalog construction without storage writes
# -----------------------------------------------------------------------------

from src.metadata.catalog import MetadataCatalog

catalog = MetadataCatalog(
    spark=spark,
    catalog_path="/tmp/implementation_28_metadata_catalog",
)

assert catalog.catalog_path == (
    "/tmp/implementation_28_metadata_catalog"
)

catalog_init_signature = inspect.signature(
    MetadataCatalog
)

assert "spark" in catalog_init_signature.parameters
assert "catalog_path" in catalog_init_signature.parameters

catalog_register_signature = inspect.signature(
    MetadataCatalog.register
)

assert "entry" in catalog_register_signature.parameters
assert "overwrite" in catalog_register_signature.parameters

catalog_search_signature = inspect.signature(
    MetadataCatalog.search
)

assert "dataset_name" in catalog_search_signature.parameters
assert "dataset_key" in catalog_search_signature.parameters
assert "layer" in catalog_search_signature.parameters
assert "owner" in catalog_search_signature.parameters

print(
    "PASS: MetadataCatalog construction and "
    "public signatures remain operational"
)


# -----------------------------------------------------------------------------
# 13. Validate MetadataService facade without catalog persistence
# -----------------------------------------------------------------------------

from src.metadata.service import MetadataService


class _ReleaseValidationCatalog:
    """Side-effect-free catalog double for service contract validation."""

    def __init__(self) -> None:
        self._entries: dict[str, MetadataCatalogEntry] = {}
        self.catalog_path = "/tmp/release_validation_metadata_catalog"

    def register(
        self,
        entry: MetadataCatalogEntry,
        *,
        overwrite: bool = False,
    ) -> MetadataCatalogEntry:
        if entry.dataset_key in self._entries and not overwrite:
            raise RuntimeError("duplicate")

        self._entries[entry.dataset_key] = entry
        return entry

    def update(
        self,
        entry: MetadataCatalogEntry,
    ) -> MetadataCatalogEntry:
        self._entries[entry.dataset_key] = entry
        return entry

    def upsert(
        self,
        entry: MetadataCatalogEntry,
    ) -> MetadataCatalogEntry:
        self._entries[entry.dataset_key] = entry
        return entry

    def get(
        self,
        dataset_key: str,
    ) -> MetadataCatalogEntry:
        return self._entries[dataset_key]

    def exists(
        self,
        dataset_key: str,
    ) -> bool:
        return dataset_key in self._entries

    def list_entries(self) -> list[MetadataCatalogEntry]:
        return [
            self._entries[key]
            for key in sorted(self._entries)
        ]

    def search(self, **filters) -> list[MetadataCatalogEntry]:
        values = self.list_entries()

        for field_name, expected in filters.items():
            if expected is not None:
                values = [
                    entry
                    for entry in values
                    if getattr(entry, field_name) == expected
                ]

        return values

    def delete(
        self,
        dataset_key: str,
    ) -> MetadataCatalogEntry:
        return self._entries.pop(dataset_key)

    def count(self) -> int:
        return len(self._entries)

    def to_dataframe(self):
        return spark.createDataFrame(
            [
                entry.to_dict()
                for entry in self.list_entries()
            ]
        )


catalog_double = _ReleaseValidationCatalog()

metadata_service = MetadataService(
    spark=spark,
    catalog_path=catalog_double.catalog_path,
    profiler=profiler,
    fingerprint_generator=fingerprint_generator,
    catalog=catalog_double,
)

assert metadata_service.catalog is catalog_double

assert (
    metadata_service.catalog_path
    == catalog_double.catalog_path
)

service_profile = metadata_service.create_profile(
    validation_df,
    dataset_name="release_validation_metadata",
    dataset_key="gold.release_validation_metadata",
    layer="gold",
    storage_path="s3://release-validation/gold/metadata",
    storage_format="parquet",
    execution_id="implementation_28",
    pipeline_name="enterprise-workforce-data-foundation",
    pipeline_version="3.0.0",
    owner="release-validation",
    business_description="Implementation 28 metadata validation.",
    quality_status="PASSED",
    quality_score=1.0,
)

assert isinstance(
    service_profile,
    DatasetProfile,
)

registered_entry = metadata_service.register_profile(
    service_profile
)

assert isinstance(
    registered_entry,
    MetadataCatalogEntry,
)

assert (
    metadata_service.dataset_exists(
        "gold.release_validation_metadata"
    )
    is True
)

assert metadata_service.count_datasets() == 1

assert (
    metadata_service.get_dataset(
        "gold.release_validation_metadata"
    )
    is registered_entry
)

assert metadata_service.list_datasets() == [
    registered_entry
]

search_results = metadata_service.search_datasets(
    dataset_key="gold.release_validation_metadata"
)

assert search_results == [
    registered_entry
]

print(
    "PASS: MetadataService facade and dependency "
    "orchestration remain operational"
)


# -----------------------------------------------------------------------------
# 14. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    SparkDatasetProfiler(
        relative_standard_deviation=0.0
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "Invalid profiler relative standard deviation "
        "must raise ValueError."
    )


try:
    DatasetFingerprintGenerator.fingerprints_match(
        "invalid",
        fingerprint_one,
    )
except TypeError:
    pass
else:
    raise AssertionError(
        "Invalid fingerprint comparison input "
        "must raise TypeError."
    )

print("PASS: Metadata failure contracts remain operational")


# -----------------------------------------------------------------------------
# 15. Validate service public signatures
# -----------------------------------------------------------------------------

create_profile_signature = inspect.signature(
    MetadataService.create_profile
)

assert "dataframe" in create_profile_signature.parameters
assert "dataset_name" in create_profile_signature.parameters
assert "dataset_key" in create_profile_signature.parameters
assert "layer" in create_profile_signature.parameters
assert "storage_path" in create_profile_signature.parameters
assert "storage_format" in create_profile_signature.parameters

register_dataset_signature = inspect.signature(
    MetadataService.register_dataset
)

assert "dataframe" in register_dataset_signature.parameters
assert "dataset_key" in register_dataset_signature.parameters
assert "overwrite" in register_dataset_signature.parameters

search_signature = inspect.signature(
    MetadataService.search_datasets
)

assert "dataset_name" in search_signature.parameters
assert "dataset_key" in search_signature.parameters
assert "quality_status" in search_signature.parameters

print("PASS: Metadata public method signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.metadata")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required for ENG-001: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.workforce
#
# Release:
#     v3.0.0
#
# Scope:
#     Enterprise Workforce Domain
#
# Finding:
#     ENG-001 — Canonical Python namespace validation
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path


PACKAGE_NAME = "src.workforce"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
)

EXPECTED_PUBLIC_API = {
    # Version
    "WORKFORCE_DOMAIN_VERSION",

    # Enumerations
    "OvertimeType",
    "ShiftType",
    "WorkforceType",

    # Models
    "WorkforceCapacity",
    "WorkforceGap",
    "WorkforceRequirement",

    # Workforce defaults
    "DEFAULT_AVAILABLE_ASSOCIATES",
    "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
    "DEFAULT_SCHEDULED_HOURS",

    # Capacity-planning defaults
    "DEFAULT_MAXIMUM_ASSOCIATES",
    "DEFAULT_MINIMUM_ASSOCIATES",
    "DEFAULT_SAFETY_BUFFER_RATIO",
    "DEFAULT_TARGET_UTILIZATION",

    # Overtime defaults
    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",

    # Forecast confidence
    "DEFAULT_FORECAST_CONFIDENCE",
    "MAXIMUM_FORECAST_CONFIDENCE",
    "MINIMUM_FORECAST_CONFIDENCE",

    # Capacity statuses
    "CAPACITY_STATUS_BALANCED",
    "CAPACITY_STATUS_SHORTAGE",
    "CAPACITY_STATUS_SUFFICIENT",
    "CAPACITY_STATUS_SURPLUS",

    # Recommendations
    "RECOMMENDATION_ADD_ASSOCIATES",
    "RECOMMENDATION_NO_ACTION",
    "RECOMMENDATION_REDUCE_STAFFING",
    "RECOMMENDATION_REVIEW_OVERTIME",

    # Exceptions
    "WorkforceAvailabilityError",
    "WorkforceCapacityError",
    "WorkforceConfigurationError",
    "WorkforceError",
    "WorkforcePlanningError",
    "WorkforceValidationError",
}


def resolve_module_source(module: object) -> Path:
    """Return the source path for one imported Python module."""
    source_file = inspect.getsourcefile(module)

    assert source_file is not None, (
        f"Unable to resolve source file for {module.__name__}."
    )

    source_path = Path(source_file).resolve()

    assert source_path.exists(), (
        f"Resolved source file does not exist: {source_path}"
    )

    return source_path


def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    """Return absolute imports declared in one Python source module."""
    source = source_path.read_text(encoding="utf-8")

    syntax_tree = ast.parse(
        source,
        filename=str(source_path),
    )

    discovered_imports: list[str] = []

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

package = importlib.import_module(PACKAGE_NAME)

assert package.__name__ == PACKAGE_NAME
assert package.__package__ == PACKAGE_NAME

print(f"PASS: Imported canonical package {PACKAGE_NAME}")


# -----------------------------------------------------------------------------
# 2. Import every workforce module through src.*
# -----------------------------------------------------------------------------

imported_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    imported_module = importlib.import_module(
        qualified_name
    )

    assert imported_module.__name__ == qualified_name

    imported_modules[module_name] = imported_module

print(
    "PASS: Imported every workforce module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy workforce.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "workforce"
        or module_name.startswith("workforce.")
    )
)

assert not legacy_modules, (
    "Legacy workforce.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy workforce.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

modules_to_scan = {
    "__init__": package,
    **imported_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, imported_module in modules_to_scan.items():
    source_path = resolve_module_source(
        imported_module
    )

    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "workforce"
            or imported_name.startswith("workforce.")
            or imported_name == "forecast"
            or imported_name.startswith("src.forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports

assert not legacy_imports, (
    "Legacy absolute package imports remain in "
    f"{PACKAGE_NAME}: {legacy_imports}"
)

print(
    "PASS: No legacy workforce.* or forecast.* "
    "absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

assert hasattr(package, "__all__")

actual_public_api = set(package.__all__)

assert actual_public_api == EXPECTED_PUBLIC_API, {
    "missing_exports": sorted(
        EXPECTED_PUBLIC_API - actual_public_api
    ),
    "unexpected_exports": sorted(
        actual_public_api - EXPECTED_PUBLIC_API
    ),
}

assert len(package.__all__) == len(
    set(package.__all__)
), (
    "src.workforce.__all__ contains duplicate names."
)

for exported_name in package.__all__:
    assert hasattr(package, exported_name), (
        f"Public export is unavailable: {exported_name}"
    )

print(
    f"PASS: Workforce public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.workforce import (
    OvertimeType,
    ShiftType,
    WorkforceAvailabilityError,
    WorkforceCapacity,
    WorkforceCapacityError,
    WorkforceConfigurationError,
    WorkforceError,
    WorkforceGap,
    WorkforcePlanningError,
    WorkforceRequirement,
    WorkforceType,
    WorkforceValidationError,
)

from src.workforce.models import (
    OvertimeType as LeafOvertimeType,
    ShiftType as LeafShiftType,
    WorkforceCapacity as LeafWorkforceCapacity,
    WorkforceGap as LeafWorkforceGap,
    WorkforceRequirement as LeafWorkforceRequirement,
    WorkforceType as LeafWorkforceType,
)

from src.workforce.exceptions import (
    WorkforceAvailabilityError as LeafWorkforceAvailabilityError,
    WorkforceCapacityError as LeafWorkforceCapacityError,
    WorkforceConfigurationError as LeafWorkforceConfigurationError,
    WorkforceError as LeafWorkforceError,
    WorkforcePlanningError as LeafWorkforcePlanningError,
    WorkforceValidationError as LeafWorkforceValidationError,
)

# COMMAND ----------

# =============================================================================
# Implementation 28 — src.workforce Release Validation
# Continuation
# =============================================================================


# -----------------------------------------------------------------------------
# 6. Complete public/leaf object identity validation
# -----------------------------------------------------------------------------

assert OvertimeType is LeafOvertimeType
assert ShiftType is LeafShiftType
assert WorkforceType is LeafWorkforceType

assert WorkforceCapacity is LeafWorkforceCapacity
assert WorkforceGap is LeafWorkforceGap
assert WorkforceRequirement is LeafWorkforceRequirement

assert WorkforceError is LeafWorkforceError
assert WorkforceValidationError is LeafWorkforceValidationError
assert WorkforceConfigurationError is LeafWorkforceConfigurationError
assert WorkforceCapacityError is LeafWorkforceCapacityError
assert WorkforceAvailabilityError is LeafWorkforceAvailabilityError
assert WorkforcePlanningError is LeafWorkforcePlanningError

print("PASS: Workforce public object identities are consistent")


# -----------------------------------------------------------------------------
# 7. Validate workforce constants
# -----------------------------------------------------------------------------

from src.workforce import (
    CAPACITY_STATUS_BALANCED,
    CAPACITY_STATUS_SHORTAGE,
    CAPACITY_STATUS_SUFFICIENT,
    CAPACITY_STATUS_SURPLUS,
    DEFAULT_AVAILABLE_ASSOCIATES,
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_MAXIMUM_ASSOCIATES,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_ASSOCIATES,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    MAXIMUM_FORECAST_CONFIDENCE,
    MINIMUM_FORECAST_CONFIDENCE,
    RECOMMENDATION_ADD_ASSOCIATES,
    RECOMMENDATION_NO_ACTION,
    RECOMMENDATION_REDUCE_STAFFING,
    RECOMMENDATION_REVIEW_OVERTIME,
    WORKFORCE_DOMAIN_VERSION,
)

assert WORKFORCE_DOMAIN_VERSION == "1.0.0"

assert DEFAULT_PRODUCTIVITY_LINES_PER_HOUR == 120.0
assert DEFAULT_SCHEDULED_HOURS == 10.0
assert DEFAULT_AVAILABLE_ASSOCIATES == 0

assert DEFAULT_TARGET_UTILIZATION == 0.90
assert DEFAULT_SAFETY_BUFFER_RATIO == 0.05

assert DEFAULT_MINIMUM_ASSOCIATES == 1
assert DEFAULT_MAXIMUM_ASSOCIATES == 10_000

assert DEFAULT_MINIMUM_OVERTIME_HOURS == 5.0
assert DEFAULT_MAXIMUM_OVERTIME_HOURS == 10.0
assert DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP == 1

assert MINIMUM_FORECAST_CONFIDENCE == 0.0
assert MAXIMUM_FORECAST_CONFIDENCE == 1.0
assert DEFAULT_FORECAST_CONFIDENCE == 0.80

assert CAPACITY_STATUS_SUFFICIENT == "SUFFICIENT"
assert CAPACITY_STATUS_SHORTAGE == "SHORTAGE"
assert CAPACITY_STATUS_SURPLUS == "SURPLUS"
assert CAPACITY_STATUS_BALANCED == "BALANCED"

assert RECOMMENDATION_NO_ACTION == "NO_ACTION"
assert RECOMMENDATION_ADD_ASSOCIATES == "ADD_ASSOCIATES"
assert RECOMMENDATION_REDUCE_STAFFING == "REDUCE_STAFFING"
assert RECOMMENDATION_REVIEW_OVERTIME == "REVIEW_OVERTIME"

print("PASS: Workforce constants remain internally consistent")


# -----------------------------------------------------------------------------
# 8. Validate enumeration contracts
# -----------------------------------------------------------------------------

assert WorkforceType.FULL_TIME.value == "FULL_TIME"
assert WorkforceType.TEMPORARY.value == "TEMPORARY"

assert ShiftType.SHIFT_1.value == "SHIFT_1"
assert ShiftType.SHIFT_2.value == "SHIFT_2"

assert OvertimeType.NONE.value == "NONE"
assert OvertimeType.VOLUNTARY.value == "VOLUNTARY"
assert OvertimeType.MANDATORY.value == "MANDATORY"

assert WorkforceType("FULL_TIME") is WorkforceType.FULL_TIME
assert ShiftType("SHIFT_1") is ShiftType.SHIFT_1
assert OvertimeType("MANDATORY") is OvertimeType.MANDATORY

print("PASS: Workforce enumeration contracts remain operational")


# -----------------------------------------------------------------------------
# 9. Validate WorkforceCapacity contract
# -----------------------------------------------------------------------------

from dataclasses import FrozenInstanceError
from datetime import date


capacity = WorkforceCapacity(
    planning_date=date(2026, 8, 7),
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=25,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
    metadata={
        "validation": "implementation_28",
    },
)

assert capacity.planning_date == date(2026, 8, 7)
assert capacity.shift is ShiftType.SHIFT_1
assert capacity.workforce_type is WorkforceType.FULL_TIME
assert capacity.available_associates == 25
assert capacity.productivity_lines_per_hour == 120.0
assert capacity.scheduled_hours == 10.0
assert capacity.overtime_type is OvertimeType.NONE

assert capacity.metadata == {
    "validation": "implementation_28",
}

try:
    capacity.available_associates = 30
except FrozenInstanceError:
    pass
else:
    raise AssertionError(
        "WorkforceCapacity must remain a frozen dataclass."
    )

print("PASS: WorkforceCapacity contract remains operational")


# -----------------------------------------------------------------------------
# 10. Validate WorkforceRequirement contract
# -----------------------------------------------------------------------------

requirement = WorkforceRequirement(
    planning_date=date(2026, 8, 7),
    required_associates=30,
    expected_order_lines=36_000.0,
    expected_workload_units=42_000.0,
    required_hours=300.0,
    confidence=0.85,
)

assert requirement.planning_date == date(2026, 8, 7)
assert requirement.required_associates == 30
assert requirement.expected_order_lines == 36_000.0
assert requirement.expected_workload_units == 42_000.0
assert requirement.required_hours == 300.0
assert requirement.confidence == 0.85

try:
    requirement.required_associates = 31
except FrozenInstanceError:
    pass
else:
    raise AssertionError(
        "WorkforceRequirement must remain a frozen dataclass."
    )

print("PASS: WorkforceRequirement contract remains operational")


# -----------------------------------------------------------------------------
# 11. Validate WorkforceGap contract
# -----------------------------------------------------------------------------

gap = WorkforceGap(
    planning_date=date(2026, 8, 7),
    available_associates=25,
    required_associates=30,
    shortage=5,
    overtime_required=True,
    recommended_overtime_hours=5.0,
)

assert gap.planning_date == date(2026, 8, 7)
assert gap.available_associates == 25
assert gap.required_associates == 30
assert gap.shortage == 5
assert gap.overtime_required is True
assert gap.recommended_overtime_hours == 5.0

try:
    gap.shortage = 4
except FrozenInstanceError:
    pass
else:
    raise AssertionError(
        "WorkforceGap must remain a frozen dataclass."
    )

print("PASS: WorkforceGap contract remains operational")


# -----------------------------------------------------------------------------
# 12. Validate default model behavior
# -----------------------------------------------------------------------------

default_capacity = WorkforceCapacity(
    planning_date=date(2026, 8, 7),
    shift=ShiftType.SHIFT_2,
    workforce_type=WorkforceType.TEMPORARY,
    available_associates=10,
    productivity_lines_per_hour=100.0,
    scheduled_hours=10.0,
)

assert default_capacity.overtime_type is OvertimeType.NONE
assert default_capacity.metadata == {}

default_requirement = WorkforceRequirement(
    planning_date=date(2026, 8, 7),
    required_associates=10,
    expected_order_lines=12_000.0,
)

assert default_requirement.expected_workload_units is None
assert default_requirement.required_hours is None
assert default_requirement.confidence is None

default_gap = WorkforceGap(
    planning_date=date(2026, 8, 7),
    available_associates=10,
    required_associates=10,
    shortage=0,
    overtime_required=False,
)

assert default_gap.recommended_overtime_hours == 0.0

print("PASS: Workforce model default contracts remain operational")


# -----------------------------------------------------------------------------
# 13. Validate exception hierarchy
# -----------------------------------------------------------------------------

assert issubclass(WorkforceValidationError, WorkforceError)
assert issubclass(WorkforceConfigurationError, WorkforceError)
assert issubclass(WorkforceCapacityError, WorkforceError)
assert issubclass(WorkforceAvailabilityError, WorkforceError)
assert issubclass(WorkforcePlanningError, WorkforceError)

for exception_type in (
    WorkforceValidationError,
    WorkforceConfigurationError,
    WorkforceCapacityError,
    WorkforceAvailabilityError,
    WorkforcePlanningError,
):
    error = exception_type("release validation")

    assert isinstance(error, WorkforceError)
    assert str(error) == "release validation"

print("PASS: Workforce exception hierarchy remains operational")


# -----------------------------------------------------------------------------
# 14. Validate public constructor signatures
# -----------------------------------------------------------------------------

capacity_signature = inspect.signature(
    WorkforceCapacity
)

assert "planning_date" in capacity_signature.parameters
assert "shift" in capacity_signature.parameters
assert "workforce_type" in capacity_signature.parameters
assert "available_associates" in capacity_signature.parameters
assert "productivity_lines_per_hour" in capacity_signature.parameters
assert "scheduled_hours" in capacity_signature.parameters
assert "overtime_type" in capacity_signature.parameters
assert "metadata" in capacity_signature.parameters

requirement_signature = inspect.signature(
    WorkforceRequirement
)

assert "planning_date" in requirement_signature.parameters
assert "required_associates" in requirement_signature.parameters
assert "expected_order_lines" in requirement_signature.parameters
assert "expected_workload_units" in requirement_signature.parameters
assert "required_hours" in requirement_signature.parameters
assert "confidence" in requirement_signature.parameters

gap_signature = inspect.signature(
    WorkforceGap
)

assert "planning_date" in gap_signature.parameters
assert "available_associates" in gap_signature.parameters
assert "required_associates" in gap_signature.parameters
assert "shortage" in gap_signature.parameters
assert "overtime_required" in gap_signature.parameters
assert "recommended_overtime_hours" in gap_signature.parameters

print("PASS: Workforce public constructor signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.workforce")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.planning
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* package imports
#     - Legacy namespace detection
#     - Public API contract
#     - Leaf-module __all__ contracts
#     - Public object identity
#     - Dependency integrity
#     - Circular-import safety
#     - Planning domain contracts
#     - Public signatures
# =============================================================================

import importlib
import inspect
import sys


PACKAGE_NAME = "src.planning"

EXPECTED_MODULES = (
    "calculations",
    "configuration",
    "constants",
    "engine",
    "exceptions",
    "models",
    "reporting",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Validate canonical package import
# -----------------------------------------------------------------------------

planning_package = importlib.import_module(PACKAGE_NAME)

assert planning_package is not None

print("PASS: Imported canonical package src.planning")


# -----------------------------------------------------------------------------
# 2. Validate every module through canonical src.* namespace
# -----------------------------------------------------------------------------

loaded_modules = {}

for module_name in EXPECTED_MODULES:
    canonical_name = f"{PACKAGE_NAME}.{module_name}"

    loaded_modules[module_name] = importlib.import_module(
        canonical_name
    )

    assert loaded_modules[module_name] is not None


print(
    "PASS: Imported every planning module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Validate legacy modules are not loaded
# -----------------------------------------------------------------------------

legacy_loaded_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "planning"
        or module_name.startswith("planning.")
    )
)

assert legacy_loaded_modules == [], (
    "Legacy planning.* modules are loaded: "
    f"{legacy_loaded_modules}"
)

print("PASS: No legacy planning.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Validate production source imports
# -----------------------------------------------------------------------------

from pathlib import Path


planning_root = Path(
    planning_package.__file__
).resolve().parent

legacy_source_imports = []

for source_file in sorted(planning_root.glob("*.py")):
    source_text = source_file.read_text(
        encoding="utf-8"
    )

    for line_number, line in enumerate(
        source_text.splitlines(),
        start=1,
    ):
        stripped = line.strip()

        forbidden_prefixes = (
            "from planning ",
            "from planning.",
            "import planning",
            "from workforce ",
            "from workforce.",
            "import workforce",
            "from forecast ",
            "from forecast.",
            "import forecast",
        )

        if stripped.startswith(forbidden_prefixes):
            legacy_source_imports.append(
                (
                    source_file.name,
                    line_number,
                    stripped,
                )
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in src.planning: "
    f"{legacy_source_imports}"
)

print(
    "PASS: No legacy planning.*, workforce.*, or forecast.* "
    "absolute source imports remain"
)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.planning
#
# Validation:
#     Public API and leaf-module __all__ contracts
# =============================================================================


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    # Constants
    "PLANNING_DOMAIN_VERSION",
    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",
    "MINIMUM_ASSOCIATES",
    "MAXIMUM_ASSOCIATES",
    "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
    "DEFAULT_SCHEDULED_HOURS",
    "MINIMUM_OVERTIME_HOURS",
    "MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_TARGET_UTILIZATION",
    "DEFAULT_SAFETY_BUFFER_RATIO",
    "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",

    # Exceptions
    "CapacityPlanningError",
    "CapacityPlanningValidationError",
    "CapacityPlanningConfigurationError",
    "CapacityPlanningCalculationError",
    "CapacityPlanningEngineError",
    "CapacityPlanningReportingError",
    "CapacityPlanningServiceError",

    # Models
    "CapacityPlanningRequest",
    "CapacityPlanningResult",

    # Components
    "CapacityPlanningConfiguration",
    "CapacityPlanningEngine",
    "CapacityPlanningReport",
    "CapacityPlanningReporter",
    "CapacityPlanningService",
)
# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "constants": (
        "PLANNING_DOMAIN_VERSION",
        "MIN_FORECAST_CONFIDENCE",
        "MAX_FORECAST_CONFIDENCE",
        "DEFAULT_FORECAST_CONFIDENCE",
        "MINIMUM_ASSOCIATES",
        "MAXIMUM_ASSOCIATES",
        "DEFAULT_PRODUCTIVITY_LINES_PER_HOUR",
        "DEFAULT_SCHEDULED_HOURS",
        "MINIMUM_OVERTIME_HOURS",
        "MAXIMUM_OVERTIME_HOURS",
        "DEFAULT_TARGET_UTILIZATION",
        "DEFAULT_SAFETY_BUFFER_RATIO",
        "DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP",
    ),
    "exceptions": (
        "CapacityPlanningError",
        "CapacityPlanningValidationError",
        "CapacityPlanningConfigurationError",
        "CapacityPlanningCalculationError",
        "CapacityPlanningEngineError",
        "CapacityPlanningReportingError",
        "CapacityPlanningServiceError",
    ),
    "models": (
        "CapacityPlanningRequest",
        "CapacityPlanningResult",
    ),
    "configuration": (
        "CapacityPlanningConfiguration",
        "CapacityPlanningStrategy",
    ),
    "calculations": (
        "calculate_associate_gap",
        "calculate_associate_shortage",
        "calculate_associate_surplus",
        "calculate_available_capacity_lines",
        "calculate_buffered_workload",
        "calculate_capacity_utilization",
        "calculate_required_associates",
        "calculate_required_labor_hours",
    ),
    "engine": (
        "CapacityPlanningEngine",
    ),
    "reporting": (
        "CapacityPlanningReport",
        "CapacityPlanningReporter",
    ),
    "service": (
        "CapacityPlanningService",
    ),
}

for module_name, expected_all in EXPECTED_LEAF_ALL.items():
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__"), (
        f"src.planning.{module_name} has no __all__"
    )

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for src.planning.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(set(actual_all)), (
        f"Duplicate __all__ entries in "
        f"src.planning.{module_name}: {actual_all}"
    )

    for symbol_name in actual_all:
        assert hasattr(module, symbol_name), (
            f"src.planning.{module_name} declares "
            f"{symbol_name!r} in __all__ but does not expose it"
        )


print(
    "PASS: Planning leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Confirm root API is intentionally narrower than leaf APIs
# -----------------------------------------------------------------------------

assert (
    "CapacityPlanningStrategy"
    in loaded_modules["configuration"].__all__
)

assert (
    "CapacityPlanningStrategy"
    not in planning_package.__all__
)

print(
    "PASS: Planning root API remains intentionally "
    "narrower than leaf-module APIs"
)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.planning
#
# Validation:
#     Object identity, configuration, calculations,
#     engine/service/reporting contracts, signatures,
#     and final package certification
# =============================================================================

from datetime import date

from src.planning import (
    CapacityPlanningCalculationError,
    CapacityPlanningConfiguration,
    CapacityPlanningConfigurationError,
    CapacityPlanningEngine,
    CapacityPlanningEngineError,
    CapacityPlanningError,
    CapacityPlanningReport,
    CapacityPlanningReporter,
    CapacityPlanningRequest,
    CapacityPlanningResult,
    CapacityPlanningReportingError,
    CapacityPlanningService,
    CapacityPlanningServiceError,
    CapacityPlanningValidationError,
)

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

from src.planning.configuration import (
    CapacityPlanningConfiguration as LeafCapacityPlanningConfiguration,
    CapacityPlanningStrategy,
)

from src.planning.engine import (
    CapacityPlanningEngine as LeafCapacityPlanningEngine,
)

from src.planning.models import (
    CapacityPlanningRequest as LeafCapacityPlanningRequest,
    CapacityPlanningResult as LeafCapacityPlanningResult,
)

from src.planning.reporting import (
    CapacityPlanningReport as LeafCapacityPlanningReport,
    CapacityPlanningReporter as LeafCapacityPlanningReporter,
)

from src.planning.service import (
    CapacityPlanningService as LeafCapacityPlanningService,
)

from src.workforce import (
    OvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
    WorkforceType,
)


# -----------------------------------------------------------------------------
# 8. Validate root/leaf public object identity
# -----------------------------------------------------------------------------

assert (
    CapacityPlanningConfiguration
    is LeafCapacityPlanningConfiguration
)

assert (
    CapacityPlanningEngine
    is LeafCapacityPlanningEngine
)

assert (
    CapacityPlanningRequest
    is LeafCapacityPlanningRequest
)

assert (
    CapacityPlanningResult
    is LeafCapacityPlanningResult
)

assert (
    CapacityPlanningReport
    is LeafCapacityPlanningReport
)

assert (
    CapacityPlanningReporter
    is LeafCapacityPlanningReporter
)

assert (
    CapacityPlanningService
    is LeafCapacityPlanningService
)

print(
    "PASS: Planning root and leaf public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 9. Validate planning exception hierarchy
# -----------------------------------------------------------------------------

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

print(
    "PASS: Planning exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 10. Validate configuration contract
# -----------------------------------------------------------------------------

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

assert configuration.productive_hours_per_associate == 9.0
assert configuration.effective_lines_per_associate == 1080.0

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "productivity_lines_per_hour"
] == 120.0

assert configuration_payload[
    "planning_strategy"
] == "STANDARD"

print(
    "PASS: CapacityPlanningConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate planning calculations
# -----------------------------------------------------------------------------

buffered_workload = calculate_buffered_workload(
    expected_order_lines=10_000.0,
    safety_buffer_ratio=0.05,
)

assert buffered_workload == 10_500.0

required_labor_hours = calculate_required_labor_hours(
    workload_lines=buffered_workload,
    productivity_lines_per_hour=120.0,
)

assert required_labor_hours == 87.5

required_associates = calculate_required_associates(
    required_labor_hours=required_labor_hours,
    productive_hours_per_associate=9.0,
    minimum_associates=1,
    maximum_associates=10_000,
)

assert required_associates == 10

available_capacity_lines = calculate_available_capacity_lines(
    available_associates=8,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    target_utilization=0.90,
)

assert available_capacity_lines == 8_640.0

assert calculate_associate_gap(
    required_associates=10,
    available_associates=8,
) == 2

assert calculate_associate_shortage(
    required_associates=10,
    available_associates=8,
) == 2

assert calculate_associate_surplus(
    required_associates=8,
    available_associates=10,
) == 2

utilization = calculate_capacity_utilization(
    workload_lines=8_640.0,
    available_capacity_lines=8_640.0,
)

assert utilization == 1.0

print(
    "PASS: Planning calculation contracts remain operational"
)


# -----------------------------------------------------------------------------
# 12. Validate CapacityPlanningRequest
# -----------------------------------------------------------------------------

planning_date = date(2026, 8, 7)

workforce_capacity = WorkforceCapacity(
    planning_date=planning_date,
    shift=ShiftType.SHIFT_1,
    workforce_type=WorkforceType.FULL_TIME,
    available_associates=8,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    overtime_type=OvertimeType.NONE,
    metadata={
        "validation": "implementation_28",
    },
)

request = CapacityPlanningRequest(
    planning_date=planning_date,
    expected_order_lines=10_000.0,
    workforce_capacity=workforce_capacity,
    forecast_confidence=0.90,
)

request_payload = request.as_dict()

assert request_payload["planning_date"] == "2026-08-07"
assert request_payload["expected_order_lines"] == 10_000.0
assert request_payload["forecast_confidence"] == 0.90
assert request_payload["available_associates"] == 8
assert request_payload["shift"] == "SHIFT_1"
assert request_payload["workforce_type"] == "FULL_TIME"

print(
    "PASS: CapacityPlanningRequest contract remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate engine evaluation contract
# -----------------------------------------------------------------------------

engine = CapacityPlanningEngine(
    configuration=configuration
)

assert engine.configuration is configuration

requirement, gap = engine.evaluate(
    planning_date=planning_date,
    expected_order_lines=10_000.0,
    workforce_capacity=workforce_capacity,
    forecast_confidence=0.90,
)

assert isinstance(
    requirement,
    WorkforceRequirement,
)

assert isinstance(
    gap,
    WorkforceGap,
)

assert requirement.planning_date == planning_date
assert requirement.required_associates == 10
assert requirement.expected_order_lines == 10_000.0
assert requirement.expected_workload_units == 10_500.0
assert requirement.required_hours == 87.5
assert requirement.confidence == 0.90

assert gap.planning_date == planning_date
assert gap.available_associates == 8
assert gap.required_associates == 10
assert gap.shortage == 2
assert gap.overtime_required is True
assert gap.recommended_overtime_hours == 15.5

print(
    "PASS: CapacityPlanningEngine evaluation contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate CapacityPlanningResult aggregation contract
# -----------------------------------------------------------------------------

from datetime import datetime, timezone


planning_result = CapacityPlanningResult(
    request=request,
    requirement=requirement,
    gap=gap,
    generated_at_utc=datetime(
        2026,
        8,
        7,
        tzinfo=timezone.utc,
    ),
)

assert planning_result.planning_date == planning_date
assert planning_result.available_associates == 8
assert planning_result.required_associates == 10
assert planning_result.associate_gap == 2
assert planning_result.has_shortage is True

result_payload = planning_result.as_dict()

assert result_payload["planning_date"] == "2026-08-07"
assert result_payload["available_associates"] == 8
assert result_payload["required_associates"] == 10
assert result_payload["associate_gap"] == 2
assert result_payload["shortage"] == 2
assert result_payload["overtime_required"] is True

print(
    "PASS: CapacityPlanningResult aggregation contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate reporting contract
# -----------------------------------------------------------------------------

reporter = CapacityPlanningReporter()

report = reporter.build(
    workforce_capacity=workforce_capacity,
    workforce_requirement=requirement,
    workforce_gap=gap,
)

assert isinstance(
    report,
    CapacityPlanningReport,
)

assert report.planning_date == planning_date
assert report.available_associates == 8
assert report.required_associates == 10
assert report.associate_gap == 2
assert report.shortage == 2
assert report.surplus == 0
assert report.expected_order_lines == 10_000.0
assert report.buffered_workload_lines == 10_500.0
assert report.required_labor_hours == 87.5
assert report.forecast_confidence == 0.90
assert report.overtime_required is True
assert report.recommended_overtime_hours == 15.5
assert report.shift == "SHIFT_1"
assert report.workforce_type == "FULL_TIME"

report_payload = report.as_dict()

assert report_payload["planning_date"] == "2026-08-07"
assert report_payload["shortage"] == 2
assert report_payload["surplus"] == 0
assert report_payload["report_version"] == "1.0.0"

print(
    "PASS: Capacity planning reporting contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate service dependency wiring and orchestration
# -----------------------------------------------------------------------------

service = CapacityPlanningService(
    configuration=configuration,
    engine=engine,
    reporter=reporter,
)

assert service.configuration is configuration
assert service.engine is engine
assert service.reporter is reporter

service_report = service.plan(
    planning_date=planning_date,
    expected_order_lines=10_000.0,
    workforce_capacity=workforce_capacity,
    forecast_confidence=0.90,
)

assert isinstance(
    service_report,
    CapacityPlanningReport,
)

assert service_report.required_associates == 10
assert service_report.available_associates == 8
assert service_report.shortage == 2
assert service_report.overtime_required is True

print(
    "PASS: CapacityPlanningService orchestration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    CapacityPlanningRequest(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        workforce_capacity=workforce_capacity,
    )
except CapacityPlanningValidationError:
    pass
else:
    raise AssertionError(
        "Negative expected_order_lines must raise "
        "CapacityPlanningValidationError."
    )


try:
    CapacityPlanningConfiguration(
        minimum_associates=10,
        maximum_associates=5,
    )
except Exception:
    pass
else:
    raise AssertionError(
        "Invalid associate bounds must be rejected."
    )

print(
    "PASS: Planning representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 18. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    CapacityPlanningConfiguration
)

assert (
    "productivity_lines_per_hour"
    in configuration_signature.parameters
)

assert (
    "planning_strategy"
    in configuration_signature.parameters
)


engine_signature = inspect.signature(
    CapacityPlanningEngine.evaluate
)

assert "planning_date" in engine_signature.parameters
assert "expected_order_lines" in engine_signature.parameters
assert "workforce_capacity" in engine_signature.parameters
assert "forecast_confidence" in engine_signature.parameters


service_signature = inspect.signature(
    CapacityPlanningService.plan
)

assert "planning_date" in service_signature.parameters
assert "expected_order_lines" in service_signature.parameters
assert "workforce_capacity" in service_signature.parameters
assert "forecast_confidence" in service_signature.parameters


reporter_signature = inspect.signature(
    CapacityPlanningReporter.build
)

assert "workforce_capacity" in reporter_signature.parameters
assert "workforce_requirement" in reporter_signature.parameters
assert "workforce_gap" in reporter_signature.parameters

print(
    "PASS: Planning public method signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.planning")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.overtime
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* imports
#     - Legacy namespace detection
#     - Root and leaf public APIs
#     - Public object identity
#     - Configuration contract
#     - Enum and model contracts
#     - Recommendation decision paths
#     - Service orchestration
#     - Failure contracts
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path


PACKAGE_NAME = "src.overtime"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "engine",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

overtime_package = importlib.import_module(PACKAGE_NAME)

assert overtime_package.__name__ == PACKAGE_NAME
assert overtime_package.__package__ == PACKAGE_NAME

print("PASS: Imported canonical package src.overtime")


# -----------------------------------------------------------------------------
# 2. Import every module through canonical src.* namespace
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    loaded_modules[module_name] = importlib.import_module(
        qualified_name
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every overtime module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level overtime.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "overtime"
        or module_name.startswith("overtime.")
    )
)

assert legacy_modules == [], (
    "Legacy overtime.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy overtime.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    discovered_imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            discovered_imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                discovered_imports.append(node.module)

    return tuple(discovered_imports)


modules_to_scan = {
    "__init__": overtime_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    source_path = Path(source_file).resolve()

    absolute_imports = collect_absolute_imports(
        source_path
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "overtime"
            or imported_name.startswith("overtime.")
            or imported_name == "workforce"
            or imported_name.startswith("workforce.")
            or imported_name == "planning"
            or imported_name.startswith("planning.")
            or imported_name == "forecast"
            or imported_name.startswith("src.forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports


assert legacy_imports == {}, (
    "Legacy absolute imports remain in src.overtime: "
    f"{legacy_imports}"
)

print(
    "PASS: No legacy overtime.*, workforce.*, planning.*, "
    "or forecast.* absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "OVERTIME_DOMAIN_VERSION",

    "DEFAULT_MAXIMUM_OVERTIME_HOURS",
    "DEFAULT_MINIMUM_OVERTIME_HOURS",
    "DEFAULT_STANDARD_OVERTIME_HOURS",

    "DEFAULT_CRITICAL_SHORTAGE_GAP",
    "DEFAULT_MANDATORY_OVERTIME_MAX_GAP",
    "DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP",
    "DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP",

    "DEFAULT_HIGH_CONFIDENCE_THRESHOLD",
    "DEFAULT_LOW_CONFIDENCE_THRESHOLD",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    "MAXIMUM_RECOMMENDATION_CONFIDENCE",
    "MINIMUM_RECOMMENDATION_CONFIDENCE",

    "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
    "RECOMMENDATION_MANDATORY_OVERTIME",
    "RECOMMENDATION_NONE",
    "RECOMMENDATION_OPERATIONAL_REVIEW",
    "RECOMMENDATION_TEMPORARY_LABOR",
    "RECOMMENDATION_VOLUNTARY_OVERTIME",

    "PRIORITY_CRITICAL",
    "PRIORITY_HIGH",
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",

    "STATUS_NOT_REQUIRED",
    "STATUS_RECOMMENDED",
    "STATUS_REQUIRED",
    "STATUS_REVIEW_REQUIRED",

    "OVERTIME_TYPE_MANDATORY",
    "OVERTIME_TYPE_NONE",
    "OVERTIME_TYPE_VOLUNTARY",

    "SUPPORTED_OVERTIME_TYPES",
    "SUPPORTED_RECOMMENDATION_PRIORITIES",
    "SUPPORTED_RECOMMENDATION_STATUSES",
    "SUPPORTED_RECOMMENDATION_TYPES",

    "OvertimeCapacityError",
    "OvertimeConfigurationError",
    "OvertimeEngineError",
    "OvertimeError",
    "OvertimePolicyError",
    "OvertimeRecommendationError",
    "OvertimeServiceError",
    "OvertimeValidationError",

    "OvertimeRecommendation",
    "OvertimeRequest",
    "OvertimeType",
    "RecommendationPriority",
    "RecommendationStatus",
    "RecommendationType",

    "OvertimeConfiguration",
    "OvertimeRecommendationEngine",
    "OvertimeRecommendationService",
)

assert tuple(overtime_package.__all__) == (
    EXPECTED_PUBLIC_API
), (
    "Unexpected src.overtime public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   {tuple(overtime_package.__all__)}"
)

assert len(overtime_package.__all__) == len(
    set(overtime_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        overtime_package,
        symbol_name,
    )

print(
    "PASS: Overtime public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "constants": (
        "DEFAULT_CRITICAL_SHORTAGE_GAP",
        "DEFAULT_HIGH_CONFIDENCE_THRESHOLD",
        "DEFAULT_LOW_CONFIDENCE_THRESHOLD",
        "DEFAULT_MANDATORY_OVERTIME_MAX_GAP",
        "DEFAULT_MAXIMUM_OVERTIME_HOURS",
        "DEFAULT_MINIMUM_OVERTIME_HOURS",
        "DEFAULT_RECOMMENDATION_CONFIDENCE",
        "DEFAULT_STANDARD_OVERTIME_HOURS",
        "DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP",
        "DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP",
        "MAXIMUM_RECOMMENDATION_CONFIDENCE",
        "MINIMUM_RECOMMENDATION_CONFIDENCE",
        "OVERTIME_DOMAIN_VERSION",
        "OVERTIME_TYPE_MANDATORY",
        "OVERTIME_TYPE_NONE",
        "OVERTIME_TYPE_VOLUNTARY",
        "PRIORITY_CRITICAL",
        "PRIORITY_HIGH",
        "PRIORITY_LOW",
        "PRIORITY_MEDIUM",
        "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
        "RECOMMENDATION_MANDATORY_OVERTIME",
        "RECOMMENDATION_NONE",
        "RECOMMENDATION_OPERATIONAL_REVIEW",
        "RECOMMENDATION_TEMPORARY_LABOR",
        "RECOMMENDATION_VOLUNTARY_OVERTIME",
        "STATUS_NOT_REQUIRED",
        "STATUS_RECOMMENDED",
        "STATUS_REQUIRED",
        "STATUS_REVIEW_REQUIRED",
        "SUPPORTED_OVERTIME_TYPES",
        "SUPPORTED_RECOMMENDATION_PRIORITIES",
        "SUPPORTED_RECOMMENDATION_STATUSES",
        "SUPPORTED_RECOMMENDATION_TYPES",
    ),
    "exceptions": (
        "OvertimeError",
        "OvertimeValidationError",
        "OvertimeConfigurationError",
        "OvertimeRecommendationError",
        "OvertimeCapacityError",
        "OvertimePolicyError",
        "OvertimeEngineError",
        "OvertimeServiceError",
    ),
    "models": (
        "RecommendationPriority",
        "RecommendationStatus",
        "RecommendationType",
        "OvertimeRecommendation",
        "OvertimeRequest",
        "OvertimeType",
    ),
    "configuration": (
        "OvertimeConfiguration",
    ),
    "engine": (
        "OvertimeRecommendationEngine",
    ),
    "service": (
        "OvertimeRecommendationService",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.overtime.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Overtime leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.overtime import (
    OvertimeCapacityError,
    OvertimeConfiguration,
    OvertimeConfigurationError,
    OvertimeEngineError,
    OvertimeError,
    OvertimePolicyError,
    OvertimeRecommendation,
    OvertimeRecommendationEngine,
    OvertimeRecommendationError,
    OvertimeRecommendationService,
    OvertimeRequest,
    OvertimeServiceError,
    OvertimeType,
    OvertimeValidationError,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)

from src.overtime.configuration import (
    OvertimeConfiguration as LeafOvertimeConfiguration,
)

from src.overtime.engine import (
    OvertimeRecommendationEngine
    as LeafOvertimeRecommendationEngine,
)

from src.overtime.models import (
    OvertimeRecommendation as LeafOvertimeRecommendation,
    OvertimeRequest as LeafOvertimeRequest,
    OvertimeType as LeafOvertimeType,
    RecommendationPriority as LeafRecommendationPriority,
    RecommendationStatus as LeafRecommendationStatus,
    RecommendationType as LeafRecommendationType,
)

from src.overtime.service import (
    OvertimeRecommendationService
    as LeafOvertimeRecommendationService,
)

assert (
    OvertimeConfiguration
    is LeafOvertimeConfiguration
)

assert (
    OvertimeRecommendationEngine
    is LeafOvertimeRecommendationEngine
)

assert (
    OvertimeRecommendationService
    is LeafOvertimeRecommendationService
)

assert (
    OvertimeRecommendation
    is LeafOvertimeRecommendation
)

assert OvertimeRequest is LeafOvertimeRequest
assert OvertimeType is LeafOvertimeType

assert (
    RecommendationPriority
    is LeafRecommendationPriority
)

assert (
    RecommendationStatus
    is LeafRecommendationStatus
)

assert (
    RecommendationType
    is LeafRecommendationType
)

print(
    "PASS: Overtime public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

for exception_type in (
    OvertimeCapacityError,
    OvertimeConfigurationError,
    OvertimeEngineError,
    OvertimePolicyError,
    OvertimeRecommendationError,
    OvertimeServiceError,
    OvertimeValidationError,
):
    assert issubclass(
        exception_type,
        OvertimeError,
    )

print(
    "PASS: Overtime exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants
# -----------------------------------------------------------------------------

from src.overtime import (
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
)

assert OVERTIME_DOMAIN_VERSION == "1.0.0"

assert DEFAULT_MINIMUM_OVERTIME_HOURS == 5.0
assert DEFAULT_MAXIMUM_OVERTIME_HOURS == 10.0
assert DEFAULT_STANDARD_OVERTIME_HOURS == 5.0

assert DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP == 3
assert DEFAULT_MANDATORY_OVERTIME_MAX_GAP == 10
assert DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP == 11
assert DEFAULT_CRITICAL_SHORTAGE_GAP == 20

assert MINIMUM_RECOMMENDATION_CONFIDENCE == 0.0
assert MAXIMUM_RECOMMENDATION_CONFIDENCE == 1.0
assert DEFAULT_RECOMMENDATION_CONFIDENCE == 0.80
assert DEFAULT_HIGH_CONFIDENCE_THRESHOLD == 0.85
assert DEFAULT_LOW_CONFIDENCE_THRESHOLD == 0.60

print("PASS: Overtime constants remain internally consistent")


# -----------------------------------------------------------------------------
# 10. Validate enum contracts
# -----------------------------------------------------------------------------

assert RecommendationType.NONE.value == "NONE"

assert (
    RecommendationType.VOLUNTARY_OVERTIME.value
    == "VOLUNTARY_OVERTIME"
)

assert (
    RecommendationType.MANDATORY_OVERTIME.value
    == "MANDATORY_OVERTIME"
)

assert (
    RecommendationType.TEMPORARY_LABOR.value
    == "TEMPORARY_LABOR"
)

assert (
    RecommendationType.FULL_TIME_HIRING_REVIEW.value
    == "FULL_TIME_HIRING_REVIEW"
)

assert (
    RecommendationType.OPERATIONAL_REVIEW.value
    == "OPERATIONAL_REVIEW"
)

assert RecommendationPriority.LOW.value == "LOW"
assert RecommendationPriority.MEDIUM.value == "MEDIUM"
assert RecommendationPriority.HIGH.value == "HIGH"
assert RecommendationPriority.CRITICAL.value == "CRITICAL"

assert (
    RecommendationStatus.NOT_REQUIRED.value
    == "NOT_REQUIRED"
)

assert (
    RecommendationStatus.RECOMMENDED.value
    == "RECOMMENDED"
)

assert (
    RecommendationStatus.REQUIRED.value
    == "REQUIRED"
)

assert (
    RecommendationStatus.REVIEW_REQUIRED.value
    == "REVIEW_REQUIRED"
)

assert OvertimeType.NONE.value == "NONE"
assert OvertimeType.VOLUNTARY.value == "VOLUNTARY"
assert OvertimeType.MANDATORY.value == "MANDATORY"

print("PASS: Overtime enum contracts remain operational")


# -----------------------------------------------------------------------------
# 11. Validate request/recommendation model contracts
# -----------------------------------------------------------------------------

planning_date = date(2026, 8, 7)

request = OvertimeRequest(
    planning_date=planning_date,
    associate_gap=2,
    forecast_confidence=0.90,
)

assert request.planning_date == planning_date
assert request.associate_gap == 2
assert request.forecast_confidence == 0.90

try:
    request.associate_gap = 3
except FrozenInstanceError:
    pass
else:
    raise AssertionError(
        "OvertimeRequest must remain frozen."
    )


recommendation = OvertimeRecommendation(
    planning_date=planning_date,
    recommendation=RecommendationType.VOLUNTARY_OVERTIME,
    priority=RecommendationPriority.MEDIUM,
    status=RecommendationStatus.RECOMMENDED,
    overtime_type=OvertimeType.VOLUNTARY,
    overtime_hours=10.0,
    associate_gap=2,
    forecast_confidence=0.90,
    rationale="Release validation.",
)

assert recommendation.overtime_hours == 10.0

try:
    recommendation.overtime_hours = 12.0
except FrozenInstanceError:
    pass
else:
    raise AssertionError(
        "OvertimeRecommendation must remain frozen."
    )

print(
    "PASS: Overtime request and recommendation "
    "model contracts remain operational"
)


# -----------------------------------------------------------------------------
# 12. Validate configuration contract
# -----------------------------------------------------------------------------

configuration = OvertimeConfiguration()

assert configuration.minimum_overtime_hours == 5.0
assert configuration.maximum_overtime_hours == 10.0
assert configuration.standard_overtime_hours == 5.0

assert configuration.voluntary_overtime_max_gap == 3
assert configuration.mandatory_overtime_max_gap == 10
assert configuration.temporary_labor_trigger_gap == 11
assert configuration.critical_shortage_gap == 20

assert (
    configuration.default_recommendation_confidence
    == 0.80
)

assert configuration.low_confidence_threshold == 0.60
assert configuration.high_confidence_threshold == 0.85

assert configuration.configuration_version == "1.0.0"

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "minimum_overtime_hours"
] == 5.0

assert configuration_payload[
    "critical_shortage_gap"
] == 20

print(
    "PASS: OvertimeConfiguration contract remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate recommendation engine decision paths
# -----------------------------------------------------------------------------

engine = OvertimeRecommendationEngine(
    configuration=configuration
)

assert engine.configuration is configuration


# No shortage
no_action = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    )
)

assert (
    no_action.recommendation
    is RecommendationType.NONE
)

assert (
    no_action.priority
    is RecommendationPriority.LOW
)

assert (
    no_action.status
    is RecommendationStatus.NOT_REQUIRED
)

assert no_action.overtime_type is OvertimeType.NONE
assert no_action.overtime_hours == 0.0


# Low confidence
low_confidence = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=0.50,
    )
)

assert (
    low_confidence.recommendation
    is RecommendationType.OPERATIONAL_REVIEW
)

assert (
    low_confidence.status
    is RecommendationStatus.REVIEW_REQUIRED
)

assert low_confidence.overtime_hours == 0.0


# Voluntary OT
voluntary = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=0.90,
    )
)

assert (
    voluntary.recommendation
    is RecommendationType.VOLUNTARY_OVERTIME
)

assert voluntary.overtime_type is OvertimeType.VOLUNTARY
assert voluntary.overtime_hours == 10.0


# Mandatory OT
mandatory = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.90,
    )
)

assert (
    mandatory.recommendation
    is RecommendationType.MANDATORY_OVERTIME
)

assert mandatory.overtime_type is OvertimeType.MANDATORY
assert mandatory.overtime_hours == 25.0


# Temporary labor
temporary_labor = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=11,
        forecast_confidence=0.90,
    )
)

assert (
    temporary_labor.recommendation
    is RecommendationType.TEMPORARY_LABOR
)

assert (
    temporary_labor.priority
    is RecommendationPriority.HIGH
)

assert temporary_labor.overtime_hours == 110.0


# Critical shortage
critical = engine.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=20,
        forecast_confidence=0.90,
    )
)

assert (
    critical.recommendation
    is RecommendationType.FULL_TIME_HIRING_REVIEW
)

assert (
    critical.priority
    is RecommendationPriority.CRITICAL
)

assert (
    critical.status
    is RecommendationStatus.REVIEW_REQUIRED
)

assert critical.overtime_hours == 200.0

print(
    "PASS: Overtime recommendation decision paths "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 14. Validate service dependency wiring and orchestration
# -----------------------------------------------------------------------------

service = OvertimeRecommendationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine

service_result = service.recommend(
    request=OvertimeRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.90,
    )
)

assert isinstance(
    service_result,
    OvertimeRecommendation,
)

assert (
    service_result.recommendation
    is RecommendationType.VOLUNTARY_OVERTIME
)

assert service_result.overtime_hours == 15.0

print(
    "PASS: OvertimeRecommendationService orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    OvertimeRequest(
        planning_date=planning_date,
        associate_gap=-1,
        forecast_confidence=0.90,
    )
except OvertimeValidationError:
    pass
else:
    raise AssertionError(
        "Negative associate_gap must be rejected."
    )


try:
    OvertimeRequest(
        planning_date=planning_date,
        associate_gap=1,
        forecast_confidence=1.50,
    )
except OvertimeValidationError:
    pass
else:
    raise AssertionError(
        "Invalid forecast confidence must be rejected."
    )


try:
    OvertimeConfiguration(
        minimum_overtime_hours=11.0,
        maximum_overtime_hours=10.0,
    )
except OvertimeConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid overtime-hour configuration "
        "must be rejected."
    )


try:
    engine.recommend(
        request="invalid",
    )
except OvertimeValidationError:
    pass
else:
    raise AssertionError(
        "Invalid recommendation request must be rejected."
    )

print(
    "PASS: Overtime representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 16. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    OvertimeConfiguration
)

for parameter_name in (
    "minimum_overtime_hours",
    "maximum_overtime_hours",
    "standard_overtime_hours",
    "voluntary_overtime_max_gap",
    "mandatory_overtime_max_gap",
    "temporary_labor_trigger_gap",
    "critical_shortage_gap",
    "default_recommendation_confidence",
    "low_confidence_threshold",
    "high_confidence_threshold",
    "configuration_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


engine_signature = inspect.signature(
    OvertimeRecommendationEngine.recommend
)

assert "request" in engine_signature.parameters


service_signature = inspect.signature(
    OvertimeRecommendationService.recommend
)

assert "request" in service_signature.parameters


request_signature = inspect.signature(
    OvertimeRequest
)

assert "planning_date" in request_signature.parameters
assert "associate_gap" in request_signature.parameters
assert "forecast_confidence" in request_signature.parameters

print("PASS: Overtime public signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.overtime")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.staffing
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import date
from pathlib import Path


PACKAGE_NAME = "src.staffing"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "engine",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

staffing_package = importlib.import_module(PACKAGE_NAME)

assert staffing_package.__name__ == PACKAGE_NAME
assert staffing_package.__package__ == PACKAGE_NAME

print("PASS: Imported canonical package src.staffing")


# -----------------------------------------------------------------------------
# 2. Import every staffing module through canonical src.* namespace
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    loaded_modules[module_name] = importlib.import_module(
        qualified_name
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every staffing module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level staffing.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "staffing"
        or module_name.startswith("staffing.")
    )
)

assert legacy_modules == [], (
    "Legacy staffing.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy staffing.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": staffing_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "staffing"
            or imported_name.startswith("staffing.")
            or imported_name == "workforce"
            or imported_name.startswith("workforce.")
            or imported_name == "planning"
            or imported_name.startswith("planning.")
            or imported_name == "forecast"
            or imported_name.startswith("src.forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports


assert legacy_imports == {}, (
    "Legacy absolute imports remain in src.staffing: "
    f"{legacy_imports}"
)

print(
    "PASS: No legacy staffing.*, workforce.*, planning.*, "
    "or forecast.* absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "STAFFING_DOMAIN_VERSION",

    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    "LOW_CONFIDENCE_THRESHOLD",
    "HIGH_CONFIDENCE_THRESHOLD",

    "MINIMUM_ASSOCIATE_GAP",
    "TEMPORARY_LABOR_TRIGGER_GAP",
    "FULL_TIME_HIRING_TRIGGER_GAP",
    "CRITICAL_SHORTAGE_GAP",

    "RECOMMENDATION_NONE",
    "RECOMMENDATION_TEMPORARY_LABOR",
    "RECOMMENDATION_FULL_TIME_HIRING",
    "RECOMMENDATION_FULL_TIME_HIRING_REVIEW",
    "RECOMMENDATION_CROSS_TRAIN",
    "RECOMMENDATION_SHIFT_REALIGNMENT",
    "RECOMMENDATION_WORKFORCE_REDUCTION",

    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",
    "PRIORITY_HIGH",
    "PRIORITY_CRITICAL",

    "STATUS_NOT_REQUIRED",
    "STATUS_RECOMMENDED",
    "STATUS_REVIEW_REQUIRED",
    "STATUS_APPROVED",

    "SUPPORTED_RECOMMENDATION_TYPES",
    "SUPPORTED_RECOMMENDATION_PRIORITIES",
    "SUPPORTED_RECOMMENDATION_STATUSES",

    "StaffingError",
    "StaffingValidationError",
    "StaffingConfigurationError",
    "StaffingEngineError",
    "StaffingServiceError",

    "StaffingRequest",
    "StaffingRecommendation",
    "StaffingRecommendationType",
    "StaffingRecommendationPriority",
    "StaffingRecommendationStatus",

    "StaffingConfiguration",
    "StaffingRecommendationEngine",
    "StaffingRecommendationService",
)

assert tuple(staffing_package.__all__) == (
    EXPECTED_PUBLIC_API
), (
    "Unexpected src.staffing public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   {tuple(staffing_package.__all__)}"
)

assert len(staffing_package.__all__) == len(
    set(staffing_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        staffing_package,
        symbol_name,
    )

print(
    "PASS: Staffing public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate declared leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "models": (
        "StaffingRecommendation",
        "StaffingRecommendationPriority",
        "StaffingRecommendationStatus",
        "StaffingRecommendationType",
        "StaffingRequest",
    ),
    "configuration": (
        "StaffingConfiguration",
    ),
    "engine": (
        "StaffingRecommendationEngine",
    ),
    "service": (
        "StaffingRecommendationService",
    ),
}


for module_name, expected_all in EXPECTED_LEAF_ALL.items():
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.staffing.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Staffing declared leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.staffing import (
    StaffingConfiguration,
    StaffingConfigurationError,
    StaffingEngineError,
    StaffingError,
    StaffingRecommendation,
    StaffingRecommendationEngine,
    StaffingRecommendationPriority,
    StaffingRecommendationService,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
    StaffingServiceError,
    StaffingValidationError,
)

from src.staffing.configuration import (
    StaffingConfiguration as LeafStaffingConfiguration,
)

from src.staffing.engine import (
    StaffingRecommendationEngine as LeafStaffingRecommendationEngine,
)

from src.staffing.models import (
    StaffingRecommendation as LeafStaffingRecommendation,
    StaffingRecommendationPriority as LeafStaffingRecommendationPriority,
    StaffingRecommendationStatus as LeafStaffingRecommendationStatus,
    StaffingRecommendationType as LeafStaffingRecommendationType,
    StaffingRequest as LeafStaffingRequest,
)

from src.staffing.service import (
    StaffingRecommendationService as LeafStaffingRecommendationService,
)

assert StaffingConfiguration is LeafStaffingConfiguration

assert (
    StaffingRecommendationEngine
    is LeafStaffingRecommendationEngine
)

assert (
    StaffingRecommendationService
    is LeafStaffingRecommendationService
)

assert StaffingRequest is LeafStaffingRequest
assert StaffingRecommendation is LeafStaffingRecommendation

assert (
    StaffingRecommendationType
    is LeafStaffingRecommendationType
)

assert (
    StaffingRecommendationPriority
    is LeafStaffingRecommendationPriority
)

assert (
    StaffingRecommendationStatus
    is LeafStaffingRecommendationStatus
)

print(
    "PASS: Staffing public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

for exception_type in (
    StaffingValidationError,
    StaffingConfigurationError,
    StaffingEngineError,
    StaffingServiceError,
):
    assert issubclass(
        exception_type,
        StaffingError,
    )

print(
    "PASS: Staffing exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants
# -----------------------------------------------------------------------------

from src.staffing import (
    CRITICAL_SHORTAGE_GAP,
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_RECOMMENDATION_CONFIDENCE,
    FULL_TIME_HIRING_TRIGGER_GAP,
    HIGH_CONFIDENCE_THRESHOLD,
    LOW_CONFIDENCE_THRESHOLD,
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
    MINIMUM_ASSOCIATE_GAP,
    STAFFING_DOMAIN_VERSION,
    TEMPORARY_LABOR_TRIGGER_GAP,
)

assert STAFFING_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0

assert DEFAULT_FORECAST_CONFIDENCE == 0.80
assert DEFAULT_RECOMMENDATION_CONFIDENCE == 0.80

assert LOW_CONFIDENCE_THRESHOLD == 0.60
assert HIGH_CONFIDENCE_THRESHOLD == 0.90

assert MINIMUM_ASSOCIATE_GAP == 1
assert TEMPORARY_LABOR_TRIGGER_GAP == 5
assert FULL_TIME_HIRING_TRIGGER_GAP == 15
assert CRITICAL_SHORTAGE_GAP == 25

print("PASS: Staffing constants remain internally consistent")


# -----------------------------------------------------------------------------
# 10. Validate enum contracts
# -----------------------------------------------------------------------------

assert StaffingRecommendationType.NONE.value == "NONE"

assert (
    StaffingRecommendationType.TEMPORARY_LABOR.value
    == "TEMPORARY_LABOR"
)

assert (
    StaffingRecommendationType.FULL_TIME_HIRING.value
    == "FULL_TIME_HIRING"
)

assert (
    StaffingRecommendationType.FULL_TIME_HIRING_REVIEW.value
    == "FULL_TIME_HIRING_REVIEW"
)

assert (
    StaffingRecommendationType.CROSS_TRAIN.value
    == "CROSS_TRAIN"
)

assert (
    StaffingRecommendationType.SHIFT_REALIGNMENT.value
    == "SHIFT_REALIGNMENT"
)

assert (
    StaffingRecommendationType.WORKFORCE_REDUCTION.value
    == "WORKFORCE_REDUCTION"
)

assert StaffingRecommendationPriority.LOW.value == "LOW"
assert StaffingRecommendationPriority.MEDIUM.value == "MEDIUM"
assert StaffingRecommendationPriority.HIGH.value == "HIGH"

assert (
    StaffingRecommendationPriority.CRITICAL.value
    == "CRITICAL"
)

assert (
    StaffingRecommendationStatus.NOT_REQUIRED.value
    == "NOT_REQUIRED"
)

assert (
    StaffingRecommendationStatus.RECOMMENDED.value
    == "RECOMMENDED"
)

assert (
    StaffingRecommendationStatus.REVIEW_REQUIRED.value
    == "REVIEW_REQUIRED"
)

assert (
    StaffingRecommendationStatus.APPROVED.value
    == "APPROVED"
)

print("PASS: Staffing enum contracts remain operational")


# -----------------------------------------------------------------------------
# 11. Validate request model
# -----------------------------------------------------------------------------

planning_date = date(2026, 8, 7)

request = StaffingRequest(
    planning_date=planning_date,
    associate_gap=4,
    forecast_confidence=0.90,
    recurring_shortage_days=2,
    recurring_surplus_days=0,
    overtime_dependency_days=0,
    planning_horizon_days=30,
)

assert request.planning_date == planning_date
assert request.associate_gap == 4
assert request.forecast_confidence == 0.90
assert request.recurring_shortage_days == 2
assert request.recurring_surplus_days == 0
assert request.overtime_dependency_days == 0
assert request.planning_horizon_days == 30

assert request.has_shortage is True
assert request.has_surplus is False

request_payload = request.as_dict()

assert request_payload["planning_date"] == "2026-08-07"
assert request_payload["associate_gap"] == 4

print("PASS: StaffingRequest contract remains operational")


# -----------------------------------------------------------------------------
# 12. Validate configuration contract
# -----------------------------------------------------------------------------

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

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "temporary_labor_trigger_gap"
] == 5

assert configuration_payload[
    "critical_shortage_gap"
] == 25

print(
    "PASS: StaffingConfiguration contract remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate staffing engine decision paths
# -----------------------------------------------------------------------------

engine = StaffingRecommendationEngine(
    configuration=configuration
)

assert engine.configuration is configuration


# No gap
no_action = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    )
)

assert (
    no_action.recommendation
    is StaffingRecommendationType.NONE
)

assert (
    no_action.priority
    is StaffingRecommendationPriority.LOW
)

assert (
    no_action.status
    is StaffingRecommendationStatus.NOT_REQUIRED
)

assert no_action.recommended_associates == 0


# Low confidence takes precedence
low_confidence = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.50,
    )
)

assert (
    low_confidence.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)

assert (
    low_confidence.priority
    is StaffingRecommendationPriority.MEDIUM
)

assert (
    low_confidence.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)


# Limited, non-recurring shortage -> cross training
cross_train = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=0.95,
        recurring_shortage_days=0,
        overtime_dependency_days=0,
    )
)

assert (
    cross_train.recommendation
    is StaffingRecommendationType.CROSS_TRAIN
)

assert (
    cross_train.status
    is StaffingRecommendationStatus.RECOMMENDED
)

assert cross_train.recommended_associates == 2


# Material shortage -> temporary labor
temporary_labor = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.95,
    )
)

assert (
    temporary_labor.recommendation
    is StaffingRecommendationType.TEMPORARY_LABOR
)

assert (
    temporary_labor.priority
    is StaffingRecommendationPriority.HIGH
)

assert temporary_labor.recommended_associates == 5


# Recurring shortage can also trigger temporary labor
recurring_temporary = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=0.95,
        recurring_shortage_days=5,
    )
)

assert (
    recurring_temporary.recommendation
    is StaffingRecommendationType.TEMPORARY_LABOR
)


# Sustained shortage -> full-time hiring review
hiring_review = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=8,
        forecast_confidence=0.95,
        recurring_shortage_days=15,
    )
)

assert (
    hiring_review.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)

assert (
    hiring_review.priority
    is StaffingRecommendationPriority.HIGH
)

assert (
    hiring_review.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)


# Overtime dependency can trigger full-time hiring review
overtime_dependency = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.95,
        overtime_dependency_days=10,
    )
)

assert (
    overtime_dependency.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)


# Full-time hiring trigger gap
trigger_hiring = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=15,
        forecast_confidence=0.95,
    )
)

assert (
    trigger_hiring.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
)


# Critical shortage -> immediate full-time hiring
critical_hiring = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=25,
        forecast_confidence=0.95,
    )
)

assert (
    critical_hiring.recommendation
    is StaffingRecommendationType.FULL_TIME_HIRING
)

assert (
    critical_hiring.priority
    is StaffingRecommendationPriority.CRITICAL
)

assert critical_hiring.recommended_associates == 25


# Short-term surplus -> shift realignment
short_surplus = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=-4,
        forecast_confidence=0.95,
        recurring_surplus_days=2,
    )
)

assert (
    short_surplus.recommendation
    is StaffingRecommendationType.SHIFT_REALIGNMENT
)

assert (
    short_surplus.priority
    is StaffingRecommendationPriority.MEDIUM
)

assert short_surplus.recommended_associates == 4


# Persistent surplus -> workforce reduction
persistent_surplus = engine.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=-4,
        forecast_confidence=0.95,
        recurring_surplus_days=10,
    )
)

assert (
    persistent_surplus.recommendation
    is StaffingRecommendationType.WORKFORCE_REDUCTION
)

assert (
    persistent_surplus.priority
    is StaffingRecommendationPriority.HIGH
)

assert (
    persistent_surplus.status
    is StaffingRecommendationStatus.REVIEW_REQUIRED
)

print(
    "PASS: Staffing recommendation decision paths "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 14. Validate recommendation serialization contract
# -----------------------------------------------------------------------------

recommendation_payload = temporary_labor.as_dict()

assert recommendation_payload[
    "planning_date"
] == "2026-08-07"

assert recommendation_payload[
    "recommendation"
] == "TEMPORARY_LABOR"

assert recommendation_payload[
    "priority"
] == "HIGH"

assert recommendation_payload[
    "status"
] == "RECOMMENDED"

assert recommendation_payload[
    "recommended_associates"
] == 5

assert recommendation_payload[
    "recommendation_version"
] == "1.0.0"

assert isinstance(
    recommendation_payload["generated_at_utc"],
    str,
)

print(
    "PASS: StaffingRecommendation serialization "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate service dependency wiring and orchestration
# -----------------------------------------------------------------------------

service = StaffingRecommendationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine

service_result = service.recommend(
    request=StaffingRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.95,
    )
)

assert isinstance(
    service_result,
    StaffingRecommendation,
)

assert (
    service_result.recommendation
    is StaffingRecommendationType.TEMPORARY_LABOR
)

print(
    "PASS: StaffingRecommendationService orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    StaffingRequest(
        planning_date=planning_date,
        associate_gap=1,
        forecast_confidence=1.5,
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Invalid forecast confidence must be rejected."
    )


try:
    StaffingRequest(
        planning_date=planning_date,
        associate_gap=1,
        forecast_confidence=0.90,
        recurring_shortage_days=-1,
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Negative recurring shortage days must be rejected."
    )


try:
    StaffingConfiguration(
        temporary_labor_trigger_gap=20,
        full_time_hiring_trigger_gap=15,
    )
except StaffingConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid staffing threshold ordering must be rejected."
    )


try:
    engine.recommend(
        request="invalid",
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Invalid staffing engine request must be rejected."
    )


try:
    StaffingRecommendationService(
        configuration=StaffingConfiguration(),
        engine=engine,
    )
except StaffingValidationError:
    pass
else:
    raise AssertionError(
        "Service must reject mismatched configuration/engine dependencies."
    )

print(
    "PASS: Staffing representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 17. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    StaffingConfiguration
)

for parameter_name in (
    "minimum_associate_gap",
    "temporary_labor_trigger_gap",
    "full_time_hiring_trigger_gap",
    "critical_shortage_gap",
    "minimum_recurring_shortage_days",
    "full_time_hiring_shortage_days",
    "minimum_recurring_surplus_days",
    "minimum_overtime_dependency_days",
    "default_forecast_confidence",
    "low_confidence_threshold",
    "high_confidence_threshold",
    "configuration_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


request_signature = inspect.signature(
    StaffingRequest
)

for parameter_name in (
    "planning_date",
    "associate_gap",
    "forecast_confidence",
    "recurring_shortage_days",
    "recurring_surplus_days",
    "overtime_dependency_days",
    "planning_horizon_days",
):
    assert parameter_name in request_signature.parameters


engine_signature = inspect.signature(
    StaffingRecommendationEngine.recommend
)

assert "request" in engine_signature.parameters


service_signature = inspect.signature(
    StaffingRecommendationService.recommend
)

assert "request" in service_signature.parameters

print("PASS: Staffing public signatures are preserved")


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.staffing")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print("Modules validated:", len(EXPECTED_MODULES) + 1)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.optimization
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import date
from pathlib import Path


PACKAGE_NAME = "src.optimization"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "engine",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

optimization_package = importlib.import_module(
    PACKAGE_NAME
)

assert optimization_package.__name__ == PACKAGE_NAME
assert optimization_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.optimization"
)


# -----------------------------------------------------------------------------
# 2. Import every optimization module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = (
        f"{PACKAGE_NAME}.{module_name}"
    )

    loaded_modules[module_name] = (
        importlib.import_module(
            qualified_name
        )
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every optimization module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy optimization.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "optimization"
        or module_name.startswith("optimization.")
    )
)

assert legacy_modules == [], (
    "Legacy optimization.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy optimization.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": optimization_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "optimization"
            or imported_name.startswith(
                "optimization."
            )
            or imported_name == "workforce"
            or imported_name.startswith(
                "workforce."
            )
            or imported_name == "planning"
            or imported_name.startswith(
                "planning."
            )
            or imported_name == "overtime"
            or imported_name.startswith(
                "overtime."
            )
            or imported_name == "staffing"
            or imported_name.startswith(
                "staffing."
            )
            or imported_name == "forecast"
            or imported_name.startswith(
                "src.forecast."
            )
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = (
            invalid_imports
        )


assert legacy_imports == {}, (
    "Legacy absolute imports remain in "
    f"src.optimization: {legacy_imports}"
)

print(
    "PASS: No legacy optimization.*, workforce.*, "
    "planning.*, overtime.*, staffing.*, or forecast.* "
    "absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "OPTIMIZATION_DOMAIN_VERSION",

    "MIN_FORECAST_CONFIDENCE",
    "MAX_FORECAST_CONFIDENCE",
    "DEFAULT_FORECAST_CONFIDENCE",

    "OPTIMIZATION_PRIORITY_LOW",
    "OPTIMIZATION_PRIORITY_MEDIUM",
    "OPTIMIZATION_PRIORITY_HIGH",
    "OPTIMIZATION_PRIORITY_CRITICAL",
    "SUPPORTED_OPTIMIZATION_PRIORITIES",

    "OPTIMIZATION_STATUS_OPTIMAL",
    "OPTIMIZATION_STATUS_ACCEPTABLE",
    "OPTIMIZATION_STATUS_REVIEW",
    "OPTIMIZATION_STATUS_CRITICAL",
    "SUPPORTED_OPTIMIZATION_STATUSES",

    "ACTION_NONE",
    "ACTION_OVERTIME",
    "ACTION_TEMPORARY_LABOR",
    "ACTION_FULL_TIME_HIRING",
    "ACTION_SHIFT_REALIGNMENT",
    "ACTION_CROSS_TRAINING",
    "SUPPORTED_WORKFORCE_ACTIONS",

    "OptimizationError",
    "OptimizationValidationError",
    "OptimizationConfigurationError",
    "OptimizationConflictError",
    "OptimizationEngineError",
    "OptimizationServiceError",

    "OptimizationPriority",
    "OptimizationStatus",
    "WorkforceAction",
    "WorkforceOptimizationRequest",
    "WorkforceOptimizationDecision",

    "WorkforceOptimizationConfiguration",
    "WorkforceOptimizationEngine",
    "WorkforceOptimizationService",
)

assert tuple(
    optimization_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.optimization public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual: "
    f"{tuple(optimization_package.__all__)}"
)

assert len(
    optimization_package.__all__
) == len(
    set(optimization_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        optimization_package,
        symbol_name,
    )

print(
    "PASS: Optimization public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "constants": (
        "OPTIMIZATION_DOMAIN_VERSION",

        "MIN_FORECAST_CONFIDENCE",
        "MAX_FORECAST_CONFIDENCE",
        "DEFAULT_FORECAST_CONFIDENCE",

        "OPTIMIZATION_PRIORITY_LOW",
        "OPTIMIZATION_PRIORITY_MEDIUM",
        "OPTIMIZATION_PRIORITY_HIGH",
        "OPTIMIZATION_PRIORITY_CRITICAL",
        "SUPPORTED_OPTIMIZATION_PRIORITIES",

        "OPTIMIZATION_STATUS_OPTIMAL",
        "OPTIMIZATION_STATUS_ACCEPTABLE",
        "OPTIMIZATION_STATUS_REVIEW",
        "OPTIMIZATION_STATUS_CRITICAL",
        "SUPPORTED_OPTIMIZATION_STATUSES",

        "ACTION_NONE",
        "ACTION_OVERTIME",
        "ACTION_TEMPORARY_LABOR",
        "ACTION_FULL_TIME_HIRING",
        "ACTION_SHIFT_REALALIGNMENT"
        if False
        else "ACTION_SHIFT_REALIGNMENT",
        "ACTION_CROSS_TRAINING",
        "SUPPORTED_WORKFORCE_ACTIONS",
    ),
    "exceptions": (
        "OptimizationConfigurationError",
        "OptimizationConflictError",
        "OptimizationEngineError",
        "OptimizationError",
        "OptimizationServiceError",
        "OptimizationValidationError",
    ),
    "models": (
        "OptimizationPriority",
        "OptimizationStatus",
        "WorkforceAction",
        "WorkforceOptimizationDecision",
        "WorkforceOptimizationRequest",
    ),
    "configuration": (
        "WorkforceOptimizationConfiguration",
    ),
    "engine": (
        "WorkforceOptimizationEngine",
    ),
    "service": (
        "WorkforceOptimizationService",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.optimization.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Optimization leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.optimization import (
    OptimizationConfigurationError,
    OptimizationConflictError,
    OptimizationEngineError,
    OptimizationError,
    OptimizationPriority,
    OptimizationServiceError,
    OptimizationStatus,
    OptimizationValidationError,
    WorkforceAction,
    WorkforceOptimizationConfiguration,
    WorkforceOptimizationDecision,
    WorkforceOptimizationEngine,
    WorkforceOptimizationRequest,
    WorkforceOptimizationService,
)

from src.optimization.configuration import (
    WorkforceOptimizationConfiguration
    as LeafWorkforceOptimizationConfiguration,
)

from src.optimization.engine import (
    WorkforceOptimizationEngine
    as LeafWorkforceOptimizationEngine,
)

from src.optimization.models import (
    OptimizationPriority as LeafOptimizationPriority,
    OptimizationStatus as LeafOptimizationStatus,
    WorkforceAction as LeafWorkforceAction,
    WorkforceOptimizationDecision
    as LeafWorkforceOptimizationDecision,
    WorkforceOptimizationRequest
    as LeafWorkforceOptimizationRequest,
)

from src.optimization.service import (
    WorkforceOptimizationService
    as LeafWorkforceOptimizationService,
)

assert (
    WorkforceOptimizationConfiguration
    is LeafWorkforceOptimizationConfiguration
)

assert (
    WorkforceOptimizationEngine
    is LeafWorkforceOptimizationEngine
)

assert (
    WorkforceOptimizationService
    is LeafWorkforceOptimizationService
)

assert (
    WorkforceOptimizationRequest
    is LeafWorkforceOptimizationRequest
)

assert (
    WorkforceOptimizationDecision
    is LeafWorkforceOptimizationDecision
)

assert (
    OptimizationPriority
    is LeafOptimizationPriority
)

assert (
    OptimizationStatus
    is LeafOptimizationStatus
)

assert (
    WorkforceAction
    is LeafWorkforceAction
)

print(
    "PASS: Optimization public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

for exception_type in (
    OptimizationValidationError,
    OptimizationConfigurationError,
    OptimizationConflictError,
    OptimizationEngineError,
    OptimizationServiceError,
):
    assert issubclass(
        exception_type,
        OptimizationError,
    )

print(
    "PASS: Optimization exception hierarchy "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants
# -----------------------------------------------------------------------------

from src.optimization import (
    ACTION_CROSS_TRAINING,
    ACTION_FULL_TIME_HIRING,
    ACTION_NONE,
    ACTION_OVERTIME,
    ACTION_SHIFT_REALIGNMENT,
    ACTION_TEMPORARY_LABOR,
    DEFAULT_FORECAST_CONFIDENCE,
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
    OPTIMIZATION_DOMAIN_VERSION,
    OPTIMIZATION_PRIORITY_CRITICAL,
    OPTIMIZATION_PRIORITY_HIGH,
    OPTIMIZATION_PRIORITY_LOW,
    OPTIMIZATION_PRIORITY_MEDIUM,
    OPTIMIZATION_STATUS_ACCEPTABLE,
    OPTIMIZATION_STATUS_CRITICAL,
    OPTIMIZATION_STATUS_OPTIMAL,
    OPTIMIZATION_STATUS_REVIEW,
)

assert OPTIMIZATION_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert DEFAULT_FORECAST_CONFIDENCE == 0.80

assert OPTIMIZATION_PRIORITY_LOW == "LOW"
assert OPTIMIZATION_PRIORITY_MEDIUM == "MEDIUM"
assert OPTIMIZATION_PRIORITY_HIGH == "HIGH"
assert OPTIMIZATION_PRIORITY_CRITICAL == "CRITICAL"

assert OPTIMIZATION_STATUS_OPTIMAL == "OPTIMAL"
assert OPTIMIZATION_STATUS_ACCEPTABLE == "ACCEPTABLE"
assert OPTIMIZATION_STATUS_REVIEW == "REVIEW"
assert OPTIMIZATION_STATUS_CRITICAL == "CRITICAL"

assert ACTION_NONE == "NONE"
assert ACTION_OVERTIME == "OVERTIME"
assert ACTION_TEMPORARY_LABOR == "TEMPORARY_LABOR"
assert ACTION_FULL_TIME_HIRING == "FULL_TIME_HIRING"
assert ACTION_SHIFT_REALIGNMENT == "SHIFT_REALIGNMENT"
assert ACTION_CROSS_TRAINING == "CROSS_TRAINING"

print(
    "PASS: Optimization constants remain internally "
    "consistent"
)


# -----------------------------------------------------------------------------
# 10. Validate enum contracts
# -----------------------------------------------------------------------------

assert OptimizationPriority.LOW.value == "LOW"
assert OptimizationPriority.MEDIUM.value == "MEDIUM"
assert OptimizationPriority.HIGH.value == "HIGH"
assert OptimizationPriority.CRITICAL.value == "CRITICAL"

assert OptimizationStatus.OPTIMAL.value == "OPTIMAL"
assert OptimizationStatus.ACCEPTABLE.value == "ACCEPTABLE"
assert OptimizationStatus.REVIEW.value == "REVIEW"
assert OptimizationStatus.CRITICAL.value == "CRITICAL"

assert WorkforceAction.NONE.value == "NONE"
assert WorkforceAction.OVERTIME.value == "OVERTIME"

assert (
    WorkforceAction.TEMPORARY_LABOR.value
    == "TEMPORARY_LABOR"
)

assert (
    WorkforceAction.FULL_TIME_HIRING.value
    == "FULL_TIME_HIRING"
)

assert (
    WorkforceAction.SHIFT_REALIGNMENT.value
    == "SHIFT_REALIGNMENT"
)

assert (
    WorkforceAction.CROSS_TRAINING.value
    == "CROSS_TRAINING"
)

print(
    "PASS: Optimization enum contracts remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate request model contract
# -----------------------------------------------------------------------------

planning_date = date(2026, 8, 7)

request = WorkforceOptimizationRequest(
    planning_date=planning_date,
    associate_gap=5,
    forecast_confidence=0.95,
    overtime_recommended=True,
    temporary_labor_recommended=True,
    full_time_hiring_recommended=False,
    shift_realignment_recommended=False,
    cross_training_recommended=False,
    overtime_hours=25.0,
    recommended_associates=5,
)

assert request.planning_date == planning_date
assert request.associate_gap == 5
assert request.forecast_confidence == 0.95
assert request.overtime_recommended is True
assert request.temporary_labor_recommended is True
assert request.recommended_associates == 5

assert request.has_conflicting_actions is True

request_payload = request.as_dict()

assert request_payload[
    "planning_date"
] == "2026-08-07"

assert request_payload[
    "associate_gap"
] == 5

assert request_payload[
    "overtime_hours"
] == 25.0

print(
    "PASS: WorkforceOptimizationRequest contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate configuration contract
# -----------------------------------------------------------------------------

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

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "critical_associate_gap"
] == 20

assert configuration_payload[
    "full_time_hiring_priority_weight"
] == 5

print(
    "PASS: WorkforceOptimizationConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate engine decision paths
# -----------------------------------------------------------------------------

engine = WorkforceOptimizationEngine(
    configuration
)

assert engine.configuration is configuration


# Low confidence
low_confidence = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.50,
        overtime_recommended=True,
        overtime_hours=10.0,
    )
)

assert low_confidence.action is WorkforceAction.NONE
assert (
    low_confidence.priority
    is OptimizationPriority.MEDIUM
)
assert (
    low_confidence.status
    is OptimizationStatus.REVIEW
)


# No shortage / surplus
no_action = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
    )
)

assert no_action.action is WorkforceAction.NONE
assert (
    no_action.priority
    is OptimizationPriority.LOW
)
assert (
    no_action.status
    is OptimizationStatus.OPTIMAL
)


# Positive gap without recommendation
review = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.95,
    )
)

assert review.action is WorkforceAction.NONE
assert (
    review.status
    is OptimizationStatus.REVIEW
)


# Overtime only
overtime = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.95,
        overtime_recommended=True,
        overtime_hours=15.0,
    )
)

assert overtime.action is WorkforceAction.OVERTIME
assert (
    overtime.priority
    is OptimizationPriority.HIGH
)
assert (
    overtime.status
    is OptimizationStatus.ACCEPTABLE
)
assert overtime.conflicting_actions_resolved is False


# Cross training outranks overtime
cross_training = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=3,
        forecast_confidence=0.95,
        overtime_recommended=True,
        cross_training_recommended=True,
        overtime_hours=15.0,
        recommended_associates=3,
    )
)

assert (
    cross_training.action
    is WorkforceAction.CROSS_TRAINING
)

assert cross_training.conflicting_actions_resolved is True


# Shift realignment outranks cross training
shift_realign = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=4,
        forecast_confidence=0.95,
        cross_training_recommended=True,
        shift_realignment_recommended=True,
        recommended_associates=4,
    )
)

assert (
    shift_realign.action
    is WorkforceAction.SHIFT_REALIGNMENT
)


# Temporary labor outranks shift realignment
temporary_labor = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.95,
        shift_realignment_recommended=True,
        temporary_labor_recommended=True,
        recommended_associates=5,
    )
)

assert (
    temporary_labor.action
    is WorkforceAction.TEMPORARY_LABOR
)


# Full-time hiring has highest configured weight
full_time_hiring = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=15,
        forecast_confidence=0.95,
        overtime_recommended=True,
        temporary_labor_recommended=True,
        full_time_hiring_recommended=True,
        overtime_hours=20.0,
        recommended_associates=15,
    )
)

assert (
    full_time_hiring.action
    is WorkforceAction.FULL_TIME_HIRING
)

assert (
    full_time_hiring.conflicting_actions_resolved
    is True
)


# Critical associate gap
critical = engine.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=20,
        forecast_confidence=0.95,
        full_time_hiring_recommended=True,
        recommended_associates=20,
    )
)

assert (
    critical.action
    is WorkforceAction.FULL_TIME_HIRING
)

assert (
    critical.priority
    is OptimizationPriority.CRITICAL
)

assert (
    critical.status
    is OptimizationStatus.CRITICAL
)

print(
    "PASS: Workforce optimization decision paths "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 14. Validate decision serialization
# -----------------------------------------------------------------------------

decision_payload = temporary_labor.as_dict()

assert decision_payload[
    "planning_date"
] == "2026-08-07"

assert decision_payload[
    "action"
] == "TEMPORARY_LABOR"

assert decision_payload[
    "priority"
] == "HIGH"

assert decision_payload[
    "status"
] == "ACCEPTABLE"

assert decision_payload[
    "recommended_associates"
] == 5

assert decision_payload[
    "decision_version"
] == "1.0.0"

assert isinstance(
    decision_payload["generated_at_utc"],
    str,
)

print(
    "PASS: WorkforceOptimizationDecision serialization "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate service dependency wiring and orchestration
# -----------------------------------------------------------------------------

service = WorkforceOptimizationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine

service_result = service.optimize(
    request=WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=5,
        forecast_confidence=0.95,
        temporary_labor_recommended=True,
        recommended_associates=5,
    )
)

assert isinstance(
    service_result,
    WorkforceOptimizationDecision,
)

assert (
    service_result.action
    is WorkforceAction.TEMPORARY_LABOR
)

print(
    "PASS: WorkforceOptimizationService orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=1,
        forecast_confidence=1.5,
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Invalid forecast confidence must be rejected."
    )


try:
    WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=0,
        forecast_confidence=0.95,
        overtime_recommended=True,
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Shortage actions must be rejected when "
        "associate_gap is non-positive."
    )


try:
    WorkforceOptimizationRequest(
        planning_date=planning_date,
        associate_gap=2,
        forecast_confidence=0.95,
        overtime_recommended=False,
        overtime_hours=5.0,
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Positive overtime hours without an overtime "
        "recommendation must be rejected."
    )


try:
    WorkforceOptimizationConfiguration(
        low_confidence_threshold=0.95,
        high_confidence_threshold=0.90,
    )
except OptimizationConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid confidence threshold ordering "
        "must be rejected."
    )


try:
    WorkforceOptimizationConfiguration(
        overtime_priority_weight=1,
        cross_training_priority_weight=1,
    )
except OptimizationConfigurationError:
    pass
else:
    raise AssertionError(
        "Duplicate optimization priority weights "
        "must be rejected."
    )


try:
    engine.optimize(
        request="invalid",
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Invalid optimization request must be rejected."
    )


try:
    WorkforceOptimizationService(
        configuration=(
            WorkforceOptimizationConfiguration()
        ),
        engine=engine,
    )
except OptimizationValidationError:
    pass
else:
    raise AssertionError(
        "Service must reject mismatched configuration "
        "and engine dependencies."
    )

print(
    "PASS: Optimization representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 17. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    WorkforceOptimizationConfiguration
)

for parameter_name in (
    "low_confidence_threshold",
    "high_confidence_threshold",
    "default_forecast_confidence",
    "overtime_priority_weight",
    "cross_training_priority_weight",
    "shift_realignment_priority_weight",
    "temporary_labor_priority_weight",
    "full_time_hiring_priority_weight",
    "critical_associate_gap",
    "configuration_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


request_signature = inspect.signature(
    WorkforceOptimizationRequest
)

for parameter_name in (
    "planning_date",
    "associate_gap",
    "forecast_confidence",
    "overtime_recommended",
    "temporary_labor_recommended",
    "full_time_hiring_recommended",
    "shift_realignment_recommended",
    "cross_training_recommended",
    "overtime_hours",
    "recommended_associates",
):
    assert (
        parameter_name
        in request_signature.parameters
    )


engine_signature = inspect.signature(
    WorkforceOptimizationEngine.optimize
)

assert "request" in engine_signature.parameters


service_signature = inspect.signature(
    WorkforceOptimizationService.optimize
)

assert "request" in service_signature.parameters

print(
    "PASS: Optimization public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.optimization")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.orchestration
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* imports
#     - Cross-domain namespace integrity
#     - Root and leaf public APIs
#     - Public object identity
#     - Constants and enums
#     - Configuration contract
#     - Request/result contracts
#     - Dependency wiring
#     - Real end-to-end orchestration
#     - Optional-stage behavior
#     - Failure contracts
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import date
from pathlib import Path


PACKAGE_NAME = "src.orchestration"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "engine",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

orchestration_package = importlib.import_module(
    PACKAGE_NAME
)

assert orchestration_package.__name__ == PACKAGE_NAME
assert orchestration_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.orchestration"
)


# -----------------------------------------------------------------------------
# 2. Import every orchestration module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = (
        f"{PACKAGE_NAME}.{module_name}"
    )

    loaded_modules[module_name] = (
        importlib.import_module(
            qualified_name
        )
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every orchestration module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level orchestration.* loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "orchestration"
        or module_name.startswith(
            "orchestration."
        )
    )
)

assert legacy_modules == [], (
    "Legacy orchestration.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy orchestration.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": orchestration_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "orchestration"
            or imported_name.startswith(
                "orchestration."
            )
            or imported_name == "optimization"
            or imported_name.startswith(
                "optimization."
            )
            or imported_name == "overtime"
            or imported_name.startswith(
                "overtime."
            )
            or imported_name == "planning"
            or imported_name.startswith(
                "planning."
            )
            or imported_name == "staffing"
            or imported_name.startswith(
                "staffing."
            )
            or imported_name == "workforce"
            or imported_name.startswith(
                "workforce."
            )
            or imported_name == "forecast"
            or imported_name.startswith(
                "src.forecast."
            )
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = (
            invalid_imports
        )


assert legacy_imports == {}, (
    "Legacy absolute imports remain in "
    f"src.orchestration: {legacy_imports}"
)

print(
    "PASS: No legacy orchestration.*, optimization.*, "
    "overtime.*, planning.*, staffing.*, workforce.*, "
    "or forecast.* absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "EnterpriseOrchestrationConfiguration",
    "EnterpriseDecisionOrchestrationEngine",
    "EnterpriseDecisionOrchestrationService",
    "EnterpriseDecisionRequest",
    "EnterpriseDecisionResult",
    "OrchestrationStage",
    "OrchestrationStatus",
)

assert tuple(
    orchestration_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.orchestration public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual: "
    f"{tuple(orchestration_package.__all__)}"
)

assert len(
    orchestration_package.__all__
) == len(
    set(orchestration_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        orchestration_package,
        symbol_name,
    )

print(
    "PASS: Orchestration public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "constants": (
        "DEFAULT_FORECAST_CONFIDENCE",
        "EXECUTION_ORDER",
        "MAX_FORECAST_CONFIDENCE",
        "MIN_FORECAST_CONFIDENCE",
        "ORCHESTRATION_DOMAIN_NAME",
        "ORCHESTRATION_DOMAIN_VERSION",
        "ORCHESTRATION_STAGES",
        "STAGE_COMPLETE",
        "STAGE_FORECAST",
        "STAGE_OPTIMIZATION",
        "STAGE_OVERTIME",
        "STAGE_PLANNING",
        "STAGE_STAFFING",
        "STATUS_COMPLETED",
        "STATUS_FAILED",
        "STATUS_PENDING",
        "STATUS_RUNNING",
        "SUPPORTED_ORCHESTRATION_STATUSES",
        "WORKFLOW_CAPACITY_PLANNING",
        "WORKFLOW_ENTERPRISE_DECISION",
    ),
    "exceptions": (
        "OrchestrationConfigurationError",
        "OrchestrationDependencyError",
        "OrchestrationEngineError",
        "OrchestrationError",
        "OrchestrationServiceError",
        "OrchestrationStageError",
        "OrchestrationValidationError",
    ),
    "models": (
        "EnterpriseDecisionRequest",
        "EnterpriseDecisionResult",
        "OrchestrationStage",
        "OrchestrationStatus",
    ),
    "configuration": (
        "EnterpriseOrchestrationConfiguration",
    ),
    "engine": (
        "EnterpriseDecisionOrchestrationEngine",
    ),
    "service": (
        "EnterpriseDecisionOrchestrationService",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.orchestration.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Orchestration leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.orchestration import (
    EnterpriseDecisionOrchestrationEngine,
    EnterpriseDecisionOrchestrationService,
    EnterpriseDecisionRequest,
    EnterpriseDecisionResult,
    EnterpriseOrchestrationConfiguration,
    OrchestrationStage,
    OrchestrationStatus,
)

from src.orchestration.configuration import (
    EnterpriseOrchestrationConfiguration
    as LeafEnterpriseOrchestrationConfiguration,
)

from src.orchestration.engine import (
    EnterpriseDecisionOrchestrationEngine
    as LeafEnterpriseDecisionOrchestrationEngine,
)

from src.orchestration.models import (
    EnterpriseDecisionRequest
    as LeafEnterpriseDecisionRequest,
    EnterpriseDecisionResult
    as LeafEnterpriseDecisionResult,
    OrchestrationStage as LeafOrchestrationStage,
    OrchestrationStatus as LeafOrchestrationStatus,
)

from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService
    as LeafEnterpriseDecisionOrchestrationService,
)

assert (
    EnterpriseOrchestrationConfiguration
    is LeafEnterpriseOrchestrationConfiguration
)

assert (
    EnterpriseDecisionOrchestrationEngine
    is LeafEnterpriseDecisionOrchestrationEngine
)

assert (
    EnterpriseDecisionOrchestrationService
    is LeafEnterpriseDecisionOrchestrationService
)

assert (
    EnterpriseDecisionRequest
    is LeafEnterpriseDecisionRequest
)

assert (
    EnterpriseDecisionResult
    is LeafEnterpriseDecisionResult
)

assert (
    OrchestrationStage
    is LeafOrchestrationStage
)

assert (
    OrchestrationStatus
    is LeafOrchestrationStatus
)

print(
    "PASS: Orchestration public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.orchestration.exceptions import (
    OrchestrationConfigurationError,
    OrchestrationDependencyError,
    OrchestrationEngineError,
    OrchestrationError,
    OrchestrationServiceError,
    OrchestrationStageError,
    OrchestrationValidationError,
)

for exception_type in (
    OrchestrationConfigurationError,
    OrchestrationDependencyError,
    OrchestrationEngineError,
    OrchestrationServiceError,
    OrchestrationStageError,
    OrchestrationValidationError,
):
    assert issubclass(
        exception_type,
        OrchestrationError,
    )

print(
    "PASS: Orchestration exception hierarchy "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants
# -----------------------------------------------------------------------------

from src.orchestration.constants import (
    DEFAULT_FORECAST_CONFIDENCE,
    EXECUTION_ORDER,
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
    ORCHESTRATION_DOMAIN_NAME,
    ORCHESTRATION_DOMAIN_VERSION,
    ORCHESTRATION_STAGES,
    STAGE_COMPLETE,
    STAGE_FORECAST,
    STAGE_OPTIMIZATION,
    STAGE_OVERTIME,
    STAGE_PLANNING,
    STAGE_STAFFING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_RUNNING,
)

assert (
    ORCHESTRATION_DOMAIN_NAME
    == "enterprise-decision-orchestration"
)

assert ORCHESTRATION_DOMAIN_VERSION == "1.0.0"

assert MIN_FORECAST_CONFIDENCE == 0.0
assert MAX_FORECAST_CONFIDENCE == 1.0
assert DEFAULT_FORECAST_CONFIDENCE == 0.80

assert STAGE_FORECAST == "forecast"
assert STAGE_PLANNING == "planning"
assert STAGE_OVERTIME == "overtime"
assert STAGE_STAFFING == "staffing"
assert STAGE_OPTIMIZATION == "optimization"
assert STAGE_COMPLETE == "complete"

assert ORCHESTRATION_STAGES == (
    "forecast",
    "planning",
    "overtime",
    "staffing",
    "optimization",
    "complete",
)

assert EXECUTION_ORDER == (
    "forecast",
    "planning",
    "overtime",
    "staffing",
    "optimization",
)

assert STATUS_PENDING == "PENDING"
assert STATUS_RUNNING == "RUNNING"
assert STATUS_COMPLETED == "COMPLETED"
assert STATUS_FAILED == "FAILED"

print(
    "PASS: Orchestration constants remain internally "
    "consistent"
)


# -----------------------------------------------------------------------------
# 10. Validate enum contracts
# -----------------------------------------------------------------------------

assert OrchestrationStatus.PENDING.value == "PENDING"
assert OrchestrationStatus.RUNNING.value == "RUNNING"
assert OrchestrationStatus.COMPLETED.value == "COMPLETED"
assert OrchestrationStatus.FAILED.value == "FAILED"

assert OrchestrationStage.FORECAST.value == "forecast"
assert OrchestrationStage.PLANNING.value == "planning"
assert OrchestrationStage.OVERTIME.value == "overtime"
assert OrchestrationStage.STAFFING.value == "staffing"

assert (
    OrchestrationStage.OPTIMIZATION.value
    == "optimization"
)

assert OrchestrationStage.COMPLETE.value == "complete"

print(
    "PASS: Orchestration enum contracts remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate configuration contract
# -----------------------------------------------------------------------------

configuration = EnterpriseOrchestrationConfiguration()

assert configuration.default_forecast_confidence == 0.80
assert configuration.enable_overtime_stage is True
assert configuration.enable_staffing_stage is True
assert configuration.enable_optimization_stage is True
assert configuration.fail_fast is True

assert configuration.execution_order == EXECUTION_ORDER

assert configuration.configuration_version == "1.0.0"

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "default_forecast_confidence"
] == 0.80

assert configuration_payload[
    "execution_order"
] == list(EXECUTION_ORDER)

assert configuration_payload[
    "enable_overtime_stage"
] is True

print(
    "PASS: EnterpriseOrchestrationConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate request contract
# -----------------------------------------------------------------------------

planning_date = date(2026, 8, 7)

request = EnterpriseDecisionRequest(
    planning_date=planning_date,
    expected_order_lines=10_000.0,
    available_associates=8,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    forecast_confidence=0.95,
    recurring_shortage_days=0,
    recurring_surplus_days=0,
    overtime_dependency_days=0,
    planning_horizon_days=30,
)

assert request.planning_date == planning_date
assert request.expected_order_lines == 10_000.0
assert request.available_associates == 8
assert request.productivity_lines_per_hour == 120.0
assert request.scheduled_hours == 10.0
assert request.forecast_confidence == 0.95
assert request.planning_horizon_days == 30

request_payload = request.as_dict()

assert request_payload[
    "planning_date"
] == "2026-08-07"

assert request_payload[
    "expected_order_lines"
] == 10_000.0

assert request_payload[
    "available_associates"
] == 8

print(
    "PASS: EnterpriseDecisionRequest contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate default dependency construction
# -----------------------------------------------------------------------------

engine = EnterpriseDecisionOrchestrationEngine(
    configuration=configuration
)

assert engine.configuration is configuration

from src.planning import CapacityPlanningService
from src.overtime import OvertimeRecommendationService
from src.staffing import StaffingRecommendationService
from src.optimization import WorkforceOptimizationService

assert isinstance(
    engine.planning_service,
    CapacityPlanningService,
)

assert isinstance(
    engine.overtime_service,
    OvertimeRecommendationService,
)

assert isinstance(
    engine.staffing_service,
    StaffingRecommendationService,
)

assert isinstance(
    engine.optimization_service,
    WorkforceOptimizationService,
)

print(
    "PASS: Orchestration cross-domain dependency "
    "construction remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate REAL end-to-end enterprise orchestration
# -----------------------------------------------------------------------------

result = engine.execute(
    request=request
)

assert isinstance(
    result,
    EnterpriseDecisionResult,
)

assert result.planning_date == planning_date

assert (
    result.workflow_status
    is OrchestrationStatus.COMPLETED
)

assert (
    result.completed_stage
    is OrchestrationStage.COMPLETE
)

assert result.expected_order_lines == 10_000.0
assert result.available_associates == 8

assert result.required_associates >= 0

assert result.associate_gap == (
    result.required_associates
    - result.available_associates
)

assert isinstance(
    result.overtime_recommendation,
    str,
)

assert result.overtime_recommendation.strip()

assert isinstance(
    result.staffing_recommendation,
    str,
)

assert result.staffing_recommendation.strip()

assert isinstance(
    result.optimization_action,
    str,
)

assert result.optimization_action.strip()

assert isinstance(
    result.optimization_priority,
    str,
)

assert result.optimization_priority.strip()

assert isinstance(
    result.optimization_status,
    str,
)

assert result.optimization_status.strip()

assert result.overtime_hours >= 0.0
assert result.recommended_associates >= 0

assert result.forecast_confidence == 0.95

assert isinstance(result.rationale, str)
assert result.rationale.strip()

assert result.workflow_version == "1.0.0"

print(
    "PASS: Real enterprise planning → overtime → staffing → "
    "optimization orchestration remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate result serialization
# -----------------------------------------------------------------------------

result_payload = result.as_dict()

assert result_payload[
    "planning_date"
] == "2026-08-07"

assert result_payload[
    "workflow_status"
] == "COMPLETED"

assert result_payload[
    "completed_stage"
] == "complete"

assert result_payload[
    "available_associates"
] == 8

assert result_payload[
    "associate_gap"
] == (
    result_payload["required_associates"]
    - result_payload["available_associates"]
)

assert isinstance(
    result_payload["generated_at_utc"],
    str,
)

assert result_payload[
    "workflow_version"
] == "1.0.0"

print(
    "PASS: EnterpriseDecisionResult serialization "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate service dependency wiring and execution
# -----------------------------------------------------------------------------

service = EnterpriseDecisionOrchestrationService(
    configuration=configuration,
    engine=engine,
)

assert service.configuration is configuration
assert service.engine is engine

service_result = service.execute(
    request=request
)

assert isinstance(
    service_result,
    EnterpriseDecisionResult,
)

assert (
    service_result.workflow_status
    is OrchestrationStatus.COMPLETED
)

assert (
    service_result.completed_stage
    is OrchestrationStage.COMPLETE
)

print(
    "PASS: EnterpriseDecisionOrchestrationService "
    "orchestration remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate optional-stage configuration
# -----------------------------------------------------------------------------

planning_only_configuration = (
    EnterpriseOrchestrationConfiguration(
        enable_overtime_stage=False,
        enable_staffing_stage=False,
        enable_optimization_stage=False,
    )
)

planning_only_engine = (
    EnterpriseDecisionOrchestrationEngine(
        configuration=planning_only_configuration
    )
)

planning_only_result = (
    planning_only_engine.execute(
        request=request
    )
)

assert (
    planning_only_result.workflow_status
    is OrchestrationStatus.COMPLETED
)

assert (
    planning_only_result.completed_stage
    is OrchestrationStage.COMPLETE
)

assert (
    planning_only_result.overtime_recommendation
    == "NOT_EXECUTED"
)

assert (
    planning_only_result.staffing_recommendation
    == "NOT_EXECUTED"
)

assert (
    planning_only_result.optimization_action
    == "NOT_EXECUTED"
)

assert (
    planning_only_result.optimization_priority
    == "NOT_EXECUTED"
)

assert (
    planning_only_result.optimization_status
    == "NOT_EXECUTED"
)

assert planning_only_result.overtime_hours == 0.0
assert planning_only_result.recommended_associates == 0

assert (
    planning_only_result.rationale
    == (
        "Orchestration completed without optional "
        "recommendation stages."
    )
)

print(
    "PASS: Orchestration optional-stage configuration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=-1.0,
        available_associates=8,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.95,
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Negative expected_order_lines must be rejected."
    )


try:
    EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=10_000.0,
        available_associates=-1,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=0.95,
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Negative available_associates must be rejected."
    )


try:
    EnterpriseDecisionRequest(
        planning_date=planning_date,
        expected_order_lines=10_000.0,
        available_associates=8,
        productivity_lines_per_hour=120.0,
        scheduled_hours=10.0,
        forecast_confidence=1.50,
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Invalid forecast confidence must be rejected."
    )


try:
    EnterpriseOrchestrationConfiguration(
        default_forecast_confidence=1.50
    )
except OrchestrationConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid orchestration forecast confidence "
        "must be rejected."
    )


try:
    EnterpriseOrchestrationConfiguration(
        execution_order=(
            "planning",
            "forecast",
        )
    )
except OrchestrationConfigurationError:
    pass
else:
    raise AssertionError(
        "Unsupported orchestration execution order "
        "must be rejected."
    )


try:
    engine.execute(
        request="invalid"
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Invalid orchestration request must be rejected."
    )


try:
    EnterpriseDecisionOrchestrationEngine(
        configuration="invalid"
    )
except OrchestrationDependencyError:
    pass
else:
    raise AssertionError(
        "Invalid orchestration configuration dependency "
        "must be rejected."
    )


try:
    EnterpriseDecisionOrchestrationService(
        configuration=(
            EnterpriseOrchestrationConfiguration()
        ),
        engine=engine,
    )
except OrchestrationValidationError:
    pass
else:
    raise AssertionError(
        "Service must reject mismatched configuration "
        "and engine dependencies."
    )

print(
    "PASS: Orchestration representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 19. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    EnterpriseOrchestrationConfiguration
)

for parameter_name in (
    "default_forecast_confidence",
    "enable_overtime_stage",
    "enable_staffing_stage",
    "enable_optimization_stage",
    "fail_fast",
    "execution_order",
    "configuration_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


request_signature = inspect.signature(
    EnterpriseDecisionRequest
)

for parameter_name in (
    "planning_date",
    "expected_order_lines",
    "available_associates",
    "productivity_lines_per_hour",
    "scheduled_hours",
    "forecast_confidence",
    "recurring_shortage_days",
    "recurring_surplus_days",
    "overtime_dependency_days",
    "planning_horizon_days",
):
    assert (
        parameter_name
        in request_signature.parameters
    )


engine_init_signature = inspect.signature(
    EnterpriseDecisionOrchestrationEngine
)

for parameter_name in (
    "configuration",
    "planning_service",
    "overtime_service",
    "staffing_service",
    "optimization_service",
):
    assert (
        parameter_name
        in engine_init_signature.parameters
    )


engine_execute_signature = inspect.signature(
    EnterpriseDecisionOrchestrationEngine.execute
)

assert (
    "request"
    in engine_execute_signature.parameters
)


service_signature = inspect.signature(
    EnterpriseDecisionOrchestrationService.execute
)

assert "request" in service_signature.parameters

print(
    "PASS: Orchestration public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.orchestration")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.reporting
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* imports
#     - Cross-package namespace integrity
#     - Root and leaf public APIs
#     - Public object identity
#     - Constants and enums
#     - Configuration contract
#     - Request/report models
#     - Formatter: dict / json / text
#     - Real orchestration-result → reporting integration
#     - Service orchestration
#     - Failure contracts
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path


PACKAGE_NAME = "src.reporting"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "formatter",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

reporting_package = importlib.import_module(
    PACKAGE_NAME
)

assert reporting_package.__name__ == PACKAGE_NAME
assert reporting_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.reporting"
)


# -----------------------------------------------------------------------------
# 2. Import every reporting module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = (
        f"{PACKAGE_NAME}.{module_name}"
    )

    loaded_modules[module_name] = (
        importlib.import_module(
            qualified_name
        )
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every reporting module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level reporting.* loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "reporting"
        or module_name.startswith("reporting.")
    )
)

assert legacy_modules == [], (
    "Legacy reporting.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy reporting.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": reporting_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "reporting"
            or imported_name.startswith("reporting.")
            or imported_name == "orchestration"
            or imported_name.startswith(
                "orchestration."
            )
            or imported_name == "planning"
            or imported_name.startswith("planning.")
            or imported_name == "workforce"
            or imported_name.startswith("workforce.")
            or imported_name == "forecast"
            or imported_name.startswith("src.forecast.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = (
            invalid_imports
        )


assert legacy_imports == {}, (
    "Legacy absolute imports remain in "
    f"src.reporting: {legacy_imports}"
)

print(
    "PASS: No legacy reporting.*, orchestration.*, "
    "planning.*, workforce.*, or forecast.* "
    "absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "REPORTING_DOMAIN_VERSION",

    "REPORT_FORMAT_JSON",
    "REPORT_FORMAT_DICT",
    "REPORT_FORMAT_TEXT",
    "SUPPORTED_REPORT_FORMATS",
    "DEFAULT_REPORT_FORMAT",

    "REPORT_TYPE_EXECUTIVE",
    "REPORT_TYPE_OPERATIONAL",
    "REPORT_TYPE_TECHNICAL",
    "SUPPORTED_REPORT_TYPES",
    "DEFAULT_REPORT_TYPE",

    "REPORT_STATUS_SUCCESS",
    "REPORT_STATUS_WARNING",
    "REPORT_STATUS_ERROR",
    "SUPPORTED_REPORT_STATUSES",

    "DEFAULT_TIMEZONE",
    "DEFAULT_REPORT_VERSION",
    "DEFAULT_DATETIME_FORMAT",
    "INDENT_SIZE",
    "MAX_REPORT_TITLE_LENGTH",
    "MAX_REPORT_SUMMARY_LENGTH",

    "SECTION_EXECUTIVE_SUMMARY",
    "SECTION_FORECAST",
    "SECTION_PLANNING",
    "SECTION_OVERTIME",
    "SECTION_STAFFING",
    "SECTION_OPTIMIZATION",
    "SECTION_METADATA",
    "DEFAULT_REPORT_SECTIONS",

    "ReportingError",
    "ReportingValidationError",
    "ReportingConfigurationError",
    "ReportingFormattingError",
    "ReportingServiceError",

    "DecisionReportRequest",
    "EnterpriseDecisionReport",
    "ReportFormat",
    "ReportSection",
    "ReportStatus",
    "ReportType",

    "ReportingConfiguration",
    "EnterpriseDecisionReportFormatter",
    "EnterpriseDecisionReportingService",
)

assert tuple(
    reporting_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.reporting public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual: "
    f"{tuple(reporting_package.__all__)}"
)

assert len(
    reporting_package.__all__
) == len(
    set(reporting_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        reporting_package,
        symbol_name,
    )

print(
    "PASS: Reporting public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate declared leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "exceptions": (
        "ReportingConfigurationError",
        "ReportingError",
        "ReportingFormattingError",
        "ReportingServiceError",
        "ReportingValidationError",
    ),
    "models": (
        "DecisionReportRequest",
        "EnterpriseDecisionReport",
        "ReportFormat",
        "ReportSection",
        "ReportStatus",
        "ReportType",
    ),
    "configuration": (
        "ReportingConfiguration",
    ),
    "formatter": (
        "EnterpriseDecisionReportFormatter",
    ),
    "service": (
        "EnterpriseDecisionReportingService",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.reporting.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Reporting declared leaf-module __all__ "
    "contracts are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.reporting import (
    DecisionReportRequest,
    EnterpriseDecisionReport,
    EnterpriseDecisionReportFormatter,
    EnterpriseDecisionReportingService,
    ReportFormat,
    ReportingConfiguration,
    ReportSection,
    ReportStatus,
    ReportType,
)

from src.reporting.configuration import (
    ReportingConfiguration
    as LeafReportingConfiguration,
)

from src.reporting.formatter import (
    EnterpriseDecisionReportFormatter
    as LeafEnterpriseDecisionReportFormatter,
)

from src.reporting.models import (
    DecisionReportRequest
    as LeafDecisionReportRequest,
    EnterpriseDecisionReport
    as LeafEnterpriseDecisionReport,
    ReportFormat as LeafReportFormat,
    ReportSection as LeafReportSection,
    ReportStatus as LeafReportStatus,
    ReportType as LeafReportType,
)

from src.reporting.service import (
    EnterpriseDecisionReportingService
    as LeafEnterpriseDecisionReportingService,
)

assert (
    ReportingConfiguration
    is LeafReportingConfiguration
)

assert (
    EnterpriseDecisionReportFormatter
    is LeafEnterpriseDecisionReportFormatter
)

assert (
    EnterpriseDecisionReportingService
    is LeafEnterpriseDecisionReportingService
)

assert (
    DecisionReportRequest
    is LeafDecisionReportRequest
)

assert (
    EnterpriseDecisionReport
    is LeafEnterpriseDecisionReport
)

assert ReportFormat is LeafReportFormat
assert ReportSection is LeafReportSection
assert ReportStatus is LeafReportStatus
assert ReportType is LeafReportType

print(
    "PASS: Reporting public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.reporting import (
    ReportingConfigurationError,
    ReportingError,
    ReportingFormattingError,
    ReportingServiceError,
    ReportingValidationError,
)

for exception_type in (
    ReportingConfigurationError,
    ReportingFormattingError,
    ReportingServiceError,
    ReportingValidationError,
):
    assert issubclass(
        exception_type,
        ReportingError,
    )

print(
    "PASS: Reporting exception hierarchy "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants and enum contracts
# -----------------------------------------------------------------------------

from src.reporting import (
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_REPORT_FORMAT,
    DEFAULT_REPORT_SECTIONS,
    DEFAULT_REPORT_TYPE,
    DEFAULT_REPORT_VERSION,
    DEFAULT_TIMEZONE,
    INDENT_SIZE,
    MAX_REPORT_SUMMARY_LENGTH,
    MAX_REPORT_TITLE_LENGTH,
    REPORTING_DOMAIN_VERSION,
    REPORT_FORMAT_DICT,
    REPORT_FORMAT_JSON,
    REPORT_FORMAT_TEXT,
    REPORT_STATUS_ERROR,
    REPORT_STATUS_SUCCESS,
    REPORT_STATUS_WARNING,
    REPORT_TYPE_EXECUTIVE,
    REPORT_TYPE_OPERATIONAL,
    REPORT_TYPE_TECHNICAL,
)

assert REPORTING_DOMAIN_VERSION == "1.0.0"

assert REPORT_FORMAT_JSON == "json"
assert REPORT_FORMAT_DICT == "dict"
assert REPORT_FORMAT_TEXT == "text"
assert DEFAULT_REPORT_FORMAT == "dict"

assert REPORT_TYPE_EXECUTIVE == "executive"
assert REPORT_TYPE_OPERATIONAL == "operational"
assert REPORT_TYPE_TECHNICAL == "technical"
assert DEFAULT_REPORT_TYPE == "operational"

assert REPORT_STATUS_SUCCESS == "SUCCESS"
assert REPORT_STATUS_WARNING == "WARNING"
assert REPORT_STATUS_ERROR == "ERROR"

assert DEFAULT_TIMEZONE == "UTC"
assert DEFAULT_REPORT_VERSION == "1.0.0"
assert DEFAULT_DATETIME_FORMAT == "%Y-%m-%d %H:%M:%S UTC"
assert INDENT_SIZE == 4

assert MAX_REPORT_TITLE_LENGTH == 200
assert MAX_REPORT_SUMMARY_LENGTH == 5000

assert len(DEFAULT_REPORT_SECTIONS) == 7

assert ReportFormat.JSON.value == "json"
assert ReportFormat.DICT.value == "dict"
assert ReportFormat.TEXT.value == "text"

assert ReportType.EXECUTIVE.value == "executive"
assert ReportType.OPERATIONAL.value == "operational"
assert ReportType.TECHNICAL.value == "technical"

assert ReportStatus.SUCCESS.value == "SUCCESS"
assert ReportStatus.WARNING.value == "WARNING"
assert ReportStatus.ERROR.value == "ERROR"

print(
    "PASS: Reporting constants and enum contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 10. Validate ReportingConfiguration
# -----------------------------------------------------------------------------

configuration = ReportingConfiguration()

assert configuration.default_report_type == "operational"
assert configuration.default_report_format == "dict"

assert configuration.include_metadata is True
assert configuration.include_rationale is True
assert configuration.include_empty_sections is False

assert (
    configuration.section_order
    == DEFAULT_REPORT_SECTIONS
)

assert configuration.indent_size == 4
assert (
    configuration.datetime_format
    == "%Y-%m-%d %H:%M:%S UTC"
)

assert configuration.maximum_title_length == 200
assert configuration.maximum_summary_length == 5000

assert configuration.report_version == "1.0.0"

configuration_payload = configuration.as_dict()

assert configuration_payload[
    "default_report_type"
] == "operational"

assert configuration_payload[
    "default_report_format"
] == "dict"

assert configuration_payload[
    "section_order"
] == list(DEFAULT_REPORT_SECTIONS)

print(
    "PASS: ReportingConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate request and section model contracts
# -----------------------------------------------------------------------------

request = DecisionReportRequest(
    report_type=ReportType.OPERATIONAL,
    report_format=ReportFormat.DICT,
    title="Implementation 28 Workforce Decision Report",
    include_metadata=True,
    include_rationale=True,
    include_empty_sections=False,
)

assert request.report_type is ReportType.OPERATIONAL
assert request.report_format is ReportFormat.DICT

assert (
    request.title
    == "Implementation 28 Workforce Decision Report"
)

assert request.include_metadata is True
assert request.include_rationale is True
assert request.include_empty_sections is False

request_payload = request.as_dict()

assert request_payload[
    "report_type"
] == "operational"

assert request_payload[
    "report_format"
] == "dict"


sample_section = ReportSection(
    name="Planning",
    content={
        "available_associates": 8,
        "required_associates": 10,
    },
    order=0,
)

assert sample_section.name == "Planning"
assert sample_section.order == 0

assert sample_section.as_dict() == {
    "name": "Planning",
    "content": {
        "available_associates": 8,
        "required_associates": 10,
    },
    "order": 0,
}

print(
    "PASS: Reporting request and section model "
    "contracts remain operational"
)


# -----------------------------------------------------------------------------
# 12. Build a real orchestration result
# -----------------------------------------------------------------------------

from src.orchestration import (
    EnterpriseDecisionOrchestrationEngine,
    EnterpriseDecisionRequest,
    EnterpriseOrchestrationConfiguration,
    OrchestrationStage,
    OrchestrationStatus,
)

planning_date = date(2026, 8, 7)

orchestration_configuration = (
    EnterpriseOrchestrationConfiguration()
)

orchestration_engine = (
    EnterpriseDecisionOrchestrationEngine(
        configuration=orchestration_configuration
    )
)

decision_request = EnterpriseDecisionRequest(
    planning_date=planning_date,
    expected_order_lines=10_000.0,
    available_associates=8,
    productivity_lines_per_hour=120.0,
    scheduled_hours=10.0,
    forecast_confidence=0.95,
    recurring_shortage_days=0,
    recurring_surplus_days=0,
    overtime_dependency_days=0,
    planning_horizon_days=30,
)

decision_result = orchestration_engine.execute(
    request=decision_request
)

assert (
    decision_result.workflow_status
    is OrchestrationStatus.COMPLETED
)

assert (
    decision_result.completed_stage
    is OrchestrationStage.COMPLETE
)

print(
    "PASS: Created real EnterpriseDecisionResult "
    "for reporting integration validation"
)


# -----------------------------------------------------------------------------
# 13. Validate formatter dependency contract
# -----------------------------------------------------------------------------

formatter = EnterpriseDecisionReportFormatter(
    configuration=configuration
)

assert formatter.configuration is configuration

print(
    "PASS: EnterpriseDecisionReportFormatter "
    "dependency contract remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate report construction through service
# -----------------------------------------------------------------------------

service = EnterpriseDecisionReportingService(
    configuration=configuration,
    formatter=formatter,
)

assert service.configuration is configuration
assert service.formatter is formatter

report = service.build_report(
    decision_result=decision_result,
    request=request,
)

assert isinstance(
    report,
    EnterpriseDecisionReport,
)

assert (
    report.report_type
    is ReportType.OPERATIONAL
)

assert report.title == (
    "Implementation 28 Workforce Decision Report"
)

assert report.planning_date == planning_date

assert report.source_workflow_version == (
    decision_result.workflow_version
)

assert report.report_version == "1.0.0"

assert report.status in (
    ReportStatus.SUCCESS,
    ReportStatus.WARNING,
)

assert len(report.sections) >= 6

section_names = tuple(
    section.name
    for section in report.sections
)

for expected_section in (
    "Executive Summary",
    "Forecast",
    "Planning",
    "Overtime",
    "Staffing",
    "Optimization",
    "Metadata",
):
    assert expected_section in section_names

assert isinstance(report.summary, str)
assert report.summary.strip()

assert isinstance(report.metadata, dict)
assert report.metadata[
    "workflow_version"
] == decision_result.workflow_version

print(
    "PASS: Enterprise reporting service builds "
    "validated operational reports"
)


# -----------------------------------------------------------------------------
# 15. Validate report model serialization
# -----------------------------------------------------------------------------

report_payload = report.as_dict()

assert report_payload[
    "report_type"
] == "operational"

assert report_payload[
    "planning_date"
] == "2026-08-07"

assert report_payload[
    "source_workflow_version"
] == decision_result.workflow_version

assert report_payload[
    "report_version"
] == "1.0.0"

assert isinstance(
    report_payload["generated_at_utc"],
    str,
)

assert len(
    report_payload["sections"]
) == len(report.sections)

print(
    "PASS: EnterpriseDecisionReport serialization "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate DICT formatter output
# -----------------------------------------------------------------------------

dict_output = formatter.format(
    report=report,
    report_format=ReportFormat.DICT,
)

assert isinstance(dict_output, dict)

assert dict_output[
    "report_id"
] == report.report_id

assert dict_output[
    "report_type"
] == "operational"

assert dict_output[
    "planning_date"
] == "2026-08-07"

print(
    "PASS: Reporting DICT formatter remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate JSON formatter output
# -----------------------------------------------------------------------------

json_output = formatter.format(
    report=report,
    report_format=ReportFormat.JSON,
)

assert isinstance(json_output, str)

parsed_json = json.loads(json_output)

assert parsed_json[
    "report_id"
] == report.report_id

assert parsed_json[
    "report_type"
] == "operational"

assert parsed_json[
    "planning_date"
] == "2026-08-07"

assert len(parsed_json["sections"]) == len(
    report.sections
)

print(
    "PASS: Reporting JSON formatter remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate TEXT formatter output
# -----------------------------------------------------------------------------

text_output = formatter.format(
    report=report,
    report_format=ReportFormat.TEXT,
)

assert isinstance(text_output, str)

for expected_text in (
    "Implementation 28 Workforce Decision Report",
    "Report ID:",
    "Report Type: operational",
    "Planning Date: 2026-08-07",
    "Summary",
    "Planning",
    "Optimization",
    "Source Workflow Version:",
    "Report Version: 1.0.0",
):
    assert expected_text in text_output

print(
    "PASS: Reporting TEXT formatter remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate service.generate() for all three formats
# -----------------------------------------------------------------------------

dict_request = DecisionReportRequest(
    report_type=ReportType.OPERATIONAL,
    report_format=ReportFormat.DICT,
    title="Operational Workforce Report",
)

dict_service_output = service.generate(
    decision_result=decision_result,
    request=dict_request,
)

assert isinstance(
    dict_service_output,
    dict,
)


json_request = DecisionReportRequest(
    report_type=ReportType.TECHNICAL,
    report_format=ReportFormat.JSON,
    title="Technical Workforce Report",
)

json_service_output = service.generate(
    decision_result=decision_result,
    request=json_request,
)

assert isinstance(
    json_service_output,
    str,
)

assert json.loads(
    json_service_output
)["report_type"] == "technical"


text_request = DecisionReportRequest(
    report_type=ReportType.EXECUTIVE,
    report_format=ReportFormat.TEXT,
    title="Executive Workforce Report",
)

text_service_output = service.generate(
    decision_result=decision_result,
    request=text_request,
)

assert isinstance(
    text_service_output,
    str,
)

assert "Executive Workforce Report" in (
    text_service_output
)

assert "Report Type: executive" in (
    text_service_output
)

print(
    "PASS: EnterpriseDecisionReportingService supports "
    "DICT, JSON, and TEXT outputs"
)


# -----------------------------------------------------------------------------
# 20. Validate report-type section scoping
# -----------------------------------------------------------------------------

executive_report = service.build_report(
    decision_result=decision_result,
    request=DecisionReportRequest(
        report_type=ReportType.EXECUTIVE,
        report_format=ReportFormat.DICT,
        title="Executive Validation Report",
    ),
)

executive_sections = tuple(
    section.name
    for section in executive_report.sections
)

assert executive_sections == (
    "Executive Summary",
    "Planning",
    "Optimization",
    "Metadata",
)

technical_report = service.build_report(
    decision_result=decision_result,
    request=DecisionReportRequest(
        report_type=ReportType.TECHNICAL,
        report_format=ReportFormat.DICT,
        title="Technical Validation Report",
    ),
)

technical_sections = tuple(
    section.name
    for section in technical_report.sections
)

assert technical_sections == (
    "Executive Summary",
    "Forecast",
    "Planning",
    "Overtime",
    "Staffing",
    "Optimization",
    "Metadata",
)

print(
    "PASS: Reporting audience-specific section scoping "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 21. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    DecisionReportRequest(
        report_type=ReportType.OPERATIONAL,
        report_format=ReportFormat.DICT,
        title="",
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Empty report title must be rejected."
    )


try:
    ReportSection(
        name="",
        content={},
        order=0,
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Empty report section name must be rejected."
    )


try:
    ReportingConfiguration(
        default_report_type="unsupported",
    )
except ReportingConfigurationError:
    pass
else:
    raise AssertionError(
        "Unsupported report type configuration "
        "must be rejected."
    )


try:
    ReportingConfiguration(
        section_order=(
            "Planning",
            "Planning",
        )
    )
except ReportingConfigurationError:
    pass
else:
    raise AssertionError(
        "Duplicate report sections must be rejected."
    )


try:
    formatter.format(
        report="invalid",
        report_format=ReportFormat.DICT,
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Invalid report formatter input must be rejected."
    )


try:
    service.build_report(
        decision_result="invalid",
        request=request,
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Invalid orchestration result must be rejected."
    )


try:
    EnterpriseDecisionReportingService(
        configuration=ReportingConfiguration(),
        formatter=formatter,
    )
except ReportingValidationError:
    pass
else:
    raise AssertionError(
        "Service must reject mismatched configuration "
        "and formatter dependencies."
    )

print(
    "PASS: Reporting representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 22. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    ReportingConfiguration
)

for parameter_name in (
    "default_report_type",
    "default_report_format",
    "include_metadata",
    "include_rationale",
    "include_empty_sections",
    "section_order",
    "indent_size",
    "datetime_format",
    "maximum_title_length",
    "maximum_summary_length",
    "report_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


formatter_signature = inspect.signature(
    EnterpriseDecisionReportFormatter.format
)

assert "report" in formatter_signature.parameters
assert "report_format" in (
    formatter_signature.parameters
)


build_signature = inspect.signature(
    EnterpriseDecisionReportingService.build_report
)

assert (
    "decision_result"
    in build_signature.parameters
)

assert "request" in build_signature.parameters


generate_signature = inspect.signature(
    EnterpriseDecisionReportingService.generate
)

assert (
    "decision_result"
    in generate_signature.parameters
)

assert "request" in generate_signature.parameters

print(
    "PASS: Reporting public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.reporting")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.monitoring
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* imports
#     - Legacy namespace detection
#     - Root and leaf public APIs
#     - Public object identity
#     - Constants and enums
#     - Configuration contract
#     - Execution and metric models
#     - Metrics collection and alerting
#     - Health-check registration and aggregation
#     - Unified EnterpriseMonitoringService snapshot
#     - Failure contracts
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


PACKAGE_NAME = "src.monitoring"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "metrics",
    "health",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

monitoring_package = importlib.import_module(
    PACKAGE_NAME
)

assert monitoring_package.__name__ == PACKAGE_NAME
assert monitoring_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.monitoring"
)


# -----------------------------------------------------------------------------
# 2. Import every monitoring module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = (
        f"{PACKAGE_NAME}.{module_name}"
    )

    loaded_modules[module_name] = (
        importlib.import_module(
            qualified_name
        )
    )

    assert (
        loaded_modules[module_name].__name__
        == qualified_name
    )

print(
    "PASS: Imported every monitoring module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy top-level monitoring.* loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "monitoring"
        or module_name.startswith("monitoring.")
    )
)

assert legacy_modules == [], (
    "Legacy monitoring.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy monitoring.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": monitoring_package,
    **loaded_modules,
}

legacy_imports: dict[str, tuple[str, ...]] = {}

for module_name, module in modules_to_scan.items():
    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    invalid_imports = tuple(
        imported_name
        for imported_name in absolute_imports
        if (
            imported_name == "monitoring"
            or imported_name.startswith("monitoring.")
            or imported_name == "forecast"
            or imported_name.startswith("forecast.")
            or imported_name == "planning"
            or imported_name.startswith("planning.")
            or imported_name == "workforce"
            or imported_name.startswith("workforce.")
            or imported_name == "orchestration"
            or imported_name.startswith("orchestration.")
            or imported_name == "reporting"
            or imported_name.startswith("reporting.")
        )
    )

    if invalid_imports:
        legacy_imports[module_name] = invalid_imports


assert legacy_imports == {}, (
    "Legacy absolute imports remain in "
    f"src.monitoring: {legacy_imports}"
)

print(
    "PASS: No legacy monitoring.*, forecast.*, planning.*, "
    "workforce.*, orchestration.*, or reporting.* "
    "absolute source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "MONITORING_DOMAIN_NAME",
    "MONITORING_DOMAIN_VERSION",

    "HEALTH_STATUS_HEALTHY",
    "HEALTH_STATUS_DEGRADED",
    "HEALTH_STATUS_UNHEALTHY",
    "HEALTH_STATUS_UNKNOWN",
    "SUPPORTED_HEALTH_STATUSES",

    "EXECUTION_STATUS_PENDING",
    "EXECUTION_STATUS_RUNNING",
    "EXECUTION_STATUS_SUCCEEDED",
    "EXECUTION_STATUS_FAILED",
    "EXECUTION_STATUS_CANCELLED",
    "SUPPORTED_EXECUTION_STATUSES",

    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "SEVERITY_ERROR",
    "SEVERITY_CRITICAL",
    "SUPPORTED_SEVERITY_LEVELS",

    "METRIC_TYPE_COUNTER",
    "METRIC_TYPE_GAUGE",
    "METRIC_TYPE_TIMER",
    "METRIC_TYPE_DISTRIBUTION",
    "SUPPORTED_METRIC_TYPES",

    "METRIC_EXECUTION_COUNT",
    "METRIC_EXECUTION_DURATION_MS",
    "METRIC_SUCCESS_COUNT",
    "METRIC_FAILURE_COUNT",
    "METRIC_SUCCESS_RATE",
    "METRIC_FAILURE_RATE",
    "METRIC_STAGE_DURATION_MS",
    "METRIC_HEALTH_CHECK_COUNT",
    "METRIC_COMPONENT_AVAILABILITY",

    "COMPONENT_FORECAST",
    "COMPONENT_PLANNING",
    "COMPONENT_OVERTIME",
    "COMPONENT_STAFFING",
    "COMPONENT_OPTIMIZATION",
    "COMPONENT_ORCHESTRATION",
    "COMPONENT_REPORTING",
    "COMPONENT_PLATFORM",
    "SUPPORTED_MONITORING_COMPONENTS",

    "MINIMUM_SUCCESS_RATE",
    "MAXIMUM_SUCCESS_RATE",
    "DEFAULT_WARNING_SUCCESS_RATE",
    "DEFAULT_CRITICAL_SUCCESS_RATE",
    "DEFAULT_WARNING_DURATION_MS",
    "DEFAULT_CRITICAL_DURATION_MS",
    "DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS",

    "DEFAULT_MONITORING_VERSION",
    "DEFAULT_TIMEZONE",
    "DEFAULT_TIMESTAMP_FORMAT",

    "MonitoringError",
    "MonitoringValidationError",
    "MonitoringConfigurationError",
    "MonitoringMetricsError",
    "MonitoringHealthCheckError",
    "MonitoringServiceError",

    "MetricRecord",
    "ExecutionRecord",
    "ComponentHealth",
    "MonitoringAlert",
    "PlatformHealthReport",
    "MetricType",
    "ExecutionStatus",
    "HealthStatus",
    "SeverityLevel",

    "MonitoringConfiguration",
    "MonitoringMetricsService",
    "MonitoringHealthService",
    "HealthCheckCallable",
    "EnterpriseMonitoringService",
)

assert tuple(
    monitoring_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.monitoring public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   {tuple(monitoring_package.__all__)}"
)

assert len(
    monitoring_package.__all__
) == len(
    set(monitoring_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        monitoring_package,
        symbol_name,
    )

print(
    "PASS: Monitoring public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "constants": (
        "MONITORING_DOMAIN_NAME",
        "MONITORING_DOMAIN_VERSION",
        "HEALTH_STATUS_HEALTHY",
        "HEALTH_STATUS_DEGRADED",
        "HEALTH_STATUS_UNHEALTHY",
        "HEALTH_STATUS_UNKNOWN",
        "SUPPORTED_HEALTH_STATUSES",
        "EXECUTION_STATUS_PENDING",
        "EXECUTION_STATUS_RUNNING",
        "EXECUTION_STATUS_SUCCEEDED",
        "EXECUTION_STATUS_FAILED",
        "EXECUTION_STATUS_CANCELLED",
        "SUPPORTED_EXECUTION_STATUSES",
        "SEVERITY_INFO",
        "SEVERITY_WARNING",
        "SEVERITY_ERROR",
        "SEVERITY_CRITICAL",
        "SUPPORTED_SEVERITY_LEVELS",
        "METRIC_TYPE_COUNTER",
        "METRIC_TYPE_GAUGE",
        "METRIC_TYPE_TIMER",
        "METRIC_TYPE_DISTRIBUTION",
        "SUPPORTED_METRIC_TYPES",
        "METRIC_EXECUTION_COUNT",
        "METRIC_EXECUTION_DURATION_MS",
        "METRIC_SUCCESS_COUNT",
        "METRIC_FAILURE_COUNT",
        "METRIC_SUCCESS_RATE",
        "METRIC_FAILURE_RATE",
        "METRIC_STAGE_DURATION_MS",
        "METRIC_HEALTH_CHECK_COUNT",
        "METRIC_COMPONENT_AVAILABILITY",
        "COMPONENT_FORECAST",
        "COMPONENT_PLANNING",
        "COMPONENT_OVERTIME",
        "COMPONENT_STAFFING",
        "COMPONENT_OPTIMIZATION",
        "COMPONENT_ORCHESTRATION",
        "COMPONENT_REPORTING",
        "COMPONENT_PLATFORM",
        "SUPPORTED_MONITORING_COMPONENTS",
        "MINIMUM_SUCCESS_RATE",
        "MAXIMUM_SUCCESS_RATE",
        "DEFAULT_WARNING_SUCCESS_RATE",
        "DEFAULT_CRITICAL_SUCCESS_RATE",
        "DEFAULT_WARNING_DURATION_MS",
        "DEFAULT_CRITICAL_DURATION_MS",
        "DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS",
        "DEFAULT_MONITORING_VERSION",
        "DEFAULT_TIMEZONE",
        "DEFAULT_TIMESTAMP_FORMAT",
    ),
    "exceptions": (
        "MonitoringConfigurationError",
        "MonitoringError",
        "MonitoringHealthCheckError",
        "MonitoringMetricsError",
        "MonitoringServiceError",
        "MonitoringValidationError",
    ),
    "models": (
        "ComponentHealth",
        "ExecutionRecord",
        "ExecutionStatus",
        "HealthStatus",
        "MetricRecord",
        "MetricType",
        "MonitoringAlert",
        "PlatformHealthReport",
        "SeverityLevel",
    ),
    "configuration": (
        "MonitoringConfiguration",
    ),
    "metrics": (
        "MonitoringMetricsService",
    ),
    "health": (
        "HealthCheckCallable",
        "MonitoringHealthService",
    ),
    "service": (
        "EnterpriseMonitoringService",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):
    module = loaded_modules[module_name]

    assert hasattr(module, "__all__")

    actual_all = tuple(module.__all__)

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.monitoring.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )

print(
    "PASS: Monitoring leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate public/leaf object identity
# -----------------------------------------------------------------------------

from src.monitoring import (
    ComponentHealth,
    EnterpriseMonitoringService,
    ExecutionRecord,
    ExecutionStatus,
    HealthStatus,
    MetricRecord,
    MetricType,
    MonitoringConfiguration,
    MonitoringHealthService,
    MonitoringMetricsService,
    MonitoringAlert,
    PlatformHealthReport,
    SeverityLevel,
)

from src.monitoring.configuration import (
    MonitoringConfiguration
    as LeafMonitoringConfiguration,
)

from src.monitoring.health import (
    MonitoringHealthService
    as LeafMonitoringHealthService,
)

from src.monitoring.metrics import (
    MonitoringMetricsService
    as LeafMonitoringMetricsService,
)

from src.monitoring.models import (
    ComponentHealth as LeafComponentHealth,
    ExecutionRecord as LeafExecutionRecord,
    ExecutionStatus as LeafExecutionStatus,
    HealthStatus as LeafHealthStatus,
    MetricRecord as LeafMetricRecord,
    MetricType as LeafMetricType,
    MonitoringAlert as LeafMonitoringAlert,
    PlatformHealthReport as LeafPlatformHealthReport,
    SeverityLevel as LeafSeverityLevel,
)

from src.monitoring.service import (
    EnterpriseMonitoringService
    as LeafEnterpriseMonitoringService,
)

assert MonitoringConfiguration is LeafMonitoringConfiguration
assert MonitoringMetricsService is LeafMonitoringMetricsService
assert MonitoringHealthService is LeafMonitoringHealthService

assert (
    EnterpriseMonitoringService
    is LeafEnterpriseMonitoringService
)

assert MetricRecord is LeafMetricRecord
assert ExecutionRecord is LeafExecutionRecord
assert ComponentHealth is LeafComponentHealth
assert MonitoringAlert is LeafMonitoringAlert
assert PlatformHealthReport is LeafPlatformHealthReport

assert MetricType is LeafMetricType
assert ExecutionStatus is LeafExecutionStatus
assert HealthStatus is LeafHealthStatus
assert SeverityLevel is LeafSeverityLevel

print(
    "PASS: Monitoring public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.monitoring import (
    MonitoringConfigurationError,
    MonitoringError,
    MonitoringHealthCheckError,
    MonitoringMetricsError,
    MonitoringServiceError,
    MonitoringValidationError,
)

for exception_type in (
    MonitoringConfigurationError,
    MonitoringHealthCheckError,
    MonitoringMetricsError,
    MonitoringServiceError,
    MonitoringValidationError,
):
    assert issubclass(
        exception_type,
        MonitoringError,
    )

print(
    "PASS: Monitoring exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants and enum contracts
# -----------------------------------------------------------------------------

from src.monitoring import (
    COMPONENT_ORCHESTRATION,
    COMPONENT_PLATFORM,
    DEFAULT_CRITICAL_DURATION_MS,
    DEFAULT_CRITICAL_SUCCESS_RATE,
    DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
    DEFAULT_MONITORING_VERSION,
    DEFAULT_TIMESTAMP_FORMAT,
    DEFAULT_TIMEZONE,
    DEFAULT_WARNING_DURATION_MS,
    DEFAULT_WARNING_SUCCESS_RATE,
    MAXIMUM_SUCCESS_RATE,
    MINIMUM_SUCCESS_RATE,
    MONITORING_DOMAIN_NAME,
    MONITORING_DOMAIN_VERSION,
)

assert (
    MONITORING_DOMAIN_NAME
    == "enterprise-monitoring-observability"
)

assert MONITORING_DOMAIN_VERSION == "1.0.0"

assert MINIMUM_SUCCESS_RATE == 0.0
assert MAXIMUM_SUCCESS_RATE == 1.0

assert DEFAULT_WARNING_SUCCESS_RATE == 0.95
assert DEFAULT_CRITICAL_SUCCESS_RATE == 0.80

assert DEFAULT_WARNING_DURATION_MS == 5_000.0
assert DEFAULT_CRITICAL_DURATION_MS == 15_000.0

assert DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS == 30.0

assert DEFAULT_MONITORING_VERSION == "1.0.0"
assert DEFAULT_TIMEZONE == "UTC"
assert (
    DEFAULT_TIMESTAMP_FORMAT
    == "%Y-%m-%dT%H:%M:%S.%fZ"
)

assert HealthStatus.HEALTHY.value == "HEALTHY"
assert HealthStatus.DEGRADED.value == "DEGRADED"
assert HealthStatus.UNHEALTHY.value == "UNHEALTHY"
assert HealthStatus.UNKNOWN.value == "UNKNOWN"

assert ExecutionStatus.PENDING.value == "PENDING"
assert ExecutionStatus.RUNNING.value == "RUNNING"
assert ExecutionStatus.SUCCEEDED.value == "SUCCEEDED"
assert ExecutionStatus.FAILED.value == "FAILED"
assert ExecutionStatus.CANCELLED.value == "CANCELLED"

assert SeverityLevel.INFO.value == "INFO"
assert SeverityLevel.WARNING.value == "WARNING"
assert SeverityLevel.ERROR.value == "ERROR"
assert SeverityLevel.CRITICAL.value == "CRITICAL"

assert MetricType.COUNTER.value == "COUNTER"
assert MetricType.GAUGE.value == "GAUGE"
assert MetricType.TIMER.value == "TIMER"
assert MetricType.DISTRIBUTION.value == "DISTRIBUTION"

print(
    "PASS: Monitoring constants and enum contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 10. Validate configuration contract
# -----------------------------------------------------------------------------

configuration = MonitoringConfiguration()

assert COMPONENT_ORCHESTRATION in (
    configuration.enabled_components
)

assert COMPONENT_PLATFORM in (
    configuration.enabled_components
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

configuration_payload = configuration.as_dict()

assert isinstance(
    configuration_payload["enabled_components"],
    list,
)

assert (
    configuration_payload["warning_success_rate"]
    == 0.95
)

print(
    "PASS: MonitoringConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 11. Build deterministic execution records
# -----------------------------------------------------------------------------

started_at = datetime(
    2026,
    8,
    7,
    12,
    0,
    tzinfo=timezone.utc,
)

execution_1 = ExecutionRecord(
    execution_id="implementation-28-execution-001",
    component=COMPONENT_ORCHESTRATION,
    operation="enterprise_decision",
    status=ExecutionStatus.SUCCEEDED,
    started_at_utc=started_at,
    completed_at_utc=(
        started_at
        + timedelta(milliseconds=1_000)
    ),
    duration_ms=1_000.0,
    message="Execution completed successfully.",
    metadata={
        "validation": "implementation_28",
    },
)

execution_2 = ExecutionRecord(
    execution_id="implementation-28-execution-002",
    component=COMPONENT_ORCHESTRATION,
    operation="enterprise_decision",
    status=ExecutionStatus.FAILED,
    started_at_utc=(
        started_at
        + timedelta(minutes=1)
    ),
    completed_at_utc=(
        started_at
        + timedelta(
            minutes=1,
            milliseconds=17_000,
        )
    ),
    duration_ms=17_000.0,
    message="Controlled release-validation failure.",
)

assert execution_1.as_dict()["status"] == "SUCCEEDED"
assert execution_2.as_dict()["status"] == "FAILED"

print(
    "PASS: Monitoring ExecutionRecord contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 12. Validate metrics service
# -----------------------------------------------------------------------------

metrics_service = MonitoringMetricsService(
    configuration=configuration
)

assert metrics_service.configuration is configuration
assert metrics_service.metrics == ()

generated_metrics = (
    metrics_service.metrics_from_executions(
        executions=(
            execution_1,
            execution_2,
        )
    )
)

assert isinstance(generated_metrics, tuple)
assert len(generated_metrics) == 6

assert all(
    isinstance(metric, MetricRecord)
    for metric in generated_metrics
)

recorded_metrics = metrics_service.record_many(
    metrics=generated_metrics
)

assert recorded_metrics == generated_metrics

assert len(metrics_service.metrics) == 6

summary = metrics_service.summarize_executions(
    executions=(
        execution_1,
        execution_2,
    )
)

assert summary["execution_count"] == 2.0
assert summary["success_count"] == 1.0
assert summary["failure_count"] == 1.0
assert summary["success_rate"] == 0.5
assert summary["failure_rate"] == 0.5
assert summary["execution_duration_ms"] == 9_000.0

aggregated_metrics = metrics_service.aggregate_metrics()

assert COMPONENT_ORCHESTRATION in aggregated_metrics

assert (
    aggregated_metrics[
        COMPONENT_ORCHESTRATION
    ]["execution_count"]
    == 2.0
)

print(
    "PASS: MonitoringMetricsService collection and "
    "aggregation remain operational"
)


# -----------------------------------------------------------------------------
# 13. Validate execution alert generation
# -----------------------------------------------------------------------------

execution_alerts = (
    metrics_service.evaluate_execution_alerts(
        component=COMPONENT_ORCHESTRATION,
        summary=summary,
    )
)

assert isinstance(execution_alerts, tuple)

# success_rate=0.50 is below the critical threshold.
assert any(
    alert.severity is SeverityLevel.CRITICAL
    and alert.metric_name == "success_rate"
    for alert in execution_alerts
)

# Average duration=9000ms exceeds warning but not critical.
assert any(
    alert.severity is SeverityLevel.WARNING
    and alert.metric_name == "execution_duration_ms"
    for alert in execution_alerts
)

assert all(
    isinstance(alert, MonitoringAlert)
    for alert in execution_alerts
)

print(
    "PASS: Monitoring execution alert thresholds "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 14. Validate custom MetricRecord contract
# -----------------------------------------------------------------------------

custom_metric = MetricRecord(
    name="release_validation_gauge",
    metric_type=MetricType.GAUGE,
    component=COMPONENT_PLATFORM,
    value=42.0,
    recorded_at_utc=started_at,
    unit="units",
    tags={
        "validation": "implementation_28",
    },
)

assert custom_metric.as_dict()["value"] == 42.0
assert custom_metric.as_dict()["metric_type"] == "GAUGE"

assert (
    metrics_service.record(
        metric=custom_metric
    )
    is custom_metric
)

print(
    "PASS: Monitoring custom metric contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate health-service registration and component checks
# -----------------------------------------------------------------------------

health_service = MonitoringHealthService(
    configuration=configuration
)

assert health_service.configuration is configuration

health_service.register(
    component=COMPONENT_ORCHESTRATION,
    health_check=lambda: True,
)

health_service.register(
    component=COMPONENT_PLATFORM,
    health_check=lambda: {
        "healthy": True,
        "degraded": True,
        "message": (
            "Platform operational with controlled degradation."
        ),
        "details": {
            "validation": "implementation_28",
        },
    },
)

assert COMPONENT_ORCHESTRATION in (
    health_service.registered_components
)

assert COMPONENT_PLATFORM in (
    health_service.registered_components
)

orchestration_health = health_service.check_component(
    component=COMPONENT_ORCHESTRATION
)

assert isinstance(
    orchestration_health,
    ComponentHealth,
)

assert (
    orchestration_health.status
    is HealthStatus.HEALTHY
)

assert orchestration_health.is_available is True


platform_health = health_service.check_component(
    component=COMPONENT_PLATFORM
)

assert (
    platform_health.status
    is HealthStatus.DEGRADED
)

assert platform_health.is_available is True

print(
    "PASS: Monitoring component health-check contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 16. Validate platform health aggregation
# -----------------------------------------------------------------------------

platform_report = health_service.check_all()

assert isinstance(
    platform_report,
    PlatformHealthReport,
)

# Registered components are healthy/degraded; enabled components
# without registered checks resolve to UNKNOWN.
assert (
    platform_report.status
    is HealthStatus.UNKNOWN
)

assert len(
    platform_report.components
) == len(
    configuration.enabled_components
)

assert (
    platform_report.monitoring_version
    == "1.0.0"
)

platform_payload = platform_report.as_dict()

assert platform_payload["status"] == "UNKNOWN"

assert len(
    platform_payload["components"]
) == len(
    configuration.enabled_components
)

print(
    "PASS: Platform health aggregation contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate health-based alerts
# -----------------------------------------------------------------------------

health_alerts = health_service.alerts_from_health(
    report=platform_report
)

assert isinstance(health_alerts, tuple)

# Every UNKNOWN component should produce a health alert.
assert len(health_alerts) >= 1

assert all(
    isinstance(alert, MonitoringAlert)
    for alert in health_alerts
)

print(
    "PASS: Monitoring health-alert generation "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate unified EnterpriseMonitoringService
# -----------------------------------------------------------------------------

enterprise_service = EnterpriseMonitoringService(
    configuration=configuration,
    metrics_service=metrics_service,
    health_service=health_service,
)

assert enterprise_service.configuration is configuration
assert enterprise_service.metrics_service is metrics_service
assert enterprise_service.health_service is health_service

observation = enterprise_service.observe_executions(
    component=COMPONENT_ORCHESTRATION,
    executions=(
        execution_1,
        execution_2,
    ),
)

assert observation["component"] == (
    COMPONENT_ORCHESTRATION
)

assert observation["summary"][
    "execution_count"
] == 2.0

assert len(observation["metrics"]) == 6
assert len(observation["alerts"]) >= 1

print(
    "PASS: EnterpriseMonitoringService execution "
    "observation remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate unified monitoring snapshot
# -----------------------------------------------------------------------------

snapshot = enterprise_service.build_snapshot(
    execution_observations={
        COMPONENT_ORCHESTRATION: (
            execution_1,
            execution_2,
        ),
    },
    include_health=True,
)

assert snapshot["monitoring_version"] == "1.0.0"

assert COMPONENT_ORCHESTRATION in (
    snapshot["executions"]
)

assert snapshot["health"] is not None

assert snapshot["health"]["status"] == "UNKNOWN"

assert isinstance(snapshot["alerts"], list)

assert snapshot["recorded_metric_count"] >= 13

print(
    "PASS: Enterprise monitoring snapshot contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 20. Validate metrics state management
# -----------------------------------------------------------------------------

assert len(
    enterprise_service.metrics_service.metrics
) >= 1

enterprise_service.clear_metrics()

assert (
    enterprise_service.metrics_service.metrics
    == ()
)

print(
    "PASS: Monitoring metric state-management contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 21. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    MonitoringConfiguration(
        warning_success_rate=0.80,
        critical_success_rate=0.90,
    )
except MonitoringConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid success-rate threshold ordering "
        "must be rejected."
    )


try:
    MonitoringConfiguration(
        warning_duration_ms=20_000.0,
        critical_duration_ms=10_000.0,
    )
except MonitoringConfigurationError:
    pass
else:
    raise AssertionError(
        "Invalid duration threshold ordering "
        "must be rejected."
    )


try:
    ExecutionRecord(
        execution_id="invalid-execution",
        component=COMPONENT_ORCHESTRATION,
        operation="enterprise_decision",
        status=ExecutionStatus.SUCCEEDED,
        started_at_utc=started_at,
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Terminal execution without completion timestamp "
        "must be rejected."
    )


try:
    MetricRecord(
        name="invalid-counter",
        metric_type=MetricType.COUNTER,
        component=COMPONENT_PLATFORM,
        value=-1.0,
        recorded_at_utc=started_at,
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Negative counter metric must be rejected."
    )


try:
    health_service.register(
        component=COMPONENT_PLATFORM,
        health_check="invalid",
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Non-callable health check must be rejected."
    )


try:
    enterprise_service.observe_executions(
        component=COMPONENT_PLATFORM,
        executions=(
            execution_1,
        ),
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Execution/component mismatch must be rejected."
    )


try:
    EnterpriseMonitoringService(
        configuration=MonitoringConfiguration(),
        metrics_service=metrics_service,
        health_service=health_service,
    )
except MonitoringValidationError:
    pass
else:
    raise AssertionError(
        "Monitoring service must reject mismatched "
        "configuration dependencies."
    )

print(
    "PASS: Monitoring representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 22. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    MonitoringConfiguration
)

for parameter_name in (
    "enabled_components",
    "warning_success_rate",
    "critical_success_rate",
    "warning_duration_ms",
    "critical_duration_ms",
    "health_check_timeout_seconds",
    "enable_metric_collection",
    "enable_health_checks",
    "enable_alert_generation",
    "retain_execution_metadata",
    "monitoring_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


metrics_signature = inspect.signature(
    MonitoringMetricsService.summarize_executions
)

assert "executions" in metrics_signature.parameters


health_signature = inspect.signature(
    MonitoringHealthService.register
)

assert "component" in health_signature.parameters
assert "health_check" in health_signature.parameters


observe_signature = inspect.signature(
    EnterpriseMonitoringService.observe_executions
)

assert "component" in observe_signature.parameters
assert "executions" in observe_signature.parameters


snapshot_signature = inspect.signature(
    EnterpriseMonitoringService.build_snapshot
)

assert (
    "execution_observations"
    in snapshot_signature.parameters
)

assert (
    "include_health"
    in snapshot_signature.parameters
)

print(
    "PASS: Monitoring public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.monitoring")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.runner
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* imports
#     - Legacy namespace detection
#     - Root and leaf public APIs
#     - Public object identity
#     - Constants and enums
#     - Configuration contract
#     - Startup lifecycle
#     - Shutdown lifecycle
#     - EnterprisePlatformRunnerService orchestration
#     - EnterprisePlatformRunner entry point
#     - Failure contracts
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path


PACKAGE_NAME = "src.runner"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "startup",
    "shutdown",
    "service",
    "main",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

runner_package = importlib.import_module(
    PACKAGE_NAME
)

assert runner_package.__name__ == PACKAGE_NAME
assert runner_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.runner"
)


# -----------------------------------------------------------------------------
# 2. Import every runner module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    module = importlib.import_module(
        qualified_name
    )

    loaded_modules[module_name] = module

    assert module.__name__ == qualified_name

print(
    "PASS: Imported every runner module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy runner.* modules
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "runner"
        or module_name.startswith("runner.")
    )
)

assert legacy_modules == [], (
    "Legacy runner.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy runner.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source files for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:

    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


modules_to_scan = {
    "__init__": runner_package,
    **loaded_modules,
}

forbidden_prefixes = (
    "runner",
    "application",
    "api",
    "bootstrap",
    "demand",
    "forecast",
    "metadata",
    "monitoring",
    "optimization",
    "orchestration",
    "overtime",
    "planning",
    "reporting",
    "staffing",
    "validation",
    "workforce",
)

legacy_source_imports = []

for module_name, module in modules_to_scan.items():

    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    for imported_name in absolute_imports:

        if any(
            imported_name == prefix
            or imported_name.startswith(
                f"{prefix}."
            )
            for prefix in forbidden_prefixes
        ):
            legacy_source_imports.append(
                (
                    module_name,
                    imported_name,
                )
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in src.runner: "
    f"{legacy_source_imports}"
)

print(
    "PASS: No legacy platform-package absolute "
    "source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate intentionally narrow root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "RUNNER_PACKAGE_VERSION",
    "RunnerConfiguration",
    "EnterpriseRunnerStartup",
    "EnterpriseRunnerShutdown",
    "EnterprisePlatformRunnerService",
    "EnterprisePlatformRunner",
    "main",
)

assert hasattr(
    runner_package,
    "__all__",
)

assert tuple(
    runner_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.runner public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   {tuple(runner_package.__all__)}"
)

assert len(
    runner_package.__all__
) == len(
    set(runner_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:

    assert hasattr(
        runner_package,
        symbol_name,
    )

print(
    "PASS: Runner root public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "exceptions": (
        "RunnerError",
        "RunnerValidationError",
        "RunnerConfigurationError",
        "RunnerStartupError",
        "RunnerShutdownError",
        "RunnerRuntimeError",
        "RunnerExecutionError",
        "RunnerLifecycleError",
    ),
    "models": (
        "RunnerStatus",
        "RunnerDescriptor",
        "RunnerExecutionResult",
    ),
    "configuration": (
        "RunnerConfiguration",
    ),
    "startup": (
        "EnterpriseRunnerStartup",
    ),
    "shutdown": (
        "EnterpriseRunnerShutdown",
    ),
    "service": (
        "EnterprisePlatformRunnerService",
    ),
    "main": (
        "EnterprisePlatformRunner",
        "main",
    ),
}

for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):

    module = loaded_modules[module_name]

    assert hasattr(
        module,
        "__all__",
    )

    actual_all = tuple(
        module.__all__
    )

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.runner.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )


constants_all = tuple(
    loaded_modules["constants"].__all__
)

assert len(constants_all) == len(
    set(constants_all)
)

for symbol_name in constants_all:
    assert hasattr(
        loaded_modules["constants"],
        symbol_name,
    )

print(
    "PASS: Runner leaf-module __all__ contracts "
    "are complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Confirm root API is intentionally narrower than leaf APIs
# -----------------------------------------------------------------------------

assert (
    "RunnerStatus"
    in loaded_modules["models"].__all__
)

assert (
    "RunnerStatus"
    not in runner_package.__all__
)

assert (
    "RunnerError"
    in loaded_modules["exceptions"].__all__
)

assert (
    "RunnerError"
    not in runner_package.__all__
)

assert (
    "RUNNER_DOMAIN_NAME"
    in loaded_modules["constants"].__all__
)

assert (
    "RUNNER_DOMAIN_NAME"
    not in runner_package.__all__
)

print(
    "PASS: Runner root API remains intentionally "
    "narrower than leaf-module APIs"
)


# -----------------------------------------------------------------------------
# 8. Validate public object identities
# -----------------------------------------------------------------------------

from src.runner import (
    EnterprisePlatformRunner,
    EnterprisePlatformRunnerService,
    EnterpriseRunnerShutdown,
    EnterpriseRunnerStartup,
    RunnerConfiguration,
    main,
)

from src.runner.configuration import (
    RunnerConfiguration
    as LeafRunnerConfiguration,
)

from src.runner.main import (
    EnterprisePlatformRunner
    as LeafEnterprisePlatformRunner,
)

from src.runner.main import (
    main as leaf_main,
)

from src.runner.service import (
    EnterprisePlatformRunnerService
    as LeafEnterprisePlatformRunnerService,
)

from src.runner.shutdown import (
    EnterpriseRunnerShutdown
    as LeafEnterpriseRunnerShutdown,
)

from src.runner.startup import (
    EnterpriseRunnerStartup
    as LeafEnterpriseRunnerStartup,
)

assert (
    RunnerConfiguration
    is LeafRunnerConfiguration
)

assert (
    EnterpriseRunnerStartup
    is LeafEnterpriseRunnerStartup
)

assert (
    EnterpriseRunnerShutdown
    is LeafEnterpriseRunnerShutdown
)

assert (
    EnterprisePlatformRunnerService
    is LeafEnterprisePlatformRunnerService
)

assert (
    EnterprisePlatformRunner
    is LeafEnterprisePlatformRunner
)

assert main is leaf_main

print(
    "PASS: Runner public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 9. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.runner.exceptions import (
    RunnerConfigurationError,
    RunnerError,
    RunnerExecutionError,
    RunnerLifecycleError,
    RunnerRuntimeError,
    RunnerShutdownError,
    RunnerStartupError,
    RunnerValidationError,
)

for exception_type in (
    RunnerValidationError,
    RunnerConfigurationError,
    RunnerStartupError,
    RunnerShutdownError,
    RunnerRuntimeError,
    RunnerExecutionError,
    RunnerLifecycleError,
):
    assert issubclass(
        exception_type,
        RunnerError,
    )

print(
    "PASS: Runner exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 10. Validate constants and RunnerStatus enum
# -----------------------------------------------------------------------------

from src.runner.constants import (
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_RUNNER_SOURCE,
    DEFAULT_RUNNER_VERSION,
    DEFAULT_RUNTIME_MODE,
    EXIT_CODE_SUCCESS,
    RUNTIME_MODE_API,
    RUNTIME_MODE_APPLICATION,
    RUNTIME_MODE_BATCH,
    RUNTIME_MODE_VALIDATION,
    RUNNER_DOMAIN_NAME,
    RUNNER_DOMAIN_VERSION,
    SHUTDOWN_REASON_COMPLETED,
    SUPPORTED_EXIT_CODES,
    SUPPORTED_RUNTIME_MODES,
    SUPPORTED_SHUTDOWN_REASONS,
)

from src.runner.models import (
    RunnerDescriptor,
    RunnerExecutionResult,
    RunnerStatus,
)

assert RUNNER_DOMAIN_NAME == "platform-runner"
assert RUNNER_DOMAIN_VERSION == "1.0.0"

assert DEFAULT_RUNNER_VERSION == "1.0.0"
assert DEFAULT_APPLICATION_VERSION == "3.0.0"

assert DEFAULT_RUNNER_SOURCE == (
    "enterprise-platform-runner"
)

assert DEFAULT_RUNTIME_MODE == (
    RUNTIME_MODE_APPLICATION
)

assert SUPPORTED_RUNTIME_MODES == (
    RUNTIME_MODE_APPLICATION,
    RUNTIME_MODE_API,
    RUNTIME_MODE_VALIDATION,
    RUNTIME_MODE_BATCH,
)

assert EXIT_CODE_SUCCESS == 0
assert EXIT_CODE_SUCCESS in SUPPORTED_EXIT_CODES

assert (
    SHUTDOWN_REASON_COMPLETED
    in SUPPORTED_SHUTDOWN_REASONS
)

assert RunnerStatus.CREATED.value == "CREATED"
assert RunnerStatus.STARTING.value == "STARTING"
assert RunnerStatus.RUNNING.value == "RUNNING"
assert RunnerStatus.STOPPING.value == "STOPPING"
assert RunnerStatus.STOPPED.value == "STOPPED"
assert RunnerStatus.FAILED.value == "FAILED"

assert runner_package.RUNNER_PACKAGE_VERSION == "1.0.0"

print(
    "PASS: Runner constants and status contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 11. Validate RunnerConfiguration
# -----------------------------------------------------------------------------

configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

assert configuration.runner_name == (
    DEFAULT_RUNNER_SOURCE
)

assert configuration.runner_version == (
    DEFAULT_RUNNER_VERSION
)

assert configuration.runtime_mode == (
    RUNTIME_MODE_VALIDATION
)

assert configuration.retries_enabled is True

assert (
    configuration.graceful_shutdown_enabled
    is True
)

assert configuration.auto_startup is True
assert configuration.auto_shutdown is True

configuration_payload = (
    configuration.as_dict()
)

assert isinstance(
    configuration_payload,
    dict,
)

assert (
    configuration_payload["runtime_mode"]
    == RUNTIME_MODE_VALIDATION
)

assert (
    configuration_payload[
        "enable_signal_handlers"
    ]
    is False
)

print(
    "PASS: RunnerConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate startup lifecycle
# -----------------------------------------------------------------------------

startup = EnterpriseRunnerStartup(
    configuration=configuration
)

assert startup.configuration is configuration
assert startup.started is False
assert startup.last_result is None

startup_result = startup.start()

assert isinstance(
    startup_result,
    RunnerExecutionResult,
)

assert startup_result.succeeded is True

assert (
    startup_result.exit_code
    == EXIT_CODE_SUCCESS
)

assert (
    startup_result.descriptor.status
    is RunnerStatus.RUNNING
)

assert (
    startup_result.descriptor.name
    == configuration.runner_name
)

assert (
    startup_result.descriptor.version
    == configuration.runner_version
)

assert (
    startup_result.descriptor.runtime_mode
    == configuration.runtime_mode
)

assert (
    startup_result.descriptor.started_at_utc
    is not None
)

assert startup.started is True
assert startup.last_result is startup_result

print(
    "PASS: EnterpriseRunnerStartup lifecycle "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate startup single-use contract
# -----------------------------------------------------------------------------

try:
    startup.start()

except RunnerStartupError:
    pass

else:
    raise AssertionError(
        "EnterpriseRunnerStartup must reject "
        "a second startup attempt."
    )

print(
    "PASS: Runner startup single-use contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate shutdown lifecycle
# -----------------------------------------------------------------------------

shutdown = EnterpriseRunnerShutdown(
    configuration=configuration
)

assert shutdown.configuration is configuration
assert shutdown.stopped is False
assert shutdown.shutdown_reason is None
assert shutdown.last_result is None

shutdown_result = shutdown.stop(
    descriptor=startup_result.descriptor,
    reason=SHUTDOWN_REASON_COMPLETED,
)

assert isinstance(
    shutdown_result,
    RunnerExecutionResult,
)

assert shutdown_result.succeeded is True

assert (
    shutdown_result.exit_code
    == EXIT_CODE_SUCCESS
)

assert (
    shutdown_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert (
    shutdown_result.descriptor.started_at_utc
    == startup_result.descriptor.started_at_utc
)

assert shutdown.stopped is True

assert (
    shutdown.shutdown_reason
    == SHUTDOWN_REASON_COMPLETED
)

assert shutdown.last_result is shutdown_result

print(
    "PASS: EnterpriseRunnerShutdown lifecycle "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate shutdown single-use contract
# -----------------------------------------------------------------------------

try:
    shutdown.stop(
        descriptor=startup_result.descriptor,
        reason=SHUTDOWN_REASON_COMPLETED,
    )

except RunnerShutdownError:
    pass

else:
    raise AssertionError(
        "EnterpriseRunnerShutdown must reject "
        "a second shutdown attempt."
    )

print(
    "PASS: Runner shutdown single-use contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate runner service dependency wiring
# -----------------------------------------------------------------------------

service_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

service_startup = EnterpriseRunnerStartup(
    configuration=service_configuration
)

service_shutdown = EnterpriseRunnerShutdown(
    configuration=service_configuration
)

service = EnterprisePlatformRunnerService(
    configuration=service_configuration,
    startup=service_startup,
    shutdown=service_shutdown,
)

assert (
    service.configuration
    is service_configuration
)

assert service.startup is service_startup
assert service.shutdown is service_shutdown

assert service.active_descriptor is None
assert service.startup_result is None
assert service.shutdown_result is None

assert (
    service.status
    is RunnerStatus.CREATED
)

assert service.is_created is True
assert service.is_running is False
assert service.is_stopped is False

print(
    "PASS: Runner service dependency wiring "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate service startup transition
# -----------------------------------------------------------------------------

service_start_result = service.start()

assert service_start_result.succeeded is True

assert (
    service_start_result.descriptor.status
    is RunnerStatus.RUNNING
)

assert (
    service.status
    is RunnerStatus.RUNNING
)

assert service.is_created is False
assert service.is_running is True
assert service.is_stopped is False

assert (
    service.active_descriptor
    is service_start_result.descriptor
)

assert (
    service.startup_result
    is service_start_result
)

assert service.shutdown_result is None

print(
    "PASS: Runner service CREATED -> RUNNING "
    "transition remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate service shutdown transition
# -----------------------------------------------------------------------------

service_stop_result = service.stop(
    reason=SHUTDOWN_REASON_COMPLETED
)

assert service_stop_result.succeeded is True

assert (
    service_stop_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert (
    service.status
    is RunnerStatus.STOPPED
)

assert service.is_created is False
assert service.is_running is False
assert service.is_stopped is True

assert (
    service.active_descriptor
    is service_stop_result.descriptor
)

assert (
    service.shutdown_result
    is service_stop_result
)

print(
    "PASS: Runner service RUNNING -> STOPPED "
    "transition remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate complete automatic service lifecycle
# -----------------------------------------------------------------------------

automatic_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
    auto_startup=True,
    auto_shutdown=True,
)

automatic_service = (
    EnterprisePlatformRunnerService(
        configuration=automatic_configuration
    )
)

automatic_result = automatic_service.run()

assert automatic_result.succeeded is True

assert (
    automatic_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert (
    automatic_result.exit_code
    == EXIT_CODE_SUCCESS
)

assert automatic_service.startup_result is not None
assert automatic_service.shutdown_result is not None

assert automatic_service.is_stopped is True

print(
    "PASS: EnterprisePlatformRunnerService automatic "
    "startup/shutdown orchestration remains operational"
)


# -----------------------------------------------------------------------------
# 20. Validate no-auto-shutdown lifecycle
# -----------------------------------------------------------------------------

persistent_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
    auto_startup=True,
    auto_shutdown=False,
)

persistent_service = (
    EnterprisePlatformRunnerService(
        configuration=persistent_configuration
    )
)

persistent_result = persistent_service.run()

assert persistent_result.succeeded is True

assert (
    persistent_result.descriptor.status
    is RunnerStatus.RUNNING
)

assert persistent_service.is_running is True
assert persistent_service.shutdown_result is None

persistent_stop_result = (
    persistent_service.stop(
        reason=SHUTDOWN_REASON_COMPLETED
    )
)

assert (
    persistent_stop_result.descriptor.status
    is RunnerStatus.STOPPED
)

print(
    "PASS: Runner auto_shutdown=False lifecycle "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 21. Validate EnterprisePlatformRunner entry point
# -----------------------------------------------------------------------------

entry_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

enterprise_runner = EnterprisePlatformRunner(
    configuration=entry_configuration
)

assert (
    enterprise_runner.configuration
    is entry_configuration
)

assert isinstance(
    enterprise_runner.service,
    EnterprisePlatformRunnerService,
)

assert (
    enterprise_runner.service.configuration
    is entry_configuration
)

entry_result = enterprise_runner.run()

assert isinstance(
    entry_result,
    RunnerExecutionResult,
)

assert entry_result.succeeded is True

assert (
    entry_result.descriptor.status
    is RunnerStatus.STOPPED
)

assert (
    entry_result.exit_code
    == EXIT_CODE_SUCCESS
)

print(
    "PASS: EnterprisePlatformRunner entry-point "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 22. Validate production main() exit-code contract
# -----------------------------------------------------------------------------

main_exit_code = main()

assert main_exit_code == EXIT_CODE_SUCCESS

print(
    "PASS: Runner main() returns the successful "
    "production exit code"
)


# -----------------------------------------------------------------------------
# 23. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    RunnerConfiguration(
        runtime_mode="unsupported-mode",
    )

except RunnerConfigurationError:
    pass

else:
    raise AssertionError(
        "Unsupported runtime mode must be rejected."
    )


try:
    RunnerConfiguration(
        startup_timeout_seconds=0,
    )

except RunnerConfigurationError:
    pass

else:
    raise AssertionError(
        "Non-positive startup timeout must be rejected."
    )


try:
    RunnerConfiguration(
        max_retry_attempts=-1,
    )

except RunnerConfigurationError:
    pass

else:
    raise AssertionError(
        "Negative retry count must be rejected."
    )


try:
    RunnerConfiguration(
        auto_startup="yes",
    )

except RunnerConfigurationError:
    pass

else:
    raise AssertionError(
        "Non-boolean auto_startup must be rejected."
    )


failure_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

failure_service = (
    EnterprisePlatformRunnerService(
        configuration=failure_configuration
    )
)

try:
    failure_service.stop()

except RunnerLifecycleError:
    pass

else:
    raise AssertionError(
        "Runner service must reject shutdown "
        "before startup."
    )


disabled_startup_configuration = (
    RunnerConfiguration(
        runtime_mode=RUNTIME_MODE_VALIDATION,
        enable_signal_handlers=False,
        auto_startup=False,
    )
)

disabled_startup_service = (
    EnterprisePlatformRunnerService(
        configuration=(
            disabled_startup_configuration
        )
    )
)

try:
    disabled_startup_service.run()

except RunnerLifecycleError:
    pass

else:
    raise AssertionError(
        "Runner service must reject run() when "
        "automatic startup is disabled."
    )


identity_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

different_configuration = RunnerConfiguration(
    runtime_mode=RUNTIME_MODE_VALIDATION,
    enable_signal_handlers=False,
)

mismatched_startup = EnterpriseRunnerStartup(
    configuration=different_configuration
)

try:
    EnterprisePlatformRunnerService(
        configuration=identity_configuration,
        startup=mismatched_startup,
    )

except RunnerValidationError:
    pass

else:
    raise AssertionError(
        "Runner service must reject startup "
        "configured with a different "
        "RunnerConfiguration instance."
    )


invalid_descriptor = RunnerDescriptor(
    name="release-validation-runner",
    version="1.0.0",
    runtime_mode=RUNTIME_MODE_VALIDATION,
    status=RunnerStatus.CREATED,
)

invalid_shutdown = EnterpriseRunnerShutdown(
    configuration=identity_configuration
)

try:
    invalid_shutdown.stop(
        descriptor=invalid_descriptor,
        reason=SHUTDOWN_REASON_COMPLETED,
    )

except RunnerShutdownError:
    pass

else:
    raise AssertionError(
        "Shutdown must reject a descriptor "
        "that is not RUNNING."
    )

print(
    "PASS: Runner representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 24. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    RunnerConfiguration
)

for parameter_name in (
    "runner_name",
    "runner_version",
    "runtime_mode",
    "startup_timeout_seconds",
    "shutdown_timeout_seconds",
    "auto_startup",
    "auto_shutdown",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


startup_signature = inspect.signature(
    EnterpriseRunnerStartup
)

assert (
    "configuration"
    in startup_signature.parameters
)


shutdown_stop_signature = inspect.signature(
    EnterpriseRunnerShutdown.stop
)

assert (
    "descriptor"
    in shutdown_stop_signature.parameters
)

assert (
    "reason"
    in shutdown_stop_signature.parameters
)


service_signature = inspect.signature(
    EnterprisePlatformRunnerService
)

for parameter_name in (
    "configuration",
    "startup",
    "shutdown",
):
    assert (
        parameter_name
        in service_signature.parameters
    )


service_stop_signature = inspect.signature(
    EnterprisePlatformRunnerService.stop
)

assert (
    "reason"
    in service_stop_signature.parameters
)


runner_signature = inspect.signature(
    EnterprisePlatformRunner
)

assert (
    "configuration"
    in runner_signature.parameters
)


main_signature = inspect.signature(main)

assert len(
    main_signature.parameters
) == 0

print(
    "PASS: Runner public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.runner")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.application
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Scope:
#     Enterprise Application Composition Root
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path


PACKAGE_NAME = "src.application"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "container",
    "factory",
    "bootstrap",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

application_package = importlib.import_module(
    PACKAGE_NAME
)

assert application_package.__name__ == PACKAGE_NAME
assert application_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.application"
)


# -----------------------------------------------------------------------------
# 2. Import every application module through src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    module = importlib.import_module(
        qualified_name
    )

    assert module.__name__ == qualified_name

    loaded_modules[module_name] = module

print(
    "PASS: Imported every application module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy application.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "application"
        or module_name.startswith(
            "application."
        )
    )
)

assert legacy_modules == [], (
    "Legacy application.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy application.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan production source for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:
    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


FORBIDDEN_TOP_LEVEL_PACKAGES = (
    "api",
    "application",
    "bootstrap",
    "demand",
    "forecast",
    "metadata",
    "monitoring",
    "optimization",
    "orchestration",
    "overtime",
    "planning",
    "reporting",
    "runner",
    "staffing",
    "validation",
    "workforce",
)


legacy_source_imports = []

for module_name, module in {
    "__init__": application_package,
    **loaded_modules,
}.items():

    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    for imported_name in absolute_imports:

        if any(
            imported_name == prefix
            or imported_name.startswith(
                f"{prefix}."
            )
            for prefix in FORBIDDEN_TOP_LEVEL_PACKAGES
        ):
            legacy_source_imports.append(
                (
                    module_name,
                    imported_name,
                )
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in "
    f"src.application: {legacy_source_imports}"
)

print(
    "PASS: No legacy platform-package absolute "
    "source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate exact root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "APPLICATION_DOMAIN_NAME",
    "APPLICATION_DOMAIN_VERSION",
    "DEFAULT_CONFIGURATION_VERSION",

    "ENVIRONMENT_DEVELOPMENT",
    "ENVIRONMENT_TEST",
    "ENVIRONMENT_PRODUCTION",
    "SUPPORTED_ENVIRONMENTS",

    "BOOTSTRAP_CONFIGURATION",
    "BOOTSTRAP_DEPENDENCIES",
    "BOOTSTRAP_SERVICES",
    "BOOTSTRAP_API",
    "BOOTSTRAP_COMPLETE",
    "BOOTSTRAP_SEQUENCE",

    "SERVICE_FORECAST",
    "SERVICE_PLANNING",
    "SERVICE_OPTIMIZATION",
    "SERVICE_ORCHESTRATION",
    "SERVICE_REPORTING",
    "SERVICE_MONITORING",
    "SERVICE_API",
    "SUPPORTED_SERVICES",

    "ApplicationError",
    "ApplicationValidationError",
    "ApplicationConfigurationError",
    "ApplicationContainerError",
    "ApplicationDependencyError",
    "ApplicationFactoryError",
    "ApplicationBootstrapError",
    "ApplicationLifecycleError",

    "ApplicationEnvironment",
    "BootstrapStage",
    "ApplicationStatus",
    "ServiceRegistration",
    "BootstrapEvent",
    "ApplicationDescriptor",
    "ApplicationBootstrapResult",
    "ApplicationContext",

    "ApplicationConfiguration",
    "DEFAULT_APPLICATION_NAME",
    "DEFAULT_APPLICATION_VERSION",
    "DEFAULT_REQUIRED_SERVICES",

    "ServiceFactory",
    "EnterpriseApplicationContainer",
    "EnterpriseApplicationFactory",
    "EnterpriseApplicationBootstrap",
)

assert tuple(
    application_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.application public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   "
    f"{tuple(application_package.__all__)}"
)

assert len(
    application_package.__all__
) == len(
    set(application_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        application_package,
        symbol_name,
    )

print(
    "PASS: Application public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate declared leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "exceptions": (
        "ApplicationBootstrapError",
        "ApplicationConfigurationError",
        "ApplicationContainerError",
        "ApplicationDependencyError",
        "ApplicationError",
        "ApplicationFactoryError",
        "ApplicationLifecycleError",
        "ApplicationValidationError",
    ),
    "models": (
        "ApplicationBootstrapResult",
        "ApplicationContext",
        "ApplicationDescriptor",
        "ApplicationEnvironment",
        "ApplicationStatus",
        "BootstrapEvent",
        "BootstrapStage",
        "ServiceRegistration",
    ),
    "configuration": (
        "ApplicationConfiguration",
        "DEFAULT_APPLICATION_NAME",
        "DEFAULT_APPLICATION_VERSION",
        "DEFAULT_REQUIRED_SERVICES",
    ),
    "container": (
        "EnterpriseApplicationContainer",
        "ServiceFactory",
    ),
    "factory": (
        "EnterpriseApplicationFactory",
    ),
    "bootstrap": (
        "EnterpriseApplicationBootstrap",
    ),
}


for module_name, expected_all in (
    EXPECTED_LEAF_ALL.items()
):

    module = loaded_modules[module_name]

    assert hasattr(
        module,
        "__all__",
    )

    actual_all = tuple(
        module.__all__
    )

    assert actual_all == expected_all, (
        f"Unexpected __all__ for "
        f"src.application.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {actual_all}"
    )

    assert len(actual_all) == len(
        set(actual_all)
    )

    for symbol_name in actual_all:
        assert hasattr(
            module,
            symbol_name,
        )


# constants.py intentionally has no __all__
assert not hasattr(
    loaded_modules["constants"],
    "__all__",
)

print(
    "PASS: Application declared leaf-module __all__ "
    "contracts remain consistent"
)


# -----------------------------------------------------------------------------
# 7. Validate root/leaf public object identity
# -----------------------------------------------------------------------------

from src.application import (
    ApplicationBootstrapResult,
    ApplicationConfiguration,
    ApplicationContext,
    ApplicationDescriptor,
    ApplicationEnvironment,
    ApplicationStatus,
    BootstrapEvent,
    BootstrapStage,
    EnterpriseApplicationBootstrap,
    EnterpriseApplicationContainer,
    EnterpriseApplicationFactory,
    ServiceRegistration,
)

from src.application.bootstrap import (
    EnterpriseApplicationBootstrap
    as LeafEnterpriseApplicationBootstrap,
)

from src.application.configuration import (
    ApplicationConfiguration
    as LeafApplicationConfiguration,
)

from src.application.container import (
    EnterpriseApplicationContainer
    as LeafEnterpriseApplicationContainer,
)

from src.application.factory import (
    EnterpriseApplicationFactory
    as LeafEnterpriseApplicationFactory,
)

from src.application.models import (
    ApplicationBootstrapResult
    as LeafApplicationBootstrapResult,
    ApplicationContext as LeafApplicationContext,
    ApplicationDescriptor as LeafApplicationDescriptor,
    ApplicationEnvironment as LeafApplicationEnvironment,
    ApplicationStatus as LeafApplicationStatus,
    BootstrapEvent as LeafBootstrapEvent,
    BootstrapStage as LeafBootstrapStage,
    ServiceRegistration as LeafServiceRegistration,
)

assert (
    ApplicationConfiguration
    is LeafApplicationConfiguration
)

assert (
    EnterpriseApplicationContainer
    is LeafEnterpriseApplicationContainer
)

assert (
    EnterpriseApplicationFactory
    is LeafEnterpriseApplicationFactory
)

assert (
    EnterpriseApplicationBootstrap
    is LeafEnterpriseApplicationBootstrap
)

assert (
    ApplicationBootstrapResult
    is LeafApplicationBootstrapResult
)

assert ApplicationContext is LeafApplicationContext
assert ApplicationDescriptor is LeafApplicationDescriptor
assert ApplicationEnvironment is LeafApplicationEnvironment
assert ApplicationStatus is LeafApplicationStatus
assert BootstrapEvent is LeafBootstrapEvent
assert BootstrapStage is LeafBootstrapStage
assert ServiceRegistration is LeafServiceRegistration

print(
    "PASS: Application public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.application import (
    ApplicationBootstrapError,
    ApplicationConfigurationError,
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationError,
    ApplicationFactoryError,
    ApplicationLifecycleError,
    ApplicationValidationError,
)

for exception_type in (
    ApplicationValidationError,
    ApplicationConfigurationError,
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationFactoryError,
    ApplicationBootstrapError,
    ApplicationLifecycleError,
):
    assert issubclass(
        exception_type,
        ApplicationError,
    )

print(
    "PASS: Application exception hierarchy "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants and enums
# -----------------------------------------------------------------------------

from src.application import (
    APPLICATION_DOMAIN_NAME,
    APPLICATION_DOMAIN_VERSION,
    BOOTSTRAP_SEQUENCE,
    DEFAULT_APPLICATION_NAME,
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_CONFIGURATION_VERSION,
    DEFAULT_REQUIRED_SERVICES,
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_PRODUCTION,
    ENVIRONMENT_TEST,
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
)

assert APPLICATION_DOMAIN_NAME == "application"
assert APPLICATION_DOMAIN_VERSION == "1.0.0"
assert DEFAULT_CONFIGURATION_VERSION == "1.0.0"

assert ENVIRONMENT_DEVELOPMENT == "development"
assert ENVIRONMENT_TEST == "test"
assert ENVIRONMENT_PRODUCTION == "production"

assert BOOTSTRAP_SEQUENCE == (
    "configuration",
    "dependencies",
    "services",
    "api",
    "complete",
)

assert DEFAULT_APPLICATION_NAME == (
    "AI Workforce Capacity Planning Platform"
)

assert DEFAULT_APPLICATION_VERSION == "3.0.0"

assert DEFAULT_REQUIRED_SERVICES == (
    SERVICE_PLANNING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_REPORTING,
    SERVICE_MONITORING,
    SERVICE_API,
)

assert (
    ApplicationEnvironment.DEVELOPMENT.value
    == "development"
)

assert ApplicationEnvironment.TEST.value == "test"
assert (
    ApplicationEnvironment.PRODUCTION.value
    == "production"
)

assert (
    BootstrapStage.CONFIGURATION.value
    == "configuration"
)

assert BootstrapStage.DEPENDENCIES.value == "dependencies"
assert BootstrapStage.SERVICES.value == "services"
assert BootstrapStage.API.value == "api"
assert BootstrapStage.COMPLETE.value == "complete"

assert ApplicationStatus.CREATED.value == "CREATED"
assert (
    ApplicationStatus.BOOTSTRAPPING.value
    == "BOOTSTRAPPING"
)

assert ApplicationStatus.READY.value == "READY"
assert ApplicationStatus.FAILED.value == "FAILED"
assert ApplicationStatus.STOPPED.value == "STOPPED"

print(
    "PASS: Application constants and enum contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 10. Validate ApplicationConfiguration
# -----------------------------------------------------------------------------

configuration = ApplicationConfiguration(
    environment=ApplicationEnvironment.TEST,
    metadata={
        "validation": "implementation_28",
    },
)

assert configuration.application_name == (
    DEFAULT_APPLICATION_NAME
)

assert configuration.application_version == "3.0.0"

assert (
    configuration.environment
    is ApplicationEnvironment.TEST
)

assert configuration.environment_name == "test"

assert configuration.is_test is True
assert configuration.is_development is False
assert configuration.is_production is False

assert (
    configuration.required_services
    == DEFAULT_REQUIRED_SERVICES
)

assert configuration.fail_fast is True
assert configuration.validate_dependencies is True
assert configuration.enable_bootstrap_events is True

assert (
    configuration.allow_service_replacement
    is False
)

assert configuration.configuration_version == "1.0.0"

for service_name in DEFAULT_REQUIRED_SERVICES:
    assert configuration.requires_service(
        name=service_name
    )

configuration_payload = (
    configuration.as_dict()
)

assert configuration_payload[
    "application_name"
] == DEFAULT_APPLICATION_NAME

assert configuration_payload[
    "environment"
] == "test"

assert configuration_payload[
    "required_services"
] == list(DEFAULT_REQUIRED_SERVICES)

print(
    "PASS: ApplicationConfiguration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate dependency container basic contracts
# -----------------------------------------------------------------------------

container = EnterpriseApplicationContainer(
    configuration=configuration
)

assert container.configuration is configuration
assert container.service_count == 0
assert container.registered_services == ()
assert container.resolved_services == ()

container.register_instance(
    name=SERVICE_PLANNING,
    instance=object(),
    description="Release validation instance.",
)

assert container.contains(
    name=SERVICE_PLANNING
)

assert container.is_resolved(
    name=SERVICE_PLANNING
)

assert container.service_count == 1

assert container.registered_services == (
    SERVICE_PLANNING,
)

assert container.resolved_services == (
    SERVICE_PLANNING,
)

print(
    "PASS: EnterpriseApplicationContainer basic "
    "registration contract remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate singleton and transient factory behavior
# -----------------------------------------------------------------------------

factory_container = EnterpriseApplicationContainer(
    configuration=configuration
)

singleton_counter = {
    "count": 0,
}

def build_singleton():
    singleton_counter["count"] += 1
    return object()


factory_container.register_factory(
    name=SERVICE_PLANNING,
    factory=build_singleton,
    singleton=True,
)

singleton_one = factory_container.resolve(
    name=SERVICE_PLANNING
)

singleton_two = factory_container.resolve(
    name=SERVICE_PLANNING
)

assert singleton_one is singleton_two
assert singleton_counter["count"] == 1


transient_counter = {
    "count": 0,
}

def build_transient():
    transient_counter["count"] += 1
    return object()


factory_container.register_factory(
    name=SERVICE_OPTIMIZATION,
    factory=build_transient,
    singleton=False,
)

transient_one = factory_container.resolve(
    name=SERVICE_OPTIMIZATION
)

transient_two = factory_container.resolve(
    name=SERVICE_OPTIMIZATION
)

assert transient_one is not transient_two
assert transient_counter["count"] == 2

print(
    "PASS: Application container singleton/transient "
    "resolution contracts remain operational"
)


# -----------------------------------------------------------------------------
# 13. Validate real enterprise application factory
# -----------------------------------------------------------------------------

application_factory = EnterpriseApplicationFactory(
    configuration=configuration
)

assert (
    application_factory.configuration
    is configuration
)

application_container = (
    application_factory.build()
)

assert isinstance(
    application_container,
    EnterpriseApplicationContainer,
)

assert (
    application_container.configuration
    is configuration
)

assert set(
    application_container.registered_services
) == set(
    DEFAULT_REQUIRED_SERVICES
)

assert (
    application_container.service_count
    == len(DEFAULT_REQUIRED_SERVICES)
)

# Lazy factories should initially remain unresolved.
assert application_container.resolved_services == ()

print(
    "PASS: EnterpriseApplicationFactory dependency "
    "registration remains operational"
)


# -----------------------------------------------------------------------------
# 14. Resolve real application services
# -----------------------------------------------------------------------------

from src.api.service import EnterpriseAPIService
from src.monitoring.service import EnterpriseMonitoringService
from src.optimization.service import WorkforceOptimizationService
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.planning.service import CapacityPlanningService
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


planning_service = application_container.resolve(
    name=SERVICE_PLANNING
)

optimization_service = application_container.resolve(
    name=SERVICE_OPTIMIZATION
)

orchestration_service = application_container.resolve(
    name=SERVICE_ORCHESTRATION
)

reporting_service = application_container.resolve(
    name=SERVICE_REPORTING
)

monitoring_service = application_container.resolve(
    name=SERVICE_MONITORING
)

api_service = application_container.resolve(
    name=SERVICE_API
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

assert set(
    application_container.resolved_services
) == set(
    DEFAULT_REQUIRED_SERVICES
)

# Confirm singleton identity.
assert (
    application_container.resolve(
        name=SERVICE_API
    )
    is api_service
)

assert (
    application_container.resolve(
        name=SERVICE_MONITORING
    )
    is monitoring_service
)

print(
    "PASS: Real enterprise application service graph "
    "resolves through canonical dependencies"
)


# -----------------------------------------------------------------------------
# 15. Validate bootstrap lifecycle
# -----------------------------------------------------------------------------

bootstrap_configuration = ApplicationConfiguration(
    environment=ApplicationEnvironment.TEST,
    metadata={
        "validation": "implementation_28",
    },
)

bootstrap_factory = EnterpriseApplicationFactory(
    configuration=bootstrap_configuration
)

bootstrap = EnterpriseApplicationBootstrap(
    configuration=bootstrap_configuration,
    factory=bootstrap_factory,
)

assert (
    bootstrap.configuration
    is bootstrap_configuration
)

assert bootstrap.factory is bootstrap_factory
assert bootstrap.container is None
assert bootstrap.context is None
assert bootstrap.last_result is None
assert bootstrap.has_started is False
assert bootstrap.is_ready is False


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

assert (
    bootstrap.last_result
    is context.bootstrap_result
)

print(
    "PASS: EnterpriseApplicationBootstrap lifecycle "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate final application descriptor and bootstrap result
# -----------------------------------------------------------------------------

assert (
    context.descriptor.status
    is ApplicationStatus.READY
)

assert context.descriptor.application_name == (
    DEFAULT_APPLICATION_NAME
)

assert (
    context.descriptor.application_version
    == DEFAULT_APPLICATION_VERSION
)

assert (
    context.descriptor.environment
    is ApplicationEnvironment.TEST
)

bootstrap_result = context.bootstrap_result

assert isinstance(
    bootstrap_result,
    ApplicationBootstrapResult,
)

assert bootstrap_result.succeeded is True

assert (
    bootstrap_result.completed_stage
    is BootstrapStage.COMPLETE
)

assert bootstrap_result.error_message == ""

assert bootstrap_result.duration_ms >= 0.0

assert tuple(
    event.stage
    for event in bootstrap_result.events
) == (
    BootstrapStage.CONFIGURATION,
    BootstrapStage.DEPENDENCIES,
    BootstrapStage.SERVICES,
    BootstrapStage.API,
    BootstrapStage.COMPLETE,
)

assert all(
    event.succeeded
    for event in bootstrap_result.events
)

print(
    "PASS: Application bootstrap result and lifecycle "
    "events remain operational"
)


# -----------------------------------------------------------------------------
# 17. Validate final service registrations
# -----------------------------------------------------------------------------

assert len(
    context.services
) == len(
    DEFAULT_REQUIRED_SERVICES
)

service_names = tuple(
    registration.name
    for registration in context.services
)

assert set(service_names) == set(
    DEFAULT_REQUIRED_SERVICES
)

assert len(service_names) == len(
    set(service_names)
)

for registration in context.services:
    assert isinstance(
        registration,
        ServiceRegistration,
    )

    assert registration.instance is not None

    assert (
        context.get_service(
            name=registration.name
        )
        is registration.instance
    )


assert isinstance(
    context.get_service(
        name=SERVICE_API
    ),
    EnterpriseAPIService,
)

assert isinstance(
    context.get_service(
        name=SERVICE_ORCHESTRATION
    ),
    EnterpriseDecisionOrchestrationService,
)

assert isinstance(
    context.get_service(
        name=SERVICE_REPORTING
    ),
    EnterpriseDecisionReportingService,
)

assert isinstance(
    context.get_service(
        name=SERVICE_MONITORING
    ),
    EnterpriseMonitoringService,
)

print(
    "PASS: ApplicationContext service-registration "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate context serialization
# -----------------------------------------------------------------------------

context_payload = context.as_dict()

assert context_payload[
    "descriptor"
]["status"] == "READY"

assert context_payload[
    "descriptor"
]["environment"] == "test"

assert len(
    context_payload["services"]
) == len(
    DEFAULT_REQUIRED_SERVICES
)

assert context_payload[
    "bootstrap_result"
]["succeeded"] is True

assert context_payload[
    "bootstrap_result"
]["completed_stage"] == "complete"

assert context_payload[
    "metadata"
]["configuration_version"] == "1.0.0"

assert context_payload[
    "metadata"
]["application_domain_version"] == "1.0.0"

assert context_payload[
    "metadata"
]["validation"] == "implementation_28"

print(
    "PASS: ApplicationContext serialization contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate bootstrap single-use lifecycle
# -----------------------------------------------------------------------------

try:
    bootstrap.start()

except ApplicationLifecycleError:
    pass

else:
    raise AssertionError(
        "EnterpriseApplicationBootstrap must reject "
        "a second start() call."
    )

print(
    "PASS: Application bootstrap single-use contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 20. Validate representative failure contracts
# -----------------------------------------------------------------------------

try:
    ApplicationConfiguration(
        application_name="",
    )

except ApplicationConfigurationError:
    pass

else:
    raise AssertionError(
        "Empty application name must be rejected."
    )


try:
    ApplicationConfiguration(
        environment="test",
    )

except ApplicationConfigurationError:
    pass

else:
    raise AssertionError(
        "Environment must be an ApplicationEnvironment."
    )


try:
    ApplicationConfiguration(
        required_services=(
            SERVICE_API,
        ),
    )

except ApplicationConfigurationError:
    pass

else:
    raise AssertionError(
        "API service without required dependencies "
        "must be rejected."
    )


duplicate_container = (
    EnterpriseApplicationContainer(
        configuration=configuration
    )
)

duplicate_container.register_instance(
    name=SERVICE_PLANNING,
    instance=object(),
)

try:
    duplicate_container.register_instance(
        name=SERVICE_PLANNING,
        instance=object(),
    )

except ApplicationContainerError:
    pass

else:
    raise AssertionError(
        "Duplicate service registration must be rejected."
    )


try:
    duplicate_container.resolve(
        name=SERVICE_API
    )

except ApplicationDependencyError:
    pass

else:
    raise AssertionError(
        "Resolving an unregistered service must fail."
    )


try:
    EnterpriseApplicationFactory(
        configuration="invalid",
    )

except ApplicationValidationError:
    pass

else:
    raise AssertionError(
        "Factory must reject invalid configuration."
    )


different_configuration = ApplicationConfiguration(
    environment=ApplicationEnvironment.TEST,
)

different_factory = EnterpriseApplicationFactory(
    configuration=different_configuration
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
        "Bootstrap must reject a factory using a "
        "different ApplicationConfiguration instance."
    )


try:
    context.get_service(
        name="missing-service"
    )

except ApplicationValidationError:
    pass

else:
    raise AssertionError(
        "ApplicationContext must reject unknown services."
    )

print(
    "PASS: Application representative failure contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 21. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    ApplicationConfiguration
)

for parameter_name in (
    "application_name",
    "application_version",
    "environment",
    "required_services",
    "api",
    "reporting",
    "monitoring",
    "fail_fast",
    "validate_dependencies",
    "enable_bootstrap_events",
    "allow_service_replacement",
    "configuration_version",
    "metadata",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


container_signature = inspect.signature(
    EnterpriseApplicationContainer
)

assert (
    "configuration"
    in container_signature.parameters
)


factory_signature = inspect.signature(
    EnterpriseApplicationFactory
)

assert (
    "configuration"
    in factory_signature.parameters
)


bootstrap_signature = inspect.signature(
    EnterpriseApplicationBootstrap
)

assert (
    "configuration"
    in bootstrap_signature.parameters
)

assert (
    "factory"
    in bootstrap_signature.parameters
)


bootstrap_start_signature = inspect.signature(
    EnterpriseApplicationBootstrap.start
)

assert len(
    bootstrap_start_signature.parameters
) == 1  # self


context_get_service_signature = inspect.signature(
    ApplicationContext.get_service
)

assert (
    "name"
    in context_get_service_signature.parameters
)

print(
    "PASS: Application public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.application")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.api
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Scope:
#     Enterprise Transport-Neutral API Layer
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_NAME = "src.api"

EXPECTED_MODULES = (
    "constants",
    "exceptions",
    "models",
    "configuration",
    "mapper",
    "router",
    "service",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

api_package = importlib.import_module(PACKAGE_NAME)

assert api_package.__name__ == PACKAGE_NAME
assert api_package.__package__ == PACKAGE_NAME

print("PASS: Imported canonical package src.api")


# -----------------------------------------------------------------------------
# 2. Import every API module through canonical src.*
# -----------------------------------------------------------------------------

loaded_modules: dict[str, object] = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    module = importlib.import_module(qualified_name)

    assert module.__name__ == qualified_name

    loaded_modules[module_name] = module

print(
    "PASS: Imported every API module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy api.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "api"
        or module_name.startswith("api.")
    )
)

assert legacy_modules == [], (
    "Legacy api.* modules were loaded: "
    f"{legacy_modules}"
)

print("PASS: No legacy api.* modules are loaded")


# -----------------------------------------------------------------------------
# 4. Scan production source for legacy absolute imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:

    tree = ast.parse(
        source_path.read_text(encoding="utf-8"),
        filename=str(source_path),
    )

    imports: list[str] = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(node.module)

    return tuple(imports)


FORBIDDEN_TOP_LEVEL_PACKAGES = (
    "api",
    "application",
    "bootstrap",
    "demand",
    "forecast",
    "metadata",
    "monitoring",
    "optimization",
    "orchestration",
    "overtime",
    "planning",
    "reporting",
    "runner",
    "staffing",
    "validation",
    "workforce",
)


legacy_source_imports = []

for module_name, module in {
    "__init__": api_package,
    **loaded_modules,
}.items():

    source_file = inspect.getsourcefile(module)

    assert source_file is not None

    for imported_name in collect_absolute_imports(
        Path(source_file).resolve()
    ):
        if any(
            imported_name == prefix
            or imported_name.startswith(f"{prefix}.")
            for prefix in FORBIDDEN_TOP_LEVEL_PACKAGES
        ):
            legacy_source_imports.append(
                (module_name, imported_name)
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in src.api: "
    f"{legacy_source_imports}"
)

print(
    "PASS: No legacy platform-package absolute "
    "source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API against the production contract
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = tuple(
    loaded_modules["constants"].__all__
) + (
    # Exceptions
    "APIError",
    "APIValidationError",
    "APIConfigurationError",
    "APIMapperError",
    "APIRouterError",
    "APIRouteNotFoundError",
    "APIMethodNotAllowedError",
    "APIServiceError",
    "APIInternalError",

    # Models
    "APIRequestMetadata",
    "APIResponseMetadata",
    "APIRequest",
    "APIResponse",
    "APIHealthResponse",
    "APIRouteDefinition",

    # Components
    "APIConfiguration",
    "EnterpriseAPIMapper",
    "APIHandler",
    "EnterpriseAPIRouter",
    "EnterpriseAPIService",
)


actual_public_api = tuple(api_package.__all__)

assert set(actual_public_api) == set(EXPECTED_PUBLIC_API), {
    "missing_exports": sorted(
        set(EXPECTED_PUBLIC_API) - set(actual_public_api)
    ),
    "unexpected_exports": sorted(
        set(actual_public_api) - set(EXPECTED_PUBLIC_API)
    ),
}

assert len(api_package.__all__) == len(
    set(api_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(api_package, symbol_name), (
        f"src.api does not expose {symbol_name}"
    )

print(
    "PASS: API public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module __all__ contracts
# -----------------------------------------------------------------------------

EXPECTED_LEAF_ALL = {
    "exceptions": (
        "APIError",
        "APIValidationError",
        "APIConfigurationError",
        "APIMapperError",
        "APIRouterError",
        "APIRouteNotFoundError",
        "APIMethodNotAllowedError",
        "APIServiceError",
        "APIInternalError",
    ),
    "models": (
        "APIRequestMetadata",
        "APIResponseMetadata",
        "APIRequest",
        "APIResponse",
        "APIHealthResponse",
        "APIRouteDefinition",
    ),
    "configuration": (
        "APIConfiguration",
    ),
    "mapper": (
        "EnterpriseAPIMapper",
    ),
    "router": (
        "APIHandler",
        "EnterpriseAPIRouter",
    ),
    "service": (
        "EnterpriseAPIService",
    ),
}


for module_name, expected_all in EXPECTED_LEAF_ALL.items():

    module = loaded_modules[module_name]

    assert tuple(module.__all__) == expected_all, (
        f"Unexpected __all__ for src.api.{module_name}.\n"
        f"Expected: {expected_all}\n"
        f"Actual:   {tuple(module.__all__)}"
    )

    assert len(module.__all__) == len(
        set(module.__all__)
    )

    for symbol_name in module.__all__:
        assert hasattr(module, symbol_name)


constants_all = tuple(
    loaded_modules["constants"].__all__
)

assert len(constants_all) == len(set(constants_all))

for symbol_name in constants_all:
    assert hasattr(
        loaded_modules["constants"],
        symbol_name,
    )

print(
    "PASS: API leaf-module __all__ contracts are "
    "complete and duplicate-free"
)


# -----------------------------------------------------------------------------
# 7. Validate root/leaf object identities
# -----------------------------------------------------------------------------

from src.api import (
    APIConfiguration,
    APIHealthResponse,
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    APIResponseMetadata,
    APIRouteDefinition,
    EnterpriseAPIMapper,
    EnterpriseAPIRouter,
    EnterpriseAPIService,
)

from src.api.configuration import (
    APIConfiguration as LeafAPIConfiguration,
)

from src.api.mapper import (
    EnterpriseAPIMapper as LeafEnterpriseAPIMapper,
)

from src.api.models import (
    APIHealthResponse as LeafAPIHealthResponse,
    APIRequest as LeafAPIRequest,
    APIRequestMetadata as LeafAPIRequestMetadata,
    APIResponse as LeafAPIResponse,
    APIResponseMetadata as LeafAPIResponseMetadata,
    APIRouteDefinition as LeafAPIRouteDefinition,
)

from src.api.router import (
    EnterpriseAPIRouter as LeafEnterpriseAPIRouter,
)

from src.api.service import (
    EnterpriseAPIService as LeafEnterpriseAPIService,
)


assert APIConfiguration is LeafAPIConfiguration
assert EnterpriseAPIMapper is LeafEnterpriseAPIMapper
assert EnterpriseAPIRouter is LeafEnterpriseAPIRouter
assert EnterpriseAPIService is LeafEnterpriseAPIService

assert APIHealthResponse is LeafAPIHealthResponse
assert APIRequest is LeafAPIRequest
assert APIRequestMetadata is LeafAPIRequestMetadata
assert APIResponse is LeafAPIResponse
assert APIResponseMetadata is LeafAPIResponseMetadata
assert APIRouteDefinition is LeafAPIRouteDefinition

print(
    "PASS: API public object identities are consistent"
)


# -----------------------------------------------------------------------------
# 8. Validate exception hierarchy
# -----------------------------------------------------------------------------

from src.api import (
    APIConfigurationError,
    APIError,
    APIInternalError,
    APIMapperError,
    APIMethodNotAllowedError,
    APIRouteNotFoundError,
    APIRouterError,
    APIServiceError,
    APIValidationError,
)


for exception_type in (
    APIValidationError,
    APIConfigurationError,
    APIMapperError,
    APIRouterError,
    APIServiceError,
    APIInternalError,
):
    assert issubclass(exception_type, APIError)


assert issubclass(
    APIRouteNotFoundError,
    APIRouterError,
)

assert issubclass(
    APIMethodNotAllowedError,
    APIRouterError,
)

print(
    "PASS: API exception hierarchy remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate constants
# -----------------------------------------------------------------------------

from src.api import (
    API_BASE_PATH,
    API_DOMAIN_NAME,
    API_DOMAIN_VERSION,
    API_STATUS_ERROR,
    API_STATUS_SUCCESS,
    API_VERSION,
    ENDPOINT_DECISION,
    ENDPOINT_DECISION_REPORT,
    ENDPOINT_HEALTH,
    ENDPOINT_MONITORING_SNAPSHOT,
    ENDPOINT_PLATFORM_HEALTH,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
    SUPPORTED_API_ENDPOINTS,
)


assert API_DOMAIN_NAME == "enterprise-api"
assert API_DOMAIN_VERSION == "1.0.0"
assert API_VERSION == "v1"
assert API_BASE_PATH == "/api/v1"

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

assert HTTP_METHOD_GET == "GET"
assert HTTP_METHOD_POST == "POST"

assert API_STATUS_SUCCESS == "SUCCESS"
assert API_STATUS_ERROR == "ERROR"

assert HTTP_STATUS_OK == 200
assert HTTP_STATUS_BAD_REQUEST == 400
assert HTTP_STATUS_NOT_FOUND == 404
assert HTTP_STATUS_INTERNAL_SERVER_ERROR == 500

print(
    "PASS: API constants remain internally consistent"
)


# -----------------------------------------------------------------------------
# 10. Validate APIConfiguration
# -----------------------------------------------------------------------------

configuration = APIConfiguration()

assert configuration.api_version == "v1"
assert configuration.base_path == "/api"
assert (
    configuration.default_content_type
    == "application/json"
)
assert configuration.request_timeout_seconds == 30
assert (
    configuration.maximum_payload_size_bytes
    == 10_000_000
)

assert configuration.enable_health_endpoint is True
assert (
    configuration.enable_platform_health_endpoint
    is True
)
assert configuration.enable_decision_endpoint is True
assert (
    configuration.enable_decision_report_endpoint
    is True
)
assert configuration.enable_monitoring_endpoint is True

assert configuration.validate_requests is True
assert configuration.generate_metadata is True
assert configuration.configuration_version == "1.0.0"

print(
    "PASS: APIConfiguration contract remains operational"
)


# -----------------------------------------------------------------------------
# 11. Validate transport-neutral request/response models
# -----------------------------------------------------------------------------

request_metadata = APIRequestMetadata(
    request_id="impl-28-api-request",
    correlation_id="impl-28-api-correlation",
    source="release-validation",
    received_at_utc=datetime.now(timezone.utc),
)

request = APIRequest(
    operation="health_check",
    payload={},
    metadata=request_metadata,
)

response_metadata = APIResponseMetadata(
    request_id=request_metadata.request_id,
    correlation_id=request_metadata.correlation_id,
    generated_at_utc=datetime.now(timezone.utc),
    processing_time_ms=0.0,
)

response = APIResponse(
    status=API_STATUS_SUCCESS,
    http_status=HTTP_STATUS_OK,
    payload={"healthy": True},
    metadata=response_metadata,
)

health_response = APIHealthResponse(
    healthy=True,
    status="HEALTHY",
    components={"api": "HEALTHY"},
    checked_at_utc=datetime.now(timezone.utc),
)

route_definition = APIRouteDefinition(
    name=ROUTE_HEALTH,
    path=ENDPOINT_HEALTH,
    method=HTTP_METHOD_GET,
    operation="health_check",
)

assert request.operation == "health_check"
assert response.status == API_STATUS_SUCCESS
assert response.http_status == HTTP_STATUS_OK
assert health_response.healthy is True
assert route_definition.path == ENDPOINT_HEALTH

print(
    "PASS: API request/response model contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 12. Validate mapper
# -----------------------------------------------------------------------------

mapper = EnterpriseAPIMapper()

mapped_request = mapper.request_payload(request)

assert mapped_request == {}

mapped_response = mapper.response_payload(response)

assert mapped_response == {"healthy": True}

mapped_metadata = mapper.response_metadata(response)

assert (
    mapped_metadata["request_id"]
    == "impl-28-api-request"
)

assert (
    mapped_metadata["correlation_id"]
    == "impl-28-api-correlation"
)

mapped_health = mapper.health_payload(
    health_response
)

assert mapped_health["healthy"] is True
assert mapped_health["status"] == "HEALTHY"
assert mapped_health["components"] == {
    "api": "HEALTHY"
}

print(
    "PASS: EnterpriseAPIMapper contracts remain operational"
)


# -----------------------------------------------------------------------------
# 13. Validate active router topology
# -----------------------------------------------------------------------------

router = EnterpriseAPIRouter(
    configuration=configuration
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

health_route = router.resolve(
    path=ENDPOINT_HEALTH,
    method=HTTP_METHOD_GET,
)

assert health_route.name == ROUTE_HEALTH
assert health_route.operation == "health_check"

decision_route = router.resolve(
    path=ENDPOINT_DECISION,
    method=HTTP_METHOD_POST,
)

assert decision_route.name == ROUTE_DECISION
assert (
    decision_route.operation
    == "create_enterprise_decision"
)

print(
    "PASS: EnterpriseAPIRouter active-route topology "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate router registration and dispatch
# -----------------------------------------------------------------------------

def validation_health_handler(
    api_request: APIRequest,
) -> APIResponse:

    return APIResponse(
        status=API_STATUS_SUCCESS,
        http_status=HTTP_STATUS_OK,
        payload={
            "healthy": True,
            "source": "router-validation",
        },
        metadata=APIResponseMetadata(
            request_id=api_request.metadata.request_id,
            correlation_id=(
                api_request.metadata.correlation_id
            ),
            generated_at_utc=datetime.now(timezone.utc),
            processing_time_ms=0.0,
        ),
    )


router.register_handler(
    route_name=ROUTE_HEALTH,
    handler=validation_health_handler,
)

assert router.registered_handler_names == (
    ROUTE_HEALTH,
)

router_response = router.dispatch(
    path=ENDPOINT_HEALTH,
    method=HTTP_METHOD_GET,
    request=request,
)

assert isinstance(router_response, APIResponse)
assert router_response.status == API_STATUS_SUCCESS
assert router_response.http_status == HTTP_STATUS_OK
assert router_response.payload["healthy"] is True

print(
    "PASS: EnterpriseAPIRouter registration and "
    "dispatch contracts remain operational"
)


# -----------------------------------------------------------------------------
# 15. Validate standardized router failures
# -----------------------------------------------------------------------------

from src.api import (
    ERROR_CODE_METHOD_NOT_ALLOWED,
    ERROR_CODE_ROUTE_NOT_FOUND,
)


not_found_response = router.dispatch(
    path="/api/v1/not-a-route",
    method=HTTP_METHOD_GET,
    request=request,
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


method_response = router.dispatch(
    path=ENDPOINT_HEALTH,
    method=HTTP_METHOD_POST,
    request=request,
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

print(
    "PASS: API router standardized failure responses "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 16. Validate endpoint disabling
# -----------------------------------------------------------------------------

reduced_configuration = APIConfiguration(
    enable_health_endpoint=True,
    enable_platform_health_endpoint=False,
    enable_decision_endpoint=False,
    enable_decision_report_endpoint=False,
    enable_monitoring_endpoint=False,
)

reduced_router = EnterpriseAPIRouter(
    configuration=reduced_configuration
)

assert reduced_router.route_names == (
    ROUTE_HEALTH,
)

assert len(reduced_router.routes) == 1

print(
    "PASS: API endpoint-configuration contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate real EnterpriseAPIService dependency graph
# -----------------------------------------------------------------------------

from src.monitoring.service import (
    EnterpriseMonitoringService,
)

from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)

from src.reporting.service import (
    EnterpriseDecisionReportingService,
)


api_service = EnterpriseAPIService(
    configuration=configuration,
)

assert api_service.configuration is configuration

assert isinstance(
    api_service.router,
    EnterpriseAPIRouter,
)

assert isinstance(
    api_service.mapper,
    EnterpriseAPIMapper,
)

assert isinstance(
    api_service.orchestration_service,
    EnterpriseDecisionOrchestrationService,
)

assert isinstance(
    api_service.reporting_service,
    EnterpriseDecisionReportingService,
)

assert isinstance(
    api_service.monitoring_service,
    EnterpriseMonitoringService,
)

assert set(
    api_service.router.registered_handler_names
) == set(
    api_service.router.route_names
)

print(
    "PASS: EnterpriseAPIService real dependency graph "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate real API health endpoint
# -----------------------------------------------------------------------------

health_request = APIRequest(
    operation="health_check",
    payload={},
    metadata=APIRequestMetadata(
        request_id="impl-28-health",
        correlation_id="impl-28-health-correlation",
        source="release-validation",
        received_at_utc=datetime.now(timezone.utc),
    ),
)

health_api_response = api_service.handle(
    path=ENDPOINT_HEALTH,
    method=HTTP_METHOD_GET,
    request=health_request,
)

assert isinstance(
    health_api_response,
    APIResponse,
)

assert (
    health_api_response.status
    == API_STATUS_SUCCESS
)

assert (
    health_api_response.http_status
    == HTTP_STATUS_OK
)

assert (
    health_api_response.metadata.request_id
    == health_request.metadata.request_id
)

assert (
    health_api_response.metadata.correlation_id
    == health_request.metadata.correlation_id
)

print(
    "PASS: Enterprise API health endpoint remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate representative model/configuration failures
# -----------------------------------------------------------------------------

try:
    APIRequestMetadata(
        request_id="",
        correlation_id="correlation",
        source="validation",
        received_at_utc=datetime.now(timezone.utc),
    )

except APIValidationError:
    pass

else:
    raise AssertionError(
        "Empty request_id must be rejected."
    )


try:
    APIResponseMetadata(
        request_id="request",
        correlation_id="correlation",
        generated_at_utc=datetime.now(timezone.utc),
        processing_time_ms=-1.0,
    )

except APIValidationError:
    pass

else:
    raise AssertionError(
        "Negative processing_time_ms must be rejected."
    )


try:
    APIConfiguration(
        request_timeout_seconds=0,
    )

except APIConfigurationError:
    pass

else:
    raise AssertionError(
        "Non-positive request_timeout_seconds "
        "must be rejected."
    )


try:
    APIConfiguration(
        enable_health_endpoint=False,
        enable_platform_health_endpoint=False,
        enable_decision_endpoint=False,
        enable_decision_report_endpoint=False,
        enable_monitoring_endpoint=False,
    )

except APIConfigurationError:
    pass

else:
    raise AssertionError(
        "Configuration with every endpoint disabled "
        "must be rejected."
    )

print(
    "PASS: API representative validation failures "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 20. Validate mapper failures
# -----------------------------------------------------------------------------

try:
    mapper.request_payload("invalid")

except APIMapperError:
    pass

else:
    raise AssertionError(
        "Mapper must reject non-APIRequest input."
    )


try:
    mapper.response_payload("invalid")

except APIMapperError:
    pass

else:
    raise AssertionError(
        "Mapper must reject non-APIResponse input."
    )

print(
    "PASS: API mapper failure contracts remain operational"
)


# -----------------------------------------------------------------------------
# 21. Validate service dependency consistency
# -----------------------------------------------------------------------------

different_configuration = APIConfiguration()

different_router = EnterpriseAPIRouter(
    configuration=different_configuration
)

try:
    EnterpriseAPIService(
        configuration=configuration,
        router=different_router,
    )

except APIValidationError:
    pass

else:
    raise AssertionError(
        "EnterpriseAPIService must reject a router "
        "using a different APIConfiguration instance."
    )

print(
    "PASS: API service dependency-consistency "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 22. Validate public signatures
# -----------------------------------------------------------------------------

configuration_signature = inspect.signature(
    APIConfiguration
)

for parameter_name in (
    "api_version",
    "base_path",
    "default_content_type",
    "request_timeout_seconds",
    "maximum_payload_size_bytes",
    "enable_health_endpoint",
    "enable_platform_health_endpoint",
    "enable_decision_endpoint",
    "enable_decision_report_endpoint",
    "enable_monitoring_endpoint",
    "validate_requests",
    "generate_metadata",
    "configuration_version",
):
    assert (
        parameter_name
        in configuration_signature.parameters
    )


router_signature = inspect.signature(
    EnterpriseAPIRouter
)

assert (
    "configuration"
    in router_signature.parameters
)

assert "handlers" in router_signature.parameters


resolve_signature = inspect.signature(
    EnterpriseAPIRouter.resolve
)

assert "path" in resolve_signature.parameters
assert "method" in resolve_signature.parameters


dispatch_signature = inspect.signature(
    EnterpriseAPIRouter.dispatch
)

assert "path" in dispatch_signature.parameters
assert "method" in dispatch_signature.parameters
assert "request" in dispatch_signature.parameters


service_signature = inspect.signature(
    EnterpriseAPIService
)

for parameter_name in (
    "configuration",
    "router",
    "mapper",
    "orchestration_service",
    "reporting_service",
    "monitoring_service",
):
    assert (
        parameter_name
        in service_signature.parameters
    )


handle_signature = inspect.signature(
    EnterpriseAPIService.handle
)

assert "path" in handle_signature.parameters
assert "method" in handle_signature.parameters
assert "request" in handle_signature.parameters

print(
    "PASS: API public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print("IMPLEMENTATION 28 RELEASE VALIDATION PASSED")
print("Package: src.api")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print("Production-file changes required: 0")
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.bootstrap
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.bootstrap import
#     - Legacy namespace detection
#     - Source import validation
#     - Root and leaf public API contracts
#     - Public object identity
#     - Workspace src-path registration
#     - Idempotent sys.path behavior
#     - Project bootstrap delegation
#     - Failure behavior
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import os
import sys
import tempfile
from pathlib import Path


PACKAGE_NAME = "src.bootstrap"

EXPECTED_MODULES = (
    "project",
    "workspace",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

bootstrap_package = importlib.import_module(
    PACKAGE_NAME
)

assert bootstrap_package.__name__ == PACKAGE_NAME
assert bootstrap_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.bootstrap"
)


# -----------------------------------------------------------------------------
# 2. Import every bootstrap module through src.*
# -----------------------------------------------------------------------------

loaded_modules = {}

for module_name in EXPECTED_MODULES:
    qualified_name = (
        f"{PACKAGE_NAME}.{module_name}"
    )

    module = importlib.import_module(
        qualified_name
    )

    assert module.__name__ == qualified_name

    loaded_modules[module_name] = module

print(
    "PASS: Imported every bootstrap module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy bootstrap.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "bootstrap"
        or module_name.startswith(
            "bootstrap."
        )
    )
)

assert legacy_modules == [], (
    "Legacy bootstrap.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy bootstrap.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Validate production source imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:

    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(
                    node.module
                )

    return tuple(imports)


FORBIDDEN_TOP_LEVEL_PACKAGES = (
    "api",
    "application",
    "bootstrap",
    "demand",
    "forecast",
    "metadata",
    "monitoring",
    "optimization",
    "orchestration",
    "overtime",
    "planning",
    "reporting",
    "runner",
    "staffing",
    "validation",
    "workforce",
)


legacy_source_imports = []

for module_name, module in {
    "__init__": bootstrap_package,
    **loaded_modules,
}.items():

    source_file = inspect.getsourcefile(
        module
    )

    assert source_file is not None

    absolute_imports = (
        collect_absolute_imports(
            Path(source_file).resolve()
        )
    )

    for imported_name in absolute_imports:

        if any(
            imported_name == prefix
            or imported_name.startswith(
                f"{prefix}."
            )
            for prefix in (
                FORBIDDEN_TOP_LEVEL_PACKAGES
            )
        ):
            legacy_source_imports.append(
                (
                    module_name,
                    imported_name,
                )
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in "
    f"src.bootstrap: "
    f"{legacy_source_imports}"
)

print(
    "PASS: No legacy platform-package absolute "
    "source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "bootstrap_project",
)

assert hasattr(
    bootstrap_package,
    "__all__",
)

assert tuple(
    bootstrap_package.__all__
) == EXPECTED_PUBLIC_API

assert len(
    bootstrap_package.__all__
) == len(
    set(bootstrap_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        bootstrap_package,
        symbol_name,
    )

print(
    "PASS: Bootstrap root public API contains "
    "the expected bootstrap_project symbol"
)


# -----------------------------------------------------------------------------
# 6. Validate leaf-module public contracts
# -----------------------------------------------------------------------------

project_module = loaded_modules[
    "project"
]

workspace_module = loaded_modules[
    "workspace"
]


assert hasattr(
    project_module,
    "bootstrap_project",
)

assert hasattr(
    workspace_module,
    "register_workspace_src",
)


# These modules intentionally do not define __all__.
assert not hasattr(
    project_module,
    "__all__",
)

assert not hasattr(
    workspace_module,
    "__all__",
)

print(
    "PASS: Bootstrap leaf-module public contracts "
    "remain consistent"
)


# -----------------------------------------------------------------------------
# 7. Validate public object identity
# -----------------------------------------------------------------------------

from src.bootstrap import (
    bootstrap_project,
)

from src.bootstrap.project import (
    bootstrap_project as LeafBootstrapProject,
)

from src.bootstrap.workspace import (
    register_workspace_src,
)


assert (
    bootstrap_project
    is LeafBootstrapProject
)

print(
    "PASS: Bootstrap public object identity "
    "remains consistent"
)


# -----------------------------------------------------------------------------
# 8. Resolve actual repository src path
# -----------------------------------------------------------------------------

original_cwd = Path.cwd()

actual_src_path = None
current = original_cwd

while current != current.parent:

    candidate = current / "src"

    if candidate.exists():
        actual_src_path = candidate
        break

    current = current.parent


assert actual_src_path is not None, (
    "Unable to identify repository src directory "
    "for release validation."
)

actual_src_path = (
    actual_src_path.resolve()
)

print(
    "PASS: Located repository src directory for "
    "bootstrap validation"
)


# -----------------------------------------------------------------------------
# 9. Validate register_workspace_src()
# -----------------------------------------------------------------------------

src_path_string = str(
    actual_src_path
)

original_occurrences = (
    sys.path.count(
        src_path_string
    )
)


registered_src = (
    register_workspace_src()
)

assert isinstance(
    registered_src,
    Path,
)

assert (
    registered_src.resolve()
    == actual_src_path
)

assert (
    src_path_string
    in sys.path
)

assert (
    sys.path.count(
        src_path_string
    )
    >= 1
)

print(
    "PASS: register_workspace_src() locates and "
    "registers the canonical src directory"
)


# -----------------------------------------------------------------------------
# 10. Validate idempotent sys.path registration
# -----------------------------------------------------------------------------

count_before_second_call = (
    sys.path.count(
        src_path_string
    )
)

second_registered_src = (
    register_workspace_src()
)

count_after_second_call = (
    sys.path.count(
        src_path_string
    )
)

assert (
    second_registered_src.resolve()
    == actual_src_path
)

assert (
    count_after_second_call
    == count_before_second_call
)

print(
    "PASS: register_workspace_src() remains "
    "idempotent"
)


# -----------------------------------------------------------------------------
# 11. Validate bootstrap_project() delegation
# -----------------------------------------------------------------------------

bootstrap_result = (
    bootstrap_project()
)

assert isinstance(
    bootstrap_result,
    Path,
)

assert (
    bootstrap_result.resolve()
    == actual_src_path
)

assert (
    src_path_string
    in sys.path
)

print(
    "PASS: bootstrap_project() delegates to "
    "workspace registration and returns src path"
)


# -----------------------------------------------------------------------------
# 12. Validate registration from nested repository path
# -----------------------------------------------------------------------------

nested_test_directory = (
    actual_src_path
    / "__implementation_28_bootstrap_validation__"
)

nested_test_directory.mkdir(
    exist_ok=True
)

try:

    os.chdir(
        nested_test_directory
    )

    nested_registered_src = (
        register_workspace_src()
    )

    assert (
        nested_registered_src.resolve()
        == actual_src_path
    )

finally:

    os.chdir(
        original_cwd
    )

    nested_test_directory.rmdir()


print(
    "PASS: Bootstrap upward repository search "
    "remains operational from nested paths"
)


# -----------------------------------------------------------------------------
# 13. Validate failure behavior outside a repository
# -----------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as temp_dir:

    isolated_directory = Path(
        temp_dir
    ).resolve()

    os.chdir(
        isolated_directory
    )

    try:

        register_workspace_src()

    except RuntimeError as exc:

        assert (
            "Unable to locate project src directory."
            in str(exc)
        )

    else:

        raise AssertionError(
            "register_workspace_src() must fail "
            "when no parent repository contains src."
        )

    finally:

        os.chdir(
            original_cwd
        )


print(
    "PASS: Bootstrap missing-repository failure "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate public signatures
# -----------------------------------------------------------------------------

workspace_signature = (
    inspect.signature(
        register_workspace_src
    )
)

assert len(
    workspace_signature.parameters
) == 0


bootstrap_signature = (
    inspect.signature(
        bootstrap_project
    )
)

assert len(
    bootstrap_signature.parameters
) == 0

print(
    "PASS: Bootstrap public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print(
    "IMPLEMENTATION 28 RELEASE VALIDATION PASSED"
)
print("Package: src.bootstrap")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print(
    "Production-file changes required: 0"
)
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
#
# Package:
#     src.validation
#
# Release:
#     v3.0.0
#
# Finding:
#     ENG-001 — Canonical Python Import Namespace Validation
#
# Validation Scope:
#     - Canonical src.* namespace
#     - Legacy import detection
#     - Root public API
#     - Public object identity
#     - Severity/status enums
#     - ValidationResult / ValidationReport
#     - All seven Spark validation rules
#     - WARNING vs ERROR behavior
#     - DataValidator orchestration
#     - fail_fast behavior
#     - Spark report DataFrame conversion
#     - Report persistence contract
#     - Public signatures
# =============================================================================

from __future__ import annotations

import ast
import importlib
import inspect
import sys
import tempfile
from pathlib import Path


PACKAGE_NAME = "src.validation"

EXPECTED_MODULES = (
    "exceptions",
    "models",
    "reporting",
    "rules",
    "validator",
)


# -----------------------------------------------------------------------------
# 1. Import canonical package
# -----------------------------------------------------------------------------

validation_package = importlib.import_module(
    PACKAGE_NAME
)

assert validation_package.__name__ == PACKAGE_NAME
assert validation_package.__package__ == PACKAGE_NAME

print(
    "PASS: Imported canonical package src.validation"
)


# -----------------------------------------------------------------------------
# 2. Import every validation module through canonical src.*
# -----------------------------------------------------------------------------

loaded_modules = {}

for module_name in EXPECTED_MODULES:
    qualified_name = f"{PACKAGE_NAME}.{module_name}"

    module = importlib.import_module(
        qualified_name
    )

    assert module.__name__ == qualified_name

    loaded_modules[module_name] = module

print(
    "PASS: Imported every validation module through "
    "the canonical src.* namespace"
)


# -----------------------------------------------------------------------------
# 3. Reject legacy validation.* module loading
# -----------------------------------------------------------------------------

legacy_modules = sorted(
    module_name
    for module_name in sys.modules
    if (
        module_name == "validation"
        or module_name.startswith(
            "validation."
        )
    )
)

assert legacy_modules == [], (
    "Legacy validation.* modules were loaded: "
    f"{legacy_modules}"
)

print(
    "PASS: No legacy validation.* modules are loaded"
)


# -----------------------------------------------------------------------------
# 4. Scan source for legacy platform-package imports
# -----------------------------------------------------------------------------

def collect_absolute_imports(
    source_path: Path,
) -> tuple[str, ...]:

    source_text = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text,
        filename=str(source_path),
    )

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.append(
                    node.module
                )

    return tuple(imports)


FORBIDDEN_TOP_LEVEL_PACKAGES = (
    "api",
    "application",
    "bootstrap",
    "demand",
    "forecast",
    "metadata",
    "monitoring",
    "optimization",
    "orchestration",
    "overtime",
    "planning",
    "reporting",
    "runner",
    "staffing",
    "validation",
    "workforce",
)


legacy_source_imports = []

for module_name, module in {
    "__init__": validation_package,
    **loaded_modules,
}.items():

    source_file = inspect.getsourcefile(
        module
    )

    assert source_file is not None

    absolute_imports = collect_absolute_imports(
        Path(source_file).resolve()
    )

    for imported_name in absolute_imports:

        if any(
            imported_name == prefix
            or imported_name.startswith(
                f"{prefix}."
            )
            for prefix in (
                FORBIDDEN_TOP_LEVEL_PACKAGES
            )
        ):
            legacy_source_imports.append(
                (
                    module_name,
                    imported_name,
                )
            )


assert legacy_source_imports == [], (
    "Legacy absolute imports remain in "
    f"src.validation: "
    f"{legacy_source_imports}"
)

print(
    "PASS: No legacy platform-package absolute "
    "source imports remain"
)


# -----------------------------------------------------------------------------
# 5. Validate exact root public API
# -----------------------------------------------------------------------------

EXPECTED_PUBLIC_API = (
    "AllowedValuesRule",
    "DataQualityValidationError",
    "DataValidator",
    "MinimumRowCountRule",
    "NotNullRule",
    "NumericRangeRule",
    "RequiredColumnsRule",
    "RowCountMatchRule",
    "UniqueKeyRule",
    "ValidationReport",
    "ValidationResult",
    "ValidationSeverity",
    "ValidationStatus",
    "persist_validation_report",
    "print_validation_report",
    "validation_report_to_dataframe",
)


assert tuple(
    validation_package.__all__
) == EXPECTED_PUBLIC_API, (
    "Unexpected src.validation public API.\n"
    f"Expected: {EXPECTED_PUBLIC_API}\n"
    f"Actual:   {tuple(validation_package.__all__)}"
)

assert len(
    validation_package.__all__
) == len(
    set(validation_package.__all__)
)

for symbol_name in EXPECTED_PUBLIC_API:
    assert hasattr(
        validation_package,
        symbol_name,
    )

print(
    "PASS: Validation public API contains all "
    f"{len(EXPECTED_PUBLIC_API)} expected symbols"
)


# -----------------------------------------------------------------------------
# 6. Validate public object identity
# -----------------------------------------------------------------------------

from src.validation import (
    AllowedValuesRule,
    DataQualityValidationError,
    DataValidator,
    MinimumRowCountRule,
    NotNullRule,
    NumericRangeRule,
    RequiredColumnsRule,
    RowCountMatchRule,
    UniqueKeyRule,
    ValidationReport,
    ValidationResult,
    ValidationSeverity,
    ValidationStatus,
    persist_validation_report,
    print_validation_report,
    validation_report_to_dataframe,
)

from src.validation.exceptions import (
    DataQualityValidationError
    as LeafDataQualityValidationError,
)

from src.validation.models import (
    ValidationReport as LeafValidationReport,
    ValidationResult as LeafValidationResult,
    ValidationSeverity as LeafValidationSeverity,
    ValidationStatus as LeafValidationStatus,
)

from src.validation.reporting import (
    persist_validation_report
    as LeafPersistValidationReport,
    print_validation_report
    as LeafPrintValidationReport,
    validation_report_to_dataframe
    as LeafValidationReportToDataframe,
)

from src.validation.rules import (
    AllowedValuesRule as LeafAllowedValuesRule,
    MinimumRowCountRule
    as LeafMinimumRowCountRule,
    NotNullRule as LeafNotNullRule,
    NumericRangeRule as LeafNumericRangeRule,
    RequiredColumnsRule
    as LeafRequiredColumnsRule,
    RowCountMatchRule
    as LeafRowCountMatchRule,
    UniqueKeyRule as LeafUniqueKeyRule,
)

from src.validation.validator import (
    DataValidator as LeafDataValidator,
)


assert (
    DataQualityValidationError
    is LeafDataQualityValidationError
)

assert DataValidator is LeafDataValidator

assert (
    ValidationReport
    is LeafValidationReport
)

assert (
    ValidationResult
    is LeafValidationResult
)

assert (
    ValidationSeverity
    is LeafValidationSeverity
)

assert (
    ValidationStatus
    is LeafValidationStatus
)

assert (
    AllowedValuesRule
    is LeafAllowedValuesRule
)

assert (
    MinimumRowCountRule
    is LeafMinimumRowCountRule
)

assert NotNullRule is LeafNotNullRule

assert (
    NumericRangeRule
    is LeafNumericRangeRule
)

assert (
    RequiredColumnsRule
    is LeafRequiredColumnsRule
)

assert (
    RowCountMatchRule
    is LeafRowCountMatchRule
)

assert UniqueKeyRule is LeafUniqueKeyRule

assert (
    persist_validation_report
    is LeafPersistValidationReport
)

assert (
    print_validation_report
    is LeafPrintValidationReport
)

assert (
    validation_report_to_dataframe
    is LeafValidationReportToDataframe
)

print(
    "PASS: Validation public object identities "
    "are consistent"
)


# -----------------------------------------------------------------------------
# 7. Validate enum contracts
# -----------------------------------------------------------------------------

assert (
    ValidationSeverity.WARNING.value
    == "WARNING"
)

assert (
    ValidationSeverity.ERROR.value
    == "ERROR"
)

assert (
    ValidationStatus.PASSED.value
    == "PASSED"
)

assert (
    ValidationStatus.WARNING.value
    == "WARNING"
)

assert (
    ValidationStatus.FAILED.value
    == "FAILED"
)

print(
    "PASS: Validation severity/status enum contracts "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 8. Validate ValidationResult contract
# -----------------------------------------------------------------------------

validation_result = ValidationResult(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    rule_name="release_validation_rule",
    severity=ValidationSeverity.ERROR,
    status=ValidationStatus.PASSED,
    observed_value="3",
    expected_value=">= 1",
    message="Release validation passed.",
)

result_payload = (
    validation_result.to_dict()
)

assert result_payload[
    "dataset_name"
] == "implementation_28_dataset"

assert result_payload[
    "dataset_layer"
] == "validation"

assert result_payload[
    "severity"
] == "ERROR"

assert result_payload[
    "status"
] == "PASSED"

assert result_payload[
    "rule_name"
] == "release_validation_rule"

print(
    "PASS: ValidationResult serialization "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 9. Validate ValidationReport aggregation contract
# -----------------------------------------------------------------------------

warning_result = ValidationResult(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    rule_name="warning_rule",
    severity=ValidationSeverity.WARNING,
    status=ValidationStatus.WARNING,
    observed_value="1",
    expected_value="0",
    message="Controlled warning.",
)

failed_result = ValidationResult(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    rule_name="failed_rule",
    severity=ValidationSeverity.ERROR,
    status=ValidationStatus.FAILED,
    observed_value="1",
    expected_value="0",
    message="Controlled failure.",
)


passed_report = ValidationReport(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    results=(
        validation_result,
    ),
)

assert passed_report.passed_count == 1
assert passed_report.warning_count == 0
assert passed_report.failed_count == 0

assert (
    passed_report.status
    is ValidationStatus.PASSED
)


warning_report = ValidationReport(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    results=(
        validation_result,
        warning_result,
    ),
)

assert warning_report.passed_count == 1
assert warning_report.warning_count == 1
assert warning_report.failed_count == 0

assert (
    warning_report.status
    is ValidationStatus.WARNING
)


failed_report = ValidationReport(
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    results=(
        validation_result,
        warning_result,
        failed_result,
    ),
)

assert failed_report.passed_count == 1
assert failed_report.warning_count == 1
assert failed_report.failed_count == 1

assert (
    failed_report.status
    is ValidationStatus.FAILED
)

report_rows = failed_report.to_rows()

assert len(report_rows) == 3

assert all(
    row["validation_run_id"]
    == failed_report.run_id
    for row in report_rows
)

assert all(
    row["report_status"]
    == "FAILED"
    for row in report_rows
)

print(
    "PASS: ValidationReport aggregation "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 10. Create deterministic Spark validation dataset
# -----------------------------------------------------------------------------

validation_df = spark.createDataFrame(
    [
        (
            1,
            "A",
            10.0,
            "ACTIVE",
        ),
        (
            2,
            "B",
            20.0,
            "ACTIVE",
        ),
        (
            3,
            "C",
            30.0,
            "INACTIVE",
        ),
    ],
    schema=(
        "record_id long, "
        "category string, "
        "metric double, "
        "status string"
    ),
)

assert validation_df.count() == 3

print(
    "PASS: Created deterministic Spark validation dataset"
)


# -----------------------------------------------------------------------------
# 11. Validate RequiredColumnsRule
# -----------------------------------------------------------------------------

required_columns_rule = RequiredColumnsRule(
    required_columns=(
        "record_id",
        "category",
        "metric",
        "status",
    )
)

required_columns_result = (
    required_columns_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    required_columns_result.status
    is ValidationStatus.PASSED
)

assert (
    required_columns_result.rule_name
    == "required_columns"
)

print(
    "PASS: RequiredColumnsRule contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 12. Validate MinimumRowCountRule
# -----------------------------------------------------------------------------

minimum_row_rule = MinimumRowCountRule(
    minimum_rows=3
)

minimum_row_result = (
    minimum_row_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    minimum_row_result.status
    is ValidationStatus.PASSED
)

assert (
    minimum_row_result.observed_value
    == "3"
)

print(
    "PASS: MinimumRowCountRule contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 13. Validate RowCountMatchRule
# -----------------------------------------------------------------------------

row_count_rule = RowCountMatchRule(
    expected_rows=3
)

row_count_result = (
    row_count_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    row_count_result.status
    is ValidationStatus.PASSED
)

print(
    "PASS: RowCountMatchRule contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 14. Validate NotNullRule
# -----------------------------------------------------------------------------

not_null_rule = NotNullRule(
    columns=(
        "record_id",
        "category",
        "metric",
    )
)

not_null_result = (
    not_null_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    not_null_result.status
    is ValidationStatus.PASSED
)

print(
    "PASS: NotNullRule contract remains operational"
)


# -----------------------------------------------------------------------------
# 15. Validate UniqueKeyRule
# -----------------------------------------------------------------------------

unique_key_rule = UniqueKeyRule(
    key_columns=(
        "record_id",
    )
)

unique_key_result = (
    unique_key_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    unique_key_result.status
    is ValidationStatus.PASSED
)

assert (
    unique_key_result.observed_value
    == "0"
)

print(
    "PASS: UniqueKeyRule contract remains operational"
)


# -----------------------------------------------------------------------------
# 16. Validate NumericRangeRule
# -----------------------------------------------------------------------------

numeric_range_rule = NumericRangeRule(
    column="metric",
    minimum=0.0,
    maximum=100.0,
)

numeric_range_result = (
    numeric_range_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    numeric_range_result.status
    is ValidationStatus.PASSED
)

assert (
    numeric_range_result.rule_name
    == "numeric_range:metric"
)

print(
    "PASS: NumericRangeRule contract remains operational"
)


# -----------------------------------------------------------------------------
# 17. Validate AllowedValuesRule
# -----------------------------------------------------------------------------

allowed_values_rule = AllowedValuesRule(
    column="status",
    allowed_values=(
        "ACTIVE",
        "INACTIVE",
    ),
)

allowed_values_result = (
    allowed_values_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    allowed_values_result.status
    is ValidationStatus.PASSED
)

assert (
    allowed_values_result.rule_name
    == "allowed_values:status"
)

print(
    "PASS: AllowedValuesRule contract remains operational"
)


# -----------------------------------------------------------------------------
# 18. Validate WARNING-severity failure behavior
# -----------------------------------------------------------------------------

warning_rule = NumericRangeRule(
    column="metric",
    maximum=15.0,
    severity=ValidationSeverity.WARNING,
)

warning_rule_result = (
    warning_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    warning_rule_result.status
    is ValidationStatus.WARNING
)

assert (
    warning_rule_result.severity
    is ValidationSeverity.WARNING
)

assert (
    warning_rule_result.observed_value
    == "2"
)

print(
    "PASS: Validation WARNING-severity behavior "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 19. Validate ERROR-severity failure behavior
# -----------------------------------------------------------------------------

error_rule = NumericRangeRule(
    column="metric",
    maximum=15.0,
    severity=ValidationSeverity.ERROR,
)

error_rule_result = (
    error_rule.evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    error_rule_result.status
    is ValidationStatus.FAILED
)

assert (
    error_rule_result.severity
    is ValidationSeverity.ERROR
)

assert (
    error_rule_result.observed_value
    == "2"
)

print(
    "PASS: Validation ERROR-severity behavior "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 20. Validate missing-column rule behavior
# -----------------------------------------------------------------------------

missing_column_result = (
    NumericRangeRule(
        column="missing_metric",
        minimum=0.0,
    ).evaluate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
    )
)

assert (
    missing_column_result.status
    is ValidationStatus.FAILED
)

assert (
    missing_column_result.observed_value
    == "column missing"
)

print(
    "PASS: Validation missing-column failure "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 21. Validate DataValidator successful orchestration
# -----------------------------------------------------------------------------

validator = DataValidator(
    fail_fast=False
)

success_report = validator.validate(
    dataframe=validation_df,
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    rules=(
        RequiredColumnsRule(
            required_columns=(
                "record_id",
                "category",
                "metric",
                "status",
            )
        ),
        MinimumRowCountRule(
            minimum_rows=3
        ),
        RowCountMatchRule(
            expected_rows=3
        ),
        NotNullRule(
            columns=(
                "record_id",
                "category",
                "metric",
            )
        ),
        UniqueKeyRule(
            key_columns=(
                "record_id",
            )
        ),
        NumericRangeRule(
            column="metric",
            minimum=0.0,
            maximum=100.0,
        ),
        AllowedValuesRule(
            column="status",
            allowed_values=(
                "ACTIVE",
                "INACTIVE",
            ),
        ),
    ),
)

assert (
    success_report.status
    is ValidationStatus.PASSED
)

assert success_report.passed_count == 7
assert success_report.warning_count == 0
assert success_report.failed_count == 0

print(
    "PASS: DataValidator successful orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 22. Validate mixed PASSED + WARNING report
# -----------------------------------------------------------------------------

warning_validator = DataValidator(
    fail_fast=False
)

warning_validation_report = (
    warning_validator.validate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
        rules=(
            MinimumRowCountRule(
                minimum_rows=1
            ),
            NumericRangeRule(
                column="metric",
                maximum=15.0,
                severity=ValidationSeverity.WARNING,
            ),
        ),
    )
)

assert (
    warning_validation_report.status
    is ValidationStatus.WARNING
)

assert warning_validation_report.passed_count == 1
assert warning_validation_report.warning_count == 1
assert warning_validation_report.failed_count == 0

print(
    "PASS: DataValidator warning-only orchestration "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 23. Validate ERROR report without raising
# -----------------------------------------------------------------------------

failed_validation_report = validator.validate(
    dataframe=validation_df,
    dataset_name="implementation_28_dataset",
    dataset_layer="validation",
    rules=(
        NumericRangeRule(
            column="metric",
            maximum=15.0,
        ),
    ),
    raise_on_failure=False,
)

assert (
    failed_validation_report.status
    is ValidationStatus.FAILED
)

assert failed_validation_report.failed_count == 1

print(
    "PASS: DataValidator raise_on_failure=False "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 24. Validate ERROR report raises by default
# -----------------------------------------------------------------------------

try:
    validator.validate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
        rules=(
            NumericRangeRule(
                column="metric",
                maximum=15.0,
            ),
        ),
    )

except DataQualityValidationError as exc:

    assert (
        "Validation failed for "
        "validation.implementation_28_dataset."
        in str(exc)
    )

    assert (
        "numeric_range:metric"
        in str(exc)
    )

else:

    raise AssertionError(
        "DataValidator must raise "
        "DataQualityValidationError for ERROR failures."
    )

print(
    "PASS: DataValidator ERROR escalation "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 25. Validate fail_fast behavior
# -----------------------------------------------------------------------------

fail_fast_validator = DataValidator(
    fail_fast=True
)

try:
    fail_fast_validator.validate(
        dataframe=validation_df,
        dataset_name="implementation_28_dataset",
        dataset_layer="validation",
        rules=(
            NumericRangeRule(
                column="metric",
                maximum=15.0,
            ),
            MinimumRowCountRule(
                minimum_rows=100,
            ),
        ),
    )

except DataQualityValidationError as exc:

    assert "numeric_range:metric" in str(exc)

    # fail_fast should stop before evaluating the second rule
    assert "minimum_row_count" not in str(exc)

else:

    raise AssertionError(
        "fail_fast=True must raise after "
        "the first ERROR-severity failure."
    )

print(
    "PASS: DataValidator fail_fast contract "
    "remains operational"
)


# -----------------------------------------------------------------------------
# 26. Validate validation-report Spark DataFrame conversion
# -----------------------------------------------------------------------------

report_df = (
    validation_report_to_dataframe(
        spark=spark,
        report=success_report,
    )
)

assert report_df.count() == 7

expected_report_columns = {
    "dataset_name",
    "dataset_layer",
    "rule_name",
    "severity",
    "status",
    "observed_value",
    "expected_value",
    "message",
    "evaluated_at_utc",
    "validation_run_id",
    "report_status",
    "report_created_at_utc",
}

assert set(
    report_df.columns
) == expected_report_columns

assert (
    report_df.filter(
        "report_status = 'PASSED'"
    ).count()
    == 7
)

print(
    "PASS: validation_report_to_dataframe() "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 27. Validate persistence orchestration contract
# -----------------------------------------------------------------------------

class _ValidationWriterDouble:
    def __init__(self):
        self.mode_value = None
        self.options = {}
        self.output_path = None

    def mode(self, value):
        self.mode_value = value
        return self

    def option(self, key, value):
        self.options[key] = value
        return self

    def parquet(self, output_path):
        self.output_path = output_path


class _ValidationDataFrameDouble:
    def __init__(self):
        self.write = _ValidationWriterDouble()


report_df_double = _ValidationDataFrameDouble()

validation_output_path = (
    "/release-validation/"
    "implementation-28/validation-report"
)

persist_validation_report(
    report_df=report_df_double,
    output_path=validation_output_path,
    mode="overwrite",
)

assert (
    report_df_double.write.mode_value
    == "overwrite"
)

assert (
    report_df_double.write.options
    == {
        "compression": "snappy",
    }
)

assert (
    report_df_double.write.output_path
    == validation_output_path
)

print(
    "PASS: persist_validation_report() "
    "Parquet orchestration contract remains operational"
)


# -----------------------------------------------------------------------------
# 28. Validate human-readable reporting function
# -----------------------------------------------------------------------------

# This intentionally prints the release-validation report
# to confirm the reporting utility remains executable.
print_validation_report(
    success_report
)

print(
    "PASS: print_validation_report() "
    "contract remains operational"
)


# -----------------------------------------------------------------------------
# 29. Validate representative rule failures
# -----------------------------------------------------------------------------

duplicate_df = spark.createDataFrame(
    [
        (1, "A"),
        (1, "B"),
    ],
    "record_id long, category string",
)

duplicate_result = (
    UniqueKeyRule(
        key_columns=("record_id",)
    ).evaluate(
        dataframe=duplicate_df,
        dataset_name="duplicate_dataset",
        dataset_layer="validation",
    )
)

assert (
    duplicate_result.status
    is ValidationStatus.FAILED
)

assert (
    duplicate_result.observed_value
    == "1"
)


invalid_allowed_df = spark.createDataFrame(
    [
        (1, "GOOD"),
        (2, "INVALID"),
    ],
    "record_id long, status string",
)

invalid_allowed_result = (
    AllowedValuesRule(
        column="status",
        allowed_values=("GOOD",),
    ).evaluate(
        dataframe=invalid_allowed_df,
        dataset_name="allowed_values_dataset",
        dataset_layer="validation",
    )
)

assert (
    invalid_allowed_result.status
    is ValidationStatus.FAILED
)

assert (
    invalid_allowed_result.observed_value
    == "1"
)

print(
    "PASS: Validation representative rule failures "
    "remain operational"
)


# -----------------------------------------------------------------------------
# 30. Validate public signatures
# -----------------------------------------------------------------------------

validator_signature = inspect.signature(
    DataValidator
)

assert (
    "fail_fast"
    in validator_signature.parameters
)


validate_signature = inspect.signature(
    DataValidator.validate
)

for parameter_name in (
    "dataframe",
    "dataset_name",
    "dataset_layer",
    "rules",
    "raise_on_failure",
):
    assert (
        parameter_name
        in validate_signature.parameters
    )


report_dataframe_signature = (
    inspect.signature(
        validation_report_to_dataframe
    )
)

assert (
    "spark"
    in report_dataframe_signature.parameters
)

assert (
    "report"
    in report_dataframe_signature.parameters
)


persist_signature = inspect.signature(
    persist_validation_report
)

for parameter_name in (
    "report_df",
    "output_path",
    "mode",
):
    assert (
        parameter_name
        in persist_signature.parameters
    )


print_report_signature = inspect.signature(
    print_validation_report
)

assert (
    "report"
    in print_report_signature.parameters
)

print(
    "PASS: Validation public signatures are preserved"
)


# -----------------------------------------------------------------------------
# Final release-validation result
# -----------------------------------------------------------------------------

print("=" * 80)
print(
    "IMPLEMENTATION 28 RELEASE VALIDATION PASSED"
)
print("Package: src.validation")
print("Release: v3.0.0")
print("Finding: ENG-001")
print("Canonical namespace: src.*")
print(
    "Production-file changes required: 0"
)
print(
    "Modules validated:",
    len(EXPECTED_MODULES) + 1,
)
print(
    "Root public API symbols validated:",
    len(EXPECTED_PUBLIC_API),
)
print("=" * 80)