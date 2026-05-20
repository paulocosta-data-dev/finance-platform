from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import AccountTypeEnum


class Account(BaseModel):
    account_id: str

    institution_name: str

    account_name: str

    account_type: AccountTypeEnum

    currency: str

    is_internal: bool = True

    is_active: bool = True

    created_at: datetime