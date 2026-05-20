import pandas as pd

from app.domain.imports import RawTransaction
from app.ingestion.normalizer import (
    normalize_raw_transaction,
)
from app.storage.transactions import (
    save_transactions,
)


RAW_TRANSACTIONS_PATH = (
    "data/processed/raw_transactions.parquet"
)


def rebuild_raw_transaction(
    row,
) -> RawTransaction:

    return RawTransaction(
        raw_transaction_id=(
            row["raw_transaction_id"]
        ),
        import_file_id=(
            row["import_file_id"]
        ),
        source_account_id=(
            row["source_account_id"]
        ),
        sheet_name=row["sheet_name"],
        source_row_number=(
            row["source_row_number"]
        ),
        raw_date=row["raw_date"],
        raw_booking_date=(
            row["raw_booking_date"]
        ),
        raw_description=(
            row["raw_description"]
        ),
        raw_amount=row["raw_amount"],
        raw_balance=row["raw_balance"],
        raw_payload_json=(
            row["raw_payload_json"]
        ),
        created_at=row["created_at"],
    )


def run_normalization_pipeline():

    raw_df = pd.read_parquet(
        RAW_TRANSACTIONS_PATH
    )

    normalized_transactions = []

    for _, row in raw_df.iterrows():

        raw_transaction = (
            rebuild_raw_transaction(
                row
            )
        )

        transaction = (
            normalize_raw_transaction(
                raw_transaction=(
                    raw_transaction
                ),
                account_id=(
                    raw_transaction
                    .source_account_id
                ),
            )
        )

        normalized_transactions.append(
            transaction
        )

    result = save_transactions(
        normalized_transactions
    )

    print(
        f"""
Normalization pipeline completed

New transactions inserted:
{result["inserted"]}

Duplicate transactions skipped:
{result["duplicates_skipped"]}

Total transactions stored:
{result["total_transactions"]}
"""
    )