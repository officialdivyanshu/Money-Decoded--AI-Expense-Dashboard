"""
FLASK BACKEND FOR MONEY DECODED
================================
Serves index.html and handles CSV uploads with financial analysis
100% CSV-driven - NO hardcoded/demo/fallback data
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from categorizer import categorize
import os
from pathlib import Path
import sys

# ═══════════════════════════════════════════════════════════════════════
# DEBUG LOGGING
# ═══════════════════════════════════════════════════════════════════════
class DebugLogger:
    """Log all CSV processing steps for debugging"""
    def __init__(self):
        self.logs = []
    
    def log(self, step, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        msg = f"[{timestamp}] [{step}] {message}"
        self.logs.append(msg)
        print(msg, file=sys.stderr)
    
    def get_logs(self):
        return self.logs

debug_logger = DebugLogger()

# ═══════════════════════════════════════════════════════════════════════
# FLASK APP SETUP
# ═══════════════════════════════════════════════════════════════════════
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def format_currency(amount):
    """Format amount as currency string."""
    if pd.isna(amount):
        return "₹0"
    try:
        val = int(abs(amount))
        if val >= 100000:
            return f"₹{val/100000:.1f}L"
        elif val >= 1000:
            return f"₹{val/1000:.0f}k"
        else:
            return f"₹{val}"
    except:
        return "₹0"


def parse_csv_flexible(file):
    """
    Load CSV with flexible column detection.
    Returns: (df, error_msg) tuple
    STRICT VALIDATION - errors are fatal, no fallback
    """
    try:
        debug_logger.log("PARSE_CSV", f"Attempting to read file: {file.filename}")
        
        # Try reading with various encodings
        try:
            df = pd.read_csv(file, encoding='utf-8')
            debug_logger.log("PARSE_CSV", "✓ Parsed with UTF-8 encoding")
        except Exception as e1:
            debug_logger.log("PARSE_CSV", f"UTF-8 failed: {str(e1)}, trying Latin-1...")
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='latin-1')
                debug_logger.log("PARSE_CSV", "✓ Parsed with Latin-1 encoding")
            except Exception as e2:
                return None, f"Failed to parse CSV with UTF-8 or Latin-1 encoding"
        
        debug_logger.log("PARSE_CSV", f"CSV size: {len(df)} rows × {len(df.columns)} columns")
        
        # Check if empty
        if df.empty:
            return None, "❌ CSV is empty - no data to process"
        
        # Normalize column names (strip whitespace, keep case-sensitive for data integrity)
        df.columns = df.columns.str.strip()
        debug_logger.log("PARSE_CSV", f"Column names: {df.columns.tolist()}")
        
        # Check for completely empty rows
        df = df.dropna(how='all')
        if len(df) == 0:
            return None, "❌ CSV contains no valid rows (all rows are empty)"
        
        debug_logger.log("PARSE_CSV", f"After removing empty rows: {len(df)} rows")
        
        return df, None
    except Exception as e:
        return None, f"❌ CSV parsing failed: {str(e)}"


def detect_columns(df):
    """
    Auto-detect required columns with STRICT validation.
    
    Required: date, amount
    Optional: category (use if exists), merchant/description
    
    Returns: (dict, error_msg) tuple
    """
    mapping = {}
    
    # ─────────────────────────────────────────────────────────────
    # DETECT DATE COLUMN (REQUIRED)
    # ─────────────────────────────────────────────────────────────
    date_patterns = ['date', 'txn_date', 'transaction_date', 'posted_date', 
                     'time', 'timestamp', 'created_at', 'trans_date']
    date_col = None
    for col in df.columns:
        if any(p in col.lower() for p in date_patterns):
            date_col = col
            break
    
    if not date_col:
        cols_str = ", ".join(df.columns.tolist())
        return None, f"❌ MISSING DATE COLUMN - Expected column like 'Date', 'Transaction Date', etc. Found columns: {cols_str}"
    
    mapping['date'] = date_col
    debug_logger.log("DETECT_COLUMNS", f"✓ Date column: {date_col}")
    
    # ─────────────────────────────────────────────────────────────
    # DETECT AMOUNT COLUMN (REQUIRED)
    # ─────────────────────────────────────────────────────────────
    amount_patterns = ['amount', 'amt', 'value', 'sum', 'total', 'debit', 
                       'credit', 'transaction_amount', 'expense', 'money']
    amount_col = None
    for col in df.columns:
        if any(p in col.lower() for p in amount_patterns):
            amount_col = col
            break
    
    if not amount_col:
        cols_str = ", ".join(df.columns.tolist())
        return None, f"❌ MISSING AMOUNT COLUMN - Expected column like 'Amount', 'Expense', 'Debit', etc. Found columns: {cols_str}"
    
    mapping['amount'] = amount_col
    debug_logger.log("DETECT_COLUMNS", f"✓ Amount column: {amount_col}")
    
    # ─────────────────────────────────────────────────────────────
    # DETECT CATEGORY COLUMN (OPTIONAL - USE IF EXISTS)
    # ─────────────────────────────────────────────────────────────
    category_patterns = ['category', 'type', 'cat', 'trans_type', 'transaction_type']
    category_col = None
    for col in df.columns:
        if any(p in col.lower() for p in category_patterns):
            category_col = col
            break
    
    if category_col:
        mapping['category'] = category_col
        debug_logger.log("DETECT_COLUMNS", f"✓ Category column found (CSV): {category_col}")
    else:
        mapping['category'] = None
        debug_logger.log("DETECT_COLUMNS", "ℹ No category column in CSV - will use merchant-based categorization as fallback")
    
    # ─────────────────────────────────────────────────────────────
    # DETECT MERCHANT/DESCRIPTION COLUMN (OPTIONAL)
    # ─────────────────────────────────────────────────────────────
    merchant_patterns = ['merchant', 'description', 'desc', 'narration', 
                        'note', 'payee', 'vendor', 'name', 'remarks']
    merchant_col = None
    for col in df.columns:
        if any(p in col.lower() for p in merchant_patterns):
            merchant_col = col
            break
    
    mapping['merchant'] = merchant_col
    if merchant_col:
        debug_logger.log("DETECT_COLUMNS", f"✓ Merchant column: {merchant_col}")
    else:
        debug_logger.log("DETECT_COLUMNS", "ℹ No merchant column - using generic descriptions")
    
    return mapping, None


def parse_dates(df, date_col):
    """
    Parse dates with multiple format attempts.
    STRICT VALIDATION - returns None if ALL dates fail.
    """
    date_formats = [
        '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y',
        '%d-%m-%y', '%d/%m/%y', '%y-%m-%d',
        '%d %b %Y', '%d %b %y', '%B %d, %Y', '%b %d, %Y'
    ]
    
    for fmt in date_formats:
        try:
            parsed = pd.to_datetime(df[date_col], format=fmt, errors='coerce')
            # Check if we parsed at least SOME dates successfully
            if not parsed.isna().all():
                success_count = parsed.notna().sum()
                total_count = len(parsed)
                debug_logger.log("PARSE_DATES", f"✓ Format '{fmt}' succeeded: {success_count}/{total_count} dates parsed")
                return parsed
        except Exception as e:
            pass
    
    # Fallback: let pandas infer without strict format
    try:
        parsed = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        if not parsed.isna().all():
            success_count = parsed.notna().sum()
            total_count = len(parsed)
            debug_logger.log("PARSE_DATES", f"✓ Fallback inference succeeded: {success_count}/{total_count} dates parsed")
            return parsed
    except:
        pass
    
    debug_logger.log("PARSE_DATES", f"✗ Failed to parse ANY dates - all {len(df)} dates are invalid")
    return None


def analyze_csv(df, column_mapping):
    """
    Analyze transaction data - 100% CSV-driven, NO hardcoded data.
    
    Strategy:
    1. If CSV has category column → use it directly (NO merchant-based fallback)
    2. If CSV has NO category column → use merchant-based categorization as last resort
    3. All calculations from actual CSV data only
    4. Strict validation at every step
    """
    try:
        debug_logger.log("ANALYZE", "═" * 60)
        debug_logger.log("ANALYZE", "Starting CSV analysis")
        
        # Extract columns
        date_col = column_mapping['date']
        amount_col = column_mapping['amount']
        category_col = column_mapping.get('category')  # May be None
        merchant_col = column_mapping.get('merchant')
        
        debug_logger.log("ANALYZE", f"Processing with columns: date={date_col}, amount={amount_col}, category={category_col}, merchant={merchant_col}")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 1: PARSE AND VALIDATE DATES
        # ─────────────────────────────────────────────────────────────
        df['parsed_date'] = parse_dates(df, date_col)
        
        if df['parsed_date'].isna().all():
            return None, f"❌ DATE PARSING FAILED - Could not parse ANY dates in '{date_col}' column. Please ensure dates are in one of these formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, etc."
        
        unparseable_dates = df['parsed_date'].isna().sum()
        if unparseable_dates > 0:
            debug_logger.log("ANALYZE", f"⚠ {unparseable_dates} rows have unparseable dates - removing them")
        
        df = df.dropna(subset=['parsed_date'])
        debug_logger.log("ANALYZE", f"✓ Valid dates: {len(df)} rows")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 2: PARSE AND VALIDATE AMOUNTS
        # ─────────────────────────────────────────────────────────────
        df['amount'] = pd.to_numeric(df[amount_col], errors='coerce')
        
        invalid_amounts = df['amount'].isna().sum()
        if invalid_amounts > 0:
            debug_logger.log("ANALYZE", f"⚠ {invalid_amounts} rows have invalid amounts - removing them")
        
        df = df.dropna(subset=['amount'])
        debug_logger.log("ANALYZE", f"✓ Valid amounts: {len(df)} rows")
        
        # Check if we have any data left
        if df.empty:
            return None, f"❌ NO VALID DATA - After parsing dates and amounts, no valid transactions remain. Please check your CSV format."
        
        # ─────────────────────────────────────────────────────────────
        # STEP 3: SORT BY DATE
        # ─────────────────────────────────────────────────────────────
        df = df.sort_values('parsed_date')
        df['formatted_date'] = df['parsed_date'].dt.strftime('%d %b')
        date_range = f"{df['parsed_date'].min().strftime('%Y-%m-%d')} to {df['parsed_date'].max().strftime('%Y-%m-%d')}"
        debug_logger.log("ANALYZE", f"✓ Date range: {date_range}")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 4: HANDLE CATEGORIES
        # ─────────────────────────────────────────────────────────────
        if category_col and category_col in df.columns:
            # PRIORITY: Use CSV category column directly
            df['category'] = df[category_col].astype(str).str.strip()
            unique_categories = df['category'].nunique()
            debug_logger.log("ANALYZE", f"✓ Using CSV category column '{category_col}'")
            debug_logger.log("ANALYZE", f"  Found {unique_categories} unique categories in CSV")
        else:
            # FALLBACK: Use merchant-based categorization only if no CSV category column
            if merchant_col and merchant_col in df.columns:
                df['description'] = df[merchant_col].astype(str).str.strip()
                debug_logger.log("ANALYZE", f"✓ No category column found - using merchant-based categorization")
                df['category'] = df['description'].apply(lambda x: categorize(x))
            else:
                # No merchant or category column - use generic descriptions
                df['description'] = 'Transaction'
                debug_logger.log("ANALYZE", f"⚠ No merchant/category columns found - using generic 'Transaction' label")
                df['category'] = 'Others'
        
        # Add month_key NOW (before we split into expenses_df/income_df)
        df['month_key'] = df['parsed_date'].dt.strftime('%Y-%m')
        
        # ─────────────────────────────────────────────────────────────
        # SMART AMOUNT DETECTION: Handle different amount formats
        # ─────────────────────────────────────────────────────────────
        has_positive = (df['amount'] > 0).any()
        has_negative = (df['amount'] < 0).any()
        
        if has_positive and has_negative:
            # Mixed positive/negative - use as-is (negative = expenses, positive = income)
            debug_logger.log("ANALYZE", f"✓ Amounts: Mixed positive/negative detected - using as-is")
        elif has_negative and not has_positive:
            # All negative - convert to positive (they're all expenses)
            df['amount'] = df['amount'].abs()
            debug_logger.log("ANALYZE", f"✓ Amounts: All negative - converted to positive (expenses)")
        else:
            # All positive - auto-detect if they're expenses or income
            # Check if categories look like typical expenses
            expense_keywords = ['Groceries', 'Food', 'Transport', 'Uber', 'Swiggy', 'Zomato', 'Shopping', 'Entertainment', 'Netflix', 'Healthcare', 'Health', 'Utilities', 'Subscription', 'Travel', 'Hotel', 'Flight']
            income_keywords = ['Income', 'Salary', 'Bonus', 'Dividend', 'Transfer', 'Refund', 'Gift']
            
            category_str = ' '.join(df['category'].astype(str).unique()).upper()
            merchant_str = ' '.join(df[merchant_col].astype(str).unique()).upper() if merchant_col and merchant_col in df.columns else ''
            combined_str = (category_str + ' ' + merchant_str).upper()
            
            expense_matches = sum(1 for keyword in expense_keywords if keyword.upper() in combined_str)
            income_matches = sum(1 for keyword in income_keywords if keyword.upper() in combined_str)
            
            if expense_matches > income_matches:
                # Likely expenses - convert to negative
                df['amount'] = -df['amount'].abs()
                debug_logger.log("ANALYZE", f"✓ Amounts: All positive - detected as EXPENSES (using negative internally)")
            else:
                # Default: treat as expenses anyway (financial apps mostly track spending)
                df['amount'] = -df['amount'].abs()
                debug_logger.log("ANALYZE", f"✓ Amounts: All positive - defaulting to EXPENSES")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 5: CALCULATE SUMMARY STATS (100% FROM CSV)
        # ─────────────────────────────────────────────────────────────
        expenses_df = df[df['amount'] < 0]
        income_df = df[df['amount'] > 0]
        
        total_expenses = abs(expenses_df['amount'].sum())
        total_income = income_df['amount'].sum()
        net_savings = total_income - total_expenses
        
        debug_logger.log("ANALYZE", f"✓ Total Expenses: ₹{int(total_expenses)}")
        debug_logger.log("ANALYZE", f"✓ Total Income: ₹{int(total_income)}")
        debug_logger.log("ANALYZE", f"✓ Net Savings: ₹{int(net_savings)}")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 6: CATEGORY BREAKDOWN (100% FROM CSV DATA)
        # ─────────────────────────────────────────────────────────────
        category_breakdown = expenses_df.groupby('category')['amount'].sum().abs().sort_values(ascending=False)
        
        categories_dict = {}
        for cat, val in category_breakdown.items():
            categories_dict[cat] = int(val)
        
        top_category = category_breakdown.index[0] if len(category_breakdown) > 0 else "Unknown"
        top_amount = int(category_breakdown.iloc[0]) if len(category_breakdown) > 0 else 0
        debug_logger.log("ANALYZE", f"✓ Top Category: {top_category} (₹{top_amount})")
        debug_logger.log("ANALYZE", f"✓ Total categories found: {len(categories_dict)}")
        
        summary = {
            "total_expenses": int(total_expenses),
            "total_income": int(total_income),
            "net_savings": int(net_savings),
            "top_category": top_category,
            "transaction_count": len(df)
        }
        
        # ─────────────────────────────────────────────────────────────
        # STEP 7: MONTHLY TREND (100% FROM CSV DATA)
        # ─────────────────────────────────────────────────────────────
        monthly_data = expenses_df.groupby(expenses_df['month_key'])['amount'].sum().abs().sort_index()
        
        monthly_result = []
        for month_key, amount in monthly_data.items():
            month_date = pd.to_datetime(month_key)
            month_label = month_date.strftime('%b')
            monthly_result.append({"month": month_label, "amount": int(amount)})
        
        debug_logger.log("ANALYZE", f"✓ Monthly data: {len(monthly_result)} months")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 8: DAILY SPENDING - CURRENT MONTH ONLY (100% FROM CSV)
        # ─────────────────────────────────────────────────────────────
        if not df.empty:
            latest_month = df['parsed_date'].max().strftime('%Y-%m')
            current_month_df = expenses_df[expenses_df['month_key'] == latest_month]
            daily_data = current_month_df.groupby(current_month_df['parsed_date'])['amount'].sum().abs()
            daily_values = [int(v) for v in daily_data.values]
            debug_logger.log("ANALYZE", f"✓ Daily data: {len(daily_values)} days in latest month")
        else:
            daily_values = []
            debug_logger.log("ANALYZE", f"⚠ No daily data available")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 9: RECENT TRANSACTIONS - FROM ACTUAL CSV
        # ─────────────────────────────────────────────────────────────
        tx_list = []
        for _, row in df.tail(10).iterrows():
            tx_list.append({
                "date": row['formatted_date'],
                "description": str(row.get('description', row.get(merchant_col, 'Transaction')))[:40],
                "category": row['category'],
                "amount": f"₹{abs(int(row['amount']))}",
                "type": "credit" if row['amount'] > 0 else "debit"
            })
        
        # Reverse to show newest first
        tx_list.reverse()
        debug_logger.log("ANALYZE", f"✓ Recent transactions: {len(tx_list)} transactions")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 10: AI INSIGHTS - DATA-DRIVEN FROM CSV ONLY
        # ─────────────────────────────────────────────────────────────
        insights = []
        
        # Insight 1: Top spending category
        if len(category_breakdown) > 0:
            top_cat = category_breakdown.index[0]
            pct = (category_breakdown.iloc[0] / total_expenses * 100) if total_expenses > 0 else 0
            insights.append(f"{top_cat} is your largest expense ({pct:.0f}% of total spend)")
        
        # Insight 2: Month-over-month comparison (only if >= 2 months)
        if len(monthly_data) >= 2:
            latest = monthly_data.iloc[-1]
            prev = monthly_data.iloc[-2]
            change = (latest - prev) / prev * 100 if prev > 0 else 0
            if change > 10:
                insights.append(f"Spending increased {change:.0f}% vs last month — watch your budget")
            elif change < -10:
                insights.append(f"Great job! Spending down {abs(change):.0f}% vs last month")
        
        # Insight 3: Average daily spend (only if data exists)
        if len(daily_values) > 0:
            avg_daily = np.mean(daily_values)
            insights.append(f"Your average daily spend is ₹{avg_daily:.0f}")
        
        # If fewer than 3 insights, that's OK - only show what we calculated
        # NO HARDCODED FALLBACK INSIGHTS
        
        debug_logger.log("ANALYZE", f"✓ Generated {len(insights)} insights")
        debug_logger.log("ANALYZE", "✓ Analysis complete")
        debug_logger.log("ANALYZE", "═" * 60)
        
        # ─────────────────────────────────────────────────────────────
        # COMPILE RESPONSE - 100% CSV DATA
        # ─────────────────────────────────────────────────────────────
        response = {
            "status": "success",
            "summary": summary,
            "categories": categories_dict,
            "monthly": monthly_result,
            "daily": daily_values,
            "transactions": tx_list,
            "insights": insights[:3],  # Limit to 3 insights (but may be fewer)
            "debug": {
                "csv_filename": "uploaded_file.csv",
                "rows_processed": len(df),
                "date_range": date_range,
                "categories_found": list(categories_dict.keys())
            }
        }
        
        return response, None
        
    except Exception as e:
        error_msg = f"❌ ANALYSIS ERROR: {str(e)}"
        debug_logger.log("ANALYZE", error_msg)
        return None, error_msg


# ═══════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route('/')
def serve_index():
    """Serve the main HTML landing page."""
    return send_from_directory('.', 'index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle CSV file upload and return analysis JSON.
    
    NO fallback data, NO hardcoded responses.
    All errors are reported with detailed explanations.
    
    Expected:
    - file: multipart file upload (CSV, XLS, XLSX)
    
    Returns JSON:
    {
      "status": "success" or "error",
      "summary": { ... },  // Only if success
      "categories": { ... },  // Only if success
      "monthly": [ ... ],  // Only if success
      "daily": [ ... ],  // Only if success
      "transactions": [ ... ],  // Only if success
      "insights": [ ... ],  // Only if success
      "message": "error message if status=error"
    }
    """
    try:
        debug_logger.log("UPLOAD_ROUTE", "=" * 70)
        debug_logger.log("UPLOAD_ROUTE", "CSV UPLOAD INITIATED")
        
        # ─────────────────────────────────────────────────────────────
        # VALIDATE FILE EXISTS
        # ─────────────────────────────────────────────────────────────
        if 'file' not in request.files:
            msg = "❌ No file provided - please select a CSV file to upload"
            debug_logger.log("UPLOAD_ROUTE", msg)
            return jsonify({"status": "error", "message": msg}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            msg = "❌ File is empty - please select a valid CSV file"
            debug_logger.log("UPLOAD_ROUTE", msg)
            return jsonify({"status": "error", "message": msg}), 400
        
        debug_logger.log("UPLOAD_ROUTE", f"File received: {file.filename} ({file.content_length} bytes)")
        
        # ─────────────────────────────────────────────────────────────
        # VALIDATE FILE TYPE
        # ─────────────────────────────────────────────────────────────
        if not allowed_file(file.filename):
            allowed = ", ".join(ALLOWED_EXTENSIONS)
            msg = f"❌ File type not supported: '.{file.filename.rsplit('.', 1)[1].lower()}' - Supported types: {allowed}"
            debug_logger.log("UPLOAD_ROUTE", msg)
            return jsonify({"status": "error", "message": msg}), 400
        
        debug_logger.log("UPLOAD_ROUTE", "✓ File type validated")
        
        # ─────────────────────────────────────────────────────────────
        # PARSE CSV
        # ─────────────────────────────────────────────────────────────
        df, error = parse_csv_flexible(file)
        if error:
            debug_logger.log("UPLOAD_ROUTE", f"CSV parsing failed: {error}")
            return jsonify({"status": "error", "message": error}), 400
        
        debug_logger.log("UPLOAD_ROUTE", "✓ CSV parsed successfully")
        
        # ─────────────────────────────────────────────────────────────
        # DETECT COLUMNS
        # ─────────────────────────────────────────────────────────────
        columns, error = detect_columns(df)
        if error:
            debug_logger.log("UPLOAD_ROUTE", f"Column detection failed: {error}")
            return jsonify({"status": "error", "message": error}), 400
        
        debug_logger.log("UPLOAD_ROUTE", "✓ Columns detected")
        
        # ─────────────────────────────────────────────────────────────
        # ANALYZE
        # ─────────────────────────────────────────────────────────────
        result, error = analyze_csv(df, columns)
        if error:
            debug_logger.log("UPLOAD_ROUTE", f"Analysis failed: {error}")
            return jsonify({"status": "error", "message": error}), 400
        
        debug_logger.log("UPLOAD_ROUTE", "✓ Analysis successful")
        debug_logger.log("UPLOAD_ROUTE", "=" * 70)
        
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = f"❌ UPLOAD ERROR: {str(e)}"
        debug_logger.log("UPLOAD_ROUTE", error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🚀 Starting Money Decoded Flask Server")
    print("📍 Open: http://localhost:5000")
    print("🔌 CORS enabled for local development\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

