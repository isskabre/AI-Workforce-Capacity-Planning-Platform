"""Validation exceptions."""


class DataQualityValidationError(RuntimeError):
    """Raised when one or more ERROR-severity rules fail."""
