"""
Enterprise Capacity Planning — Configuration

Validated configuration contract used by the Enterprise Capacity
Planning Engine.

The configuration remains independent from Spark, forecasting
algorithms, persistence, and reporting concerns.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from src.workforce.constants import (
    DEFAULT_FORECAST_CONFIDENCE,
    DEFAULT_MAXIMUM_ASSOCIATES,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_ASSOCIATES,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP,
    DEFAULT_PRODUCTIVITY_LINES_PER_HOUR,
    DEFAULT_SAFETY_BUFFER_RATIO,
    DEFAULT_SCHEDULED_HOURS,
    DEFAULT_TARGET_UTILIZATION,
    MAXIMUM_FORECAST_CONFIDENCE,
    MINIMUM_FORECAST_CONFIDENCE,
)
from src.workforce.exceptions import WorkforceConfigurationError


# ============================================================
# Planning Strategy
# ============================================================

class CapacityPlanningStrategy(str, Enum):
    """
    Supported enterprise capacity-planning strategies.

    Attributes
    ----------
    STANDARD:
        Uses expected workload, scheduled capacity, utilization target,
        and configured safety buffer.

    CONSERVATIVE:
        Applies additional planning protection for higher operational
        uncertainty.

    AGGRESSIVE:
        Plans closer to maximum workforce utilization with a reduced
        operational buffer.
    """

    STANDARD = "STANDARD"
    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"


# ============================================================
# Capacity Planning Configuration
# ============================================================

@dataclass(slots=True)
class CapacityPlanningConfiguration:
    """
    Configuration contract for enterprise workforce capacity planning.

    Parameters
    ----------
    productivity_lines_per_hour:
        Expected number of order lines completed by one associate
        during one productive hour.

    scheduled_hours:
        Standard scheduled working hours available to one associate
        during the planning period.

    target_utilization:
        Maximum proportion of theoretical workforce capacity that
        should be treated as operationally available.

    safety_buffer_ratio:
        Additional workload buffer applied to protect operations from
        forecast uncertainty and normal execution variability.

    minimum_associates:
        Minimum workforce requirement permitted by the planning engine.

    maximum_associates:
        Maximum workforce requirement permitted by the planning engine.

    minimum_overtime_hours:
        Minimum supported overtime duration per associate.

    maximum_overtime_hours:
        Maximum supported overtime duration per associate.

    overtime_trigger_associate_gap:
        Minimum associate shortage that makes the result eligible for
        downstream overtime evaluation.

    default_forecast_confidence:
        Default forecast confidence used when an upstream forecasting
        result does not provide one.

    planning_strategy:
        Planning strategy controlling the operational risk posture.

    configuration_version:
        Semantic version identifying the configuration contract.
    """

    productivity_lines_per_hour: float = (
        DEFAULT_PRODUCTIVITY_LINES_PER_HOUR
    )

    scheduled_hours: float = DEFAULT_SCHEDULED_HOURS

    target_utilization: float = DEFAULT_TARGET_UTILIZATION

    safety_buffer_ratio: float = DEFAULT_SAFETY_BUFFER_RATIO

    minimum_associates: int = DEFAULT_MINIMUM_ASSOCIATES

    maximum_associates: int = DEFAULT_MAXIMUM_ASSOCIATES

    minimum_overtime_hours: float = DEFAULT_MINIMUM_OVERTIME_HOURS

    maximum_overtime_hours: float = DEFAULT_MAXIMUM_OVERTIME_HOURS

    overtime_trigger_associate_gap: int = (
        DEFAULT_OVERTIME_TRIGGER_ASSOCIATE_GAP
    )

    default_forecast_confidence: float = DEFAULT_FORECAST_CONFIDENCE

    planning_strategy: CapacityPlanningStrategy = (
        CapacityPlanningStrategy.STANDARD
    )

    configuration_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the complete capacity-planning configuration.

        Raises
        ------
        WorkforceConfigurationError
            If any configuration value violates the planning contract.
        """

        self._validate_positive_float(
            name="productivity_lines_per_hour",
            value=self.productivity_lines_per_hour,
        )
        self._validate_positive_float(
            name="scheduled_hours",
            value=self.scheduled_hours,
        )

        if not 0 < self.target_utilization <= 1:
            raise WorkforceConfigurationError(
                "target_utilization must be greater than 0 and less "
                "than or equal to 1."
            )

        if not 0 <= self.safety_buffer_ratio < 1:
            raise WorkforceConfigurationError(
                "safety_buffer_ratio must be greater than or equal to "
                "0 and less than 1."
            )

        if self.minimum_associates < 0:
            raise WorkforceConfigurationError(
                "minimum_associates must be non-negative."
            )

        if self.maximum_associates <= 0:
            raise WorkforceConfigurationError(
                "maximum_associates must be greater than 0."
            )

        if self.minimum_associates > self.maximum_associates:
            raise WorkforceConfigurationError(
                "minimum_associates cannot exceed maximum_associates."
            )

        self._validate_positive_float(
            name="minimum_overtime_hours",
            value=self.minimum_overtime_hours,
        )
        self._validate_positive_float(
            name="maximum_overtime_hours",
            value=self.maximum_overtime_hours,
        )

        if self.minimum_overtime_hours > self.maximum_overtime_hours:
            raise WorkforceConfigurationError(
                "minimum_overtime_hours cannot exceed "
                "maximum_overtime_hours."
            )

        if self.overtime_trigger_associate_gap < 1:
            raise WorkforceConfigurationError(
                "overtime_trigger_associate_gap must be at least 1."
            )

        if not (
            MINIMUM_FORECAST_CONFIDENCE
            <= self.default_forecast_confidence
            <= MAXIMUM_FORECAST_CONFIDENCE
        ):
            raise WorkforceConfigurationError(
                "default_forecast_confidence must be between "
                f"{MINIMUM_FORECAST_CONFIDENCE} and "
                f"{MAXIMUM_FORECAST_CONFIDENCE}."
            )

        if not isinstance(
            self.planning_strategy,
            CapacityPlanningStrategy,
        ):
            raise WorkforceConfigurationError(
                "planning_strategy must be a CapacityPlanningStrategy."
            )

        if not self.configuration_version.strip():
            raise WorkforceConfigurationError(
                "configuration_version must not be empty."
            )

    @property
    def productive_hours_per_associate(self) -> float:
        """
        Return effective productive hours per scheduled associate.

        Target utilization reduces theoretical scheduled hours to the
        capacity expected to be operationally achievable.
        """

        return self.scheduled_hours * self.target_utilization

    @property
    def effective_lines_per_associate(self) -> float:
        """
        Return expected order-line capacity per associate.

        The value reflects productivity, scheduled hours, and target
        utilization before applying workload safety buffers.
        """

        return (
            self.productivity_lines_per_hour
            * self.productive_hours_per_associate
        )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        payload = asdict(self)
        payload["planning_strategy"] = self.planning_strategy.value

        return payload

    @staticmethod
    def _validate_positive_float(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate that a numeric configuration value is positive.
        """

        if value <= 0:
            raise WorkforceConfigurationError(
                f"{name} must be greater than 0."
            )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningConfiguration",
    "CapacityPlanningStrategy",
]