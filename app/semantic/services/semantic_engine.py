from app.semantic.models.semantic_match import (
    SemanticMatchResult,
)
from app.domain.transactions import (
    Transaction,
)
from app.semantic.services.rule_loader import (
    load_semantic_rules,
)
from app.semantic.services.rule_matcher import (
    rule_matches,
)


def detect_semantic_match(
    transaction: Transaction,
) -> SemanticMatchResult:

    rules = (
        load_semantic_rules()
    )

    for rule in rules:

        if not rule.enabled:
            continue

        if rule_matches(
            transaction,
            rule,
        ):

            return (
                SemanticMatchResult(
                    matched=True,
                    semantic_type_id=(
                        rule.semantic_type_id
                    ),
                    matched_rule_id=(
                        rule.rule_id
                    ),
                    confidence=(
                        rule.confidence
                    ),
                    priority=(
                        rule.priority
                    ),
                )
            )

    return SemanticMatchResult(
        matched=False,
        semantic_type_id="UNKNOWN",
        matched_rule_id=None,
        confidence=0.0,
        priority=0,
    )