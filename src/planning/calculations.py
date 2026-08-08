"""
Enterprise Capacity Planning — Calculations

Pure mathematical functions used by the Enterprise Capacity Planning
Engine.

This module contains no Spark dependencies, persistence operations,
reporting logic, or business workflow orchestration.
"""

from __future__ import annotations

from math import ceil

from src.workforce.exceptions import WorkforceCapacityError


# ============================================================
# Workload Calculations
# ============================================================

def calculate_buffered_workload(
    *,
    expected_order_lines: float,
    safety_buffer_ratio: float,
) -> float:
    """
    Apply the configured safety buffer to forecast workload.

    Parameters
    ----------
    expected_order_lines:
        Forecast number of order lines for the planning period.

    safety_buffer_ratio:
        Additional workload ratio used to protect operations against
        forecast uncertainty and normal execution variability.

    Returns
    -------
    float
        Buffered forecast workload.

    Raises
    ------
    WorkforceCapacityError
        If workload or safety-buffer inputs are invalid.
    """

    _validate_non_negative(
        name="expected_order_lines",
        value=expected_order_lines,
    )

    if not 0 <= safety_buffer_ratio < 1:
        raise WorkforceCapacityError(
            "safety_buffer_ratio must be greater than or equal to 0 "
            "and less than 1."
        )

    return expected_order_lines * (1 + safety_buffer_ratio)


def calculate_required_labor_hours(
    *,
    workload_lines: float,
    productivity_lines_per_hour: float,
) -> float:
    """
    Calculate labor hours required to process the workload.

    Parameters
    ----------
    workload_lines:
        Number of order lines requiring processing.

    productivity_lines_per_hour:
        Expected number of order lines completed by one associate
        during one productive hour.

    Returns
    -------
    float
        Required labor hours.

    Raises
    ------
    WorkforceCapacityError
        If workload or productivity inputs are invalid.
    """

    _validate_non_negative(
        name="workload_lines",
        value=workload_lines,
    )
    _validate_positive(
        name="productivity_lines_per_hour",
        value=productivity_lines_per_hour,
    )

    return workload_lines / productivity_lines_per_hour


# ============================================================
# Workforce Requirement Calculations
# ============================================================

def calculate_required_associates(
    *,
    required_labor_hours: float,
    productive_hours_per_associate: float,
    minimum_associates: int,
    maximum_associates: int,
) -> int:
    """
    Calculate the whole-number associate requirement.

    Fractional associate requirements are rounded upward because a
    partial associate cannot be scheduled as a complete workforce
    resource.

    Parameters
    ----------
    required_labor_hours:
        Total labor hours required to process the workload.

    productive_hours_per_associate:
        Effective productive hours available from one associate.

    minimum_associates:
        Minimum workforce requirement permitted by configuration.

    maximum_associates:
        Maximum workforce requirement permitted by configuration.

    Returns
    -------
    int
        Required number of associates.

    Raises
    ------
    WorkforceCapacityError
        If calculation inputs or workforce bounds are invalid.
    """

    _validate_non_negative(
        name="required_labor_hours",
        value=required_labor_hours,
    )
    _validate_positive(
        name="productive_hours_per_associate",
        value=productive_hours_per_associate,
    )

    if minimum_associates < 0:
        raise WorkforceCapacityError(
            "minimum_associates must be non-negative."
        )

    if maximum_associates <= 0:
        raise WorkforceCapacityError(
            "maximum_associates must be greater than 0."
        )

    if minimum_associates > maximum_associates:
        raise WorkforceCapacityError(
            "minimum_associates cannot exceed maximum_associates."
        )

    calculated_requirement = ceil(
        required_labor_hours / productive_hours_per_associate
    )

    bounded_requirement = max(
        minimum_associates,
        calculated_requirement,
    )

    if bounded_requirement > maximum_associates:
        raise WorkforceCapacityError(
            "Calculated associate requirement exceeds "
            f"maximum_associates={maximum_associates}."
        )

    return bounded_requirement


# ============================================================
# Available Capacity Calculations
# ============================================================

