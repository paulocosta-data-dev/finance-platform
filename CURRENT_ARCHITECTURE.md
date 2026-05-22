# Finance Platform — Current Architecture

## Repository

GitHub:
https://github.com/paulocosta-data-dev/finance-platform

---

# Product Vision

A local-first personal finance platform for non-technical users.

The system should:
- ingest bank statements,
- normalize and classify transactions,
- learn from human corrections,
- support transaction allocation/splitting,
- forecast upcoming expenses,
- predict future spending,
- generate yearly budgets,
- be fully usable through a simple GUI by non-coders.

Target user:
- non-technical people,
- family usage,
- privacy-first local execution,
- zero cloud dependency,
- zero paid infrastructure.

---

# Core Architectural Principles

## 1. Local-first

The platform runs locally:
- Docker only for development,
- future direction:
  - desktop executable,
  - packaged local application.

No cloud dependency required.

---

## 2. Immutable pipelines

transactions.parquet should never be manually edited.

Corrections are layered:
- overrides,
- learned rules,
- re-materialization pipelines.

---

## 3. Human-in-the-loop learning

Users do NOT create rules manually.

The system:
- observes corrections,
- proposes bulk application,
- learns categorization rules.

---

## 4. Separation of concerns

Different layers:
- ingestion,
- normalization,
- semantic classification,
- categorization,
- overrides,
- learned behavior,
- UI workflows.

---

# Current Storage Layer

## Existing datasets

### imports.parquet

Tracks imports.

---

### raw_transactions.parquet

Raw ingested transactions.

---

### transactions.parquet

Normalized silver-layer transactions.

Contains:
- semantic classification,
- category assignment,
- normalized descriptions.

---

### transaction_overrides.parquet

Human corrections layer.

Contains:
- transaction_id,
- override_category_id,
- override_timestamp.

---

### learned_category_rules.yaml

Auto-generated learned rules.

Generated from:
- human corrections,
- apply-to-all workflows.

---

# Current Semantic Layer

Implemented:
- semantic rules engine,
- semantic matching,
- normalized descriptions,
- semantic confidence,
- matched rule IDs.

Current semantic types include:
- CARD_PURCHASE
- PEER_TRANSFER
- INTERNAL_TRANSFER
- INTEREST_PAYMENT
- ATM_WITHDRAWAL
- UNKNOWN

---

# Current Categorization Layer

Implemented:
- category rules YAML,
- category matching,
- unresolved detection.

Current categories include:
- groceries
- restaurant
- telecom
- books
- pharmacy
- savings
- uncategorized

---

# Current Streamlit UI

Current purpose:
- unresolved transaction review workflow.

Implemented:
- unresolved transactions table,
- category dropdown,
- create new category,
- apply-to-all checkbox,
- pending corrections,
- save corrections,
- learned rule generation.

Current architecture:
- modular services,
- no giant monolithic streamlit file.

---

# Current UI Structure

app/ui/

- services/
  - category_service.py
  - review_service.py
  - transaction_service.py

streamlit_app.py

---

# Current Major Problems

## 1. Streamlit state bugs

Issues:
- apply-all not fully working,
- stale session state,
- optimistic UI inconsistencies.

---

## 2. Pipeline materialization flow

Current flow:
- Streamlit writes overrides,
- normalization pipeline reruns.

Needs stabilization.

---

## 3. Learned rules lifecycle

Still missing:
- deduplication,
- conflict resolution,
- rule confidence management,
- rule review UI.

---

## 4. Category persistence

New categories currently only exist in session state.

Need:
- persistent category registry.

---

# Architectural Decisions Already Made

## Accepted

- local-first architecture,
- parquet-based storage,
- replayable pipelines,
- human correction layering,
- adaptive learned rules,
- Streamlit MVP,
- non-coder-first UX.

---

## Rejected

- cloud-first SaaS,
- direct parquet editing,
- hardcoded categories,
- giant monolithic UI files,
- immediate dashboard-first approach.

---

# Next Priority

## Stabilize review workflow

Before:
- dashboards,
- analytics,
- forecasting,
- allocation engine,
- DuckDB expansion.

Must stabilize:
- correction workflow,
- apply-all,
- rerun lifecycle,
- category persistence,
- session state.

---

# Future Planned Features

## 1. Full non-coder application

Goal:
- no Docker,
- no Git,
- no terminal usage.

Target:
- desktop-style experience.

Possible future technologies:
- packaged Streamlit,
- Electron wrapper,
- PyInstaller,
- Tauri,
- local launcher.

---

## 2. Monthly expense anticipation

The system should:
- predict recurring upcoming expenses,
- estimate missing current-month expenses,
- forecast likely future charges.

Examples:
- water,
- electricity,
- gas,
- internet,
- credit card payments,
- subscriptions.

Approach:
- recurrence detection,
- statistical forecasting,
- seasonality detection,
- historical averaging,
- anomaly handling.

---

## 3. Spending forecast engine

The system should forecast:
- end-of-month spending,
- category-level forecasts,
- projected cash flow.

Potential future techniques:
- moving averages,
- weighted rolling averages,
- Prophet,
- ARIMA,
- hybrid heuristics.

Must remain:
- explainable,
- understandable for non-coders.

---

## 4. Yearly budget generation

The system should:
- generate next-year budgets,
- compare against previous years,
- request external influencing variables.

Potential inputs:
- inflation,
- interest rates,
- expected salary changes,
- rent increases,
- loan changes,
- energy price changes.

The UI must guide the user through:
- data collection,
- assumptions,
- scenario generation.

---

# Important Constraints

## The platform must remain:

- local-first,
- privacy-first,
- usable by non-coders,
- low-maintenance,
- low-cost,
- understandable,
- explainable.

---

# Important UX Insight

Financial UX is mostly:
- operational density,
- fast correction workflows,
- low-friction review.

NOT:
- fancy dashboards,
- visual complexity,
- excessive charts.

---

# Current Development Status

Status:
- early operational MVP.

Main focus:
- stabilize human correction loop.

NOT ready yet for:
- production usage,
- forecasting,
- allocations,
- budgeting engine,
- packaging/distribution.