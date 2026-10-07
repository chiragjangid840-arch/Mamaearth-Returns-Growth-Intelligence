
import pandas as pd
import numpy as np

# Load data
customers = pd.read_csv("data/customers.csv")
orders = pd.read_csv("data/orders.csv")
products = pd.read_csv("data/products.csv")

print("Customers:", customers.shape)
print("Orders:", orders.shape)
print("Products:", products.shape)

# Basic cleaning
orders["payment_method"] = (
    orders["payment_method"]
    .astype(str)
    .str.strip()
    .str.upper()
)

customers["signup_date"] = pd.to_datetime(customers["signup_date"])
orders["order_date"] = pd.to_datetime(orders["order_date"])

# Missing value treatment
orders["discount_pct"] = orders["discount_pct"].fillna(
    orders.groupby("product_id")["discount_pct"].transform("median")
)

orders["rating"] = orders["rating"].fillna(
    orders.groupby("product_id")["rating"].transform("median")
)

# Merge data
analysis = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(products, on="product_id", how="left")
)

# Revenue
analysis["revenue"] = (
    analysis["quantity"]
    * analysis["price"]
    * (1 - analysis["discount_pct"] / 100)
)

# Overall metrics
total_orders = len(analysis)
total_revenue = analysis["revenue"].sum()
average_order_value = analysis["revenue"].mean()
returned_orders = analysis["returned"].sum()
return_rate = analysis["returned"].mean() * 100

print("\nOverall Metrics")
print("Total Orders:", total_orders)
print("Total Revenue:", round(total_revenue, 2))
print("Average Order Value:", round(average_order_value, 2))
print("Returned Orders:", returned_orders)
print("Return Rate:", round(return_rate, 2), "%")

# Return rate by payment method
payment_return = (
    analysis.groupby("payment_method")
    .agg(
        orders=("order_id", "count"),
        returned_orders=("returned", "sum")
    )
)

payment_return["return_rate_pct"] = (
    payment_return["returned_orders"]
    / payment_return["orders"] * 100
)

print("\nReturn Rate by Payment Method")
print(payment_return)

# Return rate by city
city_return = (
    analysis.groupby("city")
    .agg(
        orders=("order_id", "count"),
        returned_orders=("returned", "sum")
    )
)

city_return["return_rate_pct"] = (
    city_return["returned_orders"]
    / city_return["orders"] * 100
)

print("\nReturn Rate by City")
print(city_return.sort_values("return_rate_pct", ascending=False))

# Revenue by category
category_revenue = (
    analysis.groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print("\nRevenue by Category")
print(category_revenue)

# Monthly analysis
analysis["month"] = analysis["order_date"].dt.to_period("M").astype(str)

monthly = analysis.groupby("month").agg(
    orders=("order_id", "count"),
    revenue=("revenue", "sum"),
    returned_orders=("returned", "sum")
)

monthly["return_rate_pct"] = (
    monthly["returned_orders"]
    / monthly["orders"] * 100
)

print("\nMonthly Analysis")
print(monthly)

# COD + City Tier segmentation
segment = (
    analysis.groupby(["payment_method", "city_tier"])
    .agg(
        orders=("order_id", "count"),
        returned_orders=("returned", "sum")
    )
)

segment["return_rate_pct"] = (
    segment["returned_orders"]
    / segment["orders"] * 100
)

print("\nPayment Method + City Tier")
print(segment)

# Correlation
corr_columns = [
    "quantity",
    "discount_pct",
    "rating",
    "returned",
    "price",
    "revenue"
]

print("\nCorrelation Matrix")
print(analysis[corr_columns].corr().round(2))
