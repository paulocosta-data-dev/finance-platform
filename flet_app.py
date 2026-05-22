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
            controls=[
                ft.Container(
                    content=ft.Text(
                        str(
                            self.row[
                                "transaction_date"
                            ]
                        )[:10]
                    ),
                    width=120,
                ),
                ft.Container(
                    content=ft.Text(
                        self.description
                    ),
                    width=450,
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
                    width=120,
                ),
                ft.Container(
                    content=ft.Text(
                        self.current_category
                    ),
                    width=160,
                ),
                self.selected_category,
                self.new_category,
                ft.Row(
                    controls=[
                        self.apply_all,
                        ft.Text(
                            "Apply All"
                        ),
                    ],
                    spacing=5,
                ),
            ]
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
            "description": (
                self.description
            ),
        }


class FinanceReviewApp:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

        self.page.title = (
            "Finance Platform"
        )

        self.page.window_width = 1600

        self.page.window_height = 900

        self.page.scroll = (
            ft.ScrollMode.AUTO
        )

        self.available_categories = (
            load_available_categories()
        )

        self.review_rows = []

        self.content_column = (
            ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
        )

        self.status_text = ft.Text()

        self.load_transactions()

        apply_button = (
            ft.Button(
                content=ft.Text(
                    "Apply Changes"
                ),
                on_click=self.apply_changes,
            )
        )

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text(
                        "Finance Platform",
                        size=32,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),
                    ft.Text(
                        (
                            "Unresolved "
                            "Transactions Review"
                        ),
                        size=18,
                    ),
                    self.status_text,
                    apply_button,
                    self.content_column,
                ]
            )
        )

    def load_transactions(self):

        self.content_column.controls.clear()

        unresolved_df = (
            load_unresolved_transactions()
        )

        unresolved_count = len(
            unresolved_df
        )

        self.status_text.value = (
            f"""
Unresolved transactions:
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

            self.content_column.controls.append(
                review_row.build()
            )

        self.page.update()

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

        try:

            save_corrections(
                corrections=corrections,
                unresolved_df=(
                    unresolved_df
                ),
            )

            self.status_text.value = (
                (
                    "Corrections applied "
                    "successfully"
                )
            )

            self.available_categories = (
                load_available_categories()
            )

            self.load_transactions()

        except Exception as error:

            self.status_text.value = (
                f"Error: {error}"
            )

            self.page.update()


def main(page: ft.Page):

    FinanceReviewApp(page)


ft.run(main)