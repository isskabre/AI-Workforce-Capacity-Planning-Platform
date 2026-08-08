"""
Enterprise Decision Reporting Constants

Centralized constants used by the Enterprise Reporting domain.

Version:
    1.0.0

Author:
    AI Workforce Capacity Planning Platform
"""

from __future__ import annotations

# ---------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------

REPORTING_DOMAIN_VERSION = "1.0.0"

# ---------------------------------------------------------------------
# Report Formats
# ---------------------------------------------------------------------

REPORT_FORMAT_JSON = "json"
REPORT_FORMAT_DICT = "dict"
REPORT_FORMAT_TEXT = "text"

SUPPORTED_REPORT_FORMATS = (
    REPORT_FORMAT_JSON,
    REPORT_FORMAT_DICT,
    REPORT_FORMAT_TEXT,
)

DEFAULT_REPORT_FORMAT = REPORT_FORMAT_DICT

# ---------------------------------------------------------------------
# Report Types
# ---------------------------------------------------------------------

REPORT_TYPE_EXECUTIVE = "executive"
REPORT_TYPE_OPERATIONAL = "operational"
REPORT_TYPE_TECHNICAL = "technical"

SUPPORTED_REPORT_TYPES = (
    REPORT_TYPE_EXECUTIVE,
    REPORT_TYPE_OPERATIONAL,
    REPORT_TYPE_TECHNICAL,
)

DEFAULT_REPORT_TYPE = REPORT_TYPE_OPERATIONAL

# ---------------------------------------------------------------------
# Report Status
# ---------------------------------------------------------------------

REPORT_STATUS_SUCCESS = "SUCCESS"
REPORT_STATUS_WARNING = "WARNING"
REPORT_STATUS_ERROR = "ERROR"

SUPPORTED_REPORT_STATUSES = (
    REPORT_STATUS_SUCCESS,
    REPORT_STATUS_WARNING,
    REPORT_STATUS_ERROR,
)

# ---------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------

DEFAULT_TIMEZONE = "UTC"

DEFAULT_REPORT_VERSION = "1.0.0"

MAX_REPORT_TITLE_LENGTH = 200

MAX_REPORT_SUMMARY_LENGTH = 5000

# ---------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------

INDENT_SIZE = 4

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S UTC"

# ---------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------

SECTION_EXECUTIVE_SUMMARY = "Executive Summary"

SECTION_FORECAST = "Forecast"

SECTION_PLANNING = "Planning"

SECTION_OVERTIME = "Overtime"

SECTION_STAFFING = "Staffing"

SECTION_OPTIMIZATION = "Optimization"

SECTION_METADATA = "Metadata"

DEFAULT_REPORT_SECTIONS = (
    SECTION_EXECUTIVE_SUMMARY,
    SECTION_FORECAST,
    SECTION_PLANNING,
    SECTION_OVERTIME,
    SECTION_STAFFING,
    SECTION_OPTIMIZATION,
    SECTION_METADATA,
)