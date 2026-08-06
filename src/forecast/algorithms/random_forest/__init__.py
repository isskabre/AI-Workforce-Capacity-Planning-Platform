"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.random_forest

Description:
    Public package interface and factory registration for the enterprise
    Random Forest forecasting algorithm.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.forecast.algorithms.random_forest.estimator import (
    RandomForestEstimator,
)
from src.forecast.algorithms.random_forest.model import (
    RandomForestForecastModel,
)
from src.forecast.modeling.configuration import (
    EnterpriseForecastConfiguration,
)
from src.forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
)
from src.forecast.modeling.factory import (
    register_forecast_model,
)


DEFAULT_RANDOM_FOREST_PARAMETERS: dict[str, Any] = {
    "n_estimators": 200,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "max_features": 1.0,
    "bootstrap": True,
    "random_state": 42,
    "n_jobs": -1,
}


def _resolve_random_forest_parameters(
    configuration: EnterpriseForecastConfiguration,
) -> dict[str, Any]:
    """
    Resolve Random Forest parameters from enterprise configuration.

    Supported location:

        configuration.training.model_parameters["random_forest"]
    """
    training_configuration = getattr(
        configuration,
        "training",
        None,
    )

    model_parameters = getattr(
        training_configuration,
        "model_parameters",
        {},
    )

    if not isinstance(model_parameters, Mapping):
        return dict(DEFAULT_RANDOM_FOREST_PARAMETERS)

    raw_parameters = model_parameters.get(
        "random_forest",
        {},
    )

    if not isinstance(raw_parameters, Mapping):
        return dict(DEFAULT_RANDOM_FOREST_PARAMETERS)

    return {
        **DEFAULT_RANDOM_FOREST_PARAMETERS,
        **dict(raw_parameters),
    }


@register_forecast_model(
    model_key="random_forest",
    display_name="Random Forest Forecast",
    category=ForecastModelCategory.MACHINE_LEARNING,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
        ForecastModelCapability.MULTI_STEP_FORECAST,
        ForecastModelCapability.FEATURE_IMPORTANCE,
    }),
    implementation_version="1.0.0",
    description=(
        "Ensemble regression forecasting model based on multiple "
        "decision trees, bootstrap sampling, feature importance, and "
        "tree-level prediction dispersion."
    ),
    metadata={
        "framework": "scikit_learn",
        "implementation": "11",
        "algorithm_family": "machine_learning",
        "default_n_estimators": 200,
        "default_random_state": 42,
    },
    overwrite=True,
)
def build_random_forest_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    """
    Build the configured enterprise Random Forest model.
    """
    parameters = _resolve_random_forest_parameters(
        configuration
    )

    return RandomForestForecastModel(
        n_estimators=parameters["n_estimators"],
        max_depth=parameters["max_depth"],
        min_samples_split=parameters["min_samples_split"],
        min_samples_leaf=parameters["min_samples_leaf"],
        max_features=parameters["max_features"],
        bootstrap=parameters["bootstrap"],
        random_state=parameters["random_state"],
        n_jobs=parameters["n_jobs"],
    )


__all__ = [
    "DEFAULT_RANDOM_FOREST_PARAMETERS",
    "RandomForestEstimator",
    "RandomForestForecastModel",
    "build_random_forest_model",
]