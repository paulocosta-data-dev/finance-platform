import pandas as pd

from app.domain.transactions import (
    Transaction,
)

from app.entity.services.entity_detection_service import (
    detect_entity,
)


df = pd.read_parquet(
    "data/processed/transactions.parquet"
)

print()

print(
    "ENTITY DETECTION"
)

print()

for _, row in df.iterrows():

    transaction = (
        Transaction.model_validate(
            row.to_dict()
        )
    )

    result = detect_entity(
        transaction
    )

    if result.matched:

        print(
            (
                f"{result.entity_type:<20}"
                f" | "
                f"{result.entity_name:<20}"
                f" | "
                f"{row['normalized_description']}"
            )
        )