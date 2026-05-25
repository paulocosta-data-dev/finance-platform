import flet as ft

from app.cashflow.services.monthly_cashflow_service import (
    build_monthly_cashflow_summary,
)


class ForecastPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

    def build(self):

        summary = (
            build_monthly_cashflow_summary()
        )

        grouped_summary = (
            summary.get(
                "grouped_summary",
                []
            )
        )

        details = (
            summary.get(
                "details",
                []
            )
        )

        grouped_rows = []

        for row in grouped_summary:

            grouped_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                row[
                                    "group"
                                ]
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                (
                                    f"{row['last_complete_month']:.2f} EUR"
                                )
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                (
                                    f"{row['forecast']:.2f} EUR"
                                )
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                (
                                    f"{row['delta']:.2f} EUR"
                                )
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                (
                                    f"{row['delta_percentage']:.1f}%"
                                )
                            )
                        ),
                    ]
                )
            )

        detail_controls = []

        for detail in details:

            detail_controls.append(
                self.build_detail_card(
                    detail
                )
            )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Cashflow Forecast",
                    size=32,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                ft.Divider(),
                ft.Text(
                    (
                        "Forecast vs Last Complete Month"
                    ),
                    size=24,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(
                            ft.Text(
                                "Group"
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Last Month"
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Forecast"
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Delta"
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Delta %"
                            )
                        ),
                    ],
                    rows=grouped_rows,
                ),
                ft.Divider(),
                ft.Text(
                    "Forecast Components",
                    size=24,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                ft.Column(
                    spacing=10,
                    controls=detail_controls,
                ),
            ],
        )

    def build_detail_card(
        self,
        detail,
    ):

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
                spacing=10,
                controls=[
                    ft.Text(
                        detail[
                            "entity_name"
                        ],
                        size=22,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),
                    ft.Row(
                        spacing=40,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Group",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        detail[
                                            "forecast_group"
                                        ],
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        (
                                            "Recurring Type"
                                        ),
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        detail[
                                            "recurring_type"
                                        ],
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Cadence",
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        detail[
                                            "cadence"
                                        ],
                                        size=18,
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        (
                                            "Projected Amount"
                                        ),
                                        size=12,
                                        color=(
                                            ft.Colors.GREY_600
                                        ),
                                    ),
                                    ft.Text(
                                        (
                                            f"{detail['projected_monthly_amount']:.2f} EUR"
                                        ),
                                        size=18,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )