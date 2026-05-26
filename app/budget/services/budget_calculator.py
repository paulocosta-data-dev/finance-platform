"""
Automatic budget calculator.

For each spending category the algorithm:

1.  Builds a complete monthly series (all months in the dataset,
    missing months filled with 0).
2.  Computes:
      mean_active  = average spend across months where the category
                     was used (ignores zero months)
      frequency    = fraction of months where the category was used
      mean_overall = mean_active × frequency
                   = expected spend in any given month
3.  Detects trend via linear regression on the monthly series.
      slope > 0  → spending growing  → add one forward month of slope
      slope < 0  → spending falling  → keep mean_overall (conservative)
4.  Classifies the category:
      "recurring_fixed"    cv < 0.20 and frequency >= 0.70
                           → stable bills (condo, subscriptions)
      "recurring_variable" cv 0.20–0.50 and frequency >= 0.40
                           → regular but variable (groceries)
      "occasional"         everything else
                           → infrequent or highly variable spend
5.  Applies a buffer multiplier per class:
      recurring_fixed    × 1.0  (no buffer — amount is predictable)
      recurring_variable × 1.10 (10 % safety margin)
      occasional         × 1.15 (15 % safety margin)
6.  Applies inflation:
      budget = (mean_overall + trend_adjustment) × buffer × (1 + inflation_rate)
      rounded to the nearest euro.

Categories excluded from calculation:
  - "uncategorized"  (not resolved yet)
  - "savings"        (transfer, not real spending)
"""

import math
from typing import Any

EXCLUDED_CATEGORIES = {"uncategorized", "savings"}
MIN_MONTHS_FOR_TREND = 3


def _to_float(value: Any) -> float:
    """Convert Decimal or anything numeric to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_monthly_series(
    monthly_totals: dict[str, float],
    all_months: list[str],
) -> list[float]:
    """Return a list of floats ordered by month, 0.0 for missing months."""
    return [monthly_totals.get(m, 0.0) for m in all_months]


def _linear_slope(series: list[float]) -> float:
    """Returns the OLS slope (euros per month) of a numeric series."""
    n = len(series)
    if n < MIN_MONTHS_FOR_TREND:
        return 0.0

    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(series) / n

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series))
    den = sum((x - mean_x) ** 2 for x in xs)

    return num / den if den else 0.0


def calculate_category_budget(
    category_id: str,
    monthly_totals: dict[str, float],
    all_months: list[str],
    inflation_rate: float = 0.03,
) -> dict | None:
    """
    Calculate the recommended monthly budget for one category.

    Returns a dict or None if the category should be skipped.

    Dict keys:
        category_id      str
        recommended      float   (rounded to nearest euro)
        mean_overall     float
        classification   str     ("recurring_fixed" | "recurring_variable" | "occasional")
        frequency        float   (0–1, fraction of months with spend)
        trend_monthly    float   (euros/month slope; positive = growing)
        inflation_rate   float   (as provided)
        n_months_data    int     (total months in dataset)
        n_months_active  int     (months with actual spend)
    """

    if category_id in EXCLUDED_CATEGORIES:
        return None

    series = build_monthly_series(monthly_totals, all_months)
    n_total = len(series)

    active = [v for v in series if v > 0]
    n_active = len(active)

    if n_active == 0:
        return None

    mean_active = sum(active) / n_active
    frequency = n_active / n_total
    mean_overall = mean_active * frequency

    # Coefficient of variation (on active months only)
    if n_active >= 2:
        variance = sum((v - mean_active) ** 2 for v in active) / (n_active - 1)
        std_active = math.sqrt(variance)
        cv = std_active / mean_active if mean_active > 0 else 0.0
    else:
        cv = 0.0

    # Trend — computed on full series (including zero months)
    slope = _linear_slope(series)
    trend_adjustment = max(0.0, slope)  # only add positive trend; don't subtract

    # Classification
    if cv < 0.20 and frequency >= 0.70:
        classification = "recurring_fixed"
        buffer = 1.00
    elif cv <= 0.50 and frequency >= 0.40:
        classification = "recurring_variable"
        buffer = 1.10
    else:
        classification = "occasional"
        buffer = 1.15

    raw = (mean_overall + trend_adjustment) * buffer * (1 + inflation_rate)
    recommended = max(1.0, round(raw))

    return {
        "category_id": category_id,
        "recommended": recommended,
        "mean_overall": round(mean_overall, 2),
        "classification": classification,
        "frequency": round(frequency, 2),
        "trend_monthly": round(slope, 2),
        "inflation_rate": inflation_rate,
        "n_months_data": n_total,
        "n_months_active": n_active,
    }


def calculate_all_budgets(
    df,  # pandas DataFrame — transactions.parquet shape
    inflation_rate: float = 0.03,
) -> list[dict]:
    """
    Run budget calculation for every eligible category in the DataFrame.

    `df` must have columns: amount (numeric), category_id, transaction_date.
    Returns a list of dicts (one per category), sorted by recommended desc.
    """
    import pandas as pd

    if df is None or df.empty:
        return []

    df = df.copy()
    df["amount"] = df["amount"].apply(_to_float)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)

    # All months present in the dataset, sorted
    all_months = sorted(df["month"].dropna().unique().tolist())

    # Monthly spend per category (debits only)
    spending = df[df["amount"] < 0].copy()
    spending["amount"] = spending["amount"].abs()

    monthly_by_cat = (
        spending
        .groupby(["category_id", "month"])["amount"]
        .sum()
        .reset_index()
    )

    results = []

    for cat_id in spending["category_id"].dropna().unique():
        cat_rows = monthly_by_cat[monthly_by_cat["category_id"] == cat_id]
        monthly_totals = dict(zip(cat_rows["month"], cat_rows["amount"]))

        result = calculate_category_budget(
            category_id=cat_id,
            monthly_totals=monthly_totals,
            all_months=all_months,
            inflation_rate=inflation_rate,
        )

        if result is not None:
            results.append(result)

    return sorted(results, key=lambda x: x["recommended"], reverse=True)
