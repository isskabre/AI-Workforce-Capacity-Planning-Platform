"""
AI Workforce Capacity Planning Platform
Implementation 13 - Enterprise Evaluation Framework

Module:
    src.forecast.modeling.metrics

Description:
    Defines immutable forecasting metric contracts shared by evaluation,
    comparison, reporting, model registry, monitoring, and API layers.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.6.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from typing import Any


@dataclass(frozen=True, slots=True)
class ForecastMetrics:
    """
    Immutable collection of standardized forecast-quality metrics.

    Metric conventions:
        mae:
            Mean absolute error.

        mse:
            Mean squared error.

        rmse:
            Root mean squared error.

        bias:
            Mean prediction error calculated as ``predicted - actual``.
            Positive values indicate systematic overprediction; negative
            values indicate systematic underprediction.

        mape:
            Mean absolute percentage error expressed as a percentage.

        smape:
            Symmetric mean absolute percentage error expressed as a
            percentage.

        wape:
            Weighted absolute percentage error expressed as a percentage.
    """

    mae: float
    mse: float
    rmse: float
    bias: float
    mape: float
    smape: float
    wape: float

    def __post_init__(self) -> None:
        """Validate that every metric is numeric and finite."""
        for metric_field in fields(self):
            field_name = metric_field.name
            value = getattr(self, field_name)

            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{field_name} must be a numeric value."
                )

            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{field_name} must be finite."
                )

    def to_dict(self) -> dict[str, float]:
        """
        Return a serialization-safe dictionary representation.

        Returns:
            Mapping of canonical metric names to floating-point values.
        """
        return {
            key: float(value)
            for key, value in asdict(self).items()
        }

    def get(
        self,
        metric_name: str,
    ) -> float:
        """
        Return one metric by canonical name.

        Args:
            metric_name:
                Case-insensitive metric name.

        Returns:
            Requested metric value.

        Raises:
            TypeError:
                If ``metric_name`` is not a string.

            KeyError:
                If the metric is unsupported.
        """
        if not isinstance(metric_name, str):
            raise TypeError(
                "metric_name must be a string."
            )

        normalized_name = metric_name.strip().lower()

        metrics = self.to_dict()

        if normalized_name not in metrics:
            raise KeyError(
                f"Unsupported forecast metric: {metric_name}."
            )

        return metrics[normalized_name]

    def as_mapping(self) -> Mapping[str, float]:
        """
        Return an immutable-style metric mapping interface.

        A new dictionary is returned so callers cannot mutate the dataclass.
        """
        return self.to_dict()

    def with_metadata(
        self,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build a serialization-safe payload containing metrics and metadata.

        Args:
            metadata:
                Optional contextual metadata.

        Returns:
            Dictionary containing metric values and copied metadata.
        """
        return {
            "metrics": self.to_dict(),
            "metadata": dict(metadata or {}),
        }


__all__ = [
    "ForecastMetrics",
]