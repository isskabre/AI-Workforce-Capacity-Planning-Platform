"""
Implementation 26.3 — Enterprise Platform Runner Models
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RunnerStatus(str, Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class RunnerDescriptor:
    """
    Immutable runner metadata.
    """

    name: str
    version: str
    runtime_mode: str
    status: RunnerStatus
    started_at_utc: datetime | None = None


@dataclass(frozen=True, slots=True)
class RunnerExecutionResult:
    """
    Immutable execution result.
    """

    succeeded: bool
    descriptor: RunnerDescriptor
    completed_at_utc: datetime
    exit_code: int
    message: str = ""


__all__ = [
    "RunnerStatus",
    "RunnerDescriptor",
    "RunnerExecutionResult",
]