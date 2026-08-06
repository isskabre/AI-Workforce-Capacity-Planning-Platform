"""
Enterprise Forecast Dataset — Temporal Splitter

Provides deterministic time-ordered preparation of forecasting datasets.

Responsibilities
----------------
- Validate the source forecasting dataset.
- Remove the initial warm-up period.
- Create train, validation, and test datasets in chronological order.
- Validate split sizes and temporal boundaries.
- Return typed DatasetSplit objects.

This module does not persist data, generate metadata, or orchestrate the
forecast dataset workflow.
"""

from __future__ import annotations

import math
from typing import Final

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, TimestampType

from src.forecast.constants import (
    ALL_DATASET_SPLIT_NAMES,
    DATE_COLUMN,
    DEFAULT_TEST_RATIO,
    DEFAULT_TRAIN_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WARMUP_DAYS,
    MINIMUM_MODEL_READY_ROWS,
    MINIMUM_TEST_ROWS,
    MINIMUM_TRAIN_ROWS,
    MINIMUM_VALIDATION_ROWS,
    SPLIT_RATIO_TOLERANCE,
    SUPPORTED_SPLIT_STRATEGIES,
    TEMPORAL_SPLIT_STRATEGY,
    TEST_DATASET_NAME,
    TRAIN_DATASET_NAME,
    VALIDATION_DATASET_NAME,
)

from src.forecast.models import DatasetSplit


# ============================================================
# Internal Constants
# ============================================================

_ROW_NUMBER_COLUMN: Final[str] = "__forecast_row_number"

_DUPLICATE_COUNT_COLUMN: Final[str] = "__forecast_duplicate_count"


# ============================================================
# Forecast Dataset Splitter
# ============================================================

