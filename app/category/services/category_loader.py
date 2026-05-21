from pathlib import Path

import yaml

from app.category.models.category_rule import (
    CategoryRule,
)


RULES_PATH = Path(
    "app/category/rules/"
    "category_rules.yaml"
)


def load_category_rules(
) -> list[CategoryRule]:

    with open(
        RULES_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(file)

    rules = [
        CategoryRule(**rule)
        for rule in data["rules"]
    ]

    return sorted(
        rules,
        key=lambda rule: (
            rule.priority
        ),
        reverse=True,
    )