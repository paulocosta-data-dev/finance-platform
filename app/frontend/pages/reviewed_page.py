import flet as ft
import pandas as pd

from app.ui.services.category_service import (
    load_available_categories,
)

from app.ui.services.review_service import (
    save_corrections,
)


TRANSACTIONS_PATH = (
    "data/processed/transactions.parquet"
)


class ReviewedPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

        self.available_categories = (
            load_available_categories()
        )

        self.search_field = (
            ft.TextField(
                label="Search",
                width=400,
                on_change=(
                    self.refresh_page
                ),
            )
        )

        self.rows_column = (
            ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
        )

        self.content_container = (
            ft.Row(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    self.rows_column
                ],
            )
        )

        self.status_text = ft.Text()

        self.load_transactions()

    def build(self):

        return ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "Reviewed Transactions",
                    size=32,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                self.search_field,
                self.status_text,
                ft.Divider(),
                self.content_container,
            ],
        )

    def refresh_page(
        self,
        e,
    ):

        self.load_transactions()

        self.page.update()

    def load_transactions(self):

        self.rows_column.controls.clear()

        df = pd.read_parquet(
            TRANSACTIONS_PATH
        )

        reviewed_df = df[
            df["category_id"]
            != "uncategorized"
        ].copy()

        search_value = (
            self.search_field.value
            or ""
        ).lower()

        if search_value:

            reviewed_df = (
                reviewed_df[
                    reviewed_df[
                        "description"
                    ]
                    .str.lower()
                    .str.contains(
                        search_value,
                        na=False,
                    )
                ]
            )

        reviewed_df = (
            reviewed_df.sort_values(
                "transaction_date",
                ascending=False,
            )
        )

        self.status_text.value = (
            (
                "Reviewed transactions: "
                f"{len(reviewed_df)}"
            )
        )

        for _, row in (
            reviewed_df.iterrows()
        ):

            self.rows_column.controls.append(
                self.build_row(
                    row
                )
            )

    def build_row(
        self,
        row,
    ):

        category_dropdown = (
            ft.Dropdown(
                value=row[
                    "category_id"
                ],
                width=220,
                options=[
                    ft.dropdown.Option(
                        category
                    )
                    for category
                    in (
                        self.available_categories
                    )
                ],
            )
        )

        save_button = (
            ft.Button(
                content=ft.Text(
                    "Save"
                ),
                on_click=lambda e:
                self.save_category_change(
                    transaction_id=(
                        row[
                            "transaction_id"
                        ]
                    ),
                    normalized_description=(
                        row[
                            "normalized_description"
                        ]
                    ),
                    category_dropdown=(
                        category_dropdown
                    ),
                ),
            )
        )

        return ft.Row(
            width=1900,
            controls=[
                ft.Container(
                    width=140,
                    content=ft.Text(
                        str(
                            row[
                                "transaction_date"
                            ]
                        )[:10]
                    ),
                ),
                ft.Container(
                    width=650,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                row[
                                    "description"
                                ],
                                size=14,
                            ),
                            ft.Text(
                                row[
                                    "normalized_description"
                                ],
                                size=11,
                                color=(
                                    ft.Colors.GREY_600
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    width=140,
                    content=ft.Text(
                        str(
                            round(
                                row[
                                    "amount"
                                ],
                                2,
                            )
                        )
                    ),
                ),
                ft.Container(
                    width=200,
                    content=ft.Text(
                        row[
                            "category_id"
                        ]
                    ),
                ),
                category_dropdown,
                save_button,
            ],
        )

    def save_category_change(
        self,
        transaction_id,
        normalized_description,
        category_dropdown,
    ):

        correction = {
            transaction_id: {
                "category_id": (
                    category_dropdown.value
                ),
                "apply_to_all": False,
                "normalized_description": (
                    normalized_description
                ),
            }
        }

        unresolved_df = (
            pd.read_parquet(
                TRANSACTIONS_PATH
            )
        )

        save_corrections(
            corrections=correction,
            unresolved_df=(
                unresolved_df
            ),
        )

        self.load_transactions()

        self.page.update()