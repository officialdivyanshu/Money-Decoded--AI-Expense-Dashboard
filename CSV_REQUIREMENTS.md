# CSV Requirements - Money Decoded Dashboard

## ✅ MANDATORY COLUMNS (REQUIRED)

### 1. **DATE Column** (Required)
- **Column Name:** Can be: `date`, `Date`, `Transaction Date`, `Txn Date`, `Date of Transaction`, etc.
- **Format:** Any of these formats work:
  - `2026-04-01` (YYYY-MM-DD) ← **BEST**
  - `01-04-2026` (DD-MM-YYYY)
  - `04/01/2026` (MM/DD/YYYY)
  - `1 Apr 2026` (D Mon YYYY)
  - `April 1, 2026`
- **Requirements:**
  - Must be valid date (no future dates beyond today)
  - Cannot be blank/empty
  - All rows should have dates

### 2. **AMOUNT Column** (Required)
- **Column Name:** Can be: `amount`, `Amount`, `Value`, `Debit`, `Credit`, `Transaction Amount`, etc.
- **Format - TWO OPTIONS:**

  **Option A: Negative = Expenses, Positive = Income** (Most Common)
  ```
  -1500    (expense, ₹1500)
  -200     (expense, ₹200)
  3000     (income, ₹3000)
  ```
  
  **Option B: All Positive - System Auto-Detects** (Your current CSV)
  ```
  1500     (detected as expense based on category)
  200      (detected as expense based on category)
  3000     (detected as expense based on category)
  ```

- **Requirements:**
  - Must be numeric (decimal OK: 123.45)
  - No currency symbols (₹, $, €, etc.) - just numbers
  - No commas (use 1000.50, NOT 1,000.50)
  - Cannot be blank/empty
  - Cannot be 0 (zero transactions are ignored)

---

## ✅ HIGHLY RECOMMENDED COLUMNS (For Best Analysis)

### 3. **CATEGORY Column** (Recommended)
- **Column Name:** Can be: `category`, `Category`, `Type`, `Expense Type`, `Category Name`, etc.
- **Values:** Should use one of these standard categories:
  ```
  Food & Dining
  Transport
  Shopping
  Entertainment
  Utilities
  Health
  Subscriptions
  Travel
  Others
  ```
- **Or:** Any custom categories you want (System will group them)
- **Example:**
  ```
  category
  Groceries
  Food
  Transport
  Netflix
  Shopping
  Healthcare
  ```
