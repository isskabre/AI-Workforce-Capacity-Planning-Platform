"""
AI Workforce Capacity Planning Platform
Implementation 30.1 — Enterprise Workforce Decision Workspace

Module:
    deployment.databricks_app.app

Description:
    Production Streamlit interface for the AI Workforce Capacity Planning
    Platform v3.0.0.

    The application provides an operational workforce decision workspace
    on top of the validated Enterprise API Layer.

    Responsibilities:
        - Bootstrap the validated enterprise application runtime.
        - Resolve the Enterprise API Service.
        - Display production runtime status.
        - Collect workforce planning inputs.
        - Submit transport-neutral enterprise decision requests.
        - Present workforce capacity and staffing recommendations.
        - Surface optimization and recommendation intelligence.
        - Preserve platform-health and bootstrap diagnostics.
        - Avoid duplicating business-domain logic in the UI layer.

    Business calculations remain owned by the validated enterprise
    orchestration, planning, staffing, overtime, optimization, reporting,
    and monitoring services.

Author:
    AI Workforce Capacity Planning Platform

Platform Version:
    3.0.0
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

import streamlit as st


# ============================================================
# Repository Import Path
# ============================================================

APP_FILE = Path(__file__).resolve()

REPOSITORY_ROOT = APP_FILE.parents[2]

repository_root_string = str(REPOSITORY_ROOT)

if repository_root_string not in sys.path:
    sys.path.insert(
        0,
        repository_root_string,
    )


# ============================================================
# Enterprise Platform Imports
# ============================================================

from src.api import (
    APIRequest,
    APIRequestMetadata,
    APIResponse,
    ENDPOINT_DECISION,
    ENDPOINT_HEALTH,
    ENDPOINT_PLATFORM_HEALTH,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    OPERATION_CREATE_DECISION,
    OPERATION_HEALTH_CHECK,
    OPERATION_PLATFORM_HEALTH,
)
from src.application import (
    ApplicationConfiguration,
    ApplicationEnvironment,
    EnterpriseApplicationBootstrap,
    SERVICE_API,
)


# ============================================================
# Deployment Constants
# ============================================================

APP_TITLE = "AI Workforce Capacity Planning"

APP_SUBTITLE = (
    "Enterprise Decision Intelligence Platform"
)

REQUEST_SOURCE = "databricks-app"

PLATFORM_VERSION = "3.0.0"

DEPLOYMENT_TARGET = "databricks_apps"

DEPLOYMENT_ENVIRONMENT = (
    "paid_databricks_reference"
)

DEPLOYMENT_ADAPTER = "streamlit"

DECISION_RESPONSE_STATE_KEY = (
    "enterprise_decision_response"
)

DECISION_REQUEST_STATE_KEY = (
    "enterprise_decision_request"
)


# ============================================================
# Streamlit Configuration
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)


# ============================================================
# Enterprise Runtime Bootstrap
# ============================================================

@st.cache_resource
def bootstrap_platform() -> tuple[Any, Any]:
    """
    Bootstrap the validated enterprise application exactly once.

    Returns
    -------
    tuple[Any, Any]
        ApplicationContext and resolved EnterpriseAPIService.
    """

    configuration = ApplicationConfiguration(
        environment=ApplicationEnvironment.PRODUCTION,
        metadata={
            "deployment_target": DEPLOYMENT_TARGET,
            "deployment_environment": (
                DEPLOYMENT_ENVIRONMENT
            ),
            "deployment_adapter": DEPLOYMENT_ADAPTER,
            "implementation": "30.1",
        },
    )

    bootstrap = EnterpriseApplicationBootstrap(
        configuration=configuration,
    )

    context = bootstrap.start()

    api_service = context.get_service(
        name=SERVICE_API,
    )

    return context, api_service


# ============================================================
# Enterprise API Helpers
# ============================================================

def build_api_request(
    *,
    operation: str,
    payload: Mapping[str, Any] | None = None,
) -> APIRequest:
    """
    Construct one transport-neutral enterprise API request.
    """

    request_payload = (
        {}
        if payload is None
        else dict(payload)
    )

    return APIRequest(
        operation=operation,
        payload=request_payload,
        metadata=APIRequestMetadata(
            request_id=f"req-{uuid4().hex}",
            correlation_id=f"corr-{uuid4().hex}",
            source=REQUEST_SOURCE,
            received_at_utc=datetime.now(
                timezone.utc
            ),
        ),
    )


def call_api(
    *,
    api_service: Any,
    path: str,
    method: str,
    operation: str,
    payload: Mapping[str, Any] | None = None,
) -> APIResponse:
    """
    Dispatch one request through EnterpriseAPIService.
    """

    request = build_api_request(
        operation=operation,
        payload=payload,
    )

    response = api_service.handle(
        path=path,
        method=method,
        request=request,
    )

    if not isinstance(response, APIResponse):
        raise TypeError(
            "Enterprise API must return APIResponse."
        )

    return response


# ============================================================
# Presentation Helpers
# ============================================================

def payload_value(
    payload: Mapping[str, Any],
    *keys: str,
    default: Any = "N/A",
) -> Any:
    """
    Return the first matching value from a payload.
    """

    for key in keys:
        if key in payload:
            return payload[key]

    return default


def format_number(
    value: Any,
    *,
    decimals: int = 0,
) -> str:
    """
    Format a numeric value for operational presentation.
    """

    if value is None:
        return "N/A"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if decimals <= 0:
        return f"{numeric_value:,.0f}"

    return f"{numeric_value:,.{decimals}f}"


def format_percentage(
    value: Any,
) -> str:
    """
    Format a decimal confidence value as a percentage.
    """

    if value is None:
        return "N/A"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)

    return f"{numeric_value * 100.0:.1f}%"


def normalize_display_text(
    value: Any,
) -> str:
    """
    Convert machine-oriented text into a readable label.
    """

    if value is None:
        return "N/A"

    text = str(value).strip()

    if not text:
        return "N/A"

    return text.replace(
        "_",
        " ",
    ).title()


def render_api_error(
    *,
    response: APIResponse,
) -> None:
    """
    Render a standardized enterprise API error.
    """

    payload = dict(response.payload)

    error_payload = payload.get(
        "error",
        {},
    )

    if isinstance(error_payload, Mapping):
        error_code = error_payload.get(
            "code",
            "API_ERROR",
        )

        error_message = error_payload.get(
            "message",
            "Enterprise request failed.",
        )

    else:
        error_code = "API_ERROR"
        error_message = str(error_payload)

    st.error(
        f"{error_code}: {error_message}"
    )

    with st.expander(
        "API Error Details"
    ):
        st.json(payload)


def render_decision_summary(
    *,
    payload: Mapping[str, Any],
) -> None:
    """
    Render the primary enterprise decision summary.
    """

    st.subheader(
        "Decision Summary"
    )

    workflow_status = payload_value(
        payload,
        "workflow_status",
        "status",
    )

    planning_date_value = payload_value(
        payload,
        "planning_date",
    )

    confidence = payload_value(
        payload,
        "recommendation_confidence",
        "confidence",
    )

    summary_column_1, summary_column_2, summary_column_3 = (
        st.columns(3)
    )

    with summary_column_1:
        st.metric(
            label="Workflow Status",
            value=normalize_display_text(
                workflow_status
            ),
        )

    with summary_column_2:
        st.metric(
            label="Planning Date",
            value=str(
                planning_date_value
            ),
        )

    with summary_column_3:
        st.metric(
            label="Recommendation Confidence",
            value=format_percentage(
                confidence
            ),
        )


def render_capacity_analysis(
    *,
    payload: Mapping[str, Any],
) -> None:
    """
    Render workforce requirement and capacity metrics.
    """

    st.subheader(
        "Workforce Capacity Analysis"
    )

    expected_order_lines = payload_value(
        payload,
        "expected_order_lines",
    )

    available_associates = payload_value(
        payload,
        "available_associates",
    )

    required_associates = payload_value(
        payload,
        "required_associates",
    )

    associate_gap = payload_value(
        payload,
        "associate_gap",
        "workforce_gap",
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    with metric_1:
        st.metric(
            label="Expected Order Lines",
            value=format_number(
                expected_order_lines
            ),
        )

    with metric_2:
        st.metric(
            label="Available Associates",
            value=format_number(
                available_associates
            ),
        )

    with metric_3:
        st.metric(
            label="Required Associates",
            value=format_number(
                required_associates
            ),
        )

    with metric_4:
        st.metric(
            label="Associate Gap",
            value=format_number(
                associate_gap
            ),
        )


def render_recommendation(
    *,
    payload: Mapping[str, Any],
) -> None:
    """
    Render staffing and optimization recommendations.
    """

    st.subheader(
        "Operational Recommendation"
    )

    staffing_recommendation = payload_value(
        payload,
        "staffing_recommendation",
        "recommendation",
    )

    optimization_priority = payload_value(
        payload,
        "optimization_priority",
        "priority",
    )

    confidence = payload_value(
        payload,
        "recommendation_confidence",
        "confidence",
    )

    recommendation_column_1, recommendation_column_2, recommendation_column_3 = (
        st.columns(3)
    )

    with recommendation_column_1:
        st.metric(
            label="Staffing Recommendation",
            value=normalize_display_text(
                staffing_recommendation
            ),
        )

    with recommendation_column_2:
        st.metric(
            label="Optimization Priority",
            value=normalize_display_text(
                optimization_priority
            ),
        )

    with recommendation_column_3:
        st.metric(
            label="Decision Confidence",
            value=format_percentage(
                confidence
            ),
        )

    rationale = payload_value(
        payload,
        "recommendation_rationale",
        "rationale",
        "decision_rationale",
        default=None,
    )

    if rationale:
        st.info(
            str(rationale)
        )


def render_decision_payload(
    *,
    response: APIResponse,
) -> None:
    """
    Render a successful enterprise decision response.
    """

    payload = dict(
        response.payload
    )

    render_decision_summary(
        payload=payload,
    )

    st.divider()

    render_capacity_analysis(
        payload=payload,
    )

    st.divider()

    render_recommendation(
        payload=payload,
    )

    with st.expander(
        "Complete Enterprise Decision Payload"
    ):
        st.json(payload)

    with st.expander(
        "Request / Response Trace"
    ):
        trace_payload = {
            "request_id": (
                response.metadata.request_id
            ),
            "correlation_id": (
                response.metadata.correlation_id
            ),
            "http_status": (
                response.http_status
            ),
            "api_status": (
                response.status
            ),
            "processing_time_ms": (
                response.metadata
                .processing_time_ms
            ),
            "generated_at_utc": (
                response.metadata
                .generated_at_utc
                .isoformat()
            ),
        }

        st.json(
            trace_payload
        )


# ============================================================
# Application Header
# ============================================================

st.title(
    APP_TITLE
)

st.caption(
    APP_SUBTITLE
)

st.markdown(
    """
    Operational decision workspace for the validated
    **AI Workforce Capacity Planning Platform v3.0.0**.

    Enter a planning scenario below to evaluate workforce capacity,
    staffing requirements, and the recommended operational action.
    """
)


# ============================================================
# Bootstrap Production Runtime
# ============================================================

try:
    (
        application_context,
        enterprise_api,
    ) = bootstrap_platform()

except Exception as exc:
    st.error(
        "The enterprise platform could not be initialized."
    )

    st.exception(exc)

    st.stop()


# ============================================================
# Platform Runtime Status
# ============================================================

descriptor = (
    application_context.descriptor
)

status_column, version_column, environment_column = (
    st.columns(3)
)

with status_column:
    st.metric(
        label="Platform Status",
        value=descriptor.status.value,
    )

with version_column:
    st.metric(
        label="Platform Version",
        value=descriptor.application_version,
    )

with environment_column:
    st.metric(
        label="Environment",
        value=(
            descriptor.environment
            .value
            .upper()
        ),
    )


# ============================================================
# Workforce Decision Workspace
# ============================================================

st.divider()

st.header(
    "Workforce Decision Planning"
)

st.caption(
    "Evaluate an operational demand scenario through the "
    "validated enterprise decision orchestration workflow."
)

with st.form(
    "enterprise_workforce_decision_form",
    clear_on_submit=False,
):

    planning_column_1, planning_column_2 = (
        st.columns(2)
    )

    with planning_column_1:
        planning_date_input = st.date_input(
            label="Planning Date",
            value=date.today(),
            help=(
                "Operational date for the workforce "
                "capacity decision."
            ),
        )

        expected_order_lines_input = st.number_input(
            label="Expected Order Lines",
            min_value=1.0,
            value=12_000.0,
            step=500.0,
            format="%.0f",
            help=(
                "Expected workload expressed as "
                "order lines."
            ),
        )

        available_associates_input = st.number_input(
            label="Available Associates",
            min_value=0,
            value=50,
            step=1,
            help=(
                "Associates currently available "
                "for the planning period."
            ),
        )

    with planning_column_2:
        productivity_input = st.number_input(
            label="Productivity — Lines per Hour",
            min_value=0.01,
            value=20.0,
            step=1.0,
            format="%.2f",
            help=(
                "Expected average associate "
                "productivity."
            ),
        )

        scheduled_hours_input = st.number_input(
            label="Scheduled Hours",
            min_value=0.01,
            value=10.0,
            step=0.5,
            format="%.2f",
            help=(
                "Scheduled working hours for "
                "the planning period."
            ),
        )

        forecast_confidence_input = st.slider(
            label="Forecast Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.90,
            step=0.01,
            help=(
                "Confidence associated with the "
                "demand expectation."
            ),
        )

    with st.expander(
        "Advanced Planning Context"
    ):

        advanced_column_1, advanced_column_2 = (
            st.columns(2)
        )

        with advanced_column_1:
            recurring_shortage_days_input = (
                st.number_input(
                    label="Recurring Shortage Days",
                    min_value=0,
                    value=0,
                    step=1,
                )
            )

            overtime_dependency_days_input = (
                st.number_input(
                    label="Overtime Dependency Days",
                    min_value=0,
                    value=0,
                    step=1,
                )
            )

        with advanced_column_2:
            recurring_surplus_days_input = (
                st.number_input(
                    label="Recurring Surplus Days",
                    min_value=0,
                    value=0,
                    step=1,
                )
            )

            planning_horizon_days_input = (
                st.number_input(
                    label="Planning Horizon Days",
                    min_value=1,
                    max_value=365,
                    value=30,
                    step=1,
                )
            )

    submitted = st.form_submit_button(
        label="Run Workforce Decision",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# Execute Enterprise Decision
# ============================================================

if submitted:

    decision_payload = {
        "planning_date": (
            planning_date_input.isoformat()
        ),
        "expected_order_lines": float(
            expected_order_lines_input
        ),
        "available_associates": int(
            available_associates_input
        ),
        "productivity_lines_per_hour": float(
            productivity_input
        ),
        "scheduled_hours": float(
            scheduled_hours_input
        ),
        "forecast_confidence": float(
            forecast_confidence_input
        ),
        "recurring_shortage_days": int(
            recurring_shortage_days_input
        ),
        "recurring_surplus_days": int(
            recurring_surplus_days_input
        ),
        "overtime_dependency_days": int(
            overtime_dependency_days_input
        ),
        "planning_horizon_days": int(
            planning_horizon_days_input
        ),
    }

    st.session_state[
        DECISION_REQUEST_STATE_KEY
    ] = decision_payload

    with st.spinner(
        "Running enterprise workforce decision..."
    ):

        try:
            decision_response = call_api(
                api_service=enterprise_api,
                path=ENDPOINT_DECISION,
                method=HTTP_METHOD_POST,
                operation=OPERATION_CREATE_DECISION,
                payload=decision_payload,
            )

            st.session_state[
                DECISION_RESPONSE_STATE_KEY
            ] = decision_response

        except Exception as exc:
            st.error(
                "Enterprise decision execution failed."
            )

            st.exception(exc)


# ============================================================
# Decision Results
# ============================================================

decision_response = st.session_state.get(
    DECISION_RESPONSE_STATE_KEY
)

if decision_response is not None:

    st.divider()

    st.header(
        "Enterprise Decision Result"
    )

    if (
        isinstance(
            decision_response,
            APIResponse,
        )
        and decision_response.http_status == 200
        and decision_response.status == "SUCCESS"
    ):

        st.success(
            "Enterprise workforce decision completed successfully."
        )

        render_decision_payload(
            response=decision_response,
        )

    elif isinstance(
        decision_response,
        APIResponse,
    ):

        render_api_error(
            response=decision_response,
        )

    else:
        st.error(
            "Stored decision response is not "
            "a valid APIResponse."
        )


# ============================================================
# Platform Health and Administration
# ============================================================

st.divider()

with st.expander(
    "Platform Health and Administration"
):

    st.subheader(
        "Enterprise API Health"
    )

    try:
        health_response = call_api(
            api_service=enterprise_api,
            path=ENDPOINT_HEALTH,
            method=HTTP_METHOD_GET,
            operation=OPERATION_HEALTH_CHECK,
        )

        if (
            health_response.http_status == 200
            and bool(
                health_response.payload.get(
                    "healthy",
                    False,
                )
            )
        ):
            st.success(
                "Enterprise API is healthy."
            )

        else:
            st.warning(
                "Enterprise API health check "
                "returned a non-healthy state."
            )

        st.json(
            dict(
                health_response.payload
            )
        )

    except Exception as exc:
        st.error(
            "Enterprise API health validation failed."
        )

        st.exception(exc)

    st.subheader(
        "Enterprise Platform Health"
    )

    try:
        platform_health_response = call_api(
            api_service=enterprise_api,
            path=ENDPOINT_PLATFORM_HEALTH,
            method=HTTP_METHOD_GET,
            operation=OPERATION_PLATFORM_HEALTH,
        )

        if (
            platform_health_response.http_status
            == 200
            and bool(
                platform_health_response
                .payload
                .get(
                    "healthy",
                    False,
                )
            )
        ):
            st.success(
                "Enterprise platform is healthy."
            )

        else:
            st.warning(
                "Enterprise platform health check "
                "returned a non-healthy state."
            )

        st.json(
            dict(
                platform_health_response.payload
            )
        )

    except Exception as exc:
        st.error(
            "Platform health validation failed."
        )

        st.exception(exc)

    with st.expander(
        "Application Bootstrap Details"
    ):
        st.json(
            application_context.as_dict()
        )


# ============================================================
# Deployment Footer
# ============================================================

st.divider()

st.caption(
    "Implementation 30.1 • "
    "Enterprise Workforce Decision Workspace • "
    "Paid Databricks reference deployment • "
    "Platform v3.0.0"
)