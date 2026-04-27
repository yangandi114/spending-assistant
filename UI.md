# UI Design Specifications

**Owner**: Yang Andi (UI Design Lead)  
**Libraries**: `rich` (output/rendering) + `questionary` (interactive prompts)

---

## Library choices

| Library | Purpose | Rationale |
|---------|---------|-----------|
| `rich` | Tables, panels, progress bars, colored text | More readable than plain print; no manual ANSI needed |
| `questionary` | Arrow-key menu selection, text input, confirm prompts | Better UX than numbered input |
| Built-ins | File I/O, date logic, HTTP (`urllib`) | Keeps dependencies minimal |

Only two external dependencies. `rich` and `questionary` are both stable and widely used — no risk of breaking on the assignment marker's machine.

---

## Main menu

Menu is driven by `questionary.select()` with a custom green-tinted style and labelled separators to group related options. Separators use `questionary.Separator` with a dash pattern.

Actual menu output:

```
  Personal Budget Assistant
  COMP1110  B12

  -- Transactions ----
> Add Transaction
  View / Filter Transactions
  Edit / Delete Transaction
  -- Analytics ----
  Statistics & Analytics
  Check Budget Alerts
  -- Management ----
  Budget Rules
  Manage Categories
  Settings
  ---
  Export Summary Report
  Exit
```

Custom style used (defined once in `main.py` as `STYLE`):

```python
STYLE = Style([
    ("pointer",     "fg:#00ff88 bold"),
    ("highlighted", "fg:#00ff88 bold"),
    ("question",    "bold"),
    ("answer",      "fg:#00ff88 bold"),
    ("separator",   "fg:#555555 italic"),
])
```

After each action, `questionary.press_any_key_to_continue()` pauses before returning to the menu. `Ctrl+C` at any prompt exits gracefully via `KeyboardInterrupt`.

---

## Input prompts

All text input uses thin wrappers around `questionary.text()` / `questionary.select()` / `questionary.confirm()` defined in `main.py`. Each wrapper raises `KeyboardInterrupt` if the user cancels (returns `None`), so the main loop can exit cleanly.

Validation re-prompts until input is valid — no crashes, just an inline error message:

```
Invalid date. Use YYYY-MM-DD.
```

| Input | Validation | Re-prompt |
|-------|-----------|-----------|
| Date | `datetime.strptime(s, "%Y-%m-%d")` | Yes |
| Amount | `float(s) > 0` | Yes |
| Percentage | `0 < float(s) <= 100` | Yes |
| Description | non-empty after `.strip()` | Yes |
| Category | `questionary.select()` from config list | N/A |
| Currency | `questionary.select()` from config list | N/A |

Validation logic lives in `validator.py`; the prompt wrappers in `main.py` call it and loop.

---

## Transaction table

Rendered by `print_transaction_table()` in `display.py` using `rich.Table` with `box.ROUNDED`. Sorted newest-first.

```
                    Transaction History
 ID  Date        Amount                  Category  Description
  3  2026-04-02  CNY 88.00 ~ HK$100.72  Food      Hotpot
  2  2026-04-01  USD 12.50 ~ HK$ 97.89  Transport MTR fare
  1  2026-04-01  HK$50.50               Food      Lunch
```

HKD amounts display as `HK$xx.xx`. Foreign currencies show both the original and HKD equivalent using live rates from config. Conversion rates are fetched at startup and cached in `config.json`.

---

## Statistics & analytics

All statistics are in the `statistics_flow()` sub-menu. Each option calls a dedicated `print_*` function in `display.py`.

**Category totals** — table with inline unicode bar chart, color-coded by share:

```
         Spending by Category -- April 2026
 Category      Amount      Bar                     %
 Entertainment HK$1823.40  [red]████████████░░░░░░░░[/]  61.2%
 Food          HK$688.30   [yellow]████████░░░░░░░░░░░░[/]  23.1%
 Transport     HK$472.00   [green]█████░░░░░░░░░░░░░░░░[/]  15.8%

  Total: HK$2983.70
```

Red if >50%, yellow if >30%, green otherwise.

**Top 3 categories** — medal icons (1st/2nd/3rd), amount, and share percentage.

