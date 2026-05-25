from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ImportFile(BaseModel):

    import_file_id: str

    schema_version: int

    original_filename: str
    file_hash: str

    source_bank_id: str
    detected_adapter_id: str

    imported_at: datetime

    import_status: str

    total_rows: int
    valid_rows: int
    invalid_rows: int

    duplicate_of_import_id: Optional[str] = None

    processing_log: Optional[str] = None


class RawTransaction(BaseModel):

    raw_transaction_id: str

    schema_version: int

    import_file_id: str

    source_account_id: str

    sheet_name: str

    source_row_number: int

    raw_date: str
    raw_booking_date: str

    raw_description: str

    raw_amount: str
    raw_balance: str

    raw_payload_json: dict

    created_at: datetime