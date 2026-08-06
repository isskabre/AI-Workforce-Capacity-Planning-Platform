"""
Implementation 24.3 — Enterprise API Models

Enterprise transport-neutral API models.

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from .exceptions import APIValidationError


@dataclass(frozen=True, slots=True)
class APIRequestMetadata:
    """
    Request metadata.
    """

    request_id: str
    correlation_id: str
    source: str
    received_at_utc: datetime

    def __post_init__(self) -> None:

        if not self.request_id.strip():
            raise APIValidationError(
                "request_id cannot be empty."
            )

        if not self.correlation_id.strip():
            raise APIValidationError(
                "correlation_id cannot be empty."
            )

        if not self.source.strip():
            raise APIValidationError(
                "source cannot be empty."
            )


@dataclass(frozen=True, slots=True)
class APIResponseMetadata:
    """
    Response metadata.
    """

    request_id: str
    correlation_id: str
    generated_at_utc: datetime
    processing_time_ms: float

    def __post_init__(self) -> None:

        if not self.request_id.strip():
            raise APIValidationError(
                "request_id cannot be empty."
            )

        if not self.correlation_id.strip():
            raise APIValidationError(
                "correlation_id cannot be empty."
            )

        if self.processing_time_ms < 0.0:
            raise APIValidationError(
                "processing_time_ms cannot be negative."
            )


@dataclass(frozen=True, slots=True)
class APIRequest:
    """
    Generic API request.
    """

    operation: str
    payload: Mapping[str, Any]
    metadata: APIRequestMetadata

    def __post_init__(self) -> None:

        if not self.operation.strip():
            raise APIValidationError(
                "operation cannot be empty."
            )


@dataclass(frozen=True, slots=True)
class APIResponse:
    """
    Generic API response.
    """

    status: str
    http_status: int
    payload: Mapping[str, Any]
    metadata: APIResponseMetadata

    def __post_init__(self) -> None:

        if not self.status.strip():
            raise APIValidationError(
                "status cannot be empty."
            )

        if self.http_status < 100:
            raise APIValidationError(
                "Invalid HTTP status."
            )


@dataclass(frozen=True, slots=True)
class APIHealthResponse:
    """
    Health endpoint response.
    """

    healthy: bool
    status: str
    components: Mapping[str, Any]
    checked_at_utc: datetime


@dataclass(frozen=True, slots=True)
class APIRouteDefinition:
    """
    Internal API route definition.
    """

    name: str
    path: str
    method: str
    operation: str

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        if not self.name.strip():
            raise APIValidationError(
                "Route name cannot be empty."
            )

        if not self.path.strip():
            raise APIValidationError(
                "Route path cannot be empty."
            )

        if not self.method.strip():
            raise APIValidationError(
                "Route method cannot be empty."
            )

        if not self.operation.strip():
            raise APIValidationError(
                "Operation cannot be empty."
            )


__all__ = [
    "APIRequestMetadata",
    "APIResponseMetadata",
    "APIRequest",
    "APIResponse",
    "APIHealthResponse",
    "APIRouteDefinition",
]