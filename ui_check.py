"""
Money-Decoded - Financial Behavior Analyzer
A premium fintech-grade Streamlit application.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Tuple
import random

# Backend imports
from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions, get_transaction_count, get_database_date_range
from insights import get_total_spending, get_category_spending, get_top_category
from parser import parse_sms
from categorizer import categorize
from llm import generate_insight
from data_pipeline import process_transaction_csv, TransactionDataPipeline


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Money Decoded",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Financial Behavior Analyzer | Built with Streamlit + SQLite"
    }
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "csv_processed_file" not in st.session_state:
    st.session_state.csv_processed_file = None
    st.session_state.csv_processing = False
    st.session_state.csv_date_min = None
    st.session_state.csv_date_max = None
    st.session_state.csv_row_count = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def process_uploaded_csv(file):
    """
    Process uploaded CSV using robust data pipeline.
    
    Returns:
        Tuple[cleaned_df, warnings, debug_info] or (None, [error], {}) on failure
    """
    try:
        cleaned_df, warnings, debug_info = process_transaction_csv(file)
        
        # Store in session state for auto-sync
        if len(cleaned_df) > 0:
            min_date = cleaned_df['Date'].min()
            max_date = cleaned_df['Date'].max()
            st.session_state.csv_date_min = min_date.date()
            st.session_state.csv_date_max = max_date.date()
            st.session_state.csv_row_count = len(cleaned_df)
            
            print(f"[OK] Stored in session_state: {len(cleaned_df)} rows")
        
        return cleaned_df, warnings, debug_info
    
    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return None, [error_msg], {}


def insert_cleaned_data_to_db(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Insert cleaned transactions into database.
    
    Returns:
        Tuple[success_count, error_count]
    """
    try:
        create_table()
        success_count = 0
        error_count = 0
        
        print(f"\n[INFO] Inserting {len(df)} cleaned transactions to database")
        
        for idx, row in df.iterrows():
            try:
                insert_transaction(
                    amount=float(row['Amount']),
                    type_='debit',
                    merchant=str(row['Description']),
                    category=str(row['Category']),
                    date=row['Date'].strftime('%Y-%m-%d'),
                    source='csv_upload'
                )
                success_count += 1
                
                # Log first few
                if idx < 3:
                    print(f"   [OK] Row {idx}: {row['Date'].date()} | {row['Amount']:.2f} | {row['Category']}")
            
            except Exception as e:
                error_count += 1
                print(f"   [ERROR] Row {idx}: {e}")
                continue
        
        if error_count > 0:
            print(f"   [WARNING] {error_count} rows failed to insert")
        
        if success_count > 0:
            print(f"[DONE] Successfully inserted {success_count} transactions")
            st.cache_data.clear()
            print(f"   Cache cleared")
        
        return success_count, error_count
    
    except Exception as e:
        print(f"[ERROR] Database insertion failed: {e}")
        return 0, len(df)


def render_sidebar():
    """Render sidebar with date range selector and clear data button."""
    with st.sidebar:
        st.header("Date Range Filter")
        
        # Get database date range
        db_min, db_max = get_database_date_range()
        
        # Check for mismatch
        csv_has_data = st.session_state.csv_date_min is not None
        has_mismatch = csv_has_data and (
            (st.session_state.csv_date_min < db_min if db_min else False) or
            (st.session_state.csv_date_max > db_max if db_max else False)
        )
        
        # Show mismatch warning
        if has_mismatch:
            st.warning("Date range mismatch detected!")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**CSV Range:**")
                st.write(f"{st.session_state.csv_date_min}")
                st.write(f"{st.session_state.csv_date_max}")
            with col2:
                st.write("**DB Range:**")
                st.write(f"{db_min}")
                st.write(f"{db_max}")
            
            if st.button("Use Database Range"):
                st.session_state.csv_date_min = db_min
                st.session_state.csv_date_max = db_max
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            date_from = st.date_input(
                "From Date",
                value=st.session_state.csv_date_min or db_min or datetime.now().date() - timedelta(days=90),
                key="date_from"
            )
        with col2:
            date_to = st.date_input(
                "To Date",
                value=st.session_state.csv_date_max or db_max or datetime.now().date(),
                key="date_to"
            )
        
        st.divider()
        st.header("Data Management")
        if st.button("Clear All Data", use_container_width=True):
            clear_all_transactions()
            st.success("Database cleared!")
            st.rerun()
        
        return date_from, date_to


