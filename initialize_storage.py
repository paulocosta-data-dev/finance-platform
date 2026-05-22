from pathlib import Path

import pandas as pd

import yaml


DATASETS = {
    "data/processed/imports.parquet": [
        "import_id",
        "file_name",
        "import_timestamp",
        "status",
    ],
    "data/processed/raw_transactions.parquet": [
        "raw_transaction_id",
        "import_id",
        "source_account_id",
        "transaction_date",
        "raw_description",
        "raw_amount",
        "raw_balance",
        "currency",
        "raw_hash",
        "schema_version",
    ],
    "data/processed/transactions.parquet": [
        "transaction_id",
        "raw_transaction_id",
        "transaction_date",
        "description",
        "normalized_description",
        "amount",
        "currency",
        "direction",
        "semantic_type_id",
        "semantic_confidence",
        "matched_rule_id",
        "category_id",
        "created_at",
        "schema_version",
    ],
    "data/processed/transaction_overrides.parquet": [
        "transaction_id",
        "override_category_id",
        "override_timestamp",
    ],
    
    "data/processed/learned_category_rules.yaml": [],
}


def initialize_dataset(
    dataset_path: str,
    columns,
) -> None:

    path = Path(
        dataset_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():

        print(
            f"""
Dataset already exists:
{dataset_path}
"""
        )

        return

    if (
        path.suffix
        == ".parquet"
    ):

        empty_df = pd.DataFrame(
            columns=columns
        )

        empty_df.to_parquet(
            path,
            index=False,
        )

    elif (
        path.suffix
        == ".yaml"
    ):

        with open(
            path,
            "w",
        ) as file:

            yaml.dump(
                {
                    "rules": [],
                },
                file,
                sort_keys=False,
            )

    print(
        f"""
Created dataset:
{dataset_path}
"""
    )


def initialize_storage() -> None:

    print(
        "\nInitializing storage...\n"
    )

    for (
        dataset_path,
        columns,
    ) in DATASETS.items():

        initialize_dataset(
            dataset_path=dataset_path,
            columns=columns,
        )

    print(
        "\nStorage initialization completed.\n"
    )


if __name__ == "__main__":

    initialize_storage()