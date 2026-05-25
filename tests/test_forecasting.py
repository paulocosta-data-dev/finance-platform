import unittest

from app.cashflow.services.forecasting_models import (
    forecast_behavioral_amount,
    forecast_fixed_recurring_amount,
)


def _txs(amounts: list, date: str = "2024-01-15") -> list[dict]:
    return [{"amount": a, "transaction_date": date} for a in amounts]


class TestForecastFixedRecurring(unittest.TestCase):

    def test_monthly_cadence_no_multiplier(self):
        result = forecast_fixed_recurring_amount(_txs([-100, -100, -100]), "monthly")
        self.assertEqual(result, 100.0)

    def test_weekly_cadence_multiplies_by_4(self):
        result = forecast_fixed_recurring_amount(_txs([-50, -50]), "weekly")
        self.assertEqual(result, 200.0)

    def test_biweekly_cadence_multiplies_by_2(self):
        result = forecast_fixed_recurring_amount(_txs([-100]), "biweekly")
        self.assertEqual(result, 200.0)

    def test_quarterly_cadence_divides_by_3(self):
        result = forecast_fixed_recurring_amount(_txs([-300]), "quarterly")
        self.assertAlmostEqual(result, 100.0, places=2)

    def test_yearly_cadence_divides_by_12(self):
        result = forecast_fixed_recurring_amount(_txs([-1200]), "yearly")
        self.assertEqual(result, 100.0)

    def test_debit_amounts_use_absolute_value(self):
        result = forecast_fixed_recurring_amount(_txs([-200, -200]), "monthly")
        self.assertEqual(result, 200.0)

    def test_unknown_cadence_uses_multiplier_1(self):
        result = forecast_fixed_recurring_amount(_txs([-150]), "unknown_cadence")
        self.assertEqual(result, 150.0)

    def test_average_of_varying_amounts(self):
        result = forecast_fixed_recurring_amount(_txs([-100, -200]), "monthly")
        self.assertEqual(result, 150.0)


class TestForecastBehavioral(unittest.TestCase):

    def test_empty_transactions_returns_zero(self):
        result = forecast_behavioral_amount([])
        self.assertEqual(result, 0)

    def test_single_month_sums_all_amounts(self):
        data = [
            {"amount": -50, "transaction_date": "2024-01-10"},
            {"amount": -30, "transaction_date": "2024-01-20"},
        ]
        result = forecast_behavioral_amount(data)
        self.assertEqual(result, 80.0)

    def test_average_across_two_months(self):
        data = [
            {"amount": -100, "transaction_date": "2024-01-10"},
            {"amount": -200, "transaction_date": "2024-02-10"},
        ]
        result = forecast_behavioral_amount(data)
        self.assertEqual(result, 150.0)

    def test_uses_absolute_values_for_debits(self):
        data = [{"amount": -300, "transaction_date": "2024-01-15"}]
        result = forecast_behavioral_amount(data)
        self.assertEqual(result, 300.0)

    def test_three_months_average(self):
        data = [
            {"amount": -60, "transaction_date": "2024-01-10"},
            {"amount": -90, "transaction_date": "2024-02-10"},
            {"amount": -120, "transaction_date": "2024-03-10"},
        ]
        result = forecast_behavioral_amount(data)
        self.assertEqual(result, 90.0)
