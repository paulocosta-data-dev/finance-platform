import flet as ft

from app.recurring.services.recurring_override_service import (
    load_overrides,
)

from app.recurring.services.recurring_override_service import (
    save_recurring_override,
)


class ReviewedRecurringPage:

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

        self.load_overrides()

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
                    (
                        "Reviewed "
                        "Recurring"
                    ),
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

        self.load_overrides()

        self.page.update()

    def load_overrides(self):

        self.rows_column.controls.clear()

        overrides_df = (
            load_overrides()
        )

        self.status_text.value = (
            (
                "Reviewed recurring entities: "
                f"{len(overrides_df)}"
            )
        )

        if overrides_df.empty:

            return

        overrides_df = (
            overrides_df
            .sort_values(
                "timestamp",
                ascending=False,
            )
        )

        for _, row in (
            overrides_df.iterrows()
        ):

            self.rows_column.controls.append(
                self.build_row(
                    row
                )
            )

    def update_override(
        self,
        entity_name: str,
        status: str,
        recurring_type: str,
        cadence: str,
    ):

        save_recurring_override(
            entity_name=entity_name,
            status=status,
            recurring_type=(
                recurring_type
            ),
            cadence=cadence,
        )

        self.load_overrides()

        self.page.update()

    def build_row(
        self,
        row,
    ):

        entity_name = row[
            "entity_name"
        ]

        status_dropdown = (
            ft.Dropdown(
                width=180,
                value=row["status"],
                options=[
                    ft.dropdown.Option(
                        "confirmed"
                    ),
                    ft.dropdown.Option(
                        "ignored"
                    ),
                ],
            )
        )

        recurring_type_dropdown = (
            ft.Dropdown(
                width=220,
                value=row[
                    "recurring_type"
                ],
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
                    ft.dropdown.Option(
                        "ignored"
                    ),
                ],
            )
        )

        cadence_dropdown = (
            ft.Dropdown(
                width=180,
                value=row["cadence"],
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
                    ft.dropdown.Option(
                        "ignored"
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
                    ft.Text(
                        entity_name,
                        size=22,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),
                    ft.Row(
                        spacing=20,
                        controls=[
                            status_dropdown,
                            recurring_type_dropdown,
                            cadence_dropdown,
                            ft.Button(
                                content=ft.Text(
                                    "Save"
                                ),
                                on_click=lambda e,
                                entity_name=entity_name,
                                status_dropdown=(
                                    status_dropdown
                                ),
                                recurring_type_dropdown=(
                                    recurring_type_dropdown
                                ),
                                cadence_dropdown=(
                                    cadence_dropdown
                                ):
                                self.update_override(
                                    entity_name=(
                                        entity_name
                                    ),
                                    status=(
                                        status_dropdown
                                        .value
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
                        ],
                    ),
                    ft.Text(
                        (
                            "Last updated: "
                            f"{row['timestamp']}"
                        ),
                        size=14,
                        color=(
                            ft.Colors.GREY_600
                        ),
                    ),
                ],
            ),
        )