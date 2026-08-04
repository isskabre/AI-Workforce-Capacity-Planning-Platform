"""
Enterprise Decision Orchestration Models

Typed contracts for end-to-end workforce decision orchestration.

These models carry the inputs and unified outputs required to coordinate
capacity planning, overtime, staffing, and workforce optimization.
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
from .exceptions import OrchestrationValidationError


# ============================================================
# Enumerations
# ============================================================

class OrchestrationStatus(str, Enum):
    """
    Lifecycle status of an orchestration workflow.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OrchestrationStage(str, Enum):
    """
    Supported enterprise orchestration stages.
    """

    FORECAST = "forecast"
    PLANNING = "planning"
    OVERTIME = "overtime"
    STAFFING = "staffing"
    OPTIMIZATION = "optimization"
    COMPLETE = "complete"


# ============================================================
# Orchestration Request
# ============================================================

@dataclass(slots=True)
class EnterpriseDecisionRequest:
    """
    Input contract for one end-to-end workforce decision.

    Parameters
    ----------
    planning_date:
        Business date being evaluated.

    expected_order_lines:
        Forecast workload represented as expected order lines.

    available_associates:
        Number of associates available for the planning period.

    productivity_lines_per_hour:
        Expected productivity per associate.

    scheduled_hours:
        Scheduled hours per available associate.

    forecast_confidence:
        Confidence associated with the forecast.

    recurring_shortage_days:
        Recent periods with a workforce shortage.

    recurring_surplus_days:
        Recent periods with a workforce surplus.

    overtime_dependency_days:
        Recent periods dependent on overtime.

    planning_horizon_days:
        Horizon represented by the strategic staffing request.
    """

    planning_date: date

    expected_order_lines: float

    available_associates: int

    productivity_lines_per_hour: float

    scheduled_hours: float

    forecast_confidence: float

    recurring_shortage_days: int = 0

    recurring_surplus_days: int = 0

    overtime_dependency_days: int = 0

    planning_horizon_days: int = 30

    def __post_init__(self) -> None:
        """
        Validate the orchestration request.
        """

        if not isinstance(self.planning_date, date):
            raise OrchestrationValidationError(
                "planning_date must be a date."
            )

        if self.expected_order_lines < 0:
            raise OrchestrationValidationError(
                "expected_order_lines must be non-negative."
            )

        if (
            not isinstance(self.available_associates, int)
            or isinstance(self.available_associates, bool)
            or self.available_associates < 0
        ):
            raise OrchestrationValidationError(
                "available_associates must be a non-negative integer."
            )

        if self.productivity_lines_per_hour <= 0:
            raise OrchestrationValidationError(
                "productivity_lines_per_hour must be greater than 0."
            )

        if self.scheduled_hours <= 0:
            raise OrchestrationValidationError(
                "scheduled_hours must be greater than 0."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise OrchestrationValidationError(
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
            raise OrchestrationValidationError(
                "planning_horizon_days must be a positive integer."
            )

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
        Validate a non-negative integer.
        """

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise OrchestrationValidationError(
                f"{name} must be a non-negative integer."
            )


# ============================================================
# Orchestration Result
# ============================================================

@dataclass(slots=True)
class EnterpriseDecisionResult:
    """
    Unified enterprise workforce decision result.

    Parameters
    ----------
    planning_date:
        Business date evaluated.

    workflow_status:
        Final orchestration lifecycle status.

    completed_stage:
        Last successfully completed workflow stage.

    expected_order_lines:
        Forecast workload evaluated.

    available_associates:
        Available workforce count.

    required_associates:
        Calculated workforce requirement.

    associate_gap:
        Signed workforce gap.

    overtime_recommendation:
        Standardized overtime recommendation value.

    staffing_recommendation:
        Standardized strategic staffing recommendation value.

    optimization_action:
        Final workforce optimization action.

    optimization_priority:
        Final optimization priority.

    optimization_status:
        Final optimization status.

    overtime_hours:
        Recommended overtime labor hours.

    recommended_associates:
        Recommended workforce action quantity.

    forecast_confidence:
        Confidence propagated through the workflow.

    rationale:
        Unified human-readable explanation.

    generated_at_utc:
        UTC workflow completion timestamp.

    workflow_version:
        Semantic version of the orchestration contract.
    """

    planning_date: date

    workflow_status: OrchestrationStatus

    completed_stage: OrchestrationStage

    expected_order_lines: float

    available_associates: int

    required_associates: int

    associate_gap: int

    overtime_recommendation: str

    staffing_recommendation: str

    optimization_action: str

    optimization_priority: str

    optimization_status: str

    overtime_hours: float

    recommended_associates: int

    forecast_confidence: float

    rationale: str

    generated_at_utc: datetime

    workflow_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate the orchestration result.
        """

        if not isinstance(self.planning_date, date):
            raise OrchestrationValidationError(
                "planning_date must be a date."
            )

        if not isinstance(
            self.workflow_status,
            OrchestrationStatus,
        ):
            raise OrchestrationValidationError(
                "workflow_status must be an OrchestrationStatus."
            )

        if not isinstance(
            self.completed_stage,
            OrchestrationStage,
        ):
            raise OrchestrationValidationError(
                "completed_stage must be an OrchestrationStage."
            )

        if self.expected_order_lines < 0:
            raise OrchestrationValidationError(
                "expected_order_lines must be non-negative."
            )

        integer_fields = {
            "available_associates": self.available_associates,
            "required_associates": self.required_associates,
            "associate_gap": self.associate_gap,
            "recommended_associates": self.recommended_associates,
        }

        for field_name, field_value in integer_fields.items():
            if (
                not isinstance(field_value, int)
                or isinstance(field_value, bool)
            ):
                raise OrchestrationValidationError(
                    f"{field_name} must be an integer."
                )

        if self.available_associates < 0:
            raise OrchestrationValidationError(
                "available_associates must be non-negative."
            )

        if self.required_associates < 0:
            raise OrchestrationValidationError(
                "required_associates must be non-negative."
            )

        if self.recommended_associates < 0:
            raise OrchestrationValidationError(
                "recommended_associates must be non-negative."
            )

        expected_gap = (
            self.required_associates
            - self.available_associates
        )

        if self.associate_gap != expected_gap:
            raise OrchestrationValidationError(
                "associate_gap must equal required_associates minus "
                "available_associates."
            )

        string_fields = {
            "overtime_recommendation": self.overtime_recommendation,
            "staffing_recommendation": self.staffing_recommendation,
            "optimization_action": self.optimization_action,
            "optimization_priority": self.optimization_priority,
            "optimization_status": self.optimization_status,
            "rationale": self.rationale,
        }

        for field_name, field_value in string_fields.items():
            if not isinstance(field_value, str) or not field_value.strip():
                raise OrchestrationValidationError(
                    f"{field_name} must not be empty."
                )

        if self.overtime_hours < 0:
            raise OrchestrationValidationError(
                "overtime_hours must be non-negative."
            )

        if not (
            MIN_FORECAST_CONFIDENCE
            <= self.forecast_confidence
            <= MAX_FORECAST_CONFIDENCE
        ):
            raise OrchestrationValidationError(
                "forecast_confidence must be between 0 and 1."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise OrchestrationValidationError(
                "generated_at_utc must be a datetime."
            )

        if not self.workflow_version.strip():
            raise OrchestrationValidationError(
                "workflow_version must not be empty."
            )

        if (
            self.workflow_status is OrchestrationStatus.COMPLETED
            and self.completed_stage is not OrchestrationStage.COMPLETE
        ):
            raise OrchestrationValidationError(
                "Completed workflows must use the COMPLETE stage."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the result as a serializable dictionary.
        """

        return {
            "planning_date": self.planning_date.isoformat(),
            "workflow_status": self.workflow_status.value,
            "completed_stage": self.completed_stage.value,
            "expected_order_lines": self.expected_order_lines,
            "available_associates": self.available_associates,
            "required_associates": self.required_associates,
            "associate_gap": self.associate_gap,
            "overtime_recommendation": (
                self.overtime_recommendation
            ),
            "staffing_recommendation": (
                self.staffing_recommendation
            ),
            "optimization_action": self.optimization_action,
            "optimization_priority": self.optimization_priority,
            "optimization_status": self.optimization_status,
            "overtime_hours": self.overtime_hours,
            "recommended_associates": (
                self.recommended_associates
            ),
            "forecast_confidence": self.forecast_confidence,
            "rationale": self.rationale,
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "workflow_version": self.workflow_version,
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "EnterpriseDecisionRequest",
    "EnterpriseDecisionResult",
    "OrchestrationStage",
    "OrchestrationStatus",
]