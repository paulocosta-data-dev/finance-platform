from app.domain.transactions import (
    Transaction,
)
from app.semantic.models.semantic_rule import (
    SemanticRule,
)


def match_description(
    transaction: Transaction,
    rule: SemanticRule,
) -> bool:

    description = (
        transaction
        .normalized_description
    )

    conditions = (
        rule.match
        .description_contains
    )

    if not conditions:
        return True

    return any(
        value in description
        for value in conditions
    )


def match_direction(
    transaction: Transaction,
    rule: SemanticRule,
) -> bool:

    conditions = (
        rule.match.direction
    )

    if not conditions:
        return True

    return (
        transaction.direction.value
        in conditions
    )


def rule_matches(
    transaction: Transaction,
    rule: SemanticRule,
) -> bool:

    return all([
        match_description(
            transaction,
            rule,
        ),
        match_direction(
            transaction,
            rule,
        ),
    ])