from app.category.models.category_rule import (
    CategoryRule,
)
from app.domain.transactions import (
    Transaction,
)


def match_semantic_type(
    transaction: Transaction,
    rule: CategoryRule,
) -> bool:

    conditions = (
        rule.match
        .semantic_type_ids
    )

    if not conditions:
        return True

    return (
        transaction.semantic_type_id
        in conditions
    )


def match_description_contains(
    transaction: Transaction,
    rule: CategoryRule,
) -> bool:

    conditions = (
        rule.match
        .description_contains
    )

    if not conditions:
        return True

    description = (
        transaction
        .normalized_description
    )

    return any(
        value in description
        for value in conditions
    )


def category_rule_matches(
    transaction: Transaction,
    rule: CategoryRule,
) -> bool:

    return all([
        match_semantic_type(
            transaction,
            rule,
        ),
        match_description_contains(
            transaction,
            rule,
        ),
    ])