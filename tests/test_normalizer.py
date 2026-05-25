import unittest
from decimal import Decimal

from app.domain.enums import DirectionEnum
from app.ingestion.normalizer import determine_direction, normalize_description


class TestNormalizeDescription(unittest.TestCase):

    def test_converts_to_lowercase(self):
        self.assertEqual(normalize_description("CONTINENTE"), "continente")

    def test_replaces_forward_slash_with_space(self):
        self.assertEqual(normalize_description("PINGO/DOCE"), "pingo doce")

    def test_replaces_dot_with_space(self):
        self.assertEqual(normalize_description("PINGO.DOCE"), "pingo doce")

    def test_collapses_multiple_spaces(self):
        self.assertEqual(normalize_description("CONTINENTE  FOOD"), "continente food")

    def test_strips_leading_and_trailing_whitespace(self):
        self.assertEqual(normalize_description("  CONTINENTE  "), "continente")

    def test_combined_slash_dot_and_spaces(self):
        self.assertEqual(
            normalize_description("CONTINENTE  /  FOOD."),
            "continente food",
        )

    def test_empty_string_returns_empty(self):
        self.assertEqual(normalize_description(""), "")

    def test_already_normalized_string_unchanged(self):
        self.assertEqual(normalize_description("continente"), "continente")


class TestDetermineDirection(unittest.TestCase):

    def test_negative_amount_is_debit(self):
        self.assertEqual(
            determine_direction(Decimal("-10.50")),
            DirectionEnum.DEBIT,
        )

    def test_positive_amount_is_credit(self):
        self.assertEqual(
            determine_direction(Decimal("100.00")),
            DirectionEnum.CREDIT,
        )

    def test_zero_is_credit(self):
        self.assertEqual(
            determine_direction(Decimal("0")),
            DirectionEnum.CREDIT,
        )

    def test_large_debit(self):
        self.assertEqual(
            determine_direction(Decimal("-9999.99")),
            DirectionEnum.DEBIT,
        )

    def test_small_positive_credit(self):
        self.assertEqual(
            determine_direction(Decimal("0.01")),
            DirectionEnum.CREDIT,
        )
