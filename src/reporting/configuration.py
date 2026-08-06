"""
Enterprise Decision Reporting Configuration

Validated configuration contract for enterprise decision reporting.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import (
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_REPORT_FORMAT,
    DEFAULT_REPORT_SECTIONS,
    DEFAULT_REPORT_TYPE,
    DEFAULT_REPORT_VERSION,
    INDENT_SIZE,
    MAX_REPORT_SUMMARY_LENGTH,
    MAX_REPORT_TITLE_LENGTH,
    SUPPORTED_REPORT_FORMATS,
    SUPPORTED_REPORT_TYPES,
)
from .exceptions import ReportingConfigurationError


@dataclass(frozen=True, slots=True)
class ReportingConfiguration:
    """
    Configuration contract for enterprise report generation.

    Parameters
    ----------
    default_report_type:
        Default report audience classification.

    default_report_format:
        Default output representation.

    include_metadata:
        Whether metadata is included by default.

    include_rationale:
        Whether decision rationale is included by default.

    include_empty_sections:
        Whether empty sections are retained.

    section_order:
        Ordered report sections.

    indent_size:
        JSON indentation size.

    datetime_format:
        Human-readable datetime format.

    maximum_title_length:
        Maximum accepted report-title length.

    maximum_summary_length:
        Maximum accepted report-summary length.

    report_version:
        Semantic version of the reporting configuration.
    """

    default_report_type: str = DEFAULT_REPORT_TYPE

    default_report_format: str = DEFAULT_REPORT_FORMAT

    include_metadata: bool = True

    include_rationale: bool = True

    include_empty_sections: bool = False

    section_order: tuple[str, ...] = DEFAULT_REPORT_SECTIONS

    indent_size: int = INDENT_SIZE

    datetime_format: str = DEFAULT_DATETIME_FORMAT

    maximum_title_length: int = MAX_REPORT_TITLE_LENGTH

    maximum_summary_length: int = MAX_REPORT_SUMMARY_LENGTH

    report_version: str = DEFAULT_REPORT_VERSION

    def __post_init__(self) -> None:
        """Validate the reporting configuration."""

        if self.default_report_type not in SUPPORTED_REPORT_TYPES:
            raise ReportingConfigurationError(
                "default_report_type is not supported."
            )

        if self.default_report_format not in SUPPORTED_REPORT_FORMATS:
            raise ReportingConfigurationError(
                "default_report_format is not supported."
            )

        boolean_fields = {
            "include_metadata": self.include_metadata,
            "include_rationale": self.include_rationale,
            "include_empty_sections": self.include_empty_sections,
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise ReportingConfigurationError(
                    f"{field_name} must be a boolean."
                )

        if not isinstance(self.section_order, tuple):
            raise ReportingConfigurationError(
                "section_order must be a tuple."
            )

        if not self.section_order:
            raise ReportingConfigurationError(
                "section_order must not be empty."
            )

        if len(self.section_order) != len(set(self.section_order)):
            raise ReportingConfigurationError(
                "section_order must not contain duplicate sections."
            )

        for section_name in self.section_order:
            if (
                not isinstance(section_name, str)
                or not section_name.strip()
            ):
                raise ReportingConfigurationError(
                    "Every section name must be a non-empty string."
                )

        if (
            not isinstance(self.indent_size, int)
            or isinstance(self.indent_size, bool)
            or self.indent_size < 0
        ):
            raise ReportingConfigurationError(
                "indent_size must be a non-negative integer."
            )

        if (
            not isinstance(self.datetime_format, str)
            or not self.datetime_format.strip()
        ):
            raise ReportingConfigurationError(
                "datetime_format must not be empty."
            )

        if (
            not isinstance(self.maximum_title_length, int)
            or isinstance(self.maximum_title_length, bool)
            or self.maximum_title_length <= 0
        ):
            raise ReportingConfigurationError(
                "maximum_title_length must be a positive integer."
            )

        if (
            not isinstance(self.maximum_summary_length, int)
            or isinstance(self.maximum_summary_length, bool)
            or self.maximum_summary_length <= 0
        ):
            raise ReportingConfigurationError(
                "maximum_summary_length must be a positive integer."
            )

        if (
            self.maximum_summary_length
            <= self.maximum_title_length
        ):
            raise ReportingConfigurationError(
                "maximum_summary_length must exceed "
                "maximum_title_length."
            )

        if (
            not isinstance(self.report_version, str)
            or not self.report_version.strip()
        ):
            raise ReportingConfigurationError(
                "report_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """Return the configuration as a serializable dictionary."""

        payload = asdict(self)
        payload["section_order"] = list(self.section_order)

        return payload


__all__ = [
    "ReportingConfiguration",
]