from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    category_id: str

    name: str

    parent_category_id: Optional[str] = None

    is_active: bool = True

    created_at: datetime