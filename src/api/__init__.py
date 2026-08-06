"""
Implementation 24.8 — Enterprise API Package

Public API for the Enterprise API Layer.

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
    API_BASE_PATH,
    API_DOMAIN_NAME,
    API_DOMAIN_VERSION,
    API_STATUS_ACCEPTED,
    API_STATUS_ERROR,
    API_STATUS_SUCCESS,
    API_STATUS_WARNING,
    API_VERSION,
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_TEXT,
    DEFAULT_CONTENT_TYPE,
    DEFAULT_ENCODING,
    DEFAULT_REQUEST_SOURCE,
    DEFAULT_RESPONSE_VERSION,
    ENDPOINT_DECISION,
    ENDPOINT_DECISION_REPORT,
    ENDPOINT_HEALTH,
    ENDPOINT_MONITORING_SNAPSHOT,
    ENDPOINT_PLATFORM_HEALTH,
    ERROR_CODE_CONFIGURATION,
    ERROR_CODE_INTERNAL,
    ERROR_CODE_MAPPING,
    ERROR_CODE_METHOD_NOT_ALLOWED,
    ERROR_CODE_ROUTE_NOT_FOUND,
    ERROR_CODE_SERVICE,
    ERROR_CODE_VALIDATION,
    HEADER_API_VERSION,
    HEADER_CONTENT_TYPE,
    HEADER_CORRELATION_ID,
    HEADER_REQUEST_ID,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_STATUS_ACCEPTED,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
    HTTP_STATUS_UNPROCESSABLE_ENTITY,
    MAXIMUM_CORRELATION_ID_LENGTH,
    MAXIMUM_ERROR_MESSAGE_LENGTH,
    MAXIMUM_FORECAST_CONFIDENCE,
    MAXIMUM_PLANNING_HORIZON_DAYS,
    MAXIMUM_REQUEST_ID_LENGTH,
    MINIMUM_FORECAST_CONFIDENCE,
    MINIMUM_PLANNING_HORIZON_DAYS,
    OPERATION_BUILD_MONITORING_SNAPSHOT,
    OPERATION_CREATE_DECISION,
    OPERATION_CREATE_DECISION_REPORT,
    OPERATION_HEALTH_CHECK,
    OPERATION_PLATFORM_HEALTH,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
    SUPPORTED_API_ENDPOINTS,
    SUPPORTED_API_ERROR_CODES,
    SUPPORTED_API_OPERATIONS,
    SUPPORTED_API_STATUSES,
    SUPPORTED_CONTENT_TYPES,
    SUPPORTED_HTTP_METHODS,
    SUPPORTED_HTTP_STATUS_CODES,
    SUPPORTED_ROUTE_NAMES,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    APIConfigurationError,
    APIError,
    APIInternalError,
    APIMapperError,
    APIMethodNotAllowedError,
    APIRouteNotFoundError,
    APIRouterError,
    APIServiceError,
    APIValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    APIHealthResponse,
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    APIResponseMetadata,
    APIRouteDefinition,
)

# ============================================================
# Components
# ============================================================

from .configuration import APIConfiguration
from .mapper import EnterpriseAPIMapper
from .router import APIHandler, EnterpriseAPIRouter
from .service import EnterpriseAPIService


__all__ = [
    # Domain
    "API_DOMAIN_NAME",
    "API_DOMAIN_VERSION",
    "API_VERSION",
    "API_BASE_PATH",

    # Endpoints
    "ENDPOINT_HEALTH",
    "ENDPOINT_PLATFORM_HEALTH",
    "ENDPOINT_DECISION",
    "ENDPOINT_DECISION_REPORT",
    "ENDPOINT_MONITORING_SNAPSHOT",
    "SUPPORTED_API_ENDPOINTS",

    # Methods
    "HTTP_METHOD_GET",
    "HTTP_METHOD_POST",
    "SUPPORTED_HTTP_METHODS",

    # Routes
    "ROUTE_HEALTH",
    "ROUTE_PLATFORM_HEALTH",
    "ROUTE_DECISION",
    "ROUTE_DECISION_REPORT",
    "ROUTE_MONITORING_SNAPSHOT",
    "SUPPORTED_ROUTE_NAMES",

    # API statuses
    "API_STATUS_SUCCESS",
    "API_STATUS_ACCEPTED",
    "API_STATUS_WARNING",
    "API_STATUS_ERROR",
    "SUPPORTED_API_STATUSES",

    # HTTP status codes
    "HTTP_STATUS_OK",
    "HTTP_STATUS_CREATED",
    "HTTP_STATUS_ACCEPTED",
    "HTTP_STATUS_BAD_REQUEST",
    "HTTP_STATUS_NOT_FOUND",
    "HTTP_STATUS_CONFLICT",
    "HTTP_STATUS_UNPROCESSABLE_ENTITY",
    "HTTP_STATUS_INTERNAL_SERVER_ERROR",
    "HTTP_STATUS_SERVICE_UNAVAILABLE",
    "SUPPORTED_HTTP_STATUS_CODES",

    # Content types
    "CONTENT_TYPE_JSON",
    "CONTENT_TYPE_TEXT",
    "SUPPORTED_CONTENT_TYPES",
    "DEFAULT_CONTENT_TYPE",
    "DEFAULT_ENCODING",

    # Headers and metadata
    "HEADER_REQUEST_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_API_VERSION",
    "HEADER_CONTENT_TYPE",
    "DEFAULT_REQUEST_SOURCE",
    "DEFAULT_RESPONSE_VERSION",

    # Limits
    "MINIMUM_PLANNING_HORIZON_DAYS",
    "MAXIMUM_PLANNING_HORIZON_DAYS",
    "MINIMUM_FORECAST_CONFIDENCE",
    "MAXIMUM_FORECAST_CONFIDENCE",
    "MAXIMUM_REQUEST_ID_LENGTH",
    "MAXIMUM_CORRELATION_ID_LENGTH",
    "MAXIMUM_ERROR_MESSAGE_LENGTH",

    # Operations
    "OPERATION_HEALTH_CHECK",
    "OPERATION_PLATFORM_HEALTH",
    "OPERATION_CREATE_DECISION",
    "OPERATION_CREATE_DECISION_REPORT",
    "OPERATION_BUILD_MONITORING_SNAPSHOT",
    "SUPPORTED_API_OPERATIONS",

    # Error codes
    "ERROR_CODE_VALIDATION",
    "ERROR_CODE_CONFIGURATION",
    "ERROR_CODE_MAPPING",
    "ERROR_CODE_ROUTE_NOT_FOUND",
    "ERROR_CODE_METHOD_NOT_ALLOWED",
    "ERROR_CODE_SERVICE",
    "ERROR_CODE_INTERNAL",
    "SUPPORTED_API_ERROR_CODES",

    # Exceptions
    "APIError",
    "APIValidationError",
    "APIConfigurationError",
    "APIMapperError",
    "APIRouterError",
    "APIRouteNotFoundError",
    "APIMethodNotAllowedError",
    "APIServiceError",
    "APIInternalError",

    # Models
    "APIRequestMetadata",
    "APIResponseMetadata",
    "APIRequest",
    "APIResponse",
    "APIHealthResponse",
    "APIRouteDefinition",

    # Components
    "APIConfiguration",
    "EnterpriseAPIMapper",
    "APIHandler",
    "EnterpriseAPIRouter",
    "EnterpriseAPIService",
]