"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.modeling.exceptions

Description:
    Defines the standardized exception hierarchy used throughout the
    Enterprise Forecast Modeling Framework.

    Framework services and model adapters must raise these exceptions instead
    of generic built-in exceptions when reporting domain-specific failures.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ForecastModelingError(Exception):
    """
    Base exception for all Enterprise Forecast Modeling Framework failures.

    Attributes:
        message:
            Human-readable description of the failure.
        error_code:
            Stable machine-readable error identifier.
        context:
            Additional diagnostic metadata.
        cause:
            Optional originating exception.
    """

    default_error_code = "FORECAST_MODELING_ERROR"

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        context: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code or self.default_error_code
        self.context = dict(context or {})
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serialization-safe representation of the exception.

        Returns:
            Dictionary suitable for audit logs, validation reports, metadata
            persistence, or API error responses.
        """
        return {
            "error_type": type(self).__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": dict(self.context),
            "cause_type": (
                type(self.cause).__name__
                if self.cause is not None
                else None
            ),
            "cause_message": (
                str(self.cause)
                if self.cause is not None
                else None
            ),
        }

    def __str__(self) -> str:
        """Return the formatted enterprise error message."""
        return f"[{self.error_code}] {self.message}"


class ForecastConfigurationError(ForecastModelingError):
    """Raised when forecast modeling configuration is invalid."""

    default_error_code = "FORECAST_CONFIGURATION_ERROR"


class ForecastContextError(ForecastModelingError):
    """Raised when an execution context is missing or incompatible."""

    default_error_code = "FORECAST_CONTEXT_ERROR"


class ForecastInitializationError(ForecastModelingError):
    """Raised when a forecasting model cannot be initialized."""

    default_error_code = "FORECAST_INITIALIZATION_ERROR"


class ForecastTrainingError(ForecastModelingError):
    """Raised when model training fails."""

    default_error_code = "FORECAST_TRAINING_ERROR"


class ForecastPredictionError(ForecastModelingError):
    """Raised when forecast generation fails."""

    default_error_code = "FORECAST_PREDICTION_ERROR"


class ForecastEvaluationError(ForecastModelingError):
    """Raised when forecast evaluation fails."""

    default_error_code = "FORECAST_EVALUATION_ERROR"


class ForecastPersistenceError(ForecastModelingError):
    """Raised when model persistence or loading fails."""

    default_error_code = "FORECAST_PERSISTENCE_ERROR"


class ForecastArtifactError(ForecastModelingError):
    """Raised when a forecast artifact is invalid or unavailable."""

    default_error_code = "FORECAST_ARTIFACT_ERROR"


class ForecastRegistryError(ForecastModelingError):
    """Raised when model registry operations fail."""

    default_error_code = "FORECAST_REGISTRY_ERROR"


class ForecastInferenceError(ForecastModelingError):
    """Raised when inference orchestration fails."""

    default_error_code = "FORECAST_INFERENCE_ERROR"


class ForecastModelNotFoundError(ForecastModelingError):
    """Raised when a requested forecasting model is not registered."""

    default_error_code = "FORECAST_MODEL_NOT_FOUND"


class UnsupportedForecastModelError(ForecastModelingError):
    """Raised when the requested forecasting algorithm is unsupported."""

    default_error_code = "UNSUPPORTED_FORECAST_MODEL"


class ForecastDependencyError(ForecastModelingError):
    """Raised when an optional algorithm dependency is unavailable."""

    default_error_code = "FORECAST_DEPENDENCY_ERROR"


class ForecastStateError(ForecastModelingError):
    """Raised when an operation violates the model lifecycle contract."""

    default_error_code = "FORECAST_STATE_ERROR"


__all__ = [
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
]