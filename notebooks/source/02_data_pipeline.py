# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Notebook 02 — Enterprise Data Foundation Pipeline
# MAGIC
# MAGIC This notebook implements the complete metadata-driven data foundation:
# MAGIC
# MAGIC 1. runtime initialization,
# MAGIC 2. dataset registry,
# MAGIC 3. source acquisition,
# MAGIC 4. Bronze persistence,
# MAGIC 5. enterprise manifest,
# MAGIC 6. Silver cleansing and schema enforcement,
# MAGIC 7. Gold daily workload aggregation,
# MAGIC 8. data-quality validation,
# MAGIC 9. pipeline execution summary.
# MAGIC
# MAGIC **Design decision:** Bronze is the first persistent layer. The source CSV
# MAGIC is downloaded to temporary driver storage, read with Python, converted to
# MAGIC Spark, and written directly to S3. No Landing-zone file copy is used.

# COMMAND ----------

# MAGIC %run ./00_project_setup

# COMMAND ----------

# MAGIC %pip install -q kagglehub pandas

# COMMAND ----------

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import logging
import re
import shutil
import uuid

import kagglehub
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

PIPELINE_NAME = "enterprise-workforce-data-foundation"
PIPELINE_VERSION = "3.0.0"
PIPELINE_RUN_ID = str(uuid.uuid4())
PIPELINE_STARTED_AT_UTC = datetime.now(timezone.utc)

DOWNLOAD_ROOT = Path("/tmp/overtime-capacity-planning/downloads")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(PIPELINE_NAME)

if STORAGE_CONNECTION_OK is not True:
    raise RuntimeError("Project storage validation did not succeed.")

print("=" * 72)
print("AI WORKFORCE CAPACITY PLANNING — DATA FOUNDATION")
print("=" * 72)
print(f"Pipeline run ID : {PIPELINE_RUN_ID}")
print(f"Environment     : {ENVIRONMENT}")
print(f"Project root    : {PROJECT_ROOT}")
print("=" * 72)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 01 — Enterprise Dataset Registry
# MAGIC
# MAGIC The registry is embedded in this pipeline so the project remains limited
# MAGIC to three operational notebooks. It is also persisted to S3 for auditability.

# COMMAND ----------

REGISTRY_SCHEMA = StructType(
    [
        StructField("dataset_id", IntegerType(), False),
        StructField("dataset_name", StringType(), False),
        StructField("dataset_key", StringType(), False),
        StructField("dataset_version", StringType(), False),
        StructField("dataset_owner", StringType(), False),
        StructField("source_type", StringType(), False),
        StructField("source_location", StringType(), False),
        StructField("source_reference", StringType(), False),
        StructField("source_format", StringType(), False),
        StructField("primary_file_name", StringType(), False),
        StructField("bronze_folder", StringType(), False),
        StructField("silver_folder", StringType(), False),
        StructField("gold_folder", StringType(), False),
        StructField("enabled", BooleanType(), False),
        StructField("status", StringType(), False),
    ]
)

DATASET_REGISTRY = [
    (
        1,
        "DataCo SMART Supply Chain",
        "dataco_supply_chain",
        "1.0",
        "Issouf KABRE",
        "Kaggle",
        "https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis",
        "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis",
        "csv",
        "DataCoSupplyChainDataset.csv",
        "dataco_supply_chain",
        "dataco_supply_chain",
        "daily_workload",
        True,
        "READY_FOR_PROCESSING",
    )
]

registry_df = spark.createDataFrame(DATASET_REGISTRY, schema=REGISTRY_SCHEMA)

duplicate_keys = (
    registry_df
    .groupBy("dataset_key")
    .count()
    .filter(F.col("count") > 1)
    .count()
)

if duplicate_keys:
    raise RuntimeError("Dataset registry contains duplicate dataset keys.")

ready_registry_df = registry_df.filter(
    (F.col("enabled") == F.lit(True))
    & (F.col("status") == F.lit("READY_FOR_PROCESSING"))
)

if ready_registry_df.count() == 0:
    raise RuntimeError("No enabled datasets are ready for processing.")

(
    registry_df.write
    .mode("overwrite")
    .option("compression", "snappy")
    .parquet(DATASET_REGISTRY_PATH)
)

dataset_config = ready_registry_df.first().asDict(recursive=True)

