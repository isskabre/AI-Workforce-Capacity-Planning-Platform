"""
Implementation 24.5 — Enterprise API Mapper

Framework-neutral mapping utilities for the Enterprise API.

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .exceptions import APIMapperError
from .models import (
    APIHealthResponse,
    APIRequest,
    APIResponse,
)


class EnterpriseAPIMapper:
    """
    Converts Enterprise platform objects to API contracts.
    """

    def request_payload(
        self,
        request: APIRequest,
    ) -> Mapping[str, Any]:

        if not isinstance(request, APIRequest):
            raise APIMapperError(
                "Expected APIRequest."
            )

        return dict(request.payload)

    def response_payload(
        self,
        response: APIResponse,
    ) -> Mapping[str, Any]:

        if not isinstance(response, APIResponse):
            raise APIMapperError(
                "Expected APIResponse."
            )

        return dict(response.payload)

    def response_metadata(
        self,
        response: APIResponse,
    ) -> Mapping[str, Any]:

        if not isinstance(response, APIResponse):
            raise APIMapperError(
                "Expected APIResponse."
            )

        return asdict(response.metadata)

    def health_payload(
        self,
        response: APIHealthResponse,
    ) -> Mapping[str, Any]:

        if not isinstance(
            response,
            APIHealthResponse,
        ):
            raise APIMapperError(
                "Expected APIHealthResponse."
            )

        return {
            "healthy": response.healthy,
            "status": response.status,
            "components": dict(response.components),
            "checked_at_utc": response.checked_at_utc,
        }


__all__ = [
    "EnterpriseAPIMapper",
]