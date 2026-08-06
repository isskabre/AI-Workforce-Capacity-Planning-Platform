"""
Implementation 24.7 — Enterprise API Service

Framework-neutral API application service connecting transport-level
requests to enterprise orchestration, reporting, and monitoring.

The service registers API route handlers with EnterpriseAPIRouter and
provides one public dispatch entry point suitable for future exposure
through FastAPI, Databricks Apps, serverless functions, or another
transport framework.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone
from time import perf_counter
from typing import Any

from src.monitoring.exceptions import MonitoringError
from src.monitoring.service import EnterpriseMonitoringService
from src.orchestration.exceptions import OrchestrationError
from src.orchestration.models import EnterpriseDecisionRequest
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.reporting.exceptions import ReportingError
from src.reporting.models import (
    DecisionReportRequest,
    ReportFormat,
    ReportType,
)
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)

from .configuration import APIConfiguration
from .constants import (
    API_STATUS_ERROR,
    API_STATUS_SUCCESS,
    ERROR_CODE_SERVICE,
    ERROR_CODE_VALIDATION,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_OK,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
    ROUTE_DECISION,
    ROUTE_DECISION_REPORT,
    ROUTE_HEALTH,
    ROUTE_MONITORING_SNAPSHOT,
    ROUTE_PLATFORM_HEALTH,
)
from .exceptions import (
    APIError,
    APIServiceError,
    APIValidationError,
)
from .mapper import EnterpriseAPIMapper
from .models import (
    APIRequest,
    APIResponse,
    APIResponseMetadata,
)
from .router import EnterpriseAPIRouter


class EnterpriseAPIService:
    """
    Public application service for the Enterprise API Layer.

    Responsibilities
    ----------------
    - Register API route handlers.
    - Dispatch framework-neutral API requests.
    - Validate and map request payloads.
    - Execute enterprise decision orchestration.
    - Generate enterprise decision reports.
    - Expose platform health and monitoring snapshots.
    - Return standardized API response envelopes.
    """

    def __init__(
        self,
        *,
        configuration: APIConfiguration | None = None,
        router: EnterpriseAPIRouter | None = None,
        mapper: EnterpriseAPIMapper | None = None,
        orchestration_service: (
            EnterpriseDecisionOrchestrationService | None
        ) = None,
        reporting_service: (
            EnterpriseDecisionReportingService | None
        ) = None,
        monitoring_service: EnterpriseMonitoringService | None = None,
    ) -> None:
        """
        Initialize the Enterprise API service.
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
            raise APIServiceError(
                "configuration must be an APIConfiguration."
            )

        self._router = (
            router
            if router is not None
            else EnterpriseAPIRouter(
                configuration=self._configuration,
            )
        )

        if not isinstance(
            self._router,
            EnterpriseAPIRouter,
        ):
            raise APIServiceError(
                "router must be an EnterpriseAPIRouter."
            )

        if self._router.configuration is not self._configuration:
            raise APIValidationError(
                "configuration and router must reference the same "
                "APIConfiguration instance."
            )

        self._mapper = (
            mapper
            if mapper is not None
            else EnterpriseAPIMapper()
        )

        if not isinstance(
            self._mapper,
            EnterpriseAPIMapper,
        ):
            raise APIServiceError(
                "mapper must be an EnterpriseAPIMapper."
            )

        self._orchestration_service = (
            orchestration_service
            if orchestration_service is not None
            else EnterpriseDecisionOrchestrationService()
        )

        if not isinstance(
            self._orchestration_service,
            EnterpriseDecisionOrchestrationService,
        ):
            raise APIServiceError(
                "orchestration_service must be an "
                "EnterpriseDecisionOrchestrationService."
            )

        self._reporting_service = (
            reporting_service
            if reporting_service is not None
            else EnterpriseDecisionReportingService()
        )

        if not isinstance(
            self._reporting_service,
            EnterpriseDecisionReportingService,
        ):
            raise APIServiceError(
                "reporting_service must be an "
                "EnterpriseDecisionReportingService."
            )

        self._monitoring_service = (
            monitoring_service
            if monitoring_service is not None
            else EnterpriseMonitoringService()
        )

        if not isinstance(
            self._monitoring_service,
            EnterpriseMonitoringService,
        ):
            raise APIServiceError(
                "monitoring_service must be an "
                "EnterpriseMonitoringService."
            )

        self._register_handlers()

    # ========================================================
    # Public API
    # ========================================================

    def handle(
        self,
        *,
        path: str,
        method: str,
        request: APIRequest,
    ) -> APIResponse:
        """
        Dispatch one framework-neutral API request.
        """

        return self._router.dispatch(
            path=path,
            method=method,
            request=request,
        )

    # ========================================================
    # Route handlers
    # ========================================================

    def _handle_health(
        self,
        request: APIRequest,
    ) -> APIResponse:
        """
        Handle API service liveness checks.
        """

        started_at = perf_counter()

        return self._success_response(
            request=request,
            payload={
                "healthy": True,
                "status": "HEALTHY",
                "service": "enterprise-api",
                "api_version": (
                    self._configuration.api_version
                ),
                "configuration_version": (
                    self._configuration.configuration_version
                ),
            },
            started_at=started_at,
        )

    def _handle_platform_health(
        self,
        request: APIRequest,
    ) -> APIResponse:
        """
        Handle enterprise platform health requests.
        """

        started_at = perf_counter()

        try:
            health_report = (
                self._monitoring_service
                .check_platform_health()
            )

            payload = health_report.as_dict()

            payload["healthy"] = (
                health_report.status.value == "HEALTHY"
            )

            return self._success_response(
                request=request,
                payload=payload,
                started_at=started_at,
            )

        except MonitoringError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_SERVICE,
                message=str(exc),
                http_status=HTTP_STATUS_SERVICE_UNAVAILABLE,
                started_at=started_at,
            )

    def _handle_decision(
        self,
        request: APIRequest,
    ) -> APIResponse:
        """
        Handle enterprise workforce decision requests.
        """

        started_at = perf_counter()

        try:
            decision_request = self._map_decision_request(
                payload=self._mapper.request_payload(request),
            )

            decision_result = (
                self._orchestration_service.execute(
                    request=decision_request,
                )
            )

            return self._success_response(
                request=request,
                payload=decision_result.as_dict(),
                started_at=started_at,
            )

        except APIValidationError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_VALIDATION,
                message=str(exc),
                http_status=HTTP_STATUS_BAD_REQUEST,
                started_at=started_at,
            )

        except OrchestrationError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_SERVICE,
                message=str(exc),
                http_status=HTTP_STATUS_SERVICE_UNAVAILABLE,
                started_at=started_at,
            )

    def _handle_decision_report(
        self,
        request: APIRequest,
    ) -> APIResponse:
        """
        Handle enterprise decision-and-report requests.
        """

        started_at = perf_counter()

        try:
            payload = self._mapper.request_payload(request)

            decision_payload = payload.get("decision")
            report_payload = payload.get("report")

            if not isinstance(decision_payload, Mapping):
                raise APIValidationError(
                    "payload.decision must be a mapping."
                )

            if not isinstance(report_payload, Mapping):
                raise APIValidationError(
                    "payload.report must be a mapping."
                )

            decision_request = self._map_decision_request(
                payload=decision_payload,
            )

            report_request = self._map_report_request(
                payload=report_payload,
            )

            decision_result = (
                self._orchestration_service.execute(
                    request=decision_request,
                )
            )

            report_output = self._reporting_service.generate(
                decision_result=decision_result,
                request=report_request,
            )

            return self._success_response(
                request=request,
                payload={
                    "decision": decision_result.as_dict(),
                    "report_format": (
                        report_request.report_format.value
                    ),
                    "report": report_output,
                },
                started_at=started_at,
            )

        except APIValidationError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_VALIDATION,
                message=str(exc),
                http_status=HTTP_STATUS_BAD_REQUEST,
                started_at=started_at,
            )

        except (
            OrchestrationError,
            ReportingError,
        ) as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_SERVICE,
                message=str(exc),
                http_status=HTTP_STATUS_SERVICE_UNAVAILABLE,
                started_at=started_at,
            )

    def _handle_monitoring_snapshot(
        self,
        request: APIRequest,
    ) -> APIResponse:
        """
        Handle monitoring snapshot requests.
        """

        started_at = perf_counter()

        try:
            payload = self._mapper.request_payload(request)

            include_health = payload.get(
                "include_health",
                True,
            )

            if not isinstance(include_health, bool):
                raise APIValidationError(
                    "include_health must be a boolean."
                )

            snapshot = (
                self._monitoring_service.build_snapshot(
                    execution_observations={},
                    include_health=include_health,
                )
            )

            return self._success_response(
                request=request,
                payload=snapshot,
                started_at=started_at,
            )

        except APIValidationError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_VALIDATION,
                message=str(exc),
                http_status=HTTP_STATUS_BAD_REQUEST,
                started_at=started_at,
            )

        except MonitoringError as exc:
            return self._error_response(
                request=request,
                error_code=ERROR_CODE_SERVICE,
                message=str(exc),
                http_status=HTTP_STATUS_SERVICE_UNAVAILABLE,
                started_at=started_at,
            )

    # ========================================================
    # Request mapping
    # ========================================================

    @staticmethod
    def _map_decision_request(
        *,
        payload: Mapping[str, Any],
    ) -> EnterpriseDecisionRequest:
        """
        Map API payload to EnterpriseDecisionRequest.
        """

        if not isinstance(payload, Mapping):
            raise APIValidationError(
                "Decision payload must be a mapping."
            )

        required_fields = (
            "planning_date",
            "expected_order_lines",
            "available_associates",
            "productivity_lines_per_hour",
            "scheduled_hours",
            "forecast_confidence",
        )

        missing_fields = tuple(
            field_name
            for field_name in required_fields
            if field_name not in payload
        )

        if missing_fields:
            raise APIValidationError(
                "Missing required decision fields: "
                f"{', '.join(missing_fields)}."
            )

        planning_date = EnterpriseAPIService._parse_date(
            value=payload["planning_date"],
            field_name="planning_date",
        )

        try:
            return EnterpriseDecisionRequest(
                planning_date=planning_date,
                expected_order_lines=float(
                    payload["expected_order_lines"]
                ),
                available_associates=(
                    EnterpriseAPIService._parse_integer(
                        value=payload[
                            "available_associates"
                        ],
                        field_name=(
                            "available_associates"
                        ),
                    )
                ),
                productivity_lines_per_hour=float(
                    payload[
                        "productivity_lines_per_hour"
                    ]
                ),
                scheduled_hours=float(
                    payload["scheduled_hours"]
                ),
                forecast_confidence=float(
                    payload["forecast_confidence"]
                ),
                recurring_shortage_days=(
                    EnterpriseAPIService._parse_integer(
                        value=payload.get(
                            "recurring_shortage_days",
                            0,
                        ),
                        field_name=(
                            "recurring_shortage_days"
                        ),
                    )
                ),
                recurring_surplus_days=(
                    EnterpriseAPIService._parse_integer(
                        value=payload.get(
                            "recurring_surplus_days",
                            0,
                        ),
                        field_name=(
                            "recurring_surplus_days"
                        ),
                    )
                ),
                overtime_dependency_days=(
                    EnterpriseAPIService._parse_integer(
                        value=payload.get(
                            "overtime_dependency_days",
                            0,
                        ),
                        field_name=(
                            "overtime_dependency_days"
                        ),
                    )
                ),
                planning_horizon_days=(
                    EnterpriseAPIService._parse_integer(
                        value=payload.get(
                            "planning_horizon_days",
                            30,
                        ),
                        field_name=(
                            "planning_horizon_days"
                        ),
                    )
                ),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise APIValidationError(
                "Decision payload contains invalid numeric values."
            ) from exc

        except OrchestrationError as exc:
            raise APIValidationError(
                str(exc)
            ) from exc

    @staticmethod
    def _map_report_request(
        *,
        payload: Mapping[str, Any],
    ) -> DecisionReportRequest:
        """
        Map API payload to DecisionReportRequest.
        """

        if not isinstance(payload, Mapping):
            raise APIValidationError(
                "Report payload must be a mapping."
            )

        report_type_value = payload.get(
            "report_type",
            "operational",
        )

        report_format_value = payload.get(
            "report_format",
            "dict",
        )

        title = payload.get(
            "title",
            "Enterprise Workforce Decision Report",
        )

        try:
            report_type = ReportType(
                str(report_type_value).lower()
            )

            report_format = ReportFormat(
                str(report_format_value).lower()
            )

        except ValueError as exc:
            raise APIValidationError(
                "Unsupported report_type or report_format."
            ) from exc

        boolean_fields = {
            "include_metadata": payload.get(
                "include_metadata",
                True,
            ),
            "include_rationale": payload.get(
                "include_rationale",
                True,
            ),
            "include_empty_sections": payload.get(
                "include_empty_sections",
                False,
            ),
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise APIValidationError(
                    f"{field_name} must be a boolean."
                )

        try:
            return DecisionReportRequest(
                report_type=report_type,
                report_format=report_format,
                title=title,
                include_metadata=boolean_fields[
                    "include_metadata"
                ],
                include_rationale=boolean_fields[
                    "include_rationale"
                ],
                include_empty_sections=boolean_fields[
                    "include_empty_sections"
                ],
            )

        except ReportingError as exc:
            raise APIValidationError(
                str(exc)
            ) from exc

    # ========================================================
    # Response construction
    # ========================================================

    @staticmethod
    def _success_response(
        *,
        request: APIRequest,
        payload: Mapping[str, Any],
        started_at: float,
    ) -> APIResponse:
        """
        Build one standardized successful API response.
        """

        return APIResponse(
            status=API_STATUS_SUCCESS,
            http_status=HTTP_STATUS_OK,
            payload=dict(payload),
            metadata=EnterpriseAPIService._response_metadata(
                request=request,
                started_at=started_at,
            ),
        )

    @staticmethod
    def _error_response(
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

        return APIResponse(
            status=API_STATUS_ERROR,
            http_status=http_status,
            payload={
                "error": {
                    "code": error_code,
                    "message": message,
                }
            },
            metadata=EnterpriseAPIService._response_metadata(
                request=request,
                started_at=started_at,
            ),
        )

    @staticmethod
    def _response_metadata(
        *,
        request: APIRequest,
        started_at: float,
    ) -> APIResponseMetadata:
        """
        Build response metadata preserving request correlation.
        """

        return APIResponseMetadata(
            request_id=request.metadata.request_id,
            correlation_id=(
                request.metadata.correlation_id
            ),
            generated_at_utc=datetime.now(timezone.utc),
            processing_time_ms=max(
                0.0,
                (perf_counter() - started_at) * 1_000.0,
            ),
        )

    # ========================================================
    # Parsing helpers
    # ========================================================

    @staticmethod
    def _parse_date(
        *,
        value: Any,
        field_name: str,
    ) -> date:
        """
        Parse an ISO date or accept an existing date.
        """

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise APIValidationError(
                    f"{field_name} must use ISO format YYYY-MM-DD."
                ) from exc

        raise APIValidationError(
            f"{field_name} must be a date or ISO date string."
        )

    @staticmethod
    def _parse_integer(
        *,
        value: Any,
        field_name: str,
    ) -> int:
        """
        Parse a strict integer API field.
        """

        if isinstance(value, bool):
            raise APIValidationError(
                f"{field_name} must be an integer."
            )

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            stripped_value = value.strip()

            if stripped_value.lstrip("-").isdigit():
                return int(stripped_value)

        raise APIValidationError(
            f"{field_name} must be an integer."
        )

    # ========================================================
    # Router registration
    # ========================================================

    def _register_handlers(self) -> None:
        """
        Register handlers for every active API route.
        """

        handler_registry = {
            ROUTE_HEALTH: self._handle_health,
            ROUTE_PLATFORM_HEALTH: (
                self._handle_platform_health
            ),
            ROUTE_DECISION: self._handle_decision,
            ROUTE_DECISION_REPORT: (
                self._handle_decision_report
            ),
            ROUTE_MONITORING_SNAPSHOT: (
                self._handle_monitoring_snapshot
            ),
        }

        for route_name in self._router.route_names:
            handler = handler_registry.get(route_name)

            if handler is None:
                raise APIServiceError(
                    f"No API service handler exists for active "
                    f"route '{route_name}'."
                )

            self._router.register_handler(
                route_name=route_name,
                handler=handler,
            )

    # ========================================================
    # Dependencies
    # ========================================================

    @property
    def configuration(self) -> APIConfiguration:
        """
        Return the active API configuration.
        """

        return self._configuration

    @property
    def router(self) -> EnterpriseAPIRouter:
        """
        Return the active API router.
        """

        return self._router

    @property
    def mapper(self) -> EnterpriseAPIMapper:
        """
        Return the active API mapper.
        """

        return self._mapper

    @property
    def orchestration_service(
        self,
    ) -> EnterpriseDecisionOrchestrationService:
        """
        Return the enterprise orchestration dependency.
        """

        return self._orchestration_service

    @property
    def reporting_service(
        self,
    ) -> EnterpriseDecisionReportingService:
        """
        Return the enterprise reporting dependency.
        """

        return self._reporting_service

    @property
    def monitoring_service(
        self,
    ) -> EnterpriseMonitoringService:
        """
        Return the enterprise monitoring dependency.
        """

        return self._monitoring_service


__all__ = [
    "EnterpriseAPIService",
]