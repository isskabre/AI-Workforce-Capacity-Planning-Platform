# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC
# MAGIC ## Project Setup
# MAGIC
# MAGIC This notebook centralizes the shared S3 paths and configuration used by
# MAGIC all Databricks notebooks in the project.
# MAGIC
# MAGIC ### Storage architecture
# MAGIC
# MAGIC - Landing: original source files
# MAGIC - Bronze: standardized Parquet datasets
# MAGIC - Silver: cleaned and validated Parquet datasets
# MAGIC - Gold: model-ready and business-ready Parquet datasets
# MAGIC - Databricks: processing and orchestration
# MAGIC - Amazon S3: persistent storage
# MAGIC
# MAGIC This notebook is imported by other notebooks and is not scheduled as an
# MAGIC independent workflow task.

# COMMAND ----------

# Databricks notebook source

# COMMAND ----------

# ============================================================
# Overtime Capacity Planning Platform
# Enterprise Project Configuration
#
# This notebook centralizes all shared configuration used by
# the platform. It is imported by all Databricks notebooks
# through:
#
# %run ../00_project_setup/00_project_setup
#
# Responsibilities
# ----------------
# - Project identity
# - Data Lake architecture
# - Metadata locations
# - Domain-specific storage paths
# - Shared project locations
# ============================================================

# ------------------------------------------------------------
# Project Identity
# ------------------------------------------------------------

PROJECT_NAME = "overtime-capacity-planning"
PROJECT_VERSION = "1.0.0"

ENVIRONMENT = "development"

S3_BUCKET = "issouf-data-lake"

# Root of the enterprise project in S3
PROJECT_ROOT = f"s3a://{S3_BUCKET}/{PROJECT_NAME}"

# ------------------------------------------------------------
# Enterprise Data Lake
# ------------------------------------------------------------

# Landing Zone
#
# landing/
# ├── raw/
# ├── quarantine/
# └── rejected/
#
# Bronze
# Silver
# Gold

LANDING_ROOT = f"{PROJECT_ROOT}/landing"

LANDING_RAW_ROOT = f"{LANDING_ROOT}/raw"
LANDING_QUARANTINE_ROOT = f"{LANDING_ROOT}/quarantine"
LANDING_REJECTED_ROOT = f"{LANDING_ROOT}/rejected"

BRONZE_ROOT = f"{PROJECT_ROOT}/bronze"
SILVER_ROOT = f"{PROJECT_ROOT}/silver"
GOLD_ROOT = f"{PROJECT_ROOT}/gold"

# ------------------------------------------------------------
# Enterprise Metadata
# ------------------------------------------------------------

REGISTRY_ROOT = f"{PROJECT_ROOT}/registry"

DATASET_REGISTRY_PATH = (
    f"{REGISTRY_ROOT}/datasets"
)

METADATA_ROOT = f"{PROJECT_ROOT}/metadata"

MANIFEST_ROOT = (
    f"{METADATA_ROOT}/manifests"
)

ACQUISITION_METADATA_PATH = (
    f"{METADATA_ROOT}/acquisitions"
)

# ------------------------------------------------------------
# Shared Platform Locations
# ------------------------------------------------------------

MODELS_PATH = f"{PROJECT_ROOT}/models"

EXPERIMENTS_PATH = (
    f"{PROJECT_ROOT}/experiments"
)

REPORTS_PATH = f"{PROJECT_ROOT}/reports"

CHECKPOINTS_PATH = (
    f"{PROJECT_ROOT}/checkpoints"
)

# ------------------------------------------------------------
# Bronze Layer
# ------------------------------------------------------------

BRONZE_WORKLOAD_PATH = (
    f"{BRONZE_ROOT}/workload"
)

BRONZE_WORKFORCE_PATH = (
    f"{BRONZE_ROOT}/workforce"
)

BRONZE_PRODUCTIVITY_PATH = (
    f"{BRONZE_ROOT}/productivity"
)

BRONZE_CALENDAR_PATH = (
    f"{BRONZE_ROOT}/calendar"
)

# ------------------------------------------------------------
# Silver Layer
# ------------------------------------------------------------

SILVER_WORKLOAD_PATH = (
    f"{SILVER_ROOT}/workload"
)

SILVER_WORKFORCE_PATH = (
    f"{SILVER_ROOT}/workforce"
)

SILVER_PRODUCTIVITY_PATH = (
    f"{SILVER_ROOT}/productivity"
)

SILVER_CALENDAR_PATH = (
    f"{SILVER_ROOT}/calendar"
)

# ------------------------------------------------------------
# Gold Layer
# ------------------------------------------------------------

GOLD_FEATURES_PATH = (
    f"{GOLD_ROOT}/forecasting_features"
)

GOLD_PREDICTIONS_PATH = (
    f"{GOLD_ROOT}/model_predictions"
)

GOLD_CAPACITY_PATH = (
    f"{GOLD_ROOT}/capacity_planning"
)

GOLD_RECOMMENDATIONS_PATH = (
    f"{GOLD_ROOT}/recommendations"
)

# COMMAND ----------

PROJECT_PATHS = {
    "landing": LANDING_ROOT,
    "dataset_registry": DATASET_REGISTRY_PATH,
    "manifests": MANIFEST_ROOT,
    "acquisition_metadata": ACQUISITION_METADATA_PATH,
    "bronze_workload": BRONZE_WORKLOAD_PATH,
    "bronze_workforce": BRONZE_WORKFORCE_PATH,
    "bronze_productivity": BRONZE_PRODUCTIVITY_PATH,
    "bronze_calendar": BRONZE_CALENDAR_PATH,
    "silver_workload": SILVER_WORKLOAD_PATH,
    "silver_workforce": SILVER_WORKFORCE_PATH,
    "silver_productivity": SILVER_PRODUCTIVITY_PATH,
    "silver_calendar": SILVER_CALENDAR_PATH,
    "gold_features": GOLD_FEATURES_PATH,
    "gold_predictions": GOLD_PREDICTIONS_PATH,
    "gold_capacity": GOLD_CAPACITY_PATH,
    "gold_recommendations": GOLD_RECOMMENDATIONS_PATH,
    "models": MODELS_PATH,
    "experiments": EXPERIMENTS_PATH,
    "reports": REPORTS_PATH,
    "checkpoints": CHECKPOINTS_PATH,
}

# Keep imports quiet when this notebook is called through %run.
DEBUG = False

if DEBUG:
    print(f"Project root: {PROJECT_ROOT}")
    for name, path in PROJECT_PATHS.items():
        print(f"{name:25} -> {path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lightweight storage validation
# MAGIC
# MAGIC The setup notebook checks that the project root is listable.  
# MAGIC It deliberately avoids writing test data every time another notebook imports it.

# COMMAND ----------

try:
    dbutils.fs.ls(PROJECT_ROOT)
except Exception as exc:
    raise RuntimeError(
        f"Unable to access project storage at {PROJECT_ROOT}"
    ) from exc

STORAGE_CONNECTION_OK = True

# COMMAND ----------

