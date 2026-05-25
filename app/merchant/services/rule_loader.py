from pathlib import Path

import yaml

from app.merchant.models.merchant_rule import (
    MerchantRule,
)


RULES_PATH = Path(
    "app/merchant/rules/"
    "merchant_rules.yaml"
)


def load_merchant_rules():

    with open(
        RULES_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(
            file
        )

    return [
        MerchantRule(**rule)
        for rule
        in data["rules"]
    ]