import flet as ft

from app.category.services.learned_rule_service import (
    delete_learned_rule,
    get_conflicts,
    load_learned_rules,
    set_rule_enabled,
)


class LearnedRulesPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page
        self.status_text = ft.Text()
        self.rules_column = ft.Column(
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self.conflicts_column = ft.Column(
            spacing=6,
        )
        self._load()

    def _load(self):

        self.rules_column.controls.clear()
        self.conflicts_column.controls.clear()

        rules_config = load_learned_rules()
        rules = rules_config.get(
            "rules", []
        ) or []

        conflicts = get_conflicts()

        # ── Conflict banner ──────────────────────────────
        if conflicts:
            for conflict in conflicts:
                patterns = conflict["pattern"]
                cats = ", ".join(
                    r.get("category_id", "?")
                    for r in conflict["rules"]
                )
                self.conflicts_column.controls.append(
                    ft.Container(
                        bgcolor=ft.Colors.ORANGE_100,
                        padding=ft.Padding(
                            left=12,
                            right=12,
                            top=6,
                            bottom=6,
                        ),
                        border_radius=6,
                        content=ft.Text(
                            f"⚠ Conflict: \"{patterns}\" "
                            f"maps to: {cats}",
                            size=12,
                            color=ft.Colors.ORANGE_900,
                        ),
                    )
                )

        # ── Rule rows ────────────────────────────────────
        if not rules:
            self.rules_column.controls.append(
                ft.Text(
                    "No learned rules yet.",
                    color=ft.Colors.GREY_500,
                )
            )
            return

        # Header row
        self.rules_column.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        width=300,
                        content=ft.Text(
                            "Pattern",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            "Category",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                    ),
                    ft.Container(
                        width=80,
                        content=ft.Text(
                            "Enabled",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            "Actions",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                    ),
                ],
            )
        )

        self.rules_column.controls.append(
            ft.Divider()
        )

        for rule in rules:
            self.rules_column.controls.append(
                self._build_rule_row(rule)
            )

    def _build_rule_row(
        self,
        rule: dict,
    ) -> ft.Row:

        rule_id = rule.get("rule_id", "")
        pattern = rule.get("pattern", "")
        category = rule.get(
            "category_id", ""
        )
        enabled = rule.get("enabled", True)

        enabled_toggle = ft.Checkbox(
            value=enabled,
            on_change=lambda e,
            rid=rule_id: self._toggle(
                rid,
                e.control.value,
            ),
        )

        delete_btn = ft.Button(
            content=ft.Text(
                "Delete",
                size=12,
            ),
            on_click=lambda e,
            rid=rule_id: self._delete(rid),
        )

        row_color = (
            ft.Colors.WHITE
            if enabled
            else ft.Colors.GREY_200
        )

        return ft.Container(
            bgcolor=row_color,
            border_radius=4,
            padding=ft.Padding(
                left=4,
                right=4,
                top=2,
                bottom=2,
            ),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=300,
                        content=ft.Text(
                            pattern,
                            size=13,
                            color=(
                                ft.Colors.GREY_500
                                if not enabled
                                else None
                            ),
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            category,
                            size=13,
                        ),
                    ),
                    ft.Container(
                        width=80,
                        content=enabled_toggle,
                    ),
                    ft.Container(
                        width=120,
                        content=delete_btn,
                    ),
                ],
            ),
        )

    def _toggle(
        self,
        rule_id: str,
        enabled: bool,
    ):

        set_rule_enabled(rule_id, enabled)
        self._load()
        self.page.update()

    def _delete(
        self,
        rule_id: str,
    ):

        delete_learned_rule(rule_id)
        self._load()
        self.status_text.value = (
            f"Rule '{rule_id}' deleted."
        )
        self.page.update()

    def build(self) -> ft.Column:

        return ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "Learned Rules",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Rules created automatically "
                    "when you correct a category. "
                    "Disable or delete rules that "
                    "are wrong.",
                    size=13,
                    color=ft.Colors.GREY_600,
                ),
                self.status_text,
                self.conflicts_column,
                ft.Divider(),
                ft.Container(
                    expand=True,
                    content=ft.Row(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            self.rules_column
                        ],
                    ),
                ),
            ],
        )
