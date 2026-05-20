from datetime import datetime
from pathlib import Path

import pandas as pd

from app.domain.imports import RawTransaction
from app.ingestion.base import BankAdapter
from app.utils.raw_hash import (
    generate_raw_transaction_hash,
)


class CGDAdapter(BankAdapter):

    @property
    def bank_id(self) -> str:
        return "CGD"

    def can_handle(
        self,
        file_path: Path,
    ) -> bool:

        try:

            df = pd.read_excel(
                file_path,
                nrows=10,
                header=None,
            )

            flattened_values = " ".join(
                str(value)
                for value in df.values.flatten()
            )

            return (
                "Data do Movimento"
                in flattened_values
                and "Descrição"
                in flattened_values
                and "Saldo"
                in flattened_values
            )

        except Exception:
            return False

    def extract_raw_transactions(
        self,
        file_path: Path,
        import_file_id: str,
    ) -> list[RawTransaction]:

        df = pd.read_excel(
            file_path,
            skiprows=4,
            header=0,
        )

        transactions = []

        for index, row in df.iterrows():

            if pd.isna(
                row.get("Data do Movimento")
            ):
                continue

            source_row_number = index + 1

            raw_transaction = RawTransaction(
                raw_transaction_id=(
                    generate_raw_transaction_hash(
                        import_file_id=(
                            import_file_id
                        ),
                        source_row_number=(
                            source_row_number
                        ),
                    )
                ),
                import_file_id=import_file_id,
                source_account_id="CGD_MAIN",
                sheet_name="Sheet1",
                source_row_number=(
                    source_row_number
                ),
                raw_date=str(
                    row.get(
                        "Data do Movimento",
                        "",
                    )
                ),
                raw_booking_date=str(
                    row.get(
                        "Data Valor",
                        "",
                    )
                ),
                raw_description=str(
                    row.get(
                        "Descrição",
                        "",
                    )
                ),
                raw_amount=str(
                    row.get(
                        "Valor",
                        "",
                    )
                ),
                raw_balance=str(
                    row.get(
                        "Saldo",
                        "",
                    )
                ),
                raw_payload_json=(
                    row.to_dict()
                ),
                created_at=datetime.now(),
            )

            transactions.append(
                raw_transaction
            )

        return transactions