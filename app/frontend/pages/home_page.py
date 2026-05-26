import flet as ft

from app.cashflow.services.dashboard_service import (
    get_category_breakdown_current_month,
    get_monthly_income_spending,
    get_summary_stats,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _metric_card(title: str, value: str, color=None) -> ft.Container:

    return ft.Container(
        width=220,
        padding=16,
        border_radius=10,
        bgcolor=color or ft.Colors.BLUE_50,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Text(title, size=12, color=ft.Colors.GREY_700),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD),
            ],
        ),
    )


def _section_title(text: str) -> ft.Text:
    return ft.Text(text, size=18, weight=ft.FontWeight.BOLD)


def _bar(value: float, max_value: float, color, height: float = 120) -> ft.Container:
    """Vertical bar proportional to value/max_value."""

    pct = (value / max_value) if max_value > 0 else 0
    bar_height = max(4, round(pct * height))

    return ft.Container(
        width=28,
        height=height,
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.Container(
                    width=28,
                    height=bar_height,
                    bgcolor=color,
                    border_radius=ft.BorderRadius(top_left=4, top_right=4, bottom_left=0, bottom_right=0),
                ),
            ],
        ),
    )


# ── Monthly income/spending chart ────────────────────────────────────────────

def _build_monthly_chart(monthly: list[dict]) -> ft.Container:

    if not monthly:
        return ft.Container(
            content=ft.Text("No transaction data yet.", color=ft.Colors.GREY_500),
        )

    max_val = max(
        max(m["income"], m["spending"]) for m in monthly
    ) or 1.0

    chart_cols = []

    for m in monthly:
        label = m["month"][-5:]  # "MM-YY" style — show "YYYY-MM" last 5 chars

        income_bar = _bar(m["income"], max_val, ft.Colors.GREEN_400)
        spending_bar = _bar(m["spending"], max_val, ft.Colors.RED_300)

        chart_cols.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Row(
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[income_bar, spending_bar],
                    ),
                    ft.Text(label, size=10, color=ft.Colors.GREY_600),
                ],
            )
        )

    legend = ft.Row(
        spacing=16,
        controls=[
            ft.Row(spacing=4, controls=[
                ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN_400, border_radius=2),
                ft.Text("Income", size=11, color=ft.Colors.GREY_700),
            ]),
            ft.Row(spacing=4, controls=[
                ft.Container(width=12, height=12, bgcolor=ft.Colors.RED_300, border_radius=2),
                ft.Text("Spending", size=11, color=ft.Colors.GREY_700),
            ]),
        ],
    )

    return ft.Container(
        padding=16,
        border_radius=10,
        bgcolor=ft.Colors.BLUE_50,
        content=ft.Column(
            spacing=12,
            controls=[
                legend,
                ft.Row(
                    spacing=16,
                    alignment=ft.MainAxisAlignment.START,
                    controls=chart_cols,
                ),
            ],
        ),
    )


# ── Category breakdown ───────────────────────────────────────────────────────

def _build_category_breakdown(breakdown: list[dict]) -> ft.Container:

    if not breakdown:
        return ft.Container(
            content=ft.Text("No spending data for current month.", color=ft.Colors.GREY_500),
        )

    total = sum(r["total"] for r in breakdown) or 1.0
    top = breakdown[:12]

    rows = []

    for item in top:
        pct = round(item["total"] / total * 100, 1)
        bar_width = max(4, round(pct * 2.5))  # scale: 100% → 250px

        rows.append(
            ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(item["category_id"], size=13),
                            ft.Text(f"€{item['total']:.0f}  ({pct}%)", size=12, color=ft.Colors.GREY_600),
                        ],
                    ),
                    ft.Container(
                        height=6,
                        width=bar_width,
                        bgcolor=ft.Colors.BLUE_400,
                        border_radius=3,
                    ),
                ],
            )
        )

    return ft.Container(
        padding=16,
        border_radius=10,
        bgcolor=ft.Colors.BLUE_50,
        width=360,
        content=ft.Column(spacing=10, controls=rows),
    )


# ── Page builder ─────────────────────────────────────────────────────────────

def build_home_page() -> ft.Column:

    stats = get_summary_stats()
    monthly = get_monthly_income_spending(n_months=6)
    breakdown = get_category_breakdown_current_month()

    month_label = stats.get("current_month_label", "—")

    top_cards = ft.Row(
        wrap=True,
        spacing=16,
        run_spacing=16,
        controls=[
            _metric_card(
                f"Income  {month_label}",
                f"€{stats.get('current_month_income', 0):.0f}",
                ft.Colors.GREEN_50,
            ),
            _metric_card(
                f"Spending  {month_label}",
                f"€{stats.get('current_month_spending', 0):.0f}",
                ft.Colors.RED_50,
            ),
            _metric_card(
                "Total Transactions",
                str(stats.get("total_transactions", 0)),
            ),
            _metric_card(
                "Categorized",
                f"{stats.get('categorized', 0)}  ({stats.get('coverage_pct', 0)}%)",
            ),
            _metric_card(
                "Pending Review",
                str(stats.get("uncategorized", 0)),
                ft.Colors.ORANGE_50,
            ),
        ],
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text("Dashboard", size=34, weight=ft.FontWeight.BOLD),
            top_cards,
            ft.Divider(),
            ft.Row(
                spacing=30,
                wrap=True,
                controls=[
                    ft.Column(
                        spacing=10,
                        controls=[
                            _section_title("Income vs Spending — last 6 months"),
                            _build_monthly_chart(monthly),
                        ],
                    ),
                    ft.Column(
                        spacing=10,
                        controls=[
                            _section_title(f"Category breakdown — {month_label}"),
                            _build_category_breakdown(breakdown),
                        ],
                    ),
                ],
            ),
        ],
    )
