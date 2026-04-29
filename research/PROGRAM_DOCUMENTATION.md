# Personal Budget & Spending Assistant — Program Documentation

**Course:** HKU 2025–2026 Sem 2, COMP1110 Group B12
**Repository:** [github.com/yangandi114/spending-assistant](https://github.com/yangandi114/spending-assistant)
**Topic:** A — Personal Budget & Spending Assistant
**Document version:** 2.0 — April 2026

This document consolidates the team's design notes (`MAIN_DOCUMENTATION.md`), the *Competitive Analysis & Requirements Specification* report, and the live source code on GitHub into a single user-facing reference. It describes what the program does, how to run it, what it reads and writes, and how each requirement from the team's specification is realised in code.

---

## 1. Team & Roles

| Role | Member | Student ID |
|------|--------|------------|
| Project Lead & UI Design | Yang Andi | 3036587092 |
| Algorithm & Logic | Mao Yicheng | 3036483040 |
| Research & Documentation | Tao Xinran | 3036525393 |
| Testing & Evaluation | Wang Ziyi | 3036484020 |
| Data Modeling & File Management | Yao Junzhu | 3036590427 |

Per-module authorship recorded in the source files: `main.py` and `validator.py` (Yang Andi); `analytics.py`, `alerts.py`, and the `print_outliers` function in `display.py` (Mao Yicheng); the rest of `display.py` (Yang Andi); `data.py` (Yao Junzhu, with `fetch_exchange_rates` by Yang Andi); the test data generator under `tests/` (Wang Ziyi); the *Competitive Analysis & Requirements Specification* report (Tao Xinran).

### Project timeline

- **Phase 1 (Mar 15 – Mar 23):** Planning & research — *complete.*
- **Phase 2 (Mar 24 – Apr 12):** Architecture & implementation — *complete.*
- **Phase 3 (Apr 13 – Apr 19):** Testing & evaluation — *complete.*
- **Phase 4 (Apr 20 – May 2):** Final deliverables & reports — *in progress.*

---

## 2. Overview

The Personal Budget & Spending Assistant is a **command-line (CLI) personal finance tool** for individual users. Positioning summarised from the team's competitive analysis: lightweight, plain-text, multi-currency-aware, with full data sovereignty (everything stays on disk in readable JSON), and free. It deliberately avoids the trade-offs of GUI subscription apps (cloud lock-in, paid tiers, weak Asian bank coverage) and the steep learning curve of double-entry plain-text accounting tools (Ledger, hledger, Beancount).

The program offers four core capabilities:

1. **Record** expenses by category, currency, date, and free-text description.
2. **Analyse** spending — category totals, 7-day vs. 30-day trends, top categories, end-of-month forecast, calendar heatmap, outlier detection.
3. **Constrain** spending via per-category budget rules (daily caps, monthly caps, percentage-of-total thresholds) with synchronous alerting.
4. **Export** a plain-text monthly summary report.

The tool runs in any modern terminal that supports Unicode, on macOS, Linux, or Windows (including WSL).

---

## 3. Architecture

The program is organised into six Python modules with strict layering and no circular imports.

| Module | Role |
|--------|------|
| `main.py` | CLI entry point and orchestrator. Hosts the interactive menu loop and routes each menu choice to a dedicated *flow* function. |
| `data.py` | File-I/O layer. Reads and writes JSON files; fetches live FX rates from `open.er-api.com`. All other modules go through this layer. |
| `validator.py` | Boundary input validation (date, amount, description, category). Returns booleans; never raises. |
| `analytics.py` | Pure computation layer — filtering, totals, trends, forecast, heatmap, outliers. No I/O, no internal imports. |
| `alerts.py` | Rule-checking layer. Evaluates transactions against budget rules and returns structured alert dictionaries. |
| `display.py` | Rendering layer. All `rich`-formatted tables, panels, progress bars, and the plain-text report exporter live here. |

Data flow on every interaction follows a one-way path: user input → `validator.py` → `data.py` (load) → `analytics.py` / `alerts.py` (compute) → `display.py` (render) → `data.py` (save).

External dependencies: **`questionary`** (interactive prompts), **`rich`** (formatted terminal output), and the Python standard library (`json`, `urllib.request`, `datetime`, `calendar`, `collections`, `os`).

---

## 4. Installation & Usage

### 4.1 Prerequisites

- Python 3.10 or newer
- Dependencies (listed in `requirements.txt`):
  ```
  pip install -r requirements.txt
  ```
- Internet access on first run (optional — the program falls back to cached/default exchange rates if offline)

### 4.2 Running the program

From the project root:

```
python main.py
```

On startup the program:

1. Creates the `data/`, `config/`, and `outputs/` directories if they do not yet exist.
2. Attempts to fetch live HKD-based exchange rates from `open.er-api.com` (5-second timeout). On success, the rates in `config/config.json` are overwritten with fresh values; on any failure (offline, API down, malformed response) the cached rates are used and a yellow notice is printed.
3. Displays the main menu and enters the interactive loop until the user selects **🚪 Exit** or presses **Ctrl+C**.

### 4.3 Generating test data

For evaluation or development, the test fixture generates 120+ synthetic transactions with edge cases (multiple currencies, boundary dates, large amounts, uncategorised entries):

```
python tests/test_generator.py
```

This populates `data/transactions.json`. Re-run `python main.py` to inspect the result through the menu.

### 4.4 Main menu

```
  ── Transactions ─────────────────
  ➕   Add Transaction
  📋   View / Filter Transactions
  ✏️    Edit / Delete Transaction
  ── Analytics ────────────────────
  📊   Statistics & Analytics
  ⚠️    Check Budget Alerts
  ── Management ───────────────────
  💰   Budget Rules
  🏷️    Manage Categories
  ⚙️    Settings
  ─────────────────────────────────
  📄   Export Summary Report
  🚪   Exit
```

Navigation uses arrow keys; **Enter** to select. Every prompt accepts **Ctrl+C** to cancel back to the previous menu, with the top-level loop catching the interrupt for a graceful exit.

---

## 5. Features and Usage Walkthrough

### 5.1 Add Transaction

Step-by-step prompts for date, amount, currency, category, and description. The system auto-assigns a sequential ID and immediately runs all alert checks against the new ledger; any triggered alerts and a daily budget-progress bar are shown before returning to the main menu.

**Input fields**

| Field | Validation | Default |
|-------|------------|---------|
| Date | `YYYY-MM-DD` calendar-valid date | Today |
| Amount | Strictly positive number | — |
| Currency | Picked from the configured list (HKD, CNY, JPY, KRW, NTD, USD, GBP, EUR by default) | — |
| Category | Picked from the configured list, plus the literal `Uncategorized` | — |
| Description | Non-empty, non-whitespace string | — |

**Sample output**

```
✅  Transaction #42 added.
🔴  Food: Daily limit exceeded! (HK$120.00 / HK$80.00)
[Today's Budget Progress table]
```

### 5.2 View / Filter Transactions

Sub-menu offering four browsing modes:

- **All Transactions** — full ledger, newest first.
- **Filter by Date Range** — two date prompts; range is inclusive on both ends.
- **Filter by Category** — single-select from configured categories.
- **Search by Keyword** — case-insensitive substring match on the description field.

All four render via `print_transaction_table`. Non-HKD amounts are shown alongside their HKD equivalent in dim style: `USD 25.00 ≈ HK$194.50`.

### 5.3 Edit / Delete Transaction

The full ledger is printed; the user types the numeric ID of the target transaction (or `q` to cancel). For an edit, the user picks one of the five fields (Date, Amount, Currency, Category, Description); for a delete, a confirmation prompt is shown before the row is removed and the ledger saved.

### 5.4 Statistics & Analytics

Sub-menu with three groups:

- **Overview** — Category Totals (Current Month or All Time), Top 3 Categories, Major Expenses (top 5%).
- **Trends & Forecast** — 7-day vs. 30-day daily-average comparison with directional indicator (⬆/⬇/→); end-of-month projected total based on linear extrapolation of the daily average so far.
- **Visuals** — Today's per-category budget progress bars; calendar-grid heatmap of the current month, where each cell is shaded `░ ▒ ▓ █` according to spending intensity relative to the monthly daily average.

### 5.5 Check Budget Alerts

Loads the current ledger and runs all rule checks: daily-cap exceeded, monthly-percentage exceeded, three-or-more consecutive days of overspend, end-of-month forecast exceeding the sum of all monthly caps, and uncategorised transactions. Active alerts are rendered in a coloured panel (red for hard violations, yellow for soft warnings); an empty result shows a green "All clear" panel.

### 5.6 Budget Rules

CRUD interface for per-category budget rules.

- **View Rules** — table of current rules with `—` for any unset optional field.
- **Add / Update Rule** — pick a category, then optionally set any combination of daily cap (HKD), monthly cap (HKD), and percentage-of-total threshold (1–100). Adding a rule for a category that already has one overwrites it.
- **Delete Rule** — pick a category, confirm, remove.

### 5.7 Manage Categories

View, add, or remove the list of spending categories. Default categories: `Food`, `Transport`, `Personal`, `Entertainment`, `Health`, `Utilities`. Removed categories are no longer offered when logging a transaction; existing transactions retain whatever string they were saved with (which is then flagged by the *uncategorized* alert).

### 5.8 Settings

- **Set Monthly Income** — used by the savings-goal calculation.
- **Set Savings Goal** — monthly target in HKD.
- **View Savings Progress** — full panel showing income, total spent this month, remaining balance, savings goal, progress bar, and current status.
- **Currency Exchange Rates** — prints the current rates (1 unit → HKD) and optionally lets the user override one rate manually; the change is persisted to `config.json`.

### 5.9 Export Summary Report

Generates a 72-character-wide, plain-text monthly summary in `outputs/`. The filename follows the pattern `report_YYYY-MM-DD_HHMMSS.txt`. Contents: header, spending by category with shares, 7d/30d trends with month-over-month percentage, top 3 categories, and the list of currently active alerts.

---

## 6. Inputs

### 6.1 Interactive inputs

All user input is collected via `questionary` prompts. Validation is enforced *at the boundary* — `main.py` re-prompts on invalid input rather than passing bad data downstream. Internal modules trust that data already on disk is well-formed.

| Helper | Validates |
|--------|-----------|
| `get_valid_date` | Format `YYYY-MM-DD`; rejects impossible dates such as `2026-13-01`. |
| `get_valid_amount` | Positive numeric (int or float). Zero and negatives rejected. |
| `get_valid_percentage` | Number in the half-open range `(0, 100]`. |
| `get_valid_description` | Non-empty after trimming whitespace. |

Cancellation: pressing **Ctrl+C** at any prompt raises `KeyboardInterrupt`, which is caught by the top-level loop and returns the user gracefully to the main menu (or exits if at top level).

### 6.2 File-based inputs

The program reads three JSON files at startup and on demand. All three are auto-created with safe defaults on first run.

**`data/transactions.json`** — the transaction ledger. List of objects:

```json
[
  {
    "id": 1,
    "date": "2026-04-15",
    "amount": 95.5,
    "currency": "HKD",
    "category": "Food",
    "description": "Lunch at canteen"
  }
]
```

**`data/budget_rules.json`** — per-category rules. Each rule has a mandatory `category`; the three constraint fields are optional and may be present in any combination.

```json
[
  {
    "category": "Food",
    "daily_cap": 80.0,
    "monthly_cap": 2000.0,
    "pct_threshold": 35
  }
]
```

**`config/config.json`** — application configuration.

```json
{
  "categories": ["Food", "Transport", "Personal", "Entertainment", "Health", "Utilities"],
  "currencies": { "HKD": 1.0, "CNY": 1.15, "JPY": 0.052, "USD": 7.78, "...": "..." },
  "default_currency": "HKD",
  "savings_goal": 500.0,
  "income": 0.0
}
```

### 6.3 Network input

`open.er-api.com/v6/latest/HKD` is queried once on startup with a 5-second timeout. The API returns HKD-base rates which the code inverts to *X→HKD* form. Any failure (network, non-200, malformed JSON, missing currency) is silently absorbed and the existing cached rates remain in use.

---

## 7. Outputs

### 7.1 Terminal output

Every visible piece of output is rendered through `display.py` using `rich`. The colour palette has consistent semantics:

- **Green** — confirmation, success, healthy budget.
- **Yellow** — soft warning, threshold approaching, missing setup.
- **Red** — hard violation, error, validation failure.
- **Cyan / Magenta** — informational headers and identifiers.
- **Dim** — placeholders and secondary information (HKD-equivalents, "no data" notices).

Tables use `rich.box` styles (`ROUNDED`, `SIMPLE`, `SIMPLE_HEAVY`) chosen to match the data type.

### 7.2 File outputs

| Path | Producer | Format | Trigger |
|------|----------|--------|---------|
| `data/transactions.json` | `save_transactions` | Indented JSON | Every add / edit / delete |
| `data/budget_rules.json` | `save_budget_rules` | Indented JSON | Every rule change |
| `config/config.json` | `save_config` | Indented JSON | Settings, category, or rate changes; also after FX fetch |
| `outputs/report_YYYY-MM-DD_HHMMSS.txt` | `export_report` | 72-column plain text, no colour codes | "Export Summary Report" menu |

Sample report excerpt:

```
========================================================================
   MONTHLY SPENDING SUMMARY REPORT
   April 2026   (generated 2026-04-28 14:05)
========================================================================

SPENDING BY CATEGORY
----------------------------------------
  Food             HK$ 1310.30    14.2%
  Entertainment    HK$ 8755.60    37.5%
  ...
  TOTAL            HK$23210.90

SPENDING TRENDS
----------------------------------------
  7-day avg:    HK$  825.50/day
  30-day avg:   HK$  774.10/day
  Trend:        +6.6%
```

### 7.3 Alert output structure

Alerts returned by `alerts.py` are dictionaries with a stable schema, allowing the same alert objects to feed both the live menu (`print_alerts`) and the exported report.

| `type` | Severity | Extra keys |
|--------|----------|-----------|
| `daily_exceeded` | red | `category`, `spent`, `cap` |
| `pct_exceeded` | red | `category`, `pct`, `threshold` |
| `consecutive_overspend` | red | `category`, `streak` |
| `forecast_warning` | yellow | — |
| `uncategorized` | yellow | `id`, `category` |

Every alert also carries a pre-formatted human-readable `message` field.

---

## 8. Requirements-to-Implementation Map

This section maps each requirement from the team's *Competitive Analysis & Requirements Specification* report onto the actual code artefacts. Status legend:

- ✅ **Implemented** — present and working as specified.
- 🟡 **Partial** — present but with caveats noted.
- ❌ **Not implemented** — explicitly out of scope or deferred.

### 8.1 Functional requirements

| ID | Domain | Status | Implementation |
|----|--------|--------|----------------|
| FR-01 | Transaction Entry | ✅ | `add_transaction_flow` in `main.py`; one cohesive flow with auto-defaults for date and currency. (Note: spec describes a `budget add ...` one-line CLI; this delivery uses an interactive prompt sequence instead — functionally equivalent for course scope.) |
| FR-02 | Transaction Entry | ✅ | The same `add_transaction_flow` *is* the interactive mode (this delivery has no separate one-line mode). |
| FR-03 | Transaction Entry | ❌ | CSV import not implemented. Marked Could-list (C-01) in the spec. |
| FR-04 | Transaction Query | 🟡 | `view_transactions_flow` supports filtering by date range, single category, or keyword. Spec also names tag, currency, and amount range — these are not exposed (no tag system was implemented). |
| FR-05 | Transaction Query | ✅ | `print_transaction_table` (paginated `rich` table with colour highlighting). |
| FR-06 | Category Management | 🟡 | `manage_categories_flow` supports add and remove. Edit (rename with migration of existing transactions) is not implemented; transactions retain whatever string was saved. |
| FR-07 | Category Management | ✅ | `DEFAULT_CONFIG["categories"]` ships six defaults: Food, Transport, Personal, Entertainment, Health, Utilities. |
| FR-08 | Budget Rules | 🟡 | Daily cap, monthly cap, percentage threshold all supported via `manage_budget_rules_flow`. The fourth construct named in the spec — *category monthly cap* — overlaps with monthly cap; treated as the same. |
| FR-09 | Budget Rules | 🟡 | 7-day vs. 30-day rolling averages are *displayed* (`print_trends`) and a forecast warning fires when projected end-of-month exceeds total caps, but rolling-window soft alerts are not modelled as user-configurable rules. |
| FR-10 | Budget Rules | 🟡 | Severity is hard-coded into `print_alerts` (red for cap/percent/streak, yellow for forecast/uncategorized). Not user-configurable per rule. |
| FR-11 | Multi-currency | 🟡 | Each transaction stores `amount` and `currency` (two of the five fields specified). Per-transaction rate snapshot, home-currency amount, and rate source are **not** persisted — the display layer reconverts at render time using the *current* config rates, which loses historical accuracy. **This is the most material gap vs. the spec.** |
| FR-12 | Multi-currency | 🟡 | `fetch_exchange_rates` in `data.py` retrieves live rates from `open.er-api.com`. Rates are cached in `config.json` but with no TTL — they are simply overwritten on the next successful fetch. |
| FR-13 | Multi-currency | 🟡 | Falls back to cached rates on any API failure. The "manual rate input on stale cache" branch is not implemented; the user can edit a rate manually only via Settings. |
| FR-14 | Multi-currency | ❌ | Home currency is hard-coded to HKD throughout (`DEFAULT_CONFIG["default_currency"]`, hard-coded `"HKD"` in many display strings). User cannot change it; historical recalculation not supported. |
| FR-15 | Subscriptions | ❌ | Subscription modelling not implemented. (Spec marked Should-list S-02.) |
| FR-16 | Subscriptions | ❌ | Same as above. |
| FR-17 | Alerts | ✅ | `add_transaction_flow` calls `get_all_alerts` immediately after every save and renders any non-uncategorized alerts. |
| FR-18 | Alerts | ❌ | Alerts are recomputed on demand and never persisted to `alerts.json`. Historical alert retrieval is therefore unavailable. |
| FR-19 | Reporting | ✅ | `export_report` covers per-category amount + share, plus 7d/30d trends and top 3 categories. Month-over-month delta is shown only for trend (not per category). |
| FR-20 | Reporting | ❌ | Tag-filtered aggregation requires a tag system; not implemented. |
| FR-21 | Export | 🟡 | Plain text export via `export_report`. CSV, JSON, and Markdown export formats are not implemented. |
| FR-22 | Persistence | ✅ | Three readable JSON files: `transactions.json`, `budget_rules.json`, `config.json`. (Subscriptions and alerts files are not produced — see FR-15, FR-18.) |
| FR-23 | Persistence | ❌ | No backup-on-write mechanism. `_save_json` writes directly with no temp-file rename and no rolling history. |
| FR-24 | Initialisation | 🟡 | First run creates the directory structure and writes a `DEFAULT_CONFIG`. There is no interactive wizard for home currency, categories, budget, or alert thresholds — the user discovers these via the Settings menu. |

### 8.2 Non-functional requirements

| Category | Spec target | Status |
|----------|-------------|--------|
| Performance — single command ≤ 500 ms | ✅ Trivially met for typical ledgers. No formal pytest benchmarks shipped. |
| Performance — monthly summary ≤ 1 s | ✅ Met. |
| Usability — first transaction in ≤ 3 minutes | ✅ Single guided flow; defaults reduce typing. |
| Usability — `--help` per command | ❌ Not applicable in the delivered form (the program is menu-driven, not flag-driven). |
| Reliability — no data loss on abnormal termination | 🟡 `_save_json` writes directly, not via temp+rename, so a crash mid-write can corrupt a file. Loaders detect malformed JSON and fall back to defaults, mitigating but not preventing the issue. |
| Reliability — graceful degradation when FX API down | ✅ `fetch_exchange_rates` returns `None` on any error; cached rates are used. |
| Portability — macOS / Linux / Windows | ✅ Pure Python + cross-platform libraries. CI is not configured in this submission. |
| Maintainability — ≥ 70% test coverage | 🟡 Test fixture (`tests/test_generator.py`, 120+ synthetic transactions with edge cases) supports manual evaluation, but no unit tests of behaviour are shipped. |
| Security — local-only data | ✅ Only outbound network call is the FX endpoint; no transaction data leaves the machine. |
| Internationalisation | ❌ All UI strings are hard-coded English. |
| Compatibility — Python 3.10+, no NumPy/pandas/async | ✅ Met. |
| Accessibility — non-colour markers | 🟡 Severity icons (🔴 / 🟡 / ⬆ / ⬇) are present but bracketed `[WARN]`-style text markers as specified are not used. |

### 8.3 MoSCoW delivery status

| Bucket | Items | Delivered |
|--------|-------|-----------|
| **Must (10)** | M-01 Basic entry; M-02 Querying; M-03 Categories; M-04 Caps; M-05 Multi-CCY core; M-06 Monthly summary; M-07 Three-level alerts; M-08 CSV+MD export; M-09 JSON + backup; M-10 Init wizard | M-01 ✅ · M-02 🟡 · M-03 ✅ · M-04 ✅ · M-05 🟡 · M-06 ✅ · M-07 🟡 · M-08 ❌ · M-09 🟡 · M-10 ❌ |
| **Should (6)** | Tag system; Subscriptions; Rolling-window alerts; Home-CCY switching; Alert history; JSON / plain-text export | All ❌ except plain-text export ✅ |
| **Could (6)** | Historical CSV import; Sinking fund; YoY comparison; Currency dashboard; Progress bars; Colour-blind palette | Progress bars ✅ (`print_budget_bars`); rest ❌ |
| **Won't** | Bank sync; GUI; Investment tracking; AI categorisation; Multi-user sync | All correctly absent |

---

## 9. Known Issues & Recommended Fixes

The list below is based on a review of the code at the time of writing. Verify against the latest `main` branch before submission.

1. **Multi-currency analytics use raw amounts.** `analytics.py` aggregations (`get_totals_by_category`, `linear_forecast`, `get_savings_progress`, `get_spending_outliers`) and the `alerts.py` rule checks all sum `t["amount"]` directly without consulting `t["currency"]`. A 100 USD transaction is therefore aggregated as 100 HKD. The display layer converts at render time, masking the issue visually but leaving every total, percentage, forecast, and cap comparison incorrect when non-HKD transactions exist. **Suggested fix:** introduce a small helper `to_hkd(txn, rates)` in `analytics.py` and route every sum through it. This is the single most material spec-vs-implementation gap and fixing it brings FR-11 from 🟡 to closer to ✅.

2. **`get_consecutive_overspend` skips zero-spend days.** The streak counter iterates only over dates with transactions in the relevant category; a calendar day with no spending does not break the streak. **Suggested fix:** iterate over calendar days backwards from today, breaking the streak whenever the day's total (zero or otherwise) is below the cap.

3. **`validate_category` is dead code.** Defined in `validator.py` but never called — categories are always menu-selected, never typed. Either remove it or wire it into the (future) CSV import flow.

4. **Doc/code drift on report filename.** `MAIN_DOCUMENTATION.md` describes `report_YYYYMMDD_HHMMSS.txt`; the code produces `report_YYYY-MM-DD_HHMMSS.txt` (with hyphens between Y/M/D). Pick one and align both.

5. **No transactional file writes.** `_save_json` opens the target file directly for writing, so a crash or kill mid-write can leave a partial file. Loaders gracefully fall back to defaults on malformed JSON, which limits the blast radius but still loses the data. **Suggested fix:** write to a temp file in the same directory, then `os.replace()` onto the destination — atomic on POSIX and modern Windows.

> *Resolved in current `main` branch:* the previous entry-point bug — where `main()` was called from inside its own body without an `if __name__ == "__main__":` guard — has been corrected on GitHub. Earlier snapshots may still exhibit it.

---

## 10. File Layout

```
spending-assistant/
├── main.py                  ← CLI orchestrator
├── data.py                  ← File I/O + FX fetch
├── display.py               ← rich rendering + report export
├── validator.py             ← Input validation
├── alerts.py                ← Budget rule checks
├── analytics.py             ← Pure computation
├── requirements.txt         ← Pip dependencies (questionary, rich)
├── README.md                ← Quick reference + structure
├── MAIN_DOCUMENTATION.md    ← Module-level API reference
├── DOCUMENTATION.md         ← Higher-level design write-up
├── FEATURES.md              ← Feature list
├── PLAN.md                  ← Timeline & roles
├── UI.md                    ← UI design notes
├── prompts.md               ← AI prompt log (per assignment requirement)
├── roles.md                 ← Role definitions
├── config/
│   └── config.json          ← Categories, FX rates, income, savings goal
├── data/
│   ├── transactions.json    ← Transaction ledger
│   └── budget_rules.json    ← Per-category rules
├── outputs/                 ← Generated text reports
└── tests/
    └── test_generator.py    ← 120+ synthetic transactions (edge cases)
```

---

## 11. Quick Reference: Common Workflows

**Log a HK$45 lunch:**
Main Menu → ➕ Add Transaction → Date `Enter` (today) → Amount `45` → Currency `HKD` → Category `Food` → Description `Canteen lunch`.

**Set a HK$80 daily food budget:**
Main Menu → 💰 Budget Rules → Add / Update Rule → Category `Food` → Set daily cap? `y` → `80` → Set monthly cap? `n` → Set % threshold? `n`.

**See where the month is heading:**
Main Menu → 📊 Statistics & Analytics → Spending Forecast.

**Generate a shareable summary:**
Main Menu → 📄 Export Summary Report → file path is printed; copy from `outputs/`.

---

*End of document.*
