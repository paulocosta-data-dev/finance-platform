from datetime import datetime
from pathlib import Path

from app.utils.paths import data_path
import pandas as pd

from app.category.services.learned_rule_service import (
    append_learned_rule,
)


OVERRIDES_PATH = data_path(
    "data/processed/transaction_overrides.parquet"
)


def load_or_create_overrides_df(
) -> pd.DataFrame:

    overrides_path = OVERRIDES_PATH

    if overrides_path.exists():

        return pd.read_parquet(
            str(OVERRIDES_PATH)
        )

    overrides_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    empty_df = pd.DataFrame(
        columns=[
            "transaction_id",
            "override_category_id",
            "override_timestamp",
        ]
    )

    empty_df.to_parquet(
        OVERRIDES_PATH,
        index=False,
    )

    return empty_df


def save_corrections(
    corrections: dict,
    unresolved_df: pd.DataFrame,
) -> None:

    if not corrections:

        return

    overrides_df = (
        load_or_create_overrides_df()
    )

    new_overrides = []

    processed_transactions = set()

    for (
        transaction_id,
        correction_data,
    ) in corrections.items():

        if (
            transaction_id
            in processed_transactions
        ):

            continue

        category_id = (
            correction_data[
                "category_id"
            ]
        )

        apply_to_all = (
            correction_data[
                "apply_to_all"
            ]
        )

        normalized_description = (
            correction_data[
                "normalized_description"
            ]
        )

        if apply_to_all:

            matching_transactions = (
                unresolved_df[
                    unresolved_df[
                        "normalized_description"
                    ]
                    == normalized_description
                ]
            )

            for (
                _,
                matching_row,
            ) in (
                matching_transactions
                .iterrows()
            ):

                matching_transaction_id = (
                    matching_row[
                        "transaction_id"
                    ]
                )

                if (
                    matching_transaction_id
                    in processed_transactions
                ):

                    continue

                processed_transactions.add(
                    matching_transaction_id
                )

                new_overrides.append(
                    {
                        "transaction_id": (
                            matching_transaction_id
                        ),
                        "override_category_id": (
                            category_id
                        ),
                        "override_timestamp": (
                            datetime.utcnow()
                        ),
                    }
                )

            append_learned_rule(
                description=(
                    normalized_description
                ),
                category_id=(
                    category_id
                ),
            )

        else:

            processed_transactions.add(
                transaction_id
            )

            new_overrides.append(
                {
                    "transaction_id": (
                        transaction_id
                    ),
                    "override_category_id": (
                        category_id
                    ),
                    "override_timestamp": (
                        datetime.utcnow()
                    ),
                }
            )

    if not new_overrides:

        return

    new_overrides_df = pd.DataFrame(
        new_overrides
    )

    updated_overrides_df = (
        pd.concat(
            [
                overrides_df,
                new_overrides_df,
            ],
            ignore_index=True,
        )
    )

    updated_overrides_df = (
        updated_overrides_df
        .drop_duplicates(
            subset=[
                "transaction_id",
            ],
            keep="last",
        )
    )

    updated_overrides_df.to_parquet(
        str(OVERRIDES_PATH),
        index=False,
    )

    from app.pipelines.normalization_pipeline import (
        run_normalization_pipeline,
    )
    run_normalization_pipeline(rebuild_silver=True)