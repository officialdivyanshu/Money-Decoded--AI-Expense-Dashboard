#!/usr/bin/env python3
"""
Simulate the complete Streamlit workflow for SMS insertion and analysis
"""

from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions
from parser import parse_sms
from categorizer import categorize
from insights import get_total_spending, get_category_spending, get_top_category
from datetime import datetime, timedelta
import pandas as pd
import random

def load_transactions_from_db(start_date, end_date):
    """Load real transactions from SQLite database."""
    try:
        create_table()
        rows = fetch_all_transactions()
        
        if not rows:
            print("  No rows returned from database")
            return pd.DataFrame()
        
        records = []
        for row in rows:
            try:
                records.append({
                    "Date": pd.to_datetime(row[5]),
                    "Amount": float(row[1]),
                    "Category": row[4] if row[4] else "Others",
                    "Description": row[3]
                })
            except (IndexError, ValueError) as e:
                print(f"  Skipping row due to error: {e}")
                continue
        
        if not records:
            print("  No records converted from rows")
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]
        print(f"  Loaded {len(df)} transactions after date filtering")
        return df
    except Exception as e:
        print(f"  ERROR in load_transactions_from_db: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def compute_metrics(df):
    total_spend   = df["Amount"].sum()
    top_cat       = df.groupby("Category")["Amount"].sum().idxmax()
    avg_daily     = df.groupby("Date")["Amount"].sum().mean()
    budget        = total_spend * 1.15
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

def check_if_has_transactions():
    """Check if database has any transactions."""
    try:
        rows = fetch_all_transactions()
        has_trans = len(rows) > 0 if rows else False
        print(f"  Checking transactions: {has_trans} (found {len(rows) if rows else 0} rows)")
        return has_trans
    except Exception as e:
        print(f"  ERROR checking transactions: {e}")
        return False

print("=" * 60)
print("SIMULATING STREAMLIT WORKFLOW")
print("=" * 60)

# STEP 1: Initial page load
print("\n[STEP 1] Initial page load (app startup)")
print("-" * 60)
create_table()
print("  create_table() called")
clear_all_transactions()
print("  clear_all_transactions() called")

# STEP 2: User adds SMS transaction
print("\n[STEP 2] User adds SMS transaction")
print("-" * 60)
sms = "Rs.450 spent on Zomato"
print(f"  SMS input: '{sms}'")
data = parse_sms(sms)
print(f"  Parsed: {data}")
category = categorize(data["merchant"])
print(f"  Category: {category}")
insert_transaction(
    amount=data["amount"],
    type_=data["type"],
    merchant=data["merchant"],
    category=category,
    date=datetime.now().strftime("%Y-%m-%d"),
    source="sms"
)
print(f"  ✓ Transaction inserted")

# STEP 3: Streamlit reruns after st.rerun() is called
print("\n[STEP 3] Streamlit reruns (simulating st.rerun())")
print("-" * 60)
print("  Rebuilding app...")
# Note: app_initialized would be in session state, so we don't clear

# STEP 4: check_if_has_transactions 
print("\n[STEP 4] Checking if has transactions")
print("-" * 60)
has_transactions = check_if_has_transactions()

if not has_transactions:
    print("\n  ❌ NO TRANSACTIONS FOUND - would show empty state!")
else:
    print(f"\n  ✓ Found transactions - proceeding to load data")
    
    # STEP 5: Load data for analysis
    today = datetime.today().date()
    start = today - timedelta(days=90)
    end = today
    
    print(f"\n[STEP 5] Loading transactions for date range: {start} to {end}")
    print("-" * 60)
    df = load_transactions_from_db(start, end)
    
    if df.empty:
        print(f"\n  ❌ EMPTY DATAFRAME - would show 'no transactions in this date range'!")
    else:
        print(f"\n  ✓ Loaded DataFrame with {len(df)} row(s)")
        print(f"\n  DataFrame:")
        print(df)
        
        # STEP 6: Compute metrics
        print(f"\n[STEP 6] Computing metrics")
        print("-" * 60)
        try:
            m = compute_metrics(df)
            print(f"  ✓ Metrics computed:")
            for k, v in m.items():
                print(f"    - {k}: {v}")
            print(f"\n  ✓ Would render analytics dashboard!")
        except Exception as e:
            print(f"  ❌ ERROR computing metrics: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "=" * 60)
print("END OF SIMULATION")
print("=" * 60)
