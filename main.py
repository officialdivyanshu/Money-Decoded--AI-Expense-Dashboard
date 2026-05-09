from categorizer import categorize
from parser import parse_sms
from database import create_table, insert_transaction, fetch_all_transactions, clear_all_transactions
from datetime import datetime
from insights import get_total_spending, get_category_spending, get_top_category

def process_sms(sms):
    data = parse_sms(sms)

    data["category"] = categorize(data["merchant"])
    data["date"] = datetime.now().strftime("%Y-%m-%d")
    data["source"] = "sms"

    insert_transaction(
        amount=data["amount"],
        type_=data["type"],
        merchant=data["merchant"],
        category=data["category"],
        date=data["date"],
        source=data["source"]
    )

    print("SMS processed and stored:", data)


# 🔥 MAIN BLOCK (indent properly)
if __name__ == "__main__":
    create_table()
    clear_all_transactions()  # Start with zero data each time

    # Uncomment below to test with sample data:
    # sms = "Rs.450 spent on Zomato"
    # process_sms(sms)
    # print(fetch_all_transactions())
    # print("\n--- INSIGHTS ---")
    # print("Total Spending:", get_total_spending())
    # print("Category Breakdown:", get_category_spending())
    # print("Top Category:", get_top_category())
