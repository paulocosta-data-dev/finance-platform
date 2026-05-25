from pydantic import BaseModel


class EntityMatchResult(
    BaseModel
):

    matched: bool

    entity_name: str | None

    entity_type: str | None

    confidence: float