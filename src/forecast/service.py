"""
Enterprise Forecast Dataset — Service Layer

Provides the public orchestration API for creating a versioned,
model-ready enterprise forecasting dataset.

Responsibilities
----------------
- Validate the forecasting feature dataset.
- Coordinate warm-up removal and temporal splitting.
- Generate reproducibility metadata.
- Generate an operational execution summary.
- Construct the ForecastDatasetBundle.
- Optionally persist all forecast dataset artifacts.

The notebook should interact only with ForecastDatasetService and should not
directly coordinate splitter or persistence operations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import NumericType

from forecast.constants import (
    DATE_COLUMN,
    DEFAULT_FORECAST_HORIZON,
    DEFAULT_TEST_RATIO,
    DEFAULT_TRAIN_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WARMUP_DAYS,
    FORECAST_DATASET_NAME,
    FORECAST_DATASET_VERSION,
    STATUS_COMPLETED,
    STATUS_PERSISTED,
    TEMPORAL_SPLIT_STRATEGY,
)
from forecast.models import (
    DatasetSplit,
    ForecastDatasetBundle,
    ForecastDatasetMetadata,
    ForecastDatasetSummary,
    ForecastPersistenceResult,
)
from forecast.persistence import ForecastDatasetPersistence
from forecast.splitter import ForecastDatasetSplitter


# ============================================================
# Forecast Dataset Service
# ============================================================

class ForecastDatasetService:
    """
    Build a validated and optionally persisted forecast dataset bundle.

    This class is the only public orchestration entry point required by
    notebooks and downstream application services.

    Examples
    --------
    Build without persistence:

    >>> service = ForecastDatasetService(
    ...     spark=spark,
    ...     target_column="order_line_count",
    ... )
    >>> bundle = service.build(forecast_df)

    Build and persist:

    >>> service = ForecastDatasetService(
    ...     spark=spark,
    ...     target_column="order_line_count",
    ...     root_path="s3://bucket/project/forecasts",
    ... )
    >>> bundle = service.build(forecast_df)
    """

    def __init__(
        self,
        *,
        spark: SparkSession,
        target_column: str,
        date_column: str = DATE_COLUMN,
        forecast_horizon: int = DEFAULT_FORECAST_HORIZON,
        dataset_name: str = FORECAST_DATASET_NAME,
        dataset_version: str = FORECAST_DATASET_VERSION,
        warmup_days: int = DEFAULT_WARMUP_DAYS,
        train_ratio: float = DEFAULT_TRAIN_RATIO,
        validation_ratio: float = DEFAULT_VALIDATION_RATIO,
        test_ratio: float = DEFAULT_TEST_RATIO,
        split_strategy: str = TEMPORAL_SPLIT_STRATEGY,
        root_path: Optional[str] = None,
        splitter: Optional[ForecastDatasetSplitter] = None,
        persistence: Optional[ForecastDatasetPersistence] = None,
    ) -> None:
        """
        Initialize the forecast dataset service.

        Parameters
        ----------
        spark:
            Active SparkSession.

        target_column:
            Historical target variable used for supervised forecasting.

        date_column:
            Column defining chronological dataset order.

        forecast_horizon:
            Number of future periods the forecasting models are expected
            to predict.

        dataset_name:
            Canonical forecast dataset identifier.

        dataset_version:
            Semantic version assigned to the generated dataset.

        warmup_days:
            Number of earliest observations removed before splitting.

        train_ratio:
            Proportion of model-ready observations allocated to training.

        validation_ratio:
            Proportion allocated to validation.

        test_ratio:
            Proportion allocated to testing.

        split_strategy:
            Dataset splitting strategy. Only temporal splitting is supported.

        root_path:
            Optional storage root. When supplied, the completed dataset bundle
            is automatically persisted.

        splitter:
            Optional preconfigured ForecastDatasetSplitter dependency.

        persistence:
            Optional preconfigured ForecastDatasetPersistence dependency.

            ``root_path`` and ``persistence`` cannot both be supplied because
            that would create ambiguous persistence configuration.
        """

        self.spark = spark
        self.target_column = target_column
        self.date_column = date_column
        self.forecast_horizon = forecast_horizon
        self.dataset_name = dataset_name
        self.dataset_version = dataset_version
        self.warmup_days = warmup_days
        self.train_ratio = train_ratio
        self.validation_ratio = validation_ratio
        self.test_ratio = test_ratio
        self.split_strategy = split_strategy
        self.root_path = root_path

        self._validate_configuration(
            splitter=splitter,
            persistence=persistence,
        )

        self.splitter = splitter or ForecastDatasetSplitter(
            date_column=self.date_column,
            warmup_days=self.warmup_days,
            train_ratio=self.train_ratio,
            validation_ratio=self.validation_ratio,
            test_ratio=self.test_ratio,
            split_strategy=self.split_strategy,
        )

        self.persistence = self._resolve_persistence(
            root_path=root_path,
            persistence=persistence,
        )

        self._validate_dependency_alignment()

    # ========================================================
    # Public API
    # ========================================================

    def build(
        self,
        dataframe: DataFrame,
        *,
        persist: Optional[bool] = None,
    ) -> ForecastDatasetBundle:
        """
        Build the enterprise forecast dataset.

        Processing flow
        ---------------
        1. Validate the feature dataset.
        2. Remove warm-up observations.
        3. Create chronological train, validation, and test splits.
        4. Generate metadata and execution summary.
        5. Build the typed forecast dataset bundle.
        6. Optionally persist all artifacts.

        Parameters
        ----------
        dataframe:
            Forecasting feature DataFrame produced by the Demand Intelligence
            Engine.

        persist:
            Optional runtime persistence override.

            - ``None``: Persist when a persistence dependency is configured.
            - ``True``: Require and execute persistence.
            - ``False``: Build the bundle without persistence.

        Returns
        -------
        ForecastDatasetBundle
            Typed dataset bundle containing train, validation, and test
            DataFrames, metadata, summary, and an optional persistence result.
        """

        generated_at_utc = datetime.now(timezone.utc)

        self._validate_input_dataset(dataframe)

        (
            model_ready_dataframe,
            warmup_rows_removed,
            train_split,
            validation_split,
            test_split,
        ) = self._prepare_dataset(dataframe)

        source_rows = (
            train_split.row_count
            + validation_split.row_count
            + test_split.row_count
            + warmup_rows_removed
        )

        model_ready_rows = (
            train_split.row_count
            + validation_split.row_count
            + test_split.row_count
        )

        source_start_date, source_end_date = (
            self._calculate_date_boundaries(dataframe)
        )

        persistence_requested = self._resolve_persist_flag(
            persist
        )

        final_status = (
            STATUS_PERSISTED
            if persistence_requested
            else STATUS_COMPLETED
        )

        metadata = self._create_metadata(
            source_rows=source_rows,
            warmup_rows_removed=warmup_rows_removed,
            model_ready_rows=model_ready_rows,
            total_columns=len(model_ready_dataframe.columns),
            source_start_date=source_start_date,
            source_end_date=source_end_date,
            train_split=train_split,
            validation_split=validation_split,
            test_split=test_split,
            generated_at_utc=generated_at_utc,
        )

        summary = self._create_summary(
            source_rows=source_rows,
            warmup_rows_removed=warmup_rows_removed,
            model_ready_rows=model_ready_rows,
            total_columns=len(model_ready_dataframe.columns),
            train_split=train_split,
            validation_split=validation_split,
            test_split=test_split,
            status=final_status,
        )

        bundle = self._build_bundle(
            train_split=train_split,
            validation_split=validation_split,
            test_split=test_split,
            metadata=metadata,
            summary=summary,
        )

        self._validate_bundle(bundle)

        if persistence_requested:
            bundle.persistence = self._persist_dataset(bundle)

        return bundle

    # ========================================================
    # Dataset Preparation
    # ========================================================

    def _prepare_dataset(
        self,
        dataframe: DataFrame,
    ) -> tuple[
        DataFrame,
        int,
        DatasetSplit,
        DatasetSplit,
        DatasetSplit,
    ]:
        """
        Coordinate warm-up removal and temporal dataset splitting.
        """

        return self.splitter.prepare_and_split(dataframe)

    # ========================================================
    # Metadata Creation
    # ========================================================

    def _create_metadata(
        self,
        *,
        source_rows: int,
        warmup_rows_removed: int,
        model_ready_rows: int,
        total_columns: int,
        source_start_date: object,
        source_end_date: object,
        train_split: DatasetSplit,
        validation_split: DatasetSplit,
        test_split: DatasetSplit,
        generated_at_utc: datetime,
    ) -> ForecastDatasetMetadata:
        """
        Create reproducibility and lineage metadata.
        """

        return ForecastDatasetMetadata(
            dataset_name=self.dataset_name,
            dataset_version=self.dataset_version,
            target_column=self.target_column,
            date_column=self.date_column,
            forecast_horizon=self.forecast_horizon,
            warmup_days=self.warmup_days,
            split_strategy=self.split_strategy,
            train_ratio=self.train_ratio,
            validation_ratio=self.validation_ratio,
            test_ratio=self.test_ratio,
            source_rows=source_rows,
            warmup_rows_removed=warmup_rows_removed,
            model_ready_rows=model_ready_rows,
            total_columns=total_columns,
            start_date=source_start_date,
            end_date=source_end_date,
            train_start_date=train_split.start_date,
            train_end_date=train_split.end_date,
            validation_start_date=validation_split.start_date,
            validation_end_date=validation_split.end_date,
            test_start_date=test_split.start_date,
            test_end_date=test_split.end_date,
            generated_at_utc=generated_at_utc,
        )

    # ========================================================
    # Summary Creation
    # ========================================================

    @staticmethod
    def _create_summary(
        *,
        source_rows: int,
        warmup_rows_removed: int,
        model_ready_rows: int,
        total_columns: int,
        train_split: DatasetSplit,
        validation_split: DatasetSplit,
        test_split: DatasetSplit,
        status: str,
    ) -> ForecastDatasetSummary:
        """
        Create the operational dataset execution summary.
        """

        return ForecastDatasetSummary(
            source_rows=source_rows,
            warmup_rows_removed=warmup_rows_removed,
            model_ready_rows=model_ready_rows,
            train_rows=train_split.row_count,
            validation_rows=validation_split.row_count,
            test_rows=test_split.row_count,
            total_columns=total_columns,
            validation_passed=True,
            status=status,
        )

    # ========================================================
    # Bundle Construction
    # ========================================================

    @staticmethod
    def _build_bundle(
        *,
        train_split: DatasetSplit,
        validation_split: DatasetSplit,
        test_split: DatasetSplit,
        metadata: ForecastDatasetMetadata,
        summary: ForecastDatasetSummary,
    ) -> ForecastDatasetBundle:
        """
        Construct the standard ForecastDatasetBundle.
        """

        return ForecastDatasetBundle(
            train=train_split,
            validation=validation_split,
            test=test_split,
            metadata=metadata,
            summary=summary,
        )

    # ========================================================
    # Persistence Orchestration
    # ========================================================

    def _persist_dataset(
        self,
        bundle: ForecastDatasetBundle,
    ) -> ForecastPersistenceResult:
        """
        Persist the validated forecast dataset bundle.
        """

        if self.persistence is None:
            raise RuntimeError(
                "Forecast dataset persistence was requested, but no "
                "ForecastDatasetPersistence dependency is configured."
            )

        return self.persistence.persist_bundle(bundle)

    def _resolve_persist_flag(
        self,
        persist: Optional[bool],
    ) -> bool:
        """
        Determine whether the current build should persist artifacts.
        """

        if persist is not None and not isinstance(persist, bool):
            raise TypeError(
                "persist must be True, False, or None."
            )

        if persist is None:
            return self.persistence is not None

        if persist and self.persistence is None:
            raise ValueError(
                "persist=True requires either root_path or a configured "
                "ForecastDatasetPersistence dependency."
            )

        return persist

    def _resolve_persistence(
        self,
        *,
        root_path: Optional[str],
        persistence: Optional[ForecastDatasetPersistence],
    ) -> Optional[ForecastDatasetPersistence]:
        """
        Resolve the persistence dependency.
        """

        if persistence is not None:
            return persistence

        if root_path is None:
            return None

        return ForecastDatasetPersistence(
            spark=self.spark,
            root_path=root_path,
        )

    # ========================================================
    # Service Configuration Validation
    # ========================================================

    def _validate_configuration(
        self,
        *,
        splitter: Optional[ForecastDatasetSplitter],
        persistence: Optional[ForecastDatasetPersistence],
    ) -> None:
        """
        Validate service configuration before dependencies are created.
        """

        if self.spark is None:
            raise ValueError(
                "spark cannot be None."
            )

        required_spark_attributes = (
            "createDataFrame",
            "read",
        )

        missing_spark_attributes = [
            attribute
            for attribute in required_spark_attributes
            if not hasattr(self.spark, attribute)
        ]

        if missing_spark_attributes:
            raise TypeError(
                "spark must be an active Spark or Spark Connect session. "
                f"Missing required attributes: {missing_spark_attributes}."
            )

        self._validate_non_empty_string(
            value=self.target_column,
            name="target_column",
        )

        self._validate_non_empty_string(
            value=self.date_column,
            name="date_column",
        )

        self._validate_non_empty_string(
            value=self.dataset_name,
            name="dataset_name",
        )

        self._validate_non_empty_string(
            value=self.dataset_version,
            name="dataset_version",
        )

        if not isinstance(self.forecast_horizon, int):
            raise TypeError(
                "forecast_horizon must be an integer."
            )

        if self.forecast_horizon <= 0:
            raise ValueError(
                "forecast_horizon must be greater than zero."
            )

        if not isinstance(self.warmup_days, int):
            raise TypeError(
                "warmup_days must be an integer."
            )

        if self.warmup_days < 0:
            raise ValueError(
                "warmup_days cannot be negative."
            )

        if root_path_supplied := (self.root_path is not None):
            self._validate_non_empty_string(
                value=self.root_path,
                name="root_path",
            )

        if root_path_supplied and persistence is not None:
            raise ValueError(
                "Supply either root_path or persistence, not both."
            )

        if splitter is not None and not isinstance(
            splitter,
            ForecastDatasetSplitter,
        ):
            raise TypeError(
                "splitter must be a ForecastDatasetSplitter."
            )

        if persistence is not None and not isinstance(
            persistence,
            ForecastDatasetPersistence,
        ):
            raise TypeError(
                "persistence must be a ForecastDatasetPersistence."
            )

    def _validate_dependency_alignment(self) -> None:
        """
        Ensure injected dependencies match the service configuration.
        """

        splitter_mismatches: list[str] = []

        if self.splitter.date_column != self.date_column:
            splitter_mismatches.append(
                "date_column"
            )

        if self.splitter.warmup_days != self.warmup_days:
            splitter_mismatches.append(
                "warmup_days"
            )

        if self.splitter.train_ratio != self.train_ratio:
            splitter_mismatches.append(
                "train_ratio"
            )

        if (
            self.splitter.validation_ratio
            != self.validation_ratio
        ):
            splitter_mismatches.append(
                "validation_ratio"
            )

        if self.splitter.test_ratio != self.test_ratio:
            splitter_mismatches.append(
                "test_ratio"
            )

        if (
            self.splitter.split_strategy
            != self.split_strategy
        ):
            splitter_mismatches.append(
                "split_strategy"
            )

        if splitter_mismatches:
            raise ValueError(
                "The configured ForecastDatasetSplitter does not align "
                "with the service configuration. Mismatched settings: "
                f"{tuple(splitter_mismatches)}."
            )

        if (
            self.persistence is not None
            and self.persistence.spark is not self.spark
        ):
            raise ValueError(
                "ForecastDatasetPersistence must use the same SparkSession "
                "as ForecastDatasetService."
            )

    # ========================================================
    # Input Dataset Validation
    # ========================================================

    def _validate_input_dataset(
        self,
        dataframe: DataFrame,
    ) -> None:
        """
        Validate the forecast feature dataset before preparation.
        """

        if dataframe is None:
            raise ValueError(
                "ForecastDatasetService.build requires a DataFrame."
            )

        required_dataframe_attributes = (
            "columns",
            "schema",
            "filter",
            "agg",
            "count",
        )

        missing_dataframe_attributes = [
            attribute
            for attribute in required_dataframe_attributes
            if not hasattr(dataframe, attribute)
        ]

        if missing_dataframe_attributes:
            raise TypeError(
                "ForecastDatasetService.build requires a Spark or Spark Connect "
                "DataFrame. "
                f"Missing required attributes: {missing_dataframe_attributes}."
            )

        required_columns = {
            self.date_column,
            self.target_column,
        }

        missing_columns = sorted(
            required_columns.difference(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "The forecast dataset is missing required columns: "
                f"{missing_columns}. Available columns: "
                f"{dataframe.columns}"
            )

        if not dataframe.columns:
            raise ValueError(
                "The forecast dataset contains no columns."
            )

        target_field = dataframe.schema[self.target_column]

        if not isinstance(
            target_field.dataType,
            NumericType,
        ):
            raise ValueError(
                f"Target column '{self.target_column}' must be numeric. "
                f"Found: {target_field.dataType.simpleString()}."
            )

        null_target_exists = (
            dataframe
            .filter(
                F.col(self.target_column).isNull()
            )
            .limit(1)
            .count()
            > 0
        )

        if null_target_exists:
            raise ValueError(
                f"Target column '{self.target_column}' contains null "
                "values."
            )

        non_finite_target_exists = (
            dataframe
            .filter(
                F.isnan(
                    F.col(self.target_column).cast("double")
                )
                | (
                    F.abs(
                        F.col(self.target_column).cast("double")
                    )
                    == float("inf")
                )
            )
            .limit(1)
            .count()
            > 0
        )

        if non_finite_target_exists:
            raise ValueError(
                f"Target column '{self.target_column}' contains NaN or "
                "infinite values."
            )

    # ========================================================
    # Bundle Validation
    # ========================================================

    @staticmethod
    def _validate_bundle(
        bundle: ForecastDatasetBundle,
    ) -> None:
        """
        Validate the final bundle before returning or persisting it.
        """

        if not isinstance(bundle, ForecastDatasetBundle):
            raise TypeError(
                "Expected a ForecastDatasetBundle."
            )

        if not bundle.summary.validation_passed:
            raise ValueError(
                "Forecast dataset bundle validation did not pass."
            )

        if bundle.summary.source_rows <= 0:
            raise ValueError(
                "Forecast dataset source row count must be positive."
            )

        if bundle.summary.model_ready_rows <= 0:
            raise ValueError(
                "Forecast model-ready row count must be positive."
            )

        if (
            bundle.summary.source_rows
            != bundle.summary.warmup_rows_removed
            + bundle.summary.model_ready_rows
        ):
            raise ValueError(
                "Source rows do not reconcile with warm-up removal and "
                "model-ready rows."
            )

        if bundle.total_rows != bundle.summary.model_ready_rows:
            raise ValueError(
                "Forecast dataset split rows do not reconcile with the "
                "model-ready row count."
            )

        if bundle.train.row_count != bundle.summary.train_rows:
            raise ValueError(
                "Training split row count does not match the summary."
            )

        if (
            bundle.validation.row_count
            != bundle.summary.validation_rows
        ):
            raise ValueError(
                "Validation split row count does not match the summary."
            )

        if bundle.test.row_count != bundle.summary.test_rows:
            raise ValueError(
                "Test split row count does not match the summary."
            )

        if (
            bundle.metadata.source_rows
            != bundle.summary.source_rows
        ):
            raise ValueError(
                "Metadata and summary source row counts do not match."
            )

        if (
            bundle.metadata.model_ready_rows
            != bundle.summary.model_ready_rows
        ):
            raise ValueError(
                "Metadata and summary model-ready row counts do not match."
            )

        if (
            bundle.metadata.total_columns
            != bundle.summary.total_columns
        ):
            raise ValueError(
                "Metadata and summary column counts do not match."
            )

    # ========================================================
    # Dataset Statistics
    # ========================================================

    def _calculate_date_boundaries(
        self,
        dataframe: DataFrame,
    ) -> tuple[object, object]:
        """
        Calculate source dataset start and end dates.
        """

        boundaries = (
            dataframe
            .agg(
                F.min(
                    F.col(self.date_column)
                ).alias("start_date"),
                F.max(
                    F.col(self.date_column)
                ).alias("end_date"),
            )
            .collect()[0]
        )

        start_date = boundaries["start_date"]
        end_date = boundaries["end_date"]

        if start_date is None or end_date is None:
            raise ValueError(
                "Unable to determine forecast dataset date boundaries."
            )

        if start_date > end_date:
            raise ValueError(
                "Forecast dataset start date is later than its end date."
            )

        return start_date, end_date

    # ========================================================
    # Generic Validation Helpers
    # ========================================================

    @staticmethod
    def _validate_non_empty_string(
        *,
        value: object,
        name: str,
    ) -> None:
        """
        Validate a required non-empty string.
        """

        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{name} cannot be empty."
            )