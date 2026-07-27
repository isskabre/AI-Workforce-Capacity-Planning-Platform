"""Structured validation results and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class ValidationSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ValidationResult:
    dataset_name: str
    dataset_layer: str
    rule_name: str
    severity: ValidationSeverity
    status: ValidationStatus
    observed_value: str
    expected_value: str
    message: str
    evaluated_at_utc: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["severity"] = self.severity.value
        row["status"] = self.status.value
        return row


@dataclass(frozen=True)
class ValidationReport:
    dataset_name: str
    dataset_layer: str
    results: tuple[ValidationResult, ...]
    run_id: str = field(default_factory=lambda: str(uuid4()))
    created_at_utc: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def passed_count(self) -> int:
        return sum(r.status is ValidationStatus.PASSED for r in self.results)

    @property
    def warning_count(self) -> int:
        return sum(r.status is ValidationStatus.WARNING for r in self.results)

    @property
    def failed_count(self) -> int:
        return sum(r.status is ValidationStatus.FAILED for r in self.results)

    @property
    def status(self) -> ValidationStatus:
        if self.failed_count:
            return ValidationStatus.FAILED
        if self.warning_count:
            return ValidationStatus.WARNING
        return ValidationStatus.PASSED

    def to_rows(self) -> list[dict[str, Any]]:
        rows = []
        for result in self.results:
            row = result.to_dict()
            row.update(
                {
                    "validation_run_id": self.run_id,
                    "report_status": self.status.value,
                    "report_created_at_utc": self.created_at_utc,
                }
            )
            rows.append(row)
        return rows
