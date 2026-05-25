import pandas as pd
import flet as ft

from app.category.services.recurring_detection_service import (
    detect_recurring_transactions,
)


TRANSACTIONS_PATH = (
    "data/processed/transactions.parquet"
)


def load_transactions():

    return pd.read_parquet(
        TRANSACTIONS_PATH
    )


def build_metric_card(
    title,
    value,
):

    return ft.Container(
        width=260,
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.BLUE_50,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    title,
                    size=14,
                    color=(
                        ft.Colors.GREY_700
                    ),
                ),
                ft.Text(
                    str(value),
                    size=30,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
            ],
        ),
    )


def build_home_page():

    df = load_transactions()

    total_transactions = len(df)

    categorized_transactions = len(
        df[
            df["category_id"]
            != "uncategorized"
        ]
    )

    uncategorized_transactions = (
        total_transactions
        - categorized_transactions
    )

    categorization_coverage = round(
        (
            categorized_transactions
            / max(
                total_transactions,
                1,
            )
        )
        * 100,
        1,
    )

    distinct_entities = len(
        df[
            "entity_name"
        ]
        .dropna()
        .unique()
    )

    recurring_entities = len(
        detect_recurring_transactions()
    )

    total_spending = round(
        abs(
            df[
                df["amount"]
                < 0
            ]["amount"]
            .sum()
        ),
        2,
    )

    top_entities = (
        df[
            df["entity_name"]
            .notna()
        ]
        .groupby(
            "entity_name"
        )
        .size()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    top_entities_rows = []

    for (
        entity_name,
        count,
    ) in top_entities.items():

        top_entities_rows.append(
            ft.Row(
                alignment=(
                    ft.MainAxisAlignment
                    .SPACE_BETWEEN
                ),
                controls=[
                    ft.Text(
                        entity_name,
                        size=16,
                    ),
                    ft.Text(
                        str(count),
                        size=16,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),
                ],
            )
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text(
                "Dashboard",
                size=34,
                weight=(
                    ft.FontWeight.BOLD
                ),
            ),
            ft.Row(
                wrap=True,
                spacing=20,
                run_spacing=20,
                controls=[
                    build_metric_card(
                        (
                            "Total "
                            "Transactions"
                        ),
                        total_transactions,
                    ),
                    build_metric_card(
                        (
                            "Categorized "
                            "Transactions"
                        ),
                        categorized_transactions,
                    ),
                    build_metric_card(
                        (
                            "Uncategorized "
                            "Transactions"
                        ),
                        uncategorized_transactions,
                    ),
                    build_metric_card(
                        (
                            "Coverage"
                        ),
                        (
                            f"{categorization_coverage}%"
                        ),
                    ),
                    build_metric_card(
                        (
                            "Distinct "
                            "Entities"
                        ),
                        distinct_entities,
                    ),
                    build_metric_card(
                        (
                            "Recurring "
                            "Entities"
                        ),
                        recurring_entities,
                    ),
                    build_metric_card(
                        (
                            "Total "
                            "Spending"
                        ),
                        (
                            f"{total_spending:.2f} EUR"
                        ),
                    ),
                ],
            ),
            ft.Divider(),
            ft.Text(
                "Top Financial Entities",
                size=24,
                weight=(
                    ft.FontWeight.BOLD
                ),
            ),
            ft.Container(
                padding=20,
                border_radius=12,
                bgcolor=(
                    ft.Colors.BLUE_50
                ),
                content=ft.Column(
                    spacing=15,
                    controls=(
                        top_entities_rows
                    ),
                ),
            ),
        ],
    )