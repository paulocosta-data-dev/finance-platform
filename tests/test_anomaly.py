"""
Unit tests for app/anomaly/services/anomaly_service.py
All tests use synthetic DataFrames — no file I/O.
"""

import unittest
import pandas as pd
from app.anomaly.services.anomaly_service import (
    MIN_HISTORY_COUNT,
    build_category_stats,
    flag_anomalies,
)


def _make_df(rows):
    return pd.DataFrame(rows, columns=["category_id", "amount"])


def _cat_rows(category, amounts):
    return [{"category_id": category, "amount": -abs(a)} for a in amounts]


class TestBuildCategoryStats(unittest.TestCase):

    def test_empty_df_returns_empty(self):
        self.assertEqual(build_category_stats(pd.DataFrame()), {})

    def test_none_returns_empty(self):
        self.assertEqual(build_category_stats(None), {})

    def test_skips_categories_below_min_count(self):
        rows = _cat_rows("groceries", [50.0] * (MIN_HISTORY_COUNT - 1))
        df = _make_df(rows)
        stats = build_category_stats(df)
        self.assertNotIn("groceries", stats)

    def test_includes_categories_at_min_count(self):
        rows = _cat_rows("groceries", [50.0] * MIN_HISTORY_COUNT)
        df = _make_df(rows)
        stats = build_category_stats(df)
        self.assertIn("groceries", stats)

    def test_credits_not_included(self):
        # Positive amounts = credits, should be ignored
        rows = [{"category_id": "salary", "amount": 2000.0}] * 10
        df = _make_df(rows)
        stats = build_category_stats(df)
        self.assertNotIn("salary", stats)

    def test_mean_and_std_computed_correctly(self):
        amounts = [100.0, 100.0, 100.0, 100.0, 100.0]
        df = _make_df(_cat_rows("telecom", amounts))
        stats = build_category_stats(df)
        self.assertAlmostEqual(stats["telecom"]["mean"], 100.0)
        self.assertAlmostEqual(stats["telecom"]["std"], 0.0)

    def test_returns_required_keys(self):
        df = _make_df(_cat_rows("groceries", [40, 60, 50, 55, 45]))
        stats = build_category_stats(df)
        self.assertIn("count", stats["groceries"])
        self.assertIn("mean", stats["groceries"])
        self.assertIn("std", stats["groceries"])

    def test_count_correct(self):
        df = _make_df(_cat_rows("groceries", [50.0] * 8))
        stats = build_category_stats(df)
        self.assertEqual(stats["groceries"]["count"], 8)


class TestFlagAnomalies(unittest.TestCase):

    def _base_stats(self, mean=50.0, std=10.0, count=10):
        return {"groceries": {"mean": mean, "std": std, "count": count}}

    def test_empty_df_returns_empty(self):
        result = flag_anomalies(pd.DataFrame(), {})
        self.assertTrue(result.empty)

    def test_normal_amount_not_flagged(self):
        df = _make_df([{"category_id": "groceries", "amount": -55.0}])
        result = flag_anomalies(df, self._base_stats())
        self.assertFalse(result.iloc[0]["is_anomaly"])

    def test_medium_anomaly_flagged(self):
        # amount > mean + 2*std = 50 + 20 = 70; use 75
        df = _make_df([{"category_id": "groceries", "amount": -75.0}])
        result = flag_anomalies(df, self._base_stats())
        self.assertTrue(result.iloc[0]["is_anomaly"])
        self.assertEqual(result.iloc[0]["anomaly_severity"], "medium")

    def test_high_anomaly_flagged(self):
        # amount > mean + 3*std = 50 + 30 = 80; use 90
        df = _make_df([{"category_id": "groceries", "amount": -90.0}])
        result = flag_anomalies(df, self._base_stats())
        self.assertTrue(result.iloc[0]["is_anomaly"])
        self.assertEqual(result.iloc[0]["anomaly_severity"], "high")

    def test_credit_never_flagged(self):
        # Positive amount — should never be flagged regardless of size
        df = _make_df([{"category_id": "groceries", "amount": 9999.0}])
        result = flag_anomalies(df, self._base_stats())
        self.assertFalse(result.iloc[0]["is_anomaly"])

    def test_zero_std_never_flags(self):
        # All historical amounts were identical → std=0 → never flag
        stats = {"groceries": {"mean": 50.0, "std": 0.0, "count": 10}}
        df = _make_df([{"category_id": "groceries", "amount": -9999.0}])
        result = flag_anomalies(df, stats)
        self.assertFalse(result.iloc[0]["is_anomaly"])

    def test_no_stats_for_category_not_flagged(self):
        df = _make_df([{"category_id": "unknown_cat", "amount": -9999.0}])
        result = flag_anomalies(df, {})
        self.assertFalse(result.iloc[0]["is_anomaly"])

    def test_columns_always_added(self):
        df = _make_df([{"category_id": "groceries", "amount": -10.0}])
        result = flag_anomalies(df, {})
        self.assertIn("is_anomaly", result.columns)
        self.assertIn("anomaly_severity", result.columns)

    def test_mixed_rows_flagged_correctly(self):
        stats = self._base_stats(mean=50.0, std=10.0)
        df = _make_df([
            {"category_id": "groceries", "amount": -55.0},   # normal
            {"category_id": "groceries", "amount": -75.0},   # medium
            {"category_id": "groceries", "amount": -95.0},   # high
        ])
        result = flag_anomalies(df, stats)
        self.assertFalse(result.iloc[0]["is_anomaly"])
        self.assertEqual(result.iloc[1]["anomaly_severity"], "medium")
        self.assertEqual(result.iloc[2]["anomaly_severity"], "high")


if __name__ == "__main__":
    unittest.main()
