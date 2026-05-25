from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Allocation(BaseModel):
    allocation_id: str

    transaction_id: str

    category_id: str

    amount: Decimal

    allocation_note: Optional[str] = None

    created_by: str

    created_at: datetime