"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    src.forecast.modeling.contexts

Description:
    Immutable execution context objects shared throughout the Enterprise
    Forecast Modeling Framework.

    These context objects define the standardized interfaces exchanged
    between dataset preparation, model training, prediction, and evaluation
    services. They intentionally remain independent from infrastructure
    technologies such as Spark, Pandas, Databricks, or MLflow.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from collections.abc import Mapping

# ---------------------------------------------------------------------
# Type Aliases
# ---------------------------------------------------------------------

DatasetLike = Any
Metadata = Mapping[str, Any]
FeatureColumns = tuple[str, ...]

# ---------------------------------------------------------------------
# Training Context
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ForecastTrainingContext:
    """
    Immutable execution context supplied to model training.

    This object contains every resource required to train a forecasting
    model while remaining completely independent from the underlying
    data engine.
    """

    training_dataset: DatasetLike

    validation_dataset: DatasetLike | None = None

    feature_columns: FeatureColumns = ()

    target_column: str = ""

    forecast_horizon: int = 1

    experiment_id: str | None = None

    configuration: Any = None

    metadata: Metadata = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable dictionary representation.
        """
        return asdict(self)


# ---------------------------------------------------------------------
# Prediction Context
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ForecastPredictionContext:
    """
    Immutable execution context supplied to prediction operations.
    """

    prediction_dataset: DatasetLike

    forecast_horizon: int = 1

    prediction_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_version: str | None = None

    metadata: Metadata = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable dictionary representation.
        """
        return asdict(self)


# ---------------------------------------------------------------------
# Evaluation Context
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ForecastEvaluationContext:
    """
    Immutable execution context supplied to evaluation operations.
    """

    actual_values: DatasetLike

    predicted_values: DatasetLike

    metric: str

    metadata: Metadata = field(default_factory=dict)

    evaluation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable dictionary representation.
        """
        return asdict(self)


# ---------------------------------------------------------------------
# Module Exports
# ---------------------------------------------------------------------

__all__ = [
    "DatasetLike",
    "FeatureColumns",
    "ForecastEvaluationContext",
    "ForecastPredictionContext",
    "ForecastTrainingContext",
    "Metadata",
]