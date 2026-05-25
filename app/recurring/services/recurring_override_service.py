from datetime import datetime
from pathlib import Path

import pandas as pd


OVERRIDES_PATH = Path(
    "data/processed/"
    "recurring_overrides.parquet"
)


def load_overrides():

    if not OVERRIDES_PATH.exists():

        return pd.DataFrame(
            columns=[
                "entity_name",
                "status",
                "recurring_type",
                "cadence",
                "timestamp",
            ]
        )

    return pd.read_parquet(
        OVERRIDES_PATH
    )


def get_override_lookup():

    overrides_df = (
        load_overrides()
    )

    if overrides_df.empty:

        return {}

    latest_overrides = (
        overrides_df
        .sort_values(
            "timestamp"
        )
        .drop_duplicates(
            subset=[
                "entity_name"
            ],
            keep="last",
        )
    )

    return {
        row["entity_name"]: {
            "status": (
                row["status"]
            ),
            "recurring_type": (
                row[
                    "recurring_type"
                ]
            ),
            "cadence": (
                row["cadence"]
            ),
        }
        for _, row
        in latest_overrides.iterrows()
    }


def save_recurring_override(
    entity_name: str,
    status: str,
    recurring_type: str,
    cadence: str,
):

    overrides_df = (
        load_overrides()
    )

    new_row_df = pd.DataFrame([
        {
            "entity_name": (
                entity_name
            ),
            "status": status,
            "recurring_type": (
                recurring_type
            ),
            "cadence": cadence,
            "timestamp": (
                datetime.utcnow()
            ),
        }
    ])

    if overrides_df.empty:

        updated_df = (
            new_row_df
        )

    else:

        updated_df = pd.concat(
            [
                overrides_df,
                new_row_df,
            ],
     