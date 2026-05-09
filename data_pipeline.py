"""
ROBUST DATA PIPELINE FOR FINANCIAL TRANSACTIONS
================================================

Handles ANY reasonable CSV format with:
- Flexible column detection
- Smart date parsing
- Data cleaning & normalization
- Automatic date range detection
- Failsafe processing

Used by: ui_check.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Optional
import re


class DataPipelineException(Exception):
    """Custom exception for data pipeline errors."""
    pass


class TransactionDataPipeline:
    """
    Robust data pipeline for transaction CSVs.
    
    Handles flexible column names, multiple date formats,
    currency symbols, and data cleaning.
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.column_mapping = {}
        self.warnings = []
        self.stats = {
            'total_rows_read': 0,
            'rows_dropped': 0,
            'rows_valid': 0,
            'date_range': None,
            'amount_range': None,
            'categories_found': [],
        }
    
    # ===================================================================
    # PHASE 1: LOAD CSV
    # ===================================================================
    
    def load_csv(self, file) -> Tuple[pd.DataFrame, List[str]]:
        """
        Load CSV and perform initial validation.
        
        Args:
            file: Streamlit UploadedFile object
        
        Returns:
            Tuple[DataFrame, List of warnings]
        """
        try:
            # Read CSV
            df = pd.read_csv(file)
            self.raw_data = df.copy()
            self.stats['total_rows_read'] = len(df)
            
            # Normalize column names (strip whitespace, lowercase)
            df.columns = df.columns.str.strip()
            
            print(f"[OK] CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"  Columns: {df.columns.tolist()}")
            
            return df, self.warnings
        
        except Exception as e:
            raise DataPipelineException(f"Failed to load CSV: {str(e)}")
    
    # ===================================================================
    # PHASE 2: DETECT COLUMNS
    # ===================================================================
    
    def detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Auto-detect date, amount, category, and merchant columns.
        
        Searches for common column name patterns.
        
        Returns:
            Dict with keys: 'date', 'amount', 'category', 'merchant'
        """
        mapping = {}
        columns_lower = {col: col for col in df.columns}  # Case-insensitive lookup
        
        # -------------------------------------------------------------
        # DETECT DATE COLUMN
        # -------------------------------------------------------------
        date_patterns = [
            'date', 'txn_date', 'transaction_date', 'posted_date',
            'time', 'timestamp', 'created_at', 'trans_date', 'trx_date'
        ]
        
        date_col = None
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in date_patterns):
                date_col = col
                break
        
        if date_col is None:
            raise DataPipelineException("❌ Could not find date column. Try renaming to 'date' or 'Date'")
        
        mapping['date'] = date_col
        print(f"[OK] Detected date column: '{date_col}'")
        
        # -------------------------------------------------------------
        # DETECT AMOUNT COLUMN
        # -------------------------------------------------------------
        amount_patterns = [
            'amount', 'amt', 'value', 'sum', 'total', 'debit', 'credit',
            'transaction_amount', 'txn_amount', 'quantity_or_amount'
        ]
        
        amount_col = None
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in amount_patterns):
                amount_col = col
                break
        
        if amount_col is None:
            raise DataPipelineException("❌ Could not find amount column. Try renaming to 'amount' or 'Amount'")
        
        mapping['amount'] = amount_col
        print(f"[OK] Detected amount column: '{amount_col}'")
        
        # -------------------------------------------------------------
        # DETECT CATEGORY COLUMN (OPTIONAL)
        # -------------------------------------------------------------
        category_patterns = [
            'category', 'cat', 'type', 'transaction_type', 'txn_type',
            'classification', 'class'
        ]
        
        category_col = None
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in category_patterns):
                category_col = col
                break
        
        if category_col:
            mapping['category'] = category_col
            print(f"[OK] Detected category column: '{category_col}'")
        else:
            mapping['category'] = None
            print(f"[INFO] No category column found (optional)")
        
        # -------------------------------------------------------------
        # DETECT MERCHANT/DESCRIPTION COLUMN (OPTIONAL)
        # -------------------------------------------------------------
        merchant_patterns = [
            'merchant', 'description', 'desc', 'narration', 'note',
            'narrative', 'reference', 'payee', 'vendor', 'store'
        ]
        
        merchant_col = None
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in merchant_patterns):
                merchant_col = col
                break
        
        if merchant_col:
            mapping['merchant'] = merchant_col
            print(f"[OK] Detected merchant column: '{merchant_col}'")
        else:
            mapping['merchant'] = None
            print(f"[INFO] No merchant column found (optional)")
        
        self.column_mapping = mapping
        return mapping
    
    # ===================================================================
    # PHASE 3: SMART DATE PARSING
    # ===================================================================
    
    def parse_dates(self, df: pd.DataFrame, date_col: str) -> pd.Series:
        """
        Intelligently parse dates using multiple format attempts.
        
        Strategy:
        1. Try 10 explicit formats
        2. Fallback: dayfirst=True inference
        3. Drop unparseable rows
        
        Returns:
            Parsed date series (NaT for failures, to be dropped later)
        """
        date_formats = [
            "%Y-%m-%d",            # ISO: 2025-03-10
            "%d-%m-%Y",            # DD-MM-YYYY: 10-03-2025
            "%m-%d-%Y",            # MM-DD-YYYY: 03-10-2025
            "%d/%m/%Y",            # DD/MM/YYYY: 10/03/2025
            "%m/%d/%Y",            # MM/DD/YYYY: 03/10/2025
            "%Y/%m/%d",            # YYYY/MM/DD: 2025/03/10
            "%d.%m.%Y",            # DD.MM.YYYY: 10.03.2025
            "%d-%b-%Y",            # DD-Mon-YYYY: 10-Mar-2025
            "%Y-%m-%d %H:%M:%S",   # ISO with time
            "%d-%m-%Y %H:%M:%S",   # DD-MM-YYYY with time
        ]
        
        # Try each format
        for fmt in date_formats:
            try:
                parsed = pd.to_datetime(df[date_col], format=fmt, errors="raise")
                print(f"[OK] Date format detected: {fmt}")
                return parsed
            except (ValueError, TypeError):
                continue
        
        # Fallback: Intelligent inference
        print(f"[INFO] Using fallback date parsing (dayfirst=True)")
        parsed = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        
        # Count unparseable
        nat_count = parsed.isna().sum()
        if nat_count > 0:
            warning = f"[WARNING] {nat_count} rows have unparseable dates (will be dropped)"
            self.warnings.append(warning)
            print(f"{warning}")
        
        return parsed
    
    # ===================================================================
    # PHASE 4: CLEAN AMOUNTS (CURRENCY SYMBOLS, NEGATIVES, etc.)
    # ===================================================================
    
    def clean_amounts(self, df: pd.DataFrame, amount_col: str) -> pd.Series:
        """
        Clean amount column:
        - Remove currency symbols (₹, $, £, €, etc.)
        - Handle parentheses as negative (accounting format)
        - Convert to numeric
        
        Returns:
            Cleaned numeric series
        """
        amounts = df[amount_col].astype(str).copy()
        
        # Remove common currency symbols
        amounts = amounts.str.replace(r'[₹$£€¥]', '', regex=True)
        amounts = amounts.str.replace(r'[,]', '', regex=True)  # Remove commas
        amounts = amounts.str.strip()
        
        # Handle parentheses as negative (accounting format)
        # E.g., "(100)" → -100
        def handle_parentheses(val):
            if isinstance(val, str) and val.startswith('(') and val.endswith(')'):
                return '-' + val[1:-1]
            return val
        
        amounts = amounts.apply(handle_parentheses)
        
        # Convert to numeric
        amounts = pd.to_numeric(amounts, errors="coerce")
        
        # Count non-convertible
        nan_count = amounts.isna().sum()
        if nan_count > 0:
            warning = f"[WARNING] {nan_count} rows have invalid amounts (will be dropped)"
            self.warnings.append(warning)
            print(f"{warning}")
        
        return amounts
    
    # ===================================================================
    # PHASE 5: MAIN CLEANING PIPELINE
    # ===================================================================
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute full data cleaning pipeline.
        
        Steps:
        1. Detect columns
        2. Parse dates
        3. Clean amounts
        4. Normalize category/merchant
        5. Drop null rows
        6. Validate data
        
        Returns:
            Cleaned DataFrame with standard column names
        """
        print("\n" + "="*60)
        print("STARTING DATA CLEANING PIPELINE")
        print("="*60)
        
        try:
            # Step 1: Detect columns
            mapping = self.detect_columns(df)
            
            # Step 2: Parse dates
            df['Date'] = self.parse_dates(df, mapping['date'])
            
            # Step 3: Clean amounts
            df['Amount'] = self.clean_amounts(df, mapping['amount'])
            
            # Step 4: Category and Merchant
            if mapping['category']:
                df['Category'] = df[mapping['category']].fillna('Other').astype(str)
            else:
                df['Category'] = 'Other'
            
            if mapping['merchant']:
                df['Description'] = df[mapping['merchant']].fillna('Unknown').astype(str)
            else:
                df['Description'] = 'Unknown'
            
            # Step 5: Select relevant columns
            df = df[['Date', 'Amount', 'Category', 'Description']].copy()
            
            # Step 6: Drop rows with null date or amount
            rows_before = len(df)
            df = df.dropna(subset=['Date', 'Amount'])
            rows_dropped = rows_before - len(df)
            
            if rows_dropped > 0:
                warning = f"[WARNING] {rows_dropped} rows dropped due to invalid data"
                self.warnings.append(warning)
                print(f"{warning}")
            
            # Step 7: Remove duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                df = df.drop_duplicates()
                warning = f"[INFO] {duplicates} duplicate rows removed"
                self.warnings.append(warning)
                print(f"{warning}")
            
            # Step 8: Validate
            if len(df) == 0:
                raise DataPipelineException("[ERROR] No valid rows after cleaning!")
            
            self.cleaned_data = df
            self.stats['rows_valid'] = len(df)
            self.stats['rows_dropped'] = rows_before - len(df)
            
            # Step 9: Calculate statistics
            self.stats['date_range'] = (df['Date'].min(), df['Date'].max())
            self.stats['amount_range'] = (df['Amount'].min(), df['Amount'].max())
            self.stats['categories_found'] = df['Category'].unique().tolist()
            
            print(f"\n[DONE] CLEANING COMPLETE")
            print(f"   Valid rows: {len(df)}")
            print(f"   Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
            print(f"   Amount range: {df['Amount'].min():.2f} to {df['Amount'].max():.2f}")
            print(f"   Categories: {len(df['Category'].unique())}")
            
            return df
        
        except DataPipelineException as e:
            print(f"\n[ERROR] {str(e)}")
            raise
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {str(e)}")
            raise DataPipelineException(f"Data cleaning failed: {str(e)}")
    
    # ===================================================================
    # PHASE 6: GET DATE RANGE FOR UI AUTO-SYNC
    # ===================================================================
    
    def get_date_range(self) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
        """
        Get min and max dates from cleaned data.
        
        Returns:
            Tuple[min_date, max_date] or (None, None) if no data
        """
        if self.cleaned_data is None or len(self.cleaned_data) == 0:
            return None, None
        
        return (
            self.cleaned_data['Date'].min(),
            self.cleaned_data['Date'].max()
        )
    
    # ===================================================================
    # PHASE 7: DEBUG INFORMATION
    # ===================================================================
    
    def get_debug_info(self) -> Dict:
        """
        Get comprehensive debug information.
        
        Returns:
            Dict with all pipeline stats and warnings
        """
        return {
            'column_mapping': self.column_mapping,
            'warnings': self.warnings,
            'stats': self.stats,
            'sample_data': self.cleaned_data.head(5) if self.cleaned_data is not None else None,
        }
    
    # ===================================================================
    # MAIN ENTRY POINT
    # ===================================================================
    
    def process(self, file) -> Tuple[pd.DataFrame, List[str], Dict]:
        """
        Complete pipeline: Load → Detect → Clean → Validate
        
        Args:
            file: Streamlit UploadedFile
        
        Returns:
            Tuple[cleaned_df, warnings, debug_info]
        """
        # Load
        df, _ = self.load_csv(file)
        
        # Clean
        cleaned_df = self.clean_data(df)
        
        # Get debug info
        debug_info = self.get_debug_info()
        
        return cleaned_df, self.warnings, debug_info


# ===========================================================================
# STANDALONE PROCESSING FUNCTION (for quick use)
# ===========================================================================

def process_transaction_csv(file) -> Tuple[pd.DataFrame, List[str], Dict]:
    """
    Standalone function to process transaction CSV.
    
    Usage:
        df, warnings, debug_info = process_transaction_csv(uploaded_file)
    
    Returns:
        Tuple[DataFrame, List[warnings], Dict[debug_info]]
    """
    pipeline = TransactionDataPipeline()
    return pipeline.process(file)
