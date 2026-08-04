"""
Enterprise Decision Orchestration Engine

Coordinates capacity planning, overtime recommendation, strategic
staffing, and workforce optimization into one unified enterprise
decision.

The orchestration engine delegates business rules to the existing
domain services. It does not duplicate planning, overtime, staffing,
or optimization logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from src.optimization.configuration import (
    WorkforceOptimizationConfiguration,
)
from src.optimization.engine import WorkforceOptimizationEngine
from src.optimization.models import WorkforceOptimizationRequest
from src.optimization.service import WorkforceOptimizationService
from src.overtime.models import (
    OvertimeRequest,
    RecommendationType as OvertimeRecommendationType,
)
from src.overtime.service import OvertimeRecommendationService
from src.planning.service import CapacityPlanningService
from src.staffing.models import (
    StaffingRecommendationType,
    StaffingRequest,
)
from src.staffing.service import StaffingRecommendationService
from src.workforce.models import (
    OvertimeType as WorkforceOvertimeType,
    ShiftType,
    WorkforceCapacity,
    WorkforceType,
)

from .configuration import EnterpriseOrchestrationConfiguration
from .exceptions import (
    OrchestrationDependencyError,
    OrchestrationEngineError,
    OrchestrationStageError,
    OrchestrationValidationError,
)
from .models import (
    EnterpriseDecisionRequest,
    EnterpriseDecisionResult,
    OrchestrationStage,
    OrchestrationStatus,
)


class EnterpriseDecisionOrchestrationEngine:
    """
    Coordinate the complete enterprise workforce decision workflow.

    Parameters
    ----------
    configuration:
        Optional orchestration configuration.

    planning_service:
        Optional capacity-planning service dependency.

    overtime_service:
        Optional overtime-recommendation service dependency.

    staffing_service:
        Optional strategic-staffing service dependency.

    optimization_service:
        Optional workforce-optimization service dependency.

    Notes
    -----
    Default production dependencies are constructed when explicit
    dependencies are not provided.
    """

    def __init__(
        self,
        *,
        configuration: Optional[
            EnterpriseOrchestrationConfiguration
        ] = None,
        planning_service: Optional[
            CapacityPlanningService
        ] = None,
        overtime_service: Optional[
            OvertimeRecommendationService
        ] = None,
        staffing_service: Optional[
            StaffingRecommendationService
        ] = None,
        optimization_service: Optional[
            WorkforceOptimizationService
        ] = None,
    ) -> None:
        """
        Initialize the orchestration engine.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else EnterpriseOrchestrationConfiguration()
        )

        if not isinstance(
            self._configuration,
            EnterpriseOrchestrationConfiguration,
        ):
            raise OrchestrationDependencyError(
                "configuration must be an "
                "EnterpriseOrchestrationConfiguration."
            )

        self._planning_service = (
            planning_service
            if planning_service is not None
            else CapacityPlanningService()
        )

        self._overtime_service = (
            overtime_service
            if overtime_service is not None
            else OvertimeRecommendationService()
        )

        self._staffing_service = (
            staffing_service
            if staffing_service is not None
            else StaffingRecommendationService()
        )

        if optimization_service is None:
            optimization_configuration = (
                WorkforceOptimizationConfiguration()
            )

            optimization_engine = WorkforceOptimizationEngine(
                configuration=optimization_configuration,
            )

            optimization_service = WorkforceOptimizationService(
                configuration=optimization_configuration,
                engine=optimization_engine,
            )

        self._optimization_service = optimization_service

        self._validate_dependencies()

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def execute(
        self,
        *,
        request: EnterpriseDecisionRequest,
    ) -> EnterpriseDecisionResult:
        """
        Execute the complete enterprise workforce decision workflow.

        Parameters
        ----------
        request:
            Validated end-to-end workforce decision request.

        Returns
        -------
        EnterpriseDecisionResult
            Unified, serializable enterprise workforce decision.

        Raises
        ------
        OrchestrationValidationError
            If the request is invalid.

        OrchestrationStageError
            If a workflow stage fails.

        OrchestrationEngineError
            If orchestration fails unexpectedly.
        """

        if not isinstance(request, EnterpriseDecisionRequest):
            raise OrchestrationValidationError(
                "request must be an EnterpriseDecisionRequest."
            )

        try:
            capacity_report = self._execute_planning_stage(
                request=request,
            )

            associate_gap = capacity_report.associate_gap

            overtime_recommendation = (
                self._execute_overtime_stage(
                    request=request,
                    associate_gap=associate_gap,
                )
            )

            staffing_recommendation = (
                self._execute_staffing_stage(
                    request=request,
                    associate_gap=associate_gap,
                )
            )

            optimization_decision = (
                self._execute_optimization_stage(
                    request=request,
                    associate_gap=associate_gap,
                    overtime_recommendation=(
                        overtime_recommendation
                    ),
                    staffing_recommendation=(
                        staffing_recommendation
                    ),
                )
            )

            return EnterpriseDecisionResult(
                planning_date=request.planning_date,
                workflow_status=OrchestrationStatus.COMPLETED,
                completed_stage=OrchestrationStage.COMPLETE,
                expected_order_lines=request.expected_order_lines,
                available_associates=(
                    capacity_report.available_associates
                ),
                required_associates=(
                    capacity_report.required_associates
                ),
                associate_gap=associate_gap,
                overtime_recommendation=(
                    overtime_recommendation.recommendation.value
                    if overtime_recommendation is not None
                    else "NOT_EXECUTED"
                ),
                staffing_recommendation=(
                    staffing_recommendation.recommendation.value
                    if staffing_recommendation is not None
                    else "NOT_EXECUTED"
                ),
                optimization_action=(
                    optimization_decision.action.value
                    if optimization_decision is not None
                    else "NOT_EXECUTED"
                ),
                optimization_priority=(
                    optimization_decision.priority.value
                    if optimization_decision is not None
                    else "NOT_EXECUTED"
                ),
                optimization_status=(
                    optimization_decision.status.value
                    if optimization_decision is not None
                    else "NOT_EXECUTED"
                ),
                overtime_hours=(
                    optimization_decision.overtime_hours
                    if optimization_decision is not None
                    else (
                        overtime_recommendation.overtime_hours
                        if overtime_recommendation is not None
                        else 0.0
                    )
                ),
                recommended_associates=(
                    optimization_decision.recommended_associates
                    if optimization_decision is not None
                    else (
                        staffing_recommendation
                        .recommended_associates
                        if staffing_recommendation is not None
                        else 0
                    )
                ),
                forecast_confidence=request.forecast_confidence,
                rationale=(
                    optimization_decision.rationale
                    if optimization_decision is not None
                    else self._build_fallback_rationale(
                        overtime_recommendation=(
                            overtime_recommendation
                        ),
                        staffing_recommendation=(
                            staffing_recommendation
                        ),
                    )
                ),
                generated_at_utc=datetime.now(timezone.utc),
            )

        except (
            OrchestrationValidationError,
            OrchestrationStageError,
            OrchestrationEngineError,
        ):
            raise

        except Exception as exc:
            raise OrchestrationEngineError(
                "Enterprise decision orchestration failed."
            ) from exc

    # --------------------------------------------------------
    # Planning stage
    # --------------------------------------------------------

    def _execute_planning_stage(
        self,
        *,
        request: EnterpriseDecisionRequest,
    ):
        """
        Execute workforce capacity planning.
        """

        try:
            workforce_capacity = WorkforceCapacity(
                planning_date=request.planning_date,
                shift=ShiftType.SHIFT_1,
                workforce_type=WorkforceType.FULL_TIME,
                available_associates=(
                    request.available_associates
                ),
                productivity_lines_per_hour=(
                    request.productivity_lines_per_hour
                ),
                scheduled_hours=request.scheduled_hours,
                overtime_type=WorkforceOvertimeType.NONE,
            )

            return self._planning_service.plan(
                planning_date=request.planning_date,
                expected_order_lines=(
                    request.expected_order_lines
                ),
                workforce_capacity=workforce_capacity,
                forecast_confidence=(
                    request.forecast_confidence
                ),
            )

        except Exception as exc:
            raise OrchestrationStageError(
                "Capacity planning stage failed."
            ) from exc

    # --------------------------------------------------------
    # Overtime stage
    # --------------------------------------------------------

    def _execute_overtime_stage(
        self,
        *,
        request: EnterpriseDecisionRequest,
        associate_gap: int,
    ):
        """
        Execute overtime recommendation.
        """

        if not self._configuration.enable_overtime_stage:
            return None

        try:
            return self._overtime_service.recommend(
                request=OvertimeRequest(
                    planning_date=request.planning_date,
                    associate_gap=max(0, associate_gap),
                    forecast_confidence=(
                        request.forecast_confidence
                    ),
                )
            )

        except Exception as exc:
            raise OrchestrationStageError(
                "Overtime recommendation stage failed."
            ) from exc

    # --------------------------------------------------------
    # Staffing stage
    # --------------------------------------------------------

    def _execute_staffing_stage(
        self,
        *,
        request: EnterpriseDecisionRequest,
        associate_gap: int,
    ):
        """
        Execute strategic staffing recommendation.
        """

        if not self._configuration.enable_staffing_stage:
            return None

        try:
            return self._staffing_service.recommend(
                request=StaffingRequest(
                    planning_date=request.planning_date,
                    associate_gap=associate_gap,
                    forecast_confidence=(
                        request.forecast_confidence
                    ),
                    recurring_shortage_days=(
                        request.recurring_shortage_days
                    ),
                    recurring_surplus_days=(
                        request.recurring_surplus_days
                    ),
                    overtime_dependency_days=(
                        request.overtime_dependency_days
                    ),
                    planning_horizon_days=(
                        request.planning_horizon_days
                    ),
                )
            )

        except Exception as exc:
            raise OrchestrationStageError(
                "Strategic staffing stage failed."
            ) from exc

    # --------------------------------------------------------
    # Optimization stage
    # --------------------------------------------------------

    def _execute_optimization_stage(
        self,
        *,
        request: EnterpriseDecisionRequest,
        associate_gap: int,
        overtime_recommendation,
        staffing_recommendation,
    ):
        """
        Execute unified workforce optimization.
        """

        if not self._configuration.enable_optimization_stage:
            return None

        try:
            overtime_recommended = (
                overtime_recommendation is not None
                and overtime_recommendation.recommendation
                in {
                    OvertimeRecommendationType
                    .VOLUNTARY_OVERTIME,
                    OvertimeRecommendationType
                    .MANDATORY_OVERTIME,
                }
            )

            overtime_temporary_labor = (
                overtime_recommendation is not None
                and overtime_recommendation.recommendation
                is OvertimeRecommendationType.TEMPORARY_LABOR
            )

            staffing_temporary_labor = (
                staffing_recommendation is not None
                and staffing_recommendation.recommendation
                is StaffingRecommendationType.TEMPORARY_LABOR
            )

            full_time_hiring_recommended = (
                staffing_recommendation is not None
                and staffing_recommendation.recommendation
                in {
                    StaffingRecommendationType
                    .FULL_TIME_HIRING,
                    StaffingRecommendationType
                    .FULL_TIME_HIRING_REVIEW,
                }
            )

            shift_realignment_recommended = (
                staffing_recommendation is not None
                and staffing_recommendation.recommendation
                is StaffingRecommendationType.SHIFT_REALIGNMENT
            )

            cross_training_recommended = (
                staffing_recommendation is not None
                and staffing_recommendation.recommendation
                is StaffingRecommendationType.CROSS_TRAIN
            )

            return self._optimization_service.optimize(
                request=WorkforceOptimizationRequest(
                    planning_date=request.planning_date,
                    associate_gap=associate_gap,
                    forecast_confidence=(
                        request.forecast_confidence
                    ),
                    overtime_recommended=(
                        overtime_recommended
                    ),
                    temporary_labor_recommended=(
                        overtime_temporary_labor
                        or staffing_temporary_labor
                    ),
                    full_time_hiring_recommended=(
                        full_time_hiring_recommended
                    ),
                    shift_realignment_recommended=(
                        shift_realignment_recommended
                    ),
                    cross_training_recommended=(
                        cross_training_recommended
                    ),
                    overtime_hours=(
                        overtime_recommendation.overtime_hours
                        if overtime_recommended
                        and overtime_recommendation is not None
                        else 0.0
                    ),
                    recommended_associates=(
                        staffing_recommendation
                        .recommended_associates
                        if staffing_recommendation is not None
                        else max(0, associate_gap)
                    ),
                )
            )

        except Exception as exc:
            raise OrchestrationStageError(
                "Workforce optimization stage failed."
            ) from exc

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _build_fallback_rationale(
        *,
        overtime_recommendation,
        staffing_recommendation,
    ) -> str:
        """
        Build a rationale when optimization is disabled.
        """

        rationale_parts = []

        if overtime_recommendation is not None:
            rationale_parts.append(
                overtime_recommendation.rationale
            )

        if staffing_recommendation is not None:
            rationale_parts.append(
                staffing_recommendation.rationale
            )

        if not rationale_parts:
            return (
                "Orchestration completed without optional "
                "recommendation stages."
            )

        return " ".join(rationale_parts)

    def _validate_dependencies(self) -> None:
        """
        Validate required orchestration dependencies.
        """

        dependencies = {
            "planning_service": (
                self._planning_service,
                CapacityPlanningService,
            ),
            "overtime_service": (
                self._overtime_service,
                OvertimeRecommendationService,
            ),
            "staffing_service": (
                self._staffing_service,
                StaffingRecommendationService,
            ),
            "optimization_service": (
                self._optimization_service,
                WorkforceOptimizationService,
            ),
        }

        for dependency_name, (
            dependency,
            expected_type,
        ) in dependencies.items():
            if not isinstance(dependency, expected_type):
                raise OrchestrationDependencyError(
                    f"{dependency_name} must be a "
                    f"{expected_type.__name__}."
                )

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    @property
    def configuration(
        self,
    ) -> EnterpriseOrchestrationConfiguration:
        """
        Return the active orchestration configuration.
        """

        return self._configuration

    @property
    def planning_service(self) -> CapacityPlanningService:
        """
        Return the capacity-planning service.
        """

        return self._planning_service

    @property
    def overtime_service(
        self,
    ) -> OvertimeRecommendationService:
        """
        Return the overtime-recommendation service.
        """

        return self._overtime_service

    @property
    def staffing_service(
        self,
    ) -> StaffingRecommendationService:
        """
        Return the strategic-staffing service.
        """

        return self._staffing_service

    @property
    def optimization_service(
        self,
    ) -> WorkforceOptimizationService:
        """
        Return the workforce-optimization service.
        """

        return self._optimization_service


__all__ = [
    "EnterpriseDecisionOrchestrationEngine",
]