import uuid
from datetime import datetime
from decimal import Decimal

import pandas as pd

from app.domain.allocations import Allocation
from app.storage.allocations import (
    get_allocations_for_transaction,
    save_allocations,
)
from app.utils.paths import data_path


TRANSACTIONS_PATH = data_path(
    "data/processed/transactions.parquet"
)


def _load_transactions() -> pd.DataFrame:

    if not TRANSACTIONS_PATH.exists():
        return pd.DataFrame()

    return pd.read_parquet(TRANSACTIONS_PATH)


def _save_transactions(df: pd.DataFrame) -> None:

    TRANSACTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(TRANSACTIONS_PATH, index=False)


def get_atm_transactions() -> pd.DataFrame:
    """Return all ATM_WITHDRAWAL transactions that are not yet ALLOCATED."""

    df = _load_transactions()

    if df.empty:
        return df

    mask = (
        (df["semantic_type_id"] == "ATM_WITHDRAWAL")
        & (df["resolution_status"] != "ALLOCATED")
    )

    return df[mask].sort_values("transaction_date", ascending=False).reset_index(drop=True)


def get_existing_allocations(transaction_id: str) -> pd.DataFrame:
    """Return any allocations already saved for this transaction."""

    return get_allocations_for_transaction(transaction_id)


def save_transaction_allocations(
    transaction_id: str,
    splits: list[dict],
) -> dict:
    """Persist allocation splits and mark the parent as ALLOCATED.

    `splits` is a list of dicts:
        [{"category_id": str, "amount": float, "note": str}, ...]

    Returns a summary dict with keys: saved, total_allocated, remainder.
    """

    df = _load_transactions()

    if df.empty or transaction_id not in df["transaction_id"].values:
        return {"error": "transaction not found"}

    parent_row = df[df["transaction_id"] == transaction_id].iloc[0]
    parent_amount = abs(float(parent_row["amount"]))

    total_allocated = sum(abs(float(s["amount"])) for s in splits)
    remainder = round(parent_amount - total_allocated, 2)

    allocations = [
        Allocation(
            allocation_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            category_id=s["category_id"],
            amount=Decimal(str(s["amount"])),
            allocation_note=s.get("note") or None,
            created_by="user",
            created_at=datetime.utcnow(),
        )
        for s in splits
        if float(s["amount"]) > 0
    ]

    save_allocations(allocations)

    # Mark parent transaction as ALLOCATED
    df.loc[
        df["transaction_id"] == transaction_id,
        "resolution_status",
    ] = "ALLOCATED"

    _save_transactions(df)

    return {
        "saved": len(allocations),
        "total_allocated": total_allocated,
        "remainder": remainder,
    }
