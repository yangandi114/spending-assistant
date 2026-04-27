# AI Prompts — COMP1110 Personal Budget Assistant
# This file documents prompts used with GenAI tools (Claude / Deepseek / Gemini) during development.
#
# Labels used below:
#   • Human-written                 — wrote it directly, no AI generation involved (sometimes after seeing AI handle a similar pattern earlier).
#   • AI suggested                  — the idea, library, or approach came from AI; the actual code may be ours or AI's.
#   • AI generated                  — AI produced the code; we read it, tested it, accepted it.
#   • AI generated + human polished — AI produced the first draft, we reviewed, tested, edited, sometimes re-prompted multiple times.

---

## main.py

**Overall structure — AI generated + human polished**
> **[1]** "I'm building a Python terminal app for tracking personal spending and managing budget. what's a good way to structure the menu navigation so it's easy to add new options later?"

> **[2]** "show me how to set up the main loop using a dispatch dict so each menu item maps to a handler function, using questionary for interactive menus and rich for coloured output. the menu should have: Add Transaction, View/Filter Transactions, Edit/Delete Transaction, Statistics, Alerts, Budget Rules, Categories, Settings, Export Report"

> **[3]** "also wrap the loop in try/except KeyboardInterrupt so ctrl+c quits cleanly with a goodbye message instead of a stack trace"

**Custom questionary STYLE theme — AI suggested**
> **[1]** "is there a way to customise the colours of the questionary select prompt? the default styling looks plain"

> **[2]** "how do I define a Style object and apply it globally? I want the selected item and pointer to be bright green (#00ff88), and separators to be dim grey italic. the answer line should also stay green so it's consistent"

**_sep() Separator helper — AI suggested**
> **[1]** "can I add non-selectable section labels inside a questionary select menu, like dividers between groups of options?"

> **[2]** "show me how to add separators with labels like '-- Transactions --' between groups of items in a questionary.select() choices list. also a plain dashed line one for spacing"

**ask / choose / confirm / pause wrappers — Human-written**
Thin wrappers around `questionary.text/select/confirm/press_any_key_to_continue`. They exist to (a) apply our STYLE everywhere without repeating the kwarg and (b) raise `KeyboardInterrupt` when `.ask()` returns `None` (questionary returns None on ctrl+c) so the main loop can catch a single exception and quit gracefully. Wrote these myself once I noticed I was copy-pasting the same `if result is None: raise KeyboardInterrupt` block in multiple places.

**find_transaction_by_id() — Human-written**
Plain linear search through the transactions list.

**show_hkd_conversion() — Human-written**
prints the HKD-equivalent in dim text if the currency isn't already HKD. Used inside add_transaction_flow.

**get_valid_date / get_valid_amount / get_valid_percentage / get_valid_description — AI generated + human polished**
> **[1]** "what's a good pattern for repeatedly asking the user for input until they give something valid in a terminal app?"

> **[2]** "write helper functions using questionary.text() that keep prompting until valid input is given. need one for dates in YYYY-MM-DD format, one for positive float amounts, one for percentages 1-100, and one for non-empty descriptions. use my validator module. print red error messages on bad input"

> **[3]** "for the date one, default the prompt to today's date so the user can just press enter most of the time"

**add_transaction_flow() — AI generated + human polished**
> **[1]** "how should I structure a multi-step input form in a terminal app where the user enters several fields one by one?"

> **[2]** "write the add transaction function. should ask for: date, amount, currency from a list, category from config (plus an Uncategorized fallback option), description. after saving, immediately check budget alerts and show today's budget progress bars. use my existing load/save functions and the get_valid_* helpers"

> **[3]** "actually filter out the 'uncategorized' alerts when showing the post-add alerts — those should only show in the dedicated alerts view, otherwise it's noisy after every add"

**view_transactions_flow() — AI generated + human polished**
> **[1]** "what filtering options would make sense for a transaction history view?"

> **[2]** "write the view transactions flow with these modes: All, Filter by Date Range, Filter by Category, Search by Keyword. use questionary.select with grouped separators (Browse, Filter). for date range validate start <= end. keyword search should be case-insensitive against description"

