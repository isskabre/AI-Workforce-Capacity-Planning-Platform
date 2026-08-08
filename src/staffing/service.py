"""
Enterprise Staffing Recommendation Service

Application-service layer for strategic staffing recommendations.

The service owns the staffing engine and exposes a stable API for
higher-level orchestration, dashboards, and future AI-assistant
components.
"""

from __future__ import annotations

from typing import Optional

from .configuration import StaffingConfiguration
from .engine import StaffingRecommendationEngine
from .exceptions import (
    StaffingServiceError,
    StaffingValidationError,
)
from .models import (
    StaffingRecommendation,
    StaffingRequest,
)


# ============================================================
# Staffing Recommendation Service
# ============================================================

class StaffingRecommendationService:
    """
    Public application service for strategic staffing recommendations.

    Parameters
    ----------
    configuration:
        Optional validated staffing configuration.

    engine:
        Optional staffing recommendation engine.

    Notes
    -----
    When both dependencies are supplied, the engine must reference the
    same configuration instance.
    """

    def __init__(
        self,
        *,
        configuration: Optional[StaffingConfiguration] = None,
        engine: Optional[StaffingRecommendationEngine] = None,
    ) -> None:
        """
        Initialize the staffing recommendation service.
        """

        if configuration is not None and engine is not None:
            if engine.configuration is not configuration:
                raise StaffingValidationError(
                    "When both configuration and engine are supplied, "
                    "the engine must use the same configuration object."
                )

        self._configuration = (
            configuration
            if configuration is not None
            else (
                engine.configuration
                if engine is not None
                else StaffingConfiguration()
            )
        )

        self._engine = (
            engine
            if engine is not None
            else StaffingRecommendationEngine(
                configuration=self._configuration,
            )
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
            Validated staffing request.

        Returns
        -------
        StaffingRecommendation
            Standardized strategic workforce recommendation.

        Raises
        ------
        StaffingValidationError
            If the request is invalid.

        StaffingServiceError
            If the service cannot complete recommendation generation.
        """

        if not isinstance(request, StaffingRequest):
            raise StaffingValidationError(
                "request must be a StaffingRequest."
            )

        try:
            return self._engine.recommend(
                request=request,
            )

        except (
            StaffingValidationError,
            StaffingServiceError,
        ):
            raise

        except Exception as exc:
            raise StaffingServiceError(
                "Failed to generate staffing recommendation."
            ) from exc

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    @property
    def configuration(self) -> StaffingConfiguration:
        """
        Return the active staffing configuration.
        """

        return self._configuration

    @property
    def engine(self) -> StaffingRecommendationEngine:
        """
        Return the active staffing recommendation engine.
        """

        return self._engine


# ============================================================
# Public API
# ============================================================

__all__ = [
    "StaffingRecommendationService",
]