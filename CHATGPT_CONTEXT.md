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
│   ├── domain/                  # Pydantic models (Transaction, RawTransaction, ImportFile, enums)
│   ├── ingestion/               # Bank file adapters (CGD, Activo) + normalizer
│   ├── pipelines/               # Ingestion and normalization pipelines
│   ├── semantic/                # Semantic type detection (PURCHASE, SALARY, ATM_WITHDRAWAL, etc.)
│   ├── category/                # Category rule matching + recurring detection
│   ├── merchant/                # Merchant identification
│   ├── entity/                  # Entity detection (merchant vs. financial flow)
│   ├── cashflow/                # Forecasting models + monthly cashflow service
│   ├── recurring/               # Recurring override service
│   ├── overrides/               # Human corrections service
│   ├── storage/                 # Parquet read/write for transactions, raw, imports
│   ├── seeds/                   # Base reference data (categories, semantic types)
│   ├── schema/                  # Schema versioning
│   ├── utils/                   # Hashing utilities
│   ├── ui/services/             # Services called by UI pages
│   └── frontend/pages/          # Flet UI pages (one file per page)
├── tests/                       # Unit tests (unittest-based, run via Health Check page)
│   ├── helpers.py
│   ├── test_normalizer.py
│   ├── test_category.py
│   ├── test_forecasting.py
│   └── test_recurring.py
└── data/
    └── processed/               # Parquet files (created at runtime, not in git)
        ├── transactions.parquet
        ├── raw_transactions.parquet
        ├── imports.parquet
        ├── transaction_overrides.parquet
        ├── recurring_overrides.parquet
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

Current pages: Dashboard, Forecast, Review Transactions, Reviewed Transactions, Recurring Transactions, Reviewed Recurring, Import Bank File, Health Check.

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

## Schema migration system

`app/schema/` contains a full forward-migration engine.

**Files:**
- `versions.py` — single source of truth for current schema version per dataset (`CURRENT_TRANSACTION_SCHEMA_VERSION = 1`, same for raw and imports)
- `migrations.py` — migration functions + `MIGRATIONS` registry: `dict[dataset_key → list[(from_v, to_v, fn)]]`
- `migration_runner.py` — `run_pending_migrations()` reads each parquet file, detects its version via `df["schema_version"].min()`, and applies any pending steps in order

**How it runs:** `flet_app.py` calls `run_pending_migrations()` at the very start of `FinancePlatformApp.__init__()`, before any page is instantiated.

**How to add a new migration:**
1. Bump the relevant constant in `versions.py` (e.g. `CURRENT_TRANSACTION_SCHEMA_VERSION = 2`)
2. Add a function `_transactions_v1_to_v2(df) -> df` in `migrations.py`
3. Append `(1, 2, _transactions_v1_to_v2)` to `MIGRATIONS["transactions"]`

Never modify existing migration entries — only append.

---

## Path resolution (portable across dev and packaged exe)

`app/utils/paths.py` centralises all path resolution:

```python
def data_path(relative: str) -> Path:
    """User data files (parquet, yaml rules). Next to exe when packaged."""
    ...

def resource_path(relative: str) -> Path:
    """Bundled read-only resources (YAML rule files). In sys._MEIPASS when packaged."""
    ...
```

All services use these functions — no hardcoded strings anywhere. This ensures the app works both via `flet run flet_app.py` and as a bundled `.exe`.

---

## Learned rules lifecycle

`app/category/services/learned_rule_service.py` manages rules written to `data/processed/learned_category_rules.yaml`.

**Functions:**
- `append_learned_rule(description, category_id)` — adds or updates a rule; same pattern → updates in-place (no duplicates)
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

## What is NOT yet built

- Allocation/splitting engine (ATM withdrawals, cash transactions)
- Yearly budget generation
- Spending anomaly detection
- Packaging as standalone executable (currently needs Python + `flet run flet_app.py`) — path resolution is done, PyInstaller spec is ready; blocked by disk space on build machine
- Multi-account support in the UI

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

These are listed roughly in order of impact vs. effort. Use this section to brief an AI assistant on what to work on next.

### 1. Packaging for non-coders (highest real-world impact)

Right now the app requires Python and a terminal. The product vision says zero terminal for end users.

What to explore:
- `pyinstaller` to bundle the app into a `.exe`
- Flet has a built-in `flet pack` command (wraps PyInstaller) — check if it handles Pandas/PyArrow correctly
- The data folder needs to live alongside the executable, not inside it
- Test on a machine without Python installed

Key risk: PyArrow and DuckDB are notoriously difficult to bundle with PyInstaller. Research this first before building anything.

### 2. Schema migration system ✅ DONE

`app/schema/` is fully implemented. See the **Schema migration system** section above for details.

### 3. ATM allocation workflow

`ATM_WITHDRAWAL` transactions have `is_terminal_spending=False` and `resolution_status=MANUAL_REVIEW_REQUIRED` because they need to be split into sub-categories (e.g. "withdrew €200: €80 groceries, €120 leisure"). The data model already has `ALLOCATED` as a status — the workflow just doesn't exist yet.

What to build:
- A split/allocation UI for ATM transactions in the Review page
- An `allocations.parquet` store (the domain model `app/domain/allocations.py` already exists)
- Logic to mark parent transaction as `ALLOCATED` and create child allocation records

### 4. Learned rules lifecycle ✅ DONE

See the **Learned rules lifecycle** section above for full details.

### 5. Dashboard with real cashflow visibility

The current Dashboard shows transaction counts. What a user actually needs:
- Monthly income vs. spending (last 3–6 months)
- Category breakdown for current month
- Running balance trend
- Comparison: this month vs. same month last year

All the data is already there. This is mostly a visualisation task. Flet supports basic charting or you can use a Canvas widget.

### 6. Multi-account awareness in the UI

Transactions have `account_id` but the UI never exposes it — everything is shown as a single pool. For a household with 2–3 accounts this matters.

What to add:
- Account filter on the Review, Forecast, and Dashboard pages
- Per-account balance tracking
- Cross-account transfer detection (already partially handled via `INTERNAL_TRANSFER` semantic type)

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

## Learned rules lifecycle

`app/category/services/learned_rule_service.py` manages rules written to `data/processed/learned_category_rules.yaml`.

**Functions:**
- `append_learned_rule(d