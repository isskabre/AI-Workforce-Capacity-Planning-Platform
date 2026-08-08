# Databricks notebook source
# MAGIC %md
# MAGIC # AI Workforce Capacity Planning Platform
# MAGIC ## Notebook 01 — Public Dataset Evaluation and Selection
# MAGIC
# MAGIC **Implementation:** 28 — Enterprise Release Validation  
# MAGIC **Platform release:** v3.0.0  
# MAGIC **Notebook version:** 3.0.0  
# MAGIC
# MAGIC ### Purpose
# MAGIC
# MAGIC Evaluate and select the public dataset used by the AI Workforce Capacity
# MAGIC Planning Platform for workload forecasting, feature engineering, capacity
# MAGIC planning, and overtime decision support.
# MAGIC
# MAGIC ### Business objective
# MAGIC
# MAGIC Select a public dataset that can support daily operational workload
# MAGIC forecasting, feature engineering, capacity simulation, and overtime
# MAGIC recommendations for a distribution-center scenario.
# MAGIC
# MAGIC ### Core decision
# MAGIC
# MAGIC The platform forecasts **operational workload**, not overtime directly.
# MAGIC
# MAGIC Forecast workload is subsequently translated into required labor capacity,
# MAGIC available capacity, capacity gaps, and overtime recommendations.

# COMMAND ----------

# MAGIC %run ./00_project_setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## Platform Bootstrap Contract
# MAGIC
# MAGIC Validate that Notebook 01 is executing against the approved v3.0.0  
# MAGIC platform bootstrap before dataset evaluation begins.

# COMMAND ----------

# =============================================================================
# AI Workforce Capacity Planning Platform
# Implementation 28 — Enterprise Release Validation
# Notebook 01 — Platform Bootstrap Contract Validation
# =============================================================================

EXPECTED_PLATFORM_RELEASE = "v3.0.0"

required_bootstrap_symbols = (
    "PLATFORM_RELEASE",
    "PROJECT_NAME",
    "PROJECT_KEY",
    "PROJECT_VERSION",
    "PROJECT_ROOT",
    "CONFIGURATION_STATUS",
    "STORAGE_STATUS",
    "RUNTIME_STATUS",
)

missing_bootstrap_symbols = [
    symbol
    for symbol in required_bootstrap_symbols
    if symbol not in globals()
]

if missing_bootstrap_symbols:
    raise RuntimeError(
        "Notebook 01 is missing required platform bootstrap symbols: "
        f"{missing_bootstrap_symbols}"
    )

if PLATFORM_RELEASE != EXPECTED_PLATFORM_RELEASE:
    raise RuntimeError(
        "Notebook 01 platform release mismatch: "
        f"expected {EXPECTED_PLATFORM_RELEASE!r}, "
        f"received {PLATFORM_RELEASE!r}."
    )

if CONFIGURATION_STATUS != "PASSED":
    raise RuntimeError(
        "Notebook 01 requires CONFIGURATION_STATUS='PASSED'."
    )

if STORAGE_STATUS != "PASSED":
    raise RuntimeError(
        "Notebook 01 requires STORAGE_STATUS='PASSED'."
    )

if RUNTIME_STATUS != "READY":
    raise RuntimeError(
        "Notebook 01 requires RUNTIME_STATUS='READY'."
    )

print("=" * 72)
print("NOTEBOOK 01 — PLATFORM BOOTSTRAP CONTRACT")
print("=" * 72)
print(f"Platform release     : {PLATFORM_RELEASE}")
print(f"Project              : {PROJECT_NAME}")
print(f"Project version      : {PROJECT_VERSION}")
print(f"Configuration status : {CONFIGURATION_STATUS}")
print(f"Storage status       : {STORAGE_STATUS}")
print(f"Runtime status       : {RUNTIME_STATUS}")
print("Bootstrap contract   : PASSED")
print("=" * 72)

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluation criteria
# MAGIC
# MAGIC | Criterion | Weight |
# MAGIC |---|---:|
# MAGIC | Distribution-center similarity | 25% |
# MAGIC | Daily time-series availability | 20% |
# MAGIC | Historical depth | 15% |
# MAGIC | Workload-target quality | 15% |
# MAGIC | Feature richness | 10% |
# MAGIC | Traditional ML suitability | 5% |
# MAGIC | LSTM suitability | 5% |
# MAGIC | Documentation and licensing | 5% |

