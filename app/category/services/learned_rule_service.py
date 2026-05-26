from app.utils.paths import data_path
import yaml


LEARNED_RULES_PATH = data_path(
    "data/processed/learned_category_rules.yaml"
)


def _ensure_learned_rules_file() -> None:

    if LEARNED_RULES_PATH.exists():
        return

    LEARNED_RULES_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        LEARNED_RULES_PATH,
        "w",
    ) as file:

        yaml.dump(
            {"rules": []},
            file,
            sort_keys=False,
        )


def load_learned_rules(
) -> dict:

    _ensure_learned_rules_file()

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
        