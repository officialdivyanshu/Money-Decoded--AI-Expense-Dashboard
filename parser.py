import re


def parse_sms(sms):
    # Extract amount
    amount_match = re.search(r"(?:Rs\.?|INR|₹)\s?(\d+)", sms)
    amount = int(amount_match.group(1)) if amount_match else None

    # Detect type
    if "debited" in sms.lower() or "spent" in sms.lower():
        txn_type = "debit"
    elif "credited" in sms.lower() or "received" in sms.lower():
        txn_type = "credit"
    else:
        txn_type = "unknown"

    # Extract merchant
    merchant_match = re.search(r"(?:to|at|on)\s([A-Za-z0-9& ]+)", sms)
    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown"

    return {
        "amount": amount,
        "type": txn_type,
        "merchant": merchant
    }

if __name__ == "__main__":
    sms = "Rs.450 spent on Zomato"

    result = parse_sms(sms)
    print(result)