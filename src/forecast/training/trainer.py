"""
AI Workforce Capacity Planning Platform
Implementation 13 - Enterprise Training Framework

Module:
    forecast.training.trainer

Description:
    Defines the algorithm-agnostic enterprise trainer responsible for
    orchestrating the training lifecycle of one forecasting model.

    The trainer validates the model and training context, optionally resets
    existing runtime state, delegates execution to the forecasting model,
    validates the returned training result, and exposes consistent enterprise
    error handling.

Architecture:
    Enterprise Forecast Training Framework

Version:
    2.5.0
"""

from __future__ import annotations

from src.forecast.algorithms.base.forecast_model import (
    EnterpriseForecastModel,
)
from src.forecast.modeling.contexts import (
    ForecastTrainingContext,
)
from src.forecast.modeling.contracts import (
    ForecastModelState,
)
from src.forecast.modeling.exceptions import (
    ForecastTrainingError,
)
from src.forecast.modeling.results import (
    ForecastTrainingResult,
)


class EnterpriseForecastTrainer:
    """
    Stateless orchestration service for training one forecasting model.

    The trainer does not call an estimator directly. It delegates training
    through ``EnterpriseForecastModel.train`` so that each model preserves
    its own lifecycle, estimator integration, metadata, and result contracts.

    The class is algorithm-agnostic and supports every forecasting model
    implementing ``EnterpriseForecastModel``.

    Examples:
        Train a newly created model:

        >>> trainer = EnterpriseForecastTrainer()
        >>> result = trainer.train(
        ...     model=model,
        ...     context=training_context,
        ... )

        Retrain an existing model after resetting its runtime state:

        >>> result = trainer.train(
        ...     model=model,
        ...     context=training_context,
        ...     reset_existing=True,
        ... )
    """

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
        Train one enterprise forecasting model.

        Args:
            model:
                Forecasting model implementing the enterprise model contract.

            context:
                Immutable training context containing the training dataset,
                optional validation dataset, feature columns, target column,
                forecast horizon, configuration, and execution metadata.

            reset_existing:
                Whether to reset an existing model before training.

                When ``False``, only a model in the ``CREATED`` state may be
                trained. This prevents accidental destruction of an existing
                fitted model.

                When ``True``, the model is reset before training when its
                current state is not ``CREATED``.

        Returns:
            The standardized ``ForecastTrainingResult`` returned by the model.

        Raises:
            ForecastTrainingError:
                If validation fails, the model is in an invalid lifecycle
                state, model training fails, or an invalid result is returned.
        """
        self._validate_model(model)
        self._validate_context(context)
        self._validate_reset_existing(reset_existing)

        self._prepare_model(
            model=model,
            reset_existing=reset_existing,
        )

        try:
            result = model.train(context)

        except ForecastTrainingError:
            raise

        except Exception as exc:
            raise ForecastTrainingError(
                "Enterprise forecast training execution failed.",
                context={
                    "model_key": model.model_key,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "model_state": model.state.value,
                    "forecast_horizon": context.forecast_horizon,
                    "target_column": context.target_column,
                },
                cause=exc,
            ) from exc

        self._validate_training_result(
            model=model,
            result=result,
        )

        return result

    # ------------------------------------------------------------------
    # Request validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_model(
        model: EnterpriseForecastModel,
    ) -> None:
        """Validate the supplied forecasting model."""
        if model is None:
            raise ForecastTrainingError(
                "Forecasting model cannot be None.",
                context={
                    "argument": "model",
                },
            )

        if not isinstance(
            model,
            EnterpriseForecastModel,
        ):
            raise ForecastTrainingError(
                "model must be an EnterpriseForecastModel.",
                context={
                    "argument": "model",
                    "received_type": type(model).__name__,
                },
            )

    @staticmethod
    def _validate_context(
        context: ForecastTrainingContext,
    ) -> None:
        """Validate the supplied training context."""
        if context is None:
            raise ForecastTrainingError(
                "Forecast training context cannot be None.",
                context={
                    "argument": "context",
                },
            )

        if not isinstance(
            context,
            ForecastTrainingContext,
        ):
            raise ForecastTrainingError(
                "context must be a ForecastTrainingContext.",
                context={
                    "argument": "context",
                    "received_type": type(context).__name__,
                },
            )

        if context.training_dataset is None:
            raise ForecastTrainingError(
                "Training dataset cannot be None.",
                context={
                    "argument": "context.training_dataset",
                },
            )

        if not isinstance(
            context.forecast_horizon,
            int,
        ):
            raise ForecastTrainingError(
                "Forecast horizon must be an integer.",
                context={
                    "forecast_horizon": (
                        context.forecast_horizon
                    ),
                },
            )

        if context.forecast_horizon <= 0:
            raise ForecastTrainingError(
                "Forecast horizon must be greater than zero.",
                context={
                    "forecast_horizon": (
                        context.forecast_horizon
                    ),
                },
            )

    @staticmethod
    def _validate_reset_existing(
        reset_existing: bool,
    ) -> None:
        """Validate the reset behavior flag."""
        if not isinstance(reset_existing, bool):
            raise ForecastTrainingError(
                "reset_existing must be a boolean.",
                context={
                    "argument": "reset_existing",
                    "received_type": (
                        type(reset_existing).__name__
                    ),
                },
            )

    # ------------------------------------------------------------------
    # Lifecycle preparation
    # ------------------------------------------------------------------

    @staticmethod
    def _prepare_model(
        *,
        model: EnterpriseForecastModel,
        reset_existing: bool,
    ) -> None:
        """
        Prepare the forecasting model for a new training execution.

        Existing model state is preserved by default. An explicit
        ``reset_existing=True`` request is required before retraining.
        """
        if model.state == ForecastModelState.CREATED:
            return

        if reset_existing:
            model.reset()

            if model.state != ForecastModelState.CREATED:
                raise ForecastTrainingError(
                    "Forecast model reset did not restore the CREATED state.",
                    context={
                        "model_key": model.model_key,
                        "model_state": model.state.value,
                    },
                )

            return

        raise ForecastTrainingError(
            "Forecast model is not in the CREATED state. "
            "Set reset_existing=True to retrain it.",
            context={
                "model_key": model.model_key,
                "model_name": model.model_name,
                "model_state": model.state.value,
            },
        )

    # ------------------------------------------------------------------
    # Result validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_training_result(
        *,
        model: EnterpriseForecastModel,
        result: ForecastTrainingResult,
    ) -> None:
        """Validate the model's standardized training result."""
        if not isinstance(
            result,
            ForecastTrainingResult,
        ):
            raise ForecastTrainingError(
                "Forecast model returned an invalid training result.",
                context={
                    "model_key": model.model_key,
                    "expected_type": (
                        "ForecastTrainingResult"
                    ),
                    "received_type": type(result).__name__,
                },
            )

        if not result.succeeded:
            raise ForecastTrainingError(
                "Forecast model returned an unsuccessful training result.",
                context={
                    "model_key": model.model_key,
                    "model_name": model.model_name,
                    "result_status": result.status.value,
                },
            )

        if model.state != ForecastModelState.TRAINED:
            raise ForecastTrainingError(
                "Forecast model did not transition to the TRAINED state.",
                context={
                    "model_key": model.model_key,
                    "model_state": model.state.value,
                },
            )

        if model.training_context is None:
            raise ForecastTrainingError(
                "Trained forecast model does not contain a training context.",
                context={
                    "model_key": model.model_key,
                },
            )


__all__ = [
    "EnterpriseForecastTrainer",
]