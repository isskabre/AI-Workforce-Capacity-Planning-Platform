"""
Enterprise metadata catalog persistence and discovery.

This module manages dataset-level metadata catalog entries. It does not
profile datasets, generate fingerprints, or orchestrate pipeline workflows.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Sequence

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from src.metadata.exceptions import (
    CatalogEntryAlreadyExistsError,
    CatalogEntryNotFoundError,
    CatalogPersistenceError,
    CatalogValidationError,
)
from src.metadata.models import MetadataCatalogEntry


class MetadataCatalog:
    """
    Parquet-backed enterprise metadata catalog.

    The catalog maintains one current record per dataset key and provides
    registration, retrieval, update, listing, and filtered discovery.
    """

    _CATALOG_SCHEMA = StructType(
        [
            StructField("dataset_name", StringType(), nullable=False),
            StructField("dataset_key", StringType(), nullable=False),
            StructField("layer", StringType(), nullable=False),
            StructField("storage_path", StringType(), nullable=False),
            StructField("storage_format", StringType(), nullable=False),
            StructField("row_count", LongType(), nullable=False),
            StructField("column_count", LongType(), nullable=False),
            StructField("schema_hash", StringType(), nullable=False),
            StructField("metadata_hash", StringType(), nullable=False),
            StructField("fingerprint_version", StringType(), nullable=False),
            StructField(
                "null_cell_percentage",
                DoubleType(),
                nullable=False,
            ),
            StructField(
                "duplicate_row_percentage",
                DoubleType(),
                nullable=False,
            ),
            StructField("quality_status", StringType(), nullable=False),
            StructField("quality_score", DoubleType(), nullable=True),
            StructField("owner", StringType(), nullable=False),
            StructField(
                "business_description",
                StringType(),
                nullable=False,
            ),
            StructField("execution_id", StringType(), nullable=False),
            StructField("pipeline_name", StringType(), nullable=False),
            StructField("pipeline_version", StringType(), nullable=False),
            StructField(
                "profiled_at_utc",
                TimestampType(),
                nullable=False,
            ),
        ]
    )

    def __init__(
        self,
        spark: SparkSession,
        catalog_path: str,
    ) -> None:
        self._spark = spark
        self._catalog_path = self._validate_catalog_path(catalog_path)

    @property
    def catalog_path(self) -> str:
        """Return the configured catalog persistence path."""

        return self._catalog_path

    def register(
        self,
        entry: MetadataCatalogEntry,
        *,
        overwrite: bool = False,
    ) -> MetadataCatalogEntry:
        """
        Register a new catalog entry.

        When overwrite is False, duplicate dataset keys are rejected.
        When overwrite is True, the existing current record is replaced.
        """

        self._validate_entry(entry)

        if self.exists(entry.dataset_key):
            if not overwrite:
                raise CatalogEntryAlreadyExistsError(
                    "Catalog entry already exists for dataset key "
                    f"'{entry.dataset_key}'."
                )

            return self.update(entry)

        current_entries = self.list_entries()
        self._persist_entries([*current_entries, entry])

        return entry

    def update(
        self,
        entry: MetadataCatalogEntry,
    ) -> MetadataCatalogEntry:
        """Replace the current catalog entry for an existing dataset key."""

        self._validate_entry(entry)

        current_entries = self.list_entries()

        if not any(
            current.dataset_key == entry.dataset_key
            for current in current_entries
        ):
            raise CatalogEntryNotFoundError(
                "Cannot update missing catalog entry for dataset key "
                f"'{entry.dataset_key}'."
            )

        updated_entries = [
            entry
            if current.dataset_key == entry.dataset_key
            else current
            for current in current_entries
        ]

        self._persist_entries(updated_entries)

        return entry

    def upsert(
        self,
        entry: MetadataCatalogEntry,
    ) -> MetadataCatalogEntry:
        """Insert a new catalog entry or replace the existing entry."""

        self._validate_entry(entry)

        if self.exists(entry.dataset_key):
            return self.update(entry)

        return self.register(entry)

    def exists(self, dataset_key: str) -> bool:
        """Return whether a current catalog entry exists."""

        normalized_key = self._validate_dataset_key(dataset_key)

        return any(
            entry.dataset_key == normalized_key
            for entry in self.list_entries()
        )

    def get(self, dataset_key: str) -> MetadataCatalogEntry:
        """Return one catalog entry by dataset key."""

        normalized_key = self._validate_dataset_key(dataset_key)

        for entry in self.list_entries():
            if entry.dataset_key == normalized_key:
                return entry

        raise CatalogEntryNotFoundError(
            "Catalog entry not found for dataset key "
            f"'{normalized_key}'."
        )

    def list_entries(self) -> List[MetadataCatalogEntry]:
        """Return all current catalog entries in deterministic order."""

        if not self._catalog_exists():
            return []

        try:
            dataframe = self._spark.read.schema(
                self._CATALOG_SCHEMA
            ).parquet(self._catalog_path)

            rows = dataframe.orderBy(
                F.col("dataset_key").asc()
            ).collect()

            return [
                self._row_to_entry(row.asDict(recursive=True))
                for row in rows
            ]

        except Exception as exc:
            raise CatalogPersistenceError(
                "Unable to load metadata catalog from "
                f"'{self._catalog_path}'."
            ) from exc

    def search(
        self,
        *,
        dataset_name: Optional[str] = None,
        dataset_key: Optional[str] = None,
        layer: Optional[str] = None,
        owner: Optional[str] = None,
        storage_format: Optional[str] = None,
        quality_status: Optional[str] = None,
        pipeline_name: Optional[str] = None,
    ) -> List[MetadataCatalogEntry]:
        """Search current catalog entries using optional exact-match filters."""

        filters = {
            "dataset_name": dataset_name,
            "dataset_key": dataset_key,
            "layer": layer,
            "owner": owner,
            "storage_format": storage_format,
            "quality_status": quality_status,
            "pipeline_name": pipeline_name,
        }

        normalized_filters = {
            field_name: value.strip().lower()
            for field_name, value in filters.items()
            if value is not None and value.strip()
        }

        results: List[MetadataCatalogEntry] = []

        for entry in self.list_entries():
            if all(
                str(getattr(entry, field_name)).strip().lower()
                == expected_value
                for field_name, expected_value
                in normalized_filters.items()
            ):
                results.append(entry)

        return results

    def delete(self, dataset_key: str) -> MetadataCatalogEntry:
        """
        Remove a catalog entry.

        This is a hard delete. Lifecycle-based archival will be introduced
        only when the catalog domain model contains lifecycle attributes.
        """

        normalized_key = self._validate_dataset_key(dataset_key)
        current_entries = self.list_entries()

        deleted_entry = next(
            (
                entry
                for entry in current_entries
                if entry.dataset_key == normalized_key
            ),
            None,
        )

        if deleted_entry is None:
            raise CatalogEntryNotFoundError(
                "Cannot delete missing catalog entry for dataset key "
                f"'{normalized_key}'."
            )

        remaining_entries = [
            entry
            for entry in current_entries
            if entry.dataset_key != normalized_key
        ]

        self._persist_entries(remaining_entries)

        return deleted_entry

    def count(self) -> int:
        """Return the number of current catalog entries."""

        return len(self.list_entries())

    def to_dataframe(self) -> DataFrame:
        """Return the current catalog as a Spark DataFrame."""

        entries = self.list_entries()
        records = [self._entry_to_record(entry) for entry in entries]

        return self._spark.createDataFrame(
            records,
            schema=self._CATALOG_SCHEMA,
        )

    def _persist_entries(
        self,
        entries: Sequence[MetadataCatalogEntry],
    ) -> None:
        """Persist a complete deterministic catalog snapshot."""

        dataset_keys = [entry.dataset_key for entry in entries]

        if len(dataset_keys) != len(set(dataset_keys)):
            raise CatalogValidationError(
                "Catalog snapshot contains duplicate dataset keys."
            )

        for entry in entries:
            self._validate_entry(entry)

        try:
            records = [
                self._entry_to_record(entry)
                for entry in sorted(
                    entries,
                    key=lambda item: item.dataset_key,
                )
            ]

            dataframe = self._spark.createDataFrame(
                records,
                schema=self._CATALOG_SCHEMA,
            )

            dataframe.write.mode("overwrite").parquet(
                self._catalog_path
            )

        except CatalogValidationError:
            raise

        except Exception as exc:
            raise CatalogPersistenceError(
                "Unable to persist metadata catalog to "
                f"'{self._catalog_path}'."
            ) from exc

    def _catalog_exists(self) -> bool:
        """Return whether the configured catalog path contains Parquet data."""

        try:
            (
                self._spark.read
                .format("parquet")
                .load(self._catalog_path)
                .limit(0)
                .collect()
            )

            return True

        except Exception as exc:
            error_message = str(exc).lower()

            path_not_found_indicators = (
                "path_not_found",
                "path does not exist",
                "doesn't exist",
                "not found",
                "no such file or directory",
            )

            if any(
                indicator in error_message
                for indicator in path_not_found_indicators
            ):
                return False

            raise CatalogPersistenceError(
                "Unable to inspect metadata catalog path "
                f"'{self._catalog_path}'."
            ) from exc

    def _get_filesystem(self):
        hadoop_configuration = (
            self._spark.sparkContext._jsc.hadoopConfiguration()
        )

        return self._spark._jvm.org.apache.hadoop.fs.FileSystem.get(
            hadoop_configuration
        )

    def _get_hadoop_path(self):
        return self._spark._jvm.org.apache.hadoop.fs.Path(
            self._catalog_path
        )

    @staticmethod
    def _validate_catalog_path(catalog_path: str) -> str:
        if not isinstance(catalog_path, str) or not catalog_path.strip():
            raise CatalogValidationError(
                "Catalog path must be a non-empty string."
            )

        return catalog_path.strip().rstrip("/")

    @staticmethod
    def _validate_dataset_key(dataset_key: str) -> str:
        if not isinstance(dataset_key, str) or not dataset_key.strip():
            raise CatalogValidationError(
                "Dataset key must be a non-empty string."
            )

        return dataset_key.strip()

    @classmethod
    def _validate_entry(
        cls,
        entry: MetadataCatalogEntry,
    ) -> None:
        if not isinstance(entry, MetadataCatalogEntry):
            raise CatalogValidationError(
                "Catalog entry must be a MetadataCatalogEntry instance."
            )

        required_text_fields = (
            "dataset_name",
            "dataset_key",
            "layer",
            "storage_path",
            "storage_format",
            "schema_hash",
            "metadata_hash",
            "fingerprint_version",
            "quality_status",
            "owner",
            "business_description",
            "execution_id",
            "pipeline_name",
            "pipeline_version",
        )

        for field_name in required_text_fields:
            value = getattr(entry, field_name)

            if not isinstance(value, str) or not value.strip():
                raise CatalogValidationError(
                    f"Catalog field '{field_name}' must be a "
                    "non-empty string."
                )

        if entry.row_count < 0:
            raise CatalogValidationError(
                "Catalog row_count cannot be negative."
            )

        if entry.column_count < 0:
            raise CatalogValidationError(
                "Catalog column_count cannot be negative."
            )

        cls._validate_percentage(
            "null_cell_percentage",
            entry.null_cell_percentage,
        )
        cls._validate_percentage(
            "duplicate_row_percentage",
            entry.duplicate_row_percentage,
        )

        if (
            entry.quality_score is not None
            and not 0.0 <= entry.quality_score <= 100.0
        ):
            raise CatalogValidationError(
                "Catalog quality_score must be between 0 and 100."
            )

        if not isinstance(entry.profiled_at_utc, datetime):
            raise CatalogValidationError(
                "Catalog profiled_at_utc must be a datetime."
            )

    @staticmethod
    def _validate_percentage(
        field_name: str,
        value: float,
    ) -> None:
        if not 0.0 <= value <= 100.0:
            raise CatalogValidationError(
                f"Catalog {field_name} must be between 0 and 100."
            )

    @staticmethod
    def _entry_to_record(
        entry: MetadataCatalogEntry,
    ) -> Dict[str, object]:
        return {
            "dataset_name": entry.dataset_name,
            "dataset_key": entry.dataset_key,
            "layer": entry.layer,
            "storage_path": entry.storage_path,
            "storage_format": entry.storage_format,
            "row_count": int(entry.row_count),
            "column_count": int(entry.column_count),
            "schema_hash": entry.schema_hash,
            "metadata_hash": entry.metadata_hash,
            "fingerprint_version": entry.fingerprint_version,
            "null_cell_percentage": float(
                entry.null_cell_percentage
            ),
            "duplicate_row_percentage": float(
                entry.duplicate_row_percentage
            ),
            "quality_status": entry.quality_status,
            "quality_score": (
                float(entry.quality_score)
                if entry.quality_score is not None
                else None
            ),
            "owner": entry.owner,
            "business_description": entry.business_description,
            "execution_id": entry.execution_id,
            "pipeline_name": entry.pipeline_name,
            "pipeline_version": entry.pipeline_version,
            "profiled_at_utc": entry.profiled_at_utc,
        }

    @staticmethod
    def _row_to_entry(
        row: Dict[str, object],
    ) -> MetadataCatalogEntry:
        return MetadataCatalogEntry(
            dataset_name=str(row["dataset_name"]),
            dataset_key=str(row["dataset_key"]),
            layer=str(row["layer"]),
            storage_path=str(row["storage_path"]),
            storage_format=str(row["storage_format"]),
            row_count=int(row["row_count"]),
            column_count=int(row["column_count"]),
            schema_hash=str(row["schema_hash"]),
            metadata_hash=str(row["metadata_hash"]),
            fingerprint_version=str(row["fingerprint_version"]),
            null_cell_percentage=float(
                row["null_cell_percentage"]
            ),
            duplicate_row_percentage=float(
                row["duplicate_row_percentage"]
            ),
            quality_status=str(row["quality_status"]),
            quality_score=(
                float(row["quality_score"])
                if row["quality_score"] is not None
                else None
            ),
            owner=str(row["owner"]),
            business_description=str(
                row["business_description"]
            ),
            execution_id=str(row["execution_id"]),
            pipeline_name=str(row["pipeline_name"]),
            pipeline_version=str(row["pipeline_version"]),
            profiled_at_utc=row["profiled_at_utc"],
        )