import re

from app.domain.transactions import (
    Transaction,
)
from app.semantic.models.semantic_rule import (
    SemanticRule,
)


def match_description_contains(
    transaction: Transaction,
    rule: SemanticRule,
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


def match_description_startswith(
    transaction: Transaction,
    rule: SemanticRule,
) -> bool:

    conditions = (
        rule.match
        .description_startswith
    )

    if not conditions:
        return True

    description = (
        transaction
        .normalized_description
    )

    return any(
        description.startswith(
            value
        )
        for value in conditions
    )


def match_description_regex(
    transaction: Transaction,
    rule: SemanticRule,
) -> bool:

    conditions = (
        rule.match
        .description_regex
    )

    if not conditions:
        return True

    description = (
        transaction
        .normalized_description
    )

    return any(
        re.search(
            pattern,
            description,
        )
        for pattern in conditions
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
        match_description_contains(
            transaction,
            rule,
        ),
        match_description_startswith(
            transaction,
            rule,
        ),
        match_description_regex(
            transaction,
            rule,
        ),
        match_direction(
            transaction,
            rule,
        ),
    ])