**Major expenses (top 5%)** — written by Mao Yicheng. Shows the largest transactions by amount (top 5% of the list), displayed as a table.

**Spending trends (7d vs 30d)** — compares daily average over the last 7 days against the last 30. Shows direction as up/down with percentage change:

```
 7-day avg   HK$185.71/day
 30-day avg  HK$165.00/day
 Trend       +12.6%  (spending more)
```

**Spending forecast** — extrapolates this month's total from the daily average so far:

```
 Based on      12 days of data
 Projected total   HK$3850.00
```

**Budget progress bars** — shows today's spending vs daily cap for each category with a bar:

```
                Today's Budget Progress
 Category      Progress              Spent     Limit    %
 Food          [green]████░░░░░░░░░░░░░░░░░░[/]  HK$32.00  HK$80.00  40.0%
 Entertainment [red]████████████████████[/]  HK$105.00 HK$100.00 105.0%
```

Green < 80%, yellow 80-99%, red >= 100%.

**Spending heatmap** — monthly calendar grid (Mon-Sun columns). Each day cell is a unicode block showing spending intensity relative to the month's daily average:

```
 August 2026 -- Spending Heatmap
 Mo  Tu  We  Th  Fr  Sa  Su
 ·   ·   ░   ░   ▒   ▓   ·
 █   ░   ·   ▒   ░   ·   ·
 ...
```

`░` low, `▒` medium, `▓` high, `█` very high, `·` no spending.

---

## Budget alerts

All alert checks are in `alerts.py`; rendering is in `print_alerts()` in `display.py`. Alerts also trigger automatically after adding a transaction.

Alert types:
- **daily_exceeded** — today's spending exceeded a category's daily cap
- **pct_exceeded** — a category's share of total spending is over its threshold
- **consecutive_overspend** — 3+ consecutive days over the daily cap
- **forecast_warning** — projected month-end total exceeds total monthly caps
- **uncategorized** — transaction has an unknown or missing category

Rendered in a red-bordered panel. Serious alerts (daily, pct, streak) get a red bullet; uncategorized get yellow:

```
 Budget Alerts
 [red]  Food: Daily limit exceeded! (HK$105.00 / HK$80.00)
  Entertainment: 61.2% of total (limit: 25%)[/]
 [yellow]  Transaction #12 has invalid/unknown category: 'Misc'[/]
```

All clear shows a green panel instead.

---

## Settings

Accessible from the main menu. Options:
- Set monthly income (stored in `config.json`)
- Set savings goal (stored in `config.json`)
- View savings progress — shows income, spent, remaining, goal progress bar, and status
- Currency exchange rates — view current rates and optionally override one manually

Live rates are fetched from `open.er-api.com` at startup via `urllib.request` and written to `config.json`. If the fetch fails (offline), cached rates are used with a warning printed to the menu.

---

## Export report

Saved to `outputs/report_YYYY-MM-DD_HHmmss.txt`. Uses `Console(file=f, no_color=True, width=72)` — plain text, no ANSI codes, readable in any editor.

Report sections:
1. Header with month and generation timestamp
2. Spending by category (amounts + percentages)
3. Spending trends (7d vs 30d averages)
4. Top 3 categories
5. Active alerts

---

## Architecture summary

```
main.py
  menu loop (questionary.select)
  sub-flow functions (add, view, edit, stats, alerts, rules, settings, export)
  input wrappers (ask, choose, confirm, pause)
  HKD conversion helper (show_hkd_conversion)

display.py
  console = Console()  -- single instance, shared via import
  print_header / print_transaction_table / print_statistics
  print_top_categories / print_trends / print_alerts
  print_budget_bars / print_budget_rules / print_savings_goal
  print_heatmap / print_forecast / print_outliers
  export_report

validator.py
  validate_date / validate_amount / validate_category / validate_description
```

---

## File responsibilities

| File | Owner |
|------|-------|
| `main.py` (menu, flows, wrappers) | Yang Andi |
| `display.py` (all rendering) | Yang Andi; `print_outliers` by Mao Yicheng |
| `validator.py` | Yang Andi |
| `alerts.py` (logic) | Mao Yicheng, Yang Andi |
| `analytics.py` | Mao Yicheng, Yang Andi |
| `data.py` | Yao Junzhu |