**select_transaction_by_id() + edit_transaction_field() — AI generated + human polished**
> **[1]** "what's a clean way to let users pick and edit a specific record from a list in a terminal app?"

> **[2]** "write a flow where the user sees a transaction table, enters an ID to select it, then chooses to edit a specific field or delete it. handle invalid IDs (non-number, not found) with a re-prompt loop. let user type 'q' to cancel out. for editing, dispatch to different input helpers based on which field was chosen (Date / Amount / Currency / Category / Description)"

**edit_delete_flow() — AI generated + human polished**
> **[1]** "wire up the select-then-act flow — show table first, pick a row, then ask edit / delete / cancel"

> **[2]** "write the outer flow that prints the transaction table, calls select_transaction_by_id, then offers Edit Field / Delete Transaction / Cancel. delete should confirm first. edit should pick a field and dispatch to edit_transaction_field. save afterwards"

**statistics_flow() — AI generated + human polished**
> **[1]** "how do I organise a sub-menu with grouped sections using questionary? like having headers between groups of options"

> **[2]** "write a statistics sub-menu with grouped separators for Overview, Trends & Forecast, and Visuals sections. options: Category Totals (current month + all time), Top 3 Categories, Major Expenses (Top 5%), 7d vs 30d trend, Forecast, Budget Progress Bars, Spending Heatmap"

**alerts_flow() — Human-written**
load transactions, load rules, call `get_all_alerts` and `print_alerts`.

**add_or_update_budget_rule() — AI generated + human polished**
> **[1]** "how should i ask the user to set up a budget rule that has multiple optional fields?"

> **[2]** "write a function that picks a category, then for each of daily_cap / monthly_cap / pct_threshold ask confirm() if they want to set it, and if yes ask for the value. if a rule for that category already exists in budget_rules, replace it; otherwise append. save afterwards"

**manage_budget_rules_flow() — AI generated + human polished**
> **[1]** "wrap the budget rule editing in a sub-menu — view / add-update / delete"

> **[2]** "write manage_budget_rules_flow. View Rules just calls print_budget_rules. Add/Update calls add_or_update_budget_rule. Delete should list existing rule categories in a select menu and confirm before removing"

**view_categories / add_category / remove_category / manage_categories_flow — Human-written**
Simple list operations on `config["categories"]`. Print the list, append a new name (with duplicate check), or remove a chosen one (with confirmation). Save config after each change.

**set_income / set_savings_goal — Human-written**
Each shows the current value in the prompt, asks for a new amount via `get_valid_amount`, writes to config, saves.

**update_exchange_rate() — Human-written**
Lists all current rates, asks if user wants to update one, picks the currency, asks for the new rate, validates positive float, saves. Re-prompts on bad input.

**settings_flow() — AI generated + human polished**
> **[1]** "build a settings sub-menu grouped under Income & Goals and Currencies"

> **[2]** "write settings_flow with sections: Set Monthly Income, Set Savings Goal, View Savings Progress, Currency Exchange Rates. dispatch to the matching handler functions"

**export_flow() — Human-written**
Three-line wrapper that loads the data and calls `export_report`. Just shows the resulting filename in green.

**fetch_exchange_rates integration in main() — AI generated + human polished**
**The live exchange rate feature was Andi's idea (Yang Andi).** I'd been hard-coding rates in DEFAULT_CONFIG and didn't like that it is not live updated, especially since I travel and use multiple currencies. I asked AI which API to use — AI suggested the open.er-api.com free endpoint (no key needed). I then told AI to write the rates back into the existing config.json so the rest of the app (which reads `config["currencies"]`) wouldn't need to change at all.

> **[1]** "ok so at startup I want to fetch live exchange rates. update the config and print a green ✓. fall back to the cached rates if failed to fetch rates for robustness of the program.

> **[2]** "make sure ensure_dirs() runs before fetch_exchange_rates so the config dir exists when we try to write"

---

## data.py

**fetch_exchange_rates() — AI generated + human polished, idea by Yang Andi**
AI suggested the API and wrote the urllib request; I added the fallback behaviour and asked AI to invert the rates because the API gives "1 HKD = X currency" but I want "1 currency = X HKD" for easier conversion. **I also suggested storing the result in our existing config.json** rather than a separate rates file or in-memory cache — keeps everything in one place and the rest of the code already reads `config["currencies"]`.

