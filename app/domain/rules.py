from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Rule(BaseModel):
    rule_id: str

    name: str

    priority: int

    is_enabled: bool = True

    match_field: str

    match_operator: str

    match_value: str

    assigned_category_id: Optional[str] = None

    assigned_semantic_type_id: Optional[str] = None

    confidence_score: Decimal

    created_at: datetime

    last_matched_at: Optional[datetime] = None

    match_count: int = 0


class RuleMatch(BaseModel):
    rule_match_id: str

    transaction_id: str

    rule_id: str

    suggested_category_id: Optional[str] = None

    suggested_semantic_type_id: Optional[str] = None

    confidence_score: Decimal

    match_reason: str

    matched_at: datetime