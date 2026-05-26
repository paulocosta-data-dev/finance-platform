import pandas as pd

from app.schema.migrations import MIGRATIONS
from app.schema.versions import (
    CURRENT_IMPORT_SCHEMA_VERSION,
    CURRENT_RAW_SCHEMA_VERSION,
    CURRENT_TRANSACTION_SCHEMA_VERSION,
)
from app.utils.paths import data_path


# Map each dataset key to its parquet path and expected current version.
_DATASETS = {
    "transactions": {
        "path": data_path(
            "data/processed/transactions.parquet"
        ),
        "current_version": (
            CURRENT_TRANSACTION_SCHEMA_VERSION
        ),
    },
    "raw_transactions": {
        "path": data_path(
            "data/processed/raw_transactions.parquet"
        ),
        "current_version": (
            CURRENT_RAW_SCHEMA_VERSION
        ),
    },
    "imports": {
        "path": data_path(
            "data/processed/imports.parquet"
        ),
        "current_version": (
            CURRENT_IMPORT_SCHEMA_VERSION
        ),
    },
}


def _detect_version(df: pd.DataFrame) -> int:
    """Return the lowest schema_version found in the DataFrame.
    Files without the column are treated as version 0."""
    if df.empty or "schema_version" not in df.columns:
        return 0
    return int(df["schema_version"].min())


def run_pending_migrations() -> dict:
    """Check every tracked dataset and apply any outstanding migrations.

    Returns a summary dict:
        datasets_checked  — number of existing parquet files inspected
        datasets_migrated — number of files that were actually rewritten
        migrations_applied — list of human-readable migration labels
    """

    summary = {
        "datasets_checked": 0,
        "datasets_migrated": 0,
        "migrations_applied": [],
    }

    for key, config in _DATASETS.items():

        path = config["path"]
        target_version = config["current_version"]

        if not path.exists():
            continue

        summary["datasets_checked"] += 1

        df = pd.read_parquet(path)
        file_version = _detect_version(df)

        if file_version >= target_version:
            continue

        pending = [
            (fv, tv, fn)
            for fv, tv, fn in MIGRATIONS.get(key, [])
            if file_version < tv <= target_version
        ]

        if not pending:
            continue

        for from_v, to_v, migrate_fn in pending:
            df = migrate_fn(df)
            label = f"{key}: v{from_v} → v{to_v}"
            summary["migrations_applied"].append(label)
            file_version = to_v

        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        summary["datasets_migrated"] += 1

    return summary
