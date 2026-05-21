import pandas as pd


TRANSACTIONS_PATH = (
    "data/processed/"
    "transactions.parquet"
)


def load_transactions():

    return pd.read_parquet(
        TRANSACTIONS_PATH
    )


def semantic_distribution():

    df = load_transactions()

    distribution = (
        df.groupby(
            "semantic_type_id"
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            by="count",
            ascending=False,
        )
    )

    return distribution


def unresolved_transactions():

    df = load_transactions()

    unresolved = df[
        df["semantic_type_id"]
        == "UNKNOWN"
    ]

    return (
        unresolved.groupby(
            "normalized_description"
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            by="count",
            ascending=False,
        )
    )


def matched_rules_distribution():

    df = load_transactions()

    matched = df[
        df["matched_rule_id"]
        .notna()
    ]

    return (
        matched.groupby(
            "matched_rule_id"
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            by="count",
            ascending=False,
        )
    )