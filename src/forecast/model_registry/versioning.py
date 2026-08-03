"""
AI Workforce Capacity Planning Platform
Implementation 16 - Enterprise Model Registry Framework

Module:
    forecast.model_registry.versioning

Description:
    Defines semantic model-version contracts and read-only version resolution
    services for registered enterprise forecasting models.

    The versioning layer interprets, orders, and resolves registered model
    versions. It never registers, removes, promotes, persists, or loads model
    artifacts.

Architecture:
    Enterprise Model Registry Framework

Version:
    2.8.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Final

from forecast.model_registry.registry import (
    EnterpriseModelRegistry,
    ForecastModelRegistration,
)
from forecast.modeling.exceptions import (
    ForecastRegistryError,
)


_SEMANTIC_VERSION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)$"
)


@dataclass(frozen=True, slots=True, order=True)
class ForecastModelVersion:
    """
    Immutable semantic version used by the model registry.

    Versions follow the strict numeric format:

        major.minor.patch

    Examples:
        1.0.0
        1.4.12
        10.0.3

    Pre-release labels, build metadata, shortened versions, and prefixed
    versions such as ``v1.0.0`` are intentionally unsupported in this
    framework version.
    """

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        """Validate semantic-version components."""
        self._validate_component(
            value=self.major,
            field_name="major",
        )
        self._validate_component(
            value=self.minor,
            field_name="minor",
        )
        self._validate_component(
            value=self.patch,
            field_name="patch",
        )

    @classmethod
    def parse(
        cls,
        value: str,
    ) -> "ForecastModelVersion":
        """
        Parse a strict ``major.minor.patch`` version string.

        Args:
            value:
                Semantic version string.

        Returns:
            Immutable parsed version.

        Raises:
            ForecastRegistryError:
                If the value is not a valid strict semantic version.
        """
        if not isinstance(value, str):
            raise ForecastRegistryError(
                "Model version must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = value.strip()

        if not normalized:
            raise ForecastRegistryError(
                "Model version must not be empty."
            )

        match = _SEMANTIC_VERSION_PATTERN.fullmatch(
            normalized
        )

        if match is None:
            raise ForecastRegistryError(
                "Model version must use strict major.minor.patch format.",
                context={
                    "model_version": value,
                    "expected_format": "major.minor.patch",
                },
            )

        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
        )

    def bump_major(self) -> "ForecastModelVersion":
        """
        Return the next major version.

        Example:
            ``2.4.7`` becomes ``3.0.0``.
        """
        return ForecastModelVersion(
            major=self.major + 1,
            minor=0,
            patch=0,
        )

    def bump_minor(self) -> "ForecastModelVersion":
        """
        Return the next minor version.

        Example:
            ``2.4.7`` becomes ``2.5.0``.
        """
        return ForecastModelVersion(
            major=self.major,
            minor=self.minor + 1,
            patch=0,
        )

    def bump_patch(self) -> "ForecastModelVersion":
        """
        Return the next patch version.

        Example:
            ``2.4.7`` becomes ``2.4.8``.
        """
        return ForecastModelVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
        )

    def to_string(self) -> str:
        """Return the canonical semantic-version string."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe semantic-version payload."""
        return {
            "version": self.to_string(),
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
        }

    def __str__(self) -> str:
        """Return the canonical semantic-version string."""
        return self.to_string()

    @staticmethod
    def _validate_component(
        *,
        value: Any,
        field_name: str,
    ) -> None:
        """Validate one non-negative semantic-version component."""
        if isinstance(value, bool) or not isinstance(
            value,
            int,
        ):
            raise ForecastRegistryError(
                f"Version {field_name} must be an integer.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        if value < 0:
            raise ForecastRegistryError(
                f"Version {field_name} cannot be negative.",
                context={
                    field_name: value,
                },
            )


@dataclass(frozen=True, slots=True)
class ForecastModelVersionEntry:
    """
    Immutable pairing of a parsed version and its registry record.

    Attributes:
        version:
            Parsed semantic model version.

        registration:
            Corresponding immutable registry registration.
    """

    version: ForecastModelVersion
    registration: ForecastModelRegistration

    def __post_init__(self) -> None:
        """Validate version-entry consistency."""
        if not isinstance(
            self.version,
            ForecastModelVersion,
        ):
            raise ForecastRegistryError(
                "Version entry version must be a "
                "ForecastModelVersion.",
                context={
                    "received_type": type(
                        self.version
                    ).__name__,
                },
            )

        if not isinstance(
            self.registration,
            ForecastModelRegistration,
        ):
            raise ForecastRegistryError(
                "Version entry registration must be a "
                "ForecastModelRegistration.",
                context={
                    "received_type": type(
                        self.registration
                    ).__name__,
                },
            )

        registration_version = ForecastModelVersion.parse(
            self.registration.model_version
        )

        if registration_version != self.version:
            raise ForecastRegistryError(
                "Version entry does not match registration model_version.",
                context={
                    "entry_version": str(self.version),
                    "registration_version": (
                        self.registration.model_version
                    ),
                    "model_name": (
                        self.registration.model_name
                    ),
                },
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe version entry."""
        return {
            "version": self.version.to_dict(),
            "registration": self.registration.to_dict(),
        }


class EnterpriseModelVersioning:
    """
    Read-only semantic version service over EnterpriseModelRegistry.

    Responsibilities:
        - parse and validate registered semantic versions;
        - return versions in semantic order;
        - resolve latest, previous, and next registered versions;
        - resolve registrations by semantic version;
        - calculate candidate major, minor, and patch versions.

    This service never mutates the registry.
    """

    def __init__(
        self,
        *,
        registry: EnterpriseModelRegistry,
    ) -> None:
        """
        Initialize the versioning service.

        Args:
            registry:
                Registry used as the read-only source of model versions.
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
        """Return the registry used by this service."""
        return self._registry

    def list_version_entries(
        self,
        model_name: str,
    ) -> tuple[ForecastModelVersionEntry, ...]:
        """
        Return registered versions in ascending semantic order.

        An empty tuple is returned when the model has no registrations.

        Raises:
            ForecastRegistryError:
                If a registered model version does not follow strict semantic
                version format.
        """
        normalized_model_name = self._validate_model_name(
            model_name
        )

        registrations = self._registry.list_versions(
            normalized_model_name
        )

        entries = tuple(
            ForecastModelVersionEntry(
                version=ForecastModelVersion.parse(
                    registration.model_version
                ),
                registration=registration,
            )
            for registration in registrations
        )

        return tuple(
            sorted(
                entries,
                key=lambda entry: (
                    entry.version,
                    entry.registration.registration_id,
                ),
            )
        )

    def list_versions(
        self,
        model_name: str,
    ) -> tuple[str, ...]:
        """
        Return canonical registered version strings in semantic order.
        """
        return tuple(
            entry.version.to_string()
            for entry in self.list_version_entries(
                model_name
            )
        )

    def version_exists(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> bool:
        """
        Return whether one semantic model version is registered.

        The supplied version is parsed before registry lookup, ensuring that
        only canonical strict semantic versions are accepted.
        """
        normalized_model_name = self._validate_model_name(
            model_name
        )
        parsed_version = ForecastModelVersion.parse(
            model_version
        )

        return self._registry.contains(
            model_name=normalized_model_name,
            model_version=parsed_version.to_string(),
        )

    def get_registration(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelRegistration:
        """
        Return one registration by semantic model version.

        Raises:
            ForecastRegistryError:
                If the version is invalid or not registered.
        """
        normalized_model_name = self._validate_model_name(
            model_name
        )
        parsed_version = ForecastModelVersion.parse(
            model_version
        )

        return self._registry.get(
            model_name=normalized_model_name,
            model_version=parsed_version.to_string(),
        )

    def latest_version(
        self,
        model_name: str,
    ) -> str:
        """
        Return the highest registered semantic version.

        Raises:
            ForecastRegistryError:
                If the model has no registered versions.
        """
        latest_entry = self.latest_entry(
            model_name
        )
        return latest_entry.version.to_string()

    def latest_registration(
        self,
        model_name: str,
    ) -> ForecastModelRegistration:
        """
        Return the registration with the highest semantic version.
        """
        return self.latest_entry(
            model_name
        ).registration

    def latest_entry(
        self,
        model_name: str,
    ) -> ForecastModelVersionEntry:
        """
        Return the highest semantic version entry.

        Raises:
            ForecastRegistryError:
                If the model has no registered versions.
        """
        entries = self.list_version_entries(
            model_name
        )

        if not entries:
            raise ForecastRegistryError(
                "No registered versions were found for the model.",
                context={
                    "model_name": model_name,
                },
            )

        return entries[-1]

    def earliest_version(
        self,
        model_name: str,
    ) -> str:
        """
        Return the lowest registered semantic version.

        Raises:
            ForecastRegistryError:
                If the model has no registered versions.
        """
        return self.earliest_entry(
            model_name
        ).version.to_string()

    def earliest_registration(
        self,
        model_name: str,
    ) -> ForecastModelRegistration:
        """Return the registration with the lowest semantic version."""
        return self.earliest_entry(
            model_name
        ).registration

    def earliest_entry(
        self,
        model_name: str,
    ) -> ForecastModelVersionEntry:
        """
        Return the lowest semantic version entry.

        Raises:
            ForecastRegistryError:
                If the model has no registered versions.
        """
        entries = self.list_version_entries(
            model_name
        )

        if not entries:
            raise ForecastRegistryError(
                "No registered versions were found for the model.",
                context={
                    "model_name": model_name,
                },
            )

        return entries[0]

    def previous_version(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> str | None:
        """
        Return the immediately preceding registered version.

        ``None`` is returned when the requested version is the earliest
        registered version.

        Raises:
            ForecastRegistryError:
                If the requested version is not registered.
        """
        entry = self.previous_entry(
            model_name=model_name,
            model_version=model_version,
        )

        return (
            entry.version.to_string()
            if entry is not None
            else None
        )

    def previous_registration(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelRegistration | None:
        """
        Return the immediately preceding registration when available.
        """
        entry = self.previous_entry(
            model_name=model_name,
            model_version=model_version,
        )

        return (
            entry.registration
            if entry is not None
            else None
        )

    def previous_entry(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelVersionEntry | None:
        """
        Return the immediately preceding registered version entry.
        """
        entries, current_index = self._resolve_entry_index(
            model_name=model_name,
            model_version=model_version,
        )

        if current_index == 0:
            return None

        return entries[current_index - 1]

    def next_version(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> str | None:
        """
        Return the immediately following registered version.

        ``None`` is returned when the requested version is the latest
        registered version.

        Raises:
            ForecastRegistryError:
                If the requested version is not registered.
        """
        entry = self.next_entry(
            model_name=model_name,
            model_version=model_version,
        )

        return (
            entry.version.to_string()
            if entry is not None
            else None
        )

    def next_registration(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelRegistration | None:
        """
        Return the immediately following registration when available.
        """
        entry = self.next_entry(
            model_name=model_name,
            model_version=model_version,
        )

        return (
            entry.registration
            if entry is not None
            else None
        )

    def next_entry(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastModelVersionEntry | None:
        """
        Return the immediately following registered version entry.
        """
        entries, current_index = self._resolve_entry_index(
            model_name=model_name,
            model_version=model_version,
        )

        if current_index == len(entries) - 1:
            return None

        return entries[current_index + 1]

    def next_patch_version(
        self,
        model_name: str,
    ) -> str:
        """
        Calculate the next patch version from the latest registration.

        When the model has no registered versions, ``0.0.1`` is returned.
        """
        latest = self._latest_or_none(
            model_name
        )

        if latest is None:
            return "0.0.1"

        return latest.bump_patch().to_string()

    def next_minor_version(
        self,
        model_name: str,
    ) -> str:
        """
        Calculate the next minor version from the latest registration.

        When the model has no registered versions, ``0.1.0`` is returned.
        """
        latest = self._latest_or_none(
            model_name
        )

        if latest is None:
            return "0.1.0"

        return latest.bump_minor().to_string()

    def next_major_version(
        self,
        model_name: str,
    ) -> str:
        """
        Calculate the next major version from the latest registration.

        When the model has no registered versions, ``1.0.0`` is returned.
        """
        latest = self._latest_or_none(
            model_name
        )

        if latest is None:
            return "1.0.0"

        return latest.bump_major().to_string()

    def to_dict(
        self,
        model_name: str,
    ) -> dict[str, Any]:
        """
        Return a serialization-safe version inventory for one model.
        """
        normalized_model_name = self._validate_model_name(
            model_name
        )
        entries = self.list_version_entries(
            normalized_model_name
        )

        return {
            "model_name": normalized_model_name,
            "total_versions": len(entries),
            "is_empty": len(entries) == 0,
            "earliest_version": (
                entries[0].version.to_string()
                if entries
                else None
            ),
            "latest_version": (
                entries[-1].version.to_string()
                if entries
                else None
            ),
            "versions": [
                entry.to_dict()
                for entry in entries
            ],
        }

    def _resolve_entry_index(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> tuple[
        tuple[ForecastModelVersionEntry, ...],
        int,
    ]:
        """
        Resolve the ordered entries and index of a registered version.
        """
        normalized_model_name = self._validate_model_name(
            model_name
        )
        parsed_version = ForecastModelVersion.parse(
            model_version
        )

        entries = self.list_version_entries(
            normalized_model_name
        )

        for index, entry in enumerate(entries):
            if entry.version == parsed_version:
                return entries, index

        raise ForecastRegistryError(
            "Requested model version is not registered.",
            context={
                "model_name": normalized_model_name,
                "model_version": (
                    parsed_version.to_string()
                ),
                "registered_versions": tuple(
                    entry.version.to_string()
                    for entry in entries
                ),
            },
        )

    def _latest_or_none(
        self,
        model_name: str,
    ) -> ForecastModelVersion | None:
        """Return the latest parsed version when registrations exist."""
        entries = self.list_version_entries(
            model_name
        )

        if not entries:
            return None

        return entries[-1].version

    @staticmethod
    def _validate_model_name(
        model_name: Any,
    ) -> str:
        """Validate and normalize one model name."""
        if not isinstance(model_name, str):
            raise ForecastRegistryError(
                "model_name must be a string.",
                context={
                    "received_type": type(
                        model_name
                    ).__name__,
                },
            )

        normalized = model_name.strip()

        if not normalized:
            raise ForecastRegistryError(
                "model_name must not be empty."
            )

        return normalized


__all__ = [
    "EnterpriseModelVersioning",
    "ForecastModelVersion",
    "ForecastModelVersionEntry",
]