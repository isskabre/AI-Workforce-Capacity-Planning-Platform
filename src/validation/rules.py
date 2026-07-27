"""Reusable Spark validation rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .models import ValidationResult, ValidationSeverity, ValidationStatus


class ValidationRule(Protocol):
    name: str
    severity: ValidationSeverity

    def evaluate(
        self,
        *,
        dataframe: DataFrame,
        dataset_name: str,
        dataset_layer: str,
    ) -> ValidationResult:
        ...


def _build_result(
    *,
    dataset_name: str,
    dataset_layer: str,
    rule_name: str,
    severity: ValidationSeverity,
    passed: bool,
    observed_value: Any,
    expected_value: Any,
    passed_message: str,
    failed_message: str,
) -> ValidationResult:
    if passed:
        status = ValidationStatus.PASSED
        message = passed_message
    elif severity is ValidationSeverity.WARNING:
        status = ValidationStatus.WARNING
        message = failed_message
    else:
        status = ValidationStatus.FAILED
        message = failed_message

    return ValidationResult(
        dataset_name=dataset_name,
        dataset_layer=dataset_layer,
        rule_name=rule_name,
        severity=severity,
        status=status,
        observed_value=str(observed_value),
        expected_value=str(expected_value),
        message=message,
    )


@dataclass(frozen=True)
class RequiredColumnsRule:
    required_columns: Sequence[str]
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "required_columns"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        missing = sorted(set(self.required_columns) - set(dataframe.columns))
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=self.name,
            severity=self.severity,
            passed=not missing,
            observed_value=missing or "none",
            expected_value=sorted(self.required_columns),
            passed_message="All required columns are present.",
            failed_message=f"Missing required columns: {missing}",
        )


@dataclass(frozen=True)
class MinimumRowCountRule:
    minimum_rows: int = 1
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "minimum_row_count"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        actual = dataframe.count()
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=self.name,
            severity=self.severity,
            passed=actual >= self.minimum_rows,
            observed_value=actual,
            expected_value=f">= {self.minimum_rows}",
            passed_message=f"Dataset contains {actual:,} rows.",
            failed_message=f"Dataset has {actual:,} rows; minimum is {self.minimum_rows:,}.",
        )


@dataclass(frozen=True)
class RowCountMatchRule:
    expected_rows: int
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "row_count_match"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        actual = dataframe.count()
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=self.name,
            severity=self.severity,
            passed=actual == self.expected_rows,
            observed_value=actual,
            expected_value=self.expected_rows,
            passed_message="Row count matches the expected value.",
            failed_message=f"Expected {self.expected_rows:,} rows; found {actual:,}.",
        )


@dataclass(frozen=True)
class NotNullRule:
    columns: Sequence[str]
    maximum_null_ratio: float = 0.0
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "not_null"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        missing = sorted(set(self.columns) - set(dataframe.columns))
        if missing:
            return _build_result(
                dataset_name=dataset_name,
                dataset_layer=dataset_layer,
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                observed_value=f"missing columns: {missing}",
                expected_value=f"null ratio <= {self.maximum_null_ratio}",
                passed_message="",
                failed_message=f"Cannot evaluate nulls; missing columns: {missing}",
            )

        count = dataframe.count()
        if count == 0:
            details = {"dataset": 1.0}
        else:
            row = dataframe.agg(
                *[
                    (
                        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0))
                        / F.lit(count)
                    ).alias(c)
                    for c in self.columns
                ]
            ).first()
            details = {c: float(row[c] or 0.0) for c in self.columns}

        maximum = max(details.values(), default=0.0)
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=self.name,
            severity=self.severity,
            passed=maximum <= self.maximum_null_ratio,
            observed_value=details,
            expected_value=f"each ratio <= {self.maximum_null_ratio}",
            passed_message="Null ratios are within threshold.",
            failed_message=f"Null-ratio threshold exceeded: {details}",
        )


@dataclass(frozen=True)
class UniqueKeyRule:
    key_columns: Sequence[str]
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "unique_key"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        missing = sorted(set(self.key_columns) - set(dataframe.columns))
        if missing:
            return _build_result(
                dataset_name=dataset_name,
                dataset_layer=dataset_layer,
                rule_name=self.name,
                severity=self.severity,
                passed=False,
                observed_value=f"missing columns: {missing}",
                expected_value=list(self.key_columns),
                passed_message="",
                failed_message=f"Cannot evaluate uniqueness; missing columns: {missing}",
            )

        duplicates = (
            dataframe.groupBy(*self.key_columns)
            .count()
            .filter(F.col("count") > 1)
            .count()
        )
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=self.name,
            severity=self.severity,
            passed=duplicates == 0,
            observed_value=duplicates,
            expected_value=0,
            passed_message="Business key is unique.",
            failed_message=f"Found {duplicates:,} duplicate key groups.",
        )


@dataclass(frozen=True)
class NumericRangeRule:
    column: str
    minimum: float | None = None
    maximum: float | None = None
    allow_null: bool = False
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "numeric_range"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        rule_name = f"{self.name}:{self.column}"
        if self.column not in dataframe.columns:
            return _build_result(
                dataset_name=dataset_name,
                dataset_layer=dataset_layer,
                rule_name=rule_name,
                severity=self.severity,
                passed=False,
                observed_value="column missing",
                expected_value=self.column,
                passed_message="",
                failed_message=f"Column is missing: {self.column}",
            )

        invalid = F.lit(False)
        if not self.allow_null:
            invalid = invalid | F.col(self.column).isNull()
        if self.minimum is not None:
            invalid = invalid | (F.col(self.column) < F.lit(self.minimum))
        if self.maximum is not None:
            invalid = invalid | (F.col(self.column) > F.lit(self.maximum))

        invalid_count = dataframe.filter(invalid).count()
        expected = {
            "minimum": self.minimum,
            "maximum": self.maximum,
            "allow_null": self.allow_null,
        }
        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=rule_name,
            severity=self.severity,
            passed=invalid_count == 0,
            observed_value=invalid_count,
            expected_value=expected,
            passed_message=f"Column {self.column!r} is within range.",
            failed_message=f"Column {self.column!r} has {invalid_count:,} invalid values.",
        )


@dataclass(frozen=True)
class AllowedValuesRule:
    column: str
    allowed_values: Sequence[Any]
    allow_null: bool = False
    severity: ValidationSeverity = ValidationSeverity.ERROR
    name: str = "allowed_values"

    def evaluate(self, *, dataframe, dataset_name, dataset_layer):
        rule_name = f"{self.name}:{self.column}"
        if self.column not in dataframe.columns:
            return _build_result(
                dataset_name=dataset_name,
                dataset_layer=dataset_layer,
                rule_name=rule_name,
                severity=self.severity,
                passed=False,
                observed_value="column missing",
                expected_value=self.column,
                passed_message="",
                failed_message=f"Column is missing: {self.column}",
            )

        valid = F.col(self.column).isin(list(self.allowed_values))
        if self.allow_null:
            valid = valid | F.col(self.column).isNull()
        invalid_count = dataframe.filter(~valid).count()

        return _build_result(
            dataset_name=dataset_name,
            dataset_layer=dataset_layer,
            rule_name=rule_name,
            severity=self.severity,
            passed=invalid_count == 0,
            observed_value=invalid_count,
            expected_value=list(self.allowed_values),
            passed_message=f"Column {self.column!r} contains allowed values.",
            failed_message=f"Column {self.column!r} has {invalid_count:,} invalid values.",
        )
