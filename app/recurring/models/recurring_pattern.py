from datetime import date

from pydantic import BaseModel


class RecurringPattern(
    BaseModel
):

    normalized_description: str

    occurrences: int

    average_amount: float

    semantic_type_id: str

    category_id: str

    first_seen: date

    last_seen: date

    average_interval_days: float

    cadence_type: str