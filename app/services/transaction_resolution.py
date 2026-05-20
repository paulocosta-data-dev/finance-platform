from app.domain.allocations import Allocation
from app.domain.overrides import ManualOverride
from app.domain.rules import RuleMatch
from app.domain.transactions import Transaction


def resolve_transaction_state(
    transaction: Transaction,
    rule_match: RuleMatch | None = None,
    manual_override: ManualOverride | None = None,
    allocations: list[Allocation] | None = None,
) -> dict:
    """
    Resolves the final semantic state of a transaction.

    Precedence:
        allocations
            > manual override
                > rule match
                    > unresolved
    """

    allocations = allocations or []

    # --- Allocation wins ---
    if allocations:
        return {
            "resolution_source": "ALLOCATIONS",
            "resolved": True,
            "category_ids": [a.category_id for a in allocations],
            "semantic_type_id": transaction.semantic_type_id,
        }

    # --- Manual override wins ---
    if manual_override and manual_override.is_active:
        return {
            "resolution_source": "MANUAL_OVERRIDE",
            "resolved": True,
            "category_ids": (
                [manual_override.final_category_id]
                if manual_override.final_category_id
                else []
            ),
            "semantic_type_id": (
                manual_override.final_semantic_type_id
                or transaction.semantic_type_id
            ),
        }

    # --- Rule match fallback ---
    if rule_match:
        return {
            "resolution_source": "RULE_MATCH",
            "resolved": True,
            "category_ids": (
                [rule_match.suggested_category_id]
                if rule_match.suggested_category_id
                else []
            ),
            "semantic_type_id": (
                rule_match.suggested_semantic_type_id
                or transaction.semantic_type_id
            ),
        }

    # --- Unresolved fallback ---
    return {
        "resolution_source": "UNRESOLVED",
        "resolved": False,
        "category_ids": [],
        "semantic_type_id": transaction.semantic_type_id,
    }