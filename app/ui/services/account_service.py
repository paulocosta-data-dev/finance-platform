"""
Account-awareness helpers.
Provides the list of known accounts and per-account balance/stats.
"""

from app.utils.paths import data_path
import pandas as pd

TRANSACTIONS_PATH = data_path(
    "data/processed/transactions.parquet"
)

ALL_ACCOUNTS = "__all__"


def _load() -> pd.DataFrame:

    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()

    return pd.read_parquet(TRANSACTIONS_PATH)


def get_account_ids() -> list[str]:
    """Return sorted list of distinct account_ids found in transactions."""

    df = _load()

    if df.empty or "account_id" not in df.columns:
        return []

    return sorted(df["account_id"].dropna().unique().tolist())


def get_account_balances() -> list[dict]:
    """Return running balance per account.

    Each dict: {"account_id": str, "income": float, "spending": float, "balance": float}
    """

    df = _load()

    if df.empty:
        return []

    result = []

    for account_id, group in df.groupby("account_id"):
        income = float(group[group["amount"] > 0]["amount"].sum())
        spending = float(abs(group[group["amount"] < 0]["amount"].sum()))
        balance = round(income - spending, 2)
        result.append({
            "account_id": account_id,
            "income": round(income, 2),
            "spending": round(spending, 2),
            "balance": balance,
        })

    return sorted(result, key=lambda x: x["account_id"])


def filter_by_account(
    df: pd.DataFrame,
    account_id: str,
) -> pd.DataFrame:
    """Filter a DataFrame by account_id. Pass ALL_ACCOUNTS to skip filtering."""

    if account_id == ALL_ACCOUNTS or not account_id:
        return df

    if "account_id" not in df.columns:
        return df

    return df[df["account_id"] == account_id].copy()
