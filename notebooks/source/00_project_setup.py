# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Notebook 00 — Project Setup
# MAGIC
# MAGIC Shared project identity, S3 paths, runtime constants, and lightweight
# MAGIC storage validation.
# MAGIC
# MAGIC **Architecture:** Kaggle acquisition → Bronze → Silver → Gold.
# MAGIC
# MAGIC The former Landing layer is intentionally removed. Source files remain
# MAGIC temporary during execution; Bronze is the first persistent data layer.

# COMMAND ----------

from __future__ import annotations

from datetime import datetime, timezone

PROJECT_NAME = "AI Workforce Capacity Planning Platform"
PROJECT_KEY = "overtime-capacity-planning"
PROJECT_VERSION = "2.0.0"
ENVIRONMENT = "development"

S3_BUCKET = "issouf-data-lake"
PROJECT_ROOT = f"s3a://{S3_BUCKET}/{PROJECT_KEY}"

BRONZE_ROOT = f"{PROJECT_ROOT}/bronze"
SILVER_ROOT = f"{PROJECT_ROOT}/silver"
GOLD_ROOT = f"{PROJECT_ROOT}/gold"

METADATA_ROOT = f"{PROJECT_ROOT}/metadata"
REGISTRY_ROOT = f"{PROJECT_ROOT}/registry"
MANIFEST_ROOT = f"{METADATA_ROOT}/manifests"
VALIDATION_ROOT = f"{METADATA_ROOT}/validation"
PIPELINE_LOG_ROOT = f"{METADATA_ROOT}/pipeline_logs"

MODEL_ROOT = f"{PROJECT_ROOT}/models"

DATASET_REGISTRY_PATH = f"{REGISTRY_ROOT}/dataset_registry"
PROJECT_INITIALIZED_AT_UTC = datetime.now(timezone.utc)

PROJECT_PATHS = {
    "project_root": PROJECT_ROOT,
    "bronze": BRONZE_ROOT,
    "silver": SILVER_ROOT,
    "gold": GOLD_ROOT,
    "registry": REGISTRY_ROOT,
    "manifests": MANIFEST_ROOT,
    "validation": VALIDATION_ROOT,
    "pipeline_logs": PIPELINE_LOG_ROOT,
    "models": MODEL_ROOT,
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lightweight storage validation
# MAGIC
# MAGIC The check confirms that Databricks can access the S3 project root.
# MAGIC It does not write temporary test data.

# COMMAND ----------

try:
    dbutils.fs.ls(PROJECT_ROOT)
    STORAGE_CONNECTION_OK = True
except Exception as exc:
    STORAGE_CONNECTION_OK = False
    raise RuntimeError(
        f"Unable to access project storage: {PROJECT_ROOT}"
    ) from exc

print("=" * 72)
print(PROJECT_NAME.upper())
print("=" * 72)
print(f"Project version : {PROJECT_VERSION}")
print(f"Environment     : {ENVIRONMENT}")
print(f"Project root    : {PROJECT_ROOT}")
print(f"Storage status  : {'PASSED' if STORAGE_CONNECTION_OK else 'FAILED'}")
print("=" * 72)

# COMMAND ----------

