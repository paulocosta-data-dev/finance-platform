from app.semantic.services.entity_registry_loader import (
    load_entity_registry,
)


def detect_entity(
    normalized_description: str,
):

    entity_registry = (
        load_entity_registry()
    )

    for (
        canonical_entity,
        entity_data,
    ) in (
        entity_registry.items()
    ):

        aliases = entity_data.get(
            "aliases",
            []
        )

        for alias in aliases:

            if (
                alias
                in normalized_description
            ):

                return {
                    "entity_name": (
                        canonical_entity
                    ),
                    "entity_type": (
                        "merchant"
                    ),
                    "entity_confidence": (
                        0.95
                    ),
                }

    if (
        "trf p "
        in normalized_description
        or "trf de "
        in normalized_description
    ):

        return {
            "entity_name": (
                "peer_transfer"
            ),
            "entity_type": (
                "financial_flow"
            ),
            "entity_confidence": (
                0.95
            ),
        }

    if (
        "ordenado"
        in normalized_description
    ):

        return {
            "entity_name": (
                "salary"
            ),
            "entity_type": (
                "income"
            ),
            "entity_confidence": (
                0.98
            ),
        }

    return {
        "entity_name": None,
        "entity_type": None,
        "entity_confidence": 0.0,
    }