"""
Generates the raw user browsing/purchase history used by this project.
Run this FIRST, before recommender.py.
"""
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(3)

products = [
    ("P001", "Wireless Earbuds", "Electronics"),
    ("P002", "Smartphone", "Electronics"),
    ("P003", "Laptop Bag", "Electronics"),
    ("P004", "Bluetooth Speaker", "Electronics"),
    ("P005", "Smart Watch", "Electronics"),
    ("P006", "Running Shoes", "Sports"),
    ("P007", "Yoga Mat", "Sports"),
    ("P008", "Cricket Bat", "Sports"),
    ("P009", "Dumbbell Set", "Sports"),
    ("P010", "Cycling Helmet", "Sports"),
    ("P011", "Men's T-Shirt", "Fashion"),
    ("P012", "Women's Handbag", "Fashion"),
    ("P013", "Sneakers", "Fashion"),
    ("P014", "Denim Jacket", "Fashion"),
    ("P015", "Sunglasses", "Fashion"),
    ("P016", "Novel - Fiction", "Books"),
    ("P017", "Self-Help Book", "Books"),
    ("P018", "Cookbook", "Books"),
    ("P019", "Comic Book", "Books"),
    ("P020", "Biography", "Books"),
    ("P021", "Table Lamp", "Home"),
    ("P022", "Bedsheet Set", "Home"),
    ("P023", "Coffee Maker", "Home"),
    ("P024", "Wall Clock", "Home"),
    ("P025", "Storage Boxes", "Home"),
]

categories = list(set(p[2] for p in products))
users = [f"U{str(i).zfill(3)}" for i in range(1, 51)]

# Give each user 1-2 "preferred" categories so behavior has realistic patterns
user_preferences = {
    u: random.sample(categories, k=random.choice([1, 2])) for u in users
}

rows = []
start_date = datetime.now() - timedelta(days=60)

for user in users:
    preferred_cats = user_preferences[user]
    n_events = random.randint(8, 20)

    for _ in range(n_events):
        # 70% chance the user views something from their preferred category,
        # 30% chance they browse something random (realistic behavior)
        if random.random() < 0.7:
            cat = random.choice(preferred_cats)
            candidates = [p for p in products if p[2] == cat]
        else:
            candidates = products

        product_id, product_name, category = random.choice(candidates)
        view_count = random.randint(1, 5)
        purchased = "Yes" if random.random() < 0.2 else "No"
        event_date = start_date + timedelta(days=random.randint(0, 60))

        rows.append({
            "user_id": user,
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "view_count": view_count,
            "purchased": purchased,
            "event_date": event_date.strftime("%Y-%m-%d"),
        })

df = pd.DataFrame(rows)
df.to_excel("data/browsing_history_raw.xlsx", index=False)
print(f"Created data/browsing_history_raw.xlsx with {len(df)} rows")
print(f"Users: {df['user_id'].nunique()} | Products: {df['product_id'].nunique()}")
