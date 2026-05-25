from pathlib import Path

import yaml


ENTITY_REGISTRY_PATH = (
    "app/semantic/entities/"
    "entity_registry.yaml"
)


def load_entity_registry():

    path = Path(
        ENTITY_REGISTRY_PATH
    )

    if not path.exists():

        return {}

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(
            file
        )

    if not data:

        return {}

    return data.get(
        "entities",
        {},
    )