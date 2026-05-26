"""
Provides the data that powers the Dashboard page.
All computations are done directly on transactions.parquet
without requiring recurring overrides or forecast groups.
"""

from app.utils.paths import data_path
import pandas as pd

TRANSACTIONS_PATH = data_path(
    "data/processed/transactions.parquet"
)


def _load() -> pd.DataFrame:

    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()

    df = pd.read_parquet(TRANSACTIONS_PATH)

    if df.empty:
        return df

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    )

    return df


def get_monthly_income_spending(n_months: int = 6) -> list[dict]:
    """Return last n_months of monthly income and spending.

    Each dict: {"month": "2024-11", "income": 3200.0, "spending": 1850.0}
    Ordered oldest → newest.
    """

    df = _load()

    if df.empty:
        return []

    df["month"] = df["transaction_date"].dt.to_period("M")

    all_months = sorted(df["month"].dropna().unique())
    recent_months = all_months[-n_months:]

    result = []

    for month in recent_months:
        month_df = df[df["month"] == month]
        income = float(month_df[month_df["amount"] > 0]["amount"].sum())
        spending = float(abs(month_df[month_df["amount"] < 0]["amount"].sum()))
        result.append({
            "month": str(month),
            "income": round(income, 2),
            "spending": round(spending, 2),
        })

    return result


def get_category_breakdown_current_month() -> list[dict]:
    """Return spending by category for the current (most recent) month.

    Each dict: {"category_id": str, "total": float}
    Ordered by total descending.
    """

    df = _load()

    if df.empty:
        return []

    df["month"] = df["transaction_date"].dt.to_period("M")
    current_month = df["month"].max()

    month_df = df[
        (df["month"] == current_month)
        & (df["amount"] < 0)
    ]

    if month_df.empty:
        return []

    breakdown = (
        month_df.groupby("category_id")["amount"]
        .sum()
        .abs()
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )

    return [
        {"category_id": row["category_id"], "total": row["amount"]}
        for _, row in breakdown.iterrows()
    ]


def get_summary_stats() -> dict:
    """Quick headline numbers for the top metric cards."""

    df = _load()

    if df.empty:
        return {
            "total_transactions": 0,
            "categorized": 0,
            "uncategorized": 0,
            "coverage_pct": 0.0,
            "total_spending": 0.0,
            "total_income": 0.0,
            "current_month_label": "—",
        }

    total = len(df)
    categorized = int((df["category_id"] != "uncategorized").sum())
    uncategorized = total - categorized
    coverage = round(categorized / max(total, 1) * 100, 1)

    df["month"] = df["transaction_date"].dt.to_period("M")
    current_month = df["month"].max()
    month_df = df[df["month"] == current_month]

    current_income = float(month_df[month_df["amount"] > 0]["amount"].sum())
    current_spending = float(abs(month_df[month_df["amount"] < 0]["amount"].sum()))

    return {
        "total_transactions": total,
        "categorized": categorized,
        "uncategorized": uncategorized,
        "coverage_pct": coverage,
        "current_month_income": round(current_income, 2),
        "current_month_spending": round(current_spending, 2),
        "current_month_label": str(current_month),
    }
