from app.domain.semantic import (
    SemanticType,
)


SEMANTIC_TYPES = [

    SemanticType(
        semantic_type_id=(
            "UNKNOWN"
        ),
        name="Unknown",
        is_terminal_spending=False,
        requires_allocation=False,
        exclude_from_spending_reports=False,
        is_income=False,
        is_transfer=False,
    ),

    SemanticType(
        semantic_type_id=(
            "CARD_PURCHASE"
        ),
        name="Card Purchase",
        is_terminal_spending=True,
        requires_allocation=False,
        exclude_from_spending_reports=False,
        is_income=False,
        is_transfer=False,
    ),

    SemanticType(
        semantic_type_id=(
            "PEER_TRANSFER"
        ),
        name="Peer Transfer",
        is_terminal_spending=False,
        requires_allocation=False,
        exclude_from_spending_reports=True,
        is_income=False,
        is_transfer=True,
    ),

    SemanticType(
        semantic_type_id=(
            "SALARY"
        ),
        name="Salary",
        is_terminal_spending=False,
        requires_allocation=False,
        exclude_from_spending_reports=True,
        is_income=True,
        is_transfer=False,
    ),

    SemanticType(
        semantic_type_id=(
            "INTERNAL_TRANSFER"
        ),
        name="Internal Transfer",
        is_terminal_spending=False,
        requires_allocation=False,
        exclude_from_spending_reports=True,
        is_income=False,
        is_transfer=True,
    ),

    SemanticType(
        semantic_type_id=(
            "ATM_WITHDRAWAL"
        ),
        name="ATM Withdrawal",
        is_terminal_spending=True,
        requires_allocation=True,
        exclude_from_spending_reports=False,
        is_income=False,
        is_transfer=False,
    ),

    SemanticType(
        semantic_type_id=(
            "INTEREST_PAYMENT"
        ),
        name="Interest Payment",
        is_terminal_spending=False,
        requires_allocation=False,
        exclude_from_spending_reports=True,
        is_income=True,
        is_transfer=False,
    ),
]


SEMANTIC_TYPE_MAP = {

    semantic_type.semantic_type_id:
    semantic_type

    for semantic_type
    in SEMANTIC_TYPES
}


def get_semantic_type(
    semantic_type_id: str,
) -> SemanticType:

    return SEMANTIC_TYPE_MAP[
        semantic_type_id
    ]