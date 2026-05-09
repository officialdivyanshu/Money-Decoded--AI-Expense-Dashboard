#!/usr/bin/env python3
"""
Test compute_metrics with a single row to see if there's an error
"""

from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions
from parser import parse_sms
from categorizer import categorize
from datetime import datetime, timedelta
import pandas as pd

def compute_metrics(df):
    """Copied from ui_check.py"""
    total_spend   = df["Amount"].sum()
    top_cat       = df.groupby("Category")["Amount"].sum().idxmax()
    avg_daily     = df.groupby("Date")["Amount"].sum().mean()
    budget        = total_spend * 1.15          # pretend budget
    savings_pct   = max(0, round((budget - total_spend) / budget * 100, 1))
    weekend_mask  = df["Date"].dt.dayofweek >= 5
    wknd_avg = df[weekend_mask]["Amount"].mean() if weekend_mask.any() else 0
    wkd_avg  = df[~weekend_mask]["Amount"].mean() if (~weekend_mask).any() else 1
    weekend_uplift = round((wknd_avg / wkd_avg - 1) * 100, 1) if wkd_avg else 0
    return {
        "total_spend":   total_spend,
        "top_cat":        top_cat,
        "avg_daily":      avg_daily,
        "savings_pct":    savings_pct,
        "weekend_uplift": weekend_uplift,
    }

# Create test dataframe with single row
records = [{
    "Date": pd.to_datetime("2026-05-01"),
    "Amount": 450.0,
    "Category": "food",
    "Description": "Zomato"
}]

df = pd.DataFrame(records)
print(f"DataFrame:")
print(df)
print(f"\nDataframe info:")
print(df.info())

print(f"\n🧮 Testing compute_metrics...")
try:
    m = compute_metrics(df)
    print(f"✓ Metrics calculated successfully:")
    for k, v in m.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
