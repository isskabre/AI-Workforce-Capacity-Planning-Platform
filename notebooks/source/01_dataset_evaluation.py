# Databricks notebook source
# MAGIC %md
# MAGIC # Implementation 02 — Public Dataset Evaluation and Selection
# MAGIC
# MAGIC ## Business Objective
# MAGIC
# MAGIC Select a public dataset that can support the development of an AI Workforce
# MAGIC Capacity Planning prototype for a distribution center.
# MAGIC
# MAGIC The selected dataset must be suitable for:
# MAGIC
# MAGIC - Daily workload forecasting
# MAGIC - Traditional machine learning model comparison
# MAGIC - LSTM experimentation
# MAGIC - Capacity planning simulation
# MAGIC - Overtime recommendation
# MAGIC - Stakeholder demonstration
# MAGIC
# MAGIC ## Core Decision
# MAGIC
# MAGIC The project will forecast future operational workload rather than directly
# MAGIC predict overtime.
# MAGIC
# MAGIC Forecasted workload will later be converted into:
# MAGIC
# MAGIC 1. Required labor hours
# MAGIC 2. Available labor capacity
# MAGIC 3. Capacity gap
# MAGIC 4. Recommended overtime

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset Evaluation Criteria
# MAGIC
# MAGIC Each candidate dataset will be evaluated using the following criteria:
# MAGIC
# MAGIC | Criterion | Weight |
# MAGIC |---|---:|
# MAGIC | Distribution-center similarity | 25% |
# MAGIC | Daily time-series availability | 20% |
# MAGIC | Historical depth | 15% |
# MAGIC | Workload target quality | 15% |
# MAGIC | Feature richness | 10% |
# MAGIC | Traditional ML suitability | 5% |
# MAGIC | LSTM suitability | 5% |
# MAGIC | Documentation and licensing | 5% |
# MAGIC
# MAGIC The final dataset score will be calculated as a weighted score out of 10.

# COMMAND ----------

from pyspark.sql.types import (
    FloatType,
    StringType,
    StructField,
    StructType,
)

# Define the schema explicitly because the score columns
# currently contain only null values.
candidate_schema = StructType(
    [
        StructField("dataset_name", StringType(), False),
        StructField("domain", StringType(), False),
        StructField("dc_similarity_score", FloatType(), True),
        StructField("daily_time_series_score", FloatType(), True),
        StructField("historical_depth_score", FloatType(), True),
        StructField("workload_target_score", FloatType(), True),
        StructField("feature_richness_score", FloatType(), True),
        StructField("traditional_ml_score", FloatType(), True),
        StructField("lstm_score", FloatType(), True),
        StructField("documentation_score", FloatType(), True),
        StructField("evaluation_status", StringType(), False),
    ]
)

dataset_candidates = [
    (
        "SMART Supply Chain",
        "Supply chain and logistics",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "Pending",
    ),
    (
        "M5 Forecasting",
        "Retail demand and distribution",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "Pending",
    ),
    (
        "Corporación Favorita Grocery Sales",
        "Retail demand and replenishment",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "Pending",
    ),
    (
        "Rossmann Store Sales",
        "Retail demand forecasting",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "Pending",
    ),
]

dataset_candidates_df = spark.createDataFrame(
    dataset_candidates,
    schema=candidate_schema,
)

