from database import create_connection


def get_total_spending():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='debit'")
        total = cursor.fetchone()[0]
        return total if total else 0
    except Exception as e:
        print(f"Error getting total spending: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_category_spending():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE type='debit'
        GROUP BY category
        """)

        results = cursor.fetchall()
        return results if results else []
    except Exception as e:
        print(f"Error getting category spending: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_top_category():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE type='debit'
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
        """)

        result = cursor.fetchone()
        return result if result else None
    except Exception as e:
        print(f"Error getting top category: {e}")
        return None
    finally:
        if conn:
            conn.close()