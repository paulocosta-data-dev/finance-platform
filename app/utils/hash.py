import hashlib


def generate_transaction_hash(
    raw_transaction_id: str,
) -> str:

    return hashlib.sha256(
        raw_transaction_id
        .encode("utf-8")
    ).hexdigest()