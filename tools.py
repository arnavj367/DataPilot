"""Safe, deterministic Pandas tools used by the DataPilot agent."""
from __future__ import annotations

import json
import pandas as pd


def _json_safe(value):
    """Convert Pandas/numpy values into JSON-serializable Python values."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    if pd.isna(value) if not isinstance(value, (list, dict, tuple)) else False:
        return None
    return value


def inspect_dataset(df: pd.DataFrame) -> dict:
    """Return shape, columns, data types, and a small preview."""
    return {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "columns": [
            {"name": str(column), "dtype": str(df[column].dtype),
             "missing": int(df[column].isna().sum())}
            for column in df.columns
        ],
        "preview": df.head(5).to_dict(orient="records"),
    }


def summary_statistics(df: pd.DataFrame, column: str) -> dict:
    """Calculate descriptive statistics for a numeric column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist.", "available_columns": list(df.columns)}
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' is not numeric."}
    series = df[column].dropna()
    if series.empty:
        return {"error": f"Column '{column}' has no numeric values."}
    return _json_safe({
        "column": column,
        "count": int(series.count()),
        "mean": series.mean(),
        "median": series.median(),
        "min": series.min(),
        "max": series.max(),
        "std": series.std(),
        "sum": series.sum(),
    })


def group_and_aggregate(
    df: pd.DataFrame, group_column: str, value_column: str, operation: str = "sum"
) -> dict:
    """Aggregate a numeric column by groups such as region or product."""
    if group_column not in df.columns:
        return {"error": f"Group column '{group_column}' does not exist.", "available_columns": list(df.columns)}
    if value_column not in df.columns:
        return {"error": f"Value column '{value_column}' does not exist.", "available_columns": list(df.columns)}
    if not pd.api.types.is_numeric_dtype(df[value_column]):
        return {"error": f"Value column '{value_column}' is not numeric."}
    operation = operation.lower()
    if operation not in {"sum", "mean", "median", "min", "max", "count"}:
        return {"error": "Unsupported operation. Choose sum, mean, median, min, max, or count."}
    grouped = df.groupby(group_column, dropna=False)[value_column].agg(operation).reset_index()
    grouped.columns = [group_column, f"{operation}_{value_column}"]
    return {
        "group_column": group_column,
        "value_column": value_column,
        "operation": operation,
        "results": _json_safe(grouped.to_dict(orient="records")),
    }


def missing_value_analysis(df: pd.DataFrame) -> dict:
    """Count missing values in each column and across the whole dataset."""
    counts = df.isna().sum()
    return {
        "total_missing_cells": int(counts.sum()),
        "by_column": [{"column": str(col), "missing": int(count)} for col, count in counts.items()],
    }


def correlation_analysis(df: pd.DataFrame, column_a: str, column_b: str) -> dict:
    """Calculate Pearson correlation between two numeric columns."""
    for col in (column_a, column_b):
        if col not in df.columns:
            return {"error": f"Column '{col}' does not exist.", "available_columns": list(df.columns)}
        if not pd.api.types.is_numeric_dtype(df[col]):
            return {"error": f"Column '{col}' is not numeric."}
    valid = df[[column_a, column_b]].dropna()
    if len(valid) < 2:
        return {"error": "At least two complete rows are needed to calculate correlation."}
    corr = valid[column_a].corr(valid[column_b])
    return {"column_a": column_a, "column_b": column_b, "pearson_correlation": _json_safe(corr)}


def detect_outliers(df: pd.DataFrame, column: str) -> dict:
    """Find numeric outliers using the 1.5 x IQR rule."""
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist.", "available_columns": list(df.columns)}
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' is not numeric."}
    series = df[column].dropna()
    if series.empty:
        return {"error": f"Column '{column}' has no numeric values."}
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = df[column].notna() & ((df[column] < lower) | (df[column] > upper))
    return {
        "column": column, "q1": _json_safe(q1), "q3": _json_safe(q3),
        "lower_bound": _json_safe(lower), "upper_bound": _json_safe(upper),
        "outlier_count": int(mask.sum()),
        "outliers": _json_safe(df.loc[mask].to_dict(orient="records")),
    }


def analyze_trend(
    df: pd.DataFrame, date_column: str, value_column: str, frequency: str = "MS"
) -> dict:
    """Aggregate a numeric value over time. frequency: D, W, MS, or QS."""
    for col in (date_column, value_column):
        if col not in df.columns:
            return {"error": f"Column '{col}' does not exist.", "available_columns": list(df.columns)}
    if not pd.api.types.is_numeric_dtype(df[value_column]):
        return {"error": f"Value column '{value_column}' is not numeric."}
    if frequency not in {"D", "W", "MS", "QS"}:
        return {"error": "frequency must be D (daily), W (weekly), MS (monthly), or QS (quarterly)."}
    dates = pd.to_datetime(df[date_column], errors="coerce")
    work = pd.DataFrame({"date": dates, "value": df[value_column]})
    work = work.dropna(subset=["date", "value"]).sort_values("date")
    if work.empty:
        return {"error": "No valid date/value rows were found."}
    result = work.set_index("date")["value"].resample(frequency).sum().dropna().reset_index()
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    return {"date_column": date_column, "value_column": value_column,
            "frequency": frequency, "results": _json_safe(result.to_dict(orient="records"))}


TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_dataset",
            "description": "Inspect dataset size, column names, data types, missing counts, and first five rows.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summary_statistics",
            "description": "Calculate count, mean, median, min, max, standard deviation, and sum for a numeric column.",
            "parameters": {"type": "object", "properties": {"column": {"type": "string", "description": "Numeric column name"}}, "required": ["column"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "group_and_aggregate",
            "description": "Group rows by a category and aggregate a numeric column. Operations: sum, mean, median, min, max, count.",
            "parameters": {"type": "object", "properties": {
                "group_column": {"type": "string"}, "value_column": {"type": "string"},
                "operation": {"type": "string", "enum": ["sum", "mean", "median", "min", "max", "count"]}},
                "required": ["group_column", "value_column", "operation"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "missing_value_analysis",
            "description": "Count missing cells overall and for each column.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "correlation_analysis",
            "description": "Calculate Pearson correlation between two numeric columns.",
            "parameters": {"type": "object", "properties": {"column_a": {"type": "string"}, "column_b": {"type": "string"}}, "required": ["column_a", "column_b"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_outliers",
            "description": "Detect outliers in a numeric column using the 1.5 times IQR rule.",
            "parameters": {"type": "object", "properties": {"column": {"type": "string"}}, "required": ["column"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_trend",
            "description": "Aggregate a numeric column over time. frequency: D daily, W weekly, MS monthly, QS quarterly.",
            "parameters": {"type": "object", "properties": {
                "date_column": {"type": "string"}, "value_column": {"type": "string"},
                "frequency": {"type": "string", "enum": ["D", "W", "MS", "QS"]}},
                "required": ["date_column", "value_column", "frequency"]},
        },
    },
]


def run_tool(name: str, df: pd.DataFrame, args: dict) -> dict:
    """Dispatch a model-requested tool to a known Python function."""
    functions = {
        "inspect_dataset": inspect_dataset,
        "summary_statistics": summary_statistics,
        "group_and_aggregate": group_and_aggregate,
        "missing_value_analysis": missing_value_analysis,
        "correlation_analysis": correlation_analysis,
        "detect_outliers": detect_outliers,
        "analyze_trend": analyze_trend,
    }
    if name not in functions:
        return {"error": f"Unknown tool: {name}"}
    try:
        return functions[name](df, **args)
    except TypeError as exc:
        return {"error": f"Invalid arguments for {name}: {exc}"}
