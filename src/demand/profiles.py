"""
Demand Intelligence Engine — Forecast Profiles

Defines reusable demand forecasting profiles for supported business targets.
"""

from __future__ import annotations

from .constants import (
    BUSINESS_FEATURES,
    ML_FEATURE_GROUPS,
    ORDER_COUNT_COLUMN,
    ORDER_LINE_COUNT_COLUMN,
    PRIMARY_FORECAST_TARGET,
    SUPPORTED_FORECAST_HORIZONS,
    WORKLOAD_UNITS_COLUMN,
)
from .models import ForecastProfile


# ============================================================
# Profile Names
# ============================================================

ORDER_LINE_DEMAND_PROFILE_NAME = "order_line_demand"

ORDER_DEMAND_PROFILE_NAME = "order_demand"

UNIT_DEMAND_PROFILE_NAME = "unit_demand"


# ============================================================
# Forecast Profiles
# ============================================================

ORDER_LINE_DEMAND_PROFILE = ForecastProfile(
    name=ORDER_LINE_DEMAND_PROFILE_NAME,
    target=PRIMARY_FORECAST_TARGET,
    horizons=list(SUPPORTED_FORECAST_HORIZONS),
    business_features=list(BUSINESS_FEATURES),
    ml_features=list(ML_FEATURE_GROUPS),
)

ORDER_DEMAND_PROFILE = ForecastProfile(
    name=ORDER_DEMAND_PROFILE_NAME,
    target=ORDER_COUNT_COLUMN,
    horizons=list(SUPPORTED_FORECAST_HORIZONS),
    business_features=list(BUSINESS_FEATURES),
    ml_features=list(ML_FEATURE_GROUPS),
)

UNIT_DEMAND_PROFILE = ForecastProfile(
    name=UNIT_DEMAND_PROFILE_NAME,
    target=WORKLOAD_UNITS_COLUMN,
    horizons=list(SUPPORTED_FORECAST_HORIZONS),
    business_features=list(BUSINESS_FEATURES),
    ml_features=list(ML_FEATURE_GROUPS),
)


# ============================================================
# Profile Registry
# ============================================================

FORECAST_PROFILES = {
    ORDER_LINE_DEMAND_PROFILE.name: ORDER_LINE_DEMAND_PROFILE,
    ORDER_DEMAND_PROFILE.name: ORDER_DEMAND_PROFILE,
    UNIT_DEMAND_PROFILE.name: UNIT_DEMAND_PROFILE,
}


def get_forecast_profile(profile_name: str) -> ForecastProfile:
    """
    Return a registered forecast profile by name.

    Parameters
    ----------
    profile_name:
        Canonical profile name.

    Raises
    ------
    ValueError
        If the requested profile is not registered.
    """

    if not isinstance(profile_name, str) or not profile_name.strip():
        raise ValueError(
            "Forecast profile name must be a non-empty string."
        )

    normalized_name = profile_name.strip().lower()

    if normalized_name not in FORECAST_PROFILES:
        supported_profiles = ", ".join(sorted(FORECAST_PROFILES))

        raise ValueError(
            f"Unknown forecast profile: '{profile_name}'. "
            f"Supported profiles: {supported_profiles}"
        )

    return FORECAST_PROFILES[normalized_name]


def get_primary_forecast_profile() -> ForecastProfile:
    """
    Return the primary operational forecasting profile.

    The primary target is daily order-line demand because warehouse
    productivity, capacity, and overtime decisions are measured in lines.
    """

    return ORDER_LINE_DEMAND_PROFILE


def validate_forecast_profile(profile: ForecastProfile) -> None:
    """
    Validate the minimum requirements of a forecast profile.
    """

    if not profile.name.strip():
        raise ValueError("Forecast profile name cannot be empty.")

    if not profile.target.strip():
        raise ValueError("Forecast profile target cannot be empty.")

    if not profile.horizons:
        raise ValueError(
            f"Forecast profile '{profile.name}' must contain at least one horizon."
        )

    invalid_horizons = sorted(
        horizon
        for horizon in profile.horizons
        if horizon not in SUPPORTED_FORECAST_HORIZONS
    )

    if invalid_horizons:
        raise ValueError(
            f"Forecast profile '{profile.name}' contains unsupported horizons: "
            f"{invalid_horizons}"
        )

    if len(profile.horizons) != len(set(profile.horizons)):
        raise ValueError(
            f"Forecast profile '{profile.name}' contains duplicate horizons."
        )