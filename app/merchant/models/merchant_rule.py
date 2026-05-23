from pydantic import BaseModel


class MerchantRule(
    BaseModel
):

    merchant_name: str

    match_contains: (
        list[str]
    ) = []