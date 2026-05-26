"""
Persistence layer for calculated budgets.

Stores: the last run's results + the inflation rate used.
File: data/processed/budget.yaml

Schema:
    inflation_rate: 0.03
    calculated_at: "2025-05-26"
    budgets:
      groceries:
        recommended: 145
        mean_overall: 63.51
        classification: recurring_variable
        frequency: 0.38
        trend_monthly: 4.21
        n_months_data: 21
        n_months_active: 8
"""

import yaml
from datetime import date

from app.utils.paths import data_path

BUDGET_PATH = data_path("data/processed/budget.yaml")
DEFAULT_INFLATION_RATE = 0.03


def _ensure_budget_file() -> None:

    if BUDGET_PATH.exists():
        return

    BUDGET_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(BUDGET_PATH, "w") as f:
        yaml.dump(
            {
                "inflation_rate": DEFAULT_INFLATION_RATE,
                "calculated_at": None,
                "budgets": {},
            },
            f,
            sort_keys=False,
        )


def load_budgets() -> dict:
    """Return the full budget YAML dict. Creates the file if missing."""
    _ensure_budget_file()
    with open(BUDGET_PATH, "r") as f:
        return yaml.safe_load(f) or {}


def get_inflation_rate() -> float:
    data = load_budgets()
    return float(data.get("inflation_rate", DEFAULT_INFLATION_RATE))


def recalculate_budgets(inflation_rate: float | None = None) -> list[dict]:
    """
    Reload transactions, run the calculator, persist results.
    Returns the list of budget dicts.
    """
    import pandas as pd
    from app.budget.services.budget_calculator import calculate_all_budgets
    from app.utils.paths import data_path

    txn_path = data_path("data/processed/transactions.parquet")

    if not txn_path.exists():
        return []

    df = pd.read_parquet(txn_path)

    existing = load_budgets()
    rate = inflation_rate if inflation_rate is not None else float(
        existing.get("inflation_rate", DEFAULT_INFLATION_RATE)
    )

    results = calculate_all_budgets(df, inflation_rate=rate)

    budgets_dict = {r["category_id"]: {k: v for k, v in r.items() if k != "category_id"}
                   for r in results}

    with open(BUDGET_PATH, "w") as f:
        yaml.dump(
            {
                "inflation_rate": rate,
                "calculated_at": str(date.today()),
                "budgets": budgets_dict,
            },
            f,
            sort_keys=False,
        )

    return results


def get_budget_vs_actual(account_id: str = "__all__") -> list[dict]:
    """
    Join calculated budgets with current month actual spend.

    Returns list of dicts sorted by over-budget first:
        category_id, budget, actual, delta, over_budget, pct_used
    """
    import pandas as pd
    from app.cashflow.services.dashboard_service import (
        get_category_breakdown_current_month,
    )

    data = load_budgets()
    budgets = data.get("budgets", {})

    if not budgets:
        return []

    actuals = {
        row["category_id"]: row["total"]
        for row in get_category_breakdown_current_month(account_id=account_id)
    }

    result = []

    for cat_id, b in budgets.items():
        budget_amount = float(b.get("recommended", 0))
        actual_amount = float(actuals.get(cat_id, 0.0))
        delta = round(actual_amount - budget_amount, 2)
        pct_used = round(actual_amount / budget_amount * 100, 1) if budget_amount > 0 else 0.0

        result.append({
            "category_id": cat_id,
            "budget": budget_amount,
            "actual": actual_amount,
            "delta": delta,
            "over_budget": delta > 0,
            "pct_used": pct_used,
            "classification": b.get("classification", ""),
        })

    # Sort: over-budget first, then by pct_used descending
    result.sort(key=lambda x: (-int(x["over_budget"]), -x["pct_used"]))
    return result
