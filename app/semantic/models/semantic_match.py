from pydantic import BaseModel


class SemanticMatchResult(
    BaseModel
):

    matched: bool

    semantic_type_id: str

    matched_rule_id: str | None

    confidence: float

    priority: int