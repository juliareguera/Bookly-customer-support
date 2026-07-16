CUSTOMERS = {
    "C001": {"name": "Alice Johnson", "email": "alice@example.com", "phone": "555-0101"},
    "C002": {"name": "Bob Smith", "email": "bob@example.com", "phone": "555-0102"},
    "C003": {"name": "Carol Davis", "email": "carol@example.com", "phone": "555-0103"},
}

ORDERS = {
    "ORD-1001": {
        "customer_id": "C001",
        "items": [
            {"title": "The Midnight Library", "author": "Matt Haig", "format": "Hardcover", "qty": 1, "price": 24.99},
            {"title": "Atomic Habits", "author": "James Clear", "format": "Paperback", "qty": 1, "price": 16.99},
        ],
        "total": 41.98,
        "status": "delivered",
        "placed_date": "2025-06-10",
        "delivered_date": "2025-06-14",
        "tracking": "BKL202506101001",
    },
    "ORD-1002": {
        "customer_id": "C001",
        "items": [
            {"title": "Fourth Wing", "author": "Rebecca Yarros", "format": "Hardcover", "qty": 1, "price": 28.99},
        ],
        "total": 28.99,
        "status": "in_transit",
        "placed_date": "2025-07-12",
        "estimated_delivery": "2025-07-18",
        "tracking": "BKL202507121002",
    },
    "ORD-1003": {
        "customer_id": "C002",
        "items": [
            {"title": "The Women", "author": "Kristin Hannah", "format": "Paperback", "qty": 1, "price": 18.99},
            {"title": "James", "author": "Percival Everett", "format": "Hardcover", "qty": 1, "price": 26.99},
        ],
        "total": 45.98,
        "status": "processing",
        "placed_date": "2025-07-14",
    },
    "ORD-1004": {
        "customer_id": "C003",
        "items": [
            {"title": "Intermezzo", "author": "Sally Rooney", "format": "Hardcover", "qty": 1, "price": 29.99},
        ],
        "total": 29.99,
        "status": "delivered",
        "placed_date": "2025-06-01",
        "delivered_date": "2025-06-05",
        "tracking": "BKL202506011004",
    },
    "ORD-1005": {
        "customer_id": "C002",
        "items": [
            {"title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "format": "Paperback", "qty": 2, "price": 14.99},
            {"title": "A Little Life", "author": "Hanya Yanagihara", "format": "Paperback", "qty": 1, "price": 17.99},
        ],
        "total": 47.97,
        "status": "delivered",
        "placed_date": "2025-05-20",
        "delivered_date": "2025-05-25",
        "tracking": "BKL202505201005",
    },
}

RETURNS = {}

POLICIES = {
    "returns": (
        "BOOKLY RETURN POLICY:\n"
        "- Physical books may be returned within 30 days of delivery.\n"
        "- Books must be unread, unmarked, and in original condition.\n"
        "- eBooks and audiobooks are non-refundable once accessed.\n"
        "- Free return shipping for orders that were damaged or incorrectly fulfilled by Bookly.\n"
        "- Customer pays return shipping for change-of-mind returns.\n"
        "- Refunds are processed within 5-7 business days after we receive the return."
    ),
    "shipping": (
        "BOOKLY SHIPPING POLICY:\n"
        "- Standard Shipping (5-7 business days): Free on orders $35+, otherwise $3.99.\n"
        "- Express Shipping (2-3 business days): $8.99.\n"
        "- Overnight Shipping (1 business day): $18.99.\n"
        "- International Shipping (10-21 business days): Starting at $14.99.\n"
        "- Orders placed before 1 PM EST ship the same business day.\n"
        "- A tracking number is emailed as soon as your order ships.\n"
        "- Bookly+ members receive free standard shipping on every order."
    ),
    "membership": (
        "BOOKLY+ MEMBERSHIP:\n"
        "- $9.99/month or $89.99/year.\n"
        "- Benefits: 10% off all orders, free standard shipping on every order,\n"
        "  early access to new releases, and a $5 monthly reading credit.\n"
        "- Cancel anytime with no fees.\n"
        "- Manage your membership at bookly.com/account/membership."
    ),
    "payment": (
        "BOOKLY PAYMENT POLICY:\n"
        "- Accepted: Visa, Mastercard, American Express, PayPal, Apple Pay, Google Pay.\n"
        "- Payment is charged at the time of order placement.\n"
        "- Bookly Gift Cards available in $10, $25, $50, and $100 denominations.\n"
        "- Installment plans via Affirm for orders over $75.\n"
        "- Price matching within 14 days of purchase for the same edition at a major retailer."
    ),
    "privacy": (
        "BOOKLY PRIVACY POLICY SUMMARY:\n"
        "- We collect only what's needed to process your order and improve your experience.\n"
        "- We never sell your data or reading history to third parties.\n"
        "- Your reading history and wishlist are private by default.\n"
        "- You can download or delete your account data anytime from account settings.\n"
        "- Full policy at bookly.com/privacy."
    ),
}

PASSWORD_RESET_SENT: set[str] = set()
