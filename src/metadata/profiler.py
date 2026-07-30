"""
Spark-based dataset profiling for the Forecast-Aware Metadata Framework.

The profiler converts a PySpark DataFrame into structured dataset-level
and column-level statistics without exposing Spark-specific objects to
downstream platform services.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    ByteType,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StringType,
    TimestampType,
)

from .exceptions import DatasetProfilingError, UnsupportedDatasetError
from .models import ColumnProfile, DatasetStatistics


NUMERIC_TYPES = (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
)


class SparkDatasetProfiler:
    """
    Generate structural and statistical metadata for a Spark DataFrame.

    The profiler performs dataset-level analysis and column-level analysis.
    It returns typed domain objects that can be consumed without requiring
    downstream services to understand Spark internals.
    """

    def __init__(
        self,
        approximate_distinct: bool = True,
        relative_standard_deviation: float = 0.02,
    ) -> None:
        """
        Initialize the profiler.

        Args:
            approximate_distinct:
                Use Spark's approximate distinct-count algorithm when True.
                This improves performance on larger datasets.

            relative_standard_deviation:
                Maximum relative standard deviation used by
                approx_count_distinct.
        """

        if relative_standard_deviation <= 0:
            raise ValueError(
                "relative_standard_deviation must be greater than zero."
            )

        self.approximate_distinct = approximate_distinct
        self.relative_standard_deviation = relative_standard_deviation

    def profile_statistics(
        self,
        dataframe: DataFrame,
    ) -> DatasetStatistics:
        """
        Produce dataset-level structural and quality statistics.

        Args:
            dataframe: Spark DataFrame to profile.

        Returns:
            DatasetStatistics containing row, schema, null, and duplicate
            metrics.
        """

        self._validate_dataframe(dataframe)

        try:
            row_count = dataframe.count()
            column_count = len(dataframe.columns)

            type_counts = self._count_column_types(dataframe)

            null_cell_count = self._calculate_total_null_cells(
                dataframe=dataframe,
                row_count=row_count,
            )

            total_cell_count = row_count * column_count

            null_cell_percentage = self._percentage(
                numerator=null_cell_count,
                denominator=total_cell_count,
            )

            duplicate_row_count = self._calculate_duplicate_rows(
                dataframe=dataframe,
                row_count=row_count,
            )

            duplicate_row_percentage = self._percentage(
                numerator=duplicate_row_count,
                denominator=row_count,
            )

            return DatasetStatistics(
                row_count=row_count,
                column_count=column_count,
                numeric_column_count=type_counts["numeric"],
                string_column_count=type_counts["string"],
                boolean_column_count=type_counts["boolean"],
                date_column_count=type_counts["date"],
                timestamp_column_count=type_counts["timestamp"],
                other_column_count=type_counts["other"],
                null_cell_count=null_cell_count,
                null_cell_percentage=null_cell_percentage,
                duplicate_row_count=duplicate_row_count,
                duplicate_row_percentage=duplicate_row_percentage,
            )

        except DatasetProfilingError:
            raise
        except Exception as exc:
            raise DatasetProfilingError(
                f"Dataset-level profiling failed: {exc}"
            ) from exc

    def profile_columns(
        self,
        dataframe: DataFrame,
        row_count: Optional[int] = None,
    ) -> List[ColumnProfile]:
        """
        Produce one profile for every DataFrame column.

        Numeric columns receive descriptive statistics. String columns
        receive length statistics. Date and timestamp columns receive
        minimum and maximum values.

        Args:
            dataframe: Spark DataFrame to profile.
            row_count: Optional previously calculated row count.

        Returns:
            Ordered list of ColumnProfile objects.
        """

        self._validate_dataframe(dataframe)

        try:
            resolved_row_count = (
                dataframe.count()
                if row_count is None
                else int(row_count)
            )

            profiles: List[ColumnProfile] = []

            for field in dataframe.schema.fields:
                profiles.append(
                    self._profile_column(
                        dataframe=dataframe,
                        column_name=field.name,
                        data_type=field.dataType,
                        nullable=field.nullable,
                        row_count=resolved_row_count,
                    )
                )

            return profiles

        except DatasetProfilingError:
            raise
        except Exception as exc:
            raise DatasetProfilingError(
                f"Column profiling failed: {exc}"
            ) from exc

    def profile(
        self,
        dataframe: DataFrame,
    ) -> tuple[DatasetStatistics, List[ColumnProfile]]:
        """
        Produce complete dataset and column statistics.

        Returns:
            Tuple containing DatasetStatistics and column profiles.
        """

        statistics = self.profile_statistics(dataframe)

        columns = self.profile_columns(
            dataframe=dataframe,
            row_count=statistics.row_count,
        )

        return statistics, columns

    def _profile_column(
        self,
        dataframe: DataFrame,
        column_name: str,
        data_type: Any,
        nullable: bool,
        row_count: int,
    ) -> ColumnProfile:
        """Profile one column according to its Spark data type."""

        escaped_column = F.col(f"`{column_name}`")

        null_count = dataframe.filter(
            escaped_column.isNull()
        ).count()

        null_percentage = self._percentage(
            numerator=null_count,
            denominator=row_count,
        )

        distinct_count = self._distinct_count(
            dataframe=dataframe,
            column_name=column_name,
        )

        try:
            if isinstance(data_type, NUMERIC_TYPES):
                return self._profile_numeric_column(
                    dataframe=dataframe,
                    column_name=column_name,
                    data_type=data_type.simpleString(),
                    nullable=nullable,
                    null_count=null_count,
                    null_percentage=null_percentage,
                    distinct_count=distinct_count,
                )

            if isinstance(data_type, StringType):
                return self._profile_string_column(
                    dataframe=dataframe,
                    column_name=column_name,
                    data_type=data_type.simpleString(),
                    nullable=nullable,
                    null_count=null_count,
                    null_percentage=null_percentage,
                    distinct_count=distinct_count,
                )

            if isinstance(data_type, (DateType, TimestampType)):
                return self._profile_temporal_column(
                    dataframe=dataframe,
                    column_name=column_name,
                    data_type=data_type.simpleString(),
                    nullable=nullable,
                    null_count=null_count,
                    null_percentage=null_percentage,
                    distinct_count=distinct_count,
                )

            return ColumnProfile(
                column_name=column_name,
                data_type=data_type.simpleString(),
                nullable=nullable,
                null_count=null_count,
                null_percentage=null_percentage,
                distinct_count=distinct_count,
            )

        except Exception as exc:
            return ColumnProfile(
                column_name=column_name,
                data_type=data_type.simpleString(),
                nullable=nullable,
                null_count=null_count,
                null_percentage=null_percentage,
                distinct_count=distinct_count,
                profile_status="PARTIAL",
                profile_message=str(exc),
            )

    def _profile_numeric_column(
        self,
        dataframe: DataFrame,
        column_name: str,
        data_type: str,
        nullable: bool,
        null_count: int,
        null_percentage: float,
        distinct_count: int,
    ) -> ColumnProfile:
        """Calculate descriptive statistics for one numeric column."""

        column = F.col(f"`{column_name}`")

        row = (
            dataframe
            .select(
                F.min(column).alias("minimum"),
                F.max(column).alias("maximum"),
                F.avg(column).alias("mean"),
                F.expr(
                    f"percentile_approx(`{column_name}`, 0.5, 10000)"
                ).alias("median"),
                F.stddev(column).alias("standard_deviation"),
            )
            .first()
        )

        return ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            null_count=null_count,
            null_percentage=null_percentage,
            distinct_count=distinct_count,
            minimum=self._normalize_value(row["minimum"]),
            maximum=self._normalize_value(row["maximum"]),
            mean=self._to_optional_float(row["mean"]),
            median=self._to_optional_float(row["median"]),
            standard_deviation=self._to_optional_float(
                row["standard_deviation"]
            ),
        )

    def _profile_string_column(
        self,
        dataframe: DataFrame,
        column_name: str,
        data_type: str,
        nullable: bool,
        null_count: int,
        null_percentage: float,
        distinct_count: int,
    ) -> ColumnProfile:
        """Calculate value and length statistics for one string column."""

        column = F.col(f"`{column_name}`")
        length_column = F.length(column)

        row = (
            dataframe
            .select(
                F.min(column).alias("minimum"),
                F.max(column).alias("maximum"),
                F.min(length_column).alias("minimum_length"),
                F.max(length_column).alias("maximum_length"),
                F.avg(length_column).alias("average_length"),
            )
            .first()
        )

        return ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            null_count=null_count,
            null_percentage=null_percentage,
            distinct_count=distinct_count,
            minimum=self._normalize_value(row["minimum"]),
            maximum=self._normalize_value(row["maximum"]),
            minimum_length=row["minimum_length"],
            maximum_length=row["maximum_length"],
            average_length=self._to_optional_float(
                row["average_length"]
            ),
        )

    def _profile_temporal_column(
        self,
        dataframe: DataFrame,
        column_name: str,
        data_type: str,
        nullable: bool,
        null_count: int,
        null_percentage: float,
        distinct_count: int,
    ) -> ColumnProfile:
        """Calculate minimum and maximum values for a temporal column."""

        column = F.col(f"`{column_name}`")

        row = (
            dataframe
            .select(
                F.min(column).alias("minimum"),
                F.max(column).alias("maximum"),
            )
            .first()
        )

        return ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            nullable=nullable,
            null_count=null_count,
            null_percentage=null_percentage,
            distinct_count=distinct_count,
            minimum=self._normalize_value(row["minimum"]),
            maximum=self._normalize_value(row["maximum"]),
        )

    def _distinct_count(
        self,
        dataframe: DataFrame,
        column_name: str,
    ) -> int:
        """Calculate exact or approximate distinct values."""

        column = F.col(f"`{column_name}`")

        if self.approximate_distinct:
            value = (
                dataframe
                .select(
                    F.approx_count_distinct(
                        column,
                        self.relative_standard_deviation,
                    ).alias("distinct_count")
                )
                .first()["distinct_count"]
            )
        else:
            value = (
                dataframe
                .select(
                    F.countDistinct(column).alias("distinct_count")
                )
                .first()["distinct_count"]
            )

        return int(value or 0)

    @staticmethod
    def _calculate_total_null_cells(
        dataframe: DataFrame,
        row_count: int,
    ) -> int:
        """Calculate the total number of null cells in the DataFrame."""

        if row_count == 0 or not dataframe.columns:
            return 0

        expressions = [
            F.sum(
                F.when(
                    F.col(f"`{column_name}`").isNull(),
                    F.lit(1),
                ).otherwise(F.lit(0))
            ).alias(column_name)
            for column_name in dataframe.columns
        ]

        result = dataframe.agg(*expressions).first()

        return int(
            sum(
                int(result[column_name] or 0)
                for column_name in dataframe.columns
            )
        )

    @staticmethod
    def _calculate_duplicate_rows(
        dataframe: DataFrame,
        row_count: int,
    ) -> int:
        """Calculate the number of duplicate rows."""

        if row_count == 0:
            return 0

        distinct_row_count = dataframe.dropDuplicates().count()

        return max(row_count - distinct_row_count, 0)

    @staticmethod
    def _count_column_types(
        dataframe: DataFrame,
    ) -> Dict[str, int]:
        """Classify Spark schema fields into supported metadata groups."""

        counts = {
            "numeric": 0,
            "string": 0,
            "boolean": 0,
            "date": 0,
            "timestamp": 0,
            "other": 0,
        }

        for field in dataframe.schema.fields:
            data_type = field.dataType

            if isinstance(data_type, NUMERIC_TYPES):
                counts["numeric"] += 1
            elif isinstance(data_type, StringType):
                counts["string"] += 1
            elif isinstance(data_type, BooleanType):
                counts["boolean"] += 1
            elif isinstance(data_type, DateType):
                counts["date"] += 1
            elif isinstance(data_type, TimestampType):
                counts["timestamp"] += 1
            else:
                counts["other"] += 1

        return counts

    @staticmethod
    def _validate_dataframe(dataframe: DataFrame) -> None:
        """Validate the profiler input."""

        if dataframe is None:
            raise UnsupportedDatasetError(
                "The dataset cannot be None."
            )

        if not isinstance(dataframe, DataFrame):
            raise UnsupportedDatasetError(
                "SparkDatasetProfiler requires a PySpark DataFrame."
            )

        if not dataframe.columns:
            raise DatasetProfilingError(
                "The dataset contains no columns."
            )

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> float:
        """Return a percentage rounded to four decimal places."""

        if denominator <= 0:
            return 0.0

        return round(
            (float(numerator) / float(denominator)) * 100.0,
            4,
        )

    @staticmethod
    def _normalize_value(value: Any) -> Optional[Any]:
        """Convert values to metadata-safe scalar representations."""

        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return value

    @staticmethod
    def _to_optional_float(value: Any) -> Optional[float]:
        """Convert a numeric value to float while preserving nulls."""

        if value is None:
            return None

        return float(value)