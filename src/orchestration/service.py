"""
Enterprise Decision Orchestration Service

Public service layer for the enterprise decision orchestration workflow.
"""

from __future__ import annotations

from typing import Optional

from .configuration import EnterpriseOrchestrationConfiguration
from .engine import EnterpriseDecisionOrchestrationEngine
from .exceptions import (
    OrchestrationServiceError,
    OrchestrationValidationError,
)
from .models import (
    EnterpriseDecisionRequest,
    EnterpriseDecisionResult,
)


class EnterpriseDecisionOrchestrationService:
    """
    Public service for enterprise decision orchestration.
    """

    def __init__(
        self,
        *,
        configuration: Optional[
            EnterpriseOrchestrationConfiguration
        ] = None,
        engine: Optional[
            EnterpriseDecisionOrchestrationEngine
        ] = None,
    ) -> None:
        """
        Initialize the orchestration service.
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
            raise OrchestrationServiceError(
                "configuration must be an "
                "EnterpriseOrchestrationConfiguration."
            )

        self._engine = (
            engine
            if engine is not None
            else EnterpriseDecisionOrchestrationEngine(
                configuration=self._configuration,
            )
        )

        if not isinstance(
            self._engine,
            EnterpriseDecisionOrchestrationEngine,
        ):
            raise OrchestrationServiceError(
                "engine must be an "
                "EnterpriseDecisionOrchestrationEngine."
            )

        if (
            self._engine.configuration
            is not self._configuration
        ):
            raise OrchestrationValidationError(
                "Configuration and engine must share the "
                "same EnterpriseOrchestrationConfiguration."
            )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def execute(
        self,
        *,
        request: EnterpriseDecisionRequest,
    ) -> EnterpriseDecisionResult:
        """
        Execute the enterprise decision workflow.
        """

        return self._engine.execute(
            request=request,
        )

    # ---------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------

    @property
    def configuration(
        self,
    ) -> EnterpriseOrchestrationConfiguration:
        """
        Active configuration.
        """

        return self._configuration

    @property
    def engine(
        self,
    ) -> EnterpriseDecisionOrchestrationEngine:
        """
        Underlying orchestration engine.
        """

        return self._engine


__all__ = [
    "EnterpriseDecisionOrchestrationService",
]