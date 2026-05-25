import unittest
from unittest.mock import patch

import pandas as pd


def _make_df(entity: str, amount: float, count: int) -> pd.DataFrame:
    rows = [
        {
            "entity_name": entity,
            "amount": amount,
            "transaction_date": f"2024-{i + 1:02d}-15",
        }
        for i in range(count)
    ]
    return pd.DataFrame(rows)


class TestRecurringDetection(unittest.TestCase):

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_entity_with_3_occurrences_is_detected(self, mock_load, _):
        mock_load.return_value = _make_df("spotify", -9.99, 3)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["entity_name"], "spotify")
        self.assertEqual(result[0]["occurrences"], 3)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_entity_with_2_occurrences_is_excluded(self, mock_load, _):
        mock_load.return_value = _make_df("netflix", -14.99, 2)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_internal_transfer_is_excluded(self, mock_load, _):
        mock_load.return_value = _make_df("internal_transfer", -500, 5)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_peer_transfer_is_excluded(self, mock_load, _):
        mock_load.return_value = _make_df("peer_transfer", -200, 4)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={"electricity": {"status": "confirmed"}},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_confirmed_override_is_skipped(self, mock_load, _):
        mock_load.return_value = _make_df("electricity", -80, 4)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={"gym": {"status": "ignored"}},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_ignored_override_is_skipped(self, mock_load, _):
        mock_load.return_value = _make_df("gym", -45, 4)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_average_amount_calculated_correctly(self, mock_load, _):
        rows = [
            {"entity_name": "gym", "amount": -40, "transaction_date": "2024-01-15"},
            {"entity_name": "gym", "amount": -50, "transaction_date": "2024-02-15"},
            {"entity_name": "gym", "amount": -60, "transaction_date": "2024-03-15"},
        ]
        mock_load.return_value = pd.DataFrame(rows)
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["average_amount"], 50.0)

    @patch(
        "app.category.services.recurring_detection_service.get_override_lookup",
        return_value={},
    )
    @patch("app.category.services.recurring_detection_service.load_transactions")
    def test_empty_dataframe_returns_empty_list(self, mock_load, _):
        mock_load.return_value = pd.DataFrame(
            columns=["entity_name", "amount", "transaction_date"]
        )
        from app.category.services.recurring_detection_service import (
            detect_recurring_transactions,
        )
        result = detect_recurring_transactions()
        self.assertEqual(result, [])
