"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.lstm

Description:
    Public package interface and factory registration for the enterprise
    PyTorch LSTM forecasting algorithm.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.forecast.algorithms.lstm.estimator import (
    LSTMEstimator,
)
from src.forecast.algorithms.lstm.model import (
    LSTMForecastModel,
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


DEFAULT_LSTM_PARAMETERS: dict[str, Any] = {
    "hidden_size": 32,
    "num_layers": 1,
    "dropout": 0.0,
    "learning_rate": 0.001,
    "epochs": 20,
    "batch_size": 32,
    "weight_decay": 0.0,
    "gradient_clip_norm": 1.0,
    "random_state": 42,
    "device": "auto",
    "scale_features": True,
    "scale_target": True,
}


def _resolve_lstm_parameters(
    configuration: EnterpriseForecastConfiguration,
) -> dict[str, Any]:
    """
    Resolve LSTM parameters from enterprise configuration.

    Supported location:

        configuration.training.model_parameters["lstm"]

    Missing or invalid model-specific configuration values fall back to
    the platform defaults.
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
        return dict(DEFAULT_LSTM_PARAMETERS)

    raw_parameters = model_parameters.get(
        "lstm",
        {},
    )

    if not isinstance(raw_parameters, Mapping):
        return dict(DEFAULT_LSTM_PARAMETERS)

    return {
        **DEFAULT_LSTM_PARAMETERS,
        **dict(raw_parameters),
    }


@register_forecast_model(
    model_key="lstm",
    display_name="LSTM Forecast",
    category=ForecastModelCategory.DEEP_LEARNING,
    capabilities=frozenset({
        ForecastModelCapability.POINT_FORECAST,
        ForecastModelCapability.MULTI_STEP_FORECAST,
    }),
    implementation_version="1.0.0",
    description=(
        "PyTorch Long Short-Term Memory forecasting model supporting "
        "sequence-based feature tensors, configurable recurrent layers, "
        "feature and target scaling, deterministic training, and persisted "
        "neural-network state."
    ),
    metadata={
        "framework": "pytorch",
        "implementation": "11",
        "algorithm_family": "deep_learning",
        "default_hidden_size": 32,
        "default_num_layers": 1,
        "default_epochs": 20,
        "default_device": "auto",
    },
    overwrite=True,
)
def build_lstm_model(
    configuration: EnterpriseForecastConfiguration,
) -> BaseForecastModel:
    """
    Build the configured enterprise LSTM forecasting model.
    """
    parameters = _resolve_lstm_parameters(
        configuration
    )

    return LSTMForecastModel(
        hidden_size=parameters["hidden_size"],
        num_layers=parameters["num_layers"],
        dropout=parameters["dropout"],
        learning_rate=parameters["learning_rate"],
        epochs=parameters["epochs"],
        batch_size=parameters["batch_size"],
        weight_decay=parameters["weight_decay"],
        gradient_clip_norm=parameters[
            "gradient_clip_norm"
        ],
        random_state=parameters["random_state"],
        device=parameters["device"],
        scale_features=parameters[
            "scale_features"
        ],
        scale_target=parameters[
            "scale_target"
        ],
    )


__all__ = [
    "DEFAULT_LSTM_PARAMETERS",
    "LSTMEstimator",
    "LSTMForecastModel",
    "build_lstm_model",
]