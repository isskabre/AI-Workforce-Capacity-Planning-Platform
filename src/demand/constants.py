"""
Demand Intelligence Engine Constants

Centralized constants used throughout the Demand Intelligence module.
"""

# ============================================================
# Dataset Columns
# ============================================================

DATE_COLUMN = "order_date"

ORDER_COUNT_COLUMN = "order_count"

ORDER_LINE_COUNT_COLUMN = "order_line_count"

WORKLOAD_UNITS_COLUMN = "workload_units"

GROSS_SALES_COLUMN = "gross_sales"

CUSTOMER_COUNT_COLUMN = "customer_count"

# ============================================================
# Forecast Targets
# ============================================================

PRIMARY_FORECAST_TARGET = ORDER_LINE_COUNT_COLUMN

SECONDARY_FORECAST_TARGETS = (
    ORDER_COUNT_COLUMN,
    WORKLOAD_UNITS_COLUMN,
)

# ============================================================
# Supported Forecast Horizons (Days)
# ============================================================

SUPPORTED_FORECAST_HORIZONS = (
    1,
    7,
    14,
    30,
    60,
    90,
)

# ============================================================
# Business Feature Names
# ============================================================

BUSINESS_FEATURES = (
    "avg_lines_per_order",
    "avg_units_per_order",
    "avg_units_per_line",
    "sales_per_order",
    "sales_per_line",
)

# ============================================================
# ML Feature Categories
# ============================================================

ML_FEATURE_GROUPS = (
    "lag",
    "rolling",
    "trend",
    "seasonality",
)