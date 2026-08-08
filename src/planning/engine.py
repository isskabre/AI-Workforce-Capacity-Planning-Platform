"""
Enterprise Capacity Planning — Engine

Core business engine that converts forecast workload and workforce
availability into capacity requirements and workforce-gap decisions.

The engine delegates all mathematical operations to the calculations
module and remains independent from Spark, persistence, reporting,
and user-interface concerns.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from src.planning.calculations import (
    calculate_associate_shortage,
    calculate_available_capacity_lines,
    calculate_buffered_workload,
    calculate_capacity_utilization,
    calculate_required_associates,
    calculate_required_labor_hours,
)
from src.planning.configuration import CapacityPlanningConfiguration
from src.workforce.exceptions import (
    WorkforcePlanningError,
    WorkforceValidationError,
)
from src.workforce.models import (
    WorkforceCapacity,
    WorkforceGap,
    WorkforceRequirement,
)


# ============================================================
# Capacity Planning Engine
# ============================================================

class CapacityPlanningEngine:
    """
    Execute enterprise workforce capacity-planning decisions.

    Parameters
    ----------
    configuration:
        Validated capacity-planning configuration controlling
        productivity, utilization, safety buffers, and workforce limits.
    """

    def __init__(
        self,
        *,
        configuration: Optional[
            CapacityPlanningConfiguration
        ] = None,
    ) -> None:
        """
        Initialize the capacity-planning engine.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else CapacityPlanningConfiguration()
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        planning_date: date,
        expected_order_lines: float,
        workforce_capacity: WorkforceCapacity,
        forecast_confidence: Optional[float] = None,
    ) -> tuple[
        WorkforceRequirement,
        WorkforceGap,
    ]:
        """
        Evaluate workforce capacity for one planning period.

        Parameters
        ----------
        planning_date:
            Business date being evaluated.

        expected_order_lines:
            Forecast order-line workload for the planning period.

        workforce_capacity:
            Available workforce and productivity information.

        forecast_confidence:
            Optional upstream forecast confidence between zero and one.
            When omitted, the configured default confidence is used.

        Returns
        -------
        tuple[WorkforceRequirement, WorkforceGap]
            Calculated workforce requirement and staffing gap.

        Raises
        ------
        WorkforceValidationError
            If the planning request is inconsistent or invalid.

        WorkforcePlanningError
            If capacity-planning execution fails.
        """

        self._validate_request(
            planning_date=planning_date,
            expected_order_lines=expected_order_lines,
            workforce_capacity=workforce_capacity,
            forecast_confidence=forecast_confidence,
        )

        resolved_confidence = (
            self._configuration.default_forecast_confidence
            if forecast_confidence is None
            else forecast_confidence
        )

        try:
            buffered_workload = calculate_buffered_workload(
                expected_order_lines=expected_order_lines,
                safety_buffer_ratio=(
                    self._configuration.safety_buffer_ratio
                ),
            )

            required_labor_hours = calculate_required_labor_hours(
                workload_lines=buffered_workload,
                productivity_lines_per_hour=(
                    workforce_capacity.productivity_lines_per_hour
                ),
            )

            productive_hours_per_associate = (
                workforce_capacity.scheduled_hours
                * self._configuration.target_utilization
            )

            required_associates = calculate_required_associates(
                required_labor_hours=required_labor_hours,
                productive_hours_per_associate=(
                    productive_hours_per_associate
                ),
                minimum_associates=(
                    self._configuration.minimum_associates
                ),
                maximum_associates=(
                    self._configuration.maximum_associates
                ),
            )

            available_capacity_lines = (
                calculate_available_capacity_lines(
                    available_associates=(
                        workforce_capacity.available_associates
                    ),
                    productivity_lines_per_hour=(
                        workforce_capacity
                        .productivity_lines_per_hour
                    ),
                    scheduled_hours=(
                        workforce_capacity.scheduled_hours
                    ),
                    target_utilization=(
                        self._configuration.target_utilization
                    ),
                )
            )

            capacity_utilization = self._resolve_utilization(
                workload_lines=buffered_workload,
                available_capacity_lines=available_capacity_lines,
            )

            shortage = calculate_associate_shortage(
                required_associates=required_associates,
                available_associates=(
                    workforce_capacity.available_associates
                ),
            )

            overtime_required = (
                shortage
                >= self._configuration
                .overtime_trigger_associate_gap
            )

            recommended_overtime_hours = (
                self._calculate_recommended_overtime_hours(
                    shortage=shortage,
                    required_labor_hours=required_labor_hours,
                    available_associates=(
                        workforce_capacity.available_associates
                    ),
                    scheduled_hours=(
                        workforce_capacity.scheduled_hours
                    ),
                )
                if overtime_required
                else 0.0
            )

            requirement = WorkforceRequirement(
                planning_date=planning_date,
                required_associates=required_associates,
                expected_order_lines=expected_order_lines,
                expected_workload_units=buffered_workload,
                required_hours=required_labor_hours,
                confidence=resolved_confidence,
            )

            gap = WorkforceGap(
                planning_date=planning_date,
                available_associates=(
                    workforce_capacity.available_associates
                ),
                required_associates=required_associates,
                shortage=shortage,
                overtime_required=overtime_required,
                recommended_overtime_hours=(
                    recommended_overtime_hours
                ),
            )

            # Capacity utilization is calculated intentionally here
            # to verify the operational feasibility of the request.
            # It will become part of richer reporting models later.
            _ = capacity_utilization

            return requirement, gap

        except WorkforcePlanningError:
            raise

        except Exception as exc:
            raise WorkforcePlanningError(
                "Capacity-planning evaluation failed."
            ) from exc

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def _validate_request(
        self,
        *,
        planning_date: date,
        expected_order_lines: float,
        workforce_capacity: WorkforceCapacity,
        forecast_confidence: Optional[float],
    ) -> None:
        """
        Validate the capacity-planning request.
        """

        if not isinstance(planning_date, date):
            raise WorkforceValidationError(
                "planning_date must be a date."
            )

        if expected_order_lines < 0:
            raise WorkforceValidationError(
                "expected_order_lines must be non-negative."
            )

        if not isinstance(
            workforce_capacity,
            WorkforceCapacity,
        ):
            raise WorkforceValidationError(
                "workforce_capacity must be a WorkforceCapacity."
            )

        if workforce_capacity.planning_date != planning_date:
            raise WorkforceValidationError(
                "workforce_capacity.planning_date must match "
                "planning_date."
            )

        if workforce_capacity.available_associates < 0:
            raise WorkforceValidationError(
                "available_associates must be non-negative."
            )

        if (
            workforce_capacity.productivity_lines_per_hour
            <= 0
        ):
            raise WorkforceValidationError(
                "productivity_lines_per_hour must be greater "
                "than 0."
            )

        if workforce_capacity.scheduled_hours <= 0:
            raise WorkforceValidationError(
                "scheduled_hours must be greater than 0."
            )

        if (
            forecast_confidence is not None
            and not 0 <= forecast_confidence <= 1
        ):
            raise WorkforceValidationError(
                "forecast_confidence must be between 0 and 1."
            )

    # --------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------

    def _calculate_recommended_overtime_hours(
        self,
        *,
        shortage: int,
        required_labor_hours: float,
        available_associates: int,
        scheduled_hours: float,
    ) -> float:
        """
        Estimate total overtime hours required for the shortage.

        The value represents the total additional labor-hour deficit,
        bounded by the configured overtime policy. Implementation 18
        will convert this planning signal into voluntary or mandatory
        overtime recommendations.
        """

        if shortage <= 0:
            return 0.0

        available_labor_hours = (
            available_associates
            * scheduled_hours
            * self._configuration.target_utilization
        )

        labor_hour_deficit = max(
            0.0,
            required_labor_hours - available_labor_hours,
        )

        maximum_supported_overtime = (
            shortage
            * self._configuration.maximum_overtime_hours
        )

        minimum_supported_overtime = (
            shortage
            * self._configuration.minimum_overtime_hours
        )

        if labor_hour_deficit == 0:
            return 0.0

        return min(
            maximum_supported_overtime,
            max(
                minimum_supported_overtime,
                labor_hour_deficit,
            ),
        )

    @staticmethod
    def _resolve_utilization(
        *,
        workload_lines: float,
        available_capacity_lines: float,
    ) -> float:
        """
        Resolve capacity utilization, including zero-capacity cases.
        """

        if available_capacity_lines == 0:
            if workload_lines == 0:
                return 0.0

            return float("inf")

        return calculate_capacity_utilization(
            workload_lines=workload_lines,
            available_capacity_lines=available_capacity_lines,
        )

    @property
    def configuration(
        self,
    ) -> CapacityPlanningConfiguration:
        """
        Return the active planning configuration.
        """

        return self._configuration


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningEngine",
]