from datetime import datetime
from pathlib import Path

from app.domain.imports import (
    ImportFile,
)
from app.ingestion.loader import (
    IngestionLoader,
)
from app.schema.versions import (
    CURRENT_IMPORT_SCHEMA_VERSION,
)
from app.storage.imports import (
    import_exists,
)
from app.storage.imports import (
    save_import,
)
from app.storage.imports import (
    update_import_status,
)
from app.storage.raw_transactions import (
    save_raw_transactions,
)
from app.utils.file_hash import (
    generate_file_hash,
)


RAW_TRANSACTIONS_PATH = (
    Path(
        "data/processed/"
        "raw_transactions.parquet"
    )
)


def run_ingestion_pipeline(
    force_reprocess: bool = False,
    rebuild_bronze: bool = False,
):

    if (
        rebuild_bronze
        and RAW_TRANSACTIONS_PATH.exists()
    ):

        RAW_TRANSACTIONS_PATH.unlink()

    loader = IngestionLoader()

    files = loader.discover_files(
        "data/raw"
    )

    total_raw_transactions = 0

    for file_path in files:

        adapter = loader.get_adapter_for_file(
            file_path
        )

        if adapter is None:

            print(
                f"No adapter found for: "
                f"{file_path}"
            )

            continue

        file_hash = generate_file_hash(
            file_path
        )

        if (
            import_exists(file_hash)
            and not force_reprocess
        ):

            print(
                f"Skipping already processed "
                f"file: {file_path.name}"
            )

            continue

        print(
            f"Processing ingestion: "
            f"{file_path.name}"
        )

        import_file = ImportFile(
            import_file_id=file_hash,
            schema_version=(
                CURRENT_IMPORT_SCHEMA_VERSION
            ),
            original_filename=(
                file_path.name
            ),
            file_hash=file_hash,
            source_bank_id=(
                adapter.bank_id
            ),
            detected_adapter_id=(
                adapter.bank_id
            ),
            imported_at=datetime.now(),
            import_status="PROCESSING",
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
        )

        save_import(
            import_file
        )

        try:

            raw_transactions = (
                adapter
                .extract_raw_transactions(
                    file_path=file_path,
                    import_file_id=(
                        file_hash
                    ),
                )
            )

            result = (
                save_raw_transactions(
                    raw_transactions,
                    overwrite_existing=False,
                )
            )

            total_raw_transactions += (
                result["inserted"]
            )

            update_import_status(
                file_hash=file_hash,
                status="SUCCESS",
            )

        except Exception as error:

            update_import_status(
                file_hash=file_hash,
                status="FAILED",
            )

            print(
                f"""
Failed ingestion:
{file_path.name}

Error:
{error}
"""
            )

    print(
        f"""
Ingestion pipeline completed

Total raw transactions ingested:
{total_raw_transactions}
"""
    )