def categorize(merchant):
    merchant = merchant.lower()

    categories = {
        "Food & Dining": ["zomato", "swiggy", "dominos", "pizza", "restaurant", "cafe", "coffee"],
        "Transport": ["uber", "ola", "rapido", "taxi", "auto", "bus"],
        "Shopping": ["amazon", "flipkart", "myntra", "mall", "store", "shop"],
        "Entertainment": ["netflix", "spotify", "hotstar", "movie", "cinema", "games"],
        "Utilities": ["electricity", "water", "gas", "internet", "mobile"],
        "Health": ["pharmacy", "hospital", "clinic", "doctor", "medical"],
        "Subscriptions": ["subscription", "premium", "membership"],
        "Travel": ["flight", "hotel", "airbnb", "booking", "train"]
    }

    for category, keywords in categories.items():
        for word in keywords:
            if word in merchant:
                return category

    return "Others"  # Return Others for uncategorized