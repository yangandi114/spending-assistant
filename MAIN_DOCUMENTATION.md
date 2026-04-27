# main.py Documentation

## Overview

`main.py` is the CLI entry point and orchestrator for the **COMP1110 Personal Budget & Spending Assistant**. It manages the interactive menu system, user input/output, and coordinates all application workflows using the `questionary` library for terminal UI and `rich` for formatted output.

**Authors**: Yang Andi, Mao Yicheng

---

## Architecture

### High-Level Flow

```
main()
  ├─ Initialize directories & fetch live exchange rates
  ├─ Enter main menu loop
  └─ Route user selection to appropriate flow handler
      ├─ add_transaction_flow()
      ├─ view_transactions_flow()
      ├─ edit_delete_flow()
      ├─ statistics_flow()
      ├─ alerts_flow()
      ├─ manage_budget_rules_flow()
      ├─ manage_categories_flow()
      ├─ settings_flow()
      └─ export_flow()
```

Each flow function handles:
1. Load necessary config/data files
2. Present sub-menu or collect user input
3. Validate input
4. Update data files
5. Display results

---

## Dependencies

### External Libraries
- **questionary**: Interactive CLI prompts (menus, text input, yes/no)
- **rich**: Formatted terminal output (colors, tables, panels)

### Internal Modules
- **data.py**: File I/O for transactions, budget rules, config, exchange rates
- **display.py**: All `rich` rendering functions (tables, alerts, stats, heatmaps)
- **validator.py**: Input validation (dates, amounts, descriptions)
- **alerts.py**: Budget alert detection logic
- **analytics.py**: Statistics and trend calculations

---

## Function Reference

### UI Helpers

#### `_sep(label="")`
**Returns a styled questionary Separator for menu visual grouping.**

Creates a visual separator line for questionary menus. When `label` is provided, inserts it between dashes; otherwise returns a plain line.

```python
_sep()           # Plain separator
_sep("Browse")   # Separator with label
```

---

#### `ask(prompt, default="")`
**Prompts user for text input; raises KeyboardInterrupt if cancelled.**

Wrapper around `questionary.text()` with consistent styling. Converts `None` (user cancelled) into an exception.

```python
name = ask("Enter name:", default="John")
# Returns: "John" or user input
# Raises: KeyboardInterrupt if Ctrl+C
```

---

#### `choose(prompt, choices)`
**Prompts user to select from a list; raises KeyboardInterrupt if cancelled.**

Wrapper around `questionary.select()` with arrow-key navigation and styled pointer.

```python
action = choose("Pick one:", ["Option A", "Option B", BACK])
# Returns: selected string
# Raises: KeyboardInterrupt if Ctrl+C
```

---

#### `confirm(prompt, default=False)`
**Prompts user for yes/no confirmation; raises KeyboardInterrupt if cancelled.**

Wrapper around `questionary.confirm()` with consistent styling.

```python
if confirm("Delete transaction?"):
    # user said yes
```

---

#### `pause()`
**Waits for any keypress before continuing.**

Used between screens to let user review output before returning to menu.

```python
pause()  # Blocks until user presses any key
```

---

### Main Application Flow

#### `main()`
**Entry point: initialises dirs, fetches live rates, runs the main menu loop.**

1. Creates required directories (`config/`, `data/`, `outputs/`)
2. Attempts to fetch live currency exchange rates from external API
3. Falls back to cached rates if offline
4. Loops menu until user selects "Exit" or presses Ctrl+C
5. Catches `KeyboardInterrupt` for graceful shutdown

```python
if __name__ == "__main__":
    main()
```

---

### Transaction Management

#### `add_transaction_flow()`
**Guides user through adding a new transaction and checks budget alerts.**

Flow:
1. Prompt for date (YYYY-MM-DD, defaults to today)
2. Prompt for amount (positive number)
3. Choose currency (with HKD conversion display)
4. Choose category
5. Enter description
6. Save transaction with auto-generated ID
7. Check & display triggered budget alerts
8. Show budget progress bars

**Validation**: Dates and amounts validated before acceptance.

---

#### `view_transactions_flow()`
**Lets user browse, filter, or search existing transactions.**

Sub-menu options:
- **All Transactions**: Display full table
- **Filter by Date Range**: Query between two dates
- **Filter by Category**: Show only one category
- **Search by Keyword**: Case-insensitive description search

