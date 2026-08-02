"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Training Framework

Module:
    forecast.training.orchestrator

Description:
    Coordinates deterministic training of multiple enterprise forecasting
    models through EnterpriseForecastTrainer.

    The orchestrator validates aligned model and context collections,
    delegates each training execution to the trainer, preserves execution
    order, and applies a consistent failure policy.

Architecture:
    Enterprise Forecast Training Framework

Version:
    2.5.0
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from forecast.algorithms.base.forecast_model import (
    EnterpriseForecastModel,
)
from forecast.modeling.contexts import (
    ForecastTrainingContext,
)
from forecast.modeling.exceptions import (
    ForecastTrainingError,
)
from forecast.modeling.results import (
    ForecastTrainingResult,
)
from forecast.training.trainer import (
    EnterpriseForecastTrainer,
)


class EnterpriseForecastTrainingOrchestrator:
    """
    Coordinate training across multiple enterprise forecasting models.

    The orchestrator contains no algorithm-specific behavior. Every model
    execution is delegated to ``EnterpriseForecastTrainer``, which then
    delegates lifecycle execution to ``EnterpriseForecastModel.train``.

    Model and context collections must use matching execution keys:

        models = {
            "naive": naive_model,
            "linear_regression": linear_model,
        }

        contexts = {
            "naive": naive_context,
            "linear_regression": linear_context,
        }

    Training occurs sequentially in mapping insertion order. Sequential
    execution provides deterministic behavior and avoids hidden concurrency
    concerns during this implementation phase.
    """

    def __init__(
        self,
        *,
        trainer: EnterpriseForecastTrainer | None = None,
    ) -> None:
        """
        Initialize the training orchestrator.

        Args:
            trainer:
                Optional trainer dependency. When omitted, a default
                ``EnterpriseForecastTrainer`` is created.
        """
        if trainer is not None and not isinstance(
            trainer,
            EnterpriseForecastTrainer,
        ):
            raise ForecastTrainingError(
                "trainer must be an EnterpriseForecastTrainer.",
                context={
                    "argument": "trainer",
                    "received_type": type(trainer).__name__,
                },
            )

        self._trainer = (
            trainer
            if trainer is not None
            else EnterpriseForecastTrainer()
        )

    @property
    def trainer(self) -> EnterpriseForecastTrainer:
        """Return the trainer used for delegated executions."""
        return self._trainer

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(
        self,
        *,
        model: EnterpriseForecastModel,
        context: ForecastTrainingContext,
        reset_existing: bool = False,
    ) -> ForecastTrainingResult:
        """
        Train one model through the configured trainer.

        This convenience method preserves one consistent entry point for
        callers that may execute either single-model or multi-model training.
        """
        return self.trainer.train(
            model=model,
            context=context,
            reset_existing=reset_existing,
        )

    def train_many(
        self,
        *,
        models: Mapping[str, EnterpriseForecastModel],
        contexts: Mapping[str, ForecastTrainingContext],
        reset_existing: bool = False,
    ) -> Mapping[str, ForecastTrainingResult]:
        """
        Train multiple forecasting models sequentially.

        Args:
            models:
                Mapping of stable execution keys to forecast models.

            contexts:
                Mapping of the same execution keys to training contexts.

            reset_existing:
                Whether non-created models should be reset before training.

        Returns:
            Read-only mapping of execution keys to successful training results.

        Raises:
            ForecastTrainingError:
                If the request is invalid or any delegated training execution
                fails. Training stops immediately on the first failure.
        """
        self._validate_collections(
            models=models,
            contexts=contexts,
        )

        results: dict[str, ForecastTrainingResult] = {}

        for execution_key, model in models.items():
            context = contexts[execution_key]

            try:
                results[execution_key] = self.trainer.train(
                    model=model,
                    context=context,
                    reset_existing=reset_existing,
                )

            except ForecastTrainingError as exc:
                raise ForecastTrainingError(
                    "Enterprise forecast training orchestration failed.",
                    context={
                        "execution_key": execution_key,
                        "model_key": (
                            model.model_key
                            if isinstance(
                                model,
                                EnterpriseForecastModel,
                            )
                            else None
                        ),
                        "completed_executions": tuple(
                            results
                        ),
                        "requested_executions": tuple(
                            models
                        ),
                    },
                    cause=exc,
                ) from exc

            except Exception as exc:
                raise ForecastTrainingError(
                    "Unexpected forecast training orchestration failure.",
                    context={
                        "execution_key": execution_key,
                        "completed_executions": tuple(
                            results
                        ),
                        "requested_executions": tuple(
                            models
                        ),
                    },
                    cause=exc,
                ) from exc

        return MappingProxyType(results)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_collections(
        *,
        models: Mapping[str, EnterpriseForecastModel],
        contexts: Mapping[str, ForecastTrainingContext],
    ) -> None:
        """Validate aligned model and training-context collections."""
        if not isinstance(models, Mapping):
            raise ForecastTrainingError(
                "models must be a mapping.",
                context={
                    "argument": "models",
                    "received_type": type(models).__name__,
                },
            )

        if not isinstance(contexts, Mapping):
            raise ForecastTrainingError(
                "contexts must be a mapping.",
                context={
                    "argument": "contexts",
                    "received_type": type(contexts).__name__,
                },
            )

        if not models:
            raise ForecastTrainingError(
                "models must contain at least one training execution.",
                context={
                    "argument": "models",
                },
            )

        if not contexts:
            raise ForecastTrainingError(
                "contexts must contain at least one training execution.",
                context={
                    "argument": "contexts",
                },
            )

        model_keys = tuple(models)
        context_keys = tuple(contexts)

        if set(model_keys) != set(context_keys):
            raise ForecastTrainingError(
                "Model and context execution keys must match.",
                context={
                    "model_keys": model_keys,
                    "context_keys": context_keys,
                    "missing_context_keys": tuple(
                        key
                        for key in model_keys
                        if key not in contexts
                    ),
                    "unexpected_context_keys": tuple(
                        key
                        for key in context_keys
                        if key not in models
                    ),
                },
            )

        for execution_key, model in models.items():
            if not isinstance(execution_key, str):
                raise ForecastTrainingError(
                    "Every execution key must be a string.",
                    context={
                        "execution_key": repr(execution_key),
                        "received_type": (
                            type(execution_key).__name__
                        ),
                    },
                )

            if not execution_key.strip():
                raise ForecastTrainingError(
                    "Execution keys must not be empty.",
                    context={
                        "execution_key": execution_key,
                    },
                )

            if not isinstance(
                model,
                EnterpriseForecastModel,
            ):
                raise ForecastTrainingError(
                    "Every model must be an EnterpriseForecastModel.",
                    context={
                        "execution_key": execution_key,
                        "received_type": type(model).__name__,
                    },
                )

            context = contexts[execution_key]

            if not isinstance(
                context,
                ForecastTrainingContext,
            ):
                raise ForecastTrainingError(
                    "Every context must be a ForecastTrainingContext.",
                    context={
                        "execution_key": execution_key,
                        "received_type": (
                            type(context).__name__
                        ),
                    },
                )


__all__ = [
    "EnterpriseForecastTrainingOrchestrator",
]