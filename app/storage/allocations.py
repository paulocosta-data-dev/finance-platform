import uuid
from datetime import datetime
from decimal import Decimal

import pandas as pd

from app.domain.allocations import Allocation
from app.utils.paths import data_path


ALLOCATIONS_PATH = data_path(
    "data/processed/allocations.parquet"
)


def load_allocations() -> pd.DataFrame:

    if not ALLOCATIONS_PATH.exists():
        return pd.DataFrame(
            columns=[
                "allocation_id",
                "transaction_id",
                "category_id",
                "amount",
                "allocation_note",
                "created_by",
                "created_at",
            ]
        )

    return pd.read_parquet(ALLOCATIONS_PATH)


def save_allocations(allocations: list[Allocation]) -> None:

    existing_df = load_allocations()

    new_rows = pd.DataFrame([
        {
            "allocation_id": a.allocation_id,
            "transaction_id": a.transaction_id,
            "category_id": a.category_id,
            "amount": float(a.amount),
            "allocation_note": a.allocation_note,
            "created_by": a.created_by,
            "created_at": a.created_at,
        }
        for a in allocations
    ])

    combined = pd.concat(
        [existing_df, new_rows],
        ignore_index=True,
    ).drop_duplicates(
        subset=["allocation_id"],
        keep="last",
    )

    ALLOCATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(ALLOCATIONS_PATH, index=False)


def get_allocations_for_transaction(
    transaction_id: str,
) -> pd.DataFrame:

    df = load_allocations()

    if df.empty:
        return df

    return df[df["transaction_id"] == transaction_id].copy()
