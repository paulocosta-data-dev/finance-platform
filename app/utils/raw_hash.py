import hashlib


def generate_raw_transaction_hash(
    import_file_id: str,
    source_row_number: int,
) -> str:

    raw_key = (
        f"{import_file_id}|"
        f"{source_row_number}"
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()