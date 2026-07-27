"""Validation orchestration."""

from __future__ import annotations

from collections.abc import Sequence

from pyspark.sql import DataFrame

from .exceptions import DataQualityValidationError
from .models import ValidationReport, ValidationSeverity, ValidationStatus
from .rules import ValidationRule


class DataValidator:
    """Execute validation rules and return structured evidence."""

    def __init__(self, *, fail_fast: bool = False) -> None:
        self.fail_fast = fail_fast

    def validate(
        self,
        *,
        dataframe: DataFrame,
        dataset_name: str,
        dataset_layer: str,
        rules: Sequence[ValidationRule],
        raise_on_failure: bool = True,
    ) -> ValidationReport:
        results = []

        for rule in rules:
            result = rule.evaluate(
                dataframe=dataframe,
                dataset_name=dataset_name,
                dataset_layer=dataset_layer,
            )
            results.append(result)

            failed_error = (
                result.status is ValidationStatus.FAILED
                and result.severity is ValidationSeverity.ERROR
            )
            if self.fail_fast and failed_error:
                report = ValidationReport(
                    dataset_name=dataset_name,
                    dataset_layer=dataset_layer,
                    results=tuple(results),
                )
                raise DataQualityValidationError(self._message(report))

        report = ValidationReport(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            results=tuple(results),
        )
        if raise_on_failure and report.status is ValidationStatus.FAILED:
            raise DataQualityValidationError(self._message(report))
        return report

    @staticmethod
    def _message(report: ValidationReport) -> str:
        failed = [
            r.rule_name
            for r in report.results
            if r.status is ValidationStatus.FAILED
        ]
        return (
            f"Validation failed for {report.dataset_layer}."
            f"{report.dataset_name}. Failed rules: {failed}"
        )
