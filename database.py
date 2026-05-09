import sqlite3
import pandas as pd


# 1️⃣ Connection
def create_connection():
    conn = sqlite3.connect("expenses.db")
    print("Connected to DB")
    return conn


# 2️⃣ Create Table
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        type TEXT,
        merchant TEXT,
        category TEXT,
        date TEXT,
        source TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Table created successfully")


# 2B️⃣ Clear all transactions (for fresh start)
def clear_all_transactions():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions;")
        conn.commit()
        print("All transactions cleared - starting fresh")
    except Exception as e:
        print(f"Error clearing transactions: {e}")
    finally:
        if conn:
            conn.close()


# 3️⃣ INSERT FUNCTION (THIS MUST EXIST BEFORE MAIN)
def insert_transaction(amount, type_, merchant, category, date, source):
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO transactions (amount, type, merchant, category, date, source)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (amount, type_, merchant, category, date, source))

        conn.commit()
        print("Transaction inserted successfully")
        return True
    except Exception as e:
        print(f"Error inserting transaction: {e}")
        return False
    finally:
        if conn:
            conn.close()


# 4 FETCH FUNCTION
def fetch_all_transactions():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []
    finally:
        if conn:
            conn.close()


# 5 COUNT TRANSACTIONS
def get_transaction_count():
    """Get count of transactions in database."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error counting transactions: {e}")
        return 0
    finally:
        if conn:
            conn.close()


# 6 GET DATE RANGE
def get_database_date_range():
    """Get min and max dates from database."""
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(date), MAX(date) FROM transactions WHERE date IS NOT NULL")
        row = cursor.fetchone()
        if row and row[0]:
            min_date = pd.to_datetime(row[0]).date()
            max_date = pd.to_datetime(row[1]).date()
            return min_date, max_date
        else:
            return None, None
    except Exception as e:
        print(f"Error getting date range: {e}")
        return None, None
    finally:
        if conn:
            conn.close()


# 5️⃣ MAIN (THIS COMES LAST ALWAYS)
if __name__ == "__main__":
    create_table()

    insert_transaction(
        amount=450,
        type_="debit",
        merchant="Zomato",
        category="Food",
        date="2026-04-10",
        source="manual"
    )

    data = fetch_all_transactions()
    print(data)