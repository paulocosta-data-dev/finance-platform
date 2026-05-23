import pandas as pd

from app.merchant.services.merchant_engine import (
    detect_merchant,
)


df = pd.read_parquet(
    "data/processed/transactions.parquet"
)

print()

print(
    "MERCHANT DETECTION"
)

print()

for _, row in df.iterrows():

    result = (
        detect_merchant(
            row[
                "normalized_description"
            ]
        )
    )

    if result.matched:

        print(
            (
                f"{result.merchant_name:<15}"
                f" | "
                f"{row['normalized_description']}"
            )
        )