def main():
    """Main Streamlit application."""
    
    # ============================================================
    # STAGE 1: DATABASE INITIALIZATION
    # ============================================================
    create_table()
    
    # ============================================================
    # HEADER
    # ============================================================
    st.title("Money Decoded")
    st.subheader("Your Personal Financial Behavior Analyzer")
    
    # ============================================================
    # SIDEBAR
    # ============================================================
    date_from, date_to = render_sidebar()
    
    # ============================================================
    # STAGE 2: FILE UPLOAD
    # ============================================================
    st.header("Data Upload")
    file = st.file_uploader("Upload Transaction CSV", type=["csv"])
    
    # ============================================================
    # STAGE 3: CSV FILE UPLOAD PROCESSING (PIPELINE-BASED)
    # ============================================================
    if file is not None:
        file_id = file.name + str(file.size)
        
        if st.session_state.csv_processed_file != file_id:
            st.session_state.csv_processing = True
            
            try:
                # --------------------------------------------------
                # PROCESS CSV WITH ROBUST PIPELINE
                # --------------------------------------------------
                with st.spinner("[WAIT] Processing CSV with validation..."):
                    cleaned_df, warnings, debug_info = process_uploaded_csv(file)
                
                if cleaned_df is None or len(cleaned_df) == 0:
                    st.error("[ERROR] Failed to process CSV")
                    if warnings:
                        for warning in warnings:
                            st.error(f"  * {warning}")
                    st.session_state.csv_processing = False
                else:
                    # --------------------------------------------------
                    # SHOW PROCESSING SUMMARY
                    # --------------------------------------------------
                    st.success(f"[DONE] Processed {len(cleaned_df)} valid transactions")
                    
                    if warnings:
                        with st.expander("[WARNING] Processing Warnings", expanded=False):
                            for warning in warnings:
                                st.warning(warning)
                    
                    # --------------------------------------------------
                    # SHOW DATA QUALITY INFORMATION
                    # --------------------------------------------------
                    with st.expander("[DATA] Data Quality Report", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Valid Rows", len(cleaned_df))
                            st.metric("Dropped Rows", debug_info['stats'].get('rows_dropped', 0))
                        with col2:
                            date_min, date_max = debug_info['stats'].get('date_range', (None, None))
                            if date_min and date_max:
                                st.metric("Date Range", f"{date_min.date()} to {date_max.date()}")
                            amount_min, amount_max = debug_info['stats'].get('amount_range', (None, None))
                            if amount_min and amount_max:
                                st.metric("Amount Range", f"{amount_min:.2f} to {amount_max:.2f}")
                        
                        st.markdown("**Detected Columns:**")
                        for key, val in debug_info['column_mapping'].items():
                            st.write(f"* {key}: `{val}`")
                        
                        st.markdown("**Sample Data (first 3 rows):**")
                        st.dataframe(debug_info['sample_data'], use_container_width=True)
                    
                    # --------------------------------------------------
                    # INSERT TO DATABASE
                    # --------------------------------------------------
                    with st.spinner(f"[DB] Inserting {len(cleaned_df)} transactions to database..."):
                        success_count, error_count = insert_cleaned_data_to_db(cleaned_df)
                    
                    if success_count > 0:
                        st.session_state.csv_processed_file = file_id
                        st.session_state.csv_processing = False
                        st.cache_data.clear()
                        st.success(f"[DONE] {success_count} transactions inserted to database!")
                        st.info("[INFO] Date range auto-synced. Refresh to see insights.")
                    else:
                        st.session_state.csv_processing = False
                        st.error("[ERROR] Failed to insert transactions to database.")
            
            except Exception as e:
                st.session_state.csv_processing = False
                st.error(f"[ERROR] {str(e)}")
                print(f"Exception: {e}")
                import traceback
                st.error(traceback.format_exc())
    
    # ============================================================
    # STAGE 4: CHECK DATA AVAILABILITY
    # ============================================================
    if st.session_state.csv_processing:
        st.warning("[WAIT] Processing file... please wait")
        return
    
    transaction_count = get_transaction_count()
    
    if transaction_count == 0:
        st.info("[INFO] No transactions yet. Upload a CSV to get started.")
        return
    
    # ============================================================
    # STAGE 5: FETCH & FILTER DATA
    # ============================================================
    all_transactions = fetch_all_transactions()
    df_all = pd.DataFrame(all_transactions, columns=["ID", "Amount", "Type", "Merchant", "Category", "Date", "Source"])
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    
    # Apply date filter
    df_filtered = df_all[(df_all["Date"].dt.date >= date_from) & (df_all["Date"].dt.date <= date_to)]
    
    if len(df_filtered) == 0:
        st.warning(f"[WARNING] No transactions found for {date_from} to {date_to}")
        st.info("Try adjusting your date range or uploading more data.")
        return
    
    st.success(f"[DONE] Found {len(df_filtered)} transactions")
    
    # ============================================================
    # STAGE 6: DISPLAY ANALYTICS
    # ============================================================
    st.header("Financial Analytics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total = df_filtered["Amount"].sum()
        st.metric("Total Spending", f"{total:.2f}")
    with col2:
        avg_per_tx = df_filtered["Amount"].mean()
        st.metric("Average per Transaction", f"{avg_per_tx:.2f}")
    with col3:
        tx_count = len(df_filtered)
        st.metric("Transaction Count", tx_count)
    
    # Category breakdown
    st.subheader("Category Breakdown")
    category_spending = df_filtered.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_category = px.bar(
            x=category_spending.index,
            y=category_spending.values,
            title="Spending by Category",
            labels={"x": "Category", "y": "Amount"},
            color=category_spending.values,
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.write("**Top Categories:**")
        for idx, (cat, amt) in enumerate(category_spending.head(5).items(), 1):
            st.write(f"{idx}. {cat}: {amt:.2f}")
    
    # Time series
    st.subheader("Spending Trend")
    daily_spending = df_filtered.groupby(df_filtered["Date"].dt.date)["Amount"].sum()
    fig_trend = px.line(
        x=daily_spending.index,
        y=daily_spending.values,
        title="Daily Spending Trend",
        labels={"x": "Date", "y": "Amount"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Raw data table
    st.subheader("Transaction Details")
    st.dataframe(
        df_filtered[["Date", "Merchant", "Amount", "Category", "Source"]].sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    main()
