# Databricks notebook source
# MAGIC %md
# MAGIC # Dataset Registry
# MAGIC
# MAGIC ## Business objective
# MAGIC Persist shared dataset definitions in S3 as Parquet so that Databricks
# MAGIC workflows can discover enabled sources without relying on notebook memory.
# MAGIC
# MAGIC Run this notebook only when a dataset definition is added or changed.

# COMMAND ----------

# MAGIC %run ../00_project_setup/00_project_setup

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# ======================================================
# Dataset Registry Schema
# ======================================================

registry_schema = StructType(
    [
        StructField("dataset_id", IntegerType(), False),
        StructField("dataset_name", StringType(), False),
        StructField("dataset_key", StringType(), False),
        StructField("dataset_version", StringType(), False),
        StructField("dataset_owner", StringType(), False),
        StructField("source_type", StringType(), False),

        # Human-readable dataset webpage
        StructField("source_location", StringType(), False),

        # Machine-readable provider identifier
        StructField("source_reference", StringType(), False),

        StructField("source_format", StringType(), False),
        StructField("landing_folder", StringType(), False),
        StructField("enabled", BooleanType(), False),
        StructField("status", StringType(), False),
    ]
)

dataset_registry = [
    (
        1,
        "DataCo SMART Supply Chain",
        "dataco_supply_chain",
        "1.0",
        "Issouf KABRE",

        "Kaggle",

        # Human readable page
        "https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis",

        # Machine readable identifier
        "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis",

        "csv",

        "dataco_supply_chain",

        True,

        "READY_FOR_DOWNLOAD",
    )
]

registry_df = spark.createDataFrame(
    dataset_registry,
    schema=registry_schema,
)

# Reject duplicate business keys before persistence.
duplicate_keys = (
    registry_df
    .groupBy("dataset_key")
    .count()
    .filter(F.col("count") > 1)
    .count()
)

if duplicate_keys > 0:
    raise ValueError(
        "Dataset registry contains duplicate dataset_key values."
    )

# Validate required source URLs.
invalid_source_locations = (
    registry_df
    .filter(
        F.col("source_location").isNull()
        | (F.trim(F.col("source_location")) == "")
        | F.col("source_location").contains("<owner>")
        | F.col("source_location").contains("<dataset-name>")
    )
    .count()
)

if invalid_source_locations > 0:
    print(
        f"{invalid_source_locations} dataset(s) still require "
        "a verified source URL."
    )

display(registry_df)

# COMMAND ----------

(
    registry_df.write
    .mode("overwrite")
    .parquet(DATASET_REGISTRY_PATH)
)

print(f"Dataset registry written to: {DATASET_REGISTRY_PATH}")

# COMMAND ----------

persisted_registry_df = spark.read.parquet(
    DATASET_REGISTRY_PATH
)

display(persisted_registry_df)
persisted_registry_df.printSchema()

# COMMAND ----------

