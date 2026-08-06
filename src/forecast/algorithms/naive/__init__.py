"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.naive

Description:
    Public package interface and factory registration for the enterprise
    Naive Last-Value forecasting algorithm.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from src.forecast.algorithms.naive.estimator import (
    NaiveLastValueEstimator,
)
from src.forecast.algorithms.naive.model import (
    NaiveForecastModel,
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


@register_forecast_model(
    model_key="naive_last_value",
    display_name="Naive Last-Value Forecast",
    category=ForecastModelCategory.BASELINE,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
        ForecastModelCapability.MULTI_STEP_FORECAST,
    }),
    implementation_version="1.0.0",
    description=(
        "Deterministic forecasting baseline that repeats the final "
        "observed training value for each requested future period."
    ),
    metadata={
        "framework": "native_python",
        "implementation": "11",
        "algorithm_family": "baseline",
    },
    overwrite=True,
)
def build_naive_last_value_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    """
    Build the enterprise Naive Last-Value forecasting model.

    The current estimator has no model-specific configuration parameters.
    The root enterprise configuration is accepted to preserve the common
    factory-builder contract and support future configuration extensions.
    """
    del configuration

    return NaiveForecastModel()


__all__ = [
    "NaiveForecastModel",
    "NaiveLastValueEstimator",
    "build_naive_last_value_model",
]