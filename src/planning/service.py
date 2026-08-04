"""
Enterprise Capacity Planning — Service

Public application service for workforce capacity planning.

The service coordinates request validation, capacity evaluation, and
report generation while keeping calculations, domain models, and
reporting responsibilities separated.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from src.planning.configuration import CapacityPlanningConfiguration
from src.planning.engine import CapacityPlanningEngine
from src.planning.reporting import (
    CapacityPlanningReport,
    CapacityPlanningReporter,
)
from src.workforce.exceptions import (
    WorkforcePlanningError,
    WorkforceValidationError,
)
from src.workforce.models import WorkforceCapacity


# ============================================================
# Capacity Planning Service
# ============================================================

class CapacityPlanningService:
    """
    Public application service for enterprise capacity planning.

    Parameters
    ----------
    configuration:
        Optional validated planning configuration.

    engine:
        Optional capacity-planning engine dependency.

    reporter:
        Optional reporting dependency.

    Notes
    -----
    When explicit dependencies are not supplied, the service creates
    default production implementations.
    """

    def __init__(
        self,
        *,
        configuration: Optional[
            CapacityPlanningConfiguration
        ] = None,
        engine: Optional[CapacityPlanningEngine] = None,
        reporter: Optional[CapacityPlanningReporter] = None,
    ) -> None:
        """
        Initialize the capacity-planning service.
        """

        if configuration is not None and engine is not None:
            if engine.configuration is not configuration:
                raise WorkforceValidationError(
                    "When both configuration and engine are supplied, "
                    "the engine must use the same configuration object."
                )

        self._configuration = (
            configuration
            if configuration is not None
            else (
                engine.configuration
                if engine is not None
                else CapacityPlanningConfiguration()
            )
        )

        self._engine = (
            engine
            if engine is not None
            else CapacityPlanningEngine(
                configuration=self._configuration,
            )
        )

        self._reporter = (
            reporter
            if reporter is not None
            else CapacityPlanningReporter()
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def plan(
        self,
        *,
        planning_date: date,
        expected_order_lines: float,
        workforce_capacity: WorkforceCapacity,
        forecast_confidence: Optional[float] = None,
    ) -> CapacityPlanningReport:
        """
        Produce one enterprise capacity-planning report.

        Parameters
        ----------
        planning_date:
            Business date being evaluated.

        expected_order_lines:
            Forecast order-line workload for the planning period.

        workforce_capacity:
            Available workforce and productivity information.

        forecast_confidence:
            Optional upstream forecast confidence between zero and one.

        Returns
        -------
        CapacityPlanningReport
            Standardized planning report suitable for dashboards,
            APIs, persistence, and downstream decision services.

        Raises
        ------
        WorkforceValidationError
            If the request is invalid.

        WorkforcePlanningError
            If planning execution or report generation fails.
        """

        try:
            requirement, gap = self._engine.evaluate(
                planning_date=planning_date,
                expected_order_lines=expected_order_lines,
                workforce_capacity=workforce_capacity,
                forecast_confidence=forecast_confidence,
            )

            return self._reporter.build(
                workforce_capacity=workforce_capacity,
                workforce_requirement=requirement,
                workforce_gap=gap,
            )

        except (
            WorkforceValidationError,
            WorkforcePlanningError,
        ):
            raise

        except Exception as exc:
            raise WorkforcePlanningError(
                "Capacity-planning service execution failed."
            ) from exc

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    @property
    def configuration(
        self,
    ) -> CapacityPlanningConfiguration:
        """
        Return the active planning configuration.
        """

        return self._configuration

    @property
    def engine(self) -> CapacityPlanningEngine:
        """
        Return the active planning engine.
        """

        return self._engine

    @property
    def reporter(self) -> CapacityPlanningReporter:
        """
        Return the active planning reporter.
        """

        return self._reporter


# ============================================================
# Public API
# ============================================================

__all__ = [
    "CapacityPlanningService",
]