> **[1]** "i want to fetch live exchange rates from a free api in python. don't want to install requests, just stdlib. what api should i use?"

> **[2]** "use open.er-api.com/v6/latest/HKD with urllib.request.urlopen. base currency HKD. the api returns 'how many X for 1 HKD' but I want 'X HKD = 1 X', so invert it. Only keep the currencies my app supports (HKD, CNY, JPY, KRW, NTD, USD, GBP, EUR). round to 6 decimals. return None on failure so the program can fall back to cached rates"

> **[3]** "btw NTD is what we call it locally but the ISO code is TWD — handle that mapping with a small dict"

**_load_json() with error handling — AI generated**
> **[1]** "what are all the errors that can happen when loading a json file in python and how should I handle them?"

> **[2]** "write a safe json file loader that handles FileNotFoundError, empty files, and JSONDecodeError separately. return a default value for all failure cases. for decode errors print a warning so the user knows the file is corrupted"

**load_config() with default merging — AI suggested**
> **[1]** "my config json file might be missing some keys if it was saved by an older version. how do I make sure all keys are always present when I load it?"

> **[2]** "show me how to merge a loaded config dict with a DEFAULT_CONFIG dict so any missing keys get filled in automatically, without overwriting keys that already exist"

**ensure_dirs / _save_json / get_next_id / load_transactions / save_transactions / load_budget_rules / save_budget_rules / save_config — Human-written**
`ensure_dirs` is a `for d in dirs: os.makedirs(d, exist_ok=True)` loop. `_save_json` is `json.dump(data, f, indent=2)`. `get_next_id` is `max(t["id"] for t in transactions) + 1`, with a guard for the empty list. The four load/save functions are one-liners that call `_load_json` / `_save_json` with the right path and default.

**DEFAULT_CONFIG and _ISO mapping — Human-written**
Picked the currencies I actually use (HKD primary; CNY for mainland trips; JPY/KRW/NTD/USD/GBP/EUR for travel/online purchases).

---

## analytics.py

**Overall module — AI generated + human polished**
> **[1]** "what kinds of statistics and analytics would be useful to include in a personal spending tracker app for a uni student?"

> **[2]** "write a Python analytics module that works on a list of transaction dicts with keys: id, date, amount, currency, category, description. include functions for: filtering by date range, totals by category, top N categories with percentage share, 7-day vs 30-day daily average trends, per-day totals for a category, consecutive days over a daily cap, savings progress given income and goal, linear end-of-month forecast, and a spending heatmap"

**parse_date / filter_by_date / get_totals_by_category / get_daily_totals_by_category — Human-written**
Standard `datetime.strptime` + for-loop patterns. `filter_by_date` does two boundary checks (start, end). `get_totals_by_category` and `get_daily_totals_by_category` both use `defaultdict(float)` with a single accumulator loop.

**get_top_n_categories — AI generated + human polished**
> **[1]** "given totals per category, give me the top n with their percentage share of the total"

> **[2]** "return list of (category, amount, percentage) tuples sorted descending by amount, top n only. handle total == 0 without dividing by zero"

**get_spending_trends — Human-written**
Filter to last 7 days and last 30 days, divide each sum by the day count. Two `if list else 0` guards for empty data. Returns a tuple.

**get_consecutive_overspend() — AI generated**
> **[1]** "how do I check if something happened several days in a row, going backwards from today?"

> **[2]** "given daily totals for a category and a daily cap, count how many consecutive most-recent days went over the cap. stop counting at the first day under the cap"

**get_savings_progress — Human-written**
Sum month-to-date spending, then compute `remaining = income - spent` and `savings = remaining - savings_goal`.

**linear_forecast() — AI generated**
> **[1]** "how would I predict how much a user will spend by the end of the month based on what they've spent so far?"

> **[2]** "function that gets transactions this month, calculates average daily spend so far, projects total for the full month. use calendar.monthrange to get the correct number of days. handle 0 transactions case"

**spending_heatmap() — AI generated + human polished**
> **[1]** "how do I bucket daily spending values into different intensity levels for a heatmap visualisation in the terminal?"

