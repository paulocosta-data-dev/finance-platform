# Finance Platform — Project Context for AI Assistants

Paste this file at the start of a conversation so the assistant has full context.

---

## What this project is

A local-first personal finance desktop application built in Python.
Target users: non-technical people (family usage). No cloud, no paid infrastructure, no terminal required to use it.

GitHub: https://github.com/paulocosta-data-dev/finance-platform

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.13+ |
| UI framework | Flet 0.85 (desktop GUI) |
| Data validation | Pydantic v2 |
| Data processing | Pandas, PyArrow |
| Analytical queries | DuckDB |
| Storage format | Parquet (local files) |
| Config/rules | YAML |
| Bank file imports | Excel (.xlsx) via OpenPyXL |

---

## Core principles

1. **Local-first** — runs entirely on the user's machine, no internet required.
2. **Immutable pipelines** — `transactions.parquet` is never hand-edited. Corrections layer on top via overrides.
3. **Human-in-the-loop** — users correct categorizations through the UI; the system learns from those corrections.
4. **Non-coder UX** — no CLI, no config files, everything through the GUI.

---

## Project structure

```
finance-platform/
├── flet_app.py                  # App entry point — run with: flet run flet_app.py
├── start.bat                    # Windows convenience launcher
├── app/
│   ├── domain/                  # Pydantic models (Transaction, RawTransaction, ImportFile, Allocation, enums)
│   ├── ingestion/               # Bank file adapters (CGD, Activo) + normalizer
│   ├── pipelines/               # Ingestion and normalization pipelines
│   ├── semantic/                # Semantic type detection (PURCHASE, SALARY, ATM_WITHDRAWAL, etc.)
│   ├── category/                # Category rule matching + recurring detection
│   ├── merchant/                # Merchant identification
│   ├── entity/                  # Entity detection (merchant vs. financial flow)
│   ├── cashflow/                # Forecasting models + monthly cashflow + dashboard service
│   ├── recurring/               # Recurring override service
│   ├── overrides/               # Human corrections service
│   ├── allocations/services/    # ATM allocation service
│   ├── storage/                 # Parquet read/write for transactions, raw, imports, allocations
│   ├── seeds/                   # Base reference data (categories, semantic types)
│   ├── schema/                  # Schema versioning + migration runner
│   ├── utils/                   # paths.py (data_path / resource_path)
│   ├── ui/services/             # Services called by UI pages (account, category, transaction, etc.)
│   └── frontend/pages/          # Flet UI pages (one file per page)
├── tests/                       # Unit tests (unittest-based, run via Health Check page)
│   ├── helpers.py
│   ├── test_normalizer.py
│   ├── test_category.py
│   ├── test_forecasting.py
│   └── test_recurring.py
└── data/
    └── processed/               # Parquet/YAML files (created at runtime, not in git)
        ├── transactions.parquet
        ├── raw_transactions.parquet
        ├── imports.parquet
        ├── transaction_overrides.parquet
        ├── recurring_overrides.parquet
        ├── allocations.parquet
        └── learned_category_rules.yaml
```

All `data/processed/` files are created automatically on first use — no setup script needed.

---

## Key data models

### Transaction (app/domain/transactions.py)

```python
class Transaction(BaseModel):
    transaction_id: str
    schema_version: int
    raw_transaction_id: str
    account_id: str
    transaction_date: date
    booking_date: date
    description: str               # raw from bank
    normalized_description: str    # lowercase, slashes/dots → spaces, collapsed
    amount: Decimal
    currency: str                  # always "EUR"
    direction: DirectionEnum       # DEBIT | CREDIT
    semantic_type_id: str          # e.g. "PURCHASE", "SALARY", "ATM_WITHDRAWAL"
    category_id: str               # default "uncategorized"
    matched_rule_id: str | None
    semantic_confidence: float
    resolution_status: ResolutionStatusEnum  # MANUAL_REVIEW_REQUIRED | AUTO_RESOLVED | MANUALLY_RESOLVED | ALLOCATED
    is_terminal_spending: bool
    entity_name: str | None
    entity_type: str | None        # "merchant" | "financial_flow"
    entity_confidence: float
    created_at: datetime
```

### Enums

```python
class DirectionEnum(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class ResolutionStatusEnum(str, Enum):
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    AUTO_RESOLVED = "AUTO_RESOLVED"
    MANUALLY_RESOLVED = "MANUALLY_RESOLVED"
    ALLOCATED = "ALLOCATED"
```

---

## Processing pipeline (what happens when a bank file is imported)

1. User drops an `.xlsx` file in the Import page.
2. `IngestionLoader` detects the bank type (CGD or Activo) by inspecting column headers.
3. The adapter extracts `RawTransaction` objects and saves them to `raw_transactions.parquet`.
4. `normalize_raw_transaction()` runs for each raw transaction:
   - normalizes description (lowercase, punctuation → spaces)
   - detects direction from amount sign
   - runs semantic engine → assigns `semantic_type_id`
   - runs category engine → assigns `category_id`
   - runs entity detection → assigns `entity_name`
