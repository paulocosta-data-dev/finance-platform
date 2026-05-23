from datetime import datetime
from decimal import Decimal

from app.category.services.category_engine import (
    detect_category,
)

from app.domain.enums import (
    DirectionEnum,
)

from app.domain.enums import (
    ResolutionStatusEnum,
)

from app.domain.imports import (
    RawTransaction,
)

from app.domain.transactions import (
    Transaction,
)

from app.entity.services.entity_detection_service import (
    detect_entity,
)

from app.schema.versions import (
    CURRENT_TRANSACTION_SCHEMA_VERSION,
)

from app.semantic.services.semantic_engine import (
    detect_semantic_match,
)

from app.semantic.services.semantic_registry import (
    get_semantic_type,
)

from app.utils.hash import (
    generate_transaction_hash,
)


def normalize_description(
    description: str,
) -> str:

    return " ".join(
        description.strip()
        .lower()
        .replace("/", " ")
        .replace(".", " ")
        .split()
    )


def determine_direction(
    amount: Decimal,
) -> DirectionEnum:

    if amount < 0:

        return (
            DirectionEnum.DEBIT
        )

    return DirectionEnum.CREDIT


def normalize_raw_transaction(
    raw_transaction: RawTransaction,
    account_id: str,
) -> Transaction:

    amount = Decimal(
        raw_transaction.raw_amount
    )

    normalized_description = (
        normalize_description(
            raw_transaction
            .raw_description
        )
    )

    direction = determine_direction(
        amount
    )

    temp_transaction = (
        Transaction(
            transaction_id="temp",
            schema_version=(
                CURRENT_TRANSACTION_SCHEMA_VERSION
            ),
            raw_transaction_id=(
                raw_transaction
                .raw_transaction_id
            ),
            account_id=account_id,
            transaction_date=(
                datetime.fromisoformat(
                    raw_transaction
                    .raw_date
                ).date()
            ),
            booking_date=(
                datetime.fromisoformat(
                    raw_transaction
                    .raw_booking_date
                ).date()
            ),
            description=(
                raw_transaction
                .raw_description
            ),
            normalized_description=(
                normalized_description
            ),
            amount=amount,
            currency="EUR",
            direction=direction,
            semantic_type_id=(
                "UNKNOWN"
            ),
            category_id=(
                "uncategorized"
            ),
            matched_rule_id=None,
            semantic_confidence=0.0,
            resolution_status=(
                ResolutionStatusEnum
                .MANUAL_REVIEW_REQUIRED
            ),
            is_terminal_spending=False,
            entity_name=None,
            entity_type=None,
            entity_confidence=0.0,
            created_at=(
                datetime.now()
            ),
        )
    )

    semantic_match = (
        detect_semantic_match(
            transaction=(
                temp_transaction
            )
        )
    )

    temp_transaction.semantic_type_id = (
        semantic_match
        .semantic_type_id
    )

    semantic_type = (
        get_semantic_type(
            semantic_match
            .semantic_type_id
        )
    )

    category_id = detect_category(
        temp_transaction
    )

    entity_match = (
        detect_entity(
            temp_transaction
        )
    )

    transaction_id = (
        generate_transaction_hash(
            raw_transaction_id=(
                raw_transaction
                .raw_transaction_id
            )
        )
    )

    return Transaction(
        transaction_id=(
            transaction_id
        ),
        schema_version=(
            CURRENT_TRANSACTION_SCHEMA_VERSION
        ),
        raw_transaction_id=(
            raw_transaction
            .raw_transaction_id
        ),
        account_id=account_id,
        transaction_date=(
            datetime.fromisoformat(
                raw_transaction
                .raw_date
            ).date()
        ),
        booking_date=(
            datetime.fromisoformat(
                raw_transaction
                .raw_booking_date
            ).date()
        ),
        description=(
            raw_transaction
            .raw_description
        ),
        normalized_description=(
            normalized_description
        ),
        amount=amount,
        currency="EUR",
        direction=direction,
        semantic_type_id=(
            semantic_match
            .semantic_type_id
        ),
        category_id=category_id,
        matched_rule_id=(
            semantic_match
            .matched_rule_id
        ),
        semantic_confidence=(
            semantic_match
            .confidence
        ),
        resolution_status=(
            ResolutionStatusEnum
            .MANUAL_REVIEW_REQUIRED
        ),
        is_terminal_spending=(
            semantic_type
            .is_terminal_spending
        ),
        entity_name=(
            entity_match
            .entity_name
        ),
        entity_type=(
            entity_match
            .entity_type
        ),
        entity_confidence=(
            entity_match
            .confidence
        ),
        created_at=datetime.now(),
    )