> **[2]** "write a function that returns a dict mapping date string to (symbol, amount). compare each day's spending to the monthly daily average. use unicode block symbols for showing percentage."

**get_spending_outliers() — AI generated, docstring polished by Mao Yicheng**
> **[1]** "how do I get the top 5 percent of values from a list in python?"

> **[2]** "write a function that returns the top X percent of transactions sorted by amount descending, with a minimum of 1 result"

---

## alerts.py

**Overall module — AI generated + human polished (docstrings + .get() access by Mao Yicheng)**
> **[1]** "what kinds of budget alerts should be in a spending tracker?"

> **[2]** "write an alerts module that checks transactions against budget rules. each rule is a dict with a category key and optional daily_cap, monthly_cap, pct_threshold. write separate functions for: daily cap exceeded today, category exceeds percentage share of total spending, consecutive days over daily cap, forecast exceeds a monthly limit, and transactions with unknown categories. each alert should be a dict with at least 'type' and 'message' keys"

**check_daily_caps — AI generated + human polished**
Generated as part of the module-level prompt above. Polished to compare against today's date *string* (matching how dates are stored in transactions) instead of a full datetime object.

**check_percentage_thresholds — AI generated**
total all spending, get each category's percentage, alert if over threshold.

**check_consecutive_overspend() — AI generated**
> **[1]** "how do I check if something happened several days in a row, going back from today?"

> **[2]** "function that walks the rules with a daily_cap, calls get_consecutive_overspend, emits an alert if the streak is 3 or more days. include the streak count in the message"

**check_forecast_alerts — Human-written**
Sum all `monthly_cap` values across rules to get a total monthly budget, then compare against `linear_forecast(transactions)`. Emit one alert if projected > total.

**check_uncategorized — Human-written**
For-loop, `t.get("category", "Uncategorized")`, check membership in the categories list, append alert if missing or unknown.

**get_all_alerts — Human-written**
Calls each of the five check functions and concatenates the lists.

---

## display.py

**Overall module — AI generated + human polished (by Andi); print_outliers by Mao Yicheng**
> **[1]** "what's the best way to display nicely formatted output in a Python terminal app? tables, colours, panels etc"

> **[2]** "write a display module using the rich library. use Tables, Panels, and Text objects, no manual ANSI codes. include functions for: a header banner, transaction table with multi-currency support, spending by category with a bar chart column, top N categories with medal ranking, 7-day vs 30-day trend with direction indicator, budget alerts panel with colour coding, daily budget progress bars, savings goal progress bar, forecast table, monthly calendar heatmap grid, and a plain text report exporter"

**print_header — Human-written**
Centered Text in a Panel with cyan border.

**print_transaction_table() with multi-currency — AI generated + human polished**
> **[1]** "how do I cleanly show amounts in different currencies in the same table column?"

> **[2]** "for non-HKD transactions, show both the original amount and the HKD equivalent as dim text side by side in a rich Table. for HKD transactions just show the HKD amount normally. sort rows newest first. use rounded box style"

**print_statistics — AI generated + human polished**
> **[1]** "render a per-category spending table with an inline ascii bar chart column"

> **[2]** "for each category show: name, amount, a Unicode progress bar based on percentage of total, and the percentage. colour the bar red >50%, yellow >30%, else green. print the grand total below the table"

**print_top_categories — AI generated + human polished**
Generated from the module-level prompt. Polished to use emoji medals for the top 3 instead of plain numbering. I asked AI to make it "feel a bit more rewarding visually".

**print_trends — Human-written**
Small rich Table with three rows: 7d avg, 30d avg, trend direction. Direction picks red / green / yellow based on the percentage difference. Empty-data branch returns "Not enough data" in dim.

**print_alerts — AI generated + human polished**
> **[1]** "render a list of alerts as a colour-coded panel using rich"

> **[2]** "if there are no alerts show a green 'all clear' panel. otherwise build a Text with one line per alert: red bold for daily_exceeded / pct_exceeded / consecutive_overspend, yellow bold for everything else (uncategorized, forecast). wrap in a red-bordered Panel titled '⚠️ Budget Alerts'"

**print_budget_bars — AI generated + human polished**
> **[1]** "render today's budget progress as a row-per-category table with progress bars"

