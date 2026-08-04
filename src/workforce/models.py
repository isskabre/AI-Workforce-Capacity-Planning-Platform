"""
Enterprise Workforce Planning Models

Strongly typed domain models used throughout the Workforce Planning
Engine. These models remain independent from Spark, forecasting
algorithms, and planning logic.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class WorkforceType(str, Enum):
    """
    Workforce employment classification.
    """

    FULL_TIME = "FULL_TIME"
    TEMPORARY = "TEMPORARY"


class ShiftType(str, Enum):
    """
    Warehouse shift.
    """

    SHIFT_1 = "SHIFT_1"
    SHIFT_2 = "SHIFT_2"


class OvertimeType(str, Enum):
    """
    Overtime classification.
    """

    NONE = "NONE"
    VOLUNTARY = "VOLUNTARY"
    MANDATORY = "MANDATORY"


@dataclass(frozen=True)
class WorkforceCapacity:
    """
    Workforce availability for one planning period.
    """

    planning_date: date

    shift: ShiftType

    workforce_type: WorkforceType

    available_associates: int

    productivity_lines_per_hour: float

    scheduled_hours: float

    overtime_type: OvertimeType = OvertimeType.NONE

    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkforceRequirement:
    """
    Estimated workforce required to execute the workload.
    """

    planning_date: date

    required_associates: int

    expected_order_lines: float

    expected_workload_units: Optional[float] = None

    required_hours: Optional[float] = None

    confidence: Optional[float] = None


@dataclass(frozen=True)
class WorkforceGap:
    """
    Capacity versus demand comparison.
    """

    planning_date: date

    available_associates: int

    required_associates: int

    shortage: int

    overtime_required: bool

    recommended_overtime_hours: float = 0.0