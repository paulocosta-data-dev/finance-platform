from pathlib import Path

import pandas as pd

from app.domain.imports import ImportFile


IMPORTS_PATH = (
    Path("data/processed/imports.parquet")
)


def import_to_dict(
    import_file: ImportFile,
) -> dict:

    return import_file.model_dump()


def load_imports() -> pd.DataFrame:

    if not IMPORTS_PATH.exists():

        return pd.DataFrame()

    return pd.read_parquet(
        IMPORTS_PATH
    )


def import_exists(
    file_hash: str,
) -> bool:

    imports_df = load_imports()

    if imports_df.empty:
        return False

    return file_hash in (
        imports_df["file_hash"]
        .values
    )


def save_import(
    import_file: ImportFile,
) -> None:

    new_df = pd.DataFrame([
        import_to_dict(import_file)
    ])

    existing_df = load_imports()

    combined_df = pd.concat(
        [existing_df, new_df],
        ignore_index=True,
    )

    combined_df = combined_df.drop_duplicates(
        subset=["import_file_id"],
        keep="last",
    )

    IMPORTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_parquet(
        IMPORTS_PATH,
        index=False,
    )


def update_import_status(
    file_hash: str,
    status: str,
) -> None:

    imports_df = load_imports()

    if imports_df.empty:
        return

    imports_df.loc[
        imports_df["file_hash"] == file_hash,
        "import_status",
    ] = status

    imports_df.to_parquet(
        IMPORTS_PATH,
        index=False,
    )