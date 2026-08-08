"""
Enterprise Decision Reporting

Public API for the enterprise decision reporting domain.

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
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_REPORT_FORMAT,
    DEFAULT_REPORT_SECTIONS,
    DEFAULT_REPORT_TYPE,
    DEFAULT_REPORT_VERSION,
    DEFAULT_TIMEZONE,
    INDENT_SIZE,
    MAX_REPORT_SUMMARY_LENGTH,
    MAX_REPORT_TITLE_LENGTH,
    REPORT_FORMAT_DICT,
    REPORT_FORMAT_JSON,
    REPORT_FORMAT_TEXT,
    REPORT_STATUS_ERROR,
    REPORT_STATUS_SUCCESS,
    REPORT_STATUS_WARNING,
    REPORT_TYPE_EXECUTIVE,
    REPORT_TYPE_OPERATIONAL,
    REPORT_TYPE_TECHNICAL,
    REPORTING_DOMAIN_VERSION,
    SECTION_EXECUTIVE_SUMMARY,
    SECTION_FORECAST,
    SECTION_METADATA,
    SECTION_OPTIMIZATION,
    SECTION_OVERTIME,
    SECTION_PLANNING,
    SECTION_STAFFING,
    SUPPORTED_REPORT_FORMATS,
    SUPPORTED_REPORT_STATUSES,
    SUPPORTED_REPORT_TYPES,
)

# ============================================================
# Exceptions
# ============================================================

from .exceptions import (
    ReportingConfigurationError,
    ReportingError,
    ReportingFormattingError,
    ReportingServiceError,
    ReportingValidationError,
)

# ============================================================
# Models
# ============================================================

from .models import (
    DecisionReportRequest,
    EnterpriseDecisionReport,
    ReportFormat,
    ReportSection,
    ReportStatus,
    ReportType,
)

# ============================================================
# Components
# ============================================================

from .configuration import ReportingConfiguration
from .formatter import EnterpriseDecisionReportFormatter
from .service import EnterpriseDecisionReportingService


__all__ = [
    # Version
    "REPORTING_DOMAIN_VERSION",

    # Formats
    "REPORT_FORMAT_JSON",
    "REPORT_FORMAT_DICT",
    "REPORT_FORMAT_TEXT",
    "SUPPORTED_REPORT_FORMATS",
    "DEFAULT_REPORT_FORMAT",

    # Types
    "REPORT_TYPE_EXECUTIVE",
    "REPORT_TYPE_OPERATIONAL",
    "REPORT_TYPE_TECHNICAL",
    "SUPPORTED_REPORT_TYPES",
    "DEFAULT_REPORT_TYPE",

    # Statuses
    "REPORT_STATUS_SUCCESS",
    "REPORT_STATUS_WARNING",
    "REPORT_STATUS_ERROR",
    "SUPPORTED_REPORT_STATUSES",

    # Metadata and formatting
    "DEFAULT_TIMEZONE",
    "DEFAULT_REPORT_VERSION",
    "DEFAULT_DATETIME_FORMAT",
    "INDENT_SIZE",
    "MAX_REPORT_TITLE_LENGTH",
    "MAX_REPORT_SUMMARY_LENGTH",

    # Sections
    "SECTION_EXECUTIVE_SUMMARY",
    "SECTION_FORECAST",
    "SECTION_PLANNING",
    "SECTION_OVERTIME",
    "SECTION_STAFFING",
    "SECTION_OPTIMIZATION",
    "SECTION_METADATA",
    "DEFAULT_REPORT_SECTIONS",

    # Exceptions
    "ReportingError",
    "ReportingValidationError",
    "ReportingConfigurationError",
    "ReportingFormattingError",
    "ReportingServiceError",

    # Models and enums
    "DecisionReportRequest",
    "EnterpriseDecisionReport",
    "ReportFormat",
    "ReportSection",
    "ReportStatus",
    "ReportType",

    # Components
    "ReportingConfiguration",
    "EnterpriseDecisionReportFormatter",
    "EnterpriseDecisionReportingService",
]