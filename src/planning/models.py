"""
Enterprise Capacity Planning Models

Typed request and result contracts used by the Enterprise Capacity
Planning Engine and its downstream services.

These models aggregate workforce domain objects without duplicating
capacity calculations or reporting logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

from src.planning.exceptions import (
    CapacityPlanningValidationError,
)
from src.workforce.models import (
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
)


# ============================================================
# Capacity Planning Request
# ============================================================

@dataclass(slots=True)
class CapacityPlanningRequest:
    """
    Input contract for one capacity-planning evaluation.

    Attributes
    ----------
    planning_date:
        Business date being evaluated.

    expected_order_lines:
        Forecast order-line workload for the planning period.

    workforce_capacity:
        Available workforce, productivity, shift, and schedule
        information.

    forecast_confidence:
        Optional forecast confidence between zero and one.
    """

    planning_date: date

    expected_order_lines: float

    workforce_capacity: WorkforceCapacity

    forecast_confidence: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Validate the capacity-planning request.
        """

        if not isinstance(self.planning_date, date):
            raise CapacityPlanningValidationError(
                "planning_date must be a date."
            )

        if self.expected_order_lines < 0:
            raise CapacityPlanningValidationError(
                "expected_order_lines must be non-negative."
            )

        if not isinstance(
            self.workforce_capacity,
            WorkforceCapacity,
        ):
            raise CapacityPlanningValidationError(
                "workforce_capacity must be a WorkforceCapacity."
            )

        if (
            self.workforce_capacity.planning_date
            != self.planning_date
        ):
            raise CapacityPlanningValidationError(
                "workforce_capacity.planning_date must match "
                "planning_date."
            )

        if (
            self.forecast_confidence is not None
            and not 0 <= self.forecast_confidence <= 1
        ):
            raise CapacityPlanningValidationError(
                "forecast_confidence must be between 0 and 1."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the request as a serializable dictionary.
        """

        return {
            "planning_date": self.planning_date.isoformat(),
            "expected_order_lines": self.expected_order_lines,
            "forecast_confidence": self.forecast_confidence,
            "shift": self.workforce_capacity.shift.value,
            "workforce_type": (
                self.workforce_capacity.workforce_type.value
            ),
            "available_associates": (
                self.workforce_capacity.available_associates
            ),
            "productivity_lines_per_hour": (
                self.workforce_capacity
                .productivity_lines_per_hour
            ),
            "scheduled_hours": (
                self.workforce_capacity.scheduled_hours
            ),
            "overtime_type": (
                self.workforce_capacity.overtime_type.value
            ),
            "metadata": dict(
                self.workforce_capacity.metadata
            ),
        }


# ============================================================
# Capacity Planning Result
# ============================================================

@dataclass(slots=True)
class CapacityPlanningResult:
    """
    Standard result contract for one capacity-planning evaluation.

    Attributes
    ----------
    request:
        Original validated planning request.

    requirement:
        Calculated workforce requirement.

    gap:
        Calculated workforce shortage and overtime signal.

    generated_at_utc:
        UTC timestamp identifying result generation.

    planning_version:
        Semantic version of the planning result contract.
    """

    request: CapacityPlanningRequest

    requirement: WorkforceRequirement

    gap: WorkforceGap

    generated_at_utc: datetime

    planning_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """
        Validate result object consistency.
        """

        if not isinstance(
            self.request,
            CapacityPlanningRequest,
        ):
            raise CapacityPlanningValidationError(
                "request must be a CapacityPlanningRequest."
            )

        if not isinstance(
            self.requirement,
            WorkforceRequirement,
        ):
            raise CapacityPlanningValidationError(
                "requirement must be a WorkforceRequirement."
            )

        if not isinstance(self.gap, WorkforceGap):
            raise CapacityPlanningValidationError(
                "gap must be a WorkforceGap."
            )

        planning_dates = {
            self.request.planning_date,
            self.requirement.planning_date,
            self.gap.planning_date,
        }

        if len(planning_dates) != 1:
            raise CapacityPlanningValidationError(
                "Request, requirement, and gap must share the "
                "same planning_date."
            )

        if (
            self.gap.available_associates
            != self.request
            .workforce_capacity
            .available_associates
        ):
            raise CapacityPlanningValidationError(
                "gap.available_associates must match the request "
                "workforce capacity."
            )

        if (
            self.gap.required_associates
            != self.requirement.required_associates
        ):
            raise CapacityPlanningValidationError(
                "gap.required_associates must match the workforce "
                "requirement."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise CapacityPlanningValidationError(
                "generated_at_utc must be a datetime."
            )

        if not self.planning_version.strip():
            raise CapacityPlanningValidationError(
                "planning_version must not be empty."
            )

    @property
    def planning_date(self) -> date:
        """
        Return the evaluated planning date.
        """

        return self.request.planning_date

    @property
    def available_associates(self) -> int:
        """
        Return the available associate count.
        """

        return (
            self.request
            .workforce_capacity
            .available_associates
        )

    @property
    def required_associates(self) -> int:
        """
        Return the required associate count.
        """

        return self.requirement.required_associates

    @property
    def associate_gap(self) -> int:
        """
        Return the signed associate gap.

        Positive values represent shortages, negative values represent
        surpluses, and zero represents balanced capacity.
        """

        return (
            self.required_associates
            - self.available_associates
        )

    @property
    def has_shortage(self) -> bool:
        """
        Return whether additional workforce is required.
        """

        return self.gap.shortage > 0

    def as_dict(self) -> dict[str, Any]:
        """
        Return the result as a serializable dictionary.
        """

        return {
            "planning_date": self.planning_date.isoformat(),
            "expected_order_lines": (
                self.request.expected_order_lines
            ),
            "forecast_confidence": (
                self.requirement.confidence
            ),
            "available_associates": (
                self.available_associates
            ),
            "required_associates": (
                self.required_associates
            ),
            "associate_gap": self.associate_gap,
            "shortage": self.gap.shortage,
            "overtime_required": (
                self.gap.overtime_required
            ),
            "recommended_overtime_hours": (
                self.gap.recommended_overtime_hours
            ),
            "required_labor_hours": (
                self.requirement.required_hours
            ),
            "buffered_workload_lines": (
                self.requirement.expected_workload_units
            ),
            "shift": (
                self.request
                .workforce_capacity
                .shift
                .value
            ),
            "workforce_type": (
                self.request
                .workforce_capacity
                .workforce_type
                .value
            ),
            "generated_at_utc": (
                self.generated_at_utc.isoformat()
            ),
            "planning_version": self.planning_version,
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningRequest",
    "CapacityPlanningResult",
]