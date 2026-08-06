"""
Implementation 24.2 — Enterprise API Exceptions

Enterprise exception hierarchy for the API layer.

Version:
    1.0.0
"""

from __future__ import annotations


class APIError(Exception):
    """
    Base exception for the Enterprise API package.
    """


class APIValidationError(APIError):
    """
    Raised when API request validation fails.
    """


class APIConfigurationError(APIError):
    """
    Raised when API configuration is invalid.
    """


class APIMapperError(APIError):
    """
    Raised when request or response mapping fails.
    """


class APIRouterError(APIError):
    """
    Raised when API routing fails.
    """


class APIRouteNotFoundError(APIRouterError):
    """
    Raised when a requested route does not exist.
    """


class APIMethodNotAllowedError(APIRouterError):
    """
    Raised when the HTTP method is not supported.
    """


class APIServiceError(APIError):
    """
    Raised when the API service layer fails.
    """


class APIInternalError(APIError):
    """
    Raised for unexpected internal API failures.
    """


__all__ = [
    "APIError",
    "APIValidationError",
    "APIConfigurationError",
    "APIMapperError",
    "APIRouterError",
    "APIRouteNotFoundError",
    "APIMethodNotAllowedError",
    "APIServiceError",
    "APIInternalError",
]