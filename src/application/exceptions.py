"""
Implementation 25.2 — Enterprise Application Exceptions

Enterprise exception hierarchy for the Application Layer.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


# ============================================================
# Base Exception
# ============================================================

class ApplicationError(Exception):
    """
    Base exception for the Enterprise Application Layer.
    """


# ============================================================
# Validation
# ============================================================

class ApplicationValidationError(ApplicationError):
    """
    Raised when application input or state validation fails.
    """


# ============================================================
# Configuration
# ============================================================

class ApplicationConfigurationError(ApplicationError):
    """
    Raised when application configuration is invalid.
    """


# ============================================================
# Dependency Injection
# ============================================================

class ApplicationContainerError(ApplicationError):
    """
    Raised when dependency-container operations fail.
    """


class ApplicationDependencyError(ApplicationError):
    """
    Raised when application dependency resolution fails.

    This includes missing dependencies, circular dependencies,
    invalid dependency graphs, and service-construction failures.
    """


class ApplicationFactoryError(ApplicationError):
    """
    Raised when application service factories fail.
    """


# ============================================================
# Bootstrap
# ============================================================

class ApplicationBootstrapError(ApplicationError):
    """
    Raised when application bootstrap fails.
    """


# ============================================================
# Lifecycle
# ============================================================

class ApplicationLifecycleError(ApplicationError):
    """
    Raised when an invalid application lifecycle operation occurs.
    """


# ============================================================
# Public API
# ============================================================

__all__ = [
    "ApplicationBootstrapError",
    "ApplicationConfigurationError",
    "ApplicationContainerError",
    "ApplicationDependencyError",
    "ApplicationError",
    "ApplicationFactoryError",
    "ApplicationLifecycleError",
    "ApplicationValidationError",
]