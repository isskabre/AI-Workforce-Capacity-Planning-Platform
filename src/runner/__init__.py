"""
Implementation 26.9 — Enterprise Platform Runner

Enterprise runner package.

Provides the production entry point responsible for
starting, executing, and shutting down the AI Workforce
Capacity Planning Platform.

Author:
    AI Workforce Capacity Planning Platform

Version:
    1.0.0
"""

from src.runner.constants import *
from src.runner.exceptions import *
from src.runner.models import *
from src.runner.configuration import RunnerConfiguration
from src.runner.startup import EnterpriseRunnerStartup
from src.runner.shutdown import EnterpriseRunnerShutdown
from src.runner.service import EnterprisePlatformRunnerService
from src.runner.main import (
    EnterprisePlatformRunner,
    main,
)

RUNNER_PACKAGE_VERSION = "1.0.0"

__all__ = [
    # Package
    "RUNNER_PACKAGE_VERSION",

    # Configuration
    "RunnerConfiguration",

    # Startup / Shutdown
    "EnterpriseRunnerStartup",
    "EnterpriseRunnerShutdown",

    # Service
    "EnterprisePlatformRunnerService",

    # Entry Point
    "EnterprisePlatformRunner",
    "main",
]