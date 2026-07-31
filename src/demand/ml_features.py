"""
Demand Intelligence Engine — Machine Learning Features

Creates leakage-safe temporal features for daily demand forecasting.
"""

from __future__ import annotations

from collections.abc import Sequence

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from .constants import DATE_COLUMN


DEFAULT_LAG_PERIODS = (
    1,
    2,
    3,
    7,
    14,
    30,
    60,
    90,
)

DEFAULT_ROLLING_WINDOWS = (
    3,
    7,
    14,
    30,
    60,
    90,
)

DEFAULT_TREND_PERIODS = (
    1,
    7,
    14,
    30,
)


def add_ml_features(
    dataframe: DataFrame,
    target_column: str,
    group_columns: Sequence[str] = (),
    lag_periods: Sequence[int] = DEFAULT_LAG_PERIODS,
    rolling_windows: Sequence[int] = DEFAULT_ROLLING_WINDOWS,
    trend_periods: Sequence[int] = DEFAULT_TREND_PERIODS,
) -> DataFrame:
    """
    Add leakage-safe temporal features for a forecasting target.

    Generated feature groups:

    - Lag features
    - Rolling statistics
    - Trend and growth features
    - Calendar seasonality enhancements

    The current row is excluded from all rolling calculations.
    """

    _validate_inputs(
        dataframe=dataframe,
        target_column=target_column,
        group_columns=group_columns,
        lag_periods=lag_periods,
        rolling_windows=rolling_windows,
        trend_periods=trend_periods,
    )

    result = dataframe

    result = add_lag_features(
        dataframe=result,
        target_column=target_column,
        group_columns=group_columns,
        lag_periods=lag_periods,
    )

    result = add_rolling_features(
        dataframe=result,
        target_column=target_column,
        group_columns=group_columns,
        rolling_windows=rolling_windows,
    )

    result = add_trend_features(
        dataframe=result,
        target_column=target_column,
        group_columns=group_columns,
        trend_periods=trend_periods,
    )

    result = add_seasonality_features(result)

    return result


def add_lag_features(
    dataframe: DataFrame,
    target_column: str,
    group_columns: Sequence[str] = (),
    lag_periods: Sequence[int] = DEFAULT_LAG_PERIODS,
) -> DataFrame:
    """
    Add historical target values for configured lag periods.
    """

    result = dataframe
    window = _ordered_window(group_columns)

    for period in lag_periods:
        result = result.withColumn(
            f"{target_column}_lag_{period}",
            F.lag(F.col(target_column), int(period)).over(window),
        )

    return result


def add_rolling_features(
    dataframe: DataFrame,
    target_column: str,
    group_columns: Sequence[str] = (),
    rolling_windows: Sequence[int] = DEFAULT_ROLLING_WINDOWS,
) -> DataFrame:
    """
    Add historical rolling statistics.

    Each rolling frame ends at the previous row, preventing target leakage.
    """

    result = dataframe
    ordered_window = _ordered_window(group_columns)

    for window_size in rolling_windows:
        historical_window = ordered_window.rowsBetween(
            -int(window_size),
            -1,
        )

        result = (
            result
            .withColumn(
                f"{target_column}_rolling_mean_{window_size}",
                F.avg(F.col(target_column)).over(historical_window),
            )
            .withColumn(
                f"{target_column}_rolling_std_{window_size}",
                F.stddev_samp(F.col(target_column)).over(historical_window),
            )
            .withColumn(
                f"{target_column}_rolling_min_{window_size}",
                F.min(F.col(target_column)).over(historical_window),
            )
            .withColumn(
                f"{target_column}_rolling_max_{window_size}",
                F.max(F.col(target_column)).over(historical_window),
            )
        )

    return result


def add_trend_features(
    dataframe: DataFrame,
    target_column: str,
    group_columns: Sequence[str] = (),
    trend_periods: Sequence[int] = DEFAULT_TREND_PERIODS,
) -> DataFrame:
    """
    Add leakage-safe historical change and growth indicators.

    All calculations use values available before the forecast date.
    The current row's target value is never used as an input feature.
    """

    result = dataframe
    window = _ordered_window(group_columns)

    previous_day_value = F.lag(
        F.col(target_column),
        1,
    ).over(window)

    for period in trend_periods:
        historical_value = F.lag(
            F.col(target_column),
            int(period) + 1,
        ).over(window)

        result = (
            result
            .withColumn(
                f"{target_column}_change_{period}",
                previous_day_value - historical_value,
            )
            .withColumn(
                f"{target_column}_growth_rate_{period}",
                _safe_growth_rate(
                    current_value=previous_day_value,
                    previous_value=historical_value,
                ),
            )
        )

    rolling_mean_7 = f"{target_column}_rolling_mean_7"
    rolling_mean_30 = f"{target_column}_rolling_mean_30"

    if (
        rolling_mean_7 in result.columns
        and rolling_mean_30 in result.columns
    ):
        result = result.withColumn(
            f"{target_column}_momentum_7_30",
            F.when(
                F.col(rolling_mean_30).isNull()
                | (F.col(rolling_mean_30) == 0),
                F.lit(None).cast("double"),
            ).otherwise(
                F.col(rolling_mean_7)
                / F.col(rolling_mean_30)
            ),
        )

    return result


