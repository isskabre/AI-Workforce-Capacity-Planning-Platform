"""
AI Workforce Capacity Planning Platform
Implementation 16 - Enterprise Model Registry Framework

Module:
    forecast.model_registry.promotion

Description:
    Provides immutable lifecycle records and enterprise model-promotion
    operations for registered forecasting-model artifacts.

    ForecastModelRegistration remains immutable. Lifecycle state is managed
    independently through append-only promotion records maintained by this
    service.

Architecture:
    Enterprise Model Registry Framework

Version:
    2.8.0
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from threading import RLock
from typing import Any
from uuid import uuid4

from src.forecast.model_registry.registry import (
    EnterpriseModelRegistry,
    ForecastModelRegistration,
)
from src.forecast.model_registry.versioning import (
    EnterpriseModelVersioning,
)
from src.forecast.modeling.artifacts import (
    ForecastArtifactStatus,
)
from src.forecast.modeling.exceptions import (
    ForecastRegistryError,
)


class ForecastLifecycleState(StrEnum):
    """Supported enterprise model lifecycle states."""

    REGISTERED = "REGISTERED"
    STAGING = "STAGING"
    CHAMPION = "CHAMPION"
    ARCHIVED = "ARCHIVED"
    RETIRED = "RETIRED"


class ForecastPromotionAction(StrEnum):
    """Supported enterprise model lifecycle actions."""

    PROMOTE_TO_STAGING = "PROMOTE_TO_STAGING"
    PROMOTE_TO_CHAMPION = "PROMOTE_TO_CHAMPION"
    ARCHIVE = "ARCHIVE"
    RETIRE = "RETIRE"
    ROLLBACK_TO_CHAMPION = "ROLLBACK_TO_CHAMPION"


_VALID_TRANSITIONS: dict[
    tuple[ForecastLifecycleState, ForecastPromotionAction],
    ForecastLifecycleState,
] = {
    (
        ForecastLifecycleState.REGISTERED,
        ForecastPromotionAction.PROMOTE_TO_STAGING,
    ): ForecastLifecycleState.STAGING,
    (
        ForecastLifecycleState.STAGING,
        ForecastPromotionAction.PROMOTE_TO_CHAMPION,
    ): ForecastLifecycleState.CHAMPION,
    (
        ForecastLifecycleState.STAGING,
        ForecastPromotionAction.ARCHIVE,
    ): ForecastLifecycleState.ARCHIVED,
    (
        ForecastLifecycleState.CHAMPION,
        ForecastPromotionAction.ARCHIVE,
    ): ForecastLifecycleState.ARCHIVED,
    (
        ForecastLifecycleState.ARCHIVED,
        ForecastPromotionAction.RETIRE,
    ): ForecastLifecycleState.RETIRED,
    (
        ForecastLifecycleState.ARCHIVED,
        ForecastPromotionAction.ROLLBACK_TO_CHAMPION,
    ): ForecastLifecycleState.CHAMPION,
}


@dataclass(frozen=True, slots=True)
class ForecastPromotionRecord:
    """
    Immutable audit record for one model lifecycle transition.

    Attributes:
        model_name:
            Stable registered model name.

        model_version:
            Registered model version.

        action:
            Lifecycle action performed.

        previous_state:
            Lifecycle state before the transition.

        new_state:
            Lifecycle state after the transition.

        promotion_id:
            Unique lifecycle-event identifier.

        promoted_at:
            UTC timestamp when the transition completed.

        performed_by:
            Optional user, service, or process identifier.

        reason:
            Optional human-readable transition reason.

        metadata:
            Additional serializable lifecycle metadata.
    """

    model_name: str
    model_version: str
    action: ForecastPromotionAction
    previous_state: ForecastLifecycleState
    new_state: ForecastLifecycleState
    promotion_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    promoted_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    performed_by: str | None = None
    reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        model_name = self._validate_required_string(
            self.model_name,
            field_name="model_name",
        )
        model_version = self._validate_required_string(
            self.model_version,
            field_name="model_version",
        )
        promotion_id = self._validate_required_string(
            self.promotion_id,
            field_name="promotion_id",
        )

        if not isinstance(
            self.action,
            ForecastPromotionAction,
        ):
            raise ForecastRegistryError(
                "Promotion action is invalid.",
                context={
                    "received_type": type(
                        self.action
                    ).__name__,
                },
            )

        if not isinstance(
            self.previous_state,
            ForecastLifecycleState,
        ):
            raise ForecastRegistryError(
                "Promotion previous_state is invalid.",
                context={
                    "received_type": type(
                        self.previous_state
                    ).__name__,
                },
            )

        if not isinstance(
            self.new_state,
            ForecastLifecycleState,
        ):
            raise ForecastRegistryError(
                "Promotion new_state is invalid.",
                context={
                    "received_type": type(
                        self.new_state
                    ).__name__,
                },
            )

        expected_state = _VALID_TRANSITIONS.get(
            (
                self.previous_state,
                self.action,
            )
        )

        if expected_state != self.new_state:
            raise ForecastRegistryError(
                "Promotion record contains an invalid lifecycle transition.",
                context={
                    "action": self.action.value,
                    "previous_state": self.previous_state.value,
                    "new_state": self.new_state.value,
                },
            )

        self._validate_timezone_aware_datetime(
            self.promoted_at,
            field_name="promoted_at",
        )

        if not isinstance(self.metadata, Mapping):
            raise ForecastRegistryError(
                "Promotion metadata must be a mapping.",
                context={
                    "received_type": type(
                        self.metadata
                    ).__name__,
                },
            )

        object.__setattr__(
            self,
            "model_name",
            model_name,
        )
        object.__setattr__(
            self,
            "model_version",
            model_version,
        )
        object.__setattr__(
            self,
            "promotion_id",
            promotion_id,
        )
        object.__setattr__(
            self,
            "performed_by",
            self._normalize_optional_string(
                self.performed_by,
                field_name="performed_by",
            ),
        )
        object.__setattr__(
            self,
            "reason",
            self._normalize_optional_string(
                self.reason,
                field_name="reason",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def model_identity(self) -> str:
        """Return the stable model identity."""
        return f"{self.model_name}:{self.model_version}"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe promotion record."""
        return {
            "promotion_id": self.promotion_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_identity": self.model_identity,
            "action": self.action.value,
            "previous_state": self.previous_state.value,
            "new_state": self.new_state.value,
            "promoted_at": self.promoted_at.isoformat(),
            "performed_by": self.performed_by,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def _validate_required_string(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ForecastRegistryError(
                f"{field_name} must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = value.strip()

        if not normalized:
            raise ForecastRegistryError(
                f"{field_name} must not be empty."
            )

        return normalized

    @classmethod
    def _normalize_optional_string(
        cls,
        value: Any,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None

        return cls._validate_required_string(
            value,
            field_name=field_name,
        )

    @staticmethod
    def _validate_timezone_aware_datetime(
        value: Any,
        *,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise ForecastRegistryError(
                f"{field_name} must be a datetime.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ForecastRegistryError(
                f"{field_name} must be timezone-aware."
            )


@dataclass(frozen=True, slots=True)
class ForecastPromotionResult:
    """
    Immutable result returned by one lifecycle operation.

    Attributes:
        record:
            Immutable lifecycle-transition record.

        registration:
            Immutable registry registration affected by the transition.

        current_state:
            Lifecycle state after the operation.

        success:
            Whether the operation completed successfully.

        message:
            Human-readable operation summary.
    """

    record: ForecastPromotionRecord
    registration: ForecastModelRegistration
    current_state: ForecastLifecycleState
    success: bool = True
    message: str = ""

    def __post_init__(self) -> None:
        if not isinstance(
            self.record,
            ForecastPromotionRecord,
        ):
            raise ForecastRegistryError(
                "Promotion result record must be a "
                "ForecastPromotionRecord."
            )

        if not isinstance(
            self.registration,
            ForecastModelRegistration,
        ):
            raise ForecastRegistryError(
                "Promotion result registration must be a "
                "ForecastModelRegistration."
            )

        if not isinstance(
            self.current_state,
            ForecastLifecycleState,
        ):
            raise ForecastRegistryError(
                "Promotion result current_state is invalid."
            )

        if not isinstance(self.success, bool):
            raise ForecastRegistryError(
                "Promotion result success must be a boolean."
            )

        if not isinstance(self.message, str):
            raise ForecastRegistryError(
                "Promotion result message must be a string."
            )

        if (
            self.record.model_name
            != self.registration.model_name
            or self.record.model_version
            != self.registration.model_version
        ):
            raise ForecastRegistryError(
                "Promotion result record and registration identities "
                "do not match."
            )

        if self.current_state != self.record.new_state:
            raise ForecastRegistryError(
                "Promotion result current_state does not match the "
                "promotion record."
            )

        object.__setattr__(
            self,
            "message",
            self.message.strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe promotion result."""
        return {
            "success": self.success,
            "message": self.message,
            "current_state": self.current_state.value,
            "record": self.record.to_dict(),
            "registration": self.registration.to_dict(),
        }


class EnterpriseModelPromotionService:
    """
    Manage model lifecycle transitions without mutating registrations.

    Lifecycle history is maintained as append-only immutable records within
    this service instance. Registry registrations remain unchanged.

    The service enforces:

    - valid state transitions;
    - registration existence;
    - one champion per normalized model family;
    - deterministic promotion history;
    - rollback only to an eligible archived version.
    """

    def __init__(
        self,
        *,
        registry: EnterpriseModelRegistry,
        versioning: EnterpriseModelVersioning | None = None,
    ) -> None:
        """
        Initialize the promotion service.

        Args:
            registry:
                Registry containing immutable model registrations.

            versioning:
                Optional semantic-version service. A default service is
                created from ``registry`` when omitted.
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

        if versioning is not None and not isinstance(
            versioning,
            EnterpriseModelVersioning,
        ):
            raise ForecastRegistryError(
                "versioning must be an EnterpriseModelVersioning.",
                context={
                    "received_type": type(
                        versioning
                    ).__name__,
                },
            )

        resolved_versioning = (
            versioning
            if versioning is not None
            else EnterpriseModelVersioning(
                registry=registry
            )
        )

        if resolved_versioning.registry is not registry:
            raise ForecastRegistryError(
                "Promotion service registry and versioning registry "
                "must be the same instance."
            )

        self._registry = registry
        self._versioning = resolved_versioning
        self._history: dict[
            tuple[str, str],
            list[ForecastPromotionRecord],
        ] = {}
        self._lock = RLock()

    @property
    def registry(self) -> EnterpriseModelRegistry:
        """Return the associated model registry."""
        return self._registry

    @property
    def versioning(self) -> EnterpriseModelVersioning:
        """Return the associated versioning service."""
        return self._versioning

    def current_state(
        self,
        *,
        model_name: str,
        model_version: str,
    ) -> ForecastLifecycleState:
        """
        Return the current lifecycle state for one registered model version.
        """
        registration = self._registry.get(
            model_name=model_name,
            model_version=model_version,
        )

        key = self._build_key(
            registration.model_name,
            registration.model_version,
        )

        with self._lock:
            records = tuple(
                self._history.get(
                    key,
                    (),
                )
            )

        if records:
            return records[-1].new_state

        return self._initial_state(registration)

    def promote_to_staging(
        self,
        *,
        model_name: str,
        model_version: str,
        performed_by: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastPromotionResult:
        """Promote a registered model version to staging."""
        return self._transition(
            model_name=model_name,
            model_version=model_version,
            action=ForecastPromotionAction.PROMOTE_TO_STAGING,
            performed_by=performed_by,
            reason=reason,
            metadata=metadata,
        )

    def promote_to_champion(
        self,
        *,
        model_name: str,
        model_version: str,
        performed_by: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastPromotionResult:
        """
        Promote a staged model version to champion.

        A model family may contain at most one champion.
        """
        registration = self._registry.get(
            model_name=model_name,
            model_version=model_version,
        )

        existing_champion = self.current_champion(
            registration.model_name
        )

        if (
            existing_champion is not None
            and existing_champion.model_version
            != registration.model_version
        ):
            raise ForecastRegistryError(
                "Model family already has a champion version.",
                context={
                    "model_name": registration.model_name,
                    "champion_version": (
                        existing_champion.model_version
                    ),
                    "requested_version": (
                        registration.model_version
                    ),
                },
            )

        return self._transition(
            model_name=registration.model_name,
            model_version=registration.model_version,
            action=ForecastPromotionAction.PROMOTE_TO_CHAMPION,
            performed_by=performed_by,
            reason=reason,
            metadata=metadata,
        )

    def archive(
        self,
        *,
        model_name: str,
        model_version: str,
        performed_by: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastPromotionResult:
        """Archive a staged or champion model version."""
        return self._transition(
            model_name=model_name,
            model_version=model_version,
            action=ForecastPromotionAction.ARCHIVE,
            performed_by=performed_by,
            reason=reason,
            metadata=metadata,
        )

    def retire(
        self,
        *,
        model_name: str,
        model_version: str,
        performed_by: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastPromotionResult:
        """Retire an archived model version."""
        return self._transition(
            model_name=model_name,
            model_version=model_version,
            action=ForecastPromotionAction.RETIRE,
            performed_by=performed_by,
            reason=reason,
            metadata=metadata,
        )

    def rollback_champion(
        self,
        *,
        model_name: str,
        performed_by: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastPromotionResult:
        """
        Roll back to the nearest lower archived semantic version.

        The current champion is archived first. The previous eligible archived
        version is then restored as champion.
        """
        champion = self.current_champion(
            model_name
        )

        if champion is None:
            raise ForecastRegistryError(
                "Model family does not have a champion to roll back.",
                context={
                    "model_name": model_name,
                },
            )

        rollback_candidate = self._find_rollback_candidate(
            champion
        )

        if rollback_candidate is None:
            raise ForecastRegistryError(
                "No archived previous version is available for rollback.",
                context={
                    "model_name": champion.model_name,
                    "champion_version": champion.model_version,
                },
            )

        rollback_metadata = dict(metadata or {})

        rollback_metadata.update(
            {
                "rollback_from_version": (
                    champion.model_version
                ),
                "rollback_to_version": (
                    rollback_candidate.model_version
                ),
            }
        )

        self.archive(
            model_name=champion.model_name,
            model_version=champion.model_version,
            performed_by=performed_by,
            reason=(
                reason
                or "Archived current champion during rollback."
            ),
            metadata=rollback_metadata,
        )

        return self._transition(
            model_name=rollback_candidate.model_name,
            model_version=rollback_candidate.model_version,
            action=(
                ForecastPromotionAction.ROLLBACK_TO_CHAMPION
            ),
            performed_by=performed_by,
            reason=(
                reason
                or "Restored previous archived version as champion."
            ),
            metadata=rollback_metadata,
        )

    def current_champion(
        self,
        model_name: str,
    ) -> ForecastModelRegistration | None:
        """
        Return the current champion registration for one model family.
        """
        normalized_name = self._normalize_identity(
            model_name,
            field_name="model_name",
        )

        champions = tuple(
            registration
            for registration
            in self._registry.list_versions(
                normalized_name
            )
            if self.current_state(
                model_name=registration.model_name,
                model_version=registration.model_version,
            )
            == ForecastLifecycleState.CHAMPION
        )

        if len(champions) > 1:
            raise ForecastRegistryError(
                "Model family contains multiple champion versions.",
                context={
                    "model_name": normalized_name,
                    "champion_versions": tuple(
                        registration.model_version
                        for registration in champions
                    ),
                },
            )

        return champions[0] if champions else None

    def promotion_history(
        self,
        *,
        model_name: str,
        model_version: str | None = None,
    ) -> tuple[ForecastPromotionRecord, ...]:
        """
        Return lifecycle history for a model family or specific version.
        """
        normalized_name = self._normalize_identity(
            model_name,
            field_name="model_name",
        )

        if model_version is not None:
            registration = self._registry.get(
                model_name=normalized_name,
                model_version=model_version,
            )

            key = self._build_key(
                registration.model_name,
                registration.model_version,
            )

            with self._lock:
                return tuple(
                    self._history.get(
                        key,
                        (),
                    )
                )

        self._registry.list_versions(
            normalized_name
        )

        with self._lock:
            records = tuple(
                record
                for key, history
                in self._history.items()
                if key[0] == normalized_name.lower()
                for record in history
            )

        return tuple(
            sorted(
                records,
                key=lambda record: (
                    record.promoted_at,
                    record.promotion_id,
                ),
            )
        )

    def to_dict(
        self,
        *,
        model_name: str,
    ) -> dict[str, Any]:
        """Return a serialization-safe lifecycle inventory."""
        registrations = self._registry.list_versions(
            model_name
        )

        champion = self.current_champion(
            model_name
        )

        return {
            "model_name": model_name.strip(),
            "total_versions": len(registrations),
            "champion_version": (
                champion.model_version
                if champion is not None
                else None
            ),
            "versions": [
                {
                    "model_version": registration.model_version,
                    "current_state": self.current_state(
                        model_name=registration.model_name,
                        model_version=registration.model_version,
                    ).value,
                    "history": [
                        record.to_dict()
                        for record in self.promotion_history(
                            model_name=registration.model_name,
                            model_version=registration.model_version,
                        )
                    ],
                }
                for registration in registrations
            ],
        }

    def _transition(
        self,
        *,
        model_name: str,
        model_version: str,
        action: ForecastPromotionAction,
        performed_by: str | None,
        reason: str | None,
        metadata: Mapping[str, Any] | None,
    ) -> ForecastPromotionResult:
        """Execute and record one validated lifecycle transition."""
        registration = self._registry.get(
            model_name=model_name,
            model_version=model_version,
        )

        if not isinstance(action, ForecastPromotionAction):
            raise ForecastRegistryError(
                "Lifecycle action is invalid."
            )

        if metadata is not None and not isinstance(
            metadata,
            Mapping,
        ):
            raise ForecastRegistryError(
                "Promotion metadata must be a mapping.",
                context={
                    "received_type": type(
                        metadata
                    ).__name__,
                },
            )

        previous_state = self.current_state(
            model_name=registration.model_name,
            model_version=registration.model_version,
        )

        new_state = _VALID_TRANSITIONS.get(
            (
                previous_state,
                action,
            )
        )

        if new_state is None:
            raise ForecastRegistryError(
                "Invalid model lifecycle transition.",
                context={
                    "model_name": registration.model_name,
                    "model_version": registration.model_version,
                    "action": action.value,
                    "current_state": previous_state.value,
                },
            )

        record = ForecastPromotionRecord(
            model_name=registration.model_name,
            model_version=registration.model_version,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            performed_by=performed_by,
            reason=reason,
            metadata=dict(metadata or {}),
        )

        key = self._build_key(
            registration.model_name,
            registration.model_version,
        )

        with self._lock:
            self._history.setdefault(
                key,
                [],
            ).append(record)

        return ForecastPromotionResult(
            record=record,
            registration=registration,
            current_state=new_state,
            success=True,
            message=(
                f"Model {registration.model_name}:"
                f"{registration.model_version} transitioned from "
                f"{previous_state.value} to {new_state.value}."
            ),
        )

    def _find_rollback_candidate(
        self,
        champion: ForecastModelRegistration,
    ) -> ForecastModelRegistration | None:
        """Return the nearest lower archived semantic version."""
        candidate = self._versioning.previous_registration(
            model_name=champion.model_name,
            model_version=champion.model_version,
        )

        while candidate is not None:
            state = self.current_state(
                model_name=candidate.model_name,
                model_version=candidate.model_version,
            )

            if state == ForecastLifecycleState.ARCHIVED:
                return candidate

            candidate = self._versioning.previous_registration(
                model_name=candidate.model_name,
                model_version=candidate.model_version,
            )

        return None

    @staticmethod
    def _initial_state(
        registration: ForecastModelRegistration,
    ) -> ForecastLifecycleState:
        """Resolve initial lifecycle state from registered artifact metadata."""
        if (
            registration.artifact_status
            == ForecastArtifactStatus.CHAMPION
        ):
            return ForecastLifecycleState.CHAMPION

        if (
            registration.artifact_status
            == ForecastArtifactStatus.ARCHIVED
        ):
            return ForecastLifecycleState.ARCHIVED

        return ForecastLifecycleState.REGISTERED

    @staticmethod
    def _build_key(
        model_name: str,
        model_version: str,
    ) -> tuple[str, str]:
        return (
            model_name.strip().lower(),
            model_version.strip().lower(),
        )

    @staticmethod
    def _normalize_identity(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ForecastRegistryError(
                f"{field_name} must be a string.",
                context={
                    "received_type": type(value).__name__,
                },
            )

        normalized = value.strip()

        if not normalized:
            raise ForecastRegistryError(
                f"{field_name} must not be empty."
            )

        return normalized


__all__ = [
    "EnterpriseModelPromotionService",
    "ForecastLifecycleState",
    "ForecastPromotionAction",
    "ForecastPromotionRecord",
    "ForecastPromotionResult",
]