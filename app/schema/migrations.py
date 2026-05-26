import pandas as pd


# Each migration is a tuple: (from_version, to_version, transform_fn)
# transform_fn receives a DataFrame and returns the migrated DataFrame.
# Add new entries here when the schema changes — never modify existing ones.


def _transactions_v0_to_v1(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure schema_version column exists on pre-versioned files."""
    df = df.copy()
    if "schema_version" not in df.columns:
        df["schema_version"] = 1
    else:
        df["schema_version"] = (
            df["schema_version"].fillna(1).astype(int)
        )
    return df


def _raw_transactions_v0_to_v1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "schema_version" not in df.columns:
        df["schema_version"] = 1
    return df


def _imports_v0_to_v1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "schema_version" not in df.columns:
        df["schema_version"] = 1
    return df


# Registry: dataset_key → ordered list of migrations to apply in sequence.
# New migrations go at the bottom of each list.
MIGRATIONS: dict[str, list[tuple]] = {
    "transactions": [
        (0, 1, _transactions_v0_to_v1),
    ],
    "raw_transactions": [
        (0, 1, _raw_transactions_v0_to_v1),
    ],
    "imports": [
        (0, 1, _imports_v0_to_v1),
    ],
}
