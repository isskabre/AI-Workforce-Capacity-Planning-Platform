"""
Enterprise Capacity Planning — Reporting

Reporting contracts and serialization helpers for workforce capacity
planning results.

This module converts validated planning domain objects into stable,
dashboard-ready and API-ready summaries without performing capacity
calculations or business workflow orchestration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from typing import Any

from src.workforce.constants import (
    CAPACITY_STATUS_BALANCED,
    CAPACITY_STATUS_SHORTAGE,
    CAPACITY_STATUS_SURPLUS,
    RECOMMENDATION_ADD_ASSOCIATES,
    RECOMMENDATION_NO_ACTION,
    RECOMMENDATION_REDUCE_STAFFING,
    RECOMMENDATION_REVIEW_OVERTIME,
)
from src.workforce.exceptions import WorkforceValidationError
from src.workforce.models import (
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
)


# ============================================================
# Capacity Planning Report
# ============================================================

@dataclass(slots=True)
class CapacityPlanningReport:
    """
    Serializable enterprise capacity-planning report.

    Attributes
    ----------
    planning_date:
        Business date evaluated by the planning engine.

    capacity_status:
        Final capacity classification: SHORTAGE, BALANCED, or SURPLUS.

    recommendation:
        Standardized operational recommendation.

    available_associates:
        Number of associates available for the planning period.

    required_associates:
        Number of associates required to process the expected workload.

    associate_gap:
        Signed difference between required and available associates.
        Positive values represent shortages; negative values represent
        surpluses.

    shortage:
        Number of additional associates required.

    surplus:
        Number of associates above the calculated requirement.

    expected_order_lines:
        Original forecast workload.

    buffered_workload_lines:
        Forecast workload after applying the planning safety buffer.

    required_labor_hours:
        Total productive labor hours required.

    forecast_confidence:
        Forecast confidence used by the planning engine.

    overtime_required:
        Whether the result should proceed to overtime evaluation.

    recommended_overtime_hours:
        Total overtime-hour planning signal.

    shift:
        Warehouse shift classification.

    workforce_type:
        Workforce employment classification.

    generated_at_utc:
        UTC timestamp identifying report generation.

    report_version:
        Semantic version of the reporting contract.
    """

    planning_date: date

    capacity_status: str

    recommendation: str

    available_associates: int

    required_associates: int

    associate_gap: int

    shortage: int

    surplus: int

    expected_order_lines: float

    buffered_workload_lines: float

    required_labor_hours: float

    forecast_confidence: float

    overtime_required: bool

    recommended_overtime_hours: float

    shift: str

    workforce_type: str

    generated_at_utc: datetime

    report_version: str = "1.0.0"

    def as_dict(self) -> dict[str, Any]:
        """
        Return the report as a JSON-compatible dictionary.
        """

        payload = asdict(self)

        payload["planning_date"] = self.planning_date.isoformat()
        payload["generated_at_utc"] = (
            self.generated_at_utc.isoformat()
        )

        return payload


# ============================================================
# Capacity Planning Reporter
# ============================================================

class CapacityPlanningReporter:
    """
    Build standardized reports from capacity-planning domain objects.
    """

    def build(
        self,
        *,
        workforce_capacity: WorkforceCapacity,
        workforce_requirement: WorkforceRequirement,
        workforce_gap: WorkforceGap,
    ) -> CapacityPlanningReport:
        """
        Create one enterprise capacity-planning report.

        Parameters
        ----------
        workforce_capacity:
            Available workforce information used by the planning engine.

        workforce_requirement:
            Calculated workforce requirement.

        workforce_gap:
            Calculated staffing gap and overtime signal.

        Returns
        -------
        CapacityPlanningReport
            Standardized reporting object.

        Raises
        ------
        WorkforceValidationError
            If the supplied domain objects are invalid or inconsistent.
        """

        self._validate_inputs(
            workforce_capacity=workforce_capacity,
            workforce_requirement=workforce_requirement,
            workforce_gap=workforce_gap,
        )

        associate_gap = (
            workforce_requirement.required_associates
            - workforce_capacity.available_associates
        )

        shortage = max(0, associate_gap)
        surplus = max(0, -associate_gap)

        capacity_status = self._resolve_capacity_status(
            associate_gap=associate_gap,
        )

        recommendation = self._resolve_recommendation(
            associate_gap=associate_gap,
            overtime_required=workforce_gap.overtime_required,
        )

        return CapacityPlanningReport(
            planning_date=workforce_requirement.planning_date,
            capacity_status=capacity_status,
            recommendation=recommendation,
            available_associates=(
                workforce_capacity.available_associates
            ),
            required_associates=(
                workforce_requirement.required_associates
            ),
            associate_gap=associate_gap,
            shortage=shortage,
            surplus=surplus,
            expected_order_lines=(
                workforce_requirement.expected_order_lines
            ),
            buffered_workload_lines=(
                workforce_requirement.expected_workload_units
                if workforce_requirement.expected_workload_units
                is not None
                else workforce_requirement.expected_order_lines
            ),
            required_labor_hours=(
                workforce_requirement.required_hours
                if workforce_requirement.required_hours is not None
                else 0.0
            ),
            forecast_confidence=(
                workforce_requirement.confidence
                if workforce_requirement.confidence is not None
                else 0.0
            ),
            overtime_required=workforce_gap.overtime_required,
            recommended_overtime_hours=(
                workforce_gap.recommended_overtime_hours
            ),
            shift=workforce_capacity.shift.value,
            workforce_type=workforce_capacity.workforce_type.value,
            generated_at_utc=datetime.now(timezone.utc),
        )

    @staticmethod
    def _resolve_capacity_status(
        *,
        associate_gap: int,
    ) -> str:
        """
        Resolve the standardized capacity status.
        """

        if associate_gap > 0:
            return CAPACITY_STATUS_SHORTAGE

        if associate_gap < 0:
            return CAPACITY_STATUS_SURPLUS

        return CAPACITY_STATUS_BALANCED

    @staticmethod
    def _resolve_recommendation(
        *,
        associate_gap: int,
        overtime_required: bool,
    ) -> str:
        """
        Resolve the standardized operational recommendation.
        """

        if associate_gap > 0:
            if overtime_required:
                return RECOMMENDATION_REVIEW_OVERTIME

            return RECOMMENDATION_ADD_ASSOCIATES

        if associate_gap < 0:
            return RECOMMENDATION_REDUCE_STAFFING

        return RECOMMENDATION_NO_ACTION

    @staticmethod
    def _validate_inputs(
        *,
        workforce_capacity: WorkforceCapacity,
        workforce_requirement: WorkforceRequirement,
        workforce_gap: WorkforceGap,
    ) -> None:
        """
        Validate reporting inputs and planning-date consistency.
        """

        if not isinstance(
            workforce_capacity,
            WorkforceCapacity,
        ):
            raise WorkforceValidationError(
                "workforce_capacity must be a WorkforceCapacity."
            )

        if not isinstance(
            workforce_requirement,
            WorkforceRequirement,
        ):
            raise WorkforceValidationError(
                "workforce_requirement must be a "
                "WorkforceRequirement."
            )

        if not isinstance(
            workforce_gap,
            WorkforceGap,
        ):
            raise WorkforceValidationError(
                "workforce_gap must be a WorkforceGap."
            )

        planning_dates = {
            workforce_capacity.planning_date,
            workforce_requirement.planning_date,
            workforce_gap.planning_date,
        }

        if len(planning_dates) != 1:
            raise WorkforceValidationError(
                "All reporting inputs must share the same "
                "planning_date."
            )

        if (
            workforce_gap.available_associates
            != workforce_capacity.available_associates
        ):
            raise WorkforceValidationError(
                "workforce_gap.available_associates must match "
                "workforce_capacity.available_associates."
            )

        if (
            workforce_gap.required_associates
            != workforce_requirement.required_associates
        ):
            raise WorkforceValidationError(
                "workforce_gap.required_associates must match "
                "workforce_requirement.required_associates."
            )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningReport",
    "CapacityPlanningReporter",
]