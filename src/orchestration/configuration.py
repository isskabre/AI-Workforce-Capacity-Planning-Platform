"""
Enterprise Decision Orchestration Configuration

Validated configuration for the end-to-end workforce decision
orchestration workflow.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .constants import (
    DEFAULT_FORECAST_CONFIDENCE,
    EXECUTION_ORDER,
    ORCHESTRATION_DOMAIN_VERSION,
)
from .exceptions import OrchestrationConfigurationError


@dataclass(slots=True)
class EnterpriseOrchestrationConfiguration:
    """
    Configuration contract for enterprise decision orchestration.

    Parameters
    ----------
    default_forecast_confidence:
        Confidence used when an upstream request does not provide one.

    enable_overtime_stage:
        Whether the overtime recommendation stage is enabled.

    enable_staffing_stage:
        Whether the strategic staffing stage is enabled.

    enable_optimization_stage:
        Whether the workforce optimization stage is enabled.

    fail_fast:
        Whether orchestration stops immediately when a stage fails.

    execution_order:
        Ordered workflow stages executed by the orchestration engine.

    configuration_version:
        Semantic version of the orchestration configuration contract.
    """

    default_forecast_confidence: float = (
        DEFAULT_FORECAST_CONFIDENCE
    )

    enable_overtime_stage: bool = True

    enable_staffing_stage: bool = True

    enable_optimization_stage: bool = True

    fail_fast: bool = True

    execution_order: tuple[str, ...] = EXECUTION_ORDER

    configuration_version: str = ORCHESTRATION_DOMAIN_VERSION

    def __post_init__(self) -> None:
        """
        Validate the complete orchestration configuration.
        """

        if not 0.0 <= self.default_forecast_confidence <= 1.0:
            raise OrchestrationConfigurationError(
                "default_forecast_confidence must be between 0 and 1."
            )

        boolean_fields = {
            "enable_overtime_stage": self.enable_overtime_stage,
            "enable_staffing_stage": self.enable_staffing_stage,
            "enable_optimization_stage": (
                self.enable_optimization_stage
            ),
            "fail_fast": self.fail_fast,
        }

        for field_name, field_value in boolean_fields.items():
            if not isinstance(field_value, bool):
                raise OrchestrationConfigurationError(
                    f"{field_name} must be a boolean."
                )

        if not isinstance(self.execution_order, tuple):
            raise OrchestrationConfigurationError(
                "execution_order must be a tuple."
            )

        if not self.execution_order:
            raise OrchestrationConfigurationError(
                "execution_order must not be empty."
            )

        if len(self.execution_order) != len(
            set(self.execution_order)
        ):
            raise OrchestrationConfigurationError(
                "execution_order must not contain duplicate stages."
            )

        if self.execution_order != EXECUTION_ORDER:
            raise OrchestrationConfigurationError(
                "execution_order must match the supported enterprise "
                "workflow order."
            )

        if not self.configuration_version.strip():
            raise OrchestrationConfigurationError(
                "configuration_version must not be empty."
            )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the configuration as a serializable dictionary.
        """

        payload = asdict(self)
        payload["execution_order"] = list(self.execution_order)

        return payload


__all__ = [
    "EnterpriseOrchestrationConfiguration",
]