All results displayed in formatted rich table.

---

#### `edit_delete_flow()`
**Lets user select a transaction by ID and edit a field or delete it.**

Flow:
1. Display all transactions
2. User enters transaction ID
3. Choose action: Edit Field or Delete Transaction
4. If edit: pick field (Date, Amount, Currency, Category, Description)
   - Validate new value
   - Update transaction
   - Save
5. If delete: confirm, then remove from ledger

---

### Analytics & Monitoring

#### `statistics_flow()`
**Shows analytics sub-menu: totals, trends, forecast, heatmap, etc.**

Sub-menu options:

**Overview**
- Category Totals — Current Month
- Category Totals — All Time
- Top 3 Categories
- Major Expenses (Top 5%)

**Trends & Forecast**
- Spending Trends (7d vs 30d)
- Spending Forecast

**Visuals**
- Budget Progress Bars
- Spending Heatmap

Each option displays results in formatted tables/charts via `display.py` functions.

---

#### `alerts_flow()`
**Loads and displays all active budget alerts.**

1. Load transactions, budget rules, config
2. Calculate all alerts via `alerts.py` logic
3. Display formatted alert list via `display.py`

Alerts include:
- Budget cap violations (daily/monthly)
- Spending % thresholds exceeded
- Uncategorized transactions

---

### Configuration Management

#### `manage_budget_rules_flow()`
**Lets user view, add/update, or delete per-category budget rules.**

Actions:
- **View Rules**: Display all budget rules in table
- **Add/Update Rule**: 
  - Choose category
  - Optionally set daily cap (HKD)
  - Optionally set monthly cap (HKD)
  - Optionally set % threshold (0–100)
  - Save (updates existing or adds new rule)
- **Delete Rule**:
  - Choose category
  - Confirm deletion

---

#### `manage_categories_flow()`
**Lets user view, add, or remove spending categories.**

Actions:
- **View**: List all categories
- **Add**: Enter new category name, save to config
- **Remove**: Select category, confirm, remove from config

Changes saved to `config/config.json`.

---

#### `settings_flow()`
**Lets user set income, savings goal, and update currency exchange rates.**

Sub-menu options:

**Income & Goals**
- Set Monthly Income (HKD)
- Set Savings Goal (HKD)
- View Savings Progress (displays progress bar toward goal)

**Currencies**
- View current exchange rates (1 unit → HKD)
- Update a rate manually (persists to config)

---

### Reporting

#### `export_flow()`
**Exports a full summary report to a text file in outputs/.**

1. Load all transactions, budget rules, config
2. Call `export_report()` from `display.py`
3. Display success message with filename

Output file format: `outputs/report_YYYYMMDD_HHMMSS.txt`

---

## Global Variables

### `STYLE`
Custom questionary color scheme:
- **pointer**: Green `❯` cursor
- **highlighted**: Bold green selection
- **question**: Bold question text
- **answer**: Green answer text
- **separator**: Dim gray separators

### `BACK`
Menu option string: `"↩   Back"` (constant used by all sub-menus)

### `HANDLERS`
Dictionary mapping menu labels to flow function handlers:
```python
HANDLERS = {
    "➕   Add Transaction":           add_transaction_flow,
    "📋   View / Filter Transactions": view_transactions_flow,
    ...
}
```

### `MAIN_MENU`
List of main menu options with separators, passed to `questionary.select()`.

---

## Usage Examples

### Running the Application
```bash
python main.py
```

Starts the main menu loop. Press Ctrl+C or select "Exit" to quit.

---

### Adding a Transaction (Interactive)
```
Main Menu → ➕ Add Transaction
  Date: 2026-04-15
  Amount: 150
  Currency: HKD
  Category: Food
  Description: Lunch at restaurant
  
✅ Transaction #42 added
⚠️ [Alert] Food category is at 95% of monthly cap
```

---

### Viewing Filtered Transactions
```
Main Menu → 📋 View / Filter Transactions
  → Filter by Category
  → Choose: Food
  
(Displays table of all Food transactions)
```

---

### Managing Budget Rules
```
Main Menu → 💰 Budget Rules
  → Add / Update Rule
  → Category: Food
  → Set daily cap? (y/n) → Yes
  → Daily cap (HKD): 50
  → Set monthly cap? (y/n) → Yes
  → Monthly cap (HKD): 1000
  
✅ Rule saved
```

