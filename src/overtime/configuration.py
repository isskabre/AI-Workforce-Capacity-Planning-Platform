"""
Enterprise Overtime Recommendation — Configuration

Validated policy configuration used by the Enterprise Overtime
Recommendation Engine.

This module centralizes overtime duration limits, shortage thresholds,
confidence thresholds, and recommendation policy defaults.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import (
    DEFAULT_CRITICAL_SHORTAGE_GAP,
    DEFAULT_HIGH_CONFIDENCE_THRESHOLD,
    DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_MANDATORY_OVERTIME_MAX_GAP,
    DEFAULT_MAXIMUM_OVERTIME_HOURS,
    DEFAULT_MINIMUM_OVERTIME_HOURS,
    DEFAULT_RECOMMENDATION_CONFIDENCE,
    DEFAULT_STANDARD_OVERTIME_HOURS,
    DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP,
    DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP,
    MAXIMUM_RECOMMENDATION_CONFIDENCE,
    MINIMUM_RECOMMENDATION_CONFIDENCE,
)
from .exceptions import OvertimeConfigurationError


# ============================================================
# Overtime Configuration
# ============================================================

@dataclass(slots=True)
class OvertimeConfiguration:
    """
    Configuration contract for enterprise overtime recommendations.

    Parameters
    ----------
    minimum_overtime_hours:
        Minimum supported overtime duration per associate.

    maximum_overtime_hours:
        Maximum supported overtime duration per associate.

    standard_overtime_hours:
        Default overtime duration used for standard recommendations.

    voluntary_overtime_max_gap:
        Largest associate shortage eligible for voluntary overtime.

    mandatory_overtime_max_gap:
        Largest associate shortage addressed primarily through
        mandatory overtime.

    temporary_labor_trigger_gap:
        Associate shortage at which temporary labor should be reviewed.

    critical_shortage_gap:
        Associate shortage classified as operationally critical.

    default_recommendation_confidence:
        Confidence used when no upstream confidence is provided.

    low_confidence_threshold:
        Confidence below which operational review is required.

    high_confidence_threshold:
        Confidence at or above which a recommendation is considered
        strongly supported.

    configuration_version:
        Semantic version identifying this configuration contract.
    """

    minimum_overtime_hours: float = DEFAULT_MINIMUM_OVERTIME_HOURS

    maximum_overtime_hours: float = DEFAULT_MAXIMUM_OVERTIME_HOURS

    standard_overtime_hours: float = DEFAULT_STANDARD_OVERTIME_HOURS

    voluntary_overtime_max_gap: int = (
        DEFAULT_VOLUNTARY_OVERTIME_MAX_GAP
    )

    mandatory_overtime_max_gap: int = (
        DEFAULT_MANDATORY_OVERTIME_MAX_GAP
    )

    temporary_labor_trigger_gap: int = (
        DEFAULT_TEMPORARY_LABOR_TRIGGER_GAP
    )

    critical_shortage_gap: int = DEFAULT_CRITICAL_SHORTAGE_GAP

    default_recommendation_confidence: float = (
        DEFAULT_RECOMMENDATION_CONFIDENCE
    )

    low_confidence_threshold: float = (
        DEFAULT_LOW_CONFIDENCE_THRESHOLD
    )

    high_confidence_threshold: float = (
        DEFAULT_HIGH_CONFIDENCE_THRESHOLD
    )

    configuration_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the complete overtime policy configuration.

        Raises
        ------
        OvertimeConfigurationError
            If any configuration value violates the policy contract.
        """

        self._validate_positive_float(
            name="minimum_overtime_hours",
            value=self.minimum_overtime_hours,
        )
        self._validate_positive_float(
            name="maximum_overtime_hours",
            value=self.maximum_overtime_hours,
        )
        self._validate_positive_float(
            name="standard_overtime_hours",
            value=self.standard_overtime_hours,
        )

        if self.minimum_overtime_hours > self.maximum_overtime_hours:
            raise OvertimeConfigurationError(
                "minimum_overtime_hours cannot exceed "
                "maximum_overtime_hours."
            )

        if not (
            self.minimum_overtime_hours
            <= self.standard_overtime_hours
            <= self.maximum_overtime_hours
        ):
            raise OvertimeConfigurationError(
                "standard_overtime_hours must be between the minimum "
                "and maximum overtime hours."
            )

        self._validate_positive_integer(
            name="voluntary_overtime_max_gap",
            value=self.voluntary_overtime_max_gap,
        )
        self._validate_positive_integer(
            name="mandatory_overtime_max_gap",
            value=self.mandatory_overtime_max_gap,
        )
        self._validate_positive_integer(
            name="temporary_labor_trigger_gap",
            value=self.temporary_labor_trigger_gap,
        )
        self._validate_positive_integer(
            name="critical_shortage_gap",
            value=self.critical_shortage_gap,
        )

        if (
            self.voluntary_overtime_max_gap
            >= self.temporary_labor_trigger_gap
        ):
            raise OvertimeConfigurationError(
                "voluntary_overtime_max_gap must be less than "
                "temporary_labor_trigger_gap."
            )

        if (
            self.mandatory_overtime_max_gap
            >= self.temporary_labor_trigger_gap
        ):
            raise OvertimeConfigurationError(
                "mandatory_overtime_max_gap must be less than "
                "temporary_labor_trigger_gap."
            )

        if (
            self.temporary_labor_trigger_gap
            >= self.critical_shortage_gap
        ):
            raise OvertimeConfigurationError(
                "temporary_labor_trigger_gap must be less than "
                "critical_shortage_gap."
            )

        self._validate_confidence(
            name="default_recommendation_confidence",
            value=self.default_recommendation_confidence,
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
            raise OvertimeConfigurationError(
                "low_confidence_threshold must be less than "
                "high_confidence_threshold."
            )

        if not self.configuration_version.strip():
            raise OvertimeConfigurationError(
                "configuration_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        return asdict(self)

    @staticmethod
    def _validate_positive_float(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate that a numeric value is greater than zero.
        """

        if value <= 0:
            raise OvertimeConfigurationError(
                f"{name} must be greater than 0."
            )

    @staticmethod
    def _validate_positive_integer(
        *,
        name: str,
        value: int,
    ) -> None:
        """
        Validate that a value is a positive integer.
        """

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise OvertimeConfigurationError(
                f"{name} must be a positive integer."
            )

    @staticmethod
    def _validate_confidence(
        *,
        name: str,
        value: float,
    ) -> None:
        """
        Validate a recommendation confidence value.
        """

        if not (
            MINIMUM_RECOMMENDATION_CONFIDENCE
            <= value
            <= MAXIMUM_RECOMMENDATION_CONFIDENCE
        ):
            raise OvertimeConfigurationError(
                f"{name} must be between "
                f"{MINIMUM_RECOMMENDATION_CONFIDENCE} and "
                f"{MAXIMUM_RECOMMENDATION_CONFIDENCE}."
            )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "OvertimeConfiguration",
]