> **[2]** "for each rule that has a daily_cap, compute today's spend in that category, render a unicode progress bar (clamp filled at 20), colour red >=100%, yellow >=80%, else green. show columns: Category, Progress bar, Spent, Limit, %"

**print_budget_rules — Human-written**
Plain rich Table with four columns showing each rule's category, daily cap, monthly cap, % threshold. Show '—' for any optional field that isn't set.

**print_savings_goal — AI generated + human polished**
> **[1]** "render a savings goal progress card showing income, spent, remaining, goal, a progress bar, and a status line"

> **[2]** "compute progress as savings / goal * 100 (clamp 0-100). progress bar. colour green if savings >= goal, yellow if positive, red if negative. status line either 'Goal achieved!' in green or 'Need HK$X more' in yellow. show a placeholder if income or goal isn't set"

**print_forecast — Human-written**
Two row table — "Based on N days of data" and "Projected total HK$X". Calls `linear_forecast`.

**print_heatmap() calendar grid — AI generated + human polished**
> **[1]** "I want to show a calendar grid in the terminal for the current month, with Mon-Sun as columns. what's the easiest way to get the correct day offsets in python?"

> **[2]** "render the grid using a rich Table with 7 columns (Mo Tu We Th Fr Sa Su). each cell shows a unicode symbol from spending_heatmap (· for no spending, unicode characters for low/medium/high/very high). colours green/yellow/red/bold red."

**print_outliers() — AI generated + human polished by Mao Yicheng**
> **[1]** "how would I identify unusually large transactions compared to the user's normal spending?"

> **[2]** "write a function that displays the top 5 percent of transactions by amount in a rich table. show date, category, amount in HKD, and description. if no outliers exist print a dim placeholder message"

**export_report() plain text file — AI generated + human polished**
> **[1]** "how do I write output to a plain text file using rich without including any colour codes or markup?"

> **[2]** "write a function that exports a spending summary report as a plain .txt file using a rich Console pointed at a file with no_color=True and width=72. include sections for: header with month + timestamp, spending by category (amount, percentage, total), 7-day and 30-day averages with trend %, top 3 categories, active alerts. auto-generate a timestamped filename like outputs/report_YYYY-MM-DD_HHMMSS.txt"

---

## validator.py

**All four functions — AI suggested approach, code Human-written**
Asked AI for the general pattern but the functions are short enough I just wrote them directly. `validate_date` uses `datetime.strptime` in a try/except. `validate_amount` tries `float()` and checks `> 0`, returns a `(bool, value)` tuple so the caller doesn't have to re-parse. `validate_category` is an `in` membership check. `validate_description` is `bool(desc and desc.strip())`. The `(bool, value)` return shape on `validate_amount` was AI's suggestion.

> **[1]** "what's a clean way to handle input validation for things like dates and numbers in python? want simple functions that return bool, called from a re-prompt loop in the program"

---

## Questionary library usage (general)

**Choosing questionary itself — AI suggested**
> **[1]** "is there a python library for building interactive terminal menus with arrow key navigation? I don't want to just print numbered options and parse the input"

> **[2]** "show me how to use questionary. need: arrow-key select menus, text input with a default value, yes/no confirmation, press any key to continue, and how to detect if the user cancelled with ctrl+c?"

---

## tests/test_generator.py

**Test data generator — AI generated + human polished by Wang Ziyi**
> **[1]** "generate a script that generates realistic fake transaction data to test my budget app. categories are Food, Transport, Personal, Entertainment, Health, Utilities. about 120 transactions over the past month or so"

> **[2]** "for each category have a list of realistic Hong Kong descriptions (eg McDonald's, MTR fare, Uniqlo, Netflix etc). amounts should be in a category-appropriate range — Food 15-120, Transport 5-55, Personal 50-400, Entertainment 30-600, Health 20-250, Utilities 100-600. dates random within the past 30 days. mostly HKD but 30% in other currencies."

> **[3]** "also put some edge cases for testing"

> **[4]** "generate matching budget_rules.json (one rule per category with daily/monthly/pct thresholds tuned so the Entertainment spike actually triggers them) and a config.json with realistic student income (HK$12000) and savings goal (HK$2000)"

---
