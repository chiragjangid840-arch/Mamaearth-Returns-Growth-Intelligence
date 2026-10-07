
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

Path("visualizations").mkdir(exist_ok=True)

customers = pd.read_csv("data/customers.csv")
orders = pd.read_csv("data/orders.csv")
products = pd.read_csv("data/products.csv")

orders["payment_method"] = (
    orders["payment_method"]
    .astype(str)
    .str.strip()
    .str.upper()
)

orders["discount_pct"] = orders["discount_pct"].fillna(
    orders.groupby("product_id")["discount_pct"].transform("median")
)

orders["order_date"] = pd.to_datetime(orders["order_date"])

analysis = (
    orders
    .merge(customers, on="customer_id")
    .merge(products, on="product_id")
)

analysis["revenue"] = (
    analysis["quantity"]
    * analysis["price"]
    * (1 - analysis["discount_pct"] / 100)
)

# ---------------------------------
# Visualization 1:
# Return rate by payment method
# ---------------------------------

payment = (
    analysis.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
)

plt.figure(figsize=(7, 5))
payment.plot(kind="bar")
plt.title("Return Rate by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Return Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "visualizations/return_rate_by_payment.png",
    dpi=150
)

plt.close()


# ---------------------------------
# Visualization 2:
# Monthly revenue trend
# ---------------------------------

analysis["month"] = analysis["order_date"].dt.to_period("M").astype(str)

monthly_revenue = (
    analysis.groupby("month")["revenue"]
    .sum()
)

plt.figure(figsize=(8, 5))
monthly_revenue.plot(marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (INR)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    dpi=150
)

plt.close()

print("Visualizations created successfully!")
