"""
Demand Intelligence Engine — Service Layer

Provides the public orchestration interface for validating daily demand data,
generating dataset summaries, resolving forecast profiles, and building
forecast-ready feature datasets.
"""

from __future__ import annotations

from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .business_features import (
    add_business_features,
    validate_business_features,
)
from .constants import (
    CUSTOMER_COUNT_COLUMN,
    DATE_COLUMN,
    GROSS_SALES_COLUMN,
    ORDER_COUNT_COLUMN,
    ORDER_LINE_COUNT_COLUMN,
    WORKLOAD_UNITS_COLUMN,
)
from .ml_features import (
    add_ml_features,
    validate_ml_features,
)
from .models import DemandSummary, ForecastProfile
from .profiles import (
    get_forecast_profile,
    get_primary_forecast_profile,
    validate_forecast_profile,
)


class DemandService:
    """
    Public orchestration service for the Demand Intelligence Engine.

    The service coordinates:

    - Gold dataset validation
    - Demand dataset summarization
    - Forecast profile resolution
    - Business feature generation
    - Machine-learning feature generation
    - Final forecast dataset validation

    Spark transformation logic remains in the specialized feature modules.
    """

    def __init__(
        self,
        default_dataset_name: str = "gold_daily_demand",
    ) -> None:
        """
        Initialize the service.

        Parameters
        ----------
        default_dataset_name:
            Logical name used when generating a demand summary.
        """

        normalized_name = default_dataset_name.strip()

        if not normalized_name:
            raise ValueError(
                "Default dataset name cannot be empty."
            )

        self._default_dataset_name = normalized_name

    # ============================================================
    # Public API
    # ============================================================

    def summarize_dataset(
        self,
        dataframe: DataFrame,
        target_column: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> DemandSummary:
        """
        Generate a validated summary of a daily demand dataset.

        Parameters
        ----------
        dataframe:
            Gold daily demand Spark DataFrame.

        target_column:
            Forecast target to summarize. When omitted, the target from the
            primary forecast profile is used.

        dataset_name:
            Optional logical dataset name.

        Returns
        -------
        DemandSummary
            Summary containing date coverage, record counts, timeline gaps,
            duplicate dates, and validation status.
        """

        profile = get_primary_forecast_profile()

        resolved_target = (
            target_column.strip()
            if target_column is not None
            else profile.target
        )

        if not resolved_target:
            raise ValueError(
                "Target column cannot be empty."
            )

        resolved_dataset_name = (
            dataset_name.strip()
            if dataset_name is not None
            else self._default_dataset_name
        )

        if not resolved_dataset_name:
            raise ValueError(
                "Dataset name cannot be empty."
            )

        self._validate_input_schema(
            dataframe=dataframe,
            target_column=resolved_target,
        )

        metrics = self._collect_dataset_metrics(
            dataframe=dataframe,
            target_column=resolved_target,
        )

        business_rules_passed = (
            self._count_business_rule_violations(dataframe) == 0
        )

        validation_passed = (
            metrics["null_date_records"] == 0
            and metrics["null_target_records"] == 0
            and metrics["missing_dates"] == 0
            and metrics["duplicate_dates"] == 0
            and business_rules_passed
        )

        return DemandSummary(
            dataset_name=resolved_dataset_name,
            start_date=metrics["start_date"],
            end_date=metrics["end_date"],
            total_days=metrics["total_days"],
            total_records=metrics["total_records"],
            target_column=resolved_target,
            missing_dates=metrics["missing_dates"],
            duplicate_dates=metrics["duplicate_dates"],
            validation_passed=validation_passed,
        )

    def get_profile(
        self,
        profile_name: Optional[str] = None,
    ) -> ForecastProfile:
        """
        Resolve and validate a forecast profile.

        When no profile name is provided, the primary operational profile is
        returned.
        """

        if profile_name is None:
            profile = get_primary_forecast_profile()
        else:
            normalized_name = profile_name.strip()

            if not normalized_name:
                raise ValueError(
                    "Forecast profile name cannot be empty."
                )

            profile = get_forecast_profile(normalized_name)

        validate_forecast_profile(profile)

        return profile

    def build_forecast_dataset(
        self,
        dataframe: DataFrame,
        profile_name: Optional[str] = None,
        validate_input: bool = True,
        validate_output: bool = True,
    ) -> DataFrame:
        """
        Build a forecast-ready daily demand feature dataset.

        Workflow
        --------
        1. Resolve the forecast profile.
        2. Validate the Gold input dataset.
        3. Generate business features.
        4. Generate leakage-safe ML features.
        5. Validate the resulting feature dataset.
        6. Return records ordered chronologically.

        Parameters
        ----------
        dataframe:
            Gold daily demand Spark DataFrame.

        profile_name:
            Registered forecast profile name. Defaults to the primary
            order-line demand profile.

        validate_input:
            Whether strict input-data validation should run before feature
            engineering.

        validate_output:
            Whether final feature validation should run after generation.

        Returns
        -------
        DataFrame
            Spark DataFrame containing original Gold columns, business
            features, and leakage-safe temporal ML features.
        """

        profile = self.get_profile(profile_name)

        self._validate_input_schema(
            dataframe=dataframe,
            target_column=profile.target,
        )

        if validate_input:
            self._validate_input_dataset(
                dataframe=dataframe,
                target_column=profile.target,
            )

        forecast_dataframe = add_business_features(dataframe)

        validate_business_features(forecast_dataframe)

        forecast_dataframe = add_ml_features(
            dataframe=forecast_dataframe,
            target_column=profile.target,
        )

        if validate_output:
            self.validate_forecast_dataset(
                dataframe=forecast_dataframe,
                profile_name=profile.name,
            )

        return forecast_dataframe.orderBy(
            F.col(DATE_COLUMN).asc()
        )

    def validate_forecast_dataset(
        self,
        dataframe: DataFrame,
        profile_name: Optional[str] = None,
    ) -> None:
        """
        Validate a generated forecast feature dataset.

        This validation confirms:

        - Required base columns exist
        - Business features exist
        - Expected ML features exist
        - Date values are populated
        - Target values are populated
        - Daily dates are unique

        Null values in early lag and rolling-feature rows are expected and are
        therefore not treated as validation failures.
        """

        profile = self.get_profile(profile_name)

        self._validate_input_schema(
            dataframe=dataframe,
            target_column=profile.target,
        )

        validate_business_features(dataframe)

        validate_ml_features(
            dataframe=dataframe,
            target_column=profile.target,
        )

        quality_metrics = (
            dataframe
            .agg(
                F.sum(
                    F.when(
                        F.col(DATE_COLUMN).isNull(),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("null_date_records"),
                F.sum(
                    F.when(
                        F.col(profile.target).isNull(),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("null_target_records"),
            )
            .first()
        )

        null_date_records = int(
            quality_metrics["null_date_records"] or 0
        )

        null_target_records = int(
            quality_metrics["null_target_records"] or 0
        )

        duplicate_dates = self._count_duplicate_dates(dataframe)

        validation_errors: list[str] = []

        if null_date_records:
            validation_errors.append(
                f"{null_date_records} records contain a null "
                f"'{DATE_COLUMN}' value"
            )

        if null_target_records:
            validation_errors.append(
                f"{null_target_records} records contain a null "
                f"'{profile.target}' value"
            )

        if duplicate_dates:
            validation_errors.append(
                f"{duplicate_dates} duplicate daily records were found"
            )

        if validation_errors:
            formatted_errors = "; ".join(validation_errors)

            raise ValueError(
                "Forecast dataset validation failed: "
                f"{formatted_errors}."
            )

    # ============================================================
    # Private Validation
    # ============================================================

    def _validate_input_schema(
        self,
        dataframe: DataFrame,
        target_column: str,
    ) -> None:
        """
        Validate the minimum schema required by the demand engine.
        """

        if dataframe is None:
            raise ValueError(
                "Demand DataFrame cannot be None."
            )

        required_columns = {
            DATE_COLUMN,
            target_column,
            ORDER_COUNT_COLUMN,
            ORDER_LINE_COUNT_COLUMN,
            WORKLOAD_UNITS_COLUMN,
            GROSS_SALES_COLUMN,
            CUSTOMER_COUNT_COLUMN,
        }

        missing_columns = sorted(
            required_columns.difference(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Demand dataset is missing required columns: "
                f"{missing_columns}"
            )

    def _validate_input_dataset(
        self,
        dataframe: DataFrame,
        target_column: str,
    ) -> None:
        """
        Perform strict business and timeline validation before feature creation.
        """

        metrics = self._collect_dataset_metrics(
            dataframe=dataframe,
            target_column=target_column,
        )

        validation_errors: list[str] = []

        if metrics["total_records"] == 0:
            validation_errors.append(
                "the dataset contains no records"
            )

        if metrics["null_date_records"] > 0:
            validation_errors.append(
                f"{metrics['null_date_records']} records contain null dates"
            )

        if metrics["null_target_records"] > 0:
            validation_errors.append(
                f"{metrics['null_target_records']} records contain a null "
                f"'{target_column}' value"
            )

        if metrics["duplicate_dates"] > 0:
            validation_errors.append(
                f"{metrics['duplicate_dates']} duplicate daily records exist"
            )

        if metrics["missing_dates"] > 0:
            validation_errors.append(
                f"{metrics['missing_dates']} calendar dates are missing"
            )

        business_rule_violations = (
            self._count_business_rule_violations(dataframe)
        )

        if business_rule_violations > 0:
            validation_errors.append(
                f"{business_rule_violations} records violate demand "
                "business sanity rules"
            )

        if validation_errors:
            formatted_errors = "; ".join(validation_errors)

            raise ValueError(
                "Demand input validation failed: "
                f"{formatted_errors}."
            )

    # ============================================================
    # Private Metrics
    # ============================================================

    def _collect_dataset_metrics(
        self,
        dataframe: DataFrame,
        target_column: str,
    ) -> dict[str, object]:
        """
        Collect core dataset quality and timeline metrics in one Spark action.
        """

        metrics_row = (
            dataframe
            .agg(
                F.count(F.lit(1)).alias("total_records"),
                F.countDistinct(
                    F.col(DATE_COLUMN)
                ).alias("distinct_dates"),
                F.min(
                    F.to_date(F.col(DATE_COLUMN))
                ).alias("start_date"),
                F.max(
                    F.to_date(F.col(DATE_COLUMN))
                ).alias("end_date"),
                F.sum(
                    F.when(
                        F.col(DATE_COLUMN).isNull(),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("null_date_records"),
                F.sum(
                    F.when(
                        F.col(target_column).isNull(),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("null_target_records"),
            )
            .first()
        )

        total_records = int(
            metrics_row["total_records"] or 0
        )

        distinct_dates = int(
            metrics_row["distinct_dates"] or 0
        )

        start_date = metrics_row["start_date"]
        end_date = metrics_row["end_date"]

        null_date_records = int(
            metrics_row["null_date_records"] or 0
        )

        null_target_records = int(
            metrics_row["null_target_records"] or 0
        )

        if start_date is None or end_date is None:
            total_days = 0
        else:
            total_days = (
                end_date - start_date
            ).days + 1

        duplicate_dates = max(
            total_records
            - null_date_records
            - distinct_dates,
            0,
        )

        missing_dates = max(
            total_days - distinct_dates,
            0,
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "total_records": total_records,
            "distinct_dates": distinct_dates,
            "missing_dates": missing_dates,
            "duplicate_dates": duplicate_dates,
            "null_date_records": null_date_records,
            "null_target_records": null_target_records,
        }

    def _count_duplicate_dates(
        self,
        dataframe: DataFrame,
    ) -> int:
        """
        Count excess records created by duplicate dates.
        """

        duplicate_row = (
            dataframe
            .where(F.col(DATE_COLUMN).isNotNull())
            .groupBy(DATE_COLUMN)
            .count()
            .where(F.col("count") > 1)
            .agg(
                F.sum(
                    F.col("count") - F.lit(1)
                ).alias("duplicate_dates")
            )
            .first()
        )

        return int(
            duplicate_row["duplicate_dates"] or 0
        )

    def _count_business_rule_violations(
        self,
        dataframe: DataFrame,
    ) -> int:
        """
        Count records violating approved daily-demand sanity rules.

        Rules
        -----
        - order_line_count must be greater than or equal to order_count
        - workload_units must be greater than or equal to order_line_count
        - customer_count must be less than or equal to order_count
        - major demand measures cannot be negative
        """

        violation_condition = (
            (
                F.col(ORDER_LINE_COUNT_COLUMN)
                < F.col(ORDER_COUNT_COLUMN)
            )
            | (
                F.col(WORKLOAD_UNITS_COLUMN)
                < F.col(ORDER_LINE_COUNT_COLUMN)
            )
            | (
                F.col(CUSTOMER_COUNT_COLUMN)
                > F.col(ORDER_COUNT_COLUMN)
            )
            | (F.col(ORDER_COUNT_COLUMN) < 0)
            | (F.col(ORDER_LINE_COUNT_COLUMN) < 0)
            | (F.col(WORKLOAD_UNITS_COLUMN) < 0)
            | (F.col(GROSS_SALES_COLUMN) < 0)
            | (F.col(CUSTOMER_COUNT_COLUMN) < 0)
        )

        violation_row = (
            dataframe
            .agg(
                F.sum(
                    F.when(
                        violation_condition,
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("violation_count")
            )
            .first()
        )

        return int(
            violation_row["violation_count"] or 0
        )