"""
Demand Intelligence Engine Models

Business data models used throughout the Demand Intelligence Engine.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


# ============================================================
# Feature Definition
# ============================================================

@dataclass(slots=True)
class FeatureDefinition:
    """
    Metadata describing a single engineered feature.
    """

    name: str
    category: str
    description: str


# ============================================================
# Forecast Profile
# ============================================================

@dataclass(slots=True)
class ForecastProfile:
    """
    Defines how a forecasting dataset should be generated.
    """

    name: str
    target: str

    horizons: List[int] = field(default_factory=list)

    business_features: List[str] = field(default_factory=list)

    ml_features: List[str] = field(default_factory=list)


# ============================================================
# Demand Summary
# ============================================================

@dataclass(slots=True)
class DemandSummary:
    """
    Summary statistics describing the demand dataset.
    """

    dataset_name: str

    start_date: Optional[date]

    end_date: Optional[date]

    total_days: int

    total_records: int

    target_column: str

    missing_dates: int

    duplicate_dates: int

    validation_passed: bool