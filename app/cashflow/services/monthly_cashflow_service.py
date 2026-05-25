from collections import defaultdict

import pandas as pd

from app.cashflow.services.forecast_group_registry_service import (
    resolve_forecast_group,
)

from app.cashflow.services.forecasting_models import (
    forecast_behavioral_amount,
)

from app.cashflow.services.forecasting_models import (
    forecast_fixed_recurring_amount,
)

from app.cashflow.services.monthly_baseline_service import (
    build_last_complete_month_baseline,
)

from app.recurring.services.recurring_override_service import (
    load_overrides,
)


TRANSACTIONS_PATH = (
    "data/processed/transactions.parquet"
)


def load_transactions():

    return pd.read_parquet(
        TRANSACTIONS_PATH
    )


def build_monthly_cashflow_summary():

    transactions_df = (
        load_transactions()
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

    grouped_entities = (
        defaultdict(list)
    )

    for _, row in (
        transactions_df.iterrows()
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

        if (
            override["status"]
            != "confirmed"
        ):

            continue

        grouped_entities[
            entity_name
        ].append(row)

    forecast_groups = (
        defaultdict(float)
    )

    details = []

    for (
        entity_name,
        transactions,
    ) in (
        grouped_entities.items()
    ):

        override = (
            override_lookup[
                entity_name
            ]
        )

        recurring_type = (
            override[
                "recurring_type"
            ]
        )

        cadence = (
            override[
                "cadence"
            ]
        )

        if (
            recurring_type
            == "behavioral"
        ):

            projected_amount = (
                forecast_behavioral_amount(
                    transactions
                )
            )

        else:

            projected_amount = (
                forecast_fixed_recurring_amount(
                    transactions=(
                        transactions
                    ),
                    cadence=cadence,
                )
            )

        forecast_group = (
            resolve_forecast_group(
                entity_name
            )
        )

        forecast_groups[
            forecast_group
        ] += projected_amount

        details.append(
            {
                "entity_name": (
                    entity_name
                ),
                "forecast_group": (
                    forecast_group
                ),
                "recurring_type": (
                    recurring_type
                ),
                "cadence": cadence,
                "projected_monthly_amount": (
                    projected_amount
                ),
                "transaction_count": (
                    len(
                        transactions
                    )
                ),
            }
        )

    baseline = (
        build_last_complete_month_baseline()
    )

    grouped_summary = []

    for (
        forecast_group,
        projected_amount,
    ) in (
        forecast_groups.items()
    ):

        baseline_amount = (
            baseline.get(
                forecast_group,
                0,
            )
        )

        delta = round(
            (
                projected_amount
                - baseline_amount
            ),
            2,
        )

        delta_percentage = 0

        if baseline_amount > 0:

            delta_percentage = round(
                (
                    delta
                    / baseline_amount
                )
                * 100,
                1,
            )

        grouped_summary.append(
            {
                "group": (
                    forecast_group
                ),
                "last_complete_month": (
                    round(
                        baseline_amount,
                        2,
                    )
                ),
                "forecast": round(
                    projected_amount,
                    2,
                ),
                "delta": delta,
                "delta_percentage": (
                    delta_percentage
                ),
            }
        )

    return {
        "grouped_summary": (
            grouped_summary
        ),
        "details": details,
    }