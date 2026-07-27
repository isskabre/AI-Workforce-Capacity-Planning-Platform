# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Notebook 06 — Enterprise Data Quality & Validation Framework
# MAGIC
# MAGIC **Implementation:** 06 — Enterprise Data Quality & Validation Framework  
# MAGIC **Notebook version:** 1.0.1
# MAGIC
# MAGIC This notebook validates the reusable `src/validation` package against:
# MAGIC
# MAGIC 1. controlled demonstration data,
# MAGIC 2. the persisted Bronze dataset,
# MAGIC 3. the persisted Silver dataset,
# MAGIC 4. the persisted Gold dataset,
# MAGIC 5. the validation-evidence persistence layer.
# MAGIC
# MAGIC The notebook is an orchestration and acceptance-test layer. Reusable
# MAGIC validation logic remains in `src/validation`.

# COMMAND ----------

# MAGIC %run ./00_project_setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 01 — Imports and Repository Resolution

# COMMAND ----------

from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import functions as F

# COMMAND ----------

current_path = Path.cwd()
repository_root = current_path

while (
    repository_root.parent != repository_root
    and not (repository_root / "src").exists()
):
    repository_root = repository_root.parent

if not (repository_root / "src").exists():
    raise RuntimeError(
        "Unable to locate the repository root containing src/."
    )

if str(repository_root) not in sys.path:
    sys.path.insert(0, str(repository_root))

print(f"Repository root: {repository_root}")

# COMMAND ----------