class ForecastDatasetSplitter:
    """
    Prepare and split a forecasting dataset chronologically.

    The splitter intentionally supports temporal splitting only. Random and
    shuffled splits are prohibited because they would introduce time-series
    leakage between training, validation, and test datasets.
    """

    def __init__(
        self,
        *,
        date_column: str = DATE_COLUMN,
        warmup_days: int = DEFAULT_WARMUP_DAYS,
        train_ratio: float = DEFAULT_TRAIN_RATIO,
        validation_ratio: float = DEFAULT_VALIDATION_RATIO,
        test_ratio: float = DEFAULT_TEST_RATIO,
        split_strategy: str = TEMPORAL_SPLIT_STRATEGY,
    ) -> None:
        """
        Initialize the temporal splitter.

        Parameters
        ----------
        date_column:
            Column used to establish chronological ordering.

        warmup_days:
            Number of earliest ordered observations removed before splitting.

        train_ratio:
            Proportion of model-ready rows assigned to training.

        validation_ratio:
            Proportion of model-ready rows assigned to validation.

        test_ratio:
            Proportion of model-ready rows assigned to testing.

        split_strategy:
            Dataset split strategy. Only ``temporal`` is supported.
        """

        self.date_column = date_column
        self.warmup_days = warmup_days
        self.train_ratio = train_ratio
        self.validation_ratio = validation_ratio
        self.test_ratio = test_ratio
        self.split_strategy = split_strategy

        self._validate_configuration()

    # ========================================================
    # Public API
    # ========================================================

    def validate_source_dataset(self, dataframe: DataFrame) -> int:
        """
        Validate the source dataset and return its row count.

        Validation ensures that:

        - The input is a Spark DataFrame.
        - The dataset is not empty.
        - The configured date column exists.
        - The date column uses a date or timestamp data type.
        - The date column contains no null values.
        - Each date appears only once.

        Returns
        -------
        int
            Number of rows in the source dataset.

        Raises
        ------
        TypeError
            If the input is not a Spark DataFrame.

        ValueError
            If the dataset violates any forecast preparation requirement.
        """

        if dataframe is None:
            raise ValueError(
                "Forecast dataset cannot be None."
            )

        required_dataframe_attributes = (
            "columns",
            "schema",
            "filter",
            "groupBy",
            "count",
        )

        missing_dataframe_attributes = [
            attribute
            for attribute in required_dataframe_attributes
            if not hasattr(dataframe, attribute)
        ]

        if missing_dataframe_attributes:
            raise TypeError(
                "A Spark or Spark Connect DataFrame is required. "
                f"Missing required attributes: {missing_dataframe_attributes}."
            )

        if self.date_column not in dataframe.columns:
            raise ValueError(
                f"Required date column '{self.date_column}' was not found. "
                f"Available columns: {dataframe.columns}"
            )

        source_rows = dataframe.count()

        if source_rows == 0:
            raise ValueError(
                "The source forecasting dataset is empty."
            )

        date_field = dataframe.schema[self.date_column]

        if not isinstance(
            date_field.dataType,
            (DateType, TimestampType),
        ):
            raise ValueError(
                f"Date column '{self.date_column}' must use DateType or "
                f"TimestampType. Found: {date_field.dataType.simpleString()}."
            )

        null_date_rows = (
            dataframe
            .filter(F.col(self.date_column).isNull())
            .limit(1)
            .count()
        )

        if null_date_rows > 0:
            raise ValueError(
                f"Date column '{self.date_column}' contains null values."
            )

        duplicate_date = (
            dataframe
            .groupBy(self.date_column)
            .agg(
                F.count(F.lit(1)).alias(
                    _DUPLICATE_COUNT_COLUMN
                )
            )
            .filter(
                F.col(_DUPLICATE_COUNT_COLUMN) > 1
            )
            .select(self.date_column)
            .limit(1)
            .collect()
        )

        if duplicate_date:
            duplicate_value = duplicate_date[0][self.date_column]

            raise ValueError(
                f"Date column '{self.date_column}' must uniquely identify "
                f"each forecasting observation. Duplicate date found: "
                f"{duplicate_value}."
            )

        minimum_source_rows = (
            self.warmup_days
            + MINIMUM_MODEL_READY_ROWS
        )

        if source_rows < minimum_source_rows:
            raise ValueError(
                "The source forecasting dataset does not contain enough "
                "history for warm-up removal and temporal splitting. "
                f"Required at least {minimum_source_rows} rows, "
                f"but found {source_rows}."
            )

        return source_rows

    def remove_warmup(
        self,
        dataframe: DataFrame,
    ) -> tuple[DataFrame, int]:
        """
        Remove the earliest warm-up observations.

        Rows are ordered chronologically using the configured date column.
        The first ``warmup_days`` observations are excluded because lag and
        rolling-window features may not yet contain complete history.

        Parameters
        ----------
        dataframe:
            Validated source forecasting DataFrame.

        Returns
        -------
        tuple[DataFrame, int]
            Model-ready DataFrame and number of rows removed.
        """

        source_rows = self.validate_source_dataset(dataframe)

        ordering_window = Window.orderBy(
            F.col(self.date_column).asc()
        )

        indexed_dataframe = dataframe.withColumn(
            _ROW_NUMBER_COLUMN,
            F.row_number().over(ordering_window),
        )

        model_ready_dataframe = (
            indexed_dataframe
            .filter(
                F.col(_ROW_NUMBER_COLUMN) > self.warmup_days
            )
            .drop(_ROW_NUMBER_COLUMN)
            .orderBy(
                F.col(self.date_column).asc()
            )
        )

        model_ready_rows = (
            source_rows
            - self.warmup_days
        )

        if model_ready_rows < MINIMUM_MODEL_READY_ROWS:
            raise ValueError(
                "Warm-up removal left insufficient rows for temporal "
                "splitting. "
                f"Required at least {MINIMUM_MODEL_READY_ROWS} rows, "
                f"but found {model_ready_rows}."
            )

        return model_ready_dataframe, self.warmup_days

    def split(
        self,
        dataframe: DataFrame,
    ) -> tuple[DatasetSplit, DatasetSplit, DatasetSplit]:
        """
        Divide a model-ready dataset into temporal splits.

        The resulting order is always:

        ``training -> validation -> testing``

        No randomization or shuffling is performed.

        Parameters
        ----------
        dataframe:
            Model-ready forecasting DataFrame after warm-up removal.

        Returns
        -------
        tuple[DatasetSplit, DatasetSplit, DatasetSplit]
            Training, validation, and test split objects.
        """

        self._validate_model_ready_dataset(dataframe)

        model_ready_rows = dataframe.count()

        train_rows, validation_rows, test_rows = (
            self._calculate_split_sizes(
                model_ready_rows
            )
        )

        ordering_window = Window.orderBy(
            F.col(self.date_column).asc()
        )

        indexed_dataframe = dataframe.withColumn(
            _ROW_NUMBER_COLUMN,
            F.row_number().over(ordering_window),
        )

        train_end_index = train_rows

        validation_end_index = (
            train_rows
            + validation_rows
        )

        train_dataframe = (
            indexed_dataframe
            .filter(
                F.col(_ROW_NUMBER_COLUMN)
                <= train_end_index
            )
            .drop(_ROW_NUMBER_COLUMN)
            .orderBy(
                F.col(self.date_column).asc()
            )
        )

        validation_dataframe = (
            indexed_dataframe
            .filter(
                (
                    F.col(_ROW_NUMBER_COLUMN)
                    > train_end_index
                )
                & (
                    F.col(_ROW_NUMBER_COLUMN)
                    <= validation_end_index
                )
            )
            .drop(_ROW_NUMBER_COLUMN)
            .orderBy(
                F.col(self.date_column).asc()
            )
        )

        test_dataframe = (
            indexed_dataframe
            .filter(
                F.col(_ROW_NUMBER_COLUMN)
                > validation_end_index
            )
            .drop(_ROW_NUMBER_COLUMN)
            .orderBy(
                F.col(self.date_column).asc()
            )
        )

        train_split = self._build_dataset_split(
            name=TRAIN_DATASET_NAME,
            dataframe=train_dataframe,
            expected_rows=train_rows,
        )

        validation_split = self._build_dataset_split(
            name=VALIDATION_DATASET_NAME,
            dataframe=validation_dataframe,
            expected_rows=validation_rows,
        )

        test_split = self._build_dataset_split(
            name=TEST_DATASET_NAME,
            dataframe=test_dataframe,
            expected_rows=test_rows,
        )


        self.validate_splits(
            train_split=train_split,
            validation_split=validation_split,
            test_split=test_split,
            expected_total_rows=model_ready_rows,
        )

        return (
            train_split,
            validation_split,
            test_split,
        )

    def prepare_and_split(
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
        Execute source validation, warm-up removal, and temporal splitting.

        This convenience method is intended for orchestration by
        ``ForecastDatasetService``.

        Returns
        -------
        tuple
            Model-ready DataFrame, warm-up rows removed, training split,
            validation split, and test split.
        """

        model_ready_dataframe, warmup_rows_removed = (
            self.remove_warmup(dataframe)
        )

        train_split, validation_split, test_split = self.split(
            model_ready_dataframe
        )

        return (
            model_ready_dataframe,
            warmup_rows_removed,
            train_split,
            validation_split,
            test_split,
        )

    def validate_splits(
        self,
        *,
        train_split: DatasetSplit,
        validation_split: DatasetSplit,
        test_split: DatasetSplit,
        expected_total_rows: int,
    ) -> None:
        """
        Validate split identity, size, and chronological boundaries.

        Raises
        ------
        ValueError
            If any split requirement is violated.
        """

        splits = (
            train_split,
            validation_split,
            test_split,
        )

        actual_names = tuple(
            split.name
            for split in splits
        )

        if actual_names != ALL_DATASET_SPLIT_NAMES:
            raise ValueError(
                "Unexpected dataset split order. "
                f"Expected {ALL_DATASET_SPLIT_NAMES}, "
                f"but found {actual_names}."
            )

        if train_split.row_count < MINIMUM_TRAIN_ROWS:
            raise ValueError(
                "Training split contains insufficient rows. "
                f"Required at least {MINIMUM_TRAIN_ROWS}, "
                f"but found {train_split.row_count}."
            )

        if validation_split.row_count < MINIMUM_VALIDATION_ROWS:
            raise ValueError(
                "Validation split contains insufficient rows. "
                f"Required at least {MINIMUM_VALIDATION_ROWS}, "
                f"but found {validation_split.row_count}."
            )

        if test_split.row_count < MINIMUM_TEST_ROWS:
            raise ValueError(
                "Test split contains insufficient rows. "
                f"Required at least {MINIMUM_TEST_ROWS}, "
                f"but found {test_split.row_count}."
            )

        actual_total_rows = sum(
            split.row_count
            for split in splits
        )

        if actual_total_rows != expected_total_rows:
            raise ValueError(
                "Temporal split row counts do not reconcile with the "
                "model-ready dataset. "
                f"Expected {expected_total_rows}, "
                f"but found {actual_total_rows}."
            )

        self._validate_split_date_boundaries(
            train_split=train_split,
            validation_split=validation_split,
            test_split=test_split,
        )

    # ========================================================
    # Configuration Validation
    # ========================================================

    def _validate_configuration(self) -> None:
        """
        Validate splitter configuration during initialization.
        """

        if not isinstance(self.date_column, str):
            raise TypeError(
                "date_column must be a string."
            )

        if not self.date_column.strip():
            raise ValueError(
                "date_column cannot be empty."
            )

        if not isinstance(self.warmup_days, int):
            raise TypeError(
                "warmup_days must be an integer."
            )

        if self.warmup_days < 0:
            raise ValueError(
                "warmup_days cannot be negative."
            )

        if self.split_strategy not in SUPPORTED_SPLIT_STRATEGIES:
            raise ValueError(
                f"Unsupported split strategy '{self.split_strategy}'. "
                f"Supported strategies: "
                f"{SUPPORTED_SPLIT_STRATEGIES}."
            )

        ratios = {
            "train_ratio": self.train_ratio,
            "validation_ratio": self.validation_ratio,
            "test_ratio": self.test_ratio,
        }

        for ratio_name, ratio_value in ratios.items():
            if not isinstance(ratio_value, (int, float)):
                raise TypeError(
                    f"{ratio_name} must be numeric."
                )

            if ratio_value <= 0.0:
                raise ValueError(
                    f"{ratio_name} must be greater than zero."
                )

            if ratio_value >= 1.0:
                raise ValueError(
                    f"{ratio_name} must be less than one."
                )

        total_ratio = sum(ratios.values())

        if not math.isclose(
            total_ratio,
            1.0,
            abs_tol=SPLIT_RATIO_TOLERANCE,
        ):
            raise ValueError(
                "Temporal split ratios must sum to 1.0. "
                f"Found: {total_ratio}."
            )

    # ========================================================
    # Dataset Validation
    # ========================================================

    def _validate_model_ready_dataset(
        self,
        dataframe: DataFrame,
    ) -> None:
        """
        Validate a dataset after warm-up removal.
        """

        if not isinstance(dataframe, DataFrame):
            raise TypeError(
                "Model-ready dataset must be a PySpark DataFrame."
            )

        if self.date_column not in dataframe.columns:
            raise ValueError(
                f"Required date column '{self.date_column}' was not found "
                "in the model-ready dataset."
            )

        model_ready_rows = dataframe.count()

        if model_ready_rows < MINIMUM_MODEL_READY_ROWS:
            raise ValueError(
                "Model-ready dataset contains insufficient rows. "
                f"Required at least {MINIMUM_MODEL_READY_ROWS}, "
                f"but found {model_ready_rows}."
            )

        null_date_exists = (
            dataframe
            .filter(
                F.col(self.date_column).isNull()
            )
            .limit(1)
            .count()
            > 0
        )

        if null_date_exists:
            raise ValueError(
                f"Model-ready date column '{self.date_column}' contains "
                "null values."
            )

    # ========================================================
    # Split Construction
    # ========================================================

    def _calculate_split_sizes(
        self,
        total_rows: int,
    ) -> tuple[int, int, int]:
        """
        Calculate deterministic temporal split row counts.

        Training and validation sizes use floor allocation. The test split
        receives the remaining rows to guarantee exact reconciliation.
        """

        if total_rows < MINIMUM_MODEL_READY_ROWS:
            raise ValueError(
                f"At least {MINIMUM_MODEL_READY_ROWS} model-ready rows "
                "are required."
            )

        train_rows = math.floor(
            total_rows
            * self.train_ratio
        )

        validation_rows = math.floor(
            total_rows
            * self.validation_ratio
        )

        test_rows = (
            total_rows
            - train_rows
            - validation_rows
        )

        if train_rows < MINIMUM_TRAIN_ROWS:
            raise ValueError(
                "Calculated training split is too small. "
                f"Calculated {train_rows}; minimum is "
                f"{MINIMUM_TRAIN_ROWS}."
            )

        if validation_rows < MINIMUM_VALIDATION_ROWS:
            raise ValueError(
                "Calculated validation split is too small. "
                f"Calculated {validation_rows}; minimum is "
                f"{MINIMUM_VALIDATION_ROWS}."
            )

        if test_rows < MINIMUM_TEST_ROWS:
            raise ValueError(
                "Calculated test split is too small. "
                f"Calculated {test_rows}; minimum is "
                f"{MINIMUM_TEST_ROWS}."
            )

        return (
            train_rows,
            validation_rows,
            test_rows,
        )

    def _build_dataset_split(
        self,
        *,
        name: str,
        dataframe: DataFrame,
        expected_rows: int,
    ) -> DatasetSplit:
        """
        Build one typed DatasetSplit object.
        """

        if name not in ALL_DATASET_SPLIT_NAMES:
            raise ValueError(
                f"Unsupported dataset split name '{name}'."
            )

        statistics = (
            dataframe
            .agg(
                F.count(F.lit(1)).alias("row_count"),
                F.min(
                    F.col(self.date_column)
                ).alias("start_date"),
                F.max(
                    F.col(self.date_column)
                ).alias("end_date"),
            )
            .collect()[0]
        )

        actual_rows = int(
            statistics["row_count"]
        )

        if actual_rows != expected_rows:
            raise ValueError(
                f"Dataset split '{name}' contains an unexpected number "
                f"of rows. Expected {expected_rows}, "
                f"but found {actual_rows}."
            )

        return DatasetSplit(
            name=name,
            dataframe=dataframe,
            row_count=actual_rows,
            start_date=statistics["start_date"],
            end_date=statistics["end_date"],
        )

    # ========================================================
    # Temporal Boundary Validation
    # ========================================================

    @staticmethod
    def _validate_split_date_boundaries(
        *,
        train_split: DatasetSplit,
        validation_split: DatasetSplit,
        test_split: DatasetSplit,
    ) -> None:
        """
        Confirm strict chronological separation among all splits.
        """

        boundaries = (
            train_split.start_date,
            train_split.end_date,
            validation_split.start_date,
            validation_split.end_date,
            test_split.start_date,
            test_split.end_date,
        )

        if any(
            boundary is None
            for boundary in boundaries
        ):
            raise ValueError(
                "Every temporal split must contain valid start and end "
                "dates."
            )

        if train_split.start_date > train_split.end_date:
            raise ValueError(
                "Training split has invalid date boundaries."
            )

        if validation_split.start_date > validation_split.end_date:
            raise ValueError(
                "Validation split has invalid date boundaries."
            )

        if test_split.start_date > test_split.end_date:
            raise ValueError(
                "Test split has invalid date boundaries."
            )

        if train_split.end_date >= validation_split.start_date:
            raise ValueError(
                "Training and validation date ranges overlap or are not "
                "strictly chronological."
            )

        if validation_split.end_date >= test_split.start_date:
            raise ValueError(
                "Validation and test date ranges overlap or are not "
                "strictly chronological."
            )