from pydantic import BaseModel


class SemanticType(BaseModel):
    semantic_type_id: str

    name: str

    is_terminal_spending: bool

    requires_allocation: bool

    exclude_from_spending_reports: bool

    is_income: bool

    is_transfer: bool