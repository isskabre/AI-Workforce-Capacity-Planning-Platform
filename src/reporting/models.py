"""
Enterprise Decision Reporting Models

Typed contracts for executive, operational, and technical reports
generated from enterprise decision orchestration results.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Mapping

from .constants import (
    MAX_REPORT_SUMMARY_LENGTH,
    MAX_REPORT_TITLE_LENGTH,
    SUPPORTED_REPORT_FORMATS,
    SUPPORTED_REPORT_STATUSES,
    SUPPORTED_REPORT_TYPES,
)
from .exceptions import ReportingValidationError


# ============================================================
# Enumerations
# ============================================================

class ReportFormat(str, Enum):
    """Supported report output formats."""

    JSON = "json"
    DICT = "dict"
    TEXT = "text"


class ReportType(str, Enum):
    """Supported enterprise report types."""

    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"


class ReportStatus(str, Enum):
    """Report generation and business status."""

    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ============================================================
# Report Section
# ============================================================

@dataclass(frozen=True, slots=True)
class ReportSection:
    """
    One named section within an enterprise decision report.

    Parameters
    ----------
    name:
        Human-readable section name.

    content:
        Structured section payload.

    order:
        Display order within the report.
    """

    name: str

    content: Mapping[str, Any]

    order: int

    def __post_init__(self) -> None:
        """Validate the report section."""

        if not isinstance(self.name, str) or not self.name.strip():
            raise ReportingValidationError(
                "Report section name must not be empty."
            )

        if not isinstance(self.content, Mapping):
            raise ReportingValidationError(
                "Report section content must be a mapping."
            )

        if (
            not isinstance(self.order, int)
            or isinstance(self.order, bool)
            or self.order < 0
        ):
            raise ReportingValidationError(
                "Report section order must be a non-negative integer."
            )

    def as_dict(self) -> dict[str, Any]:
        """Return the section as a serializable dictionary."""

        return {
            "name": self.name,
            "content": dict(self.content),
            "order": self.order,
        }


# ============================================================
# Report Request
# ============================================================

@dataclass(frozen=True, slots=True)
class DecisionReportRequest:
    """
    Request contract for enterprise report generation.

    Parameters
    ----------
    report_type:
        Executive, operational, or technical report.

    report_format:
        Requested output representation.

    title:
        Human-readable report title.

    include_metadata:
        Whether metadata should be included.

    include_rationale:
        Whether decision rationale should be included.

    include_empty_sections:
        Whether sections without material data should be retained.
    """

    report_type: ReportType

    report_format: ReportFormat

    title: str

    include_metadata: bool = True

    include_rationale: bool = True

    include_empty_sections: bool = False

    def __post_init__(self) -> None:
        """Validate the reporting request."""

        if not isinstance(self.report_type, ReportType):
            raise ReportingValidationError(
                "report_type must be a ReportType."
            )

        if self.report_type.value not in SUPPORTED_REPORT_TYPES:
            raise ReportingValidationError(
                "Unsupported report_type."
            )

        if not isinstance(self.report_format, ReportFormat):
            raise ReportingValidationError(
                "report_format must be a ReportFormat."
            )

        if self.report_format.value not in SUPPORTED_REPORT_FORMATS:
            raise ReportingValidationError(
                "Unsupported report_format."
            )

        if not isinstance(self.title, str) or not self.title.strip():
            raise ReportingValidationError(
                "Report title must not be empty."
            )

        if len(self.title) > MAX_REPORT_TITLE_LENGTH:
            raise ReportingValidationError(
                f"Report title cannot exceed "
                f"{MAX_REPORT_TITLE_LENGTH} characters."
            )

        boolean_fields = {
            "include_metadata": self.include_metadata,
            "include_rationale": self.include_rationale,
            "include_empty_sections": self.include_empty_sections,
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise ReportingValidationError(
                    f"{field_name} must be a boolean."
                )

    def as_dict(self) -> dict[str, Any]:
        """Return the request as a serializable dictionary."""

        return {
            "report_type": self.report_type.value,
            "report_format": self.report_format.value,
            "title": self.title,
            "include_metadata": self.include_metadata,
            "include_rationale": self.include_rationale,
            "include_empty_sections": self.include_empty_sections,
        }


# ============================================================
# Enterprise Decision Report
# ============================================================

@dataclass(frozen=True, slots=True)
class EnterpriseDecisionReport:
    """
    Structured enterprise workforce decision report.

    Parameters
    ----------
    report_id:
        Stable identifier for the generated report.

    report_type:
        Report audience and detail classification.

    status:
        Report status.

    title:
        Report title.

    summary:
        Concise business summary.

    planning_date:
        Business date represented by the report.

    sections:
        Ordered report sections.

    generated_at_utc:
        UTC report-generation timestamp.

    source_workflow_version:
        Version of the orchestration result used to generate the report.

    report_version:
        Version of the reporting contract.

    metadata:
        Optional structured report metadata.
    """

    report_id: str

    report_type: ReportType

    status: ReportStatus

    title: str

    summary: str

    planning_date: date

    sections: tuple[ReportSection, ...]

    generated_at_utc: datetime

    source_workflow_version: str

    report_version: str = "1.0.0"

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the complete report contract."""

        if (
            not isinstance(self.report_id, str)
            or not self.report_id.strip()
        ):
            raise ReportingValidationError(
                "report_id must not be empty."
            )

        if not isinstance(self.report_type, ReportType):
            raise ReportingValidationError(
                "report_type must be a ReportType."
            )

        if not isinstance(self.status, ReportStatus):
            raise ReportingValidationError(
                "status must be a ReportStatus."
            )

        if self.status.value not in SUPPORTED_REPORT_STATUSES:
            raise ReportingValidationError(
                "Unsupported report status."
            )

        if not isinstance(self.title, str) or not self.title.strip():
            raise ReportingValidationError(
                "Report title must not be empty."
            )

        if len(self.title) > MAX_REPORT_TITLE_LENGTH:
            raise ReportingValidationError(
                f"Report title cannot exceed "
                f"{MAX_REPORT_TITLE_LENGTH} characters."
            )

        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ReportingValidationError(
                "Report summary must not be empty."
            )

        if len(self.summary) > MAX_REPORT_SUMMARY_LENGTH:
            raise ReportingValidationError(
                f"Report summary cannot exceed "
                f"{MAX_REPORT_SUMMARY_LENGTH} characters."
            )

        if not isinstance(self.planning_date, date):
            raise ReportingValidationError(
                "planning_date must be a date."
            )

        if not isinstance(self.sections, tuple):
            raise ReportingValidationError(
                "sections must be a tuple."
            )

        if not self.sections:
            raise ReportingValidationError(
                "Report must contain at least one section."
            )

        for section in self.sections:
            if not isinstance(section, ReportSection):
                raise ReportingValidationError(
                    "Every report section must be a ReportSection."
                )

        section_orders = tuple(
            section.order for section in self.sections
        )

        if len(section_orders) != len(set(section_orders)):
            raise ReportingValidationError(
                "Report section order values must be unique."
            )

        if section_orders != tuple(sorted(section_orders)):
            raise ReportingValidationError(
                "Report sections must be sorted by order."
            )

        section_names = tuple(
            section.name for section in self.sections
        )

        if len(section_names) != len(set(section_names)):
            raise ReportingValidationError(
                "Report section names must be unique."
            )

        if not isinstance(self.generated_at_utc, datetime):
            raise ReportingValidationError(
                "generated_at_utc must be a datetime."
            )

        if (
            not isinstance(self.source_workflow_version, str)
            or not self.source_workflow_version.strip()
        ):
            raise ReportingValidationError(
                "source_workflow_version must not be empty."
            )

        if (
            not isinstance(self.report_version, str)
            or not self.report_version.strip()
        ):
            raise ReportingValidationError(
                "report_version must not be empty."
            )

        if not isinstance(self.metadata, Mapping):
            raise ReportingValidationError(
                "metadata must be a mapping."
            )

    def as_dict(self) -> dict[str, Any]:
        """Return the report as a serializable dictionary."""

        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "status": self.status.value,
            "title": self.title,
            "summary": self.summary,
            "planning_date": self.planning_date.isoformat(),
            "sections": [
                section.as_dict()
                for section in self.sections
            ],
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "source_workflow_version": (
                self.source_workflow_version
            ),
            "report_version": self.report_version,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "DecisionReportRequest",
    "EnterpriseDecisionReport",
    "ReportFormat",
    "ReportSection",
    "ReportStatus",
    "ReportType",
]