import yaml


CATEGORY_RULES_PATH = (
    "app/category/rules/"
    "category_rules.yaml"
)


def load_available_categories(
) -> list[str]:

    with open(
        CATEGORY_RULES_PATH,
        "r",
    ) as file:

        rules_config = (
            yaml.safe_load(file)
        )

    categories = set()

    for rule in rules_config[
        "rules"
    ]:

        categories.add(
            rule["category_id"]
        )

    categories.add(
        "uncategorized"
    )

    return sorted(
        list(categories)
    )