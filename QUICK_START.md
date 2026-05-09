# QUICK START GUIDE

## Run the Application

```bash
cd "c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded"
streamlit run ui_check.py
```

Opens at: http://localhost:8501

---

## Upload a CSV

The pipeline automatically handles:
- Any column name (detects intelligently)
- 10+ date formats
- Multiple currencies (₹$£€¥)
- Accounting format negatives: (100) → -100

---

## Example CSV Formats (All Work!)

### Format 1: Simple ISO Dates
```
Date,Amount,Category,Merchant
2026-04-10,450,Food,Zomato
2026-04-11,1200,Shopping,Amazon
```

### Format 2: DD-MM-YYYY
```
Transaction Date,Amt,Type,Description
10-04-2026,450,Expense,Zomato
11-04-2026,1200,Expense,Amazon
```

### Format 3: With Symbols
```
txn_date,transaction_amount,cat,narration
2026-04-10,$450,Food,Zomato
2026-04-11,₹1200,Shopping,Amazon
```

### Format 4: Accounting Format
```
Date,Amount,Category,Merchant
2026-04-10,450,Food,Zomato
2026-04-11,(1200),Return,Amazon
```

---

## Test with Sample Data

1. Use provided `test_data.csv` (15 sample transactions)
2. Upload to app
3. See data quality report
4. Verify 15 rows inserted

---

## Troubleshooting

### No columns detected?
- Column names must contain keywords: date, amount, category, merchant
- Check CSV format is valid
- Try renaming columns

### Dates showing as invalid?
- Format must be one of 10 standard formats or unambiguous text
- Check for typos: "2026-13-01" (invalid month)
- System defaults to DD-MM-YYYY for ambiguous dates

### Some rows missing?
- Check data quality report for warnings
- Invalid dates/amounts are logged
- Duplicates are removed automatically
- Nulls are dropped

### Date range mismatch warning?
- Click "Use Database Range" button to align UI
- This syncs display with actual data in database

---

## File Structure

| File | Purpose |
|------|---------|
| `ui_check.py` | Main Streamlit app (350+ lines) |
| `data_pipeline.py` | Data ingestion pipeline (450+ lines) |
| `database.py` | SQLite operations + new functions |
| `test_data.csv` | Sample 15-row test data |
| `expenses.db` | SQLite database (auto-created) |

---

## CSV Requirements

**Required Columns:**
- At least one date column
- At least one amount column

**Optional Columns:**
- Category
- Merchant/Description

**Data Types:**
- Dates: Any standard format
- Amounts: Numeric (with/without symbols)
- Others: Text

---

## Features

✓ Flexible column detection
✓ Multiple date formats
✓ Currency symbol cleaning
✓ Data validation
✓ Auto-sync with UI
✓ Mismatch detection
✓ Debug visibility
✓ Failsafe processing

---

## Commands

### Clear Database
- Click "Clear All Data" button in sidebar
- Removes all transactions, starts fresh

### View Data Quality
- After upload, click "[DATA] Data Quality Report" expander
- See rows processed, dropped, date range, categories
- Review sample data preview

### Debug Info
- Check console output (terminal where you ran streamlit)
- Shows column detection, date parsing, cleaning results
- [OK], [WARNING], [ERROR] prefixes for quick scan

---

## Common CSV Fixes

**Problem:** Column names with spaces
**Solution:** System handles it automatically (strips whitespace)

**Problem:** Mixed date formats in same column
**Solution:** System tries 10 formats, invalid dates logged as warnings

**Problem:** Amounts like "1,234.56"
**Solution:** System handles comma thousands separator

**Problem:** Negative amounts in parentheses
**Solution:** System converts (100) → -100 automatically

**Problem:** Missing categories
**Solution:** System uses "Other" as default, shows in report

---

## Integration Points

### In Python Code:
```python
from data_pipeline import process_transaction_csv
from database import get_transaction_count, get_database_date_range

# Process CSV
cleaned_df, warnings, debug_info = process_transaction_csv(file)

# Get stats
count = get_transaction_count()
min_date, max_date = get_database_date_range()
```

### In Streamlit App:
```python
from ui_check import process_uploaded_csv, insert_cleaned_data_to_db

# Upload and process
cleaned_df, warnings, debug_info = process_uploaded_csv(file)

# Insert to DB
success, errors = insert_cleaned_data_to_db(cleaned_df)
```

---

## Performance

- 15 rows: <1 second
- 100 rows: <2 seconds
- 1000 rows: <5 seconds
- Depends on: CSV size, disk speed, column complexity

---

## Support

For issues:
1. Check console output for error messages
2. Review data quality report warnings
3. Check PIPELINE_COMPLETE.md for architecture details
4. Verify CSV format matches examples above

---

## Success Criteria

✓ CSV uploads without errors
✓ Data quality report shows expected counts
✓ Date range auto-syncs to UI
✓ Insights display with correct numbers
✓ No rows silently lost

All criteria met → System working correctly!
