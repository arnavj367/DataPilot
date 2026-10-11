"""Smoke tests for the deterministic Pandas analysis tools."""
import pandas as pd
from pathlib import Path
from tools import (
    inspect_dataset, summary_statistics, group_and_aggregate,
    missing_value_analysis, correlation_analysis, detect_outliers, analyze_trend,
)

df = pd.read_csv(Path(__file__).parent / "data" / "sample_sales.csv")
print("INSPECT:", inspect_dataset(df))
print("\nREVENUE STATS:", summary_statistics(df, "Revenue"))
print("\nREVENUE BY REGION:", group_and_aggregate(df, "Region", "Revenue", "sum"))
print("\nMISSING VALUES:", missing_value_analysis(df))
print("\nCORRELATION:", correlation_analysis(df, "Revenue", "Profit"))
print("\nOUTLIERS:", detect_outliers(df, "Revenue"))
print("\nMONTHLY TREND:", analyze_trend(df, "Date", "Revenue", "MS"))
print("\nAll tool smoke tests completed.")
