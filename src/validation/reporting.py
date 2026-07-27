"""Validation reporting and persistence."""

from pyspark.sql import DataFrame, SparkSession

from .models import ValidationReport


def validation_report_to_dataframe(
    *,
    spark: SparkSession,
    report: ValidationReport,
) -> DataFrame:
    return spark.createDataFrame(report.to_rows())


def persist_validation_report(
    *,
    report_df: DataFrame,
    output_path: str,
    mode: str = "append",
) -> None:
    (
        report_df.write
        .mode(mode)
        .option("compression", "snappy")
        .parquet(output_path)
    )


def print_validation_report(report: ValidationReport) -> None:
    print("=" * 80)
    print("ENTERPRISE DATA QUALITY VALIDATION")
    print("=" * 80)
    print(f"Dataset  : {report.dataset_name}")
    print(f"Layer    : {report.dataset_layer}")
    print(f"Run ID   : {report.run_id}")
    print(f"Passed   : {report.passed_count}")
    print(f"Warnings : {report.warning_count}")
    print(f"Failed   : {report.failed_count}")
    print(f"Status   : {report.status.value}")
    print("=" * 80)
    for result in report.results:
        print(f"[{result.status.value:7}] {result.rule_name}: {result.message}")
