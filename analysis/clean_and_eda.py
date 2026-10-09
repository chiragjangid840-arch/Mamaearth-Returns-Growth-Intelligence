
from pathlib import Path
import pandas as pd

# Project folders
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "analysis"

def load_data():
    customers = pd.read_csv(DATA / "customers.csv")
    orders = pd.read_csv(DATA / "orders.csv")
    products = pd.read_csv(DATA / "products.csv")

    print("Customers:", customers.shape)
    print("Products:", products.shape)
    print("Raw orders:", orders.shape)

    return customers, orders, products


def clean_orders(orders):
    # Standardize payment method names
    orders["payment_method"] = (
        orders["payment_method"].str.strip().str.upper()
    )

    print("\nPayment methods after standardization:")
    print(orders["payment_method"].value_counts().to_string())

    # Remove duplicate orders using the required natural key
    duplicate_key = [
        "customer_id", "product_id", "order_date", "quantity",
        "discount_pct", "payment_method", "rating", "returned"
    ]

    dropped = orders.loc[
        orders.duplicated(subset=duplicate_key, keep="first")
    ]

    print("\nDropped duplicate order IDs:")
    print(dropped["order_id"].tolist())

    orders_clean = orders.drop_duplicates(
        subset=duplicate_key, keep="first"
    ).copy()

    print("Cleaned orders shape:", orders_clean.shape)

    # Fill missing values as required by the assignment
    print("\nRating median before imputation:",
          orders_clean["rating"].median())

    orders_clean["discount_pct"] = (
        orders_clean["discount_pct"].fillna(0)
    )
    orders_clean["rating"] = (
        orders_clean["rating"].fillna(
            orders_clean["rating"].median()
        )
    )

    print("\nMissing values after cleaning:")
    print(
        orders_clean[["discount_pct", "rating"]]
        .isnull().sum().to_string()
    )

    return orders_clean


def build_analysis(customers, orders_clean, products):
    analysis = orders_clean.merge(
        products, on="product_id", how="left",
        validate="many_to_one"
    )

    analysis = analysis.merge(
        customers, on="customer_id", how="left",
        validate="many_to_one"
    )

    analysis["order_date"] = pd.to_datetime(analysis["order_date"])

    analysis["order_value"] = (
        analysis["quantity"]
        * analysis["price"]
        * (1 - analysis["discount_pct"] / 100)
    )

    # IQR outlier detection: flag but do not delete
    q1 = analysis["quantity"].quantile(0.25)
    q3 = analysis["quantity"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    analysis["is_outlier"] = (
        (analysis["quantity"] < lower)
        | (analysis["quantity"] > upper)
    )

    print("\nIQR results:")
    print(f"Q1={q1}, Q3={q3}, IQR={iqr}")
    print(f"Lower={lower}, Upper={upper}")
    print(
        analysis.loc[
            analysis["is_outlier"], ["order_id", "quantity"]
        ].to_string(index=False)
    )

    print("\nTask 5 reconciliation")
    print("Cleaned orders:", len(analysis))
    print("Total revenue:", round(analysis["order_value"].sum(), 2))
    print("Average order value:", round(analysis["order_value"].mean(), 2))

    return analysis


def run_analysis():
    customers, orders, products = load_data()
    orders_clean = clean_orders(orders)
    analysis = build_analysis(customers, orders_clean, products)

    # Task 7: Hypothesis
    print("\nH0: COD does not have a higher return rate.")
    print("H1: COD has a higher return rate.")

    payment = analysis.groupby("payment_method")["returned"].agg(
        orders="count", returned_orders="sum", return_rate="mean"
    )
    payment["return_rate_pct"] = payment["return_rate"] * 100
    print(payment[["orders", "returned_orders", "return_rate_pct"]].round(1))

    cod_rate = payment.loc["COD", "return_rate_pct"]
    other_rate = (
        analysis.loc[analysis["payment_method"] != "COD", "returned"].mean()
        * 100
    )
    print("COD hypothesis:", "CONFIRMED" if cod_rate > other_rate else "NOT CONFIRMED")

    # Task 8: Segmentation
    segment = analysis.groupby(
        ["payment_method", "city_tier"]
    )["returned"].agg(orders="count", returned_orders="sum", return_rate="mean")

    segment["return_rate_pct"] = segment["return_rate"] * 100
    print("\nPayment + city tier segmentation:")
    print(segment[["orders", "returned_orders", "return_rate_pct"]].round(1))

    # Task 9: Correlation
    cols = ["rating", "returned", "discount_pct", "quantity"]
    corr = analysis[cols].corr()

    print("\nCorrelation matrix:")
    print(corr.round(3))

    print("\nPairwise correlation strength:")
    for i, col1 in enumerate(cols):
        for col2 in cols[i + 1:]:
            r = corr.loc[col1, col2]
            strength = (
                "negligible" if abs(r) < 0.2 else
                "weak" if abs(r) < 0.4 else
                "moderate" if abs(r) < 0.7 else "strong"
            )
            print(f"{col1} vs {col2}: {r:.3f} — {strength}")

    print(
        "\nHigher discounts reduce returns: BUSTED "
        f"(correlation={corr.loc['discount_pct', 'returned']:.3f})"
    )

    # Task 10: Monthly series, both including and excluding outliers
    analysis["year_month"] = analysis["order_date"].dt.to_period("M")
    monthly_all = analysis.groupby("year_month")["order_value"].sum()
    monthly_corrected = (
        analysis.loc[~analysis["is_outlier"]]
        .groupby("year_month")["order_value"].sum()
    )

    print("\nMonthly revenue including outliers:")
    print(monthly_all.round(2).to_string())

    print("\nMonthly revenue excluding outliers:")
    print(monthly_corrected.round(2).to_string())

    print("\nPeak including outliers:", monthly_all.idxmax())
    print("Peak excluding outliers:", monthly_corrected.idxmax())

    # Save reusable analysis for the visualization script
    output_file = OUTPUT / "cleaned_analysis.csv"
    analysis.to_csv(output_file, index=False)
    print("\nSaved:", output_file)


if __name__ == "__main__":
    run_analysis()
