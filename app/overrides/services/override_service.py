from app.utils.paths import data_path
import pandas as pd


OVERRIDES_PATH = data_path(
    "data/processed/transaction_overrides.parquet"
)


def load_overrides_df(
) -> pd.DataFrame:

    overrides_path = OVERRIDES_PATH

    if not overrides_path.exists():

        return pd.DataFrame(
            columns=[
                "transaction_id",
                "override_category_id",
                "override_timestamp",
            ]
        )

    return pd.read_parquet(
        str(OVERRIDES_PATH)
    )


def apply_overrides(
    transactions_df: pd.DataFrame,
) -> pd.DataFrame:

    overrides_df = (
        load_overrides_df()
    )

    if overrides_df.empty:

        return transactions_df

    latest_overrides = (
        overrides_df
        .sort_values(
            by="override_timestamp"
        )
        .drop_duplicates(
            subset=["transaction_id"],
            keep="last",
        )
    )

    override_mapping = dict(
        zip(
            latest_overrides[
                "transaction_id"
            ],
            latest_overrides[
                "override_category_id"
            ],
        )
    )

    transactions_df = (
        transactions_df.copy()
    )

    transactions_df[
        "category_id"
    ] = (
        transactions_df[
            "transaction_id"
        ]
        .map(
            override_mapping
        )
        .fillna(
            transactions_df[
                "category_id"
            ]
        )
    )

    return transactions_df