#!/usr/bin/env python3
"""
Debug script to test the transaction insertion and analysis flow
"""

from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions
from parser import parse_sms
from categorizer import categorize
from insights import get_total_spending, get_category_spending, get_top_category
from datetime import datetime
import pandas as pd

# Clear and start fresh
create_table()
clear_all_transactions()
print("✓ Database cleared")

# Test SMS parsing
sms = "Rs.450 spent on Zomato"
print(f"\n📱 Testing SMS: {sms}")
data = parse_sms(sms)
print(f"Parsed data: {data}")

# Categorize
category = categorize(data["merchant"])
print(f"Category assigned: {category}")

# Insert transaction
print(f"\n💾 Inserting transaction...")
insert_transaction(
    amount=data["amount"],
    type_=data["type"],
    merchant=data["merchant"],
    category=category,
    date=datetime.now().strftime("%Y-%m-%d"),
    source="sms"
)
print("✓ Transaction inserted")

# Fetch all transactions
print(f"\n📊 Fetching all transactions...")
rows = fetch_all_transactions()
print(f"Raw rows from DB: {rows}")

if rows:
    print(f"\n✓ Found {len(rows)} transaction(s)")
    
    # Test data conversion (like in load_transactions_from_db)
    records = []
    for row in rows:
        print(f"Processing row: {row}")
        try:
            record = {
                "Date": pd.to_datetime(row[5]),  # date column
                "Amount": float(row[1]),  # amount column
                "Category": row[4] if row[4] else "Others",  # category column
                "Description": row[3]  # merchant column
            }
            print(f"  → Converted to: {record}")
            records.append(record)
        except (IndexError, ValueError) as e:
            print(f"  → ERROR: {e}")
            continue
    
    if records:
        df = pd.DataFrame(records)
        print(f"\n📈 DataFrame created:")
        print(df)
        print(f"DataFrame types: {df.dtypes}")
        
        # Test metrics calculation
        print(f"\n🧮 Testing metrics:")
        try:
            total = get_total_spending()
            print(f"Total spending: {total}")
            
            cat_breakdown = get_category_spending()
            print(f"Category breakdown: {cat_breakdown}")
            
            top_cat = get_top_category()
            print(f"Top category: {top_cat}")
        except Exception as e:
            print(f"ERROR in metrics: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No records converted from rows")
else:
    print("❌ No transactions returned from database")
