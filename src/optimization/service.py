"""
Enterprise Workforce Optimization Service

Application service exposing the optimization engine.
"""

from __future__ import annotations

from .configuration import WorkforceOptimizationConfiguration
from .engine import WorkforceOptimizationEngine
from .exceptions import (
    OptimizationServiceError,
    OptimizationValidationError,
)
from .models import (
    WorkforceOptimizationDecision,
    WorkforceOptimizationRequest,
)


class WorkforceOptimizationService:
    """
    Enterprise application service for workforce optimization.
    """

    def __init__(
        self,
        *,
        configuration: WorkforceOptimizationConfiguration,
        engine: WorkforceOptimizationEngine,
    ) -> None:

        if not isinstance(
            configuration,
            WorkforceOptimizationConfiguration,
        ):
            raise OptimizationServiceError(
                "configuration must be a WorkforceOptimizationConfiguration."
            )

        if not isinstance(
            engine,
            WorkforceOptimizationEngine,
        ):
            raise OptimizationServiceError(
                "engine must be a WorkforceOptimizationEngine."
            )

        if engine.configuration is not configuration:
            raise OptimizationValidationError(
                "configuration and engine must reference the same "
                "configuration instance."
            )

        self._configuration = configuration
        self._engine = engine

    @property
    def configuration(
        self,
    ) -> WorkforceOptimizationConfiguration:
        """Return the active configuration."""

        return self._configuration

    @property
    def engine(
        self,
    ) -> WorkforceOptimizationEngine:
        """Return the optimization engine."""

        return self._engine

    def optimize(
        self,
        *,
        request: WorkforceOptimizationRequest,
    ) -> WorkforceOptimizationDecision:
        """
        Execute enterprise workforce optimization.
        """

        if not isinstance(
            request,
            WorkforceOptimizationRequest,
        ):
            raise OptimizationValidationError(
                "request must be a WorkforceOptimizationRequest."
            )

        return self.engine.optimize(
            request=request,
        )


__all__ = [
    "WorkforceOptimizationService",
]