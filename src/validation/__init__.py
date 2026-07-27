"""Reusable Spark data-quality framework."""

from .exceptions import DataQualityValidationError
from .models import ValidationReport, ValidationResult, ValidationSeverity, ValidationStatus
from .reporting import persist_validation_report, print_validation_report, validation_report_to_dataframe
from .rules import (
    AllowedValuesRule,
    MinimumRowCountRule,
    NotNullRule,
    NumericRangeRule,
    RequiredColumnsRule,
    RowCountMatchRule,
    UniqueKeyRule,
)
from .validator import DataValidator

__all__ = [
    "AllowedValuesRule",
    "DataQualityValidationError",
    "DataValidator",
    "MinimumRowCountRule",
    "NotNullRule",
    "NumericRangeRule",
    "RequiredColumnsRule",
    "RowCountMatchRule",
    "UniqueKeyRule",
    "ValidationReport",
    "ValidationResult",
    "ValidationSeverity",
    "ValidationStatus",
    "persist_validation_report",
    "print_validation_report",
    "validation_report_to_dataframe",
]
