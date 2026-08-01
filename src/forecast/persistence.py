"""
Enterprise Forecast Dataset — Persistence Layer

Provides version-aware persistence for forecast dataset splits, metadata,
execution summaries, and manifests.

Responsibilities
----------------
- Build deterministic versioned storage paths.
- Persist train, validation, and test Spark DataFrames.
- Persist dataset metadata and operational summaries.
- Persist a machine-readable dataset manifest.
- Return a typed ForecastPersistenceResult.

This module does not prepare features, remove warm-up rows, split datasets,
or orchestrate the complete forecast dataset workflow.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Final

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from forecast.constants import (
    DEFAULT_COMPRESSION_CODEC,
    DEFAULT_STORAGE_FORMAT,
    DEFAULT_WRITE_MODE,
    FORECAST_DATASET_VERSION_PREFIX,
    MANIFEST_FILE_NAME,
    MANIFEST_FOLDER,
    METADATA_FILE_NAME,
    METADATA_FOLDER,
    SUMMARY_FILE_NAME,
    SUMMARY_FOLDER,
    TEST_FOLDER,
    TRAIN_FOLDER,
    VALIDATION_FOLDER,
)
from forecast.models import (
    ForecastDatasetBundle,
    ForecastPersistenceResult,
)


# ============================================================
# Internal Constants
# ============================================================

_MANIFEST_CONTENT_COLUMN: Final[str] = "value"

_SUPPORTED_STORAGE_FORMATS: Final[tuple[str, ...]] = (
    "parquet",
    "delta",
)

_SUPPORTED_WRITE_MODES: Final[tuple[str, ...]] = (
    "append",
    "error",
    "errorifexists",
    "ignore",
    "overwrite",
)


# ============================================================
# Forecast Dataset Persistence
# ============================================================

class ForecastDatasetPersistence:
    """
    Persist a versioned enterprise forecast dataset.

    The persistence layer writes each temporal split independently and stores
    metadata, summary, and manifest artifacts under the same immutable dataset
    version root.

    Expected layout
    ---------------
    forecasts/
        v1.0.0/
            train/
            validation/
            test/
            metadata/
                forecast_dataset_metadata/
            summary/
                forecast_dataset_summary/
            manifest/
                forecast_dataset_manifest/
    """

    def __init__(
        self,
        *,
        spark: SparkSession,
        root_path: str,
        storage_format: str = DEFAULT_STORAGE_FORMAT,
        write_mode: str = DEFAULT_WRITE_MODE,
        compression_codec: str = DEFAULT_COMPRESSION_CODEC,
    ) -> None:
        """
        Initialize the forecast dataset persistence layer.

        Parameters
        ----------
        spark:
            Active SparkSession.

        root_path:
            Base storage path under which versioned forecast datasets are
            persisted.

            Example:

            ``s3://bucket/project/forecasts``

        storage_format:
            Spark storage format used for train, validation, test, metadata,
            and summary outputs.

        write_mode:
            Spark write mode.

        compression_codec:
            Compression codec used when supported by the selected format.
        """

        self.spark = spark
        self.root_path = self._normalize_path(root_path)
        self.storage_format = storage_format.lower().strip()
        self.write_mode = write_mode.lower().strip()
        self.compression_codec = compression_codec.strip()

        self._validate_configuration()

    # ========================================================
    # Public API
    # ========================================================

    def persist_bundle(
        self,
        bundle: ForecastDatasetBundle,
    ) -> ForecastPersistenceResult:
        """
        Persist a complete ForecastDatasetBundle.

        Parameters
        ----------
        bundle:
            Forecast dataset bundle containing train, validation, and test
            splits together with metadata and an execution summary.

        Returns
        -------
        ForecastPersistenceResult
            Paths and persistence settings associated with the completed
            write operation.
        """

        self._validate_bundle(bundle)

        persisted_at_utc = datetime.now(timezone.utc)

        dataset_root_path = self.build_dataset_root_path(
            bundle.metadata.dataset_version
        )

        train_path = self._join_path(
            dataset_root_path,
            TRAIN_FOLDER,
        )

        validation_path = self._join_path(
            dataset_root_path,
            VALIDATION_FOLDER,
        )

        test_path = self._join_path(
            dataset_root_path,
            TEST_FOLDER,
        )

        metadata_path = self._join_path(
            dataset_root_path,
            METADATA_FOLDER,
            METADATA_FILE_NAME,
        )

        summary_path = self._join_path(
            dataset_root_path,
            SUMMARY_FOLDER,
            SUMMARY_FILE_NAME,
        )

        manifest_path = self._join_path(
            dataset_root_path,
            MANIFEST_FOLDER,
            MANIFEST_FILE_NAME,
        )

        self.save_train_dataset(
            dataframe=bundle.train_df,
            path=train_path,
        )

        self.save_validation_dataset(
            dataframe=bundle.validation_df,
            path=validation_path,
        )

        self.save_test_dataset(
            dataframe=bundle.test_df,
            path=test_path,
        )

        self.save_metadata(
            metadata=bundle.as_metadata_dict(),
            path=metadata_path,
        )

        self.save_summary(
            summary=bundle.as_summary_dict(),
            path=summary_path,
        )

        manifest = self._build_manifest(
            bundle=bundle,
            dataset_root_path=dataset_root_path,
            train_path=train_path,
            validation_path=validation_path,
            test_path=test_path,
            metadata_path=metadata_path,
            summary_path=summary_path,
            manifest_path=manifest_path,
            persisted_at_utc=persisted_at_utc,
        )

        self.save_manifest(
            manifest=manifest,
            path=manifest_path,
        )

        return ForecastPersistenceResult(
            dataset_root_path=dataset_root_path,
            train_path=train_path,
            validation_path=validation_path,
            test_path=test_path,
            metadata_path=metadata_path,
            summary_path=summary_path,
            manifest_path=manifest_path,
            storage_format=self.storage_format,
            write_mode=self.write_mode,
            persisted_at_utc=persisted_at_utc,
        )

    def save_train_dataset(
        self,
        *,
        dataframe: DataFrame,
        path: str,
    ) -> None:
        """
        Persist the training dataset.
        """

        self._write_dataframe(
            dataframe=dataframe,
            path=path,
        )

    def save_validation_dataset(
        self,
        *,
        dataframe: DataFrame,
        path: str,
    ) -> None:
        """
        Persist the validation dataset.
        """

        self._write_dataframe(
            dataframe=dataframe,
            path=path,
        )

    def save_test_dataset(
        self,
        *,
        dataframe: DataFrame,
        path: str,
    ) -> None:
        """
        Persist the test dataset.
        """

        self._write_dataframe(
            dataframe=dataframe,
            path=path,
        )

    def save_metadata(
        self,
        *,
        metadata: dict[str, Any],
        path: str,
    ) -> None:
        """
        Persist forecast dataset metadata as a single-row Spark dataset.
        """

        self._validate_serializable_mapping(
            value=metadata,
            name="metadata",
        )

        metadata_dataframe = self.spark.createDataFrame(
            [metadata]
        )

        self._write_dataframe(
            dataframe=metadata_dataframe,
            path=path,
        )

    def save_summary(
        self,
        *,
        summary: dict[str, Any],
        path: str,
    ) -> None:
        """
        Persist the forecast dataset execution summary as a single row.
        """

        self._validate_serializable_mapping(
            value=summary,
            name="summary",
        )

        summary_dataframe = self.spark.createDataFrame(
            [summary]
        )

        self._write_dataframe(
            dataframe=summary_dataframe,
            path=path,
        )

    def save_manifest(
        self,
        *,
        manifest: dict[str, Any],
        path: str,
    ) -> None:
        """
        Persist the dataset manifest as formatted JSON text.

        Spark writes the JSON document into the configured manifest directory.
        The output is intentionally stored as text so external orchestration
        systems can read the manifest without requiring Spark schema inference.
        """

        self._validate_serializable_mapping(
            value=manifest,
            name="manifest",
        )

        manifest_json = json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            default=self._json_default,
        )

        manifest_dataframe = self.spark.createDataFrame(
            [(manifest_json,)],
            schema=[_MANIFEST_CONTENT_COLUMN],
        )

        (
            manifest_dataframe
            .coalesce(1)
            .write
            .mode(self.write_mode)
            .text(path)
        )

    def build_dataset_root_path(
        self,
        dataset_version: str,
    ) -> str:
        """
        Build the immutable versioned dataset root path.

        Example
        -------
        ``s3://bucket/project/forecasts/v1.0.0``
        """

        normalized_version = self._normalize_version(
            dataset_version
        )

        return self._join_path(
            self.root_path,
            normalized_version,
        )

    # ========================================================
    # DataFrame Persistence
    # ========================================================

    def _write_dataframe(
        self,
        *,
        dataframe: DataFrame,
        path: str,
    ) -> None:
        """
        Write one Spark DataFrame using the configured persistence settings.
        """

        if dataframe is None:
            raise ValueError(
                "Forecast persistence requires a DataFrame."
            )

        required_dataframe_attributes = (
            "columns",
            "write",
        )

        missing_dataframe_attributes = [
            attribute
            for attribute in required_dataframe_attributes
            if not hasattr(dataframe, attribute)
        ]

        if missing_dataframe_attributes:
            raise TypeError(
                "Forecast persistence requires a Spark or Spark Connect DataFrame. "
                f"Missing required attributes: {missing_dataframe_attributes}."
            )

        if not dataframe.columns:
            raise ValueError(
                "Forecast persistence cannot write a DataFrame with no "
                "columns."
            )

        normalized_path = self._normalize_path(path)

        writer = (
            dataframe
            .write
            .format(self.storage_format)
            .mode(self.write_mode)
        )

        if self.storage_format == "parquet":
            writer = writer.option(
                "compression",
                self.compression_codec,
            )

        writer.save(normalized_path)

    # ========================================================
    # Manifest Construction
    # ========================================================

    def _build_manifest(
        self,
        *,
        bundle: ForecastDatasetBundle,
        dataset_root_path: str,
        train_path: str,
        validation_path: str,
        test_path: str,
        metadata_path: str,
        summary_path: str,
        manifest_path: str,
        persisted_at_utc: datetime,
    ) -> dict[str, Any]:
        """
        Build the machine-readable dataset manifest.
        """

        return {
            "dataset": {
                "name": bundle.metadata.dataset_name,
                "version": bundle.metadata.dataset_version,
                "root_path": dataset_root_path,
                "storage_format": self.storage_format,
                "write_mode": self.write_mode,
                "compression_codec": self.compression_codec,
            },
            "forecast_configuration": {
                "target_column": bundle.metadata.target_column,
                "date_column": bundle.metadata.date_column,
                "forecast_horizon": bundle.metadata.forecast_horizon,
                "warmup_days": bundle.metadata.warmup_days,
                "split_strategy": bundle.metadata.split_strategy,
                "train_ratio": bundle.metadata.train_ratio,
                "validation_ratio": (
                    bundle.metadata.validation_ratio
                ),
                "test_ratio": bundle.metadata.test_ratio,
            },
            "row_counts": {
                "source_rows": bundle.summary.source_rows,
                "warmup_rows_removed": (
                    bundle.summary.warmup_rows_removed
                ),
                "model_ready_rows": (
                    bundle.summary.model_ready_rows
                ),
                "train_rows": bundle.train.row_count,
                "validation_rows": bundle.validation.row_count,
                "test_rows": bundle.test.row_count,
                "total_persisted_rows": bundle.total_rows,
            },
            "date_boundaries": {
                "dataset_start_date": self._to_iso(
                    bundle.metadata.start_date
                ),
                "dataset_end_date": self._to_iso(
                    bundle.metadata.end_date
                ),
                "train_start_date": self._to_iso(
                    bundle.train.start_date
                ),
                "train_end_date": self._to_iso(
                    bundle.train.end_date
                ),
                "validation_start_date": self._to_iso(
                    bundle.validation.start_date
                ),
                "validation_end_date": self._to_iso(
                    bundle.validation.end_date
                ),
                "test_start_date": self._to_iso(
                    bundle.test.start_date
                ),
                "test_end_date": self._to_iso(
                    bundle.test.end_date
                ),
            },
            "artifacts": {
                "train_path": train_path,
                "validation_path": validation_path,
                "test_path": test_path,
                "metadata_path": metadata_path,
                "summary_path": summary_path,
                "manifest_path": manifest_path,
            },
            "quality": {
                "validation_passed": (
                    bundle.summary.validation_passed
                ),
                "status": bundle.summary.status,
            },
            "generated_at_utc": (
                bundle.metadata.generated_at_utc.isoformat()
            ),
            "persisted_at_utc": persisted_at_utc.isoformat(),
        }

    # ========================================================
    # Validation
    # ========================================================

    def _validate_configuration(self) -> None:
        """
        Validate persistence configuration.
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

        if not self.root_path:
            raise ValueError(
                "root_path cannot be empty."
            )

        if self.storage_format not in _SUPPORTED_STORAGE_FORMATS:
            raise ValueError(
                f"Unsupported storage format '{self.storage_format}'. "
                f"Supported formats: {_SUPPORTED_STORAGE_FORMATS}."
            )

        if self.write_mode not in _SUPPORTED_WRITE_MODES:
            raise ValueError(
                f"Unsupported write mode '{self.write_mode}'. "
                f"Supported modes: {_SUPPORTED_WRITE_MODES}."
            )

        if not self.compression_codec:
            raise ValueError(
                "compression_codec cannot be empty."
            )

    @staticmethod
    def _validate_bundle(
        bundle: ForecastDatasetBundle,
    ) -> None:
        """
        Validate the forecast dataset bundle before persistence.
        """

        if not isinstance(bundle, ForecastDatasetBundle):
            raise TypeError(
                "persist_bundle requires a ForecastDatasetBundle."
            )

        if not bundle.summary.validation_passed:
            raise ValueError(
                "The forecast dataset bundle cannot be persisted because "
                "validation_passed is False."
            )

        if bundle.total_rows != bundle.summary.model_ready_rows:
            raise ValueError(
                "Forecast bundle split row counts do not reconcile with "
                "the model-ready row count."
            )

        if bundle.train.row_count != bundle.summary.train_rows:
            raise ValueError(
                "Training split row count does not match the forecast "
                "dataset summary."
            )

        if (
            bundle.validation.row_count
            != bundle.summary.validation_rows
        ):
            raise ValueError(
                "Validation split row count does not match the forecast "
                "dataset summary."
            )

        if bundle.test.row_count != bundle.summary.test_rows:
            raise ValueError(
                "Test split row count does not match the forecast dataset "
                "summary."
            )

    @staticmethod
    def _validate_serializable_mapping(
        *,
        value: dict[str, Any],
        name: str,
    ) -> None:
        """
        Validate a dictionary intended for persistence.
        """

        if not isinstance(value, dict):
            raise TypeError(
                f"{name} must be a dictionary."
            )

        if not value:
            raise ValueError(
                f"{name} cannot be empty."
            )

        try:
            json.dumps(
                value,
                default=ForecastDatasetPersistence._json_default,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{name} contains values that cannot be serialized."
            ) from error

    # ========================================================
    # Path Helpers
    # ========================================================

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize a storage path without altering its URI scheme.
        """

        if not isinstance(path, str):
            raise TypeError(
                "Storage paths must be strings."
            )

        normalized_path = path.strip().rstrip("/")

        if not normalized_path:
            raise ValueError(
                "Storage path cannot be empty."
            )

        return normalized_path

    @staticmethod
    def _join_path(
        *parts: str,
    ) -> str:
        """
        Join URI or filesystem path components using forward slashes.
        """

        cleaned_parts = [
            str(part).strip().strip("/")
            for part in parts
            if str(part).strip()
        ]

        if not cleaned_parts:
            raise ValueError(
                "At least one path component is required."
            )

        first_part = str(parts[0]).strip().rstrip("/")

        remaining_parts = [
            str(part).strip().strip("/")
            for part in parts[1:]
            if str(part).strip()
        ]

        if not remaining_parts:
            return first_part

        return "/".join(
            [first_part, *remaining_parts]
        )

    @staticmethod
    def _normalize_version(
        dataset_version: str,
    ) -> str:
        """
        Normalize a semantic dataset version to its storage folder name.
        """

        if not isinstance(dataset_version, str):
            raise TypeError(
                "dataset_version must be a string."
            )

        normalized_version = dataset_version.strip()

        if not normalized_version:
            raise ValueError(
                "dataset_version cannot be empty."
            )

        if normalized_version.startswith(
            FORECAST_DATASET_VERSION_PREFIX
        ):
            return normalized_version

        return (
            f"{FORECAST_DATASET_VERSION_PREFIX}"
            f"{normalized_version}"
        )

    # ========================================================
    # Serialization Helpers
    # ========================================================

    @staticmethod
    def _to_iso(
        value: Any,
    ) -> str | None:
        """
        Convert date-like values to ISO-8601 strings.
        """

        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return str(value)

    @staticmethod
    def _json_default(
        value: Any,
    ) -> Any:
        """
        Serialize date, datetime, and other compatible objects to JSON.
        """

        if hasattr(value, "isoformat"):
            return value.isoformat()

        if isinstance(value, set):
            return sorted(value)

        raise TypeError(
            f"Object of type {type(value).__name__} "
            "is not JSON serializable."
        )