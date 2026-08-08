"""
Implementation 24.6 — Enterprise API Router

Framework-neutral route registration, resolution, and request dispatch
for the Enterprise API Layer.

The router contains no business-domain logic and has no dependency on
FastAPI, Flask, or another HTTP framework. It maps transport-neutral API
requests to registered handlers and returns standardized API responses.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from .configuration import APIConfiguration
from .constants import (
    API_STATUS_ERROR,
    ERROR_CODE_INTERNAL,
    ERROR_CODE_METHOD_NOT_ALLOWED,
    ERROR_CODE_ROUTE_NOT_FOUND,
    ERROR_CODE_VALIDATION,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
)
from .exceptions import (
    APIError,
    APIInternalError,
    APIMethodNotAllowedError,
    APIRouteNotFoundError,
    APIRouterError,
    APIValidationError,
)
from .models import (
    APIRequest,
    APIResponse,
    APIResponseMetadata,
    APIRouteDefinition,
)


APIHandler = Callable[[APIRequest], APIResponse]


class EnterpriseAPIRouter:
    """
    Framework-neutral Enterprise API route registry and dispatcher.

    Parameters
    ----------
    configuration:
        Active API configuration.

    handlers:
        Optional mapping of route names to request handlers.

    Notes
    -----
    Handlers must accept one ``APIRequest`` and return one
    ``APIResponse``.

    Route availability is controlled by ``APIConfiguration``. Disabled
    endpoints are not added to the active route registry.
    """

    def __init__(
        self,
        *,
        configuration: APIConfiguration | None = None,
        handlers: Mapping[str, APIHandler] | None = None,
    ) -> None:
        """
        Initialize the Enterprise API router.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else APIConfiguration()
        )

        if not isinstance(
            self._configuration,
            APIConfiguration,
        ):
            raise APIRouterError(
                "configuration must be an APIConfiguration."
            )

        self._routes = self._build_routes()
        self._handlers: dict[str, APIHandler] = {}

        if handlers is not None:
            if not isinstance(handlers, Mapping):
                raise APIRouterError(
                    "handlers must be a mapping."
                )

            for route_name, handler in handlers.items():
                self.register_handler(
                    route_name=route_name,
                    handler=handler,
                )

    # ========================================================
    # Handler registration
    # ========================================================

    def register_handler(
        self,
        *,
        route_name: str,
        handler: APIHandler,
        replace: bool = False,
    ) -> None:
        """
        Register one request handler.

        Parameters
        ----------
        route_name:
            Name of an active route.

        handler:
            Callable accepting ``APIRequest`` and returning
            ``APIResponse``.

        replace:
            Whether an existing handler may be replaced.
        """

        self._validate_route_name(route_name)

        if not callable(handler):
            raise APIRouterError(
                "handler must be callable."
            )

        if not isinstance(replace, bool):
            raise APIRouterError(
                "replace must be a boolean."
            )

        if (
            route_name in self._handlers
            and not replace
        ):
            raise APIRouterError(
                f"A handler is already registered for "
                f"route '{route_name}'."
            )

        self._handlers[route_name] = handler

    def unregister_handler(
        self,
        *,
        route_name: str,
    ) -> None:
        """
        Remove one registered route handler.
        """

        self._validate_route_name(route_name)

        self._handlers.pop(route_name, None)

    # ========================================================
    # Route resolution
    # ========================================================

    def resolve(
        self,
        *,
        path: str,
        method: str,
    ) -> APIRouteDefinition:
        """
        Resolve a path and method to one active route.

        Raises
        ------
        APIValidationError
            If path or method is structurally invalid.

        APIRouteNotFoundError
            If no active route uses the supplied path.

        APIMethodNotAllowedError
            If the path exists but does not support the method.
        """

        normalized_path = self._normalize_path(path)
        normalized_method = self._normalize_method(method)

        matching_path_routes = tuple(
            route
            for route in self._routes.values()
            if route.path == normalized_path
        )

        if not matching_path_routes:
            raise APIRouteNotFoundError(
                f"No API route exists for path "
                f"'{normalized_path}'."
            )

        for route in matching_path_routes:
            if route.method == normalized_method:
                return route

        supported_methods = ", ".join(
            sorted(
                {
                    route.method
                    for route in matching_path_routes
                }
            )
        )

        raise APIMethodNotAllowedError(
            f"Method '{normalized_method}' is not allowed for "
            f"path '{normalized_path}'. Supported methods: "
            f"{supported_methods}."
        )

    # ========================================================
    # Dispatch
    # ========================================================

    def dispatch(
        self,
        *,
        path: str,
        method: str,
        request: APIRequest,
    ) -> APIResponse:
        """
        Resolve and dispatch one API request.

        Registered handler responses are returned unchanged. Router
        and validation failures are converted into standardized error
        responses using the request metadata.
        """

        if not isinstance(request, APIRequest):
            raise APIValidationError(
                "request must be an APIRequest."
            )

        started_at = perf_counter()

        try:
            route = self.resolve(
                path=path,
                method=method,
            )

            if request.operation != route.operation:
                raise APIValidationError(
                    "Request operation does not match the resolved "
                    "route operation."
                )

            handler = self._handlers.get(route.name)

            if handler is None:
                raise APIRouterError(
                    f"No handler is registered for route "
                    f"'{route.name}'."
                )

            response = handler(request)

            if not isinstance(response, APIResponse):
                raise APIInternalError(
                    "API handler must return an APIResponse."
                )

            if (
                response.metadata.request_id
                != request.metadata.request_id
            ):
                raise APIInternalError(
                    "Handler response request_id does not match "
                    "the request."
                )

            if (
                response.metadata.correlation_id
                != request.metadata.correlation_id
            ):
                raise APIInternalError(
                    "Handler response correlation_id does not match "
                    "the request."
                )

            return response

        except APIRouteNotFoundError as exc:
            return self._build_error_response(
                request=request,
                error_code=ERROR_CODE_ROUTE_NOT_FOUND,
                message=str(exc),
                http_status=HTTP_STATUS_NOT_FOUND,
                started_at=started_at,
            )

        except APIMethodNotAllowedError as exc:
            return self._build_error_response(
                request=request,
                error_code=ERROR_CODE_METHOD_NOT_ALLOWED,
                message=str(exc),
                http_status=HTTP_STATUS_BAD_REQUEST,
                started_at=started_at,
            )

        except APIValidationError as exc:
            return self._build_error_response(
                request=request,
                error_code=ERROR_CODE_VALIDATION,
                message=str(exc),
                http_status=HTTP_STATUS_BAD_REQUEST,
                started_at=started_at,
            )

        except APIError as exc:
            return self._build_error_response(
                request=request,
                error_code=ERROR_CODE_INTERNAL,
                message=str(exc),
                http_status=HTTP_STATUS_INTERNAL_SERVER_ERROR,
                started_at=started_at,
            )

        except Exception:
            return self._build_error_response(
                request=request,
                error_code=ERROR_CODE_INTERNAL,
                message="Unexpected internal API routing failure.",
                http_status=HTTP_STATUS_INTERNAL_SERVER_ERROR,
                started_at=started_at,
            )

    # ========================================================
    # Route construction
    # ========================================================

    def _build_routes(
        self,
    ) -> dict[str, APIRouteDefinition]:
        """
        Build the active route registry from API configuration.
        """

        versioned_base_path = self._versioned_base_path()

        routes: dict[str, APIRouteDefinition] = {}

        if self._configuration.enable_health_endpoint:
            routes[ROUTE_HEALTH] = APIRouteDefinition(
                name=ROUTE_HEALTH,
                path=f"{versioned_base_path}/health",
                method=HTTP_METHOD_GET,
                operation="health_check",
                metadata={
                    "enabled": True,
                    "content_type": (
                        self._configuration
                        .default_content_type
                    ),
                },
            )

        if self._configuration.enable_platform_health_endpoint:
            routes[
                ROUTE_PLATFORM_HEALTH
            ] = APIRouteDefinition(
                name=ROUTE_PLATFORM_HEALTH,
                path=(
                    f"{versioned_base_path}"
                    "/health/platform"
                ),
                method=HTTP_METHOD_GET,
                operation="platform_health",
                metadata={
                    "enabled": True,
                    "content_type": (
                        self._configuration
                        .default_content_type
                    ),
                },
            )

        if self._configuration.enable_decision_endpoint:
            routes[ROUTE_DECISION] = APIRouteDefinition(
                name=ROUTE_DECISION,
                path=f"{versioned_base_path}/decisions",
                method=HTTP_METHOD_POST,
                operation="create_enterprise_decision",
                metadata={
                    "enabled": True,
                    "content_type": (
                        self._configuration
                        .default_content_type
                    ),
                },
            )

        if (
            self._configuration
            .enable_decision_report_endpoint
        ):
            routes[
                ROUTE_DECISION_REPORT
            ] = APIRouteDefinition(
                name=ROUTE_DECISION_REPORT,
                path=(
                    f"{versioned_base_path}"
                    "/decisions/report"
                ),
                method=HTTP_METHOD_POST,
                operation=(
                    "create_enterprise_decision_report"
                ),
                metadata={
                    "enabled": True,
                    "content_type": (
                        self._configuration
                        .default_content_type
                    ),
                },
            )

        if self._configuration.enable_monitoring_endpoint:
            routes[
                ROUTE_MONITORING_SNAPSHOT
            ] = APIRouteDefinition(
                name=ROUTE_MONITORING_SNAPSHOT,
                path=(
                    f"{versioned_base_path}"
                    "/monitoring/snapshot"
                ),
                method=HTTP_METHOD_POST,
                operation="build_monitoring_snapshot",
                metadata={
                    "enabled": True,
                    "content_type": (
                        self._configuration
                        .default_content_type
                    ),
                },
            )

        return routes

    # ========================================================
    # Error responses
    # ========================================================

    @staticmethod
    def _build_error_response(
        *,
        request: APIRequest,
        error_code: str,
        message: str,
        http_status: int,
        started_at: float,
    ) -> APIResponse:
        """
        Build one standardized API error response.
        """

        processing_time_ms = max(
            0.0,
            (perf_counter() - started_at) * 1_000.0,
        )

        return APIResponse(
            status=API_STATUS_ERROR,
            http_status=http_status,
            payload={
                "error": {
                    "code": error_code,
                    "message": message,
                }
            },
            metadata=APIResponseMetadata(
                request_id=request.metadata.request_id,
                correlation_id=(
                    request.metadata.correlation_id
                ),
                generated_at_utc=datetime.now(
                    timezone.utc
                ),
                processing_time_ms=processing_time_ms,
            ),
        )

    # ========================================================
    # Validation and normalization
    # ========================================================

    def _validate_route_name(
        self,
        route_name: str,
    ) -> None:
        """
        Validate an active route name.
        """

        if (
            not isinstance(route_name, str)
            or not route_name.strip()
        ):
            raise APIRouterError(
                "route_name must be a non-empty string."
            )

        if route_name not in self._routes:
            raise APIRouteNotFoundError(
                f"Route '{route_name}' is not active."
            )

    def _versioned_base_path(self) -> str:
        """
        Return normalized base path including API version.
        """

        base_path = self._configuration.base_path.rstrip("/")
        api_version = (
            self._configuration.api_version.strip("/")
        )

        return f"{base_path}/{api_version}"

    @staticmethod
    def _normalize_path(
        path: str,
    ) -> str:
        """
        Validate and normalize an API route path.
        """

        if not isinstance(path, str) or not path.strip():
            raise APIValidationError(
                "path must be a non-empty string."
            )

        normalized = path.strip()

        if not normalized.startswith("/"):
            raise APIValidationError(
                "path must start with '/'."
            )

        if len(normalized) > 1:
            normalized = normalized.rstrip("/")

        return normalized

    @staticmethod
    def _normalize_method(
        method: str,
    ) -> str:
        """
        Validate and normalize an HTTP method.
        """

        if (
            not isinstance(method, str)
            or not method.strip()
        ):
            raise APIValidationError(
                "method must be a non-empty string."
            )

        return method.strip().upper()

    # ========================================================
    # Public state
    # ========================================================

    @property
    def configuration(self) -> APIConfiguration:
        """
        Return the active API configuration.
        """

        return self._configuration

    @property
    def routes(
        self,
    ) -> tuple[APIRouteDefinition, ...]:
        """
        Return active routes as an immutable tuple.
        """

        return tuple(self._routes.values())

    @property
    def route_names(self) -> tuple[str, ...]:
        """
        Return active route names.
        """

        return tuple(self._routes)

    @property
    def registered_handler_names(
        self,
    ) -> tuple[str, ...]:
        """
        Return route names with registered handlers.
        """

        return tuple(self._handlers)


__all__ = [
    "APIHandler",
    "EnterpriseAPIRouter",
]