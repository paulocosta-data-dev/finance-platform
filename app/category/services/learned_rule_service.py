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

    with open(LEARNED_RULES_PATH, "w") as file:
        yaml.dump(
            {"rules": []},
            file,
            sort_keys=False,
        )


def load_learned_rules() -> dict:

    _ensure_learned_rules_file()

    with open(LEARNED_RULES_PATH, "r") as file:
        return yaml.safe_load(file)


def _save_rules(rules: list) -> None:

    with open(LEARNED_RULES_PATH, "w") as file:
        yaml.dump(
            {"rules": rules},
            file,
            sort_keys=False,
        )


def append_learned_rule(
    description: str,
    category_id: str,
) -> None:
    """Add or update a learned rule.

    If a rule already exists for this description (same pattern),
    its category_id is updated in-place rather than creating a
    duplicate. Disabled rules are re-enabled when updated.
    """

    rules_config = load_learned_rules()
    existing_rules = rules_config.get("rules", []) or []

    normalized_rule_id = (
        "learned_"
        + description.lower().replace(" ", "_")[:50]
    )

    pattern = description.lower()

    # Update existing rule if same pattern already present
    for rule in existing_rules:
        if rule.get("pattern") == pattern:
            rule["category_id"] = category_id
            rule["confidence"] = 0.99
            rule["enabled"] = True
            _save_rules(existing_rules)
            return

    new_rule = {
        "rule_id": normalized_rule_id,
        "match_type": "contains",
        "pattern": pattern,
        "category_id": category_id,
        "confidence": 0.99,
        "enabled": True,
    }

    existing_rules.append(new_rule)
    _save_rules(existing_rules)


def delete_learned_rule(rule_id: str) -> bool:
    """Remove a rule by rule_id. Returns True if found and removed."""

    rules_config = load_learned_rules()
    rules = rules_config.get("rules", []) or []

    new_rules = [r for r in rules if r.get("rule_id") != rule_id]

    if len(new_rules) == len(rules):
        return False

    _save_rules(new_rules)
    return True


def set_rule_enabled(rule_id: str, enabled: bool) -> bool:
    """Enable or disable a rule. Returns True if found."""

    rules_config = load_learned_rules()
    rules = rules_config.get("rules", []) or []

    for rule in rules:
        if rule.get("rule_id") == rule_id:
            rule["enabled"] = enabled
            _save_rules(rules)
            return True

    return False


def get_conflicts() -> list:
    """Return groups of rules that share the same pattern
    but map to different categories.

    Each item: {"pattern": str, "rules": [rule_dict, ...]}
    """

    rules_config = load_learned_rules()
    rules = rules_config.get("rules", []) or []

    from collections import defaultdict
    by_pattern = defaultdict(list)

    for rule in rules:
        pattern = rule.get("pattern", "")
        by_pattern[pattern].append(rule)

    conflicts = []

    for pattern, group in by_pattern.items():
        categories = {r.get("category_id") for r in group}
        if len(categories) > 1:
            conflicts.append({"pattern": pattern, "rules": group})

    return conflicts
