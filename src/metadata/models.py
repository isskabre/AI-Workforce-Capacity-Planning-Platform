"""
Typed domain models for dataset metadata and profiling.

These models form the contract between the profiling, fingerprinting,
catalog, and metadata service components.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ColumnProfile:
    """Statistical and structural metadata for one dataset column."""

    column_name: str
    data_type: str
    nullable: bool

    null_count: int
    null_percentage: float
    distinct_count: int

    minimum: Optional[Any] = None
    maximum: Optional[Any] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    standard_deviation: Optional[float] = None

    minimum_length: Optional[int] = None
    maximum_length: Optional[int] = None
    average_length: Optional[float] = None

    profile_status: str = "COMPLETED"
    profile_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation."""

        return asdict(self)


@dataclass(frozen=True)
class DatasetStatistics:
    """Dataset-level structural and quality statistics."""

    row_count: int
    column_count: int

    numeric_column_count: int
    string_column_count: int
    boolean_column_count: int
    date_column_count: int
    timestamp_column_count: int
    other_column_count: int

    null_cell_count: int
    null_cell_percentage: float

    duplicate_row_count: int
    duplicate_row_percentage: float

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation."""

        return asdict(self)


@dataclass(frozen=True)
class DatasetFingerprint:
    """
    Enterprise fingerprint describing one logical dataset version.

    A fingerprint combines schema, content, and business metadata into
    deterministic hashes used for change detection, lineage, auditing,
    and metadata versioning.
    """

    # Schema fingerprint
    schema_hash: str

    # Content fingerprint
    content_hash: str

    # Business metadata fingerprint
    metadata_hash: str

    # Enterprise fingerprint
    combined_hash: str

    # Dataset statistics
    row_count: int
    column_count: int

    # Versioning
    fingerprint_version: str

    # Hash algorithm
    algorithm: str

    # Timestamp
    generated_at_utc: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation."""

        values = asdict(self)
        values["generated_at_utc"] = (
            self.generated_at_utc.isoformat()
        )
        return values


@dataclass(frozen=True)
class DatasetProfile:
    """Complete profile generated for one dataset execution."""

    dataset_name: str
    dataset_key: str
    layer: str
    storage_path: str
    storage_format: str

    execution_id: str
    pipeline_name: str
    pipeline_version: str

    owner: str
    business_description: str

    statistics: DatasetStatistics
    fingerprint: DatasetFingerprint
    columns: List[ColumnProfile] = field(default_factory=list)

    quality_status: str = "UNKNOWN"
    quality_score: Optional[float] = None

    profiled_at_utc: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete profile as a serializable dictionary."""

        return {
            "dataset_name": self.dataset_name,
            "dataset_key": self.dataset_key,
            "layer": self.layer,
            "storage_path": self.storage_path,
            "storage_format": self.storage_format,
            "execution_id": self.execution_id,
            "pipeline_name": self.pipeline_name,
            "pipeline_version": self.pipeline_version,
            "owner": self.owner,
            "business_description": self.business_description,
            "statistics": self.statistics.to_dict(),
            "fingerprint": self.fingerprint.to_dict(),
            "columns": [column.to_dict() for column in self.columns],
            "quality_status": self.quality_status,
            "quality_score": self.quality_score,
            "profiled_at_utc": self.profiled_at_utc.isoformat(),
        }


@dataclass(frozen=True)
class MetadataCatalogEntry:
    """Flattened dataset-level record persisted in the metadata catalog."""

    dataset_name: str
    dataset_key: str
    layer: str

    storage_path: str
    storage_format: str

    row_count: int
    column_count: int

    schema_hash: str
    metadata_hash: str
    fingerprint_version: str

    null_cell_percentage: float
    duplicate_row_percentage: float

    quality_status: str
    quality_score: Optional[float]

    owner: str
    business_description: str

    execution_id: str
    pipeline_name: str
    pipeline_version: str

    profiled_at_utc: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation."""

        values = asdict(self)
        values["profiled_at_utc"] = self.profiled_at_utc.isoformat()
        return values

    @classmethod
    def from_profile(cls, profile: DatasetProfile) -> "MetadataCatalogEntry":
        """Create a catalog entry from a complete dataset profile."""

        return cls(
            dataset_name=profile.dataset_name,
            dataset_key=profile.dataset_key,
            layer=profile.layer,
            storage_path=profile.storage_path,
            storage_format=profile.storage_format,
            row_count=profile.statistics.row_count,
            column_count=profile.statistics.column_count,
            schema_hash=profile.fingerprint.schema_hash,
            metadata_hash=profile.fingerprint.metadata_hash,
            fingerprint_version=profile.fingerprint.fingerprint_version,
            null_cell_percentage=profile.statistics.null_cell_percentage,
            duplicate_row_percentage=(
                profile.statistics.duplicate_row_percentage
            ),
            quality_status=profile.quality_status,
            quality_score=profile.quality_score,
            owner=profile.owner,
            business_description=profile.business_description,
            execution_id=profile.execution_id,
            pipeline_name=profile.pipeline_name,
            pipeline_version=profile.pipeline_version,
            profiled_at_utc=profile.profiled_at_utc,
        )