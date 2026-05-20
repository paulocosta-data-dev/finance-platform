import hashlib


def generate_transaction_hash(
    account_id: str,
    raw_date: str,
    raw_description: str,
    raw_amount: str,
) -> str:

    raw_key = "|".join([
        account_id.strip(),
        raw_date.strip(),
        raw_description.strip().lower(),
        raw_amount.strip(),
    ])

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()