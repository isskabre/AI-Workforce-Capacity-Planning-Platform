"""
Implementation 25.4 — Enterprise Application Configuration

Validated root configuration for the Enterprise Application Layer.

This module coordinates application identity, runtime environment,
service-registration policy, bootstrap behavior, and the configuration
objects required by the API, reporting, and monitoring layers.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from src.api.configuration import APIConfiguration
from src.monitoring.configuration import MonitoringConfiguration
from src.reporting.configuration import ReportingConfiguration

from .constants import (
    APPLICATION_DOMAIN_VERSION,
    DEFAULT_CONFIGURATION_VERSION,
    ENVIRONMENT_DEVELOPMENT,
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
    SUPPORTED_ENVIRONMENTS,
    SUPPORTED_SERVICES,
)
from .exceptions import ApplicationConfigurationError
from .models import ApplicationEnvironment


DEFAULT_APPLICATION_NAME = (
    "AI Workforce Capacity Planning Platform"
)

DEFAULT_APPLICATION_VERSION = "3.0.0"

DEFAULT_REQUIRED_SERVICES = (
    SERVICE_PLANNING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_REPORTING,
    SERVICE_MONITORING,
    SERVICE_API,
)


@dataclass(frozen=True, slots=True)
class ApplicationConfiguration:
    """
    Root enterprise application configuration.

    Parameters
    ----------
    application_name:
        Stable application identity.

    application_version:
        Semantic application release version.

    environment:
        Active application runtime environment.

    required_services:
        Services that must be constructed and registered during
        application bootstrap.

    api:
        Enterprise API configuration.

    reporting:
        Enterprise reporting configuration.

    monitoring:
        Enterprise monitoring configuration.

    fail_fast:
        Whether bootstrap should stop immediately when a stage fails.

    validate_dependencies:
        Whether service dependency consistency should be validated.

    enable_bootstrap_events:
        Whether bootstrap-stage events should be retained.

    allow_service_replacement:
        Whether dependency registrations may be replaced.

    configuration_version:
        Semantic version of this root configuration contract.

    metadata:
        Optional environment or deployment metadata.
    """

    application_name: str = DEFAULT_APPLICATION_NAME

    application_version: str = DEFAULT_APPLICATION_VERSION

    environment: ApplicationEnvironment = (
        ApplicationEnvironment.DEVELOPMENT
    )

    required_services: tuple[str, ...] = (
        DEFAULT_REQUIRED_SERVICES
    )

    api: APIConfiguration = field(
        default_factory=APIConfiguration
    )

    reporting: ReportingConfiguration = field(
        default_factory=ReportingConfiguration
    )

    monitoring: MonitoringConfiguration = field(
        default_factory=MonitoringConfiguration
    )

    fail_fast: bool = True

    validate_dependencies: bool = True

    enable_bootstrap_events: bool = True

    allow_service_replacement: bool = False

    configuration_version: str = (
        DEFAULT_CONFIGURATION_VERSION
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the complete application configuration.
        """

        self._validate_non_empty_string(
            name="application_name",
            value=self.application_name,
        )

        self._validate_non_empty_string(
            name="application_version",
            value=self.application_version,
        )

        if not isinstance(
            self.environment,
            ApplicationEnvironment,
        ):
            raise ApplicationConfigurationError(
                "environment must be an ApplicationEnvironment."
            )

        if self.environment.value not in SUPPORTED_ENVIRONMENTS:
            raise ApplicationConfigurationError(
                "Unsupported application environment."
            )

        if not isinstance(self.required_services, tuple):
            raise ApplicationConfigurationError(
                "required_services must be a tuple."
            )

        if not self.required_services:
            raise ApplicationConfigurationError(
                "required_services must not be empty."
            )

        if len(self.required_services) != len(
            set(self.required_services)
        ):
            raise ApplicationConfigurationError(
                "required_services must not contain duplicates."
            )

        for service_name in self.required_services:
            if service_name not in SUPPORTED_SERVICES:
                raise ApplicationConfigurationError(
                    f"Unsupported required service: "
                    f"{service_name}."
                )

        if not isinstance(self.api, APIConfiguration):
            raise ApplicationConfigurationError(
                "api must be an APIConfiguration."
            )

        if not isinstance(
            self.reporting,
            ReportingConfiguration,
        ):
            raise ApplicationConfigurationError(
                "reporting must be a ReportingConfiguration."
            )

        if not isinstance(
            self.monitoring,
            MonitoringConfiguration,
        ):
            raise ApplicationConfigurationError(
                "monitoring must be a MonitoringConfiguration."
            )

        boolean_fields = {
            "fail_fast": self.fail_fast,
            "validate_dependencies": (
                self.validate_dependencies
            ),
            "enable_bootstrap_events": (
                self.enable_bootstrap_events
            ),
            "allow_service_replacement": (
                self.allow_service_replacement
            ),
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise ApplicationConfigurationError(
                    f"{field_name} must be a boolean."
                )

        self._validate_non_empty_string(
            name="configuration_version",
            value=self.configuration_version,
        )

        if not isinstance(self.metadata, Mapping):
            raise ApplicationConfigurationError(
                "metadata must be a mapping."
            )

        if self.validate_dependencies:
            self._validate_service_dependencies()

    def _validate_service_dependencies(self) -> None:
        """
        Validate required-service dependency relationships.
        """

        service_set = set(self.required_services)

        dependency_rules = {
            SERVICE_API: {
                SERVICE_ORCHESTRATION,
                SERVICE_REPORTING,
                SERVICE_MONITORING,
            },
            SERVICE_REPORTING: {
                SERVICE_ORCHESTRATION,
            },
            SERVICE_ORCHESTRATION: {
                SERVICE_PLANNING,
                SERVICE_OPTIMIZATION,
            },
        }

        for service_name, dependencies in (
            dependency_rules.items()
        ):
            if service_name not in service_set:
                continue

            missing_dependencies = tuple(
                sorted(
                    dependency
                    for dependency in dependencies
                    if dependency not in service_set
                )
            )

            if missing_dependencies:
                raise ApplicationConfigurationError(
                    f"Service '{service_name}' requires: "
                    f"{', '.join(missing_dependencies)}."
                )

    @staticmethod
    def _validate_non_empty_string(
        *,
        name: str,
        value: Any,
    ) -> None:
        """
        Validate a required non-empty string field.
        """

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ApplicationConfigurationError(
                f"{name} must be a non-empty string."
            )

    @property
    def environment_name(self) -> str:
        """
        Return the active environment as a string.
        """

        return self.environment.value

    @property
    def is_development(self) -> bool:
        """
        Return whether the application runs in development.
        """

        return (
            self.environment
            is ApplicationEnvironment.DEVELOPMENT
        )

    @property
    def is_test(self) -> bool:
        """
        Return whether the application runs in test.
        """

        return (
            self.environment
            is ApplicationEnvironment.TEST
        )

    @property
    def is_production(self) -> bool:
        """
        Return whether the application runs in production.
        """

        return (
            self.environment
            is ApplicationEnvironment.PRODUCTION
        )

    def requires_service(
        self,
        *,
        name: str,
    ) -> bool:
        """
        Return whether a service is required.
        """

        if name not in SUPPORTED_SERVICES:
            raise ApplicationConfigurationError(
                f"Unsupported service: {name}."
            )

        return name in self.required_services

    def as_dict(self) -> dict[str, Any]:
        """
        Return a serializable configuration representation.
        """

        return {
            "application_name": self.application_name,
            "application_version": self.application_version,
            "environment": self.environment.value,
            "required_services": list(
                self.required_services
            ),
            "api": {
                "api_version": self.api.api_version,
                "base_path": self.api.base_path,
                "default_content_type": (
                    self.api.default_content_type
                ),
                "request_timeout_seconds": (
                    self.api.request_timeout_seconds
                ),
                "maximum_payload_size_bytes": (
                    self.api.maximum_payload_size_bytes
                ),
                "enable_health_endpoint": (
                    self.api.enable_health_endpoint
                ),
                "enable_platform_health_endpoint": (
                    self.api
                    .enable_platform_health_endpoint
                ),
                "enable_decision_endpoint": (
                    self.api.enable_decision_endpoint
                ),
                "enable_decision_report_endpoint": (
                    self.api
                    .enable_decision_report_endpoint
                ),
                "enable_monitoring_endpoint": (
                    self.api.enable_monitoring_endpoint
                ),
                "validate_requests": (
                    self.api.validate_requests
                ),
                "generate_metadata": (
                    self.api.generate_metadata
                ),
                "configuration_version": (
                    self.api.configuration_version
                ),
            },
            "reporting": self.reporting.as_dict(),
            "monitoring": self.monitoring.as_dict(),
            "fail_fast": self.fail_fast,
            "validate_dependencies": (
                self.validate_dependencies
            ),
            "enable_bootstrap_events": (
                self.enable_bootstrap_events
            ),
            "allow_service_replacement": (
                self.allow_service_replacement
            ),
            "configuration_version": (
                self.configuration_version
            ),
            "application_domain_version": (
                APPLICATION_DOMAIN_VERSION
            ),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "ApplicationConfiguration",
    "DEFAULT_APPLICATION_NAME",
    "DEFAULT_APPLICATION_VERSION",
    "DEFAULT_REQUIRED_SERVICES",
]