5. Normalized transactions saved to `transactions.parquet`.
6. Duplicates handled by hash: raw by `raw_transaction_id` (keep first), normalized by `transaction_id` (keep last).

---

## Category engine

Rules loaded from `app/category/rules/category_rules.yaml`.

```yaml
- rule_id: groceries
  enabled: true
  priority: 100          # higher = checked first
  category_id: groceries
  confidence: 0.98
  match:
    semantic_type_ids:   # empty list = match any
      - CARD_PURCHASE
    description_contains:  # empty list = match any; any keyword suffices
      - continente
      - pingo doce
```

ALL conditions must pass. Empty condition list matches everything.

---

## Forecasting models (app/cashflow/services/forecasting_models.py)

```python
forecast_fixed_recurring_amount(transactions, cadence: str) -> float
# Average abs(amount) × cadence multiplier:
# weekly→4, biweekly→2, monthly→1, quarterly→1/3, yearly→1/12, irregular→1

forecast_behavioral_amount(transactions) -> float
# Sums abs(amounts) per calendar month, returns average across active months
```

Input: list of dicts with `amount` and `transaction_date` keys.

---

## UI structure (Flet 0.85)

Entry point: `flet_app.py` → `FinancePlatformApp` owns all pages and handles navigation.

Navigation: left sidebar buttons swap `self.content.content` and call `self.page.update()`.

Page patterns:
- **Function-based**: `def build_X_page() -> ft.Column`
- **Class-based**: `class XPage: def __init__(self, page): ... def build(self) -> ft.Column`

Current pages: Dashboard, Forecast, Review Transactions, Reviewed Transactions, Recurring Transactions, Reviewed Recurring, Import Bank File, ATM Allocations, Learned Rules, Health Check.

**Flet 0.85 API notes** (these differ from newer Flet docs):
- Buttons: `ft.Button(content=ft.Text("label"), on_click=handler)` — NOT `ft.ElevatedButton(text=...)`
- Padding: `ft.Padding(left=x, right=x, top=y, bottom=y)` — NOT `ft.padding.symmetric(...)`
- Colors: `ft.Colors.BLUE_50`, `ft.Colors.GREEN_700`, etc.
- Scrollable column: `ft.Column(scroll=ft.ScrollMode.AUTO)`
- Background threads: `threading.Thread(target=fn, daemon=True).start()`

---

## Test suite

44 unit tests in `tests/`, using Python's built-in `unittest`.
Run from inside the app via the **Health Check** page — no terminal needed.

| File | What it tests |
|---|---|
| `test_normalizer.py` | `normalize_description`, `determine_direction` |
| `test_category.py` | `category_rule_matches` — all condition combinations |
| `test_forecasting.py` | `forecast_fixed_recurring_amount`, `forecast_behavioral_amount` |
| `test_recurring.py` | `detect_recurring_transactions` — mocked parquet and overrides |

`tests/helpers.py` — `make_transaction(...)` builds a valid `Transaction` with sensible defaults.

---

## Path resolution (portable across dev and packaged exe)

`app/utils/paths.py` centralises all path resolution:

```python
def data_path(relative: str) -> Path:
    """User data files (parquet, yaml rules). Next to exe when packaged."""

def resource_path(relative: str) -> Path:
    """Bundled read-only resources (YAML rule files). In sys._MEIPASS when packaged."""
```

All services use these functions — no hardcoded strings anywhere. This ensures the app works both via `flet run flet_app.py` and as a bundled `.exe`.

---

## Schema migration system

`app/schema/` contains a full forward-migration engine.

**Files:**
- `versions.py` — single source of truth for current schema version per dataset (`CURRENT_TRANSACTION_SCHEMA_VERSION = 1`, same for raw and imports)
- `migrations.py` — migration functions + `MIGRATIONS` registry: `dict[dataset_key → list[(from_v, to_v, fn)]]`
- `migration_runner.py` — `run_pending_migrations()` reads each parquet file, detects its version via `df["schema_version"].min()`, and applies any pending steps in order

**How it runs:** `flet_app.py` calls `run_pending_migrations()` at the very start of `FinancePlatformApp.__init__()`, before any page is instantiated.

**How to add a new migration:**
1. Bump the relevant constant in `versions.py`
2. Add a function `_transactions_v1_to_v2(df) -> df` in `migrations.py`
3. Append `(1, 2, _transactions_v1_to_v2)` to `MIGRATIONS["transactions"]`

Never modify existing migration entries — only append.

---

## Learned rules lifecycle

`app/category/services/learned_rule_service.py` manages rules written to `data/processed/learned_category_rules.yaml`.

