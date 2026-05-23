import flet as ft

from app.ui.services.category_service import (
    load_available_categories,
    persist_category,
)

from app.ui.services.review_service import (
    save_corrections,
)

from app.ui.services.transaction_service import (
    load_unresolved_transactions,
)


class ReviewRow:

    def __init__(
        self,
        row,
        available_categories,
    ):

        self.row = row

        self.transaction_id = (
            row["transaction_id"]
        )

        self.description = row[
            "description"
        ]

        self.normalized_description = row[
            "normalized_description"
        ]

        self.current_category = row[
            "category_id"
        ]

        self.selected_category = (
            ft.Dropdown(
                value=self.current_category,
                options=[
                    ft.dropdown.Option(
                        category
                    )
                    for category
                    in available_categories
                ],
                width=220,
            )
        )

        self.new_category = (
            ft.TextField(
                hint_text="Create...",
                width=220,
            )
        )

        self.apply_all = (
            ft.Checkbox(
                value=False,
            )
        )

    def build(self):

        return ft.Row(
            width=1900,
            controls=[
                ft.Container(
                    content=ft.Text(
                        str(
                            self.row[
                                "transaction_date"
                            ]
                        )[:10]
                    ),
                    width=140,
                ),
                ft.Container(
                    width=650,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                self.description,
                                size=14,
                            ),
                            ft.Text(
                                self.normalized_description,
                                size=11,
                                color=(
                                    ft.Colors.GREY_600
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    content=ft.Text(
                        str(
                            round(
                                self.row[
                                    "amount"
                                ],
                                2,
                            )
                        )
                    ),
                    width=140,
                ),
                ft.Container(
                    content=ft.Text(
                        self.current_category
                    ),
                    width=200,
                ),
                self.selected_category,
                self.new_category,
                ft.Container(
                    width=160,
                    content=ft.Row(
                        controls=[
                            self.apply_all,
                            ft.Text(
                                "Apply All"
                            ),
                        ],
                        spacing=5,
                    ),
                ),
            ],
        )

    def get_correction(self):

        category = (
            self.selected_category.value
        )

        new_category = (
            self.new_category.value
        )

        if (
            new_category
            and new_category.strip()
        ):

            normalized_new_category = (
                new_category
                .strip()
                .lower()
                .replace(
                    " ",
                    "_",
                )
            )

            persist_category(
                normalized_new_category
            )

            category = (
                normalized_new_category
            )

        if (
            category
            == self.current_category
            and not self.apply_all.value
        ):

            return None

        return {
            "category_id": category,
            "apply_to_all": (
                self.apply_all.value
            ),
            "normalized_description": (
                self.normalized_description
            ),
        }


class ReviewPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

        self.available_categories = (
            load_available_categories()
        )

        self.review_rows = []

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

        apply_button = (
            ft.Button(
                content=ft.Text(
                    "Apply Changes"
                ),
                on_click=self.apply_changes,
            )
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "Review Transactions",
                    size=32,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                self.status_text,
                apply_button,
                ft.Divider(),
                self.content_container,
            ],
        )

    def load_transactions(self):

        self.rows_column.controls.clear()

        unresolved_df = (
            load_unresolved_transactions()
        )

        unresolved_count = len(
            unresolved_df
        )

        self.status_text.value = (
            f"""
Pending review:
{unresolved_count}
"""
        )

        self.review_rows = []

        for _, row in unresolved_df.iterrows():

            review_row = (
                ReviewRow(
                    row=row,
                    available_categories=(
                        self.available_categories
                    ),
                )
            )

            self.review_rows.append(
                review_row
            )

            self.rows_column.controls.append(
                review_row.build()
            )

    def apply_changes(
        self,
        e,
    ):

        corrections = {}

        unresolved_df = (
            load_unresolved_transactions()
        )

        for review_row in self.review_rows:

            correction = (
                review_row.get_correction()
            )

            if correction is not None:

                corrections[
                    review_row.transaction_id
                ] = correction

        if not corrections:

            self.status_text.value = (
                "No corrections to apply"
            )

            self.page.update()

            return

        save_corrections(
            corrections=corrections,
            unresolved_df=(
                unresolved_df
            ),
        )

        self.available_categories = (
            load_available_categories()
        )

        self.load_transactions()

        self.page.update()