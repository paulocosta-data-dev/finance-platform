import flet as ft

from app.cashflow.services.dashboard_service import (
    get_category_breakdown_current_month,
    get_monthly_income_spending,
    get_summary_stats,
)
from app.budget.services.budget_service import get_budget_vs_actual, load_budgets
from app.ui.services.account_service import (
    ALL_ACCOUNTS,
    get_account_balances,
    get_account_ids,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

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
                    border_radius=ft.BorderRadius(
                        top_left=4, top_right=4,
                        bottom_left=0, bottom_right=0,
                    ),
                ),
            ],
        ),
    )


# ── Sub-builders ──────────────────────────────────────────────────────────────

def _build_monthly_chart(monthly: list[dict]) -> ft.Container:
    if not monthly:
        return ft.Container(
            content=ft.Text("No transaction data yet.", color=ft.Colors.GREY_500)
        )

    max_val = max(max(m["income"], m["spending"]) for m in monthly) or 1.0
    chart_cols = []

    for m in monthly:
        label = m["month"][-5:]
        chart_cols.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Row(
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            _bar(m["income"], max_val, ft.Colors.GREEN_400),
                            _bar(m["spending"], max_val, ft.Colors.RED_300),
                        ],
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
                ft.Row(spacing=16, alignment=ft.MainAxisAlignment.START, controls=chart_cols),
            ],
        ),
    )


def _build_category_breakdown(breakdown: list[dict]) -> ft.Container:
    if not breakdown:
        return ft.Container(
            content=ft.Text("No spending data for current month.", color=ft.Colors.GREY_500)
        )

    total = sum(r["total"] for r in breakdown) or 1.0
    rows = []

    for item in breakdown[:12]:
        pct = round(item["total"] / total * 100, 1)
        bar_width = max(4, round(pct * 2.5))
        rows.append(
            ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(item["category_id"], size=13),
                            ft.Text(
                                f"€{item['total']:.0f}  ({pct}%)",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                    ),
                    ft.Container(
                        height=6, width=bar_width,
                        bgcolor=ft.Colors.BLUE_400, border_radius=3,
                    ),
                ],
            )
        )

    return ft.Container(
        padding=16, border_radius=10,
        bgcolor=ft.Colors.BLUE_50, width=360,
        content=ft.Column(spacing=10, controls=rows),
    )


def _build_account_balances(balances: list[dict]) -> ft.Container:
    if not balances:
        return ft.Container(
            content=ft.Text("No accounts found.", color=ft.Colors.GREY_500)
        )

    rows = []
    for b in balances:
        balance_color = ft.Colors.GREEN_700 if b["balance"] >= 0 else ft.Colors.RED_700
        rows.append(
            ft.Container(
                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(b["account_id"], size=13, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            spacing=20,
                            controls=[
                                ft.Text(f"+€{b['income']:.0f}", size=12, color=ft.Colors.GREEN_700),
                                ft.Text(f"-€{b['spending']:.0f}", size=12, color=ft.Colors.RED_600),
                                ft.Text(
                                    f"€{b['balance']:.0f}",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=balance_color,
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )

    return ft.Container(
        padding=16, border_radius=10,
        bgcolor=ft.Colors.BLUE_50, width=400,
        content=ft.Column(spacing=8, controls=rows),
    )



def _build_budget_alerts(rows: list[dict]) -> ft.Container | None:
    """Show over-budget categories. Returns None if budget not configured."""
    over = [r for r in rows if r["over_budget"]]
    if not rows:
        return None  # budget not set up yet — silent
    if not over:
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            border_radius=8,
            bgcolor=ft.Colors.GREEN_50,
            content=ft.Text("✓ All categories within budget this month", size=13, color=ft.Colors.GREEN_800),
        )
    alert_rows = []
    for r in over[:5]:
        alert_rows.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(r["category_id"], size=13),
                    ft.Text(
                        f"€{r['actual']:.0f} / €{r['budget']:.0f}  (+€{r['delta']:.0f})",
                        size=12,
                        color=ft.Colors.RED_700,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            )
        )
    return ft.Container(
        padding=16,
        border_radius=10,
        bgcolor=ft.Colors.RED_50,
        width=400,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Over budget this month", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_800),
            ] + alert_rows,
        ),
    )

