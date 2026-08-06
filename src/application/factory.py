"""
Implementation 25.6 — Enterprise Application Factory

Factory responsible for assembling the enterprise application service
graph and registering fully wired singleton services in the dependency
injection container.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from __future__ import annotations

from src.api.mapper import EnterpriseAPIMapper
from src.api.router import EnterpriseAPIRouter
from src.api.service import EnterpriseAPIService
from src.monitoring.health import MonitoringHealthService
from src.monitoring.metrics import MonitoringMetricsService
from src.monitoring.service import EnterpriseMonitoringService
from src.optimization.configuration import (
    WorkforceOptimizationConfiguration,
)
from src.optimization.engine import (
    WorkforceOptimizationEngine,
)
from src.optimization.service import (
    WorkforceOptimizationService,
)
from src.orchestration.service import (
    EnterpriseDecisionOrchestrationService,
)
from src.planning.service import CapacityPlanningService
from src.reporting.service import (
    EnterpriseDecisionReportingService,
)

from .configuration import ApplicationConfiguration
from .constants import (
    SERVICE_API,
    SERVICE_MONITORING,
    SERVICE_OPTIMIZATION,
    SERVICE_ORCHESTRATION,
    SERVICE_PLANNING,
    SERVICE_REPORTING,
)
from .container import EnterpriseApplicationContainer
from .exceptions import (
    ApplicationFactoryError,
    ApplicationValidationError,
)


class EnterpriseApplicationFactory:
    """
    Build and wire the enterprise application dependency graph.

    All services are registered as lazy singletons. Dependencies that
    must share configuration or service instances are constructed
    through the same application container.
    """

    def __init__(
        self,
        *,
        configuration: ApplicationConfiguration,
    ) -> None:
        """
        Initialize the enterprise application factory.
        """

        if not isinstance(
            configuration,
            ApplicationConfiguration,
        ):
            raise ApplicationValidationError(
                "configuration must be an "
                "ApplicationConfiguration."
            )

        self._configuration = configuration

    # ========================================================
    # Public API
    # ========================================================

    def build(
        self,
    ) -> EnterpriseApplicationContainer:
        """
        Build and return the configured application container.
        """

        try:
            container = EnterpriseApplicationContainer(
                configuration=self._configuration,
            )

            self._register_services(
                container=container,
            )

            return container

        except (
            ApplicationValidationError,
            ApplicationFactoryError,
        ):
            raise

        except Exception as exc:
            raise ApplicationFactoryError(
                "Enterprise application factory build failed."
            ) from exc

    # ========================================================
    # Service registration
    # ========================================================

    def _register_services(
        self,
        *,
        container: EnterpriseApplicationContainer,
    ) -> None:
        """
        Register all services required by application configuration.
        """

        if not isinstance(
            container,
            EnterpriseApplicationContainer,
        ):
            raise ApplicationValidationError(
                "container must be an "
                "EnterpriseApplicationContainer."
            )

        service_factories = {
            SERVICE_PLANNING: (
                lambda: self._build_planning_service()
            ),
            SERVICE_OPTIMIZATION: (
                lambda: self._build_optimization_service()
            ),
            SERVICE_ORCHESTRATION: (
                lambda: self._build_orchestration_service(
                    container=container,
                )
            ),
            SERVICE_REPORTING: (
                lambda: self._build_reporting_service()
            ),
            SERVICE_MONITORING: (
                lambda: self._build_monitoring_service()
            ),
            SERVICE_API: (
                lambda: self._build_api_service(
                    container=container,
                )
            ),
        }

        for service_name in (
            self._configuration.required_services
        ):
            service_factory = service_factories.get(
                service_name
            )

            if service_factory is None:
                raise ApplicationFactoryError(
                    "No application factory exists for required "
                    f"service '{service_name}'."
                )

            container.register_factory(
                name=service_name,
                factory=service_factory,
                singleton=True,
                description=(
                    "Enterprise application service: "
                    f"{service_name}."
                ),
            )

    # ========================================================
    # Service builders
    # ========================================================

    @staticmethod
    def _build_planning_service(
    ) -> CapacityPlanningService:
        """
        Build the capacity-planning service.
        """

        return CapacityPlanningService()

    @staticmethod
    def _build_optimization_service(
    ) -> WorkforceOptimizationService:
        """
        Build the optimization configuration, engine, and service.

        The engine and service must reference the exact same
        WorkforceOptimizationConfiguration instance.
        """

        optimization_configuration = (
            WorkforceOptimizationConfiguration()
        )

        optimization_engine = WorkforceOptimizationEngine(
            configuration=optimization_configuration,
        )

        return WorkforceOptimizationService(
            configuration=optimization_configuration,
            engine=optimization_engine,
        )

    @staticmethod
    def _build_reporting_service(
    ) -> EnterpriseDecisionReportingService:
        """
        Build the enterprise reporting service.
        """

        return EnterpriseDecisionReportingService()

    def _build_monitoring_service(
        self,
    ) -> EnterpriseMonitoringService:
        """
        Build monitoring components with shared configuration.
        """

        monitoring_configuration = (
            self._configuration.monitoring
        )

        metrics_service = MonitoringMetricsService(
            configuration=monitoring_configuration,
        )

        health_service = MonitoringHealthService(
            configuration=monitoring_configuration,
        )

        monitoring_service = EnterpriseMonitoringService(
            configuration=monitoring_configuration,
            metrics_service=metrics_service,
            health_service=health_service,
        )

        for component in (
            monitoring_configuration.enabled_components
        ):
            monitoring_service.register_health_check(
                component=component,
                health_check=lambda: True,
            )

        return monitoring_service

    @staticmethod
    def _build_orchestration_service(
        *,
        container: EnterpriseApplicationContainer,
    ) -> EnterpriseDecisionOrchestrationService:
        """
        Build the enterprise decision orchestration service.

        Planning and optimization remain independently registered in
        the application container. The current orchestration service
        constructs and owns its established internal collaborators.
        """

        if not isinstance(
            container,
            EnterpriseApplicationContainer,
        ):
            raise ApplicationValidationError(
                "container must be an "
                "EnterpriseApplicationContainer."
            )

        return EnterpriseDecisionOrchestrationService()

    def _build_api_service(
        self,
        *,
        container: EnterpriseApplicationContainer,
    ) -> EnterpriseAPIService:
        """
        Build the API service with shared application dependencies.
        """

        if not isinstance(
            container,
            EnterpriseApplicationContainer,
        ):
            raise ApplicationValidationError(
                "container must be an "
                "EnterpriseApplicationContainer."
            )

        orchestration_service = container.resolve(
            name=SERVICE_ORCHESTRATION,
        )

        reporting_service = container.resolve(
            name=SERVICE_REPORTING,
        )

        monitoring_service = container.resolve(
            name=SERVICE_MONITORING,
        )

        api_configuration = self._configuration.api

        api_router = EnterpriseAPIRouter(
            configuration=api_configuration,
        )

        api_mapper = EnterpriseAPIMapper()

        return EnterpriseAPIService(
            configuration=api_configuration,
            router=api_router,
            mapper=api_mapper,
            orchestration_service=orchestration_service,
            reporting_service=reporting_service,
            monitoring_service=monitoring_service,
        )

    # ========================================================
    # Public state
    # ========================================================

    @property
    def configuration(
        self,
    ) -> ApplicationConfiguration:
        """
        Return the root application configuration.
        """

        return self._configuration


__all__ = [
    "EnterpriseApplicationFactory",
]