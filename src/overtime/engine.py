"""
Enterprise Overtime Recommendation — Engine

Core decision engine that converts a validated workforce shortage into
an actionable overtime or labor recommendation.

The engine contains no Spark, persistence, reporting, or user-interface
dependencies.
"""

from __future__ import annotations

from typing import Optional

from .configuration import OvertimeConfiguration
from .exceptions import (
    OvertimeEngineError,
    OvertimeValidationError,
)
from .models import (
    OvertimeRecommendation,
    OvertimeRequest,
    OvertimeType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)


# ============================================================
# Overtime Recommendation Engine
# ============================================================

class OvertimeRecommendationEngine:
    """
    Generate enterprise overtime and labor recommendations.

    Parameters
    ----------
    configuration:
        Validated overtime policy configuration. A default configuration
        is created when one is not supplied.
    """

    def __init__(
        self,
        *,
        configuration: Optional[OvertimeConfiguration] = None,
    ) -> None:
        """
        Initialize the overtime recommendation engine.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else OvertimeConfiguration()
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def recommend(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Generate one overtime or labor recommendation.

        Parameters
        ----------
        request:
            Validated overtime request containing the associate shortage
            and forecast confidence.

        Returns
        -------
        OvertimeRecommendation
            Standardized enterprise recommendation.

        Raises
        ------
        OvertimeValidationError
            If the request is not an OvertimeRequest.

        OvertimeEngineError
            If recommendation generation fails unexpectedly.
        """

        if not isinstance(request, OvertimeRequest):
            raise OvertimeValidationError(
                "request must be an OvertimeRequest."
            )

        try:
            if request.associate_gap == 0:
                return self._build_no_action_recommendation(
                    request=request,
                )

            if (
                request.forecast_confidence
                < self._configuration.low_confidence_threshold
            ):
                return self._build_low_confidence_recommendation(
                    request=request,
                )

            if (
                request.associate_gap
                <= self._configuration.voluntary_overtime_max_gap
            ):
                return self._build_voluntary_recommendation(
                    request=request,
                )

            if (
                request.associate_gap
                <= self._configuration.mandatory_overtime_max_gap
            ):
                return self._build_mandatory_recommendation(
                    request=request,
                )

            if (
                request.associate_gap
                < self._configuration.critical_shortage_gap
            ):
                return self._build_temporary_labor_recommendation(
                    request=request,
                )

            return self._build_critical_recommendation(
                request=request,
            )

        except (
            OvertimeValidationError,
            OvertimeEngineError,
        ):
            raise

        except Exception as exc:
            raise OvertimeEngineError(
                "Overtime recommendation generation failed."
            ) from exc

    # --------------------------------------------------------
    # Recommendation builders
    # --------------------------------------------------------

    def _build_no_action_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build a recommendation when no workforce shortage exists.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=RecommendationType.NONE,
            priority=RecommendationPriority.LOW,
            status=RecommendationStatus.NOT_REQUIRED,
            overtime_type=OvertimeType.NONE,
            overtime_hours=0.0,
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "Available workforce capacity meets the calculated "
                "requirement. No overtime action is required."
            ),
        )

    def _build_low_confidence_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build an operational-review recommendation for low confidence.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=RecommendationType.OPERATIONAL_REVIEW,
            priority=RecommendationPriority.MEDIUM,
            status=RecommendationStatus.REVIEW_REQUIRED,
            overtime_type=OvertimeType.NONE,
            overtime_hours=0.0,
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage requires attention, but the "
                "forecast confidence is below the configured decision "
                "threshold. Operational review is required before "
                "authorizing overtime."
            ),
        )

    def _build_voluntary_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build a voluntary-overtime recommendation.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                RecommendationType.VOLUNTARY_OVERTIME
            ),
            priority=RecommendationPriority.MEDIUM,
            status=RecommendationStatus.RECOMMENDED,
            overtime_type=OvertimeType.VOLUNTARY,
            overtime_hours=self._calculate_overtime_hours(
                associate_gap=request.associate_gap,
                hours_per_associate=(
                    self._configuration.standard_overtime_hours
                ),
            ),
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage is within the configured "
                "voluntary overtime range. Voluntary overtime is "
                "recommended as the least disruptive staffing action."
            ),
        )

    def _build_mandatory_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build a mandatory-overtime recommendation.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                RecommendationType.MANDATORY_OVERTIME
            ),
            priority=RecommendationPriority.HIGH,
            status=RecommendationStatus.REQUIRED,
            overtime_type=OvertimeType.MANDATORY,
            overtime_hours=self._calculate_overtime_hours(
                associate_gap=request.associate_gap,
                hours_per_associate=(
                    self._configuration.standard_overtime_hours
                ),
            ),
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage exceeds the voluntary overtime "
                "range but remains within the mandatory overtime policy "
                "limit. Mandatory overtime is required."
            ),
        )

    def _build_temporary_labor_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build a temporary-labor recommendation.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=RecommendationType.TEMPORARY_LABOR,
            priority=RecommendationPriority.HIGH,
            status=RecommendationStatus.REQUIRED,
            overtime_type=OvertimeType.MANDATORY,
            overtime_hours=self._calculate_overtime_hours(
                associate_gap=request.associate_gap,
                hours_per_associate=(
                    self._configuration.maximum_overtime_hours
                ),
            ),
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage exceeds the configured "
                "mandatory overtime range. Temporary labor should be "
                "secured while maximum supported overtime is evaluated."
            ),
        )

    def _build_critical_recommendation(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Build a critical workforce-review recommendation.
        """

        return OvertimeRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                RecommendationType.FULL_TIME_HIRING_REVIEW
            ),
            priority=RecommendationPriority.CRITICAL,
            status=RecommendationStatus.REVIEW_REQUIRED,
            overtime_type=OvertimeType.MANDATORY,
            overtime_hours=self._calculate_overtime_hours(
                associate_gap=request.associate_gap,
                hours_per_associate=(
                    self._configuration.maximum_overtime_hours
                ),
            ),
            associate_gap=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage is operationally critical. "
                "Maximum supported overtime and temporary labor may be "
                "required immediately, and the recurring staffing model "
                "should be reviewed for potential full-time hiring."
            ),
        )

    # --------------------------------------------------------
    # Internal calculations
    # --------------------------------------------------------

    def _calculate_overtime_hours(
        self,
        *,
        associate_gap: int,
        hours_per_associate: float,
    ) -> float:
        """
        Calculate total recommended overtime labor hours.
        """

        bounded_hours_per_associate = min(
            self._configuration.maximum_overtime_hours,
            max(
                self._configuration.minimum_overtime_hours,
                hours_per_associate,
            ),
        )

        return associate_gap * bounded_hours_per_associate

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    @property
    def configuration(self) -> OvertimeConfiguration:
        """
        Return the active overtime policy configuration.
        """

        return self._configuration


# ============================================================
# Public API
# ============================================================

__all__ = [
    "OvertimeRecommendationEngine",
]