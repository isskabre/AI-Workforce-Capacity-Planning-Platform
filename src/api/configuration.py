"""
Implementation 24.4 — Enterprise API Configuration

Enterprise configuration for the transport-neutral API layer.

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import APIConfigurationError


@dataclass(frozen=True, slots=True)
class APIConfiguration:
    """
    Enterprise API configuration.
    """

    api_version: str = "v1"

    base_path: str = "/api"

    default_content_type: str = "application/json"

    request_timeout_seconds: int = 30

    maximum_payload_size_bytes: int = 10_000_000

    enable_health_endpoint: bool = True

    enable_platform_health_endpoint: bool = True

    enable_decision_endpoint: bool = True

    enable_decision_report_endpoint: bool = True

    enable_monitoring_endpoint: bool = True

    validate_requests: bool = True

    generate_metadata: bool = True

    configuration_version: str = "1.0.0"

    def __post_init__(self) -> None:

        if not self.api_version.strip():
            raise APIConfigurationError(
                "api_version cannot be empty."
            )

        if not self.base_path.strip():
            raise APIConfigurationError(
                "base_path cannot be empty."
            )

        if not self.default_content_type.strip():
            raise APIConfigurationError(
                "default_content_type cannot be empty."
            )

        if self.request_timeout_seconds <= 0:
            raise APIConfigurationError(
                "request_timeout_seconds must be positive."
            )

        if self.maximum_payload_size_bytes <= 0:
            raise APIConfigurationError(
                "maximum_payload_size_bytes must be positive."
            )

        if not (
            self.enable_health_endpoint
            or self.enable_platform_health_endpoint
            or self.enable_decision_endpoint
            or self.enable_decision_report_endpoint
            or self.enable_monitoring_endpoint
        ):
            raise APIConfigurationError(
                "At least one endpoint must be enabled."
            )

        if not self.configuration_version.strip():
            raise APIConfigurationError(
                "configuration_version cannot be empty."
            )


__all__ = [
    "APIConfiguration",
]