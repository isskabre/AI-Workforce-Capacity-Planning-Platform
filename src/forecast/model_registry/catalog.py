"""
AI Workforce Capacity Planning Platform
Implementation 16 - Enterprise Model Registry Framework

Module:
    forecast.model_registry.catalog

Description:
    Defines the read-only enterprise forecast model catalog responsible for
    deterministic discovery, filtering, and lookup across immutable model
    registration records.

    The catalog never mutates registry state. Registration, removal,
    versioning, promotion, persistence, and model loading remain the
    responsibility of their dedicated framework services.

Architecture:
    Enterprise Model Registry Framework

Version:
    2.8.0
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry,
    ForecastModelRegistration,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifactStatus,
)
from src.forecast.modeling.contracts import (
    ForecastModelCategory,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


@dataclass(frozen=True, slots=True)
class ForecastModelCatalogQuery:
    """
    Immutable query contract for registry catalog discovery.

    All supplied filters are combined using logical AND.

    Attributes:
        model_name:
            Optional exact model-name filter. Matching is case-insensitive.

        model_version:
            Optional exact model-version filter. Matching is case-insensitive.

        model_category:
            Optional model-category filter.

        algorithm:
            Optional exact algorithm filter. Matching is case-insensitive.

        artifact_status:
            Optional persisted-artifact lifecycle status filter.

        target_column:
            Optional exact target-column filter. Matching is case-insensitive.

        forecast_horizon:
            Optional exact forecast-horizon filter.

        primary_metric:
            Optional exact primary-metric filter. Matching is case-insensitive.

        metadata:
            Optional metadata subset filter. Every supplied key/value pair
            must exist in the registration metadata.

        order_by:
            Deterministic result ordering field.

            Supported values:

            - ``model_name``
            - ``model_version``
            - ``algorithm``
            - ``registered_at``
            - ``primary_metric_value``

        descending:
            Whether results should be sorted in descending order.

        limit:
            Optional maximum number of registrations returned.
    """

    model_name: str | None = None
    model_version: str | None = None
    model_category: ForecastModelCategory | None = None
    algorithm: str | None = None
    artifact_status: ForecastArtifactStatus | None = None
    target_column: str | None = None
    forecast_horizon: int | None = None
    primary_metric: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    order_by: str = "model_name"
    descending: bool = False
    limit: int | None = None

    SUPPORTED_ORDER_FIELDS = frozenset(
        {
            "model_name",
            "model_version",
            "algorithm",
            "registered_at",
            "primary_metric_value",
        }
    )

    def __post_init__(self) -> None:
        """Validate and normalize the immutable catalog query."""
        object.__setattr__(
            self,
            "model_name",
            self._normalize_optional_string(
                self.model_name,
                field_name="model_name",
            ),
        )
        object.__setattr__(
            self,
            "model_version",
            self._normalize_optional_string(
                self.model_version,
                field_name="model_version",
            ),
        )
        object.__setattr__(
            self,
            "algorithm",
            self._normalize_optional_string(
                self.algorithm,
                field_name="algorithm",
            ),
        )
        object.__setattr__(
            self,
            "target_column",
            self._normalize_optional_string(
                self.target_column,
                field_name="target_column",
            ),
        )
        object.__setattr__(
            self,
            "primary_metric",
            self._normalize_optional_string(
                self.primary_metric,
                field_name="primary_metric",
            ),
        )

        if (
            self.model_category is not None
            and not isinstance(
                self.model_category,
                ForecastModelCategory,
            )
        ):
            raise ForecastRegistryError(
                "Catalog query model_category is invalid.",
                context={
                    "received_type": type(
                        self.model_category
                    ).__name__,
                },
            )

        if (
            self.artifact_status is not None
            and not isinstance(
                self.artifact_status,
                ForecastArtifactStatus,
            )
        ):
            raise ForecastRegistryError(
                "Catalog query artifact_status is invalid.",
                context={
                    "received_type": type(
                        self.artifact_status
                    ).__name__,
                },
            )

        if self.forecast_horizon is not None:
            if (
                isinstance(self.forecast_horizon, bool)
                or not isinstance(self.forecast_horizon, int)
            ):
                raise ForecastRegistryError(
                    "Catalog query forecast_horizon must be an integer.",
                    context={
                        "received_type": type(
                            self.forecast_horizon
                        ).__name__,
                    },
                )

            if self.forecast_horizon <= 0:
                raise ForecastRegistryError(
                    "Catalog query forecast_horizon must be greater than zero.",
                    context={
                        "forecast_horizon": self.forecast_horizon,
                    },
                )

        if not isinstance(self.metadata, Mapping):
            raise ForecastRegistryError(
                "Catalog query metadata must be a mapping.",
                context={
                    "received_type": type(
                        self.metadata
                    ).__name__,
                },
            )

        normalized_metadata: dict[str, Any] = {}

        for raw_key, value in self.metadata.items():
            if not isinstance(raw_key, str):
                raise ForecastRegistryError(
                    "Catalog query metadata keys must be strings.",
                    context={
                        "received_type": type(raw_key).__name__,
                    },
                )

            normalized_key = raw_key.strip()

            if not normalized_key:
                raise ForecastRegistryError(
                    "Catalog query metadata keys must not be empty."
                )

            normalized_metadata[normalized_key] = value

        if not isinstance(self.order_by, str):
            raise ForecastRegistryError(
                "Catalog query order_by must be a string.",
                context={
                    "received_type": type(
                        self.order_by
                    ).__name__,
                },
            )

        normalized_order_by = self.order_by.strip().lower()

        if normalized_order_by not in self.SUPPORTED_ORDER_FIELDS:
            raise ForecastRegistryError(
                "Unsupported catalog ordering field.",
                context={
                    "order_by": self.order_by,
                    "supported_order_fields": tuple(
                        sorted(self.SUPPORTED_ORDER_FIELDS)
                    ),
                },
            )

        if not isinstance(self.descending, bool):
            raise ForecastRegistryError(
                "Catalog query descending must be a boolean.",
                context={
                    "received_type": type(
                        self.descending
                    ).__name__,
                },
            )

        if self.limit is not None:
            if isinstance(self.limit, bool) or not isinstance(
                self.limit,
                int,
            ):
                raise ForecastRegistryError(
                    "Catalog query limit must be an integer.",
                    context={
                        "received_type": type(
                            self.limit
                        ).__name__,
                    },
                )

            if self.limit <= 0:
                raise ForecastRegistryError(
                    "Catalog query limit must be greater than zero.",
                    context={
                        "limit": self.limit,
                    },
                )

        object.__setattr__(
            self,
            "metadata",
            dict(normalized_metadata),
        )
        object.__setattr__(
            self,
            "order_by",
            normalized_order_by,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe catalog query."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_category": (
                self.model_category.value
                if self.model_category is not None
                else None
            ),
            "algorithm": self.algorithm,
            "artifact_status": (
                self.artifact_status.value
                if self.artifact_status is not None
                else None
            ),
            "target_column": self.target_column,
            "forecast_horizon": self.forecast_horizon,
            "primary_metric": self.primary_metric,
            "metadata": dict(self.metadata),
            "order_by": self.order_by,
            "descending": self.descending,
            "limit": self.limit,
        }

    @staticmethod
    def _normalize_optional_string(
        value: Any,
        *,
        field_name: str,
    ) -> str | None:
        """Normalize one optional non-empty string."""
        if value is None:
            return None

        if not isinstance(value, str):
            raise ForecastRegistryError(
                f"Catalog query {field_name} must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = value.strip()

        if not normalized:
            raise ForecastRegistryError(
                f"Catalog query {field_name} must not be empty."
            )

        return normalized


@dataclass(frozen=True, slots=True)
class ForecastModelCatalogResult:
    """
    Immutable result returned by enterprise model catalog queries.

    Attributes:
        query:
            Validated catalog query used for discovery.

        registrations:
            Ordered immutable matching registration records.

        total_registry_models:
            Number of registrations available before filtering.
    """

    query: ForecastModelCatalogQuery
    registrations: tuple[ForecastModelRegistration, ...]
    total_registry_models: int

    def __post_init__(self) -> None:
        """Validate the immutable catalog result."""
        if not isinstance(
            self.query,
            ForecastModelCatalogQuery,
        ):
            raise ForecastRegistryError(
                "Catalog result query must be a "
                "ForecastModelCatalogQuery.",
                context={
                    "received_type": type(
                        self.query
                    ).__name__,
                },
            )

        if not isinstance(self.registrations, tuple):
            raise ForecastRegistryError(
                "Catalog result registrations must be stored as a tuple.",
                context={
                    "received_type": type(
                        self.registrations
                    ).__name__,
                },
            )

        for index, registration in enumerate(
            self.registrations
        ):
            if not isinstance(
                registration,
                ForecastModelRegistration,
            ):
                raise ForecastRegistryError(
                    "Every catalog result item must be a "
                    "ForecastModelRegistration.",
                    context={
                        "index": index,
                        "received_type": type(
                            registration
                        ).__name__,
                    },
                )

        if (
            isinstance(self.total_registry_models, bool)
            or not isinstance(self.total_registry_models, int)
        ):
            raise ForecastRegistryError(
                "Catalog total_registry_models must be an integer.",
                context={
                    "received_type": type(
                        self.total_registry_models
                    ).__name__,
                },
            )

        if self.total_registry_models < 0:
            raise ForecastRegistryError(
                "Catalog total_registry_models cannot be negative."
            )

        if len(self.registrations) > self.total_registry_models:
            raise ForecastRegistryError(
                "Catalog result count cannot exceed total registry models.",
                context={
                    "result_count": len(self.registrations),
                    "total_registry_models": (
                        self.total_registry_models
                    ),
                },
            )

    @property
    def total_matches(self) -> int:
        """Return the number of matching registrations."""
        return len(self.registrations)

    @property
    def is_empty(self) -> bool:
        """Return whether the query produced no matches."""
        return self.total_matches == 0

    @property
    def first(self) -> ForecastModelRegistration | None:
        """Return the first catalog match when available."""
        if not self.registrations:
            return None

        return self.registrations[0]

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe catalog result."""
        return {
            "query": self.query.to_dict(),
            "total_registry_models": self.total_registry_models,
            "total_matches": self.total_matches,
            "is_empty": self.is_empty,
            "registrations": [
                registration.to_dict()
                for registration in self.registrations
            ],
        }


