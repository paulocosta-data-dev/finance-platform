from datetime import datetime
import subprocess

import pandas as pd

from app.category.services.learned_rule_service import (
    append_learned_rule,
)


OVERRIDES_PATH = (
    "data/processed/"
    "transaction_overrides.parquet"
)


def save_corrections(
    corrections: dict,
    unresolved_df: pd.DataFrame,
) -> None:

    overrides_df = pd.read_parquet(
        OVERRIDES_PATH
    )

    new_overrides = []

    for (
        transaction_id,
        correction_data,
    ) in corrections.items():

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

        description = (
            correction_data[
                "description"
            ]
        )

        if apply_to_all:

            matching_transactions = (
                unresolved_df[
                    unresolved_df[
                        "description"
                    ]
                    ==
                    description
                ]
            )

            for (
                _,
                matching_row,
            ) in (
                matching_transactions
                .iterrows()
            ):

                new_overrides.append(
                    {
                        "transaction_id": (
                            matching_row[
                                "transaction_id"
                            ]
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
                    description
                ),
                category_id=(
                    category_id
                ),
            )

        else:

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

    new_overrides_df = (
        pd.DataFrame(
            new_overrides
        )
    )

    if overrides_df.empty:

        updated_overrides_df = (
            new_overrides_df
        )

    else:

        updated_overrides_df = (
            pd.concat(
                [
                    overrides_df,
                    new_overrides_df,
                ],
                ignore_index=True,
            )
        )

    updated_overrides_df.to_parquet(
        OVERRIDES_PATH,
        index=False,
    )

    subprocess.run(
        [
            "python",
            "run_normalization_pipeline.py",
        ],
        check=True,
    )