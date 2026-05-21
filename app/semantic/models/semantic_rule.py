from typing import Optional

from pydantic import BaseModel


class RuleMatchConditions(
    BaseModel
):

    description_contains: (
        list[str]
    ) = []

    direction: list[str] = []


class SemanticRule(
    BaseModel
):

    rule_id: str

    enabled: bool = True

    priority: int

    semantic_type_id: str

    confidence: float

    match: RuleMatchConditions