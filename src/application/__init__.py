"""
Implementation 25.8 — Enterprise Application Package

Public API for the Enterprise Application Layer.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

# ============================================================
# Constants
# ============================================================

from .constants import (
    APPLICATION_DOMAIN_NAME,
    APPLICATION_DOMAIN_VERSION,
    BOOTSTRAP_API,
    BOOTSTRAP_COMPLETE,
    BOOTSTRAP_CONFIGURATION,
    BOOTSTRAP_DEPENDENCIES,
    BOOTSTRAP_SEQUENCE,
    BOOTSTRAP_SERVICES,
    DEFAULT_CONFIGURATION_VERSION,
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_PRODUCTION,
    ENVIRONMENT_TEST,
    SERVICE_API,
    SERVICE_FORECAST,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
    SUPPORTED_ENVIRONMENTS,
    SUPPORTED_SERVICES,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    ApplicationBootstrapError,
    ApplicationConfigurationError,
    ApplicationContainerError,
    ApplicationDependencyError,
    ApplicationError,
    ApplicationFactoryError,
    ApplicationLifecycleError,
    ApplicationValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    ApplicationBootstrapResult,
    ApplicationContext,
    ApplicationDescriptor,
    ApplicationEnvironment,
    ApplicationStatus,
    BootstrapEvent,
    BootstrapStage,
    ServiceRegistration,
)

# ============================================================
# Configuration
# ============================================================

from .configuration import (
    ApplicationConfiguration,
    DEFAULT_APPLICATION_NAME,
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_REQUIRED_SERVICES,
)

# ============================================================
# Components
# ============================================================

from .bootstrap import EnterpriseApplicationBootstrap
from .container import (
    EnterpriseApplicationContainer,
    ServiceFactory,
)
from .factory import EnterpriseApplicationFactory


__all__ = [
    # Domain
    "APPLICATION_DOMAIN_NAME",
    "APPLICATION_DOMAIN_VERSION",
    "DEFAULT_CONFIGURATION_VERSION",

    # Environments
    "ENVIRONMENT_DEVELOPMENT",
    "ENVIRONMENT_TEST",
    "ENVIRONMENT_PRODUCTION",
    "SUPPORTED_ENVIRONMENTS",

    # Bootstrap stages
    "BOOTSTRAP_CONFIGURATION",
    "BOOTSTRAP_DEPENDENCIES",
    "BOOTSTRAP_SERVICES",
    "BOOTSTRAP_API",
    "BOOTSTRAP_COMPLETE",
    "BOOTSTRAP_SEQUENCE",

    # Services
    "SERVICE_FORECAST",
    "SERVICE_PLANNING",
    "SERVICE_OPTIMIZATION",
    "SERVICE_ORCHESTRATION",
    "SERVICE_REPORTING",
    "SERVICE_MONITORING",
    "SERVICE_API",
    "SUPPORTED_SERVICES",

    # Exceptions
    "ApplicationError",
    "ApplicationValidationError",
    "ApplicationConfigurationError",
    "ApplicationContainerError",
    "ApplicationDependencyError",
    "ApplicationFactoryError",
    "ApplicationBootstrapError",
    "ApplicationLifecycleError",

    # Models
    "ApplicationEnvironment",
    "BootstrapStage",
    "ApplicationStatus",
    "ServiceRegistration",
    "BootstrapEvent",
    "ApplicationDescriptor",
    "ApplicationBootstrapResult",
    "ApplicationContext",

    # Configuration
    "ApplicationConfiguration",
    "DEFAULT_APPLICATION_NAME",
    "DEFAULT_APPLICATION_VERSION",
    "DEFAULT_REQUIRED_SERVICES",

    # Components
    "ServiceFactory",
    "EnterpriseApplicationContainer",
    "EnterpriseApplicationFactory",
    "EnterpriseApplicationBootstrap",
]