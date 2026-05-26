from collections import defaultdict

from app.utils.paths import data_path
import pandas as pd

from app.cashflow.services.forecast_group_registry_service import (
    resolve_forecast_group,
)

from app.recurring.services.recurring_override_service import (
    load_overrides,
)


TRANSACTIONS_PATH = data_path(
    "data/processed/transactions.parquet"
)


def build_last_complete_month_baseline():

    if not TRANSACTIONS_PATH.exists():
        return {}
    transactions_df = pd.read_parquet(
        TRANSACTIONS_PATH
    )

    overrides_df = (
        load_overrides()
    )

    if (
        transactions_df.empty
        or overrides_df.empty
    ):

        return {}

    latest_overrides = (
        overrides_df
        .sort_values(
            "timestamp"
        )
        .drop_duplicates(
            subset=[
                "entity_name"
            ],
            keep="last",
        )
    )

    override_lookup = {
        row["entity_name"]: row
        for _, row in (
            latest_overrides
            .iterrows()
        )
    }

    transactions_df[
        "transaction_date"
    ] = pd.to_datetime(
        transactions_df[
            "transaction_date"
        ]
    )

    monthly_periods = sorted(
        transactions_df[
            "transaction_date"
        ]
        .dt.to_period("M")
        .unique()
    )

    if len(monthly_periods) < 2:

        return {}

    last_complete_month = (
        monthly_periods[-2]
    )

    baseline_df = (
        transactions_df[
            transactions_df[
                "transaction_date"
            ]
            .dt.to_period("M")
            == last_complete_month
        ]
    )

    grouped_totals = (
        defaultdict(float)
    )

    for _, row in (
        baseline_df.iterrows()
    ):

        entity_name = row.get(
            "entity_name"
        )

        if not entity_name:

            continue

        override = (
            override_lookup.get(
                entity_name
            )
        )

        if override is None:

            continue

        forecast_group = (
            resolve_forecast_group(
                entity_name
            )
        )

        grouped_totals[
            forecast_group
        ] += abs(
            float(
                row["amount"]
            )
        )

    return {
        key: round(value, 2)
        for key, value in (
            grouped_totals.items()
        )
    }