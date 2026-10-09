
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "visualizations"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_clean_analysis():
    customers = pd.read_csv(DATA / "customers.csv")
    orders = pd.read_csv(DATA / "orders.csv")
    products = pd.read_csv(DATA / "products.csv")

    orders["payment_method"] = (
        orders["payment_method"].str.strip().str.upper()
    )

    # Remove duplicate orders using the assignment's natural key
    duplicate_key = [
        "customer_id", "product_id", "order_date", "quantity",
        "discount_pct", "payment_method", "rating", "returned"
    ]

    orders = orders.drop_duplicates(
        subset=duplicate_key, keep="first"
    ).copy()

    # Assignment-required missing-value handling
    orders["discount_pct"] = orders["discount_pct"].fillna(0)
    orders["rating"] = orders["rating"].fillna(
        orders["rating"].median()
    )

    analysis = orders.merge(
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

    q1 = analysis["quantity"].quantile(0.25)
    q3 = analysis["quantity"].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # Flag outliers; do not delete them from the cleaned dataset
    analysis["is_outlier"] = (
        (analysis["quantity"] < lower)
        | (analysis["quantity"] > upper)
    )

    return analysis


def plot_payment_return_rate(analysis):
    payment = (
        analysis.groupby("payment_method")["returned"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(payment.index, payment.values)

    for bar, value in zip(bars, payment.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f}%",
            ha="center",
            va="bottom"
        )

    ax.set_title("COD Returns at 44.4% — Highest by Payment Method")
    ax.set_xlabel("Payment Method")
    ax.set_ylabel("Return Rate (%)")
    ax.set_ylim(0, max(payment.values) * 1.2)
    fig.tight_layout()

    path = OUTPUT / "return_rate_by_payment.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Saved:", path)


def plot_monthly_revenue(analysis):
    # Exclude only flagged outlier orders for the corrected time series
    corrected = analysis.loc[~analysis["is_outlier"]].copy()
    corrected["year_month"] = corrected["order_date"].dt.to_period("M")

    monthly = corrected.groupby("year_month")["order_value"].sum()
    peak_month = monthly.idxmax()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(monthly.index.astype(str), monthly.values, marker="o")

    ax.set_title(f"Outlier-Corrected Monthly Revenue — Peak: {peak_month}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (INR)")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()

    path = OUTPUT / "monthly_revenue_trend.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Saved:", path)

    print("\nOutlier-corrected monthly revenue:")
    print(monthly.round(2).to_string())
    print("Peak month:", peak_month)


def main():
    analysis = load_clean_analysis()

    print("Cleaned analysis shape:", analysis.shape)
    print("Flagged outliers:", int(analysis["is_outlier"].sum()))

    plot_payment_return_rate(analysis)
    plot_monthly_revenue(analysis)

    print("\nBoth visualizations created successfully.")


if __name__ == "__main__":
    main()