display(dataset_candidates_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Candidate 1 — SMART Supply Chain
# MAGIC
# MAGIC ### Dataset purpose
# MAGIC
# MAGIC The SMART Supply Chain dataset contains transactional supply-chain information
# MAGIC related to orders, customers, products, shipping, delivery, and distribution.
# MAGIC
# MAGIC ### Evaluation question
# MAGIC
# MAGIC Does this dataset contain a sufficiently long and continuous daily time series
# MAGIC that can be used to forecast distribution-center workload?

# COMMAND ----------

# MAGIC %md
# MAGIC ### Initial findings
# MAGIC
# MAGIC | Attribute | Finding |
# MAGIC |---|---|
# MAGIC | Domain | Supply chain and logistics |
# MAGIC | Business process | Orders, shipping, delivery, products, and customers |
# MAGIC | Operational similarity | High |
# MAGIC | Primary data grain | Transaction or order-line level |
# MAGIC | Potential workload measure | Daily orders, daily order lines, or daily shipped units |
# MAGIC | Forecasting suitability | To be verified |
# MAGIC | Main risk | Transactional data may not provide enough continuous daily history |

# COMMAND ----------

from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
)

smart_facts_schema = StructType(
    [
        StructField("attribute", StringType(), False),
        StructField("finding", StringType(), False),
        StructField("status", StringType(), False),
    ]
)

smart_supply_chain_facts = [
    (
        "Domain",
        "Supply chain and logistics",
        "Confirmed",
    ),
    (
        "Business processes",
        "Orders, products, customers, shipping, delivery, and distribution",
        "Confirmed",
    ),
    (
        "Primary grain",
        "Transactional order or order-line records",
        "Confirmed",
    ),
    (
        "Potential workload target",
        "Daily order count, order-line count, or shipped units",
        "Candidate",
    ),
    (
        "Daily continuity",
        "Must be verified from the source data",
        "Pending",
    ),
    (
        "Historical depth",
        "Must be verified from the source data",
        "Pending",
    ),
    (
        "LSTM suitability",
        "Depends on the number of continuous daily observations",
        "Pending",
    ),
]

smart_supply_chain_facts_df = spark.createDataFrame(
    smart_supply_chain_facts,
    schema=smart_facts_schema,
)

display(smart_supply_chain_facts_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset Evaluation Scorecard
# MAGIC
# MAGIC Each dataset will receive a score from **1 (Poor)** to **10 (Excellent)**.
# MAGIC
# MAGIC The scores are based on objective analysis rather than preference.

# COMMAND ----------

from pyspark.sql.types import *

score_schema = StructType([
    StructField("criterion", StringType(), False),
    StructField("weight_percent", IntegerType(), False),
])

evaluation_criteria = [

    ("Distribution Center Similarity",25),

    ("Daily Time Series",20),

    ("Historical Depth",15),

    ("Workload Target Quality",15),

    ("Feature Richness",10),

    ("Traditional ML Suitability",5),

    ("LSTM Suitability",5),

    ("Documentation & License",5)

]

criteria_df = spark.createDataFrame(
    evaluation_criteria,
    schema=score_schema
)

display(criteria_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset Research Matrix
# MAGIC
# MAGIC Before assigning any score, objective evidence will be collected for each dataset.
# MAGIC
# MAGIC Only verified information will be used during scoring.

# COMMAND ----------

from pyspark.sql.types import *

research_schema = StructType([
    StructField("dataset_name", StringType(), False),
    StructField("official_source", StringType(), True),
    StructField("years_of_history", StringType(), True),
    StructField("number_of_records", StringType(), True),
    StructField("time_granularity", StringType(), True),
    StructField("target_variable", StringType(), True),
    StructField("license", StringType(), True),
    StructField("status", StringType(), False),
])

research_df = spark.createDataFrame(
    [
        (
            "SMART Supply Chain",
            None,
            None,
            None,
            None,
            None,
            None,
            "Research Pending",
        ),
        (
            "M5 Forecasting",
            None,
            None,
            None,
            None,
            None,
            None,
            "Research Pending",
        ),
        (
            "Corporación Favorita Grocery Sales",
            None,
            None,
            None,
            None,
            None,
            None,
            "Research Pending",
        ),
        (
            "Rossmann Store Sales",
            None,
            None,
            None,
            None,
            None,
            None,
            "Research Pending",
        ),
    ],
    schema=research_schema,
)

display(research_df)

# COMMAND ----------

