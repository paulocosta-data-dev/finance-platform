from pathlib import Path

import pandas as pd

from app.domain.transactions import Transaction


TRANSACTIONS_PATH = (
    Path("data/processed/transactions.parquet")
)


def transaction_to_dict(
    transaction: Transaction,
) -> dict:

    return transaction.model_dump()


def load_transactions() -> pd.DataFrame:

    if not TRANSACTIONS_PATH.exists():

        return pd.DataFrame()

    return pd.read_parquet(
        TRANSACTIONS_PATH
    )


def save_transactions(
    transactions: list[Transaction],
) -> dict:

    new_df = pd.DataFrame([
        transaction_to_dict(transaction)
        for transaction in transactions
    ])

    existing_df = load_transactions()

    existing_count = len(existing_df)

    if not existing_df.empty:

        combined_df = pd.concat(
            [existing_df, new_df],
            ignore_index=True,
        )

        combined_df = combined_df.drop_duplicates(
            subset=["transaction_id"],
            keep="first",
        )

    else:

        combined_df = new_df

    final_count = len(combined_df)

    inserted_count = (
        final_count - existing_count
    )

    skipped_duplicates = (
        len(new_df) - inserted_count
    )

    TRANSACTIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_parquet(
        TRANSACTIONS_PATH,
        index=False,
    )

    return {
        "inserted": inserted_count,
        "duplicates_skipped": skipped_duplicates,
        "total_transactions": final_count,
    }