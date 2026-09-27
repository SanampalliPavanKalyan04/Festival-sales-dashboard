"""
analysis.py
Loads data/sales_data.csv, computes the key business metrics, prints a
console summary report, saves static chart images to analysis/charts/,
and writes dashboard/data.js so the HTML dashboard can render everything
client-side with no server or build step.
"""

import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

pd.options.display.float_format = "{:,.0f}".format

df = pd.read_csv("data/sales_data.csv", parse_dates=["date"])
df["month"] = df["date"].dt.to_period("M").astype(str)
df["year"] = df["date"].dt.year
df["weekday"] = df["date"].dt.day_name()

os.makedirs("analysis/charts", exist_ok=True)

# ---------- 1. Headline metrics ----------
total_revenue = df["revenue_inr"].sum()
total_orders = df["orders"].sum()
total_units = df["units_sold"].sum()
aov = total_revenue / total_orders
festival_share = df.loc[df.is_festival, "revenue_inr"].sum() / total_revenue * 100

print("=" * 60)
print("ECOMMERCE SALES ANALYSIS — SUMMARY REPORT")
print("=" * 60)
print(f"Total revenue:            Rs {total_revenue:,.0f}")
print(f"Total orders:             {total_orders:,}")
print(f"Total units sold:         {total_units:,}")
print(f"Average order value:      Rs {aov:,.0f}")
print(f"Revenue from festival days: {festival_share:.1f}% (of only ~{df.is_festival.mean()*100:.0f}% of days)")

# ---------- 2. Festival vs Normal ----------
fest_vs_normal = df.groupby("is_festival").agg(
    revenue=("revenue_inr", "sum"),
    orders=("orders", "sum"),
    days=("date", "nunique"),
    avg_discount=("avg_discount_pct", "mean"),
    returns=("returns", "sum"),
).rename(index={True: "Festival", False: "Normal"})
fest_vs_normal["revenue_per_day"] = fest_vs_normal["revenue"] / fest_vs_normal["days"]
fest_vs_normal["return_rate_pct"] = fest_vs_normal["returns"] / fest_vs_normal["orders"] * 100
print("\n--- Festival vs Normal days ---")
print(fest_vs_normal[["days", "revenue", "revenue_per_day", "avg_discount", "return_rate_pct"]])

# ---------- 3. Revenue by festival event ----------
by_festival = (
    df[df.is_festival]
    .groupby("festival_name")
    .agg(revenue=("revenue_inr", "sum"), orders=("orders", "sum"), avg_discount=("avg_discount_pct", "mean"))
    .sort_values("revenue", ascending=False)
)
print("\n--- Revenue by festival event (both years combined) ---")
print(by_festival)

# ---------- 4. Category performance ----------
by_category = df.groupby("category").agg(
    revenue=("revenue_inr", "sum"), orders=("orders", "sum")
).sort_values("revenue", ascending=False)
by_category["festival_revenue_share_pct"] = (
    df[df.is_festival].groupby("category")["revenue_inr"].sum() / by_category["revenue"] * 100
)
print("\n--- Category performance ---")
print(by_category)

# ---------- 5. Platform comparison ----------
by_platform = df.groupby("platform").agg(
    revenue=("revenue_inr", "sum"), orders=("orders", "sum"), avg_discount=("avg_discount_pct", "mean")
)
print("\n--- Platform comparison ---")
print(by_platform)

# ---------- 6. Monthly trend & YoY ----------
monthly = df.groupby("month").agg(revenue=("revenue_inr", "sum"), orders=("orders", "sum")).reset_index()
yearly = df.groupby("year")["revenue_inr"].sum()
yoy_growth = (yearly.iloc[1] / yearly.iloc[0] - 1) * 100
print(f"\n--- YoY revenue growth 2023 -> 2024: {yoy_growth:.1f}% ---")

# ---------- 7. Day-of-week pattern ----------
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
by_dow = df.groupby("weekday")["revenue_inr"].sum().reindex(dow_order)

# ================== Charts (static PNGs for the repo / README) ==================
plt.style.use("seaborn-v0_8-darkgrid")

plt.figure(figsize=(10, 4.5))
plt.plot(monthly["month"], monthly["revenue"] / 1e7, marker="o", color="#F2A93B")
plt.title("Monthly Revenue Trend (Rs Crore)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("analysis/charts/monthly_trend.png", dpi=130)
plt.close()

plt.figure(figsize=(6, 4.5))
by_category["revenue"].sort_values().plot(kind="barh", color="#2FBF9F")
plt.title("Revenue by Category (Rs)")
plt.tight_layout()
plt.savefig("analysis/charts/category_revenue.png", dpi=130)
plt.close()

plt.figure(figsize=(6, 4.5))
fest_vs_normal["revenue_per_day"].plot(kind="bar", color=["#8B8FA3", "#F2A93B"])
plt.title("Avg Revenue per Day: Festival vs Normal (Rs)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("analysis/charts/festival_vs_normal.png", dpi=130)
plt.close()

print("\nSaved charts to analysis/charts/*.png")

# ================== Export aggregated data for the HTML dashboard ==================
export = {
    "headline": {
        "total_revenue": round(total_revenue),
        "total_orders": int(total_orders),
        "total_units": int(total_units),
        "aov": round(aov),
        "festival_revenue_share_pct": round(festival_share, 1),
        "yoy_growth_pct": round(yoy_growth, 1),
    },
    "monthly": [
        {"month": r.month, "revenue": round(r.revenue), "orders": int(r.orders)}
        for r in monthly.itertuples()
    ],
    "festival_vs_normal": {
        idx: {
            "days": int(row.days),
            "revenue": round(row.revenue),
            "revenue_per_day": round(row.revenue_per_day),
            "avg_discount": round(row.avg_discount, 1),
            "return_rate_pct": round(row.return_rate_pct, 1),
        }
        for idx, row in fest_vs_normal.iterrows()
    },
    "by_festival": [
        {
            "name": idx,
            "revenue": round(row.revenue),
            "orders": int(row.orders),
            "avg_discount": round(row.avg_discount, 1),
        }
        for idx, row in by_festival.iterrows()
    ],
    "by_category": [
        {
            "category": idx,
            "revenue": round(row.revenue),
            "orders": int(row.orders),
            "festival_share_pct": round(row.festival_revenue_share_pct, 1),
        }
        for idx, row in by_category.iterrows()
    ],
    "by_platform": [
        {
            "platform": idx,
            "revenue": round(row.revenue),
            "orders": int(row.orders),
            "avg_discount": round(row.avg_discount, 1),
        }
        for idx, row in by_platform.iterrows()
    ],
    "by_weekday": [
        {"weekday": d, "revenue": round(v)} for d, v in by_dow.items()
    ],
}

os.makedirs("dashboard", exist_ok=True)
with open("dashboard/data.js", "w") as f:
    f.write("// Auto-generated by analysis/analysis.py — do not edit by hand\n")
    f.write("const SALES_DATA = ")
    json.dump(export, f, indent=2)
    f.write(";\n")

print("Wrote dashboard/data.js")
