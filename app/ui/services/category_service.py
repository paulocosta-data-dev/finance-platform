import yaml
from pathlib import Path


CATEGORIES_PATH = (
    Path(
        "config/categories.yaml"
    )
)


def ensure_categories_file():

    if not CATEGORIES_PATH.exists():

        CATEGORIES_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        default_categories = {
            "categories": [
                "uncategorized",
                "groceries",
                "restaurant",
                "telecom",
                "books",
                "pharmacy",
                "savings",
            ]
        }

        with open(
            CATEGORIES_PATH,
            "w",
        ) as file:

            yaml.safe_dump(
                default_categories,
                file,
                sort_keys=False,
            )


def load_available_categories(
) -> list[str]:

    ensure_categories_file()

    with open(
        CATEGORIES_PATH,
        "r",
    ) as file:

        config = yaml.safe_load(
            file
        )

    categories = config.get(
        "categories",
        [],
    )

    return sorted(
        categories
    )


def persist_category(
    category_name: str,
) -> None:

    ensure_categories_file()

    with open(
        CATEGORIES_PATH,
        "r",
    ) as file:

        config = yaml.safe_load(
            file
        )

    categories = config.get(
        "categories",
        [],
    )

    if (
        category_name
        not in categories
    ):

        categories.append(
            category_name
        )

    config[
        "categories"
    ] = sorted(
        categories
    )

    with open(
        CATEGORIES_PATH,
        "w",
    ) as file:

        yaml.safe_dump(
            config,
            file,
            sort_keys=False,
        )