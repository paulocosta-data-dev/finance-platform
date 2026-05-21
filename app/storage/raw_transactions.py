from pathlib import Path

import pandas as pd

from app.domain.imports import (
    RawTransaction,
)


RAW_TRANSACTIONS_PATH = (
    Path(
        "data/processed/"
        "raw_transactions.parquet"
    )
)


def raw_transaction_to_dict(
    raw_transaction: RawTransaction,
) -> dict:

    return raw_transaction.model_dump()


def load_raw_transactions() -> pd.DataFrame:

    if not RAW_TRANSACTIONS_PATH.exists():

        return pd.DataFrame()

    return pd.read_parquet(
        RAW_TRANSACTIONS_PATH
    )


def save_raw_transactions(
    raw_transactions: list[
        RawTransaction
    ],
    overwrite_existing: bool = False,
) -> dict:

    new_df = pd.DataFrame([
        raw_transaction_to_dict(
            raw_transaction
        )
        for raw_transaction
        in raw_transactions
    ])

    existing_df = (
        load_raw_transactions()
    )

    if overwrite_existing:

        combined_df = new_df

        inserted_count = len(
            new_df
        )

        skipped_duplicates = 0

    else:

        existing_count = len(
            existing_df
        )

        if not existing_df.empty:

            combined_df = pd.concat(
                [
                    existing_df,
                    new_df,
                ],
                ignore_index=True,
            )

            combined_df = (
                combined_df
                .drop_duplicates(
                    subset=[
                        "raw_transaction_id"
                    ],
                    keep="first",
                )
            )

        else:

            combined_df = new_df

        final_count = len(
            combined_df
        )

        inserted_count = (
            final_count
            - existing_count
        )

        skipped_duplicates = (
            len(new_df)
            - inserted_count
        )

    RAW_TRANSACTIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_parquet(
        RAW_TRANSACTIONS_PATH,
        index=False,
    )

    return {
        "inserted": inserted_count,
        "duplicates_skipped": (
            skipped_duplicates
        ),
        "total_raw_transactions": (
            len(combined_df)
        ),
    }