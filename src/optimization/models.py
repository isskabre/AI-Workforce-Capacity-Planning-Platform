"""
Enterprise Workforce Optimization Models

Typed contracts used to reconcile operational and strategic workforce
recommendations into one optimization decision.
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
from .exceptions import OptimizationValidationError


# ============================================================
# Enumerations
# ============================================================

class OptimizationPriority(str, Enum):
    """Business priority of the optimization decision."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OptimizationStatus(str, Enum):
    """Final optimization status."""

    OPTIMAL = "OPTIMAL"
    ACCEPTABLE = "ACCEPTABLE"
    REVIEW = "REVIEW"
    CRITICAL = "CRITICAL"


class WorkforceAction(str, Enum):
    """Supported workforce optimization actions."""

    NONE = "NONE"
    OVERTIME = "OVERTIME"
    TEMPORARY_LABOR = "TEMPORARY_LABOR"
    FULL_TIME_HIRING = "FULL_TIME_HIRING"
    SHIFT_REALIGNMENT = "SHIFT_REALIGNMENT"
    CROSS_TRAINING = "CROSS_TRAINING"


# ============================================================
# Optimization Request
# ============================================================

@dataclass(slots=True)
class WorkforceOptimizationRequest:
    """
    Input contract for one workforce optimization decision.

    Parameters
    ----------
    planning_date:
        Business date being optimized.

    associate_gap:
        Signed workforce gap. Positive values indicate shortage;
        negative values indicate surplus.

    forecast_confidence:
        Confidence associated with the workforce forecast.

    overtime_recommended:
        Whether the overtime engine recommended overtime.

    temporary_labor_recommended:
        Whether temporary labor was recommended.

    full_time_hiring_recommended:
        Whether long-term hiring was recommended.

    shift_realignment_recommended:
        Whether workforce redistribution was recommended.

    cross_training_recommended:
        Whether cross-training was recommended.

    overtime_hours:
        Total overtime labor hours proposed by the overtime engine.

    recommended_associates:
        Number of associates proposed by the staffing engine.
    """

    planning_date: date

    associate_gap: int

    forecast_confidence: float

    overtime_recommended: bool = False

    temporary_labor_recommended: bool = False

    full_time_hiring_recommended: bool = False

    shift_realignment_recommended: bool = False

    cross_training_recommended: bool = False

    overtime_hours: float = 0.0

    recommended_associates: int = 0

    def __post_init__(self) -> None:
        """Validate the optimization request."""

        if not isinstance(self.planning_date, date):
            raise OptimizationValidationError(
                "planning_date must be a date."
            )

        if not isinstance(self.associate_gap, int) or isinstance(
            self.associate_gap,
            bool,
        ):
            raise OptimizationValidationError(
                "associate_gap must be an integer."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise OptimizationValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        boolean_fields = {
            "overtime_recommended": self.overtime_recommended,
            "temporary_labor_recommended": (
                self.temporary_labor_recommended
            ),
            "full_time_hiring_recommended": (
                self.full_time_hiring_recommended
            ),
            "shift_realignment_recommended": (
                self.shift_realignment_recommended
            ),
            "cross_training_recommended": (
                self.cross_training_recommended
            ),
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise OptimizationValidationError(
                    f"{field_name} must be a boolean."
                )

        if self.overtime_hours < 0:
            raise OptimizationValidationError(
                "overtime_hours must be non-negative."
            )

        if (
            not isinstance(self.recommended_associates, int)
            or isinstance(self.recommended_associates, bool)
            or self.recommended_associates < 0
        ):
            raise OptimizationValidationError(
                "recommended_associates must be a non-negative integer."
            )

        if self.associate_gap <= 0 and (
            self.overtime_recommended
            or self.temporary_labor_recommended
            or self.full_time_hiring_recommended
        ):
            raise OptimizationValidationError(
                "Shortage actions cannot be recommended when "
                "associate_gap is zero or negative."
            )

        if not self.overtime_recommended and self.overtime_hours > 0:
            raise OptimizationValidationError(
                "overtime_hours must be zero when overtime is not "
                "recommended."
            )

    @property
    def has_conflicting_actions(self) -> bool:
        """
        Return whether multiple major staffing actions are active.
        """

        major_actions = (
            self.overtime_recommended,
            self.temporary_labor_recommended,
            self.full_time_hiring_recommended,
        )

        return sum(major_actions) > 1

    def as_dict(self) -> dict[str, Any]:
        """Return the request as a serializable dictionary."""

        payload = asdict(self)
        payload["planning_date"] = self.planning_date.isoformat()

        return payload


# ============================================================
# Optimization Decision
# ============================================================

@dataclass(slots=True)
class WorkforceOptimizationDecision:
    """
    Final unified workforce optimization decision.
    """

    planning_date: date

    action: WorkforceAction

    priority: OptimizationPriority

    status: OptimizationStatus

    associate_gap: int

    recommended_associates: int

    overtime_hours: float

    forecast_confidence: float

    conflicting_actions_resolved: bool

    rationale: str

    generated_at_utc: datetime

    decision_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """Validate the optimization decision."""

        if not isinstance(self.planning_date, date):
            raise OptimizationValidationError(
                "planning_date must be a date."
            )

        if not isinstance(self.action, WorkforceAction):
            raise OptimizationValidationError(
                "action must be a WorkforceAction."
            )

        if not isinstance(self.priority, OptimizationPriority):
            raise OptimizationValidationError(
                "priority must be an OptimizationPriority."
            )

        if not isinstance(self.status, OptimizationStatus):
            raise OptimizationValidationError(
                "status must be an OptimizationStatus."
            )

        if not isinstance(self.associate_gap, int) or isinstance(
            self.associate_gap,
            bool,
        ):
            raise OptimizationValidationError(
                "associate_gap must be an integer."
            )

        if (
            not isinstance(self.recommended_associates, int)
            or isinstance(self.recommended_associates, bool)
            or self.recommended_associates < 0
        ):
            raise OptimizationValidationError(
                "recommended_associates must be a non-negative integer."
            )

        if self.overtime_hours < 0:
            raise OptimizationValidationError(
                "overtime_hours must be non-negative."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise OptimizationValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        if not isinstance(self.conflicting_actions_resolved, bool):
            raise OptimizationValidationError(
                "conflicting_actions_resolved must be a boolean."
            )

        if not self.rationale.strip():
            raise OptimizationValidationError(
                "rationale must not be empty."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise OptimizationValidationError(
                "generated_at_utc must be a datetime."
            )

        if not self.decision_version.strip():
            raise OptimizationValidationError(
                "decision_version must not be empty."
            )

        if self.action is WorkforceAction.NONE:
            if self.recommended_associates != 0:
                raise OptimizationValidationError(
                    "recommended_associates must be zero for NONE."
                )

            if self.overtime_hours != 0:
                raise OptimizationValidationError(
                    "overtime_hours must be zero for NONE."
                )

    def as_dict(self) -> dict[str, Any]:
        """Return the decision as a serializable dictionary."""

        return {
            "planning_date": self.planning_date.isoformat(),
            "action": self.action.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "associate_gap": self.associate_gap,
            "recommended_associates": self.recommended_associates,
            "overtime_hours": self.overtime_hours,
            "forecast_confidence": self.forecast_confidence,
            "conflicting_actions_resolved": (
                self.conflicting_actions_resolved
            ),
            "rationale": self.rationale,
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "decision_version": self.decision_version,
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "OptimizationPriority",
    "OptimizationStatus",
    "WorkforceAction",
    "WorkforceOptimizationDecision",
    "WorkforceOptimizationRequest",
]