class EnterpriseModelCatalog:
    """
    Read-only discovery service over ``EnterpriseModelRegistry``.

    The catalog obtains immutable registry snapshots through
    ``EnterpriseModelRegistry.list_models`` and performs deterministic,
    side-effect-free filtering.

    It does not:

    - register models;
    - remove models;
    - mutate registration metadata;
    - assign model versions;
    - promote or archive models;
    - load executable artifacts.
    """

    def __init__(
        self,
        *,
        registry: EnterpriseModelRegistry,
    ) -> None:
        """
        Initialize the model catalog.

        Args:
            registry:
                Enterprise model registry used as the catalog data source.
        """
        if not isinstance(
            registry,
            EnterpriseModelRegistry,
        ):
            raise ForecastRegistryError(
                "registry must be an EnterpriseModelRegistry.",
                context={
                    "received_type": type(
                        registry
                    ).__name__,
                },
            )

        self._registry = registry

    @property
    def registry(self) -> EnterpriseModelRegistry:
        """Return the registry used by the catalog."""
        return self._registry

    def search(
        self,
        query: ForecastModelCatalogQuery | None = None,
    ) -> ForecastModelCatalogResult:
        """
        Search registered model metadata.

        Args:
            query:
                Optional catalog query. An empty query returns the complete
                registry inventory.

        Returns:
            Immutable ``ForecastModelCatalogResult``.
        """
        resolved_query = (
            query
            if query is not None
            else ForecastModelCatalogQuery()
        )

        if not isinstance(
            resolved_query,
            ForecastModelCatalogQuery,
        ):
            raise ForecastRegistryError(
                "query must be a ForecastModelCatalogQuery.",
                context={
                    "received_type": type(
                        resolved_query
                    ).__name__,
                },
            )

        registry_snapshot = self._registry.list_models()

        matching = tuple(
            registration
            for registration in registry_snapshot
            if self._matches_query(
                registration=registration,
                query=resolved_query,
            )
        )

        ordered = self._sort_registrations(
            registrations=matching,
            order_by=resolved_query.order_by,
            descending=resolved_query.descending,
        )

        if resolved_query.limit is not None:
            ordered = ordered[: resolved_query.limit]

        return ForecastModelCatalogResult(
            query=resolved_query,
            registrations=ordered,
            total_registry_models=len(
                registry_snapshot
            ),
        )

    def find_one(
        self,
        query: ForecastModelCatalogQuery,
    ) -> ForecastModelRegistration:
        """
        Return exactly one matching registration.

        Raises:
            ForecastRegistryError:
                If no registrations match or if the query is ambiguous.
        """
        result = self.search(query)

        if result.total_matches == 0:
            raise ForecastRegistryError(
                "Model catalog query returned no registrations.",
                context={
                    "query": query.to_dict(),
                },
            )

        if result.total_matches > 1:
            raise ForecastRegistryError(
                "Model catalog query returned multiple registrations.",
                context={
                    "query": query.to_dict(),
                    "total_matches": result.total_matches,
                },
            )

        registration = result.first

        if registration is None:
            raise ForecastRegistryError(
                "Model catalog query did not resolve a registration."
            )

        return registration

    def list_categories(
        self,
    ) -> tuple[ForecastModelCategory, ...]:
        """Return registered model categories in deterministic order."""
        categories = {
            registration.model_category
            for registration in self._registry.list_models()
        }

        return tuple(
            sorted(
                categories,
                key=lambda category: category.value,
            )
        )

    def list_algorithms(self) -> tuple[str, ...]:
        """Return registered algorithm identifiers."""
        algorithms = {
            registration.algorithm
            for registration in self._registry.list_models()
        }

        return tuple(
            sorted(
                algorithms,
                key=str.lower,
            )
        )

    def list_target_columns(self) -> tuple[str, ...]:
        """Return registered target columns."""
        target_columns = {
            registration.target_column
            for registration in self._registry.list_models()
        }

        return tuple(
            sorted(
                target_columns,
                key=str.lower,
            )
        )

    @classmethod
    def _matches_query(
        cls,
        *,
        registration: ForecastModelRegistration,
        query: ForecastModelCatalogQuery,
    ) -> bool:
        """Return whether one registration satisfies every query filter."""
        if (
            query.model_name is not None
            and not cls._strings_equal(
                registration.model_name,
                query.model_name,
            )
        ):
            return False

        if (
            query.model_version is not None
            and not cls._strings_equal(
                registration.model_version,
                query.model_version,
            )
        ):
            return False

        if (
            query.model_category is not None
            and registration.model_category
            != query.model_category
        ):
            return False

        if (
            query.algorithm is not None
            and not cls._strings_equal(
                registration.algorithm,
                query.algorithm,
            )
        ):
            return False

        if (
            query.artifact_status is not None
            and registration.artifact_status
            != query.artifact_status
        ):
            return False

        if (
            query.target_column is not None
            and not cls._strings_equal(
                registration.target_column,
                query.target_column,
            )
        ):
            return False

        if (
            query.forecast_horizon is not None
            and registration.forecast_horizon
            != query.forecast_horizon
        ):
            return False

        if query.primary_metric is not None:
            if registration.primary_metric is None:
                return False

            if not cls._strings_equal(
                registration.primary_metric,
                query.primary_metric,
            ):
                return False

        if not cls._metadata_contains(
            registration_metadata=registration.metadata,
            query_metadata=query.metadata,
        ):
            return False

        return True

    @staticmethod
    def _metadata_contains(
        *,
        registration_metadata: Mapping[str, Any],
        query_metadata: Mapping[str, Any],
    ) -> bool:
        """Return whether registration metadata contains the query subset."""
        for key, expected_value in query_metadata.items():
            if key not in registration_metadata:
                return False

            if registration_metadata[key] != expected_value:
                return False

        return True

    @classmethod
    def _sort_registrations(
        cls,
        *,
        registrations: tuple[
            ForecastModelRegistration,
            ...
        ],
        order_by: str,
        descending: bool,
    ) -> tuple[ForecastModelRegistration, ...]:
        """Sort registrations deterministically."""
        if order_by == "model_name":
            key_function = lambda registration: (
                registration.model_name.lower(),
                registration.model_version.lower(),
                registration.registration_id,
            )

        elif order_by == "model_version":
            key_function = lambda registration: (
                registration.model_version.lower(),
                registration.model_name.lower(),
                registration.registration_id,
            )

        elif order_by == "algorithm":
            key_function = lambda registration: (
                registration.algorithm.lower(),
                registration.model_name.lower(),
                registration.model_version.lower(),
                registration.registration_id,
            )

        elif order_by == "registered_at":
            key_function = lambda registration: (
                registration.registered_at,
                registration.model_name.lower(),
                registration.model_version.lower(),
                registration.registration_id,
            )

        elif order_by == "primary_metric_value":
            key_function = lambda registration: (
                registration.primary_metric_value is None,
                (
                    registration.primary_metric_value
                    if registration.primary_metric_value is not None
                    else float("inf")
                ),
                registration.model_name.lower(),
                registration.model_version.lower(),
                registration.registration_id,
            )

        else:
            raise ForecastRegistryError(
                "Unsupported catalog ordering field.",
                context={
                    "order_by": order_by,
                },
            )

        return tuple(
            sorted(
                registrations,
                key=key_function,
                reverse=descending,
            )
        )

    @staticmethod
    def _strings_equal(
        first: str,
        second: str,
    ) -> bool:
        """Compare normalized strings case-insensitively."""
        return first.strip().lower() == second.strip().lower()


__all__ = [
    "EnterpriseModelCatalog",
    "ForecastModelCatalogQuery",
    "ForecastModelCatalogResult",
]