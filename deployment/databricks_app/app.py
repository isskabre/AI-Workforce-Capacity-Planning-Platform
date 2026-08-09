"""
AI Workforce Capacity Planning Platform
Deployment Phase — Paid Databricks Reference Deployment

Module:
    deployment.databricks_app.app

Description:
    Thin Streamlit deployment adapter for the validated v3.0.0
    AI Workforce Capacity Planning Platform.

    This module does not implement business-domain logic. It bootstraps
    the existing enterprise application runtime and exposes deployment
    health information through Databricks Apps.

    Initial deployment scope:
        - Enterprise application bootstrap
        - Application context validation
        - Enterprise API service resolution
        - Public API health validation
        - Platform health validation

    Workforce planning, recommendations, reporting, monitoring views,
    and natural-language interaction will be added after the baseline
    Databricks Apps runtime has been validated successfully.

Author:
    AI Workforce Capacity Planning Platform

Platform Version:
    3.0.0
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st


# ---------------------------------------------------------------------
# Repository import path
# ---------------------------------------------------------------------
#
# Databricks Apps launches this module from:
#
#     <repository-root>/deployment/databricks_app/app.py
#
# The validated enterprise Python packages live under:
#
#     <repository-root>/src/
#
# Explicitly registering the repository root keeps this deployment
# adapter independent from the current working directory used by the
# Databricks Apps runtime.
# ---------------------------------------------------------------------

APP_FILE = Path(__file__).resolve()
REPOSITORY_ROOT = APP_FILE.parents[2]

repository_root_string = str(REPOSITORY_ROOT)

if repository_root_string not in sys.path:
    sys.path.insert(0, repository_root_string)


# ---------------------------------------------------------------------
# Enterprise platform imports
# ---------------------------------------------------------------------

from src.api.models import APIRequest, APIRequestMetadata
from src.application import (
    ApplicationConfiguration,
    ApplicationEnvironment,
    EnterpriseApplicationBootstrap,
    SERVICE_API,
)


# ---------------------------------------------------------------------
# Deployment constants
# ---------------------------------------------------------------------

APP_TITLE = "AI Workforce Capacity Planning"
APP_SUBTITLE = "Enterprise Decision Intelligence Platform"

REQUEST_SOURCE = "databricks-app"

HEALTH_OPERATION = "health_check"
PLATFORM_HEALTH_OPERATION = "platform_health"


# ---------------------------------------------------------------------
# Runtime bootstrap
# ---------------------------------------------------------------------

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
            "deployment_target": "databricks_apps",
            "deployment_environment": "paid_databricks_reference",
            "deployment_adapter": "streamlit",
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


# ---------------------------------------------------------------------
# API request construction
# ---------------------------------------------------------------------

def build_api_request(
    *,
    operation: str,
    payload: dict[str, Any] | None = None,
) -> APIRequest:
    """
    Construct one transport-neutral enterprise API request.
    """

    return APIRequest(
        operation=operation,
        payload={} if payload is None else payload,
        metadata=APIRequestMetadata(
            request_id=f"req-{uuid4().hex}",
            correlation_id=f"corr-{uuid4().hex}",
            source=REQUEST_SOURCE,
            received_at_utc=datetime.now(timezone.utc),
        ),
    )


def call_api(
    *,
    api_service: Any,
    path: str,
    method: str,
    operation: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    """
    Dispatch one request through the validated Enterprise API Service.
    """

    request = build_api_request(
        operation=operation,
        payload=payload,
    )

    return api_service.handle(
        path=path,
        method=method,
        request=request,
    )


# ---------------------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

st.markdown(
    """
    This application is the deployment interface for the validated
    **AI Workforce Capacity Planning Platform v3.0.0**.
    """
)


# ---------------------------------------------------------------------
# Bootstrap enterprise runtime
# ---------------------------------------------------------------------

try:
    application_context, enterprise_api = bootstrap_platform()

except Exception as exc:
    st.error(
        "The enterprise platform could not be initialized."
    )

    st.exception(exc)
    st.stop()


# ---------------------------------------------------------------------
# Application runtime status
# ---------------------------------------------------------------------

descriptor = application_context.descriptor

status_column, version_column, environment_column = st.columns(3)

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
        value=descriptor.environment.value.upper(),
    )


# ---------------------------------------------------------------------
# API endpoint paths
# ---------------------------------------------------------------------

api_configuration = enterprise_api.configuration

base_path = api_configuration.base_path.rstrip("/")
api_version = api_configuration.api_version.strip("/")

versioned_base_path = f"{base_path}/{api_version}"

health_path = f"{versioned_base_path}/health"
platform_health_path = f"{versioned_base_path}/health/platform"


# ---------------------------------------------------------------------
# Public API health
# ---------------------------------------------------------------------

st.divider()

st.subheader("Enterprise API Health")

try:
    health_response = call_api(
        api_service=enterprise_api,
        path=health_path,
        method="GET",
        operation=HEALTH_OPERATION,
    )

    if health_response.http_status == 200:
        st.success("Enterprise API is healthy.")
    else:
        st.warning(
            f"Enterprise API returned HTTP "
            f"{health_response.http_status}."
        )

    st.json(dict(health_response.payload))

except Exception as exc:
    st.error("Enterprise API health validation failed.")
    st.exception(exc)


# ---------------------------------------------------------------------
# Platform health
# ---------------------------------------------------------------------

st.subheader("Platform Health")

try:
    platform_health_response = call_api(
        api_service=enterprise_api,
        path=platform_health_path,
        method="GET",
        operation=PLATFORM_HEALTH_OPERATION,
    )

    if platform_health_response.http_status == 200:
        st.success("Enterprise platform is healthy.")
    else:
        st.warning(
            f"Platform health returned HTTP "
            f"{platform_health_response.http_status}."
        )

    st.json(dict(platform_health_response.payload))

except Exception as exc:
    st.error("Platform health validation failed.")
    st.exception(exc)


# ---------------------------------------------------------------------
# Bootstrap lifecycle
# ---------------------------------------------------------------------

with st.expander("Application Bootstrap Details"):
    st.json(application_context.as_dict())


# ---------------------------------------------------------------------
# Deployment footer
# ---------------------------------------------------------------------

st.divider()

st.caption(
    "Paid Databricks reference deployment • "
    "Validated enterprise runtime • "
    "Platform v3.0.0"
)