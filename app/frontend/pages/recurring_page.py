import flet as ft

from app.category.services.recurring_detection_service import (
    detect_recurring_transactions,
)

from app.recurring.services.recurring_override_service import (
    save_recurring_override,
)


class RecurringPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

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

        self.status_text = (
            ft.Text()
        )

        self.load_recurring()

    def build(self):

        refresh_button = (
            ft.Button(
                content=ft.Text(
                    "Refresh"
                ),
                on_click=(
                    self.refresh_page
                ),
            )
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "Recurring Transactions",
                    size=32,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                self.status_text,
                refresh_button,
                ft.Divider(),
                self.content_container,
            ],
        )

    def refresh_page(
        self,
        e,
    ):

        self.load_recurring()

        self.page.update()

    def load_recurring(self):

        self.rows_column.controls.clear()

        recurring_results = (
            detect_recurring_transactions()
        )

        self.status_text.value = (
            (
                "Recurring entities detected: "
                f"{len(recurring_results)}"
            )
        )

        for result in recurring_results:

            self.rows_column.controls.append(
                self.build_row(
                    result
                )
            )

    def confirm_recurring(
        self,
        entity_name: str,
        recurring_type: str,
        cadence: str,
    ):

        save_recurring_override(
            entity_name=entity_name,
            status="confirmed",
            recurring_type=(
                recurring_type
            ),
            cadence=cadence,
        )

        self.load_recurring()

        self.page.update()

    def ignore_recurring(
        self,
        entity_name: str,
    ):

        save_recurring_override(
            entity_name=entity_name,
            status="ignored",
            recurring_type="ignored",
            cadence="ignored",
        )

        self.load_recurring()

        self.page.update()

    def build_row(
        self,
        result,
    ):

        entity_name = result[
            "entity_name"
        ]

        recurring_type_dropdown = (
            ft.Dropdown(
                width=220,
                value="behavioral",
                options=[
                    ft.dropdown.Option(
                        "behavioral"
                    ),
                    ft.dropdown.Option(
                        "subscription"
                    ),
                    ft.dropdown.Option(
                        "obligation"
                    ),
                    ft.dropdown.Option(
                        "salary"
                    ),
                    ft.dropdown.Option(
                        "savings"
                    ),
                ],
            )
        )

        cadence_dropdown = (
            ft.Dropdown(
                width=180,
                value="monthly",
                options=[
                    ft.dropdown.Option(
                        "weekly"
                    ),
                    ft.dropdown.Option(
                        "biweekly"
                    ),
                    ft.dropdown.Option(
                        "monthly"
                    ),
                    ft.dropdown.Option(
                        "quarterly"
                    ),
                    ft.dropdown.Option(
                        "yearly"
                    ),
                    ft.dropdown.Option(
                        "irregular"
                    ),
                ],
            )
        )

        return ft.Container(
            padding=15,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(
                    1,
                    ft.Colors.GREY_300,
                ),
                bottom=ft.BorderSide(
                    1,
                    ft.Colors.GREY_300,
                ),
                left=ft.BorderSide(
                    1,
                    ft.Colors.GREY_300,
                ),
                right=ft.BorderSide(
                    1,
                    ft.Colors.GREY_300,
                ),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                entity_name,
                                size=22,
                                weight=(
                                    ft.FontWeight.BOLD
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=40,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Occurrences",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        str(
                                            result[
                                                "occurrences"
                                            ]
                                        ),
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Average Amount",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        (
                                            f"{result['average_amount']:.2f} EUR"
                                        ),
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "First Seen",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        str(
                                            result[
                                                "first_seen"
                                            ]
                                        ),
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Last Seen",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        str(
                                            result[
                                                "last_seen"
                                            ]
                                        ),
                                        size=18,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=20,
                        controls=[
                            recurring_type_dropdown,
                            cadence_dropdown,
                            ft.Button(
                                content=ft.Text(
                                    "Confirm"
                                ),
                                on_click=lambda e,
                                entity_name=entity_name,
                                recurring_type_dropdown=(
                                    recurring_type_dropdown
                                ),
                                cadence_dropdown=(
                                    cadence_dropdown
                                ):
                                self.confirm_recurring(
                                    entity_name=(
                                        entity_name
                                    ),
                                    recurring_type=(
                                        recurring_type_dropdown
                                        .value
                                    ),
                                    cadence=(
                                        cadence_dropdown
                                        .value
                                    ),
                                ),
                            ),
                            ft.Button(
                                content=ft.Text(
                                    "Ignore"
                                ),
                                on_click=lambda e,
                                entity_name=entity_name:
                                self.ignore_recurring(
                                    entity_name
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )