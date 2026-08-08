"""
Enterprise Workforce Optimization Engine

Resolves multiple workforce recommendations into one enterprise
optimization decision.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .configuration import WorkforceOptimizationConfiguration
from .exceptions import (
    OptimizationConflictError,
    OptimizationEngineError,
    OptimizationValidationError,
)
from .models import (
    OptimizationPriority,
    OptimizationStatus,
    WorkforceAction,
    WorkforceOptimizationDecision,
    WorkforceOptimizationRequest,
)


class WorkforceOptimizationEngine:
    """
    Enterprise optimization decision engine.
    """

    def __init__(
        self,
        configuration: WorkforceOptimizationConfiguration,
    ) ->None:

        if not isinstance(
            configuration,
            WorkforceOptimizationConfiguration,
        ):
            raise OptimizationEngineError(
                "configuration must be a WorkforceOptimizationConfiguration."
            )

        self._configuration = configuration

    @property
    def configuration(
        self,
    ) -> WorkforceOptimizationConfiguration:
        return self._configuration

    def optimize(
        self,
        *,
        request: WorkforceOptimizationRequest,
    ) -> WorkforceOptimizationDecision:
        """
        Produce one unified optimization decision.
        """

        if not isinstance(
            request,
            WorkforceOptimizationRequest,
        ):
            raise OptimizationValidationError(
                "request must be a WorkforceOptimizationRequest."
            )

        if (
            request.forecast_confidence
            < self.configuration.low_confidence_threshold
        ):
            return self._review_decision(
                request,
                "Forecast confidence is below policy threshold.",
            )

        if request.associate_gap <= 0:
            return WorkforceOptimizationDecision(
                planning_date=request.planning_date,
                action=WorkforceAction.NONE,
                priority=OptimizationPriority.LOW,
                status=OptimizationStatus.OPTIMAL,
                associate_gap=request.associate_gap,
                recommended_associates=0,
                overtime_hours=0.0,
                forecast_confidence=request.forecast_confidence,
                conflicting_actions_resolved=False,
                rationale="No workforce action required.",
                generated_at_utc=datetime.now(timezone.utc),
            )

        actions = []

        if request.overtime_recommended:
            actions.append(
                (
                    self.configuration.overtime_priority_weight,
                    WorkforceAction.OVERTIME,
                )
            )

        if request.cross_training_recommended:
            actions.append(
                (
                    self.configuration.cross_training_priority_weight,
                    WorkforceAction.CROSS_TRAINING,
                )
            )

        if request.shift_realignment_recommended:
            actions.append(
                (
                    self.configuration.shift_realignment_priority_weight,
                    WorkforceAction.SHIFT_REALIGNMENT,
                )
            )

        if request.temporary_labor_recommended:
            actions.append(
                (
                    self.configuration.temporary_labor_priority_weight,
                    WorkforceAction.TEMPORARY_LABOR,
                )
            )

        if request.full_time_hiring_recommended:
            actions.append(
                (
                    self.configuration.full_time_hiring_priority_weight,
                    WorkforceAction.FULL_TIME_HIRING,
                )
            )

        if not actions:
            return self._review_decision(
                request,
                "Positive associate gap without recommendation.",
            )

        actions.sort()

        selected_action = actions[-1][1]

        critical = (
            request.associate_gap
            >= self.configuration.critical_associate_gap
        )

        priority = (
            OptimizationPriority.CRITICAL
            if critical
            else OptimizationPriority.HIGH
        )

        status = (
            OptimizationStatus.CRITICAL
            if critical
            else OptimizationStatus.ACCEPTABLE
        )

        return WorkforceOptimizationDecision(
            planning_date=request.planning_date,
            action=selected_action,
            priority=priority,
            status=status,
            associate_gap=request.associate_gap,
            recommended_associates=request.recommended_associates,
            overtime_hours=request.overtime_hours,
            forecast_confidence=request.forecast_confidence,
            conflicting_actions_resolved=len(actions) > 1,
            rationale=(
                f"{selected_action.value} selected using "
                "enterprise optimization policy."
            ),
            generated_at_utc=datetime.now(timezone.utc),
        )

    def _review_decision(
        self,
        request: WorkforceOptimizationRequest,
        rationale: str,
    ) -> WorkforceOptimizationDecision:

        return WorkforceOptimizationDecision(
            planning_date=request.planning_date,
            action=WorkforceAction.NONE,
            priority=OptimizationPriority.MEDIUM,
            status=OptimizationStatus.REVIEW,
            associate_gap=request.associate_gap,
            recommended_associates=0,
            overtime_hours=0.0,
            forecast_confidence=request.forecast_confidence,
            conflicting_actions_resolved=False,
            rationale=rationale,
            generated_at_utc=datetime.now(timezone.utc),
        )


__all__ = [
    "WorkforceOptimizationEngine",
]