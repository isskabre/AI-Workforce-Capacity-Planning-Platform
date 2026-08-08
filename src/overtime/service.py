"""
Enterprise Overtime Recommendation Service

High-level application service that exposes overtime recommendation
generation to the remainder of the Enterprise Workforce Planning
Platform.
"""

from __future__ import annotations

from typing import Optional

from .configuration import OvertimeConfiguration
from .engine import OvertimeRecommendationEngine
from .exceptions import (
    OvertimeServiceError,
    OvertimeValidationError,
)
from .models import (
    OvertimeRecommendation,
    OvertimeRequest,
)


class OvertimeRecommendationService:
    """
    Enterprise application service for overtime recommendations.

    The service owns the recommendation engine and provides a stable
    interface for higher-level planning modules.
    """

    def __init__(
        self,
        *,
        configuration: Optional[OvertimeConfiguration] = None,
        engine: Optional[OvertimeRecommendationEngine] = None,
    ) -> None:
        """
        Initialize the recommendation service.
        """

        self._configuration = (
            configuration
            if configuration is not None
            else OvertimeConfiguration()
        )

        self._engine = (
            engine
            if engine is not None
            else OvertimeRecommendationEngine(
                configuration=self._configuration
            )
        )

        if (
            self._engine.configuration
            is not self._configuration
        ):
            raise OvertimeValidationError(
                "Engine and configuration must reference the same "
                "configuration instance."
            )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def recommend(
        self,
        *,
        request: OvertimeRequest,
    ) -> OvertimeRecommendation:
        """
        Generate one overtime recommendation.

        Parameters
        ----------
        request
            Validated overtime request.

        Returns
        -------
        OvertimeRecommendation
            Enterprise recommendation.
        """

        if not isinstance(request, OvertimeRequest):
            raise OvertimeValidationError(
                "request must be an OvertimeRequest."
            )

        try:
            return self._engine.recommend(
                request=request,
            )

        except (
            OvertimeValidationError,
            OvertimeServiceError,
        ):
            raise

        except Exception as exc:
            raise OvertimeServiceError(
                "Failed to generate overtime recommendation."
            ) from exc

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def configuration(self) -> OvertimeConfiguration:
        """
        Active overtime configuration.
        """
        return self._configuration

    @property
    def engine(self) -> OvertimeRecommendationEngine:
        """
        Recommendation engine.
        """
        return self._engine


__all__ = [
    "OvertimeRecommendationService",
]