**Functions:**
- `append_learned_rule(description, category_id)` — adds or updates; same pattern → updates in-place (no duplicates)
- `delete_learned_rule(rule_id)` — removes by rule ID; returns bool
- `set_rule_enabled(rule_id, enabled)` — toggles without deleting; returns bool
- `get_conflicts()` — returns list of `{"pattern": str, "rules": [...]}` where the same pattern maps to different categories
- `load_learned_rules()` — returns full YAML dict; creates the file if missing

**UI page:** `app/frontend/pages/learned_rules_page.py` — table with enable/disable toggle and delete per row; orange conflict banner at top when contradictions are detected. Accessible via "Learned Rules" in the sidebar.

**Rule schema in YAML:**
```yaml
- rule_id: learned_continente
  match_type: contains
  pattern: continente
  category_id: groceries
  confidence: 0.99
  enabled: true
```

---

## ATM allocation workflow

ATM withdrawals (`semantic_type_id = ATM_WITHDRAWAL`) need to be split into sub-categories before they count as resolved spending.

**Storage:** `data/processed/allocations.parquet` via `app/storage/allocations.py`

**Domain model:** `app/domain/allocations.py` — `Allocation(allocation_id, transaction_id, category_id, amount, allocation_note, created_by, created_at)`

**Service:** `app/allocations/services/allocation_service.py`
- `get_atm_transactions()` — returns ATM withdrawals with `resolution_status != ALLOCATED`
- `get_existing_allocations(transaction_id)` — returns any already-saved splits
- `save_transaction_allocations(transaction_id, splits)` — persists splits and marks parent as `ALLOCATED`

**UI page:** `app/frontend/pages/atm_allocation_page.py` — two-panel layout: left lists pending withdrawals, right is a split editor with add/remove rows, live remainder counter (green when zero, red when over), saves to parquet on confirm. Accessible via "ATM Allocations" in the sidebar.

---

## Dashboard (real cashflow visibility)

`app/frontend/pages/home_page.py` powered by `app/cashflow/services/dashboard_service.py`.

**Top metric cards:** current month income, current month spending, total transactions, categorised count + coverage %, pending review count.

**Monthly income vs spending chart:** last 6 months as side-by-side vertical bars (green = income, red = spending). Built natively with Flet containers.

**Category breakdown:** horizontal bar chart for the current month's spending by category (top 12), showing amount and % of total.

**Account balances panel:** always shows all accounts — `account_id`, total income, total spending, net balance (green/red).

**`dashboard_service.py` functions** (all accept optional `account_id` parameter):
- `get_summary_stats(account_id)` — headline numbers for the metric cards
- `get_monthly_income_spending(n_months, account_id)` — list of `{"month", "income", "spending"}` dicts
- `get_category_breakdown_current_month(account_id)` — list of `{"category_id", "total"}` dicts

---

## Multi-account awareness

`app/ui/services/account_service.py` — central account helpers:
- `get_account_ids()` — sorted list of distinct `account_id` values in `transactions.parquet`
- `get_account_balances()` — list of `{"account_id", "income", "spending", "balance"}` dicts
- `filter_by_account(df, account_id)` — filters any DataFrame; pass `ALL_ACCOUNTS = "__all__"` to skip
- `ALL_ACCOUNTS = "__all__"` — sentinel constant used throughout

**Pages with account filter dropdown:**
- **Dashboard** — dropdown in top-right; all metric cards, chart, and breakdown update on change
- **Review Transactions** — account dropdown above the transaction list
- **Reviewed Transactions** — account dropdown next to the search field

**`transaction_service.py`** extended with:
- `load_unresolved_transactions_for_account(account_id)`
- `load_all_transactions_for_account(account_id)`

---

## What is NOT yet built

- Yearly budget generation
- Spending anomaly detection
- Packaging as standalone executable (currently needs Python + `flet run flet_app.py`) — path resolution is done, PyInstaller spec is ready; blocked by disk space on build machine

---

## How to run

```bash
pip install -r requirements.txt
flet run flet_app.py
```

Or double-click `start.bat` on Windows.
Data files are created automatically in `data/processed/` on first import.

---

## Next steps — suggested priorities

### 1. Packaging for non-coders — partially done
Path resolution and PyInstaller spec are ready. Resume by running `pyinstaller "Finance Platform.spec"` after clearing disk space.

### 2. Schema migration system ✅ DONE
See the **Schema migration system** section above.

### 3. ATM allocation workflow ✅ DONE
See the **ATM allocation workflow** section above.

### 4. Learned rules lifecycle ✅ DONE
See the **Learned rules lifecycle** section above.

### 5. Dashboard with real cashflow visibility ✅ DONE
See the **Dashboard** section above.

### 6. Multi-account awareness in the UI ✅ DONE
See the **Multi-account awareness** section above.

### 7. Yearly budget planner (next natural step)
Allow the user to set a monthly spending target per category. Compare actuals vs budget on the dashboard. Store in `data/processed/budget.yaml`. Show over/under indicators on the category breakdown.

### 8. Spending anomaly detection
Flag transactions that are unusually large compared to the category's historical average. Surface these on the Review page with a visual indicator.
