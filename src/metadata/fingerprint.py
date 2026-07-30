"""Deterministic fingerprint generation for Spark datasets."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .exceptions import DatasetFingerprintError
from .models import DatasetFingerprint, DatasetStatistics


FINGERPRINT_VERSION = "1.0.0"
HASH_ALGORITHM = "SHA-256"


class DatasetFingerprintGenerator:
    """
    Generate deterministic fingerprints for Spark datasets.

    The fingerprint combines schema, content, business metadata, and dataset
    dimensions into one reproducible identifier.
    """

    @staticmethod
    def _sha256(value: str) -> str:
        """Return a SHA-256 hexadecimal digest."""
        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _canonical_json(value: Any) -> str:
        """Serialize a value into deterministic JSON."""
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

    @staticmethod
    def _validate_dataframe(
        dataframe: DataFrame,
    ) -> None:
        """Validate the Spark DataFrame input."""
        if dataframe is None:
            raise DatasetFingerprintError(
                "A Spark DataFrame is required."
            )

        if not isinstance(dataframe, DataFrame):
            raise DatasetFingerprintError(
                "Dataset fingerprinting requires a Spark DataFrame; "
                f"received {type(dataframe).__name__}."
            )

    def _generate_schema_hash(
        self,
        dataframe: DataFrame,
    ) -> str:
        """Generate a deterministic schema hash."""
        schema_payload = [
            {
                "name": field.name,
                "data_type": field.dataType.simpleString(),
                "nullable": field.nullable,
                "metadata": dict(field.metadata),
            }
            for field in dataframe.schema.fields
        ]

        return self._sha256(
            self._canonical_json(schema_payload)
        )

    def _generate_content_hash(
        self,
        dataframe: DataFrame,
    ) -> str:
        """
        Generate an order-independent distributed content hash.

        The full dataset is not collected to the driver. Spark aggregates
        row-level hashes and returns only one summary row.
        """
        ordered_columns = sorted(dataframe.columns)

        if not ordered_columns:
            return self._sha256("EMPTY_SCHEMA")

        canonical_row = F.to_json(
            F.struct(
                *[
                    F.col(column_name).alias(column_name)
                    for column_name in ordered_columns
                ]
            ),
            options={"ignoreNullFields": "false"},
        )

        hashed_dataframe = dataframe.select(
            F.xxhash64(canonical_row).alias("_row_hash")
        )

        aggregate_row = (
            hashed_dataframe.agg(
                F.count("*").alias("row_count"),
                F.sum(
                    F.col("_row_hash").cast("decimal(38,0)")
                ).alias("hash_sum"),
                F.min("_row_hash").alias("hash_min"),
                F.max("_row_hash").alias("hash_max"),
                F.countDistinct("_row_hash").alias(
                    "distinct_row_hash_count"
                ),
            )
            .first()
        )

        content_payload = {
            "row_count": int(
                aggregate_row["row_count"]
            ),
            "hash_sum": str(
                aggregate_row["hash_sum"] or 0
            ),
            "hash_min": str(
                aggregate_row["hash_min"] or 0
            ),
            "hash_max": str(
                aggregate_row["hash_max"] or 0
            ),
            "distinct_row_hash_count": int(
                aggregate_row[
                    "distinct_row_hash_count"
                ]
            ),
            "ordered_columns": ordered_columns,
        }

        return self._sha256(
            self._canonical_json(content_payload)
        )

    def _generate_metadata_hash(
        self,
        metadata: Mapping[str, Any] | None,
    ) -> str:
        """Generate a deterministic business metadata hash."""
        metadata_payload = dict(metadata or {})

        return self._sha256(
            self._canonical_json(metadata_payload)
        )

    def generate(
        self,
        dataframe: DataFrame,
        *,
        metadata: Mapping[str, Any] | None = None,
        statistics: DatasetStatistics | None = None,
    ) -> DatasetFingerprint:
        """
        Generate a complete dataset fingerprint.

        Existing profiler statistics are reused when supplied. Otherwise,
        only row count and column count are calculated here.
        """
        self._validate_dataframe(dataframe)

        if statistics is not None and not isinstance(
            statistics,
            DatasetStatistics,
        ):
            raise DatasetFingerprintError(
                "statistics must be a DatasetStatistics instance."
            )

        row_count = (
            statistics.row_count
            if statistics is not None
            else dataframe.count()
        )

        column_count = (
            statistics.column_count
            if statistics is not None
            else len(dataframe.columns)
        )

        schema_hash = self._generate_schema_hash(
            dataframe
        )

        content_hash = self._generate_content_hash(
            dataframe
        )

        metadata_hash = self._generate_metadata_hash(
            metadata
        )

        combined_payload = {
            "schema_hash": schema_hash,
            "content_hash": content_hash,
            "metadata_hash": metadata_hash,
            "row_count": row_count,
            "column_count": column_count,
            "fingerprint_version": FINGERPRINT_VERSION,
            "algorithm": HASH_ALGORITHM,
        }

        combined_hash = self._sha256(
            self._canonical_json(combined_payload)
        )

        return DatasetFingerprint(
            schema_hash=schema_hash,
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            combined_hash=combined_hash,
            row_count=row_count,
            column_count=column_count,
            fingerprint_version=FINGERPRINT_VERSION,
            algorithm=HASH_ALGORITHM,
            generated_at_utc=datetime.now(
                timezone.utc
            ),
        )

    @staticmethod
    def fingerprints_match(
        first: DatasetFingerprint,
        second: DatasetFingerprint,
    ) -> bool:
        """Return True when two fingerprints identify the same dataset."""
        if not isinstance(first, DatasetFingerprint):
            raise TypeError(
                "first must be a DatasetFingerprint."
            )

        if not isinstance(second, DatasetFingerprint):
            raise TypeError(
                "second must be a DatasetFingerprint."
            )

        return first.combined_hash == second.combined_hash