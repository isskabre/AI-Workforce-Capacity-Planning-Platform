"""
Enterprise Forecast Training Callbacks.

Defines extensible lifecycle hooks for the enterprise
forecast training framework.
"""

from __future__ import annotations

from typing import Any


class TrainingCallback:
    """
    Base callback for forecast training lifecycle events.
    """

    def on_training_started(
        self,
        *,
        model: Any,
        context: Any,
    ) -> None:
        """
        Called before training starts.
        """
        return None

    def on_epoch_completed(
        self,
        *,
        epoch: int,
        metrics: dict[str, Any],
    ) -> None:
        """
        Called after each epoch.
        """
        return None

    def on_training_completed(
        self,
        *,
        model: Any,
        artifact: Any,
    ) -> None:
        """
        Called after successful training.
        """
        return None

    def on_training_failed(
        self,
        *,
        model: Any,
        exception: Exception,
    ) -> None:
        """
        Called when training fails.
        """
        return None