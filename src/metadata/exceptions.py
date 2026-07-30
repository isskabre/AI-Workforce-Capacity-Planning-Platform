"""
Custom exceptions for the enterprise metadata and profiling framework.
"""


class MetadataError(Exception):
    """Base exception for all metadata framework errors."""


class MetadataConfigurationError(MetadataError):
    """Raised when metadata configuration is missing or invalid."""


class DatasetProfilingError(MetadataError):
    """Raised when a dataset cannot be profiled."""


class DatasetFingerprintError(MetadataError):
    """Raised when a dataset fingerprint cannot be generated."""


class MetadataPersistenceError(MetadataError):
    """Raised when metadata cannot be persisted or loaded."""


class UnsupportedDatasetError(MetadataError):
    """Raised when the supplied dataset type is unsupported."""