---

## Error Handling

### Input Validation
- **Dates**: Format YYYY-MM-DD, must be valid calendar date
- **Amounts**: Positive numbers (int or float)
- **Descriptions**: Non-empty strings
- **Budget values**: Positive numbers or percentages 0–100

Invalid inputs trigger error message & re-prompt (no crash).

### File I/O
- Missing files are created with defaults by `data.py`
- Malformed JSON handled gracefully
- Network timeout on exchange rates falls back to cached rates

### User Cancellation
- Pressing Ctrl+C in any prompt raises `KeyboardInterrupt`
- Caught in `main()` loop → graceful exit with goodbye message

---

## Data Flow

```
User Input (questionary)
    ↓
Input Validation (validator.py)
    ↓
Data Update/Query (data.py)
    ↓
Logic Processing (alerts.py, analytics.py)
    ↓
Formatted Output (display.py + rich)
    ↓
Save to File (data.py)
```

---

## Code Style & Conventions

- **Simple, readable Python**: Year-1 CS level
- **No advanced features**: No decorators, metaclasses, or complex abstractions
- **Consistent naming**: snake_case for functions, UPPER_CASE for constants
- **Minimal comments**: Only where logic is non-obvious
- **Rich markup**: Inline tags like `[bold cyan]Text[/bold cyan]` instead of ANSI codes
- **Error messages**: Always informative, styled in red/yellow/green

---

## Testing & Validation

To verify main.py runs without syntax errors:
```bash
python -m py_compile main.py
```

To test interactively:
```bash
python main.py
# Try each menu option
# Test invalid inputs (bad dates, negative amounts)
# Test Ctrl+C cancellation
```

To generate test data:
```bash
python tests/test_generator.py
# Creates 100+ fake transactions in data/transactions.json
```

---

## Dependencies on Other Modules

| Module | Purpose |
|--------|---------|
| `data.py` | `load_config()`, `load_transactions()`, `load_budget_rules()`, `save_*()`, `fetch_exchange_rates()`, `get_next_id()`, `ensure_dirs()` |
| `display.py` | All `print_*()` functions, `export_report()`, `console` object |
| `validator.py` | `validate_date()`, `validate_amount()`, `validate_description()` |
| `alerts.py` | `get_all_alerts()` |
| `analytics.py` | `filter_by_date()` |

---

## File Structure

```
comp1110projectlocal/
├── main.py                    ← This file
├── data.py                    ← File I/O
├── display.py                 ← Rich output rendering
├── validator.py               ← Input validation
├── alerts.py                  ← Budget alert logic
├── analytics.py               ← Statistics
├── config/
│   └── config.json            ← Categories, rates, income, goals
├── data/
│   ├── transactions.json      ← Transaction ledger
│   └── budget_rules.json      ← Budget rules
├── outputs/                   ← Generated reports
└── tests/
    └── test_generator.py      ← Test data generation
```

---

## Summary

`main.py` is the **user-facing orchestrator** of the budget assistant. It:
- ✅ Manages all interactive menus via questionary
- ✅ Coordinates data flow between modules
- ✅ Ensures consistent styling & error handling
- ✅ Routes user actions to specialized flow functions
- ✅ Provides graceful error recovery

Each flow function is self-contained and focuses on a single user workflow, keeping main.py clean and maintainable.

---

---

# analytics.py Documentation

## Overview

`analytics.py` is the **pure computation layer** of the budget assistant. It performs all statistical calculations on transaction data — filtering, aggregation, trend detection, forecasting, and heatmap generation. It has no user I/O and no file access; it only operates on Python lists and dicts passed in by callers.

**Authors**: Mao Yicheng (main), Yang Andi

---

## Dependencies

### Standard Library
- **calendar**: `monthrange()` to get the number of days in a month
- **collections.defaultdict**: Accumulate category/date totals without manual key checks
- **datetime**: Date parsing, arithmetic, and comparison

### Internal Modules
None — `analytics.py` is a leaf module with no internal imports.

---

## Function Reference

### `parse_date(date_str)`
Converts a `"YYYY-MM-DD"` string into a `datetime` object.

- **Parameters**: `date_str` (str) — date in `YYYY-MM-DD` format
- **Returns**: `datetime`
- **Used by**: `filter_by_date()` internally

