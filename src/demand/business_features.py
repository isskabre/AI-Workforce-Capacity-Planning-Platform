"""
Demand Intelligence Engine — Business Features

Creates operationally meaningful demand features from the Gold daily dataset.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .constants import (
    BUSINESS_FEATURES,
    GROSS_SALES_COLUMN,
    ORDER_COUNT_COLUMN,
    ORDER_LINE_COUNT_COLUMN,
    WORKLOAD_UNITS_COLUMN,
)


def add_business_features(dataframe: DataFrame) -> DataFrame:
    """
    Add standardized business demand features.

    The function preserves all existing columns and appends:

    - avg_lines_per_order
    - avg_units_per_order
    - avg_units_per_line
    - sales_per_order
    - sales_per_line

    Division-by-zero cases return null rather than invalid or infinite values.
    """

    required_columns = {
        ORDER_COUNT_COLUMN,
        ORDER_LINE_COUNT_COLUMN,
        WORKLOAD_UNITS_COLUMN,
        GROSS_SALES_COLUMN,
    }

    missing_columns = sorted(required_columns.difference(dataframe.columns))

    if missing_columns:
        raise ValueError(
            "Cannot generate business features. "
            f"Missing required columns: {missing_columns}"
        )

    return (
        dataframe
        .withColumn(
            "avg_lines_per_order",
            _safe_divide(
                numerator=F.col(ORDER_LINE_COUNT_COLUMN),
                denominator=F.col(ORDER_COUNT_COLUMN),
            ),
        )
        .withColumn(
            "avg_units_per_order",
            _safe_divide(
                numerator=F.col(WORKLOAD_UNITS_COLUMN),
                denominator=F.col(ORDER_COUNT_COLUMN),
            ),
        )
        .withColumn(
            "avg_units_per_line",
            _safe_divide(
                numerator=F.col(WORKLOAD_UNITS_COLUMN),
                denominator=F.col(ORDER_LINE_COUNT_COLUMN),
            ),
        )
        .withColumn(
            "sales_per_order",
            _safe_divide(
                numerator=F.col(GROSS_SALES_COLUMN),
                denominator=F.col(ORDER_COUNT_COLUMN),
            ),
        )
        .withColumn(
            "sales_per_line",
            _safe_divide(
                numerator=F.col(GROSS_SALES_COLUMN),
                denominator=F.col(ORDER_LINE_COUNT_COLUMN),
            ),
        )
    )


def validate_business_features(dataframe: DataFrame) -> None:
    """
    Confirm that every expected business feature exists.
    """

    missing_features = sorted(set(BUSINESS_FEATURES).difference(dataframe.columns))

    if missing_features:
        raise ValueError(
            "Business feature generation is incomplete. "
            f"Missing features: {missing_features}"
        )


def _safe_divide(
    numerator: F.Column,
    denominator: F.Column,
) -> F.Column:
    """
    Perform division safely.

    Returns null when the denominator is null, zero, or negative.
    """

    return (
        F.when(
            denominator.isNull() | (denominator <= 0),
            F.lit(None).cast("double"),
        )
        .otherwise(numerator.cast("double") / denominator.cast("double"))
    )