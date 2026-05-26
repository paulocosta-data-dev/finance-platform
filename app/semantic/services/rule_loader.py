from app.utils.paths import resource_path
import yaml

from app.semantic.models.semantic_rule import (
    SemanticRule,
)


RULES_PATH = resource_path(
    "app/semantic/rules/semantic_rules.yaml"
)


def load_semantic_rules(
) -> list[SemanticRule]:

    with open(
        RULES_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(file)

    rules = [
        SemanticRule(**rule)
        for rule in data["rules"]
    ]

    return sorted(
        rules,
        key=lambda rule: (
            rule.priority
        ),
        reverse=True,
    )