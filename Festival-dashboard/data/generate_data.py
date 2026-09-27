"""
generate_data.py
Generates a synthetic daily sales dataset that mimics Indian e-commerce
marketplaces (Amazon.in / Flipkart style), covering two full years and
including the major festival/sale seasons that drive huge demand spikes:

    Republic Day Sale, Holi Sale, Summer Sale, Independence Day Sale,
    Big Billion Days / Great Indian Festival, Diwali Sale,
    Black Friday / Cyber Monday, Year-End Sale.

Output: data/sales_data.csv
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

PLATFORMS = ["Amazon", "Flipkart"]
CATEGORIES = {
    "Electronics": 1.35,
    "Mobiles": 1.6,
    "Fashion": 0.9,
    "Home & Kitchen": 0.8,
    "Beauty & Personal Care": 0.5,
    "Grocery": 0.35,
    "Books": 0.25,
    "Sports & Fitness": 0.55,
}

START = date(2023, 1, 1)
END = date(2024, 12, 31)

# (name, start, end, intensity multiplier, discount range)
FESTIVALS = [
    ("Republic Day Sale", date(2023, 1, 20), date(2023, 1, 26), 2.6, (20, 40)),
    ("Holi Sale", date(2023, 3, 4), date(2023, 3, 10), 1.8, (15, 35)),
    ("Summer Sale", date(2023, 5, 1), date(2023, 5, 8), 1.7, (15, 30)),
    ("Independence Day Sale", date(2023, 8, 9), date(2023, 8, 15), 2.4, (20, 45)),
    ("Big Billion Days / Great Indian Festival", date(2023, 10, 8), date(2023, 10, 15), 5.5, (35, 70)),
    ("Diwali Sale", date(2023, 11, 8), date(2023, 11, 14), 4.2, (30, 60)),
    ("Black Friday / Cyber Monday", date(2023, 11, 24), date(2023, 11, 27), 2.2, (25, 45)),
    ("Year End Sale", date(2023, 12, 25), date(2023, 12, 31), 2.0, (20, 40)),
    ("Republic Day Sale", date(2024, 1, 19), date(2024, 1, 25), 2.7, (20, 40)),
    ("Holi Sale", date(2024, 3, 22), date(2024, 3, 27), 1.8, (15, 35)),
    ("Summer Sale", date(2024, 5, 1), date(2024, 5, 8), 1.7, (15, 30)),
    ("Independence Day Sale", date(2024, 8, 9), date(2024, 8, 15), 2.5, (20, 45)),
    ("Big Billion Days / Great Indian Festival", date(2024, 10, 4), date(2024, 10, 12), 5.8, (35, 70)),
    ("Diwali Sale", date(2024, 10, 27), date(2024, 11, 2), 4.5, (30, 60)),
    ("Black Friday / Cyber Monday", date(2024, 11, 29), date(2024, 12, 2), 2.3, (25, 45)),
    ("Year End Sale", date(2024, 12, 25), date(2024, 12, 31), 2.1, (20, 40)),
]


def festival_for(d: date):
    for name, s, e, mult, disc in FESTIVALS:
        if s <= d <= e:
            return name, mult, disc
    return None, 1.0, (5, 15)


def daterange(a, b):
    n = (b - a).days
    for i in range(n + 1):
        yield a + timedelta(days=i)


rows = []
base_price = {
    "Electronics": 3200, "Mobiles": 14500, "Fashion": 950, "Home & Kitchen": 1400,
    "Beauty & Personal Care": 650, "Grocery": 420, "Books": 380, "Sports & Fitness": 1100,
}

for d in daterange(START, END):
    days_elapsed = (d - START).days
    yoy_growth = 1 + 0.00035 * days_elapsed          # slow organic growth over time
    weekday_mult = 1.15 if d.weekday() >= 5 else 1.0  # weekend bump
    fest_name, fest_mult, disc_range = festival_for(d)
    is_festival = fest_name is not None

    for platform in PLATFORMS:
        # Flipkart historically leans harder into Big Billion Days, Amazon into Great Indian Festival
        platform_bias = 1.0
        if fest_name and "Billion" in fest_name:
            platform_bias = 1.15 if platform == "Flipkart" else 1.0
        if fest_name and "Diwali" in fest_name:
            platform_bias = 1.1 if platform == "Amazon" else 1.05

        for category, cat_weight in CATEGORIES.items():
            noise = rng.normal(1.0, 0.12)
            base_orders = 40 * cat_weight * weekday_mult * yoy_growth
            orders = max(0, base_orders * fest_mult * platform_bias * noise)
            orders = int(rng.poisson(orders))

            discount_pct = rng.uniform(*disc_range)
            avg_price = base_price[category] * (1 - discount_pct / 100) * rng.normal(1.0, 0.03)
            units_per_order = rng.normal(1.4 if is_festival else 1.15, 0.15)
            units_sold = max(orders, int(orders * max(units_per_order, 1)))
            revenue = round(orders * avg_price * max(units_per_order, 1), 2)
            return_rate = rng.uniform(2, 6) if not is_festival else rng.uniform(4, 9)
            returns = int(orders * return_rate / 100)

            rows.append({
                "date": d.isoformat(),
                "platform": platform,
                "category": category,
                "is_festival": is_festival,
                "festival_name": fest_name if fest_name else "Normal Day",
                "orders": orders,
                "units_sold": units_sold,
                "avg_discount_pct": round(discount_pct, 1),
                "revenue_inr": revenue,
                "returns": returns,
            })

df = pd.DataFrame(rows)
df.to_csv("data/sales_data.csv", index=False)
print(f"Generated {len(df):,} rows -> data/sales_data.csv")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total revenue: Rs {df['revenue_inr'].sum():,.0f}")
