from pydantic import BaseModel


class CategoryMatchConditions(
    BaseModel
):

    semantic_type_ids: (
        list[str]
    ) = []

    description_contains: (
        list[str]
    ) = []


class CategoryRule(
    BaseModel
):

    rule_id: str

    enabled: bool = True

    priority: int

    category_id: str

    confidence: float

    match: CategoryMatchConditions