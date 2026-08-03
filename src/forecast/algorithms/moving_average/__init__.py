"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    forecast.algorithms.moving_average

Description:
    Public package interface and factory registration for the enterprise
    Moving Average forecasting algorithm.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from forecast.algorithms.moving_average.estimator import (
    MovingAverageEstimator,
)
from forecast.algorithms.moving_average.model import (
    MovingAverageForecastModel,
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


DEFAULT_WINDOW_SIZE = 3


def _resolve_window_size(
    configuration: EnterpriseForecastConfiguration,
) -> int:
    """
    Resolve the Moving Average window size from enterprise configuration.

    Supported configuration location:

        configuration.training.model_parameters[
            "moving_average"
        ]["window_size"]

    The default value is used when no model-specific parameter exists.
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
        return DEFAULT_WINDOW_SIZE

    moving_average_parameters: Any = (
        model_parameters.get(
            "moving_average",
            {},
        )
    )

    if not isinstance(
        moving_average_parameters,
        Mapping,
    ):
        return DEFAULT_WINDOW_SIZE

    raw_window_size = moving_average_parameters.get(
        "window_size",
        DEFAULT_WINDOW_SIZE,
    )

    if isinstance(raw_window_size, bool):
        raise ValueError(
            "Moving Average window_size must be a positive integer."
        )

    try:
        window_size = int(raw_window_size)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Moving Average window_size must be a positive integer."
        ) from exc

    if window_size <= 0:
        raise ValueError(
            "Moving Average window_size must be greater than zero."
        )

    return window_size


@register_forecast_model(
    model_key="moving_average",
    display_name="Moving Average Forecast",
    category=ForecastModelCategory.STATISTICAL,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
        ForecastModelCapability.MULTI_STEP_FORECAST,
    }),
    implementation_version="1.0.0",
    description=(
        "Statistical forecasting model that repeats the arithmetic mean "
        "of the most recent target observations across the requested "
        "forecast horizon."
    ),
    metadata={
        "framework": "native_python",
        "implementation": "11",
        "algorithm_family": "statistical",
        "default_window_size": DEFAULT_WINDOW_SIZE,
    },
    overwrite=True,
)
def build_moving_average_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    """
    Build the enterprise Moving Average forecasting model.

    Args:
        configuration:
            Root enterprise forecasting configuration.

    Returns:
        Configured MovingAverageForecastModel.
    """
    window_size = _resolve_window_size(
        configuration
    )

    return MovingAverageForecastModel(
        window_size=window_size,
    )


__all__ = [
    "DEFAULT_WINDOW_SIZE",
    "MovingAverageEstimator",
    "MovingAverageForecastModel",
    "build_moving_average_model",
]