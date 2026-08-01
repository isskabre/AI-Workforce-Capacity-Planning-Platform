"""
Enterprise Forecast Dataset — Data Models

Typed contracts used throughout forecast dataset preparation, temporal
splitting, metadata generation, persistence, and downstream model training.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

from pyspark.sql import DataFrame


# ============================================================
# Dataset Split
# ============================================================

@dataclass(slots=True)
class DatasetSplit:
    """
    Represents one temporal dataset split.

    Attributes
    ----------
    name:
        Canonical split name such as train, validation, or test.

    dataframe:
        Spark DataFrame containing the split records.

    row_count:
        Number of records in the split.

    start_date:
        Earliest date included in the split.

    end_date:
        Latest date included in the split.
    """

    name: str

    dataframe: DataFrame

    row_count: int

    start_date: Optional[date]

    end_date: Optional[date]


# ============================================================
# Forecast Dataset Metadata
# ============================================================

@dataclass(slots=True)
class ForecastDatasetMetadata:
    """
    Describes one generated forecast dataset version.

    This object captures the configuration, lineage, date coverage, split
    boundaries, and output schema required for reproducibility.
    """

    dataset_name: str

    dataset_version: str

    target_column: str

    date_column: str

    forecast_horizon: int

    warmup_days: int

    split_strategy: str

    train_ratio: float

    validation_ratio: float

    test_ratio: float

    source_rows: int

    warmup_rows_removed: int

    model_ready_rows: int

    total_columns: int

    start_date: Optional[date]

    end_date: Optional[date]

    train_start_date: Optional[date]

    train_end_date: Optional[date]

    validation_start_date: Optional[date]

    validation_end_date: Optional[date]

    test_start_date: Optional[date]

    test_end_date: Optional[date]

    generated_at_utc: datetime


# ============================================================
# Forecast Dataset Summary
# ============================================================

@dataclass(slots=True)
class ForecastDatasetSummary:
    """
    Operational summary of forecast dataset preparation.

    Attributes
    ----------
    source_rows:
        Number of rows received from the Demand Intelligence Engine.

    warmup_rows_removed:
        Number of initial rows removed because historical lag and rolling
        features were incomplete.

    model_ready_rows:
        Number of rows remaining after warm-up removal.

    train_rows:
        Number of records assigned to the training split.

    validation_rows:
        Number of records assigned to the validation split.

    test_rows:
        Number of records assigned to the test split.

    total_columns:
        Number of columns in the model-ready dataset.

    validation_passed:
        Whether all forecast dataset quality checks passed.

    status:
        Final lifecycle status of the dataset build.
    """

    source_rows: int

    warmup_rows_removed: int

    model_ready_rows: int

    train_rows: int

    validation_rows: int

    test_rows: int

    total_columns: int

    validation_passed: bool

    status: str


# ============================================================
# Forecast Persistence Result
# ============================================================

@dataclass(slots=True)
class ForecastPersistenceResult:
    """
    Paths created by the forecast dataset persistence layer.
    """

    dataset_root_path: str

    train_path: str

    validation_path: str

    test_path: str

    metadata_path: str

    summary_path: str

    manifest_path: str

    storage_format: str

    write_mode: str

    persisted_at_utc: datetime


# ============================================================
# Forecast Dataset Bundle
# ============================================================

@dataclass(slots=True)
class ForecastDatasetBundle:
    """
    Standard output of ForecastDatasetService.

    The bundle carries the three temporal splits together with their metadata,
    operational summary, and optional persistence result.
    """

    train: DatasetSplit

    validation: DatasetSplit

    test: DatasetSplit

    metadata: ForecastDatasetMetadata

    summary: ForecastDatasetSummary

    persistence: Optional[ForecastPersistenceResult] = None

    @property
    def train_df(self) -> DataFrame:
        """
        Return the training Spark DataFrame.
        """

        return self.train.dataframe

    @property
    def validation_df(self) -> DataFrame:
        """
        Return the validation Spark DataFrame.
        """

        return self.validation.dataframe

    @property
    def test_df(self) -> DataFrame:
        """
        Return the test Spark DataFrame.
        """

        return self.test.dataframe

    @property
    def total_rows(self) -> int:
        """
        Return the combined row count across all splits.
        """

        return (
            self.train.row_count
            + self.validation.row_count
            + self.test.row_count
        )

    def as_metadata_dict(self) -> dict[str, Any]:
        """
        Return metadata as a serializable dictionary.

        Date and datetime values are converted to ISO-8601 strings so the
        result can be written to JSON, Parquet metadata tables, or manifests.
        """

        return {
            "dataset_name": self.metadata.dataset_name,
            "dataset_version": self.metadata.dataset_version,
            "target_column": self.metadata.target_column,
            "date_column": self.metadata.date_column,
            "forecast_horizon": self.metadata.forecast_horizon,
            "warmup_days": self.metadata.warmup_days,
            "split_strategy": self.metadata.split_strategy,
            "train_ratio": self.metadata.train_ratio,
            "validation_ratio": self.metadata.validation_ratio,
            "test_ratio": self.metadata.test_ratio,
            "source_rows": self.metadata.source_rows,
            "warmup_rows_removed": self.metadata.warmup_rows_removed,
            "model_ready_rows": self.metadata.model_ready_rows,
            "total_columns": self.metadata.total_columns,
            "start_date": _date_to_iso(self.metadata.start_date),
            "end_date": _date_to_iso(self.metadata.end_date),
            "train_start_date": _date_to_iso(
                self.metadata.train_start_date
            ),
            "train_end_date": _date_to_iso(
                self.metadata.train_end_date
            ),
            "validation_start_date": _date_to_iso(
                self.metadata.validation_start_date
            ),
            "validation_end_date": _date_to_iso(
                self.metadata.validation_end_date
            ),
            "test_start_date": _date_to_iso(
                self.metadata.test_start_date
            ),
            "test_end_date": _date_to_iso(
                self.metadata.test_end_date
            ),
            "generated_at_utc": (
                self.metadata.generated_at_utc.isoformat()
            ),
        }

    def as_summary_dict(self) -> dict[str, Any]:
        """
        Return the operational summary as a serializable dictionary.
        """

        return {
            "source_rows": self.summary.source_rows,
            "warmup_rows_removed": (
                self.summary.warmup_rows_removed
            ),
            "model_ready_rows": self.summary.model_ready_rows,
            "train_rows": self.summary.train_rows,
            "validation_rows": self.summary.validation_rows,
            "test_rows": self.summary.test_rows,
            "total_columns": self.summary.total_columns,
            "validation_passed": self.summary.validation_passed,
            "status": self.summary.status,
        }


# ============================================================
# Serialization Helpers
# ============================================================

def _date_to_iso(value: Optional[date]) -> Optional[str]:
    """
    Convert an optional date value to ISO-8601 format.
    """

    if value is None:
        return None

    return value.isoformat()