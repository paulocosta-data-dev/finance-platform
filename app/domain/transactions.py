from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.domain.enums import DirectionEnum
from app.domain.enums import (
    ResolutionStatusEnum,
)


class Transaction(BaseModel):

    transaction_id: str

    schema_version: int

    raw_transaction_id: str

    account_id: str

    transaction_date: date
    booking_date: date

    description: str
    normalized_description: str

    amount: Decimal

    currency: str

    direction: DirectionEnum

    semantic_type_id: str

    resolution_status: (
        ResolutionStatusEnum
    )

    is_terminal_spending: bool

    created_at: datetime