"""
Enterprise Staffing Recommendation Configuration

Validated configuration contract for strategic staffing decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import (
    CRITICAL_SHORTAGE_GAP,
    DEFAULT_FORECAST_CONFIDENCE,
    FULL_TIME_HIRING_TRIGGER_GAP,
    HIGH_CONFIDENCE_THRESHOLD,
    LOW_CONFIDENCE_THRESHOLD,
    MINIMUM_ASSOCIATE_GAP,
    TEMPORARY_LABOR_TRIGGER_GAP,
)
from .exceptions import StaffingConfigurationError


@dataclass(slots=True)
class StaffingConfiguration:
    """
    Strategic staffing policy configuration.
    """

    minimum_associate_gap: int = MINIMUM_ASSOCIATE_GAP

    temporary_labor_trigger_gap: int = (
        TEMPORARY_LABOR_TRIGGER_GAP
    )

    full_time_hiring_trigger_gap: int = (
        FULL_TIME_HIRING_TRIGGER_GAP
    )

    critical_shortage_gap: int = CRITICAL_SHORTAGE_GAP

    minimum_recurring_shortage_days: int = 5

    full_time_hiring_shortage_days: int = 15

    minimum_recurring_surplus_days: int = 10

    minimum_overtime_dependency_days: int = 10

    default_forecast_confidence: float = (
        DEFAULT_FORECAST_CONFIDENCE
    )

    low_confidence_threshold: float = LOW_CONFIDENCE_THRESHOLD

    high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD

    configuration_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the complete staffing policy configuration.
        """

        self._validate_positive_integer(
            name="minimum_associate_gap",
            value=self.minimum_associate_gap,
        )
        self._validate_positive_integer(
            name="temporary_labor_trigger_gap",
            value=self.temporary_labor_trigger_gap,
        )
        self._validate_positive_integer(
            name="full_time_hiring_trigger_gap",
            value=self.full_time_hiring_trigger_gap,
        )
        self._validate_positive_integer(
            name="critical_shortage_gap",
            value=self.critical_shortage_gap,
        )

        if (
            self.minimum_associate_gap
            >= self.temporary_labor_trigger_gap
        ):
            raise StaffingConfigurationError(
                "minimum_associate_gap must be less than "
                "temporary_labor_trigger_gap."
            )

        if (
            self.temporary_labor_trigger_gap
            >= self.full_time_hiring_trigger_gap
        ):
            raise StaffingConfigurationError(
                "temporary_labor_trigger_gap must be less than "
                "full_time_hiring_trigger_gap."
            )

        if (
            self.full_time_hiring_trigger_gap
            >= self.critical_shortage_gap
        ):
            raise StaffingConfigurationError(
                "full_time_hiring_trigger_gap must be less than "
                "critical_shortage_gap."
            )

        self._validate_non_negative_integer(
            name="minimum_recurring_shortage_days",
            value=self.minimum_recurring_shortage_days,
        )
        self._validate_non_negative_integer(
            name="full_time_hiring_shortage_days",
            value=self.full_time_hiring_shortage_days,
        )
        self._validate_non_negative_integer(
            name="minimum_recurring_surplus_days",
            value=self.minimum_recurring_surplus_days,
        )
        self._validate_non_negative_integer(
            name="minimum_overtime_dependency_days",
            value=self.minimum_overtime_dependency_days,
        )

        if (
            self.minimum_recurring_shortage_days
            > self.full_time_hiring_shortage_days
        ):
            raise StaffingConfigurationError(
                "minimum_recurring_shortage_days cannot exceed "
                "full_time_hiring_shortage_days."
            )

        self._validate_confidence(
            name="default_forecast_confidence",
            value=self.default_forecast_confidence,
        )
        self._validate_confidence(
            name="low_confidence_threshold",
            value=self.low_confidence_threshold,
        )
        self._validate_confidence(
            name="high_confidence_threshold",
            value=self.high_confidence_threshold,
        )

        if (
            self.low_confidence_threshold
            >= self.high_confidence_threshold
        ):
            raise StaffingConfigurationError(
                "low_confidence_threshold must be less than "
                "high_confidence_threshold."
            )

        if not self.configuration_version.strip():
            raise StaffingConfigurationError(
                "configuration_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        return asdict(self)

    @staticmethod
    def _validate_positive_integer(
        *,
        name: str,
        value: int,
    ) -> None:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise StaffingConfigurationError(
                f"{name} must be a positive integer."
            )

    @staticmethod
    def _validate_non_negative_integer(
        *,
        name: str,
        value: int,
    ) -> None:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise StaffingConfigurationError(
                f"{name} must be a non-negative integer."
            )

    @staticmethod
    def _validate_confidence(
        *,
        name: str,
        value: float,
    ) -> None:
        if not 0.0 <= value <= 1.0:
            raise StaffingConfigurationError(
                f"{name} must be between 0 and 1."
            )


__all__ = [
    "StaffingConfiguration",
]