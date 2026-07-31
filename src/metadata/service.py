"""
Enterprise Metadata Service.

Provides the public facade for dataset profiling, fingerprint generation,
and enterprise metadata catalog operations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional

from pyspark.sql import DataFrame, SparkSession

from src.metadata.catalog import MetadataCatalog
from src.metadata.fingerprint import DatasetFingerprintGenerator
from src.metadata.models import (
    DatasetProfile,
    MetadataCatalogEntry,
)
from src.metadata.profiler import SparkDatasetProfiler


class MetadataService:
    """
    Public facade for enterprise metadata operations.

    The service coordinates profiling, fingerprint generation, profile
    creation, and catalog persistence without duplicating component logic.
    """

    def __init__(
        self,
        spark: SparkSession,
        catalog_path: str,
        *,
        profiler: Optional[SparkDatasetProfiler] = None,
        fingerprint_generator: Optional[
            DatasetFingerprintGenerator
        ] = None,
        catalog: Optional[MetadataCatalog] = None,
    ) -> None:
        """
        Initialize the metadata service and its dependencies.

        Dependency injection is supported for testing and future platform
        extensions.
        """

        self._spark = spark

        self._profiler = (
            profiler
            if profiler is not None
            else SparkDatasetProfiler()
        )

        self._fingerprint_generator = (
            fingerprint_generator
            if fingerprint_generator is not None
            else DatasetFingerprintGenerator()
        )

        self._catalog = (
            catalog
            if catalog is not None
            else MetadataCatalog(
                spark=spark,
                catalog_path=catalog_path,
            )
        )

    @property
    def catalog(self) -> MetadataCatalog:
        """Return the configured metadata catalog."""

        return self._catalog

    @property
    def catalog_path(self) -> str:
        """Return the configured metadata catalog path."""

        return self._catalog.catalog_path

    def create_profile(
        self,
        dataframe: DataFrame,
        *,
        dataset_name: str,
        dataset_key: str,
        layer: str,
        storage_path: str,
        storage_format: str,
        execution_id: str,
        pipeline_name: str,
        pipeline_version: str,
        owner: str,
        business_description: str,
        quality_status: str = "UNKNOWN",
        quality_score: Optional[float] = None,
        fingerprint_metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> DatasetProfile:
        """
        Generate a complete dataset profile.

        The workflow produces dataset statistics, column profiles, and a
        deterministic fingerprint, then combines them into a DatasetProfile.
        """

        statistics, columns = self._profiler.profile(
            dataframe
        )

        resolved_fingerprint_metadata = dict(
            fingerprint_metadata or {}
        )

        resolved_fingerprint_metadata.update(
            {
                "dataset_name": dataset_name,
                "dataset_key": dataset_key,
                "layer": layer,
                "storage_path": storage_path,
                "storage_format": storage_format,
                "owner": owner,
                "pipeline_name": pipeline_name,
                "pipeline_version": pipeline_version,
            }
        )

        fingerprint = self._fingerprint_generator.generate(
            dataframe,
            metadata=resolved_fingerprint_metadata,
            statistics=statistics,
        )

        return DatasetProfile(
            dataset_name=dataset_name,
            dataset_key=dataset_key,
            layer=layer,
            storage_path=storage_path,
            storage_format=storage_format,
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            pipeline_version=pipeline_version,
            owner=owner,
            business_description=business_description,
            statistics=statistics,
            fingerprint=fingerprint,
            columns=columns,
            quality_status=quality_status,
            quality_score=quality_score,
            profiled_at_utc=datetime.now(timezone.utc),
        )

    def register_profile(
        self,
        profile: DatasetProfile,
        *,
        overwrite: bool = False,
    ) -> MetadataCatalogEntry:
        """
        Convert a complete profile into a catalog entry and persist it.
        """

        if not isinstance(profile, DatasetProfile):
            raise TypeError(
                "profile must be a DatasetProfile instance."
            )

        catalog_entry = MetadataCatalogEntry.from_profile(
            profile
        )

        return self._catalog.register(
            catalog_entry,
            overwrite=overwrite,
        )

    def register_dataset(
        self,
        dataframe: DataFrame,
        *,
        dataset_name: str,
        dataset_key: str,
        layer: str,
        storage_path: str,
        storage_format: str,
        execution_id: str,
        pipeline_name: str,
        pipeline_version: str,
        owner: str,
        business_description: str,
        quality_status: str = "UNKNOWN",
        quality_score: Optional[float] = None,
        fingerprint_metadata: Optional[
            Mapping[str, Any]
        ] = None,
        overwrite: bool = False,
    ) -> tuple[DatasetProfile, MetadataCatalogEntry]:
        """
        Profile, fingerprint, and register one dataset.

        Returns the complete profile and the persisted catalog entry.
        """

        profile = self.create_profile(
            dataframe,
            dataset_name=dataset_name,
            dataset_key=dataset_key,
            layer=layer,
            storage_path=storage_path,
            storage_format=storage_format,
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            pipeline_version=pipeline_version,
            owner=owner,
            business_description=business_description,
            quality_status=quality_status,
            quality_score=quality_score,
            fingerprint_metadata=fingerprint_metadata,
        )

        catalog_entry = self.register_profile(
            profile,
            overwrite=overwrite,
        )

        return profile, catalog_entry

    def refresh_dataset(
        self,
        dataframe: DataFrame,
        *,
        dataset_name: str,
        dataset_key: str,
        layer: str,
        storage_path: str,
        storage_format: str,
        execution_id: str,
        pipeline_name: str,
        pipeline_version: str,
        owner: str,
        business_description: str,
        quality_status: str = "UNKNOWN",
        quality_score: Optional[float] = None,
        fingerprint_metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> tuple[DatasetProfile, MetadataCatalogEntry]:
        """
        Re-profile a dataset and replace its current catalog entry.

        The dataset must already exist in the catalog.
        """

        profile = self.create_profile(
            dataframe,
            dataset_name=dataset_name,
            dataset_key=dataset_key,
            layer=layer,
            storage_path=storage_path,
            storage_format=storage_format,
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            pipeline_version=pipeline_version,
            owner=owner,
            business_description=business_description,
            quality_status=quality_status,
            quality_score=quality_score,
            fingerprint_metadata=fingerprint_metadata,
        )

        catalog_entry = MetadataCatalogEntry.from_profile(
            profile
        )

        updated_entry = self._catalog.update(
            catalog_entry
        )

        return profile, updated_entry

    def upsert_dataset(
        self,
        dataframe: DataFrame,
        *,
        dataset_name: str,
        dataset_key: str,
        layer: str,
        storage_path: str,
        storage_format: str,
        execution_id: str,
        pipeline_name: str,
        pipeline_version: str,
        owner: str,
        business_description: str,
        quality_status: str = "UNKNOWN",
        quality_score: Optional[float] = None,
        fingerprint_metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> tuple[DatasetProfile, MetadataCatalogEntry]:
        """
        Profile a dataset and insert or replace its catalog entry.
        """

        profile = self.create_profile(
            dataframe,
            dataset_name=dataset_name,
            dataset_key=dataset_key,
            layer=layer,
            storage_path=storage_path,
            storage_format=storage_format,
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            pipeline_version=pipeline_version,
            owner=owner,
            business_description=business_description,
            quality_status=quality_status,
            quality_score=quality_score,
            fingerprint_metadata=fingerprint_metadata,
        )

        catalog_entry = MetadataCatalogEntry.from_profile(
            profile
        )

        persisted_entry = self._catalog.upsert(
            catalog_entry
        )

        return profile, persisted_entry

    def get_dataset(
        self,
        dataset_key: str,
    ) -> MetadataCatalogEntry:
        """Return one catalog entry by dataset key."""

        return self._catalog.get(dataset_key)

    def dataset_exists(
        self,
        dataset_key: str,
    ) -> bool:
        """Return whether a dataset exists in the catalog."""

        return self._catalog.exists(dataset_key)

    def list_datasets(self) -> List[MetadataCatalogEntry]:
        """Return all current catalog entries."""

        return self._catalog.list_entries()

    def search_datasets(
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
        """Search catalog entries using optional exact-match filters."""

        return self._catalog.search(
            dataset_name=dataset_name,
            dataset_key=dataset_key,
            layer=layer,
            owner=owner,
            storage_format=storage_format,
            quality_status=quality_status,
            pipeline_name=pipeline_name,
        )

    def delete_dataset(
        self,
        dataset_key: str,
    ) -> MetadataCatalogEntry:
        """Delete one current catalog entry."""

        return self._catalog.delete(dataset_key)

    def count_datasets(self) -> int:
        """Return the number of cataloged datasets."""

        return self._catalog.count()

    def catalog_dataframe(self) -> DataFrame:
        """Return the current metadata catalog as a Spark DataFrame."""

        return self._catalog.to_dataframe()