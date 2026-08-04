"""
Enterprise Staffing Recommendation Engine

Strategic decision engine that converts workforce gaps, recurrence
patterns, overtime dependency, and forecast confidence into actionable
staffing recommendations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .configuration import StaffingConfiguration
from .exceptions import (
    StaffingEngineError,
    StaffingValidationError,
)
from .models import (
    StaffingRecommendation,
    StaffingRecommendationPriority,
    StaffingRecommendationStatus,
    StaffingRecommendationType,
    StaffingRequest,
)


# ============================================================
# Staffing Recommendation Engine
# ============================================================

class StaffingRecommendationEngine:
    """
    Generate strategic workforce staffing recommendations.

    Parameters
    ----------
    configuration:
        Validated staffing policy configuration. A default configuration
        is created when one is not supplied.
    """

    def __init__(
        self,
        *,
        configuration: Optional[StaffingConfiguration] = None,
    ) -> None:
        """
        Initialize the staffing recommendation engine.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else StaffingConfiguration()
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def recommend(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Generate one strategic staffing recommendation.

        Parameters
        ----------
        request:
            Validated strategic staffing request.

        Returns
        -------
        StaffingRecommendation
            Standardized strategic workforce recommendation.

        Raises
        ------
        StaffingValidationError
            If the request is invalid.

        StaffingEngineError
            If recommendation generation fails unexpectedly.
        """

        if not isinstance(request, StaffingRequest):
            raise StaffingValidationError(
                "request must be a StaffingRequest."
            )

        try:
            if (
                request.forecast_confidence
                < self._configuration.low_confidence_threshold
            ):
                return self._build_low_confidence_review(
                    request=request,
                )

            if request.associate_gap == 0:
                return self._build_maintain_recommendation(
                    request=request,
                )

            if request.has_surplus:
                return self._build_surplus_recommendation(
                    request=request,
                )

            if (
                request.associate_gap
                >= self._configuration.critical_shortage_gap
            ):
                return self._build_critical_hiring_recommendation(
                    request=request,
                )

            if self._requires_full_time_hiring(request=request):
                return self._build_full_time_hiring_recommendation(
                    request=request,
                )

            if self._requires_temporary_labor(request=request):
                return self._build_temporary_labor_recommendation(
                    request=request,
                )

            if self._requires_cross_training(request=request):
                return self._build_cross_training_recommendation(
                    request=request,
                )

            return self._build_shift_realignment_recommendation(
                request=request,
            )

        except (
            StaffingValidationError,
            StaffingEngineError,
        ):
            raise

        except Exception as exc:
            raise StaffingEngineError(
                "Staffing recommendation generation failed."
            ) from exc

    # --------------------------------------------------------
    # Decision rules
    # --------------------------------------------------------

    def _requires_full_time_hiring(
        self,
        *,
        request: StaffingRequest,
    ) -> bool:
        """
        Return whether sustained demand supports full-time hiring.
        """

        return (
            request.associate_gap
            >= self._configuration.full_time_hiring_trigger_gap
            or request.recurring_shortage_days
            >= self._configuration.full_time_hiring_shortage_days
            or request.overtime_dependency_days
            >= self._configuration.minimum_overtime_dependency_days
        )

    def _requires_temporary_labor(
        self,
        *,
        request: StaffingRequest,
    ) -> bool:
        """
        Return whether temporary labor is the preferred action.
        """

        return (
            request.associate_gap
            >= self._configuration.temporary_labor_trigger_gap
            or request.recurring_shortage_days
            >= self._configuration.minimum_recurring_shortage_days
        )

    def _requires_cross_training(
        self,
        *,
        request: StaffingRequest,
    ) -> bool:
        """
        Return whether cross-training is appropriate.
        """

        return (
            request.associate_gap
            >= self._configuration.minimum_associate_gap
            and request.recurring_shortage_days
            < self._configuration.minimum_recurring_shortage_days
            and request.overtime_dependency_days == 0
        )

    # --------------------------------------------------------
    # Recommendation builders
    # --------------------------------------------------------

    def _build_low_confidence_review(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a low-confidence operational review.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
            ),
            priority=StaffingRecommendationPriority.MEDIUM,
            status=StaffingRecommendationStatus.REVIEW_REQUIRED,
            associate_gap=request.associate_gap,
            recommended_associates=abs(request.associate_gap),
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "Forecast confidence is below the configured staffing "
                "decision threshold. Review demand assumptions before "
                "approving a long-term workforce action."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_maintain_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a no-action staffing recommendation.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=StaffingRecommendationType.NONE,
            priority=StaffingRecommendationPriority.LOW,
            status=StaffingRecommendationStatus.NOT_REQUIRED,
            associate_gap=0,
            recommended_associates=0,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "Available workforce matches the strategic staffing "
                "requirement. Maintain the current staffing plan."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_surplus_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a workforce-reduction recommendation.
        """

        persistent_surplus = (
            request.recurring_surplus_days
            >= self._configuration.minimum_recurring_surplus_days
        )

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                StaffingRecommendationType.WORKFORCE_REDUCTION
                if persistent_surplus
                else StaffingRecommendationType.SHIFT_REALIGNMENT
            ),
            priority=(
                StaffingRecommendationPriority.HIGH
                if persistent_surplus
                else StaffingRecommendationPriority.MEDIUM
            ),
            status=StaffingRecommendationStatus.REVIEW_REQUIRED,
            associate_gap=request.associate_gap,
            recommended_associates=abs(request.associate_gap),
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "Recurring workforce surplus supports a workforce "
                "reduction review."
                if persistent_surplus
                else
                "A short-term workforce surplus exists. Realign labor "
                "across shifts or functions before reducing staffing."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_critical_hiring_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a critical full-time hiring recommendation.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=StaffingRecommendationType.FULL_TIME_HIRING,
            priority=StaffingRecommendationPriority.CRITICAL,
            status=StaffingRecommendationStatus.REVIEW_REQUIRED,
            associate_gap=request.associate_gap,
            recommended_associates=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage exceeds the configured critical "
                "threshold. Initiate immediate full-time hiring review "
                "and use temporary labor as an interim control."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_full_time_hiring_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a full-time hiring review.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                StaffingRecommendationType.FULL_TIME_HIRING_REVIEW
            ),
            priority=StaffingRecommendationPriority.HIGH,
            status=StaffingRecommendationStatus.REVIEW_REQUIRED,
            associate_gap=request.associate_gap,
            recommended_associates=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage is sustained across the planning "
                "horizon or requires recurring overtime. Review the "
                "full-time staffing baseline."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_temporary_labor_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a temporary-labor recommendation.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=StaffingRecommendationType.TEMPORARY_LABOR,
            priority=StaffingRecommendationPriority.HIGH,
            status=StaffingRecommendationStatus.RECOMMENDED,
            associate_gap=request.associate_gap,
            recommended_associates=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The workforce shortage is material but does not yet "
                "justify permanent hiring. Add temporary labor for the "
                "current planning horizon."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_cross_training_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a cross-training recommendation.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=StaffingRecommendationType.CROSS_TRAIN,
            priority=StaffingRecommendationPriority.MEDIUM,
            status=StaffingRecommendationStatus.RECOMMENDED,
            associate_gap=request.associate_gap,
            recommended_associates=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The shortage is limited and not yet recurring. "
                "Cross-train available associates before adding labor."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _build_shift_realignment_recommendation(
        self,
        *,
        request: StaffingRequest,
    ) -> StaffingRecommendation:
        """
        Build a shift-realignment recommendation.
        """

        return StaffingRecommendation(
            planning_date=request.planning_date,
            recommendation=(
                StaffingRecommendationType.SHIFT_REALIGNMENT
            ),
            priority=StaffingRecommendationPriority.MEDIUM,
            status=StaffingRecommendationStatus.RECOMMENDED,
            associate_gap=request.associate_gap,
            recommended_associates=request.associate_gap,
            forecast_confidence=request.forecast_confidence,
            rationale=(
                "The shortage can be addressed through workforce "
                "redistribution. Review shift assignments before "
                "initiating external hiring."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    @property
    def configuration(self) -> StaffingConfiguration:
        """
        Return the active staffing configuration.
        """

        return self._configuration


# ============================================================
# Public API
# ============================================================

__all__ = [
    "StaffingRecommendationEngine",
]