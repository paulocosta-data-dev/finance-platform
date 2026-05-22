import pandas as pd


TRANSACTIONS_PATH = (
    "data/processed/"
    "transactions.parquet"
)


def load_unresolved_transactions(
) -> pd.DataFrame:

    df = pd.read_parquet(
        TRANSACTIONS_PATH
    )

    unresolved_df = df[
        (
            df["category_id"]
            == "uncategorized"
        )
        |
        (
            df["semantic_type_id"]
            == "UNKNOWN"
        )
    ].copy()

    return unresolved_df


def apply_session_overrides(
    unresolved_df: pd.DataFrame,
    corrections: dict,
) -> pd.DataFrame:

    filtered_df = (
        unresolved_df.copy()
    )

    for (
        transaction_id,
        correction_data,
    ) in corrections.items():

        apply_to_all = (
            correction_data[
                "apply_to_all"
            ]
        )

        description = (
            correction_data[
                "description"
            ]
        )

        if apply_to_all:

            filtered_df = filtered_df[
                filtered_df[
                    "description"
                ]
                != description
            ]

        else:

            filtered_df = filtered_df[
                filtered_df[
                    "transaction_id"
                ]
                != transaction_id
            ]

    return filtered_df