---

### `filter_by_date(transactions, start=None, end=None)`
Returns only the transactions whose date falls within `[start, end]`.

- **Parameters**:
  - `transactions` (list) — full transaction list
  - `start` (datetime or None) — inclusive lower bound; `None` = no lower bound
  - `end` (datetime or None) — inclusive upper bound; `None` = no upper bound
- **Returns**: list of matching transaction dicts
- **Note**: Both bounds are inclusive. Callers must pass `datetime` objects, not strings.

```python
from datetime import datetime
apr = filter_by_date(txns, datetime(2026, 4, 1), datetime(2026, 4, 30))
```

---

### `get_totals_by_category(transactions, start=None, end=None)`
Sums spending per category, with optional date filter.

- **Parameters**: `transactions`, optional `start`/`end` datetime bounds
- **Returns**: `dict` mapping category name → total amount (float)
- **Edge case**: Returns `{}` if `transactions` is empty.

```python
totals = get_totals_by_category(txns)
# {"Food": 1310.3, "Entertainment": 8755.6, ...}
```

---

### `get_top_n_categories(transactions, n=3, start=None, end=None)`
Returns the top N spending categories with amount and percentage share.

- **Parameters**: `transactions`, `n` (int, default 3), optional date bounds
- **Returns**: list of `(category, amount, percentage)` tuples, sorted descending
- **Edge case**: Returns `[]` if no data. Safe when `n > number of categories`.

```python
top3 = get_top_n_categories(txns, 3)
# [("Entertainment", 8755.6, 37.5), ("Utilities", 6538.0, 28.0), ...]
```

---

### `get_spending_trends(transactions)`
Compares 7-day vs 30-day daily average spending.

- **Parameters**: `transactions` (list)
- **Returns**: `(avg_7, avg_30)` tuple of floats — HKD per day
- **Logic**: Divides total 7-day spend by 7, total 30-day spend by 30 (not just days with transactions).
- **Edge case**: Returns `(0, 0)` if no transactions in either window.

```python
avg_7, avg_30 = get_spending_trends(txns)
```

---

### `get_daily_totals_by_category(transactions, category)`
Sums spending per calendar day for one specific category.

- **Parameters**: `transactions` (list), `category` (str)
- **Returns**: `dict` mapping `"YYYY-MM-DD"` → daily total (float)
- **Edge case**: Returns `{}` if the category has no transactions.

```python
daily = get_daily_totals_by_category(txns, "Food")
# {"2026-04-15": 95.5, "2026-04-16": 42.0, ...}
```

---

### `get_consecutive_overspend(transactions, category, daily_cap)`
Counts how many consecutive days (going backwards from the most recent) a category exceeded its daily cap.

- **Parameters**: `transactions` (list), `category` (str), `daily_cap` (float)
- **Returns**: int — streak length (0 if no overspend)
- **Logic**: Sorts dates descending, increments streak until a day is found under cap or dates run out.

```python
streak = get_consecutive_overspend(txns, "Entertainment", 100)
# 15  (15 consecutive days over HK$100)
```

---

### `get_savings_progress(transactions, savings_goal, income)`
Calculates this month's spending, remaining balance, and net savings.

- **Parameters**: `transactions` (list), `savings_goal` (float), `income` (float) — all in HKD
- **Returns**: `(spent, remaining, savings)` tuple of floats
  - `spent` — total spent this calendar month
  - `remaining` — income minus spent
  - `savings` — remaining minus savings_goal (negative = goal not met)

```python
spent, remaining, savings = get_savings_progress(txns, 2000.0, 12000.0)
```

---

### `linear_forecast(transactions)`
Projects this month's total spend by extrapolating the daily average so far.

- **Parameters**: `transactions` (list)
- **Returns**: float — projected monthly total in HKD
- **Logic**: `(spent_so_far / days_elapsed) × days_in_month`
- **Edge case**: Returns `0.0` if no transactions this month.

```python
projected = linear_forecast(txns)
# 21788.79  (projected end-of-month total)
```

---

### `spending_heatmap(transactions)`
Assigns a block symbol to each day of the current month based on spending intensity relative to the monthly daily average.

- **Parameters**: `transactions` (list)
- **Returns**: `dict` mapping `"YYYY-MM-DD"` → `(symbol, amount)` tuple
- **Symbols**: `░` < 50% of avg, `▒` 50–99%, `▓` 100–149%, `█` ≥ 150%
- **Edge case**: Returns `{}` if no transactions this month.

