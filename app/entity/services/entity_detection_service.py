from app.entity.models.entity_match import (
    EntityMatchResult,
)

from app.merchant.services.merchant_engine import (
    detect_merchant,
)

from app.semantic.services.semantic_engine import (
    detect_semantic_match,
)


def detect_entity(
    transaction,
) -> EntityMatchResult:

    merchant_result = (
        detect_merchant(
            transaction
            .normalized_description
        )
    )

    if merchant_result.matched:

        return (
            EntityMatchResult(
                matched=True,
                entity_name=(
                    merchant_result
                    .merchant_name
                ),
                entity_type="merchant",
                confidence=(
                    merchant_result
                    .confidence
                ),
            )
        )

    semantic_result = (
        detect_semantic_match(
            transaction
        )
    )

    semantic_type = (
        semantic_result
        .semantic_type_id
    )

    if semantic_type in {
        "INTERNAL_TRANSFER",
        "PEER_TRANSFER",
    }:

        return (
            EntityMatchResult(
                matched=True,
                entity_name=(
                    semantic_type
                    .lower()
                ),
                entity_type=(
                    "financial_flow"
                ),
                confidence=(
                    semantic_result
                    .confidence
                ),
            )
        )

    return EntityMatchResult(
        matched=False,
        entity_name=None,
        entity_type=None,
        confidence=0.0,
    )