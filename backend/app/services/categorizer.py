import re

# Keyword rules: each category maps to a list of keywords/patterns.
# Matching is case-insensitive against the transaction description.
CATEGORY_RULES: dict[str, list[str]] = {
    "Food": [
        "restaurant", "cafe", "coffee", "starbucks", "mcdonalds", "mcdonald",
        "burger", "pizza", "sushi", "taco", "chipotle", "subway", "wendy",
        "dunkin", "domino", "kfc", "popeye", "chick-fil-a", "panera",
        "grubhub", "doordash", "ubereats", "uber eats", "deliveroo",
        "whole foods", "trader joe", "grocery", "groceries", "supermarket",
        "food", "dining", "bakery", "deli", "butcher", "farmers market",
        "instacart", "fresh direct", "aldi", "lidl", "kroger", "safeway",
        "publix", "costco", "walmart grocery", "sam's club", "bj's",
        "swiggy", "zomato", "meal", "eat", "kitchen", "grill", "bistro",
        "diner", "brunch", "lunch", "breakfast", "snack",
    ],
    "Transport": [
        "uber", "lyft", "taxi", "cab", "grab", "ola", "bolt",
        "gas station", "shell", "bp", "exxon", "mobil", "chevron", "petrol",
        "fuel", "diesel", "gasoline", "parking", "toll", "ez pass", "fastag",
        "metro", "subway", "bus", "train", "railway", "transit", "transport",
        "airline", "flight", "airways", "air ticket",
        "car wash", "auto repair", "mechanic", "tire", "tyre",
        "rapido", "careem",
    ],
    "Shopping": [
        "amazon", "ebay", "walmart", "target", "best buy", "bestbuy",
        "apple store", "microsoft store", "flipkart", "myntra", "ajio",
        "zara", "h&m", "uniqlo", "nike", "adidas", "puma",
        "shopping", "mall", "store", "retail", "online order", "order",
        "etsy", "aliexpress", "shein", "asos", "nordstrom", "macys", "macy's",
        "ikea", "home depot", "lowe's", "lowes", "wayfair", "furniture",
        "clothing", "apparel", "shoes", "fashion", "accessori",
    ],
    "Bills": [
        "electric", "electricity", "power", "utility", "utilities",
        "water bill", "gas bill", "sewage", "trash", "waste",
        "internet", "broadband", "wifi", "wi-fi", "comcast", "spectrum",
        "at&t", "verizon", "t-mobile", "tmobile", "vodafone", "airtel", "jio",
        "phone bill", "mobile bill", "cell bill", "telephone",
        "rent", "mortgage", "lease", "hoa", "maintenance",
        "insurance", "premium", "policy",
        "tax", "taxes", "property tax", "income tax",
    ],
    "Entertainment": [
        "netflix", "hulu", "disney", "hbo", "prime video", "peacock",
        "spotify", "apple music", "youtube", "twitch", "audible",
        "movie", "cinema", "theater", "theatre", "concert", "show",
        "game", "gaming", "steam", "playstation", "xbox", "nintendo",
        "park", "museum", "zoo", "aquarium", "amusement",
        "ticket", "event", "festival", "subscription",
        "hotstar", "sonyliv", "zee5",
    ],
    "Health": [
        "hospital", "clinic", "doctor", "physician", "dentist", "dental",
        "pharmacy", "drug store", "cvs", "walgreens", "rite aid",
        "medical", "health", "healthcare", "lab", "diagnostic",
        "therapy", "therapist", "counseling", "psycholog",
        "gym", "fitness", "yoga", "pilates", "crossfit", "workout",
        "vitamin", "supplement", "wellness", "optician", "optical", "eye care",
        "apollo", "medplus", "pharmeasy", "netmeds",
    ],
    "Education": [
        "tuition", "school", "university", "college", "academy",
        "course", "class", "training", "workshop", "seminar", "webinar",
        "book", "textbook", "udemy", "coursera", "skillshare", "masterclass",
        "linkedin learning", "pluralsight", "edx",
        "library", "stationery", "supplies",
        "byju", "unacademy", "vedantu",
    ],
    "Travel": [
        "hotel", "motel", "resort", "airbnb", "vrbo", "booking.com",
        "marriott", "hilton", "hyatt", "ihg", "accor", "oyo",
        "travel", "trip", "vacation", "holiday", "tourism",
        "luggage", "baggage", "visa fee", "passport",
        "makemytrip", "goibibo", "cleartrip", "yatra",
        "expedia", "kayak", "trivago", "agoda",
    ],
    "Income": [
        "salary", "payroll", "wages", "bonus", "commission",
        "deposit", "credit", "refund", "reimbursement", "cashback",
        "dividend", "interest earned", "interest credit",
        "freelance", "payment received", "transfer in",
        "venmo", "zelle", "paypal received",
    ],
}

# Pre-compile patterns for performance
_COMPILED_RULES: list[tuple[str, re.Pattern]] = []
for _cat, _keywords in CATEGORY_RULES.items():
    # Build a single regex alternation per category
    pattern = re.compile("|".join(re.escape(kw) for kw in _keywords), re.IGNORECASE)
    _COMPILED_RULES.append((_cat, pattern))


def categorize_transactions(descriptions: list[str], categories: list[str]) -> list[str]:
    """Categorize transaction descriptions using keyword matching rules.

    Args:
        descriptions: List of transaction descriptions to categorize.
        categories: List of valid category names.

    Returns:
        List of category names, one per description (same order).
    """
    valid_categories = set(categories)
    return [_categorize_one(desc, valid_categories) for desc in descriptions]


def _categorize_one(description: str, valid_categories: set[str]) -> str:
    """Categorize a single transaction description."""
    for category, pattern in _COMPILED_RULES:
        if category in valid_categories and pattern.search(description):
            return category
    return "Other"