---

### `get_spending_outliers(transactions, top_percent=0.05)`
Returns the top X% of transactions by amount — the biggest individual spends.

- **Parameters**: `transactions` (list), `top_percent` (float, default 0.05 = top 5%)
- **Returns**: list of transaction dicts, sorted by amount descending
- **Edge case**: Returns at least 1 result if list is non-empty. Returns `[]` for empty input.
- **Author**: Mao Yicheng

```python
outliers = get_spending_outliers(txns)        # top 5%
outliers = get_spending_outliers(txns, 0.10)  # top 10%
```

---

---

# alerts.py Documentation

## Overview

`alerts.py` is the **rule-checking layer**. It evaluates transaction data against user-defined budget rules and returns structured alert dictionaries. It performs no I/O and no rendering — callers pass in data, and it returns lists of alert dicts for `display.py` to render.

**Authors**: Mao Yicheng, Yang Andi

---

## Dependencies

### Internal Modules
- **analytics**: `get_daily_totals_by_category()`, `get_totals_by_category()`, `get_consecutive_overspend()`, `linear_forecast()`

---

## Alert Dict Format

Every alert returned is a dict with at least:

| Key | Type | Description |
|-----|------|-------------|
| `type` | str | Alert type identifier (see below) |
| `message` | str | Human-readable alert message |

Additional keys depend on type:

| Type | Extra keys |
|------|-----------|
| `daily_exceeded` | `category`, `spent`, `cap` |
| `pct_exceeded` | `category`, `pct`, `threshold` |
| `consecutive_overspend` | `category`, `streak` |
| `forecast_warning` | _(none)_ |
| `uncategorized` | `id`, `category` |

---

## Function Reference

### `check_daily_caps(transactions, budget_rules)`
Checks if today's spending in any category exceeds its daily cap.

- **Parameters**: `transactions` (list), `budget_rules` (list of rule dicts)
- **Returns**: list of `daily_exceeded` alert dicts (empty if all clear)
- **Logic**: Sums all today's transactions per category; compares to `daily_cap` if set.
- **Edge case**: Rules without `daily_cap` are skipped.

---

### `check_percentage_thresholds(transactions, budget_rules)`
Flags categories whose share of total spending exceeds a set percentage threshold.

- **Parameters**: `transactions` (list), `budget_rules` (list)
- **Returns**: list of `pct_exceeded` alert dicts
- **Edge case**: Returns `[]` if total spending is 0 (avoids divide-by-zero).

---

### `check_consecutive_overspend(transactions, budget_rules)`
Warns when a category has been over its daily cap for 3 or more consecutive days.

- **Parameters**: `transactions` (list), `budget_rules` (list)
- **Returns**: list of `consecutive_overspend` alert dicts
- **Threshold**: streak must be ≥ 3 days to trigger.
- **Edge case**: Rules without `daily_cap` are skipped.

---

### `check_forecast_alerts(transactions, budget_rules)`
Projects end-of-month total spend and warns if it will exceed the sum of all monthly caps.

- **Parameters**: `transactions` (list), `budget_rules` (list)
- **Returns**: list of `forecast_warning` alert dicts (0 or 1 item)
- **Edge case**: Returns `[]` if no rules have `monthly_cap` defined.

---

### `check_uncategorized(transactions, categories)`
Finds transactions with missing or unrecognised categories.

- **Parameters**: `transactions` (list), `categories` (list of valid category strings)
- **Returns**: list of `uncategorized` alert dicts, one per bad transaction
- **Triggers on**: category = `"Uncategorized"` or category not in the valid list.

---

### `get_all_alerts(transactions, budget_rules, categories)`
Aggregates all alert types into a single list for display.

- **Parameters**: `transactions` (list), `budget_rules` (list), `categories` (list of strings)
- **Returns**: combined list of all alert dicts in order: daily → percentage → consecutive → forecast → uncategorized
- **Edge case**: Returns `[]` for empty inputs.

```python
alerts = get_all_alerts(txns, rules, cfg["categories"])
# Passes to display.print_alerts(alerts)
```

---

---

# display.py Documentation

## Overview

