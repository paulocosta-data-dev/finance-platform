import flet as ft

from app.budget.services.budget_service import (
    get_budget_vs_actual,
    get_inflation_rate,
    load_budgets,
    recalculate_budgets,
)
from app.ui.services.account_service import ALL_ACCOUNTS, get_account_ids


_CLASSIFICATION_LABELS = {
    "recurring_fixed": "Fixed recurring",
    "recurring_variable": "Variable recurring",
    "occasional": "Occasional",
}

_CLASSIFICATION_COLORS = {
    "recurring_fixed": ft.Colors.BLUE_100,
    "recurring_variable": ft.Colors.GREEN_100,
    "occasional": ft.Colors.ORANGE_100,
}


class BudgetPage:

    def __init__(self, page: ft.Page):

        self.page = page
        self._selected_account = ALL_ACCOUNTS
        self._inflation_field = ft.TextField(
            value=str(round(get_inflation_rate() * 100, 1)),
            width=90,
            suffix_text="%",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._status_text = ft.Text(size=13, color=ft.Colors.GREY_600)
        self._results_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._account_dropdown = ft.Dropdown(
            value=ALL_ACCOUNTS,
            options=self._account_options(),
            width=200,
            on_change=self._on_account_change,
        )
        self._load()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _account_options(self):
        opts = [ft.dropdown.Option(ALL_ACCOUNTS, "All Accounts")]
        for acc in get_account_ids():
            opts.append(ft.dropdown.Option(acc))
        return opts

    def _on_account_change(self, e):
        self._selected_account = e.control.value or ALL_ACCOUNTS
        self._load()
        self.page.update()

    def _load(self):

        self._results_column.controls.clear()
        data = load_budgets()
        calculated_at = data.get("calculated_at")
        rate_used = data.get("inflation_rate", 0.03)
        budgets = data.get("budgets", {})

        if not budgets:
            self._results_column.controls.append(
                ft.Text(
                    "No budget calculated yet. Press 'Calculate Budget' to begin.",
                    color=ft.Colors.GREY_500,
                )
            )
            return

        rows = get_budget_vs_actual(account_id=self._selected_account)
        month_label = ""

        # Header
        self._results_column.controls.append(
            ft.Row(
                controls=[
                    ft.Container(width=180, content=ft.Text("Category", size=12, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=90, content=ft.Text("Budget €", size=12, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=90, content=ft.Text("Actual €", size=12, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=90, content=ft.Text("Delta €", size=12, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=120, content=ft.Text("% Used", size=12, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=160, content=ft.Text("Type", size=12, weight=ft.FontWeight.BOLD)),
                ],
            )
        )
        self._results_column.controls.append(ft.Divider())

        for row in rows:

            delta_color = ft.Colors.RED_700 if row["over_budget"] else ft.Colors.GREEN_700
            delta_prefix = "+" if row["delta"] > 0 else ""

            pct = min(row["pct_used"], 100)
            bar_color = ft.Colors.RED_400 if row["over_budget"] else ft.Colors.GREEN_400
            bar_width = max(2, round(pct * 1.1))  # scale: 100% → 110px

            class_label = _CLASSIFICATION_LABELS.get(row["classification"], row["classification"])
            class_color = _CLASSIFICATION_COLORS.get(row["classification"], ft.Colors.GREY_100)

            self._results_column.controls.append(
                ft.Container(
                    border_radius=6,
                    bgcolor=ft.Colors.RED_50 if row["over_budget"] else ft.Colors.WHITE,
                    padding=ft.Padding(left=4, right=4, top=4, bottom=4),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=180,
                                content=ft.Text(row["category_id"], size=13),
                            ),
                            ft.Container(
                                width=90,
                                content=ft.Text(f"€{row['budget']:.0f}", size=13),
                            ),
                            ft.Container(
                                width=90,
                                content=ft.Text(f"€{row['actual']:.0f}", size=13),
                            ),
                            ft.Container(
                                width=90,
                                content=ft.Text(
                                    f"{delta_prefix}€{abs(row['delta']):.0f}",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=delta_color,
                                ),
                            ),
                            ft.Container(
                                width=120,
                                content=ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"{row['pct_used']:.0f}%", size=11, color=ft.Colors.GREY_600),
                                        ft.Container(
                                            height=6,
                                            width=bar_width,
                                            bgcolor=bar_color,
                                            border_radius=3,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                width=160,
                                content=ft.Container(
                                    padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                    border_radius=10,
                                    bgcolor=class_color,
                                    content=ft.Text(class_label, size=11),
                                ),
                            ),
                        ],
                    ),
                )
            )

        # Show calc details at bottom
        inflation_pct = round(rate_used * 100, 1)
        self._status_text.value = (
            f"Calculated on {calculated_at}  ·  Inflation rate used: {inflation_pct}%  ·  "
            f"Over-budget categories are highlighted in red."
        )

    # ── Detail panel: show how a budget was calculated ───────────────────────

    def _show_methodology(self, category_id: str):

        data = load_budgets()
        b = data.get("budgets", {}).get(category_id)
        if not b:
            return

        lines = [
            f"Category: {category_id}",
            f"Months in dataset: {b.get('n_months_data', '?')}",
            f"Months with spend: {b.get('n_months_active', '?')}",
            f"Frequency: {b.get('frequency', 0):.0%}",
            f"Average monthly spend: €{b.get('mean_overall', 0):.2f}",
            f"Monthly trend: {'+' if b.get('trend_monthly', 0) >= 0 else ''}€{b.get('trend_monthly', 0):.2f}/mo",
            f"Classification: {b.get('classification', '?')}",
            f"Inflation rate: {b.get('inflation_rate', 0):.1%}",
            f"Recommended budget: €{b.get('recommended', 0):.0f}",
        ]

        dlg = ft.AlertDialog(
            title=ft.Text(f"How was '{category_id}' calculated?"),
            content=ft.Column(
                width=400,
                controls=[ft.Text(line, size=13) for line in lines],
            ),
            actions=[
                ft.Button(
                    content=ft.Text("Close"),
                    on_click=lambda e: self._close_dialog(dlg),
                )
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dlg):
        dlg.open = False
        self.page.update()

    # ── Recalculate ──────────────────────────────────────────────────────────

    def _on_calculate(self, e):

        self._status_text.value = "Calculating…"
        self.page.update()

        try:
            rate_str = (self._inflation_field.value or "3").strip().replace(",", ".")
            rate = float(rate_str) / 100.0
            rate = max(0.0, min(rate, 1.0))
        except ValueError:
            rate = 0.03

        recalculate_budgets(inflation_rate=rate)
        self._inflation_field.value = str(round(rate * 100, 1))
        self._load()
        self.page.update()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Column:

        toolbar = ft.Row(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text("Inflation rate:", size=13, color=ft.Colors.GREY_700),
                        self._inflation_field,
                    ],
                ),
                ft.Button(
                    content=ft.Text("Calculate Budget"),
                    on_click=self._on_calculate,
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text("Account:", size=13, color=ft.Colors.GREY_700),
                        self._account_dropdown,
                    ],
                ),
            ],
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Text("Budget Planner", size=32, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Budget is calculated automatically from your spending history. "
                    "Set the inflation rate and press Calculate.",
                    size=13,
                    color=ft.Colors.GREY_600,
                ),
                toolbar,
                self._status_text,
                ft.Divider(),
                ft.Container(
                    expand=True,
                    content=ft.Row(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[self._results_column],
                    ),
                ),
            ],
        )
