from app.utils.paths import data_path
import pandas as pd


TRANSACTIONS_PATH = data_path(
    "data/processed/transactions.parquet"
)


def load_unresolved_transactions(
) -> pd.DataFrame:

    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()
    df = pd.read_parquet(
        TRANSACTIONS_PATH
    )

    unresolved_df = df[
        (
            df["category_id"]
            == "uncategorized"
        )
    ].copy()

    unresolved_df = (
        unresolved_df.sort_values(
            by=[
                "transaction_date",
            ],
            ascending=False,
        )
    )

    return unresolved_df.reset_index(
        drop=True
    )

def load_unresolved_transactions_for_account(
    account_id: str = "__all__",
) -> pd.DataFrame:
    """Same as load_unresolved_transactions but filtered to one account."""

    from app.ui.services.account_service import filter_by_account

    df = load_unresolved_transactions()
    return filter_by_account(df, account_id)


def load_all_transactions_for_account(
    account_id: str = "__all__",
) -> pd.DataFrame:
    """Load all resolved transactions, optionally filtered by account."""

    from app.ui.services.account_service import filter_by_account

    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()

    df = pd.read_parquet(TRANSACTIONS_PATH)
    df = filter_by_account(df, account_id)

    return df.sort_values("transaction_date", ascending=False).reset_index(drop=True)
