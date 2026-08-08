"""
Implementation 24.1 — Enterprise API Constants

Centralized API constants for versioning, endpoint definitions,
request processing, response envelopes, and transport-neutral routing.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations


# ============================================================
# Domain
# ============================================================

API_DOMAIN_NAME = "enterprise-api"

API_DOMAIN_VERSION = "1.0.0"

API_VERSION = "v1"

API_BASE_PATH = f"/api/{API_VERSION}"


# ============================================================
# API Endpoints
# ============================================================

ENDPOINT_HEALTH = f"{API_BASE_PATH}/health"

ENDPOINT_PLATFORM_HEALTH = f"{API_BASE_PATH}/health/platform"

ENDPOINT_DECISION = f"{API_BASE_PATH}/decisions"

ENDPOINT_DECISION_REPORT = f"{API_BASE_PATH}/decisions/report"

ENDPOINT_MONITORING_SNAPSHOT = (
    f"{API_BASE_PATH}/monitoring/snapshot"
)

SUPPORTED_API_ENDPOINTS = (
    ENDPOINT_HEALTH,
    ENDPOINT_PLATFORM_HEALTH,
    ENDPOINT_DECISION,
    ENDPOINT_DECISION_REPORT,
    ENDPOINT_MONITORING_SNAPSHOT,
)


# ============================================================
# HTTP Methods
# ============================================================

HTTP_METHOD_GET = "GET"

HTTP_METHOD_POST = "POST"

SUPPORTED_HTTP_METHODS = (
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
)


# ============================================================
# Route Names
# ============================================================

ROUTE_HEALTH = "health"

ROUTE_PLATFORM_HEALTH = "platform_health"

ROUTE_DECISION = "enterprise_decision"

ROUTE_DECISION_REPORT = "enterprise_decision_report"

ROUTE_MONITORING_SNAPSHOT = "monitoring_snapshot"

SUPPORTED_ROUTE_NAMES = (
    ROUTE_HEALTH,
    ROUTE_PLATFORM_HEALTH,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_MONITORING_SNAPSHOT,
)


# ============================================================
# Response Statuses
# ============================================================

API_STATUS_SUCCESS = "SUCCESS"

API_STATUS_ACCEPTED = "ACCEPTED"

API_STATUS_WARNING = "WARNING"

API_STATUS_ERROR = "ERROR"

SUPPORTED_API_STATUSES = (
    API_STATUS_SUCCESS,
    API_STATUS_ACCEPTED,
    API_STATUS_WARNING,
    API_STATUS_ERROR,
)


# ============================================================
# HTTP Status Codes
# ============================================================

HTTP_STATUS_OK = 200

HTTP_STATUS_CREATED = 201

HTTP_STATUS_ACCEPTED = 202

HTTP_STATUS_BAD_REQUEST = 400

HTTP_STATUS_NOT_FOUND = 404

HTTP_STATUS_CONFLICT = 409

HTTP_STATUS_UNPROCESSABLE_ENTITY = 422

HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

HTTP_STATUS_SERVICE_UNAVAILABLE = 503

SUPPORTED_HTTP_STATUS_CODES = (
    HTTP_STATUS_OK,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_ACCEPTED,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_UNPROCESSABLE_ENTITY,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
)


# ============================================================
# Content Types
# ============================================================

CONTENT_TYPE_JSON = "application/json"

CONTENT_TYPE_TEXT = "text/plain"

SUPPORTED_CONTENT_TYPES = (
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_TEXT,
)

DEFAULT_CONTENT_TYPE = CONTENT_TYPE_JSON


# ============================================================
# Request and Response Metadata
# ============================================================

HEADER_REQUEST_ID = "X-Request-ID"

HEADER_CORRELATION_ID = "X-Correlation-ID"

HEADER_API_VERSION = "X-API-Version"

HEADER_CONTENT_TYPE = "Content-Type"

DEFAULT_REQUEST_SOURCE = "enterprise-api"

DEFAULT_RESPONSE_VERSION = "1.0.0"

DEFAULT_ENCODING = "utf-8"


# ============================================================
# Request Limits
# ============================================================

MINIMUM_PLANNING_HORIZON_DAYS = 1

MAXIMUM_PLANNING_HORIZON_DAYS = 365

MINIMUM_FORECAST_CONFIDENCE = 0.0

MAXIMUM_FORECAST_CONFIDENCE = 1.0

MAXIMUM_REQUEST_ID_LENGTH = 128

MAXIMUM_CORRELATION_ID_LENGTH = 128

MAXIMUM_ERROR_MESSAGE_LENGTH = 2_000


# ============================================================
# API Operations
# ============================================================

OPERATION_HEALTH_CHECK = "health_check"

OPERATION_PLATFORM_HEALTH = "platform_health"

OPERATION_CREATE_DECISION = "create_enterprise_decision"

OPERATION_CREATE_DECISION_REPORT = (
    "create_enterprise_decision_report"
)

OPERATION_BUILD_MONITORING_SNAPSHOT = (
    "build_monitoring_snapshot"
)

SUPPORTED_API_OPERATIONS = (
    OPERATION_HEALTH_CHECK,
    OPERATION_PLATFORM_HEALTH,
    OPERATION_CREATE_DECISION,
    OPERATION_CREATE_DECISION_REPORT,
    OPERATION_BUILD_MONITORING_SNAPSHOT,
)


# ============================================================
# Error Codes
# ============================================================

ERROR_CODE_VALIDATION = "API_VALIDATION_ERROR"

ERROR_CODE_CONFIGURATION = "API_CONFIGURATION_ERROR"

ERROR_CODE_MAPPING = "API_MAPPING_ERROR"

ERROR_CODE_ROUTE_NOT_FOUND = "API_ROUTE_NOT_FOUND"

ERROR_CODE_METHOD_NOT_ALLOWED = "API_METHOD_NOT_ALLOWED"

ERROR_CODE_SERVICE = "API_SERVICE_ERROR"

ERROR_CODE_INTERNAL = "API_INTERNAL_ERROR"

SUPPORTED_API_ERROR_CODES = (
    ERROR_CODE_VALIDATION,
    ERROR_CODE_CONFIGURATION,
    ERROR_CODE_MAPPING,
    ERROR_CODE_ROUTE_NOT_FOUND,
    ERROR_CODE_METHOD_NOT_ALLOWED,
    ERROR_CODE_SERVICE,
    ERROR_CODE_INTERNAL,
)


# ============================================================
# Public API
# ============================================================

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

    # Headers and metadata
    "HEADER_REQUEST_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_API_VERSION",
    "HEADER_CONTENT_TYPE",
    "DEFAULT_REQUEST_SOURCE",
    "DEFAULT_RESPONSE_VERSION",
    "DEFAULT_ENCODING",

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

    # Errors
    "ERROR_CODE_VALIDATION",
    "ERROR_CODE_CONFIGURATION",
    "ERROR_CODE_MAPPING",
    "ERROR_CODE_ROUTE_NOT_FOUND",
    "ERROR_CODE_METHOD_NOT_ALLOWED",
    "ERROR_CODE_SERVICE",
    "ERROR_CODE_INTERNAL",
    "SUPPORTED_API_ERROR_CODES",
]