`display.py` is the **rendering layer**. Every piece of formatted output — tables, panels, progress bars, heatmaps, and text file exports — goes through this module. It uses the `rich` library exclusively; no manual ANSI codes. It reads config via `data.load_config()` only inside `print_transaction_table()` to fetch currency rates for conversion display.

**Authors**: Yang Andi (all functions), Mao Yicheng (`print_outliers`)

---

## Dependencies

### External Libraries
- **rich**: `Console`, `Table`, `Panel`, `Text`, `box` styles

### Internal Modules
- **analytics**: filtering, totals, trends, heatmap, outliers, savings, forecast
- **alerts**: `get_all_alerts()` used inside `export_report()`
- **data**: `load_config()` used inside `print_transaction_table()` to get exchange rates

---

## Global Objects

### `console`
A module-level `rich.Console` instance used by all `print_*` functions. Import it in other modules if needed:

```python
from display import console
console.print("[bold green]Done![/bold green]")
```

---

## Function Reference

### `print_header()`
Renders the app banner panel (`💰 Personal Budget Assistant / COMP1110 B12`) in cyan.

---

### `print_transaction_table(transactions, title="Transaction History")`
Renders a paginated rich table of transactions, newest first.

- Non-HKD amounts show both the original currency and the HKD equivalent as dim text.
- Empty list → shows a "No transactions found" placeholder panel.

---

### `print_statistics(transactions, period_label="All Time")`
Renders a spending breakdown by category with inline bar charts and percentages.

- Bar length is proportional to % share of total.
- Color: green < 30%, yellow 30–50%, red > 50%.
- Empty data → shows a "No spending data" placeholder.

---

### `print_top_categories(transactions, n=3)`
Renders a medal-ranked table of the top N spending categories with HKD totals and % share.

---

### `print_trends(transactions)`
Renders a two-row table comparing 7-day and 30-day daily averages with a trend direction indicator (⬆ red, ⬇ green, → yellow).

---

### `print_alerts(alerts)`
Renders all alerts in a panel.

- Red for `daily_exceeded`, `pct_exceeded`, `consecutive_overspend`.
- Yellow for `forecast_warning`, `uncategorized`.
- Green "All clear" panel if `alerts` is empty.

---

### `print_budget_bars(transactions, budget_rules)`
Renders today's spending progress against each category's daily cap as a bar chart.

- Green < 80% of cap, yellow 80–99%, red ≥ 100%.
- Skips rules without `daily_cap`.

---

### `print_budget_rules(budget_rules)`
Renders all budget rules in a table. Shows `—` for any optional field not set.

---

### `print_savings_goal(transactions, config)`
Renders a savings progress panel showing income, total spent, remaining balance, and % toward the monthly savings goal.

- Requires both `income > 0` and `savings_goal > 0` in config; otherwise shows a setup reminder.

---

### `print_forecast(transactions)`
Renders the projected end-of-month total based on current daily average.

---

### `print_heatmap(transactions)`
Renders a Mon–Sun calendar grid for the current month. Each cell shows a spending intensity symbol color-coded from green (low) to bold red (very high). Days with no spending show `·`.

---

### `print_outliers(transactions)`
Renders the top 5% biggest transactions as a table with date, category, HKD amount, and description. Written by Mao Yicheng.

- Shows a dim placeholder if no outliers exist.

---

### `export_report(transactions, budget_rules, categories, config, filename=None)`
Writes a plain-text monthly summary report to `outputs/`.

- **Parameters**: full data sets + optional custom `filename`
- **Returns**: the filename written (str)
- **Output format**: no colour codes (uses `Console(no_color=True)`), 72-char width
- **Filename**: auto-generated as `outputs/report_YYYYMMDD_HHMMSS.txt` if not provided
- **Contents**: spending by category, 7d/30d trends, top 3 categories, active alerts

---

---

# data.py Documentation

## Overview

`data.py` is the **file I/O layer**. It handles all reading and writing of JSON data files, provides safe fallback defaults on any error, and fetches live currency exchange rates from an external API. All other modules call this module to load or persist data — none of them touch the filesystem directly.

**Authors**: Yao Junzhu (main), Yang Andi (`fetch_exchange_rates`)

