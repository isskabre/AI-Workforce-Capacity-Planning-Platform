"""
AI Workforce Capacity Planning Platform
Implementation 13 - Enterprise Evaluation Framework

Module:
    forecast.evaluation.comparison

Description:
    Provides deterministic comparison, ranking, and champion selection for
    multiple immutable ForecastEvaluationResult objects.

Architecture:
    Enterprise Evaluation Framework

Version:
    2.6.0
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from forecast.modeling.exceptions import (
    ForecastEvaluationError,
)
from forecast.modeling.results import (
    ForecastEvaluationResult,
)


@dataclass(frozen=True, slots=True)
class ForecastComparisonResult:
    """
    Immutable result returned by enterprise model comparison.

    Attributes:
        comparison_id:
            Unique comparison identifier.

        metric:
            Canonical metric used for ranking.

        champion_model_name:
            Name of the first-ranked model.

        champion_model_version:
            Version of the first-ranked model.

        ordered_results:
            Evaluation results ordered from best to worst. Each returned
            result contains its assigned rank and champion flag.

        compared_at:
            UTC timestamp when comparison completed.

        metadata:
            Additional serializable comparison metadata.
    """

    metric: str
    champion_model_name: str
    champion_model_version: str
    ordered_results: tuple[ForecastEvaluationResult, ...]
    comparison_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    compared_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_models(self) -> int:
        """Return the number of compared models."""
        return len(self.ordered_results)

    @property
    def champion(self) -> ForecastEvaluationResult:
        """Return the champion evaluation result."""
        if not self.ordered_results:
            raise ForecastEvaluationError(
                "Comparison result does not contain a champion."
            )

        return self.ordered_results[0]

    @property
    def runner_up(self) -> ForecastEvaluationResult | None:
        """Return the second-ranked model when available."""
        if len(self.ordered_results) < 2:
            return None

        return self.ordered_results[1]

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe comparison payload."""
        return {
            "comparison_id": self.comparison_id,
            "metric": self.metric,
            "champion_model_name": self.champion_model_name,
            "champion_model_version": self.champion_model_version,
            "total_models": self.total_models,
            "compared_at": self.compared_at.isoformat(),
            "metadata": dict(self.metadata),
            "ordered_results": [
                result.to_dict()
                for result in self.ordered_results
            ],
        }


