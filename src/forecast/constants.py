"""
Enterprise Forecast Dataset — Constants

Centralized immutable configuration for forecast dataset preparation,
temporal splitting, versioning, persistence, and metadata generation.

This module contains no Spark logic, functions, or business processing.
"""

from typing import Final


# ============================================================
# Dataset Identity and Versioning
# ============================================================

FORECAST_DATASET_NAME: Final[str] = "enterprise_forecast_dataset"

FORECAST_DATASET_VERSION: Final[str] = "1.0.0"

FORECAST_DATASET_VERSION_PREFIX: Final[str] = "v"


# ============================================================
# Forecast Configuration
# ============================================================

DEFAULT_FORECAST_HORIZON: Final[int] = 14

DEFAULT_WARMUP_DAYS: Final[int] = 90


# ============================================================
# Temporal Split Ratios
# ============================================================

DEFAULT_TRAIN_RATIO: Final[float] = 0.70

DEFAULT_VALIDATION_RATIO: Final[float] = 0.15

DEFAULT_TEST_RATIO: Final[float] = 0.15

TOTAL_SPLIT_RATIO: Final[float] = (
    DEFAULT_TRAIN_RATIO
    + DEFAULT_VALIDATION_RATIO
    + DEFAULT_TEST_RATIO
)

SPLIT_RATIO_TOLERANCE: Final[float] = 1e-9


# ============================================================
# Split Strategies
# ============================================================

TEMPORAL_SPLIT_STRATEGY: Final[str] = "temporal"

SUPPORTED_SPLIT_STRATEGIES: Final[tuple[str, ...]] = (
    TEMPORAL_SPLIT_STRATEGY,
)


# ============================================================
# Dataset Split Names
# ============================================================

TRAIN_DATASET_NAME: Final[str] = "train"

VALIDATION_DATASET_NAME: Final[str] = "validation"

TEST_DATASET_NAME: Final[str] = "test"

ALL_DATASET_SPLIT_NAMES: Final[tuple[str, ...]] = (
    TRAIN_DATASET_NAME,
    VALIDATION_DATASET_NAME,
    TEST_DATASET_NAME,
)


# ============================================================
# Persistence Folder Names
# ============================================================

TRAIN_FOLDER: Final[str] = "train"

VALIDATION_FOLDER: Final[str] = "validation"

TEST_FOLDER: Final[str] = "test"

METADATA_FOLDER: Final[str] = "metadata"

SUMMARY_FOLDER: Final[str] = "summary"

MANIFEST_FOLDER: Final[str] = "manifest"


# ============================================================
# Persistence File Names
# ============================================================

METADATA_FILE_NAME: Final[str] = "forecast_dataset_metadata"

SUMMARY_FILE_NAME: Final[str] = "forecast_dataset_summary"

MANIFEST_FILE_NAME: Final[str] = "forecast_dataset_manifest"


# ============================================================
# Persistence Configuration
# ============================================================

DEFAULT_STORAGE_FORMAT: Final[str] = "parquet"

DEFAULT_WRITE_MODE: Final[str] = "overwrite"

DEFAULT_COMPRESSION_CODEC: Final[str] = "snappy"


# ============================================================
# Canonical Dataset Columns
# ============================================================

DATE_COLUMN: Final[str] = "order_date"

DATASET_SPLIT_COLUMN: Final[str] = "_dataset_split"

DATASET_VERSION_COLUMN: Final[str] = "_forecast_dataset_version"

FORECAST_HORIZON_COLUMN: Final[str] = "_forecast_horizon"

SPLIT_STRATEGY_COLUMN: Final[str] = "_split_strategy"

GENERATED_AT_COLUMN: Final[str] = "_forecast_dataset_generated_at_utc"


# ============================================================
# Dataset Metadata Keys
# ============================================================

DATASET_NAME_KEY: Final[str] = "dataset_name"

DATASET_VERSION_KEY: Final[str] = "dataset_version"

TARGET_COLUMN_KEY: Final[str] = "target_column"

DATE_COLUMN_KEY: Final[str] = "date_column"

FORECAST_HORIZON_KEY: Final[str] = "forecast_horizon"

WARMUP_DAYS_KEY: Final[str] = "warmup_days"

SPLIT_STRATEGY_KEY: Final[str] = "split_strategy"

TRAIN_RATIO_KEY: Final[str] = "train_ratio"

VALIDATION_RATIO_KEY: Final[str] = "validation_ratio"

TEST_RATIO_KEY: Final[str] = "test_ratio"

SOURCE_ROWS_KEY: Final[str] = "source_rows"

WARMUP_ROWS_REMOVED_KEY: Final[str] = "warmup_rows_removed"

MODEL_READY_ROWS_KEY: Final[str] = "model_ready_rows"

TRAIN_ROWS_KEY: Final[str] = "train_rows"

VALIDATION_ROWS_KEY: Final[str] = "validation_rows"

TEST_ROWS_KEY: Final[str] = "test_rows"

TOTAL_ROWS_KEY: Final[str] = "total_rows"

TOTAL_COLUMNS_KEY: Final[str] = "total_columns"

START_DATE_KEY: Final[str] = "start_date"

END_DATE_KEY: Final[str] = "end_date"

TRAIN_START_DATE_KEY: Final[str] = "train_start_date"

TRAIN_END_DATE_KEY: Final[str] = "train_end_date"

VALIDATION_START_DATE_KEY: Final[str] = "validation_start_date"

VALIDATION_END_DATE_KEY: Final[str] = "validation_end_date"

TEST_START_DATE_KEY: Final[str] = "test_start_date"

TEST_END_DATE_KEY: Final[str] = "test_end_date"

GENERATED_AT_KEY: Final[str] = "generated_at_utc"

VALIDATION_PASSED_KEY: Final[str] = "validation_passed"

STATUS_KEY: Final[str] = "status"


# ============================================================
# Dataset Status Values
# ============================================================

STATUS_CREATED: Final[str] = "CREATED"

STATUS_VALIDATED: Final[str] = "VALIDATED"

STATUS_PERSISTED: Final[str] = "PERSISTED"

STATUS_COMPLETED: Final[str] = "COMPLETED"

STATUS_FAILED: Final[str] = "FAILED"


# ============================================================
# Minimum Dataset Requirements
# ============================================================

MINIMUM_TRAIN_ROWS: Final[int] = 30

MINIMUM_VALIDATION_ROWS: Final[int] = 7

MINIMUM_TEST_ROWS: Final[int] = 7

MINIMUM_MODEL_READY_ROWS: Final[int] = (
    MINIMUM_TRAIN_ROWS
    + MINIMUM_VALIDATION_ROWS
    + MINIMUM_TEST_ROWS
)