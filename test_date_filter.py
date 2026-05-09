#!/usr/bin/env python3
"""
Test the load_transactions_from_db function to see if date filtering is the issue
"""

from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions
from parser import parse_sms
from categorizer import categorize
from datetime import datetime, timedelta
import pandas as pd
import sys

# This is copied from ui_check.py
def load_transactions_from_db(start_date, end_date):
    """Load real transactions from SQLite database."""
    try:
        create_table()  # Ensure table exists
        rows = fetch_all_transactions()
        
        if not rows:
            return pd.DataFrame()
        
        # Convert database rows to DataFrame
        # Row format: (id, amount, type, merchant, category, date, source)
        records = []
        for row in rows:
            try:
                records.append({
                    "Date": pd.to_datetime(row[5]),  # date column
                    "Amount": float(row[1]),  # amount column
                    "Category": row[4] if row[4] else "Others",  # category column
                    "Description": row[3]  # merchant column
                })
            except (IndexError, ValueError):
                continue
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        print(f"DataFrame before filtering: {len(df)} rows")
        print(f"Date range: {start_date} to {end_date}")
        print(f"df['Date'].min(): {df['Date'].min()}")
        print(f"df['Date'].max(): {df['Date'].max()}")
        
        df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]
        print(f"DataFrame after filtering: {len(df)} rows")
        return df
    except Exception as e:
        print(f"ERROR in load_transactions_from_db: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

# Clear and start fresh
create_table()
clear_all_transactions()
print("✓ Database cleared\n")

# Insert a transaction
sms = "Rs.450 spent on Zomato"
data = parse_sms(sms)
category = categorize(data["merchant"])

insert_transaction(
    amount=data["amount"],
    type_=data["type"],
    merchant=data["merchant"],
    category=category,
    date=datetime.now().strftime("%Y-%m-%d"),
    source="sms"
)
print(f"✓ Inserted transaction for today: {datetime.now().strftime('%Y-%m-%d')}\n")

# Test with expected default date range (90 days ago to today)
today = datetime.today().date()
start = today - timedelta(days=90)
end = today

print(f"📊 Testing date range: {start} to {end}")
df = load_transactions_from_db(start, end)
print(f"\nResult: {len(df)} transactions loaded")
if not df.empty:
    print(df)
else:
    print("WARNING: Empty DataFrame returned!")