# COMMAND ----------

criteria_schema = StructType(
    [
        StructField("dataset_name", StringType(), False),
        StructField("domain", StringType(), False),
        StructField("dc_similarity", DoubleType(), False),
        StructField("daily_time_series", DoubleType(), False),
        StructField("historical_depth", DoubleType(), False),
        StructField("workload_target", DoubleType(), False),
        StructField("feature_richness", DoubleType(), False),
        StructField("traditional_ml", DoubleType(), False),
        StructField("lstm", DoubleType(), False),
        StructField("documentation", DoubleType(), False),
        StructField("decision", StringType(), False),
    ]
)

candidate_rows = [
    (
        "DataCo SMART Supply Chain",
        "Supply chain and logistics",
        9.5, 8.0, 7.5, 9.0, 9.0, 8.5, 7.5, 8.0,
        "SELECTED",
    ),
    (
        "M5 Forecasting",
        "Retail demand forecasting",
        6.5, 10.0, 10.0, 8.5, 8.0, 9.5, 9.5, 10.0,
        "NOT_SELECTED",
    ),
    (
        "Corporación Favorita Grocery Sales",
        "Retail demand and replenishment",
        6.0, 10.0, 9.5, 8.0, 8.5, 9.0, 9.0, 9.0,
        "NOT_SELECTED",
    ),
    (
        "Rossmann Store Sales",
        "Retail demand forecasting",
        4.5, 9.5, 8.5, 6.5, 7.5, 9.0, 8.5, 9.0,
        "NOT_SELECTED",
    ),
]

candidate_df = spark.createDataFrame(candidate_rows, schema=criteria_schema)

weights = {
    "dc_similarity": 0.25,
    "daily_time_series": 0.20,
    "historical_depth": 0.15,
    "workload_target": 0.15,
    "feature_richness": 0.10,
    "traditional_ml": 0.05,
    "lstm": 0.05,
    "documentation": 0.05,
}

weighted_score = sum(
    F.col(column_name) * F.lit(weight)
    for column_name, weight in weights.items()
)

scored_candidates_df = (
    candidate_df
    .withColumn("weighted_score", F.round(weighted_score, 3))
    .orderBy(F.desc("weighted_score"))
)

display(scored_candidates_df)

# COMMAND ----------

selected_rows = (
    scored_candidates_df
    .filter(F.col("decision") == "SELECTED")
    .collect()
)

if len(selected_rows) != 1:
    raise RuntimeError(
        "Dataset evaluation must produce exactly one selected dataset."
    )

selected_dataset = selected_rows[0].asDict(recursive=True)

print("=" * 72)
print("DATASET EVALUATION COMPLETED")
print("=" * 72)
print(f"Selected dataset : {selected_dataset['dataset_name']}")
print(f"Domain           : {selected_dataset['domain']}")
print(f"Weighted score   : {selected_dataset['weighted_score']}")
print("Status           : PASSED")
print("=" * 72)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Final decision
# MAGIC
# MAGIC **Selected dataset:** DataCo SMART Supply Chain
# MAGIC
# MAGIC **Rationale:** It provides transaction-level logistics data, order and
# MAGIC shipping dates, quantities, delivery outcomes, product/customer context,
# MAGIC and sufficient operational similarity to support a distribution-center
# MAGIC workload forecasting prototype.
# MAGIC
# MAGIC **Primary workload target:** daily shipped/order-item quantity.
# MAGIC
# MAGIC ### Assumptions
# MAGIC - Daily transaction volume is a defensible proxy for operational workload.
# MAGIC - Labor standards and available capacity will be engineered later.
# MAGIC - Overtime will be recommended from the capacity gap, not predicted directly.
# MAGIC
# MAGIC ### Risks
# MAGIC - The public dataset does not contain actual workforce schedules or labor hours.
# MAGIC - Daily continuity and date coverage must be validated after Bronze ingestion.
# MAGIC - Public data is used as a portfolio proxy and not as Schneider Electric data.

# COMMAND ----------

