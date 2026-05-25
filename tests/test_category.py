import unittest

from app.category.models.category_rule import CategoryMatchConditions, CategoryRule
from app.category.services.category_matcher import category_rule_matches
from tests.helpers import make_transaction


def make_rule(
    category_id: str,
    description_contains: list[str] | None = None,
    semantic_type_ids: list[str] | None = None,
    priority: int = 100,
    enabled: bool = True,
) -> CategoryRule:

    return CategoryRule(
        rule_id=f"rule-{category_id}",
        enabled=enabled,
        priority=priority,
        category_id=category_id,
        confidence=0.9,
        match=CategoryMatchConditions(
            semantic_type_ids=semantic_type_ids or [],
            description_contains=description_contains or [],
        ),
    )


class TestCategoryRuleMatches(unittest.TestCase):

    def test_empty_conditions_match_any_transaction(self):
        tx = make_transaction(normalized_description="continente", semantic_type_id="PURCHASE")
        rule = make_rule("any_category")
        self.assertTrue(category_rule_matches(tx, rule))

    def test_description_keyword_present_matches(self):
        tx = make_transaction(normalized_description="continente supermercado")
        rule = make_rule("groceries", description_contains=["continente"])
        self.assertTrue(category_rule_matches(tx, rule))

    def test_description_keyword_absent_no_match(self):
        tx = make_transaction(normalized_description="meo internet servico")
        rule = make_rule("groceries", description_contains=["continente"])
        self.assertFalse(category_rule_matches(tx, rule))

    def test_semantic_type_matches(self):
        tx = make_transaction(semantic_type_id="SALARY")
        rule = make_rule("income", semantic_type_ids=["SALARY"])
        self.assertTrue(category_rule_matches(tx, rule))

    def test_semantic_type_no_match(self):
        tx = make_transaction(semantic_type_id="PURCHASE")
        rule = make_rule("income", semantic_type_ids=["SALARY"])
        self.assertFalse(category_rule_matches(tx, rule))

    def test_both_conditions_required_semantic_fails(self):
        tx = make_transaction(
            normalized_description="continente supermercado",
            semantic_type_id="SALARY",
        )
        rule = make_rule(
            "groceries",
            description_contains=["continente"],
            semantic_type_ids=["PURCHASE"],
        )
        self.assertFalse(category_rule_matches(tx, rule))

    def test_both_conditions_required_description_fails(self):
        tx = make_transaction(
            normalized_description="meo internet",
            semantic_type_id="PURCHASE",
        )
        rule = make_rule(
            "groceries",
            description_contains=["continente"],
            semantic_type_ids=["PURCHASE"],
        )
        self.assertFalse(category_rule_matches(tx, rule))

    def test_both_conditions_pass(self):
        tx = make_transaction(
            normalized_description="continente supermercado",
            semantic_type_id="PURCHASE",
        )
        rule = make_rule(
            "groceries",
            description_contains=["continente"],
            semantic_type_ids=["PURCHASE"],
        )
        self.assertTrue(category_rule_matches(tx, rule))

    def test_partial_keyword_match_within_description(self):
        tx = make_transaction(normalized_description="pingo doce algues")
        rule = make_rule("groceries", description_contains=["pingo"])
        self.assertTrue(category_rule_matches(tx, rule))

    def test_multiple_keywords_any_one_suffices(self):
        tx = make_transaction(normalized_description="meo servico telecomunicacoes")
        rule = make_rule("telecom", description_contains=["meo", "nos", "vodafone"])
        self.assertTrue(category_rule_matches(tx, rule))
