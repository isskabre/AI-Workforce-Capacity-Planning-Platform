"""
Enterprise Workforce Optimization Configuration

Validated policy configuration for reconciling workforce actions into
one unified optimization decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import DEFAULT_FORECAST_CONFIDENCE
from .exceptions import OptimizationConfigurationError


@dataclass(slots=True)
class WorkforceOptimizationConfiguration:
    """
    Configuration contract for enterprise workforce optimization.
    """

    low_confidence_threshold: float = 0.60

    high_confidence_threshold: float = 0.90

    default_forecast_confidence: float = (
        DEFAULT_FORECAST_CONFIDENCE
    )

    overtime_priority_weight: int = 1

    cross_training_priority_weight: int = 2

    shift_realignment_priority_weight: int = 3

    temporary_labor_priority_weight: int = 4

    full_time_hiring_priority_weight: int = 5

    critical_associate_gap: int = 20

    configuration_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the optimization policy configuration.
        """

        self._validate_confidence(
            name="low_confidence_threshold",
            value=self.low_confidence_threshold,
        )
        self._validate_confidence(
            name="high_confidence_threshold",
            value=self.high_confidence_threshold,
        )
        self._validate_confidence(
            name="default_forecast_confidence",
            value=self.default_forecast_confidence,
        )

        if (
            self.low_confidence_threshold
            >= self.high_confidence_threshold
        ):
            raise OptimizationConfigurationError(
                "low_confidence_threshold must be less than "
                "high_confidence_threshold."
            )

        priority_weights = {
            "overtime_priority_weight": (
                self.overtime_priority_weight
            ),
            "cross_training_priority_weight": (
                self.cross_training_priority_weight
            ),
            "shift_realignment_priority_weight": (
                self.shift_realignment_priority_weight
            ),
            "temporary_labor_priority_weight": (
                self.temporary_labor_priority_weight
            ),
            "full_time_hiring_priority_weight": (
                self.full_time_hiring_priority_weight
            ),
        }

        for name, value in priority_weights.items():
            self._validate_positive_integer(
                name=name,
                value=value,
            )

        if len(set(priority_weights.values())) != len(
            priority_weights
        ):
            raise OptimizationConfigurationError(
                "Optimization priority weights must be unique."
            )

        if not (
            self.overtime_priority_weight
            < self.cross_training_priority_weight
            < self.shift_realignment_priority_weight
            < self.temporary_labor_priority_weight
            < self.full_time_hiring_priority_weight
        ):
            raise OptimizationConfigurationError(
                "Priority weights must increase from overtime through "
                "full-time hiring."
            )

        self._validate_positive_integer(
            name="critical_associate_gap",
            value=self.critical_associate_gap,
        )

        if not self.configuration_version.strip():
            raise OptimizationConfigurationError(
                "configuration_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        return asdict(self)

    @staticmethod
    def _validate_confidence(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate a confidence threshold.
        """

        if not 0.0 <= value <= 1.0:
            raise OptimizationConfigurationError(
                f"{name} must be between 0 and 1."
            )

    @staticmethod
    def _validate_positive_integer(
        *,
        name: str,
        value: int,
    ) -> None:
        """
        Validate a positive integer setting.
        """

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise OptimizationConfigurationError(
                f"{name} must be a positive integer."
            )


__all__ = [
    "WorkforceOptimizationConfiguration",
]