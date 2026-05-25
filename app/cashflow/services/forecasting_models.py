from collections import defaultdict

import pandas as pd


def forecast_fixed_recurring_amount(
    transactions,
    cadence: str,
):

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

    average_amount = (
        sum(amounts)
        / len(amounts)
    )

    monthly_multiplier = {
        "weekly": 4,
        "biweekly": 2,
        "monthly": 1,
        "quarterly": (
            1 / 3
        ),
        "yearly": (
            1 / 12
        ),
        "irregular": 1,
    }.get(
        cadence,
        1,
    )

    return round(
        average_amount
        * monthly_multiplier,
        2,
    )


def forecast_behavioral_amount(
    transactions,
):

    monthly_totals = (
        defaultdict(float)
    )

    for transaction in transactions:

        transaction_date = (
            pd.to_datetime(
                transaction[
                    "transaction_date"
                ]
            )
        )

        month_key = (
            (
                f"{transaction_date.year}-"
                f"{transaction_date.month}"
            )
        )

        monthly_totals[
            month_key
        ] += abs(
            float(
                transaction[
                    "amount"
                ]
            )
        )

    if not monthly_totals:

        return 0

    active_month_totals = list(
        monthly_totals.values()
    )

    average_active_month_spend = (
        sum(active_month_totals)
        / len(active_month_totals)
    )

    return round(
        average_active_month_spend,
        2,
    )