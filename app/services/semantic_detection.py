from app.domain.transactions import Transaction


def detect_semantic_type(
    transaction: Transaction,
) -> str:

    description = transaction.normalized_description

    # --- Savings transfers ---
    if (
        "dep prazo" in description
        or "reforco dep prazo" in description
        or "reforco aut dep prazo" in description
    ):
        return "SAVINGS_TRANSFER"

    # --- Peer transfers ---
    if (
        description.startswith("trf p")
        or description.startswith("trf de")
        or "trf p " in description
        or "trf de " in description
    ):
        return "PEER_TRANSFER"

    # --- Purchases ---
    if (
        "compra" in description
        or "contactless" in description
    ):
        return "PURCHASE"

    # --- Fees ---
    if (
        "comissao" in description
        or "taxa" in description
    ):
        return "FEE"

    return "UNKNOWN"