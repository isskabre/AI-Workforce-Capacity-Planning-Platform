"""
Enterprise Staffing Recommendation Models

Typed domain contracts for strategic staffing recommendations.

These models are independent from Spark, persistence, forecasting
algorithms, and user-interface concerns.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from .constants import (
    MAX_FORECAST_CONFIDENCE,
    MIN_FORECAST_CONFIDENCE,
)
from .exceptions import StaffingValidationError


# ============================================================
# Enumerations
# ============================================================

class StaffingRecommendationType(str, Enum):
    """
    Supported strategic staffing recommendation types.
    """

    NONE = "NONE"
    TEMPORARY_LABOR = "TEMPORARY_LABOR"
    FULL_TIME_HIRING = "FULL_TIME_HIRING"
    FULL_TIME_HIRING_REVIEW = "FULL_TIME_HIRING_REVIEW"
    CROSS_TRAIN = "CROSS_TRAIN"
    SHIFT_REALIGNMENT = "SHIFT_REALIGNMENT"
    WORKFORCE_REDUCTION = "WORKFORCE_REDUCTION"


class StaffingRecommendationPriority(str, Enum):
    """
    Business priority assigned to a staffing recommendation.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StaffingRecommendationStatus(str, Enum):
    """
    Lifecycle status of a staffing recommendation.
    """

    NOT_REQUIRED = "NOT_REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"


# ============================================================
# Staffing Request
# ============================================================

@dataclass(slots=True)
class StaffingRequest:
    """
    Input contract for one strategic staffing evaluation.

    Parameters
    ----------
    planning_date:
        Business date associated with the recommendation.

    associate_gap:
        Signed difference between required and available associates.
        Positive values represent a shortage. Negative values represent
        a surplus.

    forecast_confidence:
        Confidence associated with the workforce forecast.

    recurring_shortage_days:
        Number of recent planning periods with a workforce shortage.

    recurring_surplus_days:
        Number of recent planning periods with a workforce surplus.

    overtime_dependency_days:
        Number of recent planning periods dependent on overtime.

    planning_horizon_days:
        Strategic planning horizon represented by the request.
    """

    planning_date: date

    associate_gap: int

    forecast_confidence: float

    recurring_shortage_days: int = 0

    recurring_surplus_days: int = 0

    overtime_dependency_days: int = 0

    planning_horizon_days: int = 30

    def __post_init__(self) -> None:
        """
        Validate the staffing request.
        """

        if not isinstance(self.planning_date, date):
            raise StaffingValidationError(
                "planning_date must be a date."
            )

        if not isinstance(self.associate_gap, int) or isinstance(
            self.associate_gap,
            bool,
        ):
            raise StaffingValidationError(
                "associate_gap must be an integer."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise StaffingValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        self._validate_non_negative_integer(
            name="recurring_shortage_days",
            value=self.recurring_shortage_days,
        )
        self._validate_non_negative_integer(
            name="recurring_surplus_days",
            value=self.recurring_surplus_days,
        )
        self._validate_non_negative_integer(
            name="overtime_dependency_days",
            value=self.overtime_dependency_days,
        )

        if (
            not isinstance(self.planning_horizon_days, int)
            or isinstance(self.planning_horizon_days, bool)
            or self.planning_horizon_days <= 0
        ):
            raise StaffingValidationError(
                "planning_horizon_days must be a positive integer."
            )

    @property
    def has_shortage(self) -> bool:
        """
        Return whether the request represents a workforce shortage.
        """

        return self.associate_gap > 0

    @property
    def has_surplus(self) -> bool:
        """
        Return whether the request represents a workforce surplus.
        """

        return self.associate_gap < 0

    def as_dict(self) -> dict[str, Any]:
        """
        Return the request as a serializable dictionary.
        """

        payload = asdict(self)
        payload["planning_date"] = self.planning_date.isoformat()

        return payload

    @staticmethod
    def _validate_non_negative_integer(
        *,
        name: str,
        value: int,
    ) -> None:
        """
        Validate a non-negative integer request field.
        """

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise StaffingValidationError(
                f"{name} must be a non-negative integer."
            )


# ============================================================
# Staffing Recommendation
# ============================================================

@dataclass(slots=True)
class StaffingRecommendation:
    """
    Enterprise strategic staffing recommendation.

    Parameters
    ----------
    planning_date:
        Business date associated with the recommendation.

    recommendation:
        Standardized staffing recommendation type.

    priority:
        Business priority of the recommendation.

    status:
        Recommendation lifecycle status.

    associate_gap:
        Signed workforce gap used by the recommendation.

    recommended_associates:
        Number of associates associated with the recommendation.

    forecast_confidence:
        Forecast confidence used by the staffing engine.

    rationale:
        Human-readable explanation of the recommendation.

    generated_at_utc:
        UTC timestamp identifying recommendation generation.

    recommendation_version:
        Semantic version of the recommendation contract.
    """

    planning_date: date

    recommendation: StaffingRecommendationType

    priority: StaffingRecommendationPriority

    status: StaffingRecommendationStatus

    associate_gap: int

    recommended_associates: int

    forecast_confidence: float

    rationale: str

    generated_at_utc: datetime

    recommendation_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the staffing recommendation.
        """

        if not isinstance(self.planning_date, date):
            raise StaffingValidationError(
                "planning_date must be a date."
            )

        if not isinstance(
            self.recommendation,
            StaffingRecommendationType,
        ):
            raise StaffingValidationError(
                "recommendation must be a "
                "StaffingRecommendationType."
            )

        if not isinstance(
            self.priority,
            StaffingRecommendationPriority,
        ):
            raise StaffingValidationError(
                "priority must be a StaffingRecommendationPriority."
            )

        if not isinstance(
            self.status,
            StaffingRecommendationStatus,
        ):
            raise StaffingValidationError(
                "status must be a StaffingRecommendationStatus."
            )

        if not isinstance(self.associate_gap, int) or isinstance(
            self.associate_gap,
            bool,
        ):
            raise StaffingValidationError(
                "associate_gap must be an integer."
            )

        if (
            not isinstance(self.recommended_associates, int)
            or isinstance(self.recommended_associates, bool)
            or self.recommended_associates < 0
        ):
            raise StaffingValidationError(
                "recommended_associates must be a non-negative integer."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise StaffingValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        if not self.rationale.strip():
            raise StaffingValidationError(
                "rationale must not be empty."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise StaffingValidationError(
                "generated_at_utc must be a datetime."
            )

        if not self.recommendation_version.strip():
            raise StaffingValidationError(
                "recommendation_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the recommendation as a serializable dictionary.
        """

        return {
            "planning_date": self.planning_date.isoformat(),
            "recommendation": self.recommendation.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "associate_gap": self.associate_gap,
            "recommended_associates": self.recommended_associates,
            "forecast_confidence": self.forecast_confidence,
            "rationale": self.rationale,
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "recommendation_version": self.recommendation_version,
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "StaffingRecommendation",
    "StaffingRecommendationPriority",
    "StaffingRecommendationStatus",
    "StaffingRecommendationType",
    "StaffingRequest",
]