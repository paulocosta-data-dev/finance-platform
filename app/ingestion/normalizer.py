from datetime import datetime
from decimal import Decimal

from app.domain.enums import DirectionEnum
from app.domain.enums import ResolutionStatusEnum
from app.domain.imports import RawTransaction
from app.domain.transactions import Transaction
from app.services.semantic_detection import detect_semantic_type
from app.services.semantic_registry import get_semantic_type
from app.utils.hash import generate_transaction_hash


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
        return DirectionEnum.DEBIT

    return DirectionEnum.CREDIT


def normalize_raw_transaction(
    raw_transaction: RawTransaction,
    account_id: str,
) -> Transaction:

    amount = Decimal(raw_transaction.raw_amount)

    normalized_description = normalize_description(
        raw_transaction.raw_description
    )

    direction = determine_direction(amount)

    temp_transaction = Transaction(
        transaction_id="temp",
        raw_transaction_id=raw_transaction.raw_transaction_id,
        account_id=account_id,
        transaction_date=datetime.fromisoformat(
            raw_transaction.raw_date
        ).date(),
        booking_date=datetime.fromisoformat(
            raw_transaction.raw_booking_date
        ).date(),
        description=raw_transaction.raw_description,
        normalized_description=normalized_description,
        amount=amount,
        currency="EUR",
        direction=direction,
        semantic_type_id="UNKNOWN",
        resolution_status=(
            ResolutionStatusEnum.MANUAL_REVIEW_REQUIRED
        ),
        is_terminal_spending=False,
        created_at=datetime.now(),
    )

    semantic_type_id = detect_semantic_type(
        transaction=temp_transaction
    )

    semantic_type = get_semantic_type(
        semantic_type_id
    )

    transaction_id = generate_transaction_hash(
        account_id=account_id,
        raw_date=raw_transaction.raw_date,
        raw_description=raw_transaction.raw_description,
        raw_amount=raw_transaction.raw_amount,
    )

    return Transaction(
        transaction_id=transaction_id,
        raw_transaction_id=raw_transaction.raw_transaction_id,
        account_id=account_id,
        transaction_date=datetime.fromisoformat(
            raw_transaction.raw_date
        ).date(),
        booking_date=datetime.fromisoformat(
            raw_transaction.raw_booking_date
        ).date(),
        description=raw_transaction.raw_description,
        normalized_description=normalized_description,
        amount=amount,
        currency="EUR",
        direction=direction,
        semantic_type_id=semantic_type_id,
        resolution_status=(
            ResolutionStatusEnum.MANUAL_REVIEW_REQUIRED
        ),
        is_terminal_spending=(
            semantic_type.is_terminal_spending
        ),
        created_at=datetime.now(),
    )