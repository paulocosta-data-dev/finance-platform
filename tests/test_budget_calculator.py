"""
Unit tests for app/budget/services/budget_calculator.py
All tests use synthetic data — no file I/O.
"""

import unittest
from app.budget.services.budget_calculator import (
    EXCLUDED_CATEGORIES,
    _linear_slope,
    build_monthly_series,
    calculate_all_budgets,
    calculate_category_budget,
)


def _make_df(rows):
    """Build a minimal DataFrame from list of (date_str, category, amount)."""
    import pandas as pd
    return pd.DataFrame(rows, columns=["transaction_date", "category_id", "amount"])


MONTHS_10 = [f"2024-{str(m).zfill(2)}" for m in range(1, 11)]


class TestBuildMonthlySeries(unittest.TestCase):

    def test_all_present(self):
        totals = {"2024-01": 100.0, "2024-02": 200.0}
        series = build_monthly_series(totals, ["2024-01", "2024-02"])
        self.assertEqual(series, [100.0, 200.0])

    def test_fills_zeros_for_missing(self):
        totals = {"2024-03": 150.0}
        series = build_monthly_series(totals, ["2024-01", "2024-02", "2024-03"])
        self.assertEqual(series, [0.0, 0.0, 150.0])

    def test_empty_totals(self):
        series = build_monthly_series({}, MONTHS_10)
        self.assertEqual(series, [0.0] * 10)


class TestLinearSlope(unittest.TestCase):

    def test_flat_series_returns_zero(self):
        self.assertAlmostEqual(_linear_slope([50.0] * 6), 0.0, places=5)

    def test_rising_series_positive_slope(self):
        slope = _linear_slope([10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertGreater(slope, 0)

    def test_falling_series_negative_slope(self):
        slope = _linear_slope([50.0, 40.0, 30.0, 20.0, 10.0])
        self.assertLess(slope, 0)

    def test_too_few_points_returns_zero(self):
        self.assertEqual(_linear_slope([100.0, 200.0]), 0.0)

    def test_single_point_returns_zero(self):
        self.assertEqual(_linear_slope([999.0]), 0.0)


class TestCalculateCategoryBudget(unittest.TestCase):

    def test_excluded_category_returns_none(self):
        for cat in EXCLUDED_CATEGORIES:
            result = calculate_category_budget(cat, {"2024-01": 100.0}, ["2024-01"])
            self.assertIsNone(result)

    def test_no_spend_returns_none(self):
        result = calculate_category_budget("groceries", {}, MONTHS_10)
        self.assertIsNone(result)

    def test_stable_monthly_classified_recurring_fixed(self):
        # Same amount every month → cv=0, frequency=1.0 → recurring_fixed
        totals = {m: 80.0 for m in MONTHS_10}
        result = calculate_category_budget("telecom", totals, MONTHS_10)
        self.assertEqual(result["classification"], "recurring_fixed")
        self.assertEqual(result["frequency"], 1.0)

    def test_variable_frequent_classified_recurring_variable(self):
        # 6 active months, cv=0.46 → recurring_variable (cv 0.20–0.50, freq >= 0.40)
        amounts = [100, 200, 50, 0, 150, 0, 80, 0, 120, 0]
        totals = {m: v for m, v in zip(MONTHS_10, amounts) if v > 0}
        result = calculate_category_budget("groceries", totals, MONTHS_10)
        self.assertEqual(result["classification"], "recurring_variable")

    def test_occasional_category(self):
        # Only 2 out of 10 months → frequency=0.2 → occasional
        totals = {"2024-03": 200.0, "2024-08": 180.0}
        result = calculate_category_budget("restaurant", totals, MONTHS_10)
        self.assertEqual(result["classification"], "occasional")
        self.assertAlmostEqual(result["frequency"], 0.2)

    def test_inflation_applied(self):
        totals = {m: 100.0 for m in MONTHS_10}
        r0 = calculate_category_budget("telecom", totals, MONTHS_10, inflation_rate=0.0)
        r3 = calculate_category_budget("telecom", totals, MONTHS_10, inflation_rate=0.03)
        self.assertGreater(r3["recommended"], r0["recommended"])

    def test_positive_trend_increases_budget(self):
        # Rising series → trend_monthly > 0 → recommended higher
        flat = {m: 100.0 for m in MONTHS_10}
        rising = {m: 80 + i * 10 for i, m in enumerate(MONTHS_10)}
        r_flat = calculate_category_budget("groceries", flat, MONTHS_10)
        r_rising = calculate_category_budget("groceries", rising, MONTHS_10)
        self.assertGreater(r_rising["recommended"], r_flat["recommended"])

    def test_negative_trend_does_not_reduce_below_mean(self):
        # Falling series → trend_monthly < 0 → trend_adjustment = 0, budget ≥ mean
        totals = {m: 100 - i * 5 for i, m in enumerate(MONTHS_10)}
        result = calculate_category_budget("groceries", totals, MONTHS_10)
        self.assertGreaterEqual(result["recommended"], result["mean_overall"])

    def test_result_keys_present(self):
        totals = {"2024-01": 50.0}
        result = calculate_category_budget("groceries", totals, ["2024-01"])
        required = {
            "category_id", "recommended", "mean_overall", "classification",
            "frequency", "trend_monthly", "inflation_rate",
            "n_months_data", "n_months_active",
        }
        self.assertTrue(required.issubset(result.keys()))


class TestCalculateAllBudgets(unittest.TestCase):

    def test_empty_dataframe_returns_empty(self):
        import pandas as pd
        result = calculate_all_budgets(pd.DataFrame())
        self.assertEqual(result, [])

    def test_excludes_uncategorized_and_savings(self):
        df = _make_df([
            ("2024-01-15", "uncategorized", -50.0),
            ("2024-01-15", "savings", -500.0),
            ("2024-01-15", "groceries", -80.0),
        ])
        result = calculate_all_budgets(df)
        cats = [r["category_id"] for r in result]
        self.assertNotIn("uncategorized", cats)
        self.assertNotIn("savings", cats)
        self.assertIn("groceries", cats)

    def test_sorted_by_recommended_descending(self):
        df = _make_df([
            ("2024-01-01", "groceries", -200.0),
            ("2024-01-02", "telecom", -50.0),
            ("2024-01-03", "restaurant", -80.0),
        ])
        result = calculate_all_budgets(df)
        recommended = [r["recommended"] for r in result]
        self.assertEqual(recommended, sorted(recommended, reverse=True))

    def test_decimal_amounts_handled(self):
        from decimal import Decimal
        df = _make_df([
            ("2024-01-10", "groceries", Decimal("-120.50")),
            ("2024-02-10", "groceries", Decimal("-95.00")),
        ])
        result = calculate_all_budgets(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["category_id"], "groceries")


if __name__ == "__main__":
    unittest.main()
