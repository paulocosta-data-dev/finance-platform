from app.category.services.category_loader import (
    load_category_rules,
)
from app.category.services.category_matcher import (
    category_rule_matches,
)
from app.domain.transactions import (
    Transaction,
)


def detect_category(
    transaction: Transaction,
) -> str:

    rules = (
        load_category_rules()
    )

    for rule in rules:

        if not rule.enabled:
            continue

        if category_rule_matches(
            transaction,
            rule,
        ):

            return (
                rule.category_id
            )

    return "uncategorized"