display(registry_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 02 — Source Acquisition
# MAGIC
# MAGIC Kaggle files are downloaded to temporary driver storage. The configured
# MAGIC primary CSV is selected explicitly; auxiliary files are not ingested.

# COMMAND ----------

def sha256_file(file_path: Path) -> str:
    """Calculate a streaming SHA-256 checksum for one local source file."""

    digest = hashlib.sha256()

    with file_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def download_primary_kaggle_file(dataset: dict[str, Any]) -> Path:
    """Download a Kaggle dataset and return its configured primary file."""

    dataset_key = dataset["dataset_key"]
    download_path = DOWNLOAD_ROOT / dataset_key

    if download_path.exists():
        shutil.rmtree(download_path)

    download_path.mkdir(parents=True, exist_ok=True)

    resolved_path = Path(
        kagglehub.dataset_download(
            handle=dataset["source_reference"],
            output_dir=str(download_path),
            force_download=True,
        )
    )

    candidates = [
        path
        for path in resolved_path.rglob(dataset["primary_file_name"])
        if path.is_file()
    ]

    if len(candidates) != 1:
        raise RuntimeError(
            "Expected exactly one configured primary source file; "
            f"found {len(candidates)} for {dataset['primary_file_name']!r}."
        )

    return candidates[0]


primary_source_file = download_primary_kaggle_file(dataset_config)
source_size_bytes = primary_source_file.stat().st_size
source_sha256 = sha256_file(primary_source_file)

print(f"Primary source file : {primary_source_file}")
print(f"Source size bytes   : {source_size_bytes:,}")
print(f"Source SHA-256      : {source_sha256}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 03 — Bronze Layer
# MAGIC
# MAGIC Bronze preserves source values as strings, normalizes column names,
# MAGIC adds lineage metadata, and writes a reproducible Parquet snapshot to S3.

# COMMAND ----------

def normalize_column_name(column_name: str) -> str:
    """Convert a source column name into stable snake_case."""

    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")

    if not normalized:
        raise ValueError(f"Unable to normalize column name: {column_name!r}")

    return normalized


def standardize_column_names(df: DataFrame) -> DataFrame:
    """Normalize all columns and reject normalization collisions."""

    normalized_columns = [normalize_column_name(column) for column in df.columns]
    duplicate_columns = sorted(
        {
            column
            for column in normalized_columns
            if normalized_columns.count(column) > 1
        }
    )

    if duplicate_columns:
        raise RuntimeError(
            "Column normalization produced duplicates: "
            f"{duplicate_columns}"
        )

    return df.toDF(*normalized_columns)


# Read all source columns as strings. This avoids mixed-type inference errors
# and preserves raw values until Silver applies the business schema.
source_pdf = pd.read_csv(
    primary_source_file,
    dtype=str,
    keep_default_na=False,
    low_memory=False,
    encoding="latin-1",
)

if source_pdf.empty:
    raise RuntimeError("Source acquisition produced an empty dataset.")

source_df = spark.createDataFrame(source_pdf)

bronze_df = (
    standardize_column_names(source_df)
    .withColumn("_source_file_name", F.lit(primary_source_file.name))
    .withColumn("_source_sha256", F.lit(source_sha256))
    .withColumn("_dataset_key", F.lit(dataset_config["dataset_key"]))
    .withColumn("_dataset_version", F.lit(dataset_config["dataset_version"]))
    .withColumn("_pipeline_run_id", F.lit(PIPELINE_RUN_ID))
    .withColumn("_bronze_ingested_at_utc", F.current_timestamp())
)

bronze_path = f"{BRONZE_ROOT}/{dataset_config['bronze_folder']}"

(
    bronze_df.write
    .mode("overwrite")
    .option("compression", "snappy")
    .parquet(bronze_path)
)

persisted_bronze_df = spark.read.parquet(bronze_path)
bronze_row_count = persisted_bronze_df.count()
bronze_column_count = len(persisted_bronze_df.columns)

if bronze_row_count != len(source_pdf):
    raise RuntimeError(
        "Bronze row-count validation failed: "
        f"source={len(source_pdf):,}, bronze={bronze_row_count:,}."
    )

print("=" * 72)
print("BRONZE LAYER COMPLETED SUCCESSFULLY")
print("=" * 72)
print(f"Rows        : {bronze_row_count:,}")
print(f"Columns     : {bronze_column_count}")
print(f"Bronze path : {bronze_path}")
print("=" * 72)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 04 — Enterprise Manifest
# MAGIC
# MAGIC The manifest records source integrity and the persisted Bronze outcome.

# COMMAND ----------

manifest_schema = StructType(
    [
        StructField("manifest_version", StringType(), False),
        StructField("pipeline_name", StringType(), False),
        StructField("pipeline_version", StringType(), False),
        StructField("pipeline_run_id", StringType(), False),
        StructField("created_at_utc", StringType(), False),
        StructField("dataset_key", StringType(), False),
        StructField("dataset_version", StringType(), False),
        StructField("source_reference", StringType(), False),
        StructField("source_file_name", StringType(), False),
        StructField("source_size_bytes", StringType(), False),
        StructField("source_sha256", StringType(), False),
        StructField("bronze_path", StringType(), False),
        StructField("bronze_row_count", StringType(), False),
        StructField("bronze_column_count", StringType(), False),
        StructField("status", StringType(), False),
    ]
)

manifest_row = [
    (
        "2.0",
        PIPELINE_NAME,
        PIPELINE_VERSION,
        PIPELINE_RUN_ID,
        datetime.now(timezone.utc).isoformat(),
        dataset_config["dataset_key"],
        dataset_config["dataset_version"],
        dataset_config["source_reference"],
        primary_source_file.name,
        str(source_size_bytes),
        source_sha256,
        bronze_path,
        str(bronze_row_count),
        str(bronze_column_count),
        "PASSED",
    )
]

manifest_df = spark.createDataFrame(manifest_row, schema=manifest_schema)
manifest_path = (
    f"{MANIFEST_ROOT}/{dataset_config['dataset_key']}/"
    f"pipeline_run_id={PIPELINE_RUN_ID}"
)

manifest_df.write.mode("overwrite").json(manifest_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 05 — Silver Layer
# MAGIC
# MAGIC Silver removes direct PII, enforces analytical types, rejects unusable
# MAGIC records, deduplicates order lines, and adds deterministic audit columns.

# COMMAND ----------

REQUIRED_SILVER_COLUMNS = {
    "order_id",
    "order_item_id",
    "order_customer_id",
    "order_date_dateorders",
    "shipping_date_dateorders",
    "order_item_quantity",
    "sales",
    "delivery_status",
    "late_delivery_risk",
}

missing_columns = REQUIRED_SILVER_COLUMNS.difference(
    persisted_bronze_df.columns
)

if missing_columns:
    raise RuntimeError(
        "Bronze is missing Silver-required columns: "
        f"{sorted(missing_columns)}"
    )

PII_COLUMNS = [
    "customer_email",
    "customer_fname",
    "customer_lname",
    "customer_password",
    "customer_street",
]

INTEGER_COLUMNS = [
    "days_for_shipping_real",
    "days_for_shipment_scheduled",
    "late_delivery_risk",
    "category_id",
    "customer_id",
    "department_id",
    "order_customer_id",
    "order_id",
    "order_item_cardprod_id",
    "order_item_id",
    "order_item_quantity",
    "product_card_id",
    "product_category_id",
    "product_status",
]

DOUBLE_COLUMNS = [
    "benefit_per_order",
    "sales_per_customer",
    "customer_zipcode",
    "latitude",
    "longitude",
    "order_item_discount",
    "order_item_discount_rate",
    "order_item_product_price",
    "order_item_profit_ratio",
    "sales",
    "order_item_total",
    "order_profit_per_order",
    "order_zipcode",
    "product_price",
]

silver_df = persisted_bronze_df.drop(
    *[column for column in PII_COLUMNS if column in persisted_bronze_df.columns]
)

for column_name in INTEGER_COLUMNS:
    if column_name in silver_df.columns:
        silver_df = silver_df.withColumn(
            column_name,
            F.when(
                F.trim(F.col(column_name)) == "",
                F.lit(None),
            ).otherwise(F.col(column_name)).cast("long"),
        )

for column_name in DOUBLE_COLUMNS:
    if column_name in silver_df.columns:
        silver_df = silver_df.withColumn(
            column_name,
            F.when(
                F.trim(F.col(column_name)) == "",
                F.lit(None),
            ).otherwise(F.col(column_name)).cast("double"),
        )

silver_df = (
    silver_df
    .withColumn(
        "order_timestamp",
        F.coalesce(
            F.to_timestamp("order_date_dateorders", "M/d/yyyy H:mm"),
            F.to_timestamp("order_date_dateorders", "MM/dd/yyyy HH:mm"),
        ),
    )
    .withColumn(
        "shipping_timestamp",
        F.coalesce(
            F.to_timestamp("shipping_date_dateorders", "M/d/yyyy H:mm"),
            F.to_timestamp("shipping_date_dateorders", "MM/dd/yyyy HH:mm"),
        ),
    )
    .withColumn("order_date", F.to_date("order_timestamp"))
    .withColumn("shipping_date", F.to_date("shipping_timestamp"))
    .filter(F.col("order_item_id").isNotNull())
    .filter(F.col("order_id").isNotNull())
    .filter(F.col("order_date").isNotNull())
    .filter(F.col("order_item_quantity") > 0)
    .filter(F.col("sales") >= 0)
    .dropDuplicates(["order_item_id"])
    .withColumn(
        "_record_hash",
        F.sha2(
            F.concat_ws(
                "||",
                F.col("order_item_id").cast("string"),
                F.col("order_id").cast("string"),
                F.col("order_date").cast("string"),
                F.col("order_item_quantity").cast("string"),
                F.col("sales").cast("string"),
            ),
            256,
        ),
    )
    .withColumn("_silver_processed_at_utc", F.current_timestamp())
)

silver_path = f"{SILVER_ROOT}/{dataset_config['silver_folder']}"

(
    silver_df.write
    .mode("overwrite")
    .option("compression", "snappy")
    .parquet(silver_path)
)

persisted_silver_df = spark.read.parquet(silver_path)
silver_row_count = persisted_silver_df.count()

if silver_row_count == 0:
    raise RuntimeError("Silver creation rejected an empty dataset.")

if (
    persisted_silver_df
    .groupBy("order_item_id")
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
    > 0
):
    raise RuntimeError("Silver validation found duplicate order_item_id values.")

print("=" * 72)
print("SILVER LAYER COMPLETED SUCCESSFULLY")
print("=" * 72)
print(f"Rows        : {silver_row_count:,}")
print(f"Silver path : {silver_path}")
print("=" * 72)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 06 — Gold Daily Workload Dataset
# MAGIC
# MAGIC Gold produces one row per operational day for forecasting and future
# MAGIC workforce-capacity calculations.

# COMMAND ----------

gold_df = (
    persisted_silver_df
    .groupBy("order_date")
    .agg(
        F.countDistinct("order_id").alias("order_count"),
        F.count("order_item_id").alias("order_line_count"),
        F.sum("order_item_quantity").cast("long").alias("workload_units"),
        F.round(F.sum("sales"), 2).alias("gross_sales"),
        F.countDistinct("order_customer_id").alias("customer_count"),
        F.sum(
            F.when(F.col("late_delivery_risk") == 1, 1).otherwise(0)
        ).cast("long").alias("late_delivery_count"),
        F.round(F.avg("days_for_shipping_real"), 4).alias(
            "avg_real_shipping_days"
        ),
        F.round(F.avg("days_for_shipment_scheduled"), 4).alias(
            "avg_scheduled_shipping_days"
        ),
    )
    .withColumn(
        "late_delivery_rate",
        F.round(
            F.col("late_delivery_count") / F.col("order_line_count"),
            6,
        ),
    )
    .withColumn("year", F.year("order_date"))
    .withColumn("month", F.month("order_date"))
    .withColumn("day_of_week", F.dayofweek("order_date"))
    .withColumn("week_of_year", F.weekofyear("order_date"))
    .withColumn("is_weekend", F.dayofweek("order_date").isin(1, 7))
    .withColumn("_pipeline_run_id", F.lit(PIPELINE_RUN_ID))
    .withColumn("_gold_processed_at_utc", F.current_timestamp())
)

gold_path = f"{GOLD_ROOT}/{dataset_config['gold_folder']}"

(
    gold_df.write
    .mode("overwrite")
    .option("compression", "snappy")
    .parquet(gold_path)
)

persisted_gold_df = spark.read.parquet(gold_path)
gold_row_count = persisted_gold_df.count()

if gold_row_count == 0:
    raise RuntimeError("Gold creation rejected an empty daily dataset.")

if (
    persisted_gold_df
    .filter(F.col("workload_units") <= 0)
    .limit(1)
    .count()
    > 0
):
    raise RuntimeError("Gold validation found non-positive workload values.")

if (
    persisted_gold_df
    .groupBy("order_date")
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
    > 0
):
    raise RuntimeError("Gold validation found duplicate operational dates.")

display(persisted_gold_df.orderBy("order_date"))

print("=" * 72)
print("GOLD LAYER COMPLETED SUCCESSFULLY")
print("=" * 72)
print(f"Daily rows : {gold_row_count:,}")
print(f"Gold path  : {gold_path}")
print("=" * 72)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 07 — Data Quality and Pipeline Summary

# COMMAND ----------

PIPELINE_FINISHED_AT_UTC = datetime.now(timezone.utc)
PIPELINE_DURATION_SECONDS = (
    PIPELINE_FINISHED_AT_UTC - PIPELINE_STARTED_AT_UTC
).total_seconds()

quality_metrics = [
    (
        PIPELINE_RUN_ID,
        dataset_config["dataset_key"],
        "source_size_bytes",
        float(source_size_bytes),
        "PASSED",
    ),
    (
        PIPELINE_RUN_ID,
        dataset_config["dataset_key"],
        "bronze_row_count",
        float(bronze_row_count),
        "PASSED",
    ),
    (
        PIPELINE_RUN_ID,
        dataset_config["dataset_key"],
        "silver_row_count",
        float(silver_row_count),
        "PASSED",
    ),
    (
        PIPELINE_RUN_ID,
        dataset_config["dataset_key"],
        "gold_daily_row_count",
        float(gold_row_count),
        "PASSED",
    ),
]

quality_metrics_df = spark.createDataFrame(
    quality_metrics,
    [
        "pipeline_run_id",
        "dataset_key",
        "metric_name",
        "metric_value",
        "status",
    ],
)

validation_path = (
    f"{VALIDATION_ROOT}/{dataset_config['dataset_key']}/"
    f"pipeline_run_id={PIPELINE_RUN_ID}"
)

quality_metrics_df.write.mode("overwrite").parquet(validation_path)

summary_row = [
    (
        PIPELINE_RUN_ID,
        PIPELINE_NAME,
        PIPELINE_VERSION,
        PROJECT_VERSION,
        ENVIRONMENT,
        dataset_config["dataset_key"],
        "PASSED",
        PIPELINE_STARTED_AT_UTC.isoformat(),
        PIPELINE_FINISHED_AT_UTC.isoformat(),
        float(PIPELINE_DURATION_SECONDS),
        bronze_path,
        silver_path,
        gold_path,
        manifest_path,
        validation_path,
    )
]

summary_columns = [
    "pipeline_run_id",
    "pipeline_name",
    "pipeline_version",
    "project_version",
    "environment",
    "dataset_key",
    "status",
    "started_at_utc",
    "finished_at_utc",
    "duration_seconds",
    "bronze_path",
    "silver_path",
    "gold_path",
    "manifest_path",
    "validation_path",
]

pipeline_summary_df = spark.createDataFrame(summary_row, summary_columns)

pipeline_log_path = (
    f"{PIPELINE_LOG_ROOT}/{dataset_config['dataset_key']}/"
    f"pipeline_run_id={PIPELINE_RUN_ID}"
)

pipeline_summary_df.write.mode("overwrite").json(pipeline_log_path)

display(quality_metrics_df)
display(pipeline_summary_df)

print()
print("=" * 72)
print("DATA FOUNDATION PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 72)
print(f"Pipeline run ID : {PIPELINE_RUN_ID}")
print(f"Dataset         : {dataset_config['dataset_key']}")
print(f"Bronze rows     : {bronze_row_count:,}")
print(f"Silver rows     : {silver_row_count:,}")
print(f"Gold daily rows : {gold_row_count:,}")
print(f"Duration        : {PIPELINE_DURATION_SECONDS:,.2f} seconds")
print("Status          : PASSED")
print("=" * 72)

# COMMAND ----------

