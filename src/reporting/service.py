"""
Enterprise Decision Reporting Service

Builds and formats executive, operational, and technical reports from
enterprise decision orchestration results.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.orchestration.models import EnterpriseDecisionResult

from .configuration import ReportingConfiguration
from .exceptions import (
    ReportingServiceError,
    ReportingValidationError,
)
from .formatter import EnterpriseDecisionReportFormatter
from .models import (
    DecisionReportRequest,
    EnterpriseDecisionReport,
    ReportFormat,
    ReportSection,
    ReportStatus,
    ReportType,
)


class EnterpriseDecisionReportingService:
    """
    Public application service for enterprise decision reporting.

    Responsibilities
    ----------------
    - Validate orchestration and reporting inputs.
    - Build audience-specific report sections.
    - Generate a concise business summary.
    - Create a validated EnterpriseDecisionReport.
    - Format the report for downstream consumers.
    """

    def __init__(
        self,
        *,
        configuration: ReportingConfiguration | None = None,
        formatter: EnterpriseDecisionReportFormatter | None = None,
    ) -> None:
        """
        Initialize the enterprise reporting service.
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
            raise ReportingServiceError(
                "configuration must be a ReportingConfiguration."
            )

        self._formatter = (
            formatter
            if formatter is not None
            else EnterpriseDecisionReportFormatter(
                configuration=self._configuration,
            )
        )

        if not isinstance(
            self._formatter,
            EnterpriseDecisionReportFormatter,
        ):
            raise ReportingServiceError(
                "formatter must be an "
                "EnterpriseDecisionReportFormatter."
            )

        if (
            self._formatter.configuration
            is not self._configuration
        ):
            raise ReportingValidationError(
                "configuration and formatter must reference the same "
                "ReportingConfiguration instance."
            )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate(
        self,
        *,
        decision_result: EnterpriseDecisionResult,
        request: DecisionReportRequest,
    ) -> dict[str, Any] | str:
        """
        Build and format one enterprise decision report.
        """

        report = self.build_report(
            decision_result=decision_result,
            request=request,
        )

        return self._formatter.format(
            report=report,
            report_format=request.report_format,
        )

    def build_report(
        self,
        *,
        decision_result: EnterpriseDecisionResult,
        request: DecisionReportRequest,
    ) -> EnterpriseDecisionReport:
        """
        Build one validated enterprise decision report.
        """

        if not isinstance(
            decision_result,
            EnterpriseDecisionResult,
        ):
            raise ReportingValidationError(
                "decision_result must be an EnterpriseDecisionResult."
            )

        if not isinstance(request, DecisionReportRequest):
            raise ReportingValidationError(
                "request must be a DecisionReportRequest."
            )

        try:
            sections = self._build_sections(
                decision_result=decision_result,
                request=request,
            )

            summary = self._build_summary(
                decision_result=decision_result,
                report_type=request.report_type,
            )

            metadata = (
                self._build_metadata(
                    decision_result=decision_result,
                )
                if request.include_metadata
                else {}
            )

            return EnterpriseDecisionReport(
                report_id=self._build_report_id(
                    decision_result=decision_result,
                    report_type=request.report_type,
                ),
                report_type=request.report_type,
                status=self._resolve_report_status(
                    decision_result=decision_result,
                ),
                title=request.title.strip(),
                summary=summary,
                planning_date=decision_result.planning_date,
                sections=sections,
                generated_at_utc=datetime.now(timezone.utc),
                source_workflow_version=(
                    decision_result.workflow_version
                ),
                report_version=(
                    self._configuration.report_version
                ),
                metadata=metadata,
            )

        except (
            ReportingValidationError,
            ReportingServiceError,
        ):
            raise

        except Exception as exc:
            raise ReportingServiceError(
                "Enterprise decision report generation failed."
            ) from exc

    # ---------------------------------------------------------
    # Section construction
    # ---------------------------------------------------------

    def _build_sections(
        self,
        *,
        decision_result: EnterpriseDecisionResult,
        request: DecisionReportRequest,
    ) -> tuple[ReportSection, ...]:
        """
        Build ordered report sections.
        """

        section_content = {
            "Executive Summary": (
                self._build_executive_section(
                    decision_result=decision_result,
                    include_rationale=request.include_rationale,
                )
            ),
            "Forecast": self._build_forecast_section(
                decision_result=decision_result,
            ),
            "Planning": self._build_planning_section(
                decision_result=decision_result,
            ),
            "Overtime": self._build_overtime_section(
                decision_result=decision_result,
            ),
            "Staffing": self._build_staffing_section(
                decision_result=decision_result,
            ),
            "Optimization": self._build_optimization_section(
                decision_result=decision_result,
                include_rationale=request.include_rationale,
            ),
            "Metadata": (
                self._build_metadata(
                    decision_result=decision_result,
                )
                if request.include_metadata
                else {}
            ),
        }

        allowed_sections = self._sections_for_report_type(
            report_type=request.report_type,
        )

        sections: list[ReportSection] = []

        for section_name in self._configuration.section_order:
            if section_name not in allowed_sections:
                continue

            content = section_content.get(section_name, {})

            if (
                not content
                and not request.include_empty_sections
            ):
                continue

            sections.append(
                ReportSection(
                    name=section_name,
                    content=content,
                    order=len(sections),
                )
            )

        if not sections:
            raise ReportingServiceError(
                "No report sections were generated."
            )

        return tuple(sections)

    @staticmethod
    def _sections_for_report_type(
        *,
        report_type: ReportType,
    ) -> tuple[str, ...]:
        """
        Resolve sections appropriate for the report audience.
        """

        if report_type is ReportType.EXECUTIVE:
            return (
                "Executive Summary",
                "Planning",
                "Optimization",
                "Metadata",
            )

        if report_type is ReportType.OPERATIONAL:
            return (
                "Executive Summary",
                "Forecast",
                "Planning",
                "Overtime",
                "Staffing",
                "Optimization",
                "Metadata",
            )

        if report_type is ReportType.TECHNICAL:
            return (
                "Executive Summary",
                "Forecast",
                "Planning",
                "Overtime",
                "Staffing",
                "Optimization",
                "Metadata",
            )

        raise ReportingValidationError(
            "Unsupported report type."
        )

    @staticmethod
    def _build_executive_section(
        *,
        decision_result: EnterpriseDecisionResult,
        include_rationale: bool,
    ) -> dict[str, Any]:
        """
        Build the executive decision section.
        """

        content: dict[str, Any] = {
            "workflow_status": (
                decision_result.workflow_status.value
            ),
            "optimization_action": (
                decision_result.optimization_action
            ),
            "optimization_priority": (
                decision_result.optimization_priority
            ),
            "optimization_status": (
                decision_result.optimization_status
            ),
            "associate_gap": decision_result.associate_gap,
            "recommended_associates": (
                decision_result.recommended_associates
            ),
        }

        if include_rationale:
            content["rationale"] = decision_result.rationale

        return content

    @staticmethod
    def _build_forecast_section(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> dict[str, Any]:
        """
        Build forecast-related report content.
        """

        return {
            "expected_order_lines": (
                decision_result.expected_order_lines
            ),
            "forecast_confidence": (
                decision_result.forecast_confidence
            ),
        }

    @staticmethod
    def _build_planning_section(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> dict[str, Any]:
        """
        Build workforce-planning report content.
        """

        return {
            "available_associates": (
                decision_result.available_associates
            ),
            "required_associates": (
                decision_result.required_associates
            ),
            "associate_gap": decision_result.associate_gap,
            "requires_action": (
                decision_result.associate_gap != 0
            ),
        }

    @staticmethod
    def _build_overtime_section(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> dict[str, Any]:
        """
        Build overtime recommendation content.
        """

        return {
            "recommendation": (
                decision_result.overtime_recommendation
            ),
            "overtime_hours": decision_result.overtime_hours,
        }

    @staticmethod
    def _build_staffing_section(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> dict[str, Any]:
        """
        Build strategic staffing recommendation content.
        """

        return {
            "recommendation": (
                decision_result.staffing_recommendation
            ),
            "recommended_associates": (
                decision_result.recommended_associates
            ),
        }

    @staticmethod
    def _build_optimization_section(
        *,
        decision_result: EnterpriseDecisionResult,
        include_rationale: bool,
    ) -> dict[str, Any]:
        """
        Build optimization-decision report content.
        """

        content: dict[str, Any] = {
            "action": decision_result.optimization_action,
            "priority": decision_result.optimization_priority,
            "status": decision_result.optimization_status,
        }

        if include_rationale:
            content["rationale"] = decision_result.rationale

        return content

    @staticmethod
    def _build_metadata(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> dict[str, Any]:
        """
        Build report metadata.
        """

        return {
            "workflow_status": (
                decision_result.workflow_status.value
            ),
            "completed_stage": (
                decision_result.completed_stage.value
            ),
            "workflow_version": (
                decision_result.workflow_version
            ),
            "source_generated_at_utc": (
                decision_result.generated_at_utc.isoformat()
            ),
        }

    # ---------------------------------------------------------
    # Summary and status
    # ---------------------------------------------------------

    @staticmethod
    def _build_summary(
        *,
        decision_result: EnterpriseDecisionResult,
        report_type: ReportType,
    ) -> str:
        """
        Build an audience-appropriate business summary.
        """

        gap = decision_result.associate_gap

        if gap > 0:
            gap_statement = (
                f"A workforce shortage of {gap} associates "
                "was identified."
            )
        elif gap < 0:
            gap_statement = (
                f"A workforce surplus of {abs(gap)} associates "
                "was identified."
            )
        else:
            gap_statement = (
                "Available workforce matches the calculated "
                "requirement."
            )

        action_statement = (
            f"The selected enterprise action is "
            f"{decision_result.optimization_action} with "
            f"{decision_result.optimization_priority} priority."
        )

        if report_type is ReportType.EXECUTIVE:
            return f"{gap_statement} {action_statement}"

        if report_type is ReportType.OPERATIONAL:
            return (
                f"{gap_statement} {action_statement} "
                f"Recommended associates: "
                f"{decision_result.recommended_associates}. "
                f"Recommended overtime hours: "
                f"{decision_result.overtime_hours:.1f}."
            )

        return (
            f"{gap_statement} {action_statement} "
            f"Workflow status: "
            f"{decision_result.workflow_status.value}; "
            f"completed stage: "
            f"{decision_result.completed_stage.value}; "
            f"forecast confidence: "
            f"{decision_result.forecast_confidence:.2f}."
        )

    @staticmethod
    def _resolve_report_status(
        *,
        decision_result: EnterpriseDecisionResult,
    ) -> ReportStatus:
        """
        Resolve report status from workflow and optimization outcomes.
        """

        if decision_result.workflow_status.value == "FAILED":
            return ReportStatus.ERROR

        if (
            decision_result.optimization_status
            in {"REVIEW", "CRITICAL"}
        ):
            return ReportStatus.WARNING

        return ReportStatus.SUCCESS

    @staticmethod
    def _build_report_id(
        *,
        decision_result: EnterpriseDecisionResult,
        report_type: ReportType,
    ) -> str:
        """
        Build a stable unique report identifier.
        """

        return (
            f"workforce-decision-"
            f"{decision_result.planning_date.isoformat()}-"
            f"{report_type.value}-"
            f"{uuid4().hex[:8]}"
        )

    # ---------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------

    @property
    def configuration(self) -> ReportingConfiguration:
        """
        Return the active reporting configuration.
        """

        return self._configuration

    @property
    def formatter(
        self,
    ) -> EnterpriseDecisionReportFormatter:
        """
        Return the active report formatter.
        """

        return self._formatter


__all__ = [
    "EnterpriseDecisionReportingService",
]