def calculate_available_capacity_lines(
    *,
    available_associates: int,
    productivity_lines_per_hour: float,
    scheduled_hours: float,
    target_utilization: float,
) -> float:
    """
    Calculate expected order-line capacity for available associates.

    Parameters
    ----------
    available_associates:
        Number of associates available during the planning period.

    productivity_lines_per_hour:
        Expected hourly productivity for one associate.

    scheduled_hours:
        Scheduled working hours for one associate.

    target_utilization:
        Operationally achievable proportion of theoretical capacity.

    Returns
    -------
    float
        Expected available capacity measured in order lines.

    Raises
    ------
    WorkforceCapacityError
        If any capacity input is invalid.
    """

    if available_associates < 0:
        raise WorkforceCapacityError(
            "available_associates must be non-negative."
        )

    _validate_positive(
        name="productivity_lines_per_hour",
        value=productivity_lines_per_hour,
    )
    _validate_positive(
        name="scheduled_hours",
        value=scheduled_hours,
    )

    if not 0 < target_utilization <= 1:
        raise WorkforceCapacityError(
            "target_utilization must be greater than 0 and less than "
            "or equal to 1."
        )

    return (
        available_associates
        * productivity_lines_per_hour
        * scheduled_hours
        * target_utilization
    )


# ============================================================
# Capacity Gap Calculations
# ============================================================

def calculate_associate_gap(
    *,
    required_associates: int,
    available_associates: int,
) -> int:
    """
    Calculate the signed workforce gap.

    Positive values represent a shortage. Negative values represent a
    surplus. Zero represents balanced capacity.
    """

    _validate_non_negative_integer(
        name="required_associates",
        value=required_associates,
    )
    _validate_non_negative_integer(
        name="available_associates",
        value=available_associates,
    )

    return required_associates - available_associates


def calculate_associate_shortage(
    *,
    required_associates: int,
    available_associates: int,
) -> int:
    """
    Return the number of additional associates required.

    Returns zero when available staffing meets or exceeds the
    calculated workforce requirement.
    """

    return max(
        0,
        calculate_associate_gap(
            required_associates=required_associates,
            available_associates=available_associates,
        ),
    )


def calculate_associate_surplus(
    *,
    required_associates: int,
    available_associates: int,
) -> int:
    """
    Return the number of associates above the requirement.

    Returns zero when available staffing is less than or equal to the
    calculated workforce requirement.
    """

    return max(
        0,
        -calculate_associate_gap(
            required_associates=required_associates,
            available_associates=available_associates,
        ),
    )


# ============================================================
# Utilization Calculations
# ============================================================

def calculate_capacity_utilization(
    *,
    workload_lines: float,
    available_capacity_lines: float,
) -> float:
    """
    Calculate workload utilization against available line capacity.

    A value below 1 indicates sufficient capacity. A value above 1
    indicates demand exceeds available capacity.

    Returns zero when both workload and available capacity are zero.

    Raises
    ------
    WorkforceCapacityError
        If workload is negative or positive workload is evaluated
        against zero available capacity.
    """

    _validate_non_negative(
        name="workload_lines",
        value=workload_lines,
    )
    _validate_non_negative(
        name="available_capacity_lines",
        value=available_capacity_lines,
    )

    if available_capacity_lines == 0:
        if workload_lines == 0:
            return 0.0

        raise WorkforceCapacityError(
            "available_capacity_lines must be greater than 0 when "
            "workload_lines is positive."
        )

    return workload_lines / available_capacity_lines


# ============================================================
# Validation Helpers
# ============================================================

def _validate_positive(
    *,
    name: str,
    value: float,
) -> None:
    """
    Validate that a numeric value is greater than zero.
    """

    if value <= 0:
        raise WorkforceCapacityError(
            f"{name} must be greater than 0."
        )


def _validate_non_negative(
    *,
    name: str,
    value: float,
) -> None:
    """
    Validate that a numeric value is non-negative.
    """

    if value < 0:
        raise WorkforceCapacityError(
            f"{name} must be non-negative."
        )


def _validate_non_negative_integer(
    *,
    name: str,
    value: int,
) -> None:
    """
    Validate that a value is a non-negative integer.
    """

    if not isinstance(value, int) or isinstance(value, bool):
        raise WorkforceCapacityError(
            f"{name} must be an integer."
        )

    if value < 0:
        raise WorkforceCapacityError(
            f"{name} must be non-negative."
        )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "calculate_associate_gap",
    "calculate_associate_shortage",
    "calculate_associate_surplus",
    "calculate_available_capacity_lines",
    "calculate_buffered_workload",
    "calculate_capacity_utilization",
    "calculate_required_associates",
    "calculate_required_labor_hours",
]