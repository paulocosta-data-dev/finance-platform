from pathlib import Path

import yaml


LEARNED_RULES_PATH = Path(
    "data/processed/"
    "learned_category_rules.yaml"
)


def load_learned_rules(
) -> dict:

    with open(
        LEARNED_RULES_PATH,
        "r",
    ) as file:

        return yaml.safe_load(
            file
        )


def append_learned_rule(
    description: str,
    category_id: str,
) -> None:

    rules_config = (
        load_learned_rules()
    )

    normalized_rule_id = (
        description.lower()
        .replace(" ", "_")
        [:50]
    )

    new_rule = {
        "rule_id": (
            f"""
learned_
{normalized_rule_id}
"""
            .replace("\n", "")
        ),
        "match_type": (
            "contains"
        ),
        "pattern": (
            description.lower()
        ),
        "category_id": (
            category_id
        ),
        "confidence": 0.99,
    }

    existing_rules = (
        rules_config["rules"]
    )

    for rule in existing_rules:

        if (
            rule["pattern"]
            == description.lower()
        ):

            return

    existing_rules.append(
        new_rule
    )

    with open(
        LEARNED_RULES_PATH,
        "w",
    ) as file:

        yaml.dump(
            rules_config,
            file,
            sort_keys=False,
        )