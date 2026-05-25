from collections import defaultdict

import pandas as pd

from app.recurring.services.recurring_override_service import (
    get_override_lookup,
)


TRANSACTIONS_PATH = (
    "data/processed/transactions.parquet"
)


MIN_OCCURRENCES = 3


EXCLUDED_ENTITIES = {
    "peer_transfer",
    "internal_transfer",
}


def load_transactions() -> pd.DataFrame:

    return pd.read_parquet(
        TRANSACTIONS_PATH
    )


def detect_recurring_transactions():

    df = load_transactions()

    if df.empty:

        return []

    override_lookup = (
        get_override_lookup()
    )

    recurring_candidates = (
        defaultdict(list)
    )

    for _, row in df.iterrows():

        entity_name = (
            row["entity_name"]
        )

        if not entity_name:

            continue

        if entity_name in (
            EXCLUDED_ENTITIES
        ):

            continue

        override = (
            override_lookup.get(
                entity_name
            )
        )

        if override:

            if (
                override["status"]
                in [
                    "confirmed",
                    "ignored",
                ]
            ):

                continue

        recurring_candidates[
            entity_name
        ].append(row)

    recurring_results = []

    for (
        entity_name,
        transactions,
    ) in (
        recurring_candidates.items()
    ):

        occurrences = len(
            transactions
        )

        if (
            occurrences
            < MIN_OCCURRENCES
        ):

            continue

        amounts = [
            abs(
                float(
                    transaction[
                        "amount"
                    ]
                )
            )
            for transaction
            in transactions
        ]

        average_amount = round(
            (
                sum(amounts)
                / len(amounts)
            ),
            2,
        )

        transaction_dates = sorted([
            pd.to_datetime(
                transaction[
                    "transaction_date"
                ]
            )
            for transaction
            in transactions
        ])

        first_seen = (
            transaction_dates[0]
            .date()
        )

        last_seen = (
            transaction_dates[-1]
            .date()
        )

        recurring_results.append(
            {
                "entity_name": (
                    entity_name
                ),
                "occurrences": (
                    occurrences
                ),
                "average_amount": (
                    average_amount
                ),
                "first_seen": (
                    first_seen
                ),
                "last_seen": (
                    last_seen
                ),
            }
        )

    recurring_results = sorted(
        recurring_results,
        key=lambda item: (
            item["occurrences"]
        ),
        reverse=True,
    )

    return recurring_results