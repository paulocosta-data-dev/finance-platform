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