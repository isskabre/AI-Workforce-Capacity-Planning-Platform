"""
Enterprise Forecast Framework.

Public interfaces for constructing, splitting, validating, and persisting
versioned forecast datasets used throughout the AI Workforce Capacity
Planning Platform.

The package also contains dedicated subpackages for modeling, algorithms,
training, evaluation, inference, and model registry operations.

Notebook and application code should import dataset-level interfaces from
this module rather than importing their implementation modules directly.
"""

from .constants import (
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
from .models import (
    DatasetSplit,
    ForecastDatasetBundle,
    ForecastDatasetMetadata,
    ForecastDatasetSummary,
    ForecastPersistenceResult,
)
from .persistence import ForecastDatasetPersistence
from .service import ForecastDatasetService
from .splitter import ForecastDatasetSplitter


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