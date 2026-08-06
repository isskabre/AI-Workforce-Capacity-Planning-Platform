"""
Enterprise Decision Report Formatter

Formats validated enterprise decision reports into dictionary,
JSON, or human-readable text representations.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

import json
from typing import Any

from .configuration import ReportingConfiguration
from .exceptions import (
    ReportingFormattingError,
    ReportingValidationError,
)
from .models import (
    EnterpriseDecisionReport,
    ReportFormat,
)


class EnterpriseDecisionReportFormatter:
    """
    Format enterprise decision reports for downstream consumers.

    Supported outputs:

    - Dictionary for dashboards and internal Python consumers
    - JSON for APIs, persistence, and external integrations
    - Text for operational review and human-readable summaries
    """

    def __init__(
        self,
        *,
        configuration: ReportingConfiguration | None = None,
    ) -> None:
        """
        Initialize the report formatter.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else ReportingConfiguration()
        )

        if not isinstance(
            self._configuration,
            ReportingConfiguration,
        ):
            raise ReportingValidationError(
                "configuration must be a ReportingConfiguration."
            )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def format(
        self,
        *,
        report: EnterpriseDecisionReport,
        report_format: ReportFormat,
    ) -> dict[str, Any] | str:
        """
        Format one enterprise decision report.

        Parameters
        ----------
        report:
            Validated enterprise decision report.

        report_format:
            Requested output representation.

        Returns
        -------
        dict[str, Any] | str
            Dictionary, JSON string, or human-readable text.

        Raises
        ------
        ReportingValidationError
            If the request types are invalid.

        ReportingFormattingError
            If formatting fails unexpectedly.
        """

        if not isinstance(report, EnterpriseDecisionReport):
            raise ReportingValidationError(
                "report must be an EnterpriseDecisionReport."
            )

        if not isinstance(report_format, ReportFormat):
            raise ReportingValidationError(
                "report_format must be a ReportFormat."
            )

        try:
            if report_format is ReportFormat.DICT:
                return self.to_dict(report=report)

            if report_format is ReportFormat.JSON:
                return self.to_json(report=report)

            if report_format is ReportFormat.TEXT:
                return self.to_text(report=report)

            raise ReportingFormattingError(
                f"Unsupported report format: {report_format}."
            )

        except (
            ReportingValidationError,
            ReportingFormattingError,
        ):
            raise

        except Exception as exc:
            raise ReportingFormattingError(
                "Enterprise decision report formatting failed."
            ) from exc

    def to_dict(
        self,
        *,
        report: EnterpriseDecisionReport,
    ) -> dict[str, Any]:
        """
        Convert a report into a serializable dictionary.
        """

        self._validate_report(report)

        return report.as_dict()

    def to_json(
        self,
        *,
        report: EnterpriseDecisionReport,
    ) -> str:
        """
        Convert a report into a formatted JSON string.
        """

        self._validate_report(report)

        try:
            return json.dumps(
                report.as_dict(),
                indent=self._configuration.indent_size,
                ensure_ascii=False,
                sort_keys=False,
            )

        except (TypeError, ValueError) as exc:
            raise ReportingFormattingError(
                "Report could not be serialized to JSON."
            ) from exc

    def to_text(
        self,
        *,
        report: EnterpriseDecisionReport,
    ) -> str:
        """
        Convert a report into a human-readable text document.
        """

        self._validate_report(report)

        lines: list[str] = [
            report.title,
            "=" * len(report.title),
            "",
            f"Report ID: {report.report_id}",
            f"Report Type: {report.report_type.value}",
            f"Status: {report.status.value}",
            f"Planning Date: {report.planning_date.isoformat()}",
            (
                "Generated At: "
                f"{report.generated_at_utc.strftime(
                    self._configuration.datetime_format
                )}"
            ),
            "",
            "Summary",
            "-------",
            report.summary,
            "",
        ]

        for section in report.sections:
            lines.extend(
                [
                    section.name,
                    "-" * len(section.name),
                ]
            )

            if section.content:
                for key, value in section.content.items():
                    lines.append(
                        f"{self._humanize_key(key)}: "
                        f"{self._format_value(value)}"
                    )
            else:
                lines.append("No material data.")

            lines.append("")

        if report.metadata:
            lines.extend(
                [
                    "Report Metadata",
                    "---------------",
                ]
            )

            for key, value in report.metadata.items():
                lines.append(
                    f"{self._humanize_key(key)}: "
                    f"{self._format_value(value)}"
                )

            lines.append("")

        lines.extend(
            [
                f"Source Workflow Version: "
                f"{report.source_workflow_version}",
                f"Report Version: {report.report_version}",
            ]
        )

        return "\n".join(lines).strip()

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _validate_report(
        report: EnterpriseDecisionReport,
    ) -> None:
        """
        Validate the report supplied to a formatter method.
        """

        if not isinstance(report, EnterpriseDecisionReport):
            raise ReportingValidationError(
                "report must be an EnterpriseDecisionReport."
            )

    @staticmethod
    def _humanize_key(key: Any) -> str:
        """
        Convert a machine-oriented key into a readable label.
        """

        return str(key).replace("_", " ").strip().title()

    @classmethod
    def _format_value(cls, value: Any) -> str:
        """
        Convert a structured value into readable text.
        """

        if value is None:
            return "N/A"

        if isinstance(value, bool):
            return "Yes" if value else "No"

        if isinstance(value, float):
            return cls._format_float(value)

        if isinstance(value, dict):
            return json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
            )

        if isinstance(value, (list, tuple, set)):
            return ", ".join(
                cls._format_value(item)
                for item in value
            )

        return str(value)

    @staticmethod
    def _format_float(value: float) -> str:
        """
        Format a floating-point value without unnecessary zeros.
        """

        if value.is_integer():
            return f"{value:,.0f}"

        return f"{value:,.2f}"

    # ---------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------

    @property
    def configuration(self) -> ReportingConfiguration:
        """
        Return the active reporting configuration.
        """

        return self._configuration


__all__ = [
    "EnterpriseDecisionReportFormatter",
]