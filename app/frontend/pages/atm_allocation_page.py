import flet as ft

from app.allocations.services.allocation_service import (
    get_atm_transactions,
    get_existing_allocations,
    save_transaction_allocations,
)
from app.ui.services.category_service import (
    load_available_categories,
)


class SplitRow:
    """One row in the split editor: category dropdown + amount field + note."""

    def __init__(self, available_categories: list[str]):

        self.category = ft.Dropdown(
            value=available_categories[0] if available_categories else "",
            options=[ft.dropdown.Option(c) for c in available_categories],
            width=200,
        )

        self.amount = ft.TextField(
            hint_text="0.00",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.note = ft.TextField(
            hint_text="Note (optional)",
            width=220,
        )

        self._remove_btn = None

    def set_remove_callback(self, cb):
        self._remove_cb = cb
        self._remove_btn = ft.Button(
            content=ft.Text("✕", size=12),
            on_click=lambda e: cb(),
        )

    def build(self) -> ft.Row:

        controls = [self.category, self.amount, self.note]

        if self._remove_btn:
            controls.append(self._remove_btn)

        return ft.Row(controls=controls, spacing=8)

    def get_data(self) -> dict | None:

        try:
            amount = float(self.amount.value or "0")
        except ValueError:
            amount = 0.0

        if amount <= 0:
            return None

        return {
            "category_id": self.category.value or "uncategorized",
            "amount": amount,
            "note": self.note.value or "",
        }


class ATMAllocationPage:

    def __init__(self, page: ft.Page):

        self.page = page
        self.available_categories = load_available_categories()
        self.split_rows: list[SplitRow] = []

        self.atm_list_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        self.editor_column = ft.Column(spacing=8)
        self.status_text = ft.Text()
        self.remainder_text = ft.Text(size=13, color=ft.Colors.GREY_700)

        self._selected_transaction = None
        self._selected_amount = 0.0

        self._load_atm_list()

    # ── ATM transaction list ─────────────────────────────────────────────────

    def _load_atm_list(self):

        self.atm_list_column.controls.clear()

        df = get_atm_transactions()

        if df.empty:
            self.atm_list_column.controls.append(
                ft.Text("No pending ATM withdrawals.", color=ft.Colors.GREY_500)
            )
            return

        self.atm_list_column.controls.append(
            ft.Row(
                controls=[
                    ft.Container(width=120, content=ft.Text("Date", weight=ft.FontWeight.BOLD, size=12)),
                    ft.Container(width=120, content=ft.Text("Amount", weight=ft.FontWeight.BOLD, size=12)),
                    ft.Container(width=300, content=ft.Text("Description", weight=ft.FontWeight.BOLD, size=12)),
                    ft.Container(width=100, content=ft.Text("Action", weight=ft.FontWeight.BOLD, size=12)),
                ],
            )
        )
        self.atm_list_column.controls.append(ft.Divider())

        for _, row in df.iterrows():
            txn_id = row["transaction_id"]
            date_str = str(row["transaction_date"])[:10]
            amount = abs(float(row["amount"]))
            description = str(row.get("description", ""))[:60]

            allocate_btn = ft.Button(
                content=ft.Text("Allocate", size=12),
                on_click=lambda e, tid=txn_id, amt=amount, desc=description:
                    self._open_editor(tid, amt, desc),
            )

            self.atm_list_column.controls.append(
                ft.Row(
                    controls=[
                        ft.Container(width=120, content=ft.Text(date_str, size=13)),
                        ft.Container(width=120, content=ft.Text(f"€{amount:.2f}", size=13)),
                        ft.Container(width=300, content=ft.Text(description, size=13)),
                        ft.Container(width=100, content=allocate_btn),
                    ],
                )
            )

    # ── Split editor ─────────────────────────────────────────────────────────

    def _open_editor(self, transaction_id: str, amount: float, description: str):

        self._selected_transaction = transaction_id
        self._selected_amount = amount
        self.split_rows = []
        self.status_text.value = ""

        self.editor_column.controls.clear()

        self.editor_column.controls.append(
            ft.Text(
                f"Allocating: {description}  |  Total: €{amount:.2f}",
                size=14,
                weight=ft.FontWeight.BOLD,
            )
        )

        self.editor_column.controls.append(
            ft.Text(
                "Split the withdrawal into categories. Amounts must add up to the total.",
                size=12,
                color=ft.Colors.GREY_600,
            )
        )

        self._split_rows_container = ft.Column(spacing=6)
        self.editor_column.controls.append(self._split_rows_container)

        self.editor_column.controls.append(self.remainder_text)

        self.editor_column.controls.append(
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("+ Add split"),
                        on_click=lambda e: self._add_split_row(),
                    ),
                    ft.Button(
                        content=ft.Text("Save allocations"),
                        on_click=lambda e: self._save(),
                    ),
                ],
                spacing=12,
            )
        )

        # Prefill with any existing allocations
        existing = get_existing_allocations(transaction_id)

        if not existing.empty:
            for _, erow in existing.iterrows():
                self._add_split_row(
                    category=str(erow.get("category_id", "")),
                    amount=str(abs(float(erow.get("amount", 0)))),
                    note=str(erow.get("allocation_note") or ""),
                )
        else:
            self._add_split_row()

        self._update_remainder()
        self.page.update()

    def _add_split_row(
        self,
        category: str = "",
        amount: str = "",
        note: str = "",
    ):

        row = SplitRow(self.available_categories)

        if category:
            row.category.value = category
        if amount:
            row.amount.value = amount
        if note:
            row.note.value = note

        def remove(r=row):
            self.split_rows.remove(r)
            self._split_rows_container.controls = [
                sr.build() for sr in self.split_rows
            ]
            self._update_remainder()
            self.page.update()

        row.set_remove_callback(remove)

        # Update remainder whenever amount changes
        original_on_change = row.amount.on_change

        def on_amount_change(e):
            self._update_remainder()
            self.page.update()

        row.amount.on_change = on_amount_change

        self.split_rows.append(row)
        self._split_rows_container.controls.append(row.build())
        self._update_remainder()
        self.page.update()

    def _update_remainder(self):

        if self._selected_transaction is None:
            return

        try:
            allocated = sum(
                float(r.amount.value or "0")
                for r in self.split_rows
            )
        except ValueError:
            allocated = 0.0

        remainder = round(self._selected_amount - allocated, 2)

        color = ft.Colors.GREEN_700 if remainder == 0 else (
            ft.Colors.RED_700 if remainder < 0 else ft.Colors.ORANGE_700
        )

        self.remainder_text.value = f"Remainder: €{remainder:.2f}"
        self.remainder_text.color = color

    def _save(self):

        if self._selected_transaction is None:
            return

        splits = [r.get_data() for r in self.split_rows]
        splits = [s for s in splits if s is not None]

        if not splits:
            self.status_text.value = "Add at least one split."
            self.page.update()
            return

        result = save_transaction_allocations(
            transaction_id=self._selected_transaction,
            splits=splits,
        )

        if "error" in result:
            self.status_text.value = f"Error: {result['error']}"
        else:
            self.status_text.value = (
                f"Saved {result['saved']} allocations. "
                f"Total: €{result['total_allocated']:.2f}. "
                f"Remainder: €{result['remainder']:.2f}."
            )
            self._selected_transaction = None
            self.editor_column.controls.clear()
            self._load_atm_list()

        self.page.update()

    # ── Page build ───────────────────────────────────────────────────────────

    def build(self) -> ft.Column:

        return ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "ATM Allocations",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Split ATM withdrawals into spending categories.",
                    size=13,
                    color=ft.Colors.GREY_600,
                ),
                self.status_text,
                ft.Divider(),
                ft.Row(
                    expand=True,
                    spacing=30,
                    controls=[
                        ft.Container(
                            width=700,
                            content=ft.Column(
                                expand=True,
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Text(
                                        "Pending withdrawals",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    self.atm_list_column,
                                ],
                            ),
                        ),
                        ft.VerticalDivider(),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Text(
                                        "Split editor",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    self.editor_column,
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        )
