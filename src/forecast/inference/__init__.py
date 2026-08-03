"""
AI Workforce Capacity Planning Platform
Implementation 15 - Enterprise Inference Framework

Module:
    forecast.inference

Description:
    Public package interface for single-request and batch enterprise forecast
    inference.

    The package exposes model-agnostic prediction services and immutable batch
    request and result contracts. Consumers should import inference interfaces
    from this module rather than from internal implementation modules.

Architecture:
    Enterprise Inference Framework

Version:
    2.7.0
"""

from forecast.inference.batch_predictor import (
    EnterpriseForecastBatchPredictor,
    ForecastBatchPredictionItem,
    ForecastBatchPredictionRequest,
    ForecastBatchPredictionResult,
)
from forecast.inference.predictor import (
    EnterpriseForecastPredictor,
)


__all__ = [
    "EnterpriseForecastBatchPredictor",
    "EnterpriseForecastPredictor",
    "ForecastBatchPredictionItem",
    "ForecastBatchPredictionRequest",
    "ForecastBatchPredictionResult",
]