"""
Enterprise Forecast Dataset Package

Public interfaces for building, splitting, validating, and persisting
versioned forecast datasets.

Notebook and application code should import package interfaces from this
module rather than importing internal implementation modules directly.
"""

from forecast.constants import (
    DATE_COLUMN,
    DEFAULT_FORECAST_HORIZON,
    DEFAULT_TEST_RATIO,
    DEFAULT_TRAIN_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WARMUP_DAYS,
    FORECAST_DATASET_NAME,
    FORECAST_DATASET_VERSION,
    TEMPORAL_SPLIT_STRATEGY,
)
from forecast.models import (
    DatasetSplit,
    ForecastDatasetBundle,
    ForecastDatasetMetadata,
    ForecastDatasetSummary,
    ForecastPersistenceResult,
)
from forecast.persistence import ForecastDatasetPersistence
from forecast.service import ForecastDatasetService
from forecast.splitter import ForecastDatasetSplitter


__all__ = [
    # Public services
    "ForecastDatasetService",
    "ForecastDatasetSplitter",
    "ForecastDatasetPersistence",

    # Public data contracts
    "DatasetSplit",
    "ForecastDatasetBundle",
    "ForecastDatasetMetadata",
    "ForecastDatasetSummary",
    "ForecastPersistenceResult",

    # Public configuration constants
    "FORECAST_DATASET_NAME",
    "FORECAST_DATASET_VERSION",
    "DATE_COLUMN",
    "DEFAULT_FORECAST_HORIZON",
    "DEFAULT_WARMUP_DAYS",
    "DEFAULT_TRAIN_RATIO",
    "DEFAULT_VALIDATION_RATIO",
    "DEFAULT_TEST_RATIO",
    "TEMPORAL_SPLIT_STRATEGY",
]