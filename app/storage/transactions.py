from pathlib import Path

import pandas as pd

from app.domain.transactions import (
    Transaction,
)

from app.overrides.services.override_service import (
    apply_overrides,
)


TRANSACTIONS_PATH = (
    Path(
        "data/processed/"
        "transactions.parquet"
    )
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
    transactions: list[
        Transaction
    ],
    overwrite_existing: bool = False,
) -> dict:

    new_df = pd.DataFrame([
        transaction_to_dict(
            transaction
        )
        for transaction
        in transactions
    ])

    if overwrite_existing:

        final_df = (
            apply_overrides(
                new_df
            )
        )

        inserted_count = len(
            final_df
        )

        skipped_duplicates = 0

    else:

        existing_df = (
            load_transactions()
        )

        if existing_df.empty:

            combined_df = new_df

        else:

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
                        "transaction_id"
                    ],
                    keep="last",
                )
            )

        final_df = (
            apply_overrides(
                combined_df
            )
        )

        inserted_count = len(
            new_df
        )

        skipped_duplicates = (
            len(combined_df)
            - len(new_df)
        )

    TRANSACTIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    final_df.to_parquet(
        TRANSACTIONS_PATH,
        index=False,
    )

    return {
        "inserted": inserted_count,
        "duplicates_skipped": (
            skipped_duplicates
        ),
        "total_transactions": (
            len(final_df)
        ),
    }