# ── Stateful dashboard page ───────────────────────────────────────────────────

class DashboardPage:

    def __init__(self, page: ft.Page):

        self.page = page
        self._selected_account = ALL_ACCOUNTS
        self._content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._refresh()

    def _get_account_options(self) -> list[ft.dropdown.Option]:
        options = [ft.dropdown.Option(ALL_ACCOUNTS, "All Accounts")]
        for acc in get_account_ids():
            options.append(ft.dropdown.Option(acc))
        return options

    def _on_account_change(self, e):
        self._selected_account = e.control.value or ALL_ACCOUNTS
        self._refresh()
        self.page.update()

    def _refresh(self):
        acc = self._selected_account
        stats = get_summary_stats(account_id=acc)
        monthly = get_monthly_income_spending(n_months=6, account_id=acc)
        breakdown = get_category_breakdown_current_month(account_id=acc)
        balances = get_account_balances()
        budget_rows = get_budget_vs_actual(account_id=acc)
        budget_alerts = _build_budget_alerts(budget_rows)
        month_label = stats.get("current_month_label", "—")

        account_dropdown = ft.Dropdown(
            value=self._selected_account,
            options=self._get_account_options(),
            width=220,
            on_change=self._on_account_change,
        )

        top_cards = ft.Row(
            wrap=True, spacing=16, run_spacing=16,
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

        self._content.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Dashboard", size=34, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Text("Account:", size=13, color=ft.Colors.GREY_700),
                            account_dropdown,
                        ],
                    ),
                ],
            ),
            top_cards,
            ft.Divider(),
            ft.Row(
                spacing=30, wrap=True,
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
                            _section_title(f"Spending by category — {month_label}"),
                            _build_category_breakdown(breakdown),
                        ],
                    ),
                    ft.Column(
                        spacing=10,
                        controls=[
                            _section_title("Account balances"),
                            _build_account_balances(balances),
                        ],
                    ),
                ] + (
                    [
                        ft.Column(
                            spacing=10,
                            controls=[
                                _section_title("Budget alerts"),
                                budget_alerts,
                            ],
                        )
                    ] if budget_alerts is not None else []
                ),
            ),
        ]

    def build(self) -> ft.Column:
        return self._content


# Keep the function-based entry point for backward compatibility
# (flet_app.py calls build_home_page() on every navigation click)
_dashboard_instances: dict = {}


def build_home_page(page: ft.Page = None) -> ft.Column:
    """Build (or rebuild) the dashboard. Pass `page` on first call."""
    if page is not None:
        _dashboard_instances["page"] = page

    p = _dashboard_instances.get("page")

    if p is None:
        # Fallback: static version without interactivity
        stats = get_summary_stats()
        monthly = get_monthly_income_spending()
        breakdown = get_category_breakdown_current_month()
        month_label = stats.get("current_month_label", "—")
        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Dashboard", size=34, weight=ft.FontWeight.BOLD),
                ft.Row(wrap=True, spacing=16, run_spacing=16, controls=[
                    _metric_card(f"Income {month_label}", f"€{stats.get('current_month_income', 0):.0f}", ft.Colors.GREEN_50),
                    _metric_card(f"Spending {month_label}", f"€{stats.get('current_month_spending', 0):.0f}", ft.Colors.RED_50),
                    _metric_card("Total Transactions", str(stats.get("total_transactions", 0))),
                    _metric_card("Pending Review", str(stats.get("uncategorized", 0)), ft.Colors.ORANGE_50),
                ]),
                ft.Divider(),
                ft.Row(wrap=True, spacing=30, controls=[
                    ft.Column(spacing=10, controls=[_section_title("Income vs Spending"), _build_monthly_chart(monthly)]),
                    ft.Column(spacing=10, controls=[_section_title(f"Categories — {month_label}"), _build_category_breakdown(breakdown)]),
                ]),
            ],
        )

    instance = DashboardPage(p)
    return instance.build()
