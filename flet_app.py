import flet as ft

from app.schema.migration_runner import (
    run_pending_migrations,
)

from app.frontend.pages.atm_allocation_page import (
    ATMAllocationPage,
)

from app.frontend.pages.budget_page import (
    BudgetPage,
)

from app.frontend.pages.forecast_page import (
    ForecastPage,
)

from app.frontend.pages.health_page import (
    HealthPage,
)

from app.frontend.pages.learned_rules_page import (
    LearnedRulesPage,
)

from app.frontend.pages.home_page import (
    build_home_page,
)

from app.frontend.pages.import_page import (
    ImportPage,
)

from app.frontend.pages.recurring_page import (
    RecurringPage,
)

from app.frontend.pages.review_page import (
    ReviewPage,
)

from app.frontend.pages.reviewed_page import (
    ReviewedPage,
)

from app.frontend.pages.reviewed_recurring_page import (
    ReviewedRecurringPage,
)


class FinancePlatformApp:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

        run_pending_migrations()

        self.page.title = "Finance Platform"
        self.page.window_width = 1600
        self.page.window_height = 900
        self.page.padding = 0

        self.content = ft.Container(
            expand=True,
            padding=20,
        )

        self.review_page = ReviewPage(page)
        self.reviewed_page = ReviewedPage(page)
        self.import_page = ImportPage(page)
        self.recurring_page = RecurringPage(page)
        self.reviewed_recurring_page = ReviewedRecurringPage(page)
        self.forecast_page = ForecastPage(page)
        self.health_page = HealthPage(page)
        self.learned_rules_page = LearnedRulesPage(page)
        self.atm_allocation_page = ATMAllocationPage(page)
        self.budget_page = BudgetPage(page)

        navigation = ft.Column(
            width=250,
            controls=[
                ft.Text(
                    "Finance Platform",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                ft.Button(
                    content=ft.Text("Dashboard"),
                    on_click=lambda e: self.show_dashboard(),
                ),
                ft.Button(
                    content=ft.Text("Forecast"),
                    on_click=lambda e: self.show_forecast(),
                ),
                ft.Button(
                    content=ft.Text("Review Transactions"),
                    on_click=lambda e: self.show_review(),
                ),
                ft.Button(
                    content=ft.Text("Reviewed Transactions"),
                    on_click=lambda e: self.show_reviewed(),
                ),
                ft.Button(
                    content=ft.Text("Recurring Transactions"),
                    on_click=lambda e: self.show_recurring(),
                ),
                ft.Button(
                    content=ft.Text("Reviewed Recurring"),
                    on_click=lambda e: self.show_reviewed_recurring(),
                ),
                ft.Button(
                    content=ft.Text("Import Bank File"),
                    on_click=lambda e: self.show_import(),
                ),
                ft.Divider(),
                ft.Button(
                    content=ft.Text("Budget Planner"),
                    on_click=lambda e: self.show_budget(),
                ),
                ft.Button(
                    content=ft.Text("ATM Allocations"),
                    on_click=lambda e: self.show_atm_allocations(),
                ),
                ft.Button(
                    content=ft.Text("Learned Rules"),
                    on_click=lambda e: self.show_learned_rules(),
                ),
                ft.Button(
                    content=ft.Text("Health Check"),
                    on_click=lambda e: self.show_health_check(),
                ),
            ],
        )

        layout = ft.Row(
            expand=True,
            controls=[
                ft.Container(
                    width=280,
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    content=navigation,
                ),
                self.content,
            ],
        )

        self.page.add(layout)
        self.show_dashboard()

    def show_dashboard(self):
        self.content.content = build_home_page(page=self.page)
        self.page.update()

    def show_forecast(self):
        self.content.content = self.forecast_page.build()
        self.page.update()

    def show_review(self):
        self.review_page.load_transactions()
        self.content.content = self.review_page.build()
        self.page.update()

    def show_reviewed(self):
        self.reviewed_page.load_transactions()
        self.content.content = self.reviewed_page.build()
        self.page.update()

    def show_recurring(self):
        self.recurring_page.load_recurring()
        self.content.content = self.recurring_page.build()
        self.page.update()

    def show_reviewed_recurring(self):
        self.reviewed_recurring_page.load_overrides()
        self.content.content = self.reviewed_recurring_page.build()
        self.page.update()

    def show_import(self):
        self.content.content = self.import_page.build()
        self.page.update()

    def show_budget(self):
        self.budget_page._load()
        self.content.content = self.budget_page.build()
        self.page.update()

    def show_atm_allocations(self):
        self.atm_allocation_page._load_atm_list()
        self.content.content = self.atm_allocation_page.build()
        self.page.update()

    def show_learned_rules(self):
        self.learned_rules_page._load()
        self.content.content = self.learned_rules_page.build()
        self.page.update()

    def show_health_check(self):
        self.content.content = self.health_page.build()
        self.page.update()


def main(page: ft.Page):
    FinancePlatformApp(page)


ft.run(main)