class EnterpriseForecastComparison:
    """
    Stateless service for ranking enterprise forecast evaluation results.

    Ranking is deterministic:

    1. Metric score
    2. Model name
    3. Model version
    4. Result identifier

    Lower values are better for all currently supported error metrics.
    For ``bias``, absolute bias is ranked because values closest to zero
    indicate the least systematic forecast error.
    """

    SUPPORTED_METRICS = frozenset(
        {
            "mae",
            "mse",
            "rmse",
            "bias",
            "mape",
            "smape",
            "wape",
        }
    )

    def compare(
        self,
        *,
        evaluations: Sequence[ForecastEvaluationResult],
        metric: str,
        metadata: dict[str, Any] | None = None,
    ) -> ForecastComparisonResult:
        """
        Rank forecast evaluations and select one champion.

        Args:
            evaluations:
                Successful forecast evaluation results to compare.

            metric:
                Metric used for ranking.

            metadata:
                Optional comparison metadata.

        Returns:
            Immutable comparison result with ranked evaluation results.

        Raises:
            ForecastEvaluationError:
                If the request or any evaluation result is invalid.
        """
        normalized_metric = self._normalize_metric(metric)

        validated_results = self._validate_evaluations(
            evaluations=evaluations,
            metric=normalized_metric,
        )

        ordered = sorted(
            validated_results,
            key=lambda result: self._ranking_key(
                result=result,
                metric=normalized_metric,
            ),
        )

        ranked_results = tuple(
            replace(
                result,
                rank=index,
                champion=index == 1,
            )
            for index, result in enumerate(
                ordered,
                start=1,
            )
        )

        champion = ranked_results[0]

        return ForecastComparisonResult(
            metric=normalized_metric,
            champion_model_name=champion.model_name,
            champion_model_version=champion.model_version,
            ordered_results=ranked_results,
            metadata=dict(metadata or {}),
        )

    @classmethod
    def _normalize_metric(
        cls,
        metric: str,
    ) -> str:
        """Normalize and validate the ranking metric."""
        if not isinstance(metric, str):
            raise ForecastEvaluationError(
                "Comparison metric must be a string.",
                context={
                    "received_type": type(metric).__name__,
                },
            )

        normalized = metric.strip().lower()

        if not normalized:
            raise ForecastEvaluationError(
                "Comparison metric must not be empty."
            )

        if normalized not in cls.SUPPORTED_METRICS:
            raise ForecastEvaluationError(
                "Unsupported comparison metric.",
                context={
                    "metric": metric,
                    "supported_metrics": tuple(
                        sorted(cls.SUPPORTED_METRICS)
                    ),
                },
            )

        return normalized

    @staticmethod
    def _validate_evaluations(
        *,
        evaluations: Sequence[ForecastEvaluationResult],
        metric: str,
    ) -> tuple[ForecastEvaluationResult, ...]:
        """Validate evaluation results before ranking."""
        if evaluations is None:
            raise ForecastEvaluationError(
                "evaluations cannot be None."
            )

        if isinstance(evaluations, (str, bytes)):
            raise ForecastEvaluationError(
                "evaluations must be a sequence of "
                "ForecastEvaluationResult objects."
            )

        try:
            results = tuple(evaluations)
        except TypeError as exc:
            raise ForecastEvaluationError(
                "evaluations must be iterable.",
                cause=exc,
            ) from exc

        if not results:
            raise ForecastEvaluationError(
                "At least one evaluation result is required."
            )

        model_names: set[str] = set()

        for index, result in enumerate(results):
            if not isinstance(
                result,
                ForecastEvaluationResult,
            ):
                raise ForecastEvaluationError(
                    "Every comparison item must be a "
                    "ForecastEvaluationResult.",
                    context={
                        "index": index,
                        "received_type": type(result).__name__,
                    },
                )

            if not result.succeeded:
                raise ForecastEvaluationError(
                    "Only successful evaluation results can be compared.",
                    context={
                        "model_name": result.model_name,
                        "status": result.status.value,
                    },
                )

            normalized_model_name = (
                result.model_name.strip().lower()
            )

            if not normalized_model_name:
                raise ForecastEvaluationError(
                    "Evaluation model_name must not be empty.",
                    context={
                        "index": index,
                    },
                )

            if normalized_model_name in model_names:
                raise ForecastEvaluationError(
                    "Duplicate model names are not allowed in one comparison.",
                    context={
                        "model_name": result.model_name,
                    },
                )

            model_names.add(normalized_model_name)

            if metric not in result.metrics:
                raise ForecastEvaluationError(
                    "Evaluation result is missing the comparison metric.",
                    context={
                        "model_name": result.model_name,
                        "metric": metric,
                    },
                )

            metric_value = result.metrics[metric]

            if isinstance(metric_value, bool) or not isinstance(
                metric_value,
                (int, float),
            ):
                raise ForecastEvaluationError(
                    "Comparison metric value must be numeric.",
                    context={
                        "model_name": result.model_name,
                        "metric": metric,
                        "received_type": type(
                            metric_value
                        ).__name__,
                    },
                )

            if not math.isfinite(float(metric_value)):
                raise ForecastEvaluationError(
                    "Comparison metric value must be finite.",
                    context={
                        "model_name": result.model_name,
                        "metric": metric,
                    },
                )

        return results

    @staticmethod
    def _ranking_key(
        *,
        result: ForecastEvaluationResult,
        metric: str,
    ) -> tuple[float, str, str, str]:
        """Build the deterministic model-ranking key."""
        metric_value = float(result.metrics[metric])

        score = (
            abs(metric_value)
            if metric == "bias"
            else metric_value
        )

        return (
            score,
            result.model_name.strip().lower(),
            result.model_version.strip().lower(),
            result.result_id,
        )


__all__ = [
    "EnterpriseForecastComparison",
    "ForecastComparisonResult",
]