from datetime import datetime

from app.domain.imports import ImportFile
from app.ingestion.loader import IngestionLoader
from app.ingestion.normalizer import (
    normalize_raw_transaction,
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
from app.storage.transactions import (
    save_transactions,
)
from app.utils.file_hash import (
    generate_file_hash,
)


def run_ingestion_pipeline():

    loader = IngestionLoader()

    files = loader.discover_files(
        "data/raw"
    )

    normalized_transactions = []

    for file_path in files:

        adapter = loader.get_adapter_for_file(
            file_path
        )

        if adapter is None:

            print(
                f"No adapter found for: {file_path}"
            )

            continue

        file_hash = generate_file_hash(
            file_path
        )

        if import_exists(file_hash):

            print(
                f"Skipping already processed file: "
                f"{file_path.name}"
            )

            continue

        print(
            f"Processing: {file_path.name}"
        )

        import_file = ImportFile(
            import_file_id=file_hash,
            original_filename=file_path.name,
            file_hash=file_hash,
            source_bank_id=adapter.bank_id,
            detected_adapter_id=adapter.bank_id,
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
                adapter.extract_raw_transactions(
                    file_path=file_path,
                    import_file_id=file_hash,
                )
            )

            save_raw_transactions(
                raw_transactions
            )

            for raw_transaction in raw_transactions:

                transaction = (
                    normalize_raw_transaction(
                        raw_transaction=raw_transaction,
                        account_id=adapter.bank_id,
                    )
                )

                normalized_transactions.append(
                    transaction
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
Failed processing file:
{file_path.name}

Error:
{error}
"""
            )

    result = save_transactions(
        normalized_transactions
    )

    print(
        f"""
Ingestion completed

New transactions inserted:
{result["inserted"]}

Duplicate transactions skipped:
{result["duplicates_skipped"]}

Total transactions stored:
{result["total_transactions"]}
"""
    )