"""
Enterprise Overtime Recommendation Models

Enterprise domain models for overtime recommendation.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .constants import (
    MAXIMUM_RECOMMENDATION_CONFIDENCE,
    MINIMUM_RECOMMENDATION_CONFIDENCE,
)
from .exceptions import (
    OvertimeValidationError,
)


# ============================================================
# Enumerations
# ============================================================


class RecommendationType(str, Enum):
    """Enterprise recommendation categories."""

    NONE = "NONE"
    VOLUNTARY_OVERTIME = "VOLUNTARY_OVERTIME"
    MANDATORY_OVERTIME = "MANDATORY_OVERTIME"
    TEMPORARY_LABOR = "TEMPORARY_LABOR"
    FULL_TIME_HIRING_REVIEW = "FULL_TIME_HIRING_REVIEW"
    OPERATIONAL_REVIEW = "OPERATIONAL_REVIEW"


class RecommendationPriority(str, Enum):
    """Business priority."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationStatus(str, Enum):
    """Recommendation lifecycle."""

    NOT_REQUIRED = "NOT_REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    REQUIRED = "REQUIRED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class OvertimeType(str, Enum):
    """Overtime classification."""

    NONE = "NONE"
    VOLUNTARY = "VOLUNTARY"
    MANDATORY = "MANDATORY"


# ============================================================
# Request
# ============================================================


@dataclass(frozen=True, slots=True)
class OvertimeRequest:
    """
    Planning request supplied to the overtime engine.
    """

    planning_date: date

    associate_gap: int

    forecast_confidence: float


    def __post_init__(self) -> None:

        if self.associate_gap < 0:
            raise OvertimeValidationError(
                "associate_gap must be >= 0."
            )

        if not (
            MINIMUM_RECOMMENDATION_CONFIDENCE
            <= self.forecast_confidence
            <= MAXIMUM_RECOMMENDATION_CONFIDENCE
        ):
            raise OvertimeValidationError(
                "forecast_confidence must be between 0 and 1."
            )


# ============================================================
# Recommendation
# ============================================================


@dataclass(frozen=True, slots=True)
class OvertimeRecommendation:
    """
    Enterprise overtime recommendation.
    """

    planning_date: date

    recommendation: RecommendationType

    priority: RecommendationPriority

    status: RecommendationStatus

    overtime_type: OvertimeType

    overtime_hours: float

    associate_gap: int

    forecast_confidence: float

    rationale: str


    def __post_init__(self) -> None:

        if self.overtime_hours < 0:
            raise OvertimeValidationError(
                "overtime_hours cannot be negative."
            )

        if self.associate_gap < 0:
            raise OvertimeValidationError(
                "associate_gap cannot be negative."
            )

        if not (
            MINIMUM_RECOMMENDATION_CONFIDENCE
            <= self.forecast_confidence
            <= MAXIMUM_RECOMMENDATION_CONFIDENCE
        ):
            raise OvertimeValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        if not self.rationale.strip():
            raise OvertimeValidationError(
                "rationale cannot be empty."
            )


__all__ = [
    "RecommendationPriority",
    "RecommendationStatus",
    "RecommendationType",
    "OvertimeRecommendation",
    "OvertimeRequest",
    "OvertimeType",
]