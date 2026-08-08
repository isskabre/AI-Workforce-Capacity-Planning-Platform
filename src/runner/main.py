"""
Implementation 26.8 — Enterprise Platform Runner Main

Production entry point for the enterprise platform runner.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from src.runner.configuration import RunnerConfiguration
from src.runner.service import EnterprisePlatformRunnerService
from src.runner.models import RunnerExecutionResult


class EnterprisePlatformRunner:
    """
    Enterprise platform runner entry point.
    """

    def __init__(
        self,
        *,
        configuration: RunnerConfiguration | None = None,
    ) -> None:

        if configuration is None:
            configuration = RunnerConfiguration()

        self._configuration = configuration

        self._service = EnterprisePlatformRunnerService(
            configuration=configuration,
        )

    @property
    def configuration(
        self,
    ) -> RunnerConfiguration:
        """
        Return runner configuration.
        """

        return self._configuration

    @property
    def service(
        self,
    ) -> EnterprisePlatformRunnerService:
        """
        Return runner service.
        """

        return self._service

    def run(
        self,
    ) -> RunnerExecutionResult:
        """
        Execute the platform.
        """

        return self.service.run()


def main() -> int:
    """
    Production application entry point.
    """

    runner = EnterprisePlatformRunner()

    result = runner.run()

    return result.exit_code


__all__ = [
    "EnterprisePlatformRunner",
    "main",
]