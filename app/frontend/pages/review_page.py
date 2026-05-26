import flet as ft

from app.ui.services.category_service import (
    load_available_categories,
    persist_category,
)

from app.ui.services.review_service import (
    save_corrections,
)

from app.anomaly.services.anomaly_service import (
    build_category_stats,
    flag_anomalies,
)

from app.ui.services.account_service import (
    ALL_ACCOUNTS,
    get_account_ids,
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

        self.is_anomaly = bool(
            row.get("is_anomaly", False)
        )
        self.anomaly_severity = row.get(
            "anomaly_severity", None
        )

    def _build_anomaly_badge(self):
        if not self.is_anomaly:
            return ft.Container(width=140)

        if self.anomaly_severity == "high":
            label = "!! Very unusual"
            bg = ft.Colors.RED_100
            fg = ft.Colors.RED_900
        else:
            label = "! Unusual amount"
            bg = ft.Colors.ORANGE_100
            fg = ft.Colors.ORANGE_900

        return ft.Container(
            width=140,
            bgcolor=bg,
            border_radius=4,
            padding=ft.Padding(
                left=6,
                right=6,
                top=3,
                bottom=3,
            ),
            content=ft.Text(
                label,
                size=11,
                color=fg,
            ),
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
                self._build_anomaly_badge(),
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

        self._selected_account = ALL_ACCOUNTS
        self._category_stats = {}

        self._account_dropdown = ft.Dropdown(
            value=ALL_ACCOUNTS,
            options=self._account_options(),
            width=200,
            on_change=self._on_account_change,
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
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Text("Account:", size=13, color=ft.Colors.GREY_700),
                        self._account_dropdown,
                    ],
                ),
                self.status_text,
                apply_button,
                ft.Divider(),
                self.content_container,
            ],
        )

    def _account_options(self):
        opts = [ft.dropdown.Option(ALL_ACCOUNTS, "All Accounts")]
        for acc in get_account_ids():
            opts.append(ft.dropdown.Option(acc))
        return opts

    def _on_account_change(self, e):
        self._selected_account = e.control.value or ALL_ACCOUNTS
        self.load_transactions()
        self.page.update()

    def load_transactions(self):

        self.rows_column.controls.clear()

        from app.ui.services.account_service import filter_by_account
        from app.utils.paths import data_path
        import pandas as pd

        # Build category stats from full transaction history for anomaly detection
        txn_path = data_path("data/processed/transactions.parquet")
        if txn_path.exists():
            full_df = pd.read_parquet(txn_path)
            self._category_stats = build_category_stats(full_df)
        else:
            self._category_stats = {}

        unresolved_df = filter_by_account(
            load_unresolved_transactions(),
            self._selected_account,
        )

        if not unresolved_df.empty and self._category_stats:
            unresolved_df = flag_anomalies(unresolved_df, self._category_stats)

        unresolved_count = len(
            unresolved_df
        )

        self.status_text.value = (
            f"Pending review: {unresolved_count}"
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

        from app.ui.services.account_service import filter_by_account
        unresolved_df = filter_by_account(
            load_unresolved_transactions(),
            self._selected_account,
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
