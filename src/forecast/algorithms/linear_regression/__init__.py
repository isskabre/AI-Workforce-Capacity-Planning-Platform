"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    forecast.algorithms.linear_regression

Description:
    Public package interface and factory registration for the enterprise
    Linear Regression forecasting algorithm.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from forecast.algorithms.linear_regression.estimator import (
    LinearRegressionEstimator,
)
from forecast.algorithms.linear_regression.model import (
    LinearRegressionForecastModel,
)
from forecast.modeling.configuration import (
    EnterpriseForecastConfiguration,
)
from forecast.modeling.contracts import (
    BaseForecastModel,
    ForecastModelCapability,
    ForecastModelCategory,
)
from forecast.modeling.factory import (
    register_forecast_model,
)


DEFAULT_FIT_INTERCEPT = True


def _resolve_linear_regression_parameters(
    configuration: EnterpriseForecastConfiguration,
) -> dict[str, Any]:
    """
    Resolve Linear Regression parameters from enterprise configuration.

    Supported configuration location:

        configuration.training.model_parameters[
            "linear_regression"
        ]

    Supported parameters:

        fit_intercept:
            Whether the estimator learns an intercept term.

    Returns:
        Validated model parameters.
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
        return {
            "fit_intercept": DEFAULT_FIT_INTERCEPT,
        }

    raw_parameters = model_parameters.get(
        "linear_regression",
        {},
    )

    if not isinstance(raw_parameters, Mapping):
        return {
            "fit_intercept": DEFAULT_FIT_INTERCEPT,
        }

    fit_intercept = raw_parameters.get(
        "fit_intercept",
        DEFAULT_FIT_INTERCEPT,
    )

    if not isinstance(fit_intercept, bool):
        raise ValueError(
            "Linear Regression fit_intercept must be a boolean."
        )

    estimator_parameters = {
        key: value
        for key, value in raw_parameters.items()
        if key != "fit_intercept"
    }

    return {
        "fit_intercept": fit_intercept,
        "estimator_parameters": estimator_parameters,
    }


@register_forecast_model(
    model_key="linear_regression",
    display_name="Linear Regression Forecast",
    category=ForecastModelCategory.MACHINE_LEARNING,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
        ForecastModelCapability.MULTI_STEP_FORECAST,
    }),
    implementation_version="1.0.0",
    description=(
        "Multivariate ordinary least-squares forecasting model that "
        "learns an intercept and one coefficient per input feature."
    ),
    metadata={
        "framework": "numpy",
        "implementation": "11",
        "algorithm_family": "machine_learning",
        "default_fit_intercept": DEFAULT_FIT_INTERCEPT,
    },
    overwrite=True,
)
def build_linear_regression_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    """
    Build the enterprise Linear Regression forecasting model.

    Args:
        configuration:
            Root enterprise forecasting configuration.

    Returns:
        Configured LinearRegressionForecastModel.
    """
    parameters = _resolve_linear_regression_parameters(
        configuration
    )

    return LinearRegressionForecastModel(
        fit_intercept=parameters["fit_intercept"],
        estimator_parameters=parameters.get(
            "estimator_parameters"
        ),
    )


__all__ = [
    "DEFAULT_FIT_INTERCEPT",
    "LinearRegressionEstimator",
    "LinearRegressionForecastModel",
    "build_linear_regression_model",
]