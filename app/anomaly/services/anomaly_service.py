"""
Spending anomaly detection.

A transaction is flagged when its amount is unusually large compared
to the historical distribution for that category.

Rules:
  - Requires at least MIN_HISTORY_COUNT transactions in the category
    before any flagging (too few data points = no reliable signal).
  - If std == 0 (all amounts identical), never flag.
  - severity "medium" : amount > mean + MEDIUM_THRESHOLD * std
  - severity "high"   : amount > mean + HIGH_THRESHOLD  * std

All functions are pure (no I/O) so they are easy to test and cache.
"""

import math

MIN_HISTORY_COUNT = 5
MEDIUM_THRESHOLD = 2.0
HIGH_THRESHOLD = 3.0


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_category_stats(df) -> dict[str, dict]:
    """
    Compute per-category mean and std of abs(amount) for debit transactions.

    Returns:
        {
            "groceries": {"mean": 65.4, "std": 18.2, "count": 16},
            ...
        }

    Only categories with count >= MIN_HISTORY_COUNT are included.
    Categories where std == 0 are included but will never trigger flags.
    """
    if df is None or df.empty:
        return {}

    result = {}

    spending = [
        row for _, row in df.iterrows()
        if _to_float(row.get("amount", 0)) < 0
    ]

    from collections import defaultdict
    by_cat = defaultdict(list)
    for row in spending:
        cat = row.get("category_id", "")
        if cat:
            by_cat[cat].append(abs(_to_float(row["amount"])))

    for cat, amounts in by_cat.items():
        n = len(amounts)
        if n < MIN_HISTORY_COUNT:
            continue
        mean = sum(amounts) / n
        variance = sum((a - mean) ** 2 for a in amounts) / (n - 1) if n > 1 else 0.0
        std = math.sqrt(variance)
        result[cat] = {"mean": round(mean, 2), "std": round(std, 2), "count": n}

    return result


def flag_anomalies(df, category_stats: dict[str, dict]):
    """
    Return a copy of df with two new columns:
        is_anomaly      bool
        anomaly_severity  str | None  ("medium" | "high" | None)

    Only debit transactions are ever flagged.
    """
    if df is None or df.empty:
        return df

    import pandas as pd

    df = df.copy()
    df["is_anomaly"] = False
    df["anomaly_severity"] = None

    for idx, row in df.iterrows():
        amount = _to_float(row.get("amount", 0))
        if amount >= 0:
            continue  # credits never flagged

        cat = row.get("category_id", "")
        stats = category_stats.get(cat)
        if stats is None:
            continue

        mean = stats["mean"]
        std = stats["std"]
        abs_amount = abs(amount)

        if std == 0:
            continue

        if abs_amount > mean + HIGH_THRESHOLD * std:
            df.at[idx, "is_anomaly"] = True
            df.at[idx, "anomaly_severity"] = "high"
        elif abs_amount > mean + MEDIUM_THRESHOLD * std:
            df.at[idx, "is_anomaly"] = True
            df.at[idx, "anomaly_severity"] = "medium"

    return df
