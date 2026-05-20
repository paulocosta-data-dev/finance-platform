from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ManualOverride(BaseModel):
    override_id: str

    transaction_id: str

    final_category_id: Optional[str] = None

    final_semantic_type_id: Optional[str] = None

    override_reason: Optional[str] = None

    created_by: str

    created_at: datetime

    is_active: bool = True

    superseded_override_id: Optional[str] = None