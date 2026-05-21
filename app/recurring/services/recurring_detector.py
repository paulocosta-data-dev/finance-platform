import statistics

import pandas as pd

from app.recurring.models.recurring_pattern import (
    RecurringPattern,
)


TRANSACTIONS_PATH = (
    "data/processed/"
    "transactions.parquet"
)


def calculate_median_interval(
    dates: list,
) -> float:

    if len(dates) < 2:
        return 0.0

    unique_dates = sorted(
        set(
            date.date()
            for date in dates
        )
    )

    if len(unique_dates) < 2:
        return 0.0

    intervals = []

    for index in range(
        1,
        len(unique_dates),
    ):

        delta = (
            unique_dates[index]
            - unique_dates[index - 1]
        ).days

        intervals.append(delta)

    return float(
        statistics.median(
            intervals
        )
    )


def classify_cadence(
    interval_days: float,
) -> str:

    if (
        25
        <= interval_days
        <= 35
    ):

        return "MONTHLY"

    if (
        6
        <= interval_days
        <= 8
    ):

        return "WEEKLY"

    if (
        13
        <= interval_days
        <= 16
    ):

        return "BIWEEKLY"

    if (
        85
        <= interval_days
        <= 95
    ):

        return "QUARTERLY"

    if (
        170
        <= interval_days
        <= 190
    ):

        return "SEMIANNUAL"

    if (
        350
        <= interval_days
        <= 380
    ):

        return "YEARLY"

    return "IRREGULAR"


def detect_recurring_patterns(
    minimum_occurrences: int = 3,
) -> list[RecurringPattern]:

    df = pd.read_parquet(
        TRANSACTIONS_PATH
    )

    grouped = (
        df.groupby(
            [
                "normalized_description",
                "semantic_type_id",
                "category_id",
            ]
        )
    )

    patterns = []

    for keys, group in grouped:

        occurrences = len(group)

        if (
            occurrences
            < minimum_occurrences
        ):

            continue

        dates = list(
            pd.to_datetime(
                group[
                    "transaction_date"
                ]
            )
        )

        median_interval_days = (
            calculate_median_interval(
                dates
            )
        )

        recurring_pattern = (
            RecurringPattern(
                normalized_description=(
                    keys[0]
                ),
                semantic_type_id=(
                    keys[1]
                ),
                category_id=(
                    keys[2]
                ),
                occurrences=(
                    occurrences
                ),
                average_amount=float(
                    group[
                        "amount"
                    ].mean()
                ),
                first_seen=min(
                    dates
                ).date(),
                last_seen=max(
                    dates
                ).date(),
                average_interval_days=(
                    median_interval_days
                ),
                cadence_type=(
                    classify_cadence(
                        median_interval_days
                    )
                ),
            )
        )

        patterns.append(
            recurring_pattern
        )

    return sorted(
        patterns,
        key=lambda pattern: (
            pattern.occurrences
        ),
        reverse=True,
    )