from src.validation import (
    DataQualityValidationError,
    DataValidator,
    MinimumRowCountRule,
    NotNullRule,
    NumericRangeRule,
    RequiredColumnsRule,
    RowCountMatchRule,
    UniqueKeyRule,
    persist_validation_report,
    print_validation_report,
    validation_report_to_dataframe,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 02 — Validation Contracts

# COMMAND ----------

VALID_DATASET_STATUSES = [
    "ACTIVE",
    "READY_FOR_PROCESSING",
]

BRONZE_METADATA_COLUMNS = [
    "_source_file_name",
    "_source_sha256",
    "_dataset_key",
    "_dataset_version",
    "_pipeline_run_id",
    "_bronze_ingested_at_utc",
]

BRONZE_REQUIRED_NOT_NULL_COLUMNS = [
    "_source_file_name",
    "_source_sha256",
    "_dataset_key",
    "_dataset_version",
    "_pipeline_run_id",
    "_bronze_ingested_at_utc",
]

SILVER_REQUIRED_COLUMNS = [
    "order_item_id",
    "order_date",
    "workload_units",
]

GOLD_REQUIRED_COLUMNS = [
    "order_date",
    "workload_units",
]

print("Validation contracts initialized.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 03 — Controlled Successful Validation

# COMMAND ----------

valid_demo_df = spark.createDataFrame(
    [
        (1, "2026-07-27", 125.0),
        (2, "2026-07-28", 140.0),
        (3, "2026-07-29", 132.0),
    ],
    ["record_id", "business_date", "workload_units"],
)

validator = DataValidator(fail_fast=False)

valid_demo_report = validator.validate(
    dataframe=valid_demo_df,
    dataset_name="valid_demo",
    dataset_layer="TEST",
    rules=[
        RequiredColumnsRule(
            ["record_id", "business_date", "workload_units"]
        ),
        MinimumRowCountRule(1),
        NotNullRule(
            ["record_id", "business_date", "workload_units"]
        ),
        UniqueKeyRule(["record_id"]),
        NumericRangeRule(
            column="workload_units",
            minimum=0.0,
        ),
    ],
)

print_validation_report(valid_demo_report)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 04 — Controlled Failed Validation
# MAGIC
# MAGIC This controlled test confirms that invalid data produces structured
# MAGIC `FAILED` evidence. The test uses `raise_on_failure=False`, so the
# MAGIC notebook can continue after proving the failure path.

# COMMAND ----------

invalid_demo_df = spark.createDataFrame(
    [
        (1, "2026-07-27", 125.0),
        (1, None, -10.0),
    ],
    ["record_id", "business_date", "workload_units"],
)

invalid_demo_report = validator.validate(
    dataframe=invalid_demo_df,
    dataset_name="invalid_demo",
    dataset_layer="TEST",
    rules=[
        RequiredColumnsRule(
            ["record_id", "business_date", "workload_units"]
        ),
        NotNullRule(["business_date"]),
        UniqueKeyRule(["record_id"]),
        NumericRangeRule(
            column="workload_units",
            minimum=0.0,
        ),
    ],
    raise_on_failure=False,
)

print_validation_report(invalid_demo_report)

if invalid_demo_report.status.value != "FAILED":
    raise RuntimeError(
        "Controlled failure validation did not return FAILED."
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 05 — Resolve the Registered Dataset
# MAGIC
# MAGIC A dataset is eligible when:
# MAGIC
# MAGIC - `enabled` is `true`, and
# MAGIC - its normalized lifecycle status is accepted by this implementation.

# COMMAND ----------

registry_df = spark.read.parquet(DATASET_REGISTRY_PATH)

rows = (
    registry_df
    .filter(
        (F.col("enabled") == F.lit(True))
        & (
            F.upper(F.trim(F.col("status")))
            .isin(VALID_DATASET_STATUSES)
        )
    )
    .orderBy("dataset_id")
    .limit(1)
    .collect()
)

if not rows:
    raise RuntimeError(
        "No enabled dataset was found with a supported lifecycle status. "
        f"Accepted statuses: {VALID_DATASET_STATUSES}"
    )

active_dataset = rows[0].asDict()
dataset_key = active_dataset["dataset_key"]

bronze_path = f"{BRONZE_ROOT}/{dataset_key}"
silver_path = f"{SILVER_ROOT}/{dataset_key}"
gold_path = f"{GOLD_ROOT}/daily_workload"

print("=" * 80)
print("REGISTERED DATASET RESOLUTION")
print("=" * 80)
print(f"Dataset ID    : {active_dataset['dataset_id']}")
print(f"Dataset Name  : {active_dataset['dataset_name']}")
print(f"Dataset Key   : {dataset_key}")
print(f"Status        : {active_dataset['status']}")
print(f"Bronze Path   : {bronze_path}")
print(f"Silver Path   : {silver_path}")
print(f"Gold Path     : {gold_path}")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 06 — Bronze Validation
# MAGIC
# MAGIC The Bronze contract is aligned with the metadata written by the
# MAGIC validated enterprise data-foundation pipeline.

# COMMAND ----------

bronze_df = spark.read.parquet(bronze_path)

bronze_report = validator.validate(
    dataframe=bronze_df,
    dataset_name=dataset_key,
    dataset_layer="BRONZE",
    rules=[
        MinimumRowCountRule(1),
        RequiredColumnsRule(BRONZE_METADATA_COLUMNS),
        NotNullRule(BRONZE_REQUIRED_NOT_NULL_COLUMNS),
    ],
)

print_validation_report(bronze_report)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 07 — Silver Validation

# COMMAND ----------

silver_df = spark.read.parquet(silver_path)

bronze_row_count = bronze_df.count()

silver_report = validator.validate(
    dataframe=silver_df,
    dataset_name=dataset_key,
    dataset_layer="SILVER",
    rules=[
        RowCountMatchRule(bronze_row_count),

        MinimumRowCountRule(1),

        RequiredColumnsRule(
            BRONZE_METADATA_COLUMNS
        ),

        NotNullRule(
            BRONZE_REQUIRED_NOT_NULL_COLUMNS
        ),
    ],
)

print_validation_report(silver_report)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 08 — Gold Validation

# COMMAND ----------

gold_df = spark.read.parquet(gold_path)

gold_report = validator.validate(
    dataframe=gold_df,
    dataset_name=f"{dataset_key}_daily_workload",
    dataset_layer="GOLD",
    rules=[
        MinimumRowCountRule(1),
        RequiredColumnsRule(GOLD_REQUIRED_COLUMNS),
        NotNullRule(GOLD_REQUIRED_COLUMNS),
        UniqueKeyRule(["order_date"]),
        NumericRangeRule(
            column="workload_units",
            minimum=0.0,
        ),
    ],
)

print_validation_report(gold_report)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 09 — Persist Validation Evidence

# COMMAND ----------

validation_output_path = (
    f"{VALIDATION_ROOT}/enterprise_data_quality"
)

reports = [
    valid_demo_report,
    invalid_demo_report,
    bronze_report,
    silver_report,
    gold_report,
]

report_df = validation_report_to_dataframe(
    spark=spark,
    report=reports[0],
)

for report in reports[1:]:
    report_df = report_df.unionByName(
        validation_report_to_dataframe(
            spark=spark,
            report=report,
        ),
        allowMissingColumns=True,
    )

persist_validation_report(
    report_df=report_df,
    output_path=validation_output_path,
    mode="append",
)

persisted_validation_df = spark.read.parquet(
    validation_output_path
)

display(
    persisted_validation_df
    .orderBy(
        F.col("report_created_at_utc").desc(),
        F.col("dataset_layer"),
        F.col("rule_name"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Section 10 — Final Acceptance Summary

# COMMAND ----------

production_reports = [
    bronze_report,
    silver_report,
    gold_report,
]

failed_production_reports = [
    report
    for report in production_reports
    if report.status.value == "FAILED"
]

if failed_production_reports:
    failed_layers = [
        report.dataset_layer
        for report in failed_production_reports
    ]

    raise DataQualityValidationError(
        "One or more production-layer validation reports failed. "
        f"Failed layers: {failed_layers}"
    )

print("=" * 80)
print("ENTERPRISE DATA QUALITY FRAMEWORK COMPLETED SUCCESSFULLY")
print("=" * 80)
print(f"Dataset key       : {dataset_key}")
print(f"Bronze rows       : {bronze_df.count():,}")
print(f"Silver rows       : {silver_df.count():,}")
print(f"Gold rows         : {gold_df.count():,}")
print(f"Bronze status     : {bronze_report.status.value}")
print(f"Silver status     : {silver_report.status.value}")
print(f"Gold status       : {gold_report.status.value}")
print(f"Evidence path     : {validation_output_path}")
print("Framework status  : PASSED")
print("=" * 80)

# COMMAND ----------

