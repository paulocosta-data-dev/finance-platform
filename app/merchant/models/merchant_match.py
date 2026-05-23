from pydantic import BaseModel


class MerchantMatchResult(
    BaseModel
):

    matched: bool

    merchant_name: str | None

    confidence: float