- **Requirements:**
  - Should be consistent (e.g., don't use "food" AND "Food & Dining")
  - At least 1 transaction per category for it to show in charts
  - Helps with pie charts, insights, and category breakdown

### 4. **MERCHANT/DESCRIPTION Column** (Recommended)
- **Column Name:** Can be: `merchant`, `Merchant`, `Description`, `Vendor`, `Shop Name`, `Business`, etc.
- **Values:** Name of the business/store
- **Examples:**
  ```
  DMart
  Zomato
  Netflix
  Uber
  Amazon
  Apollo Pharmacy
  ```
- **Requirements:**
  - Should be descriptive
  - Helps if Category column is missing (system auto-categorizes)
  - Makes transaction table more readable

---

## ❌ COLUMNS TO AVOID

- ❌ Running Balance / Total
- ❌ Account Number / Card Number
- ❌ Reference ID / Transaction ID (takes extra space)
- ❌ Status / Pending columns
- ❌ Blank columns with no header
- ❌ Multiple date columns (system only uses first detected)

---

## 📋 PERFECT CSV FORMAT (Example)

```csv
date,amount,merchant,category
2026-04-01,-3796.67,DMart,Groceries
2026-04-01,-1004.63,Uber,Transport
2026-04-01,-560.46,Zomato,Food & Dining
2026-04-02,-2638.64,Netflix,Entertainment
2026-04-02,-147.05,Amazon,Shopping
2026-04-02,-743.35,Netflix,Entertainment
2026-04-03,5000,Salary,Income
2026-04-03,-692.74,DMart,Groceries
```

---

## ✅ ALTERNATIVE FORMATS THAT WORK

### Format 1: Lowercase, All Positive (Auto-Detect Mode)
```csv
date,amount,merchant,category
2026-04-01,3796.67,DMart,Groceries
2026-04-01,1004.63,Uber,Transport
2026-04-01,5000,Salary,Income
```
✓ System detects based on category keywords (Groceries = expense, Salary = income)

### Format 2: Date-Amount-Description Only
```csv
Transaction Date,Value,Description
2026-04-01,-1500,DMart Grocery Store
2026-04-02,-200,Uber Ride
2026-04-03,3000,Salary Income
```
✓ System auto-categorizes based on merchant keywords

### Format 3: Different Column Names
```csv
Txn Date,Debit,Credit,Vendor
2026-04-01,500,,Zomato
2026-04-02,200,,Amazon
2026-04-03,,3000,Employer Salary
```
✓ System auto-detects columns (Debit = expenses, Credit = income)

---

## 🔴 COMMON ISSUES & HOW TO FIX

| Issue | Cause | Fix |
|-------|-------|-----|
| "No date found" | Date column missing or wrong format | Use YYYY-MM-DD format or one from list above |
| "No amount found" | Amount column has ₹ symbols or commas | Remove ₹/$  and commas: 1000.50 not ₹1,000.50 |
| "Empty pie chart" | All transactions are income (positive) OR category column missing | Add proper negative amounts OR add category column |
| "No monthly trend" | Same issue - all income or no expenses | Fix amount signs: negative = expense |
| "Empty daily chart" | No transactions in current month | Add transactions from current month (2026 for example) |
| "Generic insights only" | Too few categories or all same amount | Add variety of expenses with different categories |
| Random/demo data showing | Rare edge case | Clear browser cache, try fresh upload |

---

## 🎯 STEP-BY-STEP: Export from Your Bank/App

### **HDFC Bank:**
1. Go to Statements → Download
2. Select CSV format
3. Columns: Date | Narration (Description) | Debit | Credit
4. Keep as-is, upload directly ✓

### **ICICI Bank:**
1. Export Statements → CSV
2. Date | Transaction Ref. | Description | Amount | Balance
3. Remove Balance column, keep Date | Description | Amount ✓

### **Google Pay / PhonePe:**
1. Settings → Export History
2. Should have: Date | Merchant | Amount | Category
3. Upload directly ✓

### **GPay:**
1. View Transactions → Export
2. CSV export includes all needed columns
3. Upload directly ✓

### **Paytm:**
1. Statements → Download CSV
2. Has: Date | Description | Debit | Credit | Balance
3. Remove Balance column if present ✓

---

## ✅ BEFORE YOU UPLOAD - CHECKLIST

- [ ] File is `.csv` format (NOT Excel .xlsx without conversion)
- [ ] Date column exists with valid dates (YYYY-MM-DD preferred)
- [ ] Amount column exists with numbers only (no ₹ symbols)
- [ ] At least 1 transaction with date + amount
- [ ] At least 2 different transactions (more = better insights)
- [ ] File size < 10MB
- [ ] No blank rows at top of file
- [ ] Column headers are in first row

---

## 📊 WHAT YOU'LL SEE AFTER UPLOAD

✅ If CSV is correct:
- Total expenses calculated correctly
- Pie chart with all categories
- Monthly spending trend
- Daily spending pattern
- Transaction table populated
- AI insights generated

❌ If CSV has issues:
- Partial data shown
- Empty charts
- Generic insights only
- Error message with explanation

---

## 🚀 READY TO UPLOAD?

1. Prepare CSV following format above
2. Go to dashboard: http://localhost:5000
3. Click "Upload CSV" or drag-drop file
4. See your data analyzed in real-time! 🎉