---

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `DATA_DIR` | `"data"` | Directory for transaction and rules JSON |
| `CONFIG_DIR` | `"config"` | Directory for config JSON |
| `OUTPUTS_DIR` | `"outputs"` | Directory for exported report files |
| `TRANSACTIONS_FILE` | `data/transactions.json` | Transaction ledger path |
| `BUDGET_RULES_FILE` | `data/budget_rules.json` | Budget rules path |
| `CONFIG_FILE` | `config/config.json` | App config path |
| `DEFAULT_CONFIG` | dict | Fallback config with all required keys |
| `_ISO` | dict | Maps app currency nicknames to ISO 4217 codes (e.g. `"NTD"` → `"TWD"`) |

---

## Function Reference

### `fetch_exchange_rates()`
Fetches live HKD-based exchange rates from `open.er-api.com`.

- **Parameters**: none
- **Returns**: `dict` mapping currency name → HKD rate, or `None` on any failure
- **Logic**: API returns rates as HKD→X; function inverts them to X→HKD so amounts can be multiplied directly.
- **Edge cases**: Returns `None` on network timeout (5 s), non-success API status, or any exception. Callers fall back to cached rates from config.

```python
rates = fetch_exchange_rates()
if rates:
    config["currencies"].update(rates)
```

---

### `ensure_dirs()`
Creates `data/`, `config/`, and `outputs/` directories if they do not exist.

- Uses `exist_ok=True` so it is safe to call multiple times (e.g. at every startup).

---

### `_load_json(filepath, default)` _(private)_
Reads and parses a JSON file with full error handling.

- **Returns**: parsed Python object, or `default` on any of:
  - File not found
  - Empty file
  - Malformed JSON (also prints a warning)

---

### `_save_json(filepath, data)` _(private)_
Writes a Python object to a file as indented JSON (`indent=2`).

---

### `load_transactions()` / `save_transactions(transactions)`
Load or save the transaction ledger. Default on missing file: `[]`.

---

### `load_budget_rules()` / `save_budget_rules(rules)`
Load or save budget rules. Default on missing file: `[]`.

---

### `load_config()` / `save_config(config)`
Load or save app configuration.

- `load_config()` merges any missing keys from `DEFAULT_CONFIG` so older saved configs always get new keys without overwriting existing values.

---

### `get_next_id(transactions)`
Returns the next available transaction ID.

- **Returns**: `1` if list is empty; otherwise `max(existing IDs) + 1`.
- **Edge case**: Handles non-sequential or out-of-order IDs correctly (uses `max`, not `len`).

---

---

# validator.py Documentation

## Overview

`validator.py` provides **input boundary validation** for all user-entered data. It is called by `main.py` before any transaction is accepted. Functions are intentionally simple — they return `bool` or `(bool, value)` and never raise exceptions.

**Author**: Yang Andi

---

## Design Principle

Validation happens only at the user-input boundary (in `main.py`). Internal code trusts that data already in `transactions.json` is valid and does not re-validate it on load.

---

## Function Reference

### `validate_date(date_str)`
Checks that a string is a valid calendar date in `YYYY-MM-DD` format.

- **Parameters**: `date_str` (str)
- **Returns**: `bool`
- **Accepts**: any real calendar date, including past and future dates
- **Rejects**: empty string, wrong format, impossible dates (e.g. `"2026-13-01"`)

```python
validate_date("2026-04-28")   # True
validate_date("not-a-date")   # False
validate_date("")              # False
```

---

### `validate_amount(amount_str)`
Checks that a string represents a strictly positive number.

- **Parameters**: `amount_str` (str)
- **Returns**: `(bool, float)` tuple — `(True, parsed_value)` or `(False, 0.0)`
- **Rejects**: empty string, non-numeric, zero, negative values

```python
validate_amount("99.5")   # (True, 99.5)
validate_amount("-5")     # (False, -5.0)
validate_amount("abc")    # (False, 0.0)
validate_amount("")       # (False, 0.0)
```

---

### `validate_category(category, categories)`
Checks that a category string is in the list of valid categories from config.

- **Parameters**: `category` (str), `categories` (list of str)
- **Returns**: `bool`

```python
validate_category("Food", ["Food", "Transport"])   # True
validate_category("Pizza", ["Food", "Transport"])  # False
```

---

### `validate_description(desc)`
Checks that a description is non-empty and not just whitespace.

- **Parameters**: `desc` (str or None)
- **Returns**: `bool`

```python
validate_description("Lunch")   # True
validate_description("   ")     # False
validate_description("")        # False
```
