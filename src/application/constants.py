"""
Implementation 25.1 — Enterprise Application Constants

Enterprise application lifecycle constants used by the application
bootstrap, dependency injection container, and service factory.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

# ============================================================
# Domain
# ============================================================

APPLICATION_DOMAIN_NAME = "application"
APPLICATION_DOMAIN_VERSION = "1.0.0"

# ============================================================
# Environments
# ============================================================

ENVIRONMENT_DEVELOPMENT = "development"
ENVIRONMENT_TEST = "test"
ENVIRONMENT_PRODUCTION = "production"

SUPPORTED_ENVIRONMENTS = (
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_TEST,
    ENVIRONMENT_PRODUCTION,
)

# ============================================================
# Bootstrap Stages
# ============================================================

BOOTSTRAP_CONFIGURATION = "configuration"
BOOTSTRAP_DEPENDENCIES = "dependencies"
BOOTSTRAP_SERVICES = "services"
BOOTSTRAP_API = "api"
BOOTSTRAP_COMPLETE = "complete"

BOOTSTRAP_SEQUENCE = (
    BOOTSTRAP_CONFIGURATION,
    BOOTSTRAP_DEPENDENCIES,
    BOOTSTRAP_SERVICES,
    BOOTSTRAP_API,
    BOOTSTRAP_COMPLETE,
)

# ============================================================
# Dependency Injection Service Names
# ============================================================

SERVICE_FORECAST = "forecast"
SERVICE_PLANNING = "planning"
SERVICE_OPTIMIZATION = "optimization"
SERVICE_ORCHESTRATION = "orchestration"
SERVICE_REPORTING = "reporting"
SERVICE_MONITORING = "monitoring"
SERVICE_API = "api"

SUPPORTED_SERVICES = (
    SERVICE_FORECAST,
    SERVICE_PLANNING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_REPORTING,
    SERVICE_MONITORING,
    SERVICE_API,
)

# ============================================================
# Metadata
# ============================================================

DEFAULT_CONFIGURATION_VERSION = "1.0.0"