def add_seasonality_features(dataframe: DataFrame) -> DataFrame:
    """
    Add calendar-based seasonality indicators.

    Existing Gold calendar columns are preserved and extended.
    """

    date_column = F.col(DATE_COLUMN)

    return (
        dataframe
        .withColumn(
            "day_of_month",
            F.dayofmonth(date_column),
        )
        .withColumn(
            "quarter",
            F.quarter(date_column),
        )
        .withColumn(
            "is_month_start",
            F.when(
                F.dayofmonth(date_column) == 1,
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "is_month_end",
            F.when(
                F.to_date(date_column) == F.last_day(date_column),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "is_quarter_start",
            F.when(
                F.month(date_column).isin(1, 4, 7, 10)
                & (F.dayofmonth(date_column) == 1),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "is_quarter_end",
            F.when(
                F.month(date_column).isin(3, 6, 9, 12)
                & (
                    F.to_date(date_column)
                    == F.last_day(date_column)
                ),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
    )


def validate_ml_features(
    dataframe: DataFrame,
    target_column: str,
    lag_periods: Sequence[int] = DEFAULT_LAG_PERIODS,
    rolling_windows: Sequence[int] = DEFAULT_ROLLING_WINDOWS,
    trend_periods: Sequence[int] = DEFAULT_TREND_PERIODS,
) -> None:
    """
    Confirm that all expected ML feature columns exist.
    """

    expected_features: set[str] = {
        "day_of_month",
        "quarter",
        "is_month_start",
        "is_month_end",
        "is_quarter_start",
        "is_quarter_end",
    }

    for period in lag_periods:
        expected_features.add(
            f"{target_column}_lag_{period}"
        )

    for window_size in rolling_windows:
        expected_features.update(
            {
                f"{target_column}_rolling_mean_{window_size}",
                f"{target_column}_rolling_std_{window_size}",
                f"{target_column}_rolling_min_{window_size}",
                f"{target_column}_rolling_max_{window_size}",
            }
        )

    for period in trend_periods:
        expected_features.update(
            {
                f"{target_column}_change_{period}",
                f"{target_column}_growth_rate_{period}",
            }
        )

    if 7 in rolling_windows and 30 in rolling_windows:
        expected_features.add(
            f"{target_column}_momentum_7_30"
        )

    missing_features = sorted(
        expected_features.difference(dataframe.columns)
    )

    if missing_features:
        raise ValueError(
            "ML feature generation is incomplete. "
            f"Missing features: {missing_features}"
        )


def _ordered_window(
    group_columns: Sequence[str],
) -> Window:
    """
    Create the canonical chronological Spark window.
    """

    if group_columns:
        return (
            Window
            .partitionBy(*group_columns)
            .orderBy(F.col(DATE_COLUMN))
        )

    return Window.orderBy(F.col(DATE_COLUMN))


def _safe_growth_rate(
    current_value: F.Column,
    previous_value: F.Column,
) -> F.Column:
    """
    Calculate percentage growth safely.
    """

    return (
        F.when(
            previous_value.isNull()
            | (previous_value == 0),
            F.lit(None).cast("double"),
        )
        .otherwise(
            (
                current_value.cast("double")
                - previous_value.cast("double")
            )
            / previous_value.cast("double")
        )
    )


def _validate_inputs(
    dataframe: DataFrame,
    target_column: str,
    group_columns: Sequence[str],
    lag_periods: Sequence[int],
    rolling_windows: Sequence[int],
    trend_periods: Sequence[int],
) -> None:
    """
    Validate ML feature-generation inputs.
    """

    required_columns = {
        DATE_COLUMN,
        target_column,
        *group_columns,
    }

    missing_columns = sorted(
        required_columns.difference(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Cannot generate ML features. "
            f"Missing required columns: {missing_columns}"
        )

    invalid_lags = sorted(
        period
        for period in lag_periods
        if int(period) <= 0
    )

    if invalid_lags:
        raise ValueError(
            f"Lag periods must be positive: {invalid_lags}"
        )

    invalid_windows = sorted(
        window_size
        for window_size in rolling_windows
        if int(window_size) <= 1
    )

    if invalid_windows:
        raise ValueError(
            "Rolling windows must be greater than one: "
            f"{invalid_windows}"
        )

    invalid_trends = sorted(
        period
        for period in trend_periods
        if int(period) <= 0
    )

    if invalid_trends:
        raise ValueError(
            f"Trend periods must be positive: {invalid_trends}"
        )