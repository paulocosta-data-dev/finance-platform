from datetime import date, datetime
from decimal import Decimal

from app.domain.enums import DirectionEnum, ResolutionStatusEnum
from app.domain.transactions import Transaction


def make_transaction(
    description: str = "test transaction",
    normalized_description: str = "test transaction",
    semantic_type_id: str = "PURCHASE",
    amount: Decimal = Decimal("-10.00"),
    direction: DirectionEnum = DirectionEnum.DEBIT,
    category_id: str = "uncategorized",
) -> Transaction:

    return Transaction(
        transaction_id="test-id",
        schema_version=1,
        raw_transaction_id="raw-test-id",
        account_id="acc-001",
        transaction_date=date(2024, 1, 15),
        booking_date=date(2024, 1, 15),
        description=description,
        normalized_description=normalized_description,
        amount=amount,
        currency="EUR",
        direction=direction,
        semantic_type_id=semantic_type_id,
        category_id=category_id,
        matched_rule_id=None,
        semantic_confidence=0.0,
        resolution_status=ResolutionStatusEnum.MANUAL_REVIEW_REQUIRED,
        is_terminal_spending=False,
        entity_name=None,
        entity_type=None,
        entity_confidence=0.0,
        created_at=datetime(2024, 1, 15, 12, 0, 0),
    )
