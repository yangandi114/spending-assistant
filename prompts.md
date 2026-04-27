# AI Prompts — COMP1110 Personal Budget Assistant
# This file documents prompts used with GenAI tools (Claude / Deepseek / Gemini) during development.
# Code marked as "AI generated + human polished" means AI produced the first draft and we reviewed, tested, and adjusted it.

---

## main.py

**Overall structure — AI generated + human polished**
> **[1]** "I'm building a Python terminal app for tracking personal spending. what's a good way to structure the menu navigation so it's easy to add new options later?"

> **[2]** "show me how to set up the main loop using a dispatch dict so each menu item maps to a handler function, using questionary for interactive menus and rich for coloured output. the menu should have: Add Transaction, View/Filter Transactions, Edit/Delete Transaction, Statistics, Alerts, Budget Rules, Categories, Settings, Export Report"

**STYLE + custom questionary theme — AI suggested**
> **[1]** "is there a way to customise the colours of the questionary select prompt? the default styling looks plain"

> **[2]** "how do I define a Style object and apply it globally? I want the selected item and pointer to be bright green, and separators to be dim grey"

**_sep() Separator helper — AI suggested**
> **[1]** "can I add non-selectable section labels inside a questionary select menu, like dividers between groups of options?"

> **[2]** "show me how to add separators with labels like '-- Transactions --' between groups of items in a questionary.select() choices list"

**get_valid_date / get_valid_amount / get_valid_percentage / get_valid_description — AI generated + human polished**
> **[1]** "what's a good pattern for repeatedly asking the user for input until they give something valid in a terminal app?"

> **[2]** "write helper functions using questionary.text() that keep prompting until valid input is given. I need one for dates in YYYY-MM-DD format, one for positive float amounts, one for percentages 1-100, and one for non-empty descriptions. use a validator module I already have"

**add_transaction_flow() — AI generated + human polished**
> **[1]** "how should I structure a multi-step input form in a terminal app where the user enters several fields one by one?"

> **[2]** "write the add transaction function that asks for date, amount, currency from a list, category from config, and description. after saving, immediately check budget alerts and show a budget progress bar. use my existing load/save functions"

**edit_delete_flow() + edit_transaction_field() + select_transaction_by_id() — AI generated + human polished**
> **[1]** "what's a clean way to let users pick and edit a specific record from a list in a terminal app?"

> **[2]** "write a flow where the user sees a transaction table, enters an ID to select it, then chooses to edit a specific field or delete it. handle invalid IDs with a re-prompt loop. for editing, dispatch to different input helpers based on which field was chosen"

**statistics_flow() — AI generated + human polished**
> **[1]** "how do I organise a sub-menu with grouped sections using questionary? like having headers between groups of options"

> **[2]** "write a statistics sub-menu with grouped separators for Overview, Trends & Forecast, and Visuals sections. options include: category totals for current month and all time, top 3 categories, major expenses, 7-day vs 30-day trend, forecast, budget progress bars, and a heatmap"

**fetch_exchange_rates integration in main() — AI generated**
> **[1]** "how do I run something at startup and show a loading indicator while waiting for it to finish?"

> **[2]** "at startup, fetch live exchange rates from an API, update the config if successful, and fall back to cached rates silently if it fails. show a status indicator while fetching"

---

## data.py

**fetch_exchange_rates() — AI generated + human polished**
> **[1]** "how do I make an HTTP request in Python without installing the requests library? just using built-ins"

> **[2]** "write a function that fetches live exchange rates from the open.er-api.com free API using only urllib. base currency is HKD. convert the response so each currency maps to how many HKD one unit is worth. return None on any failure so the caller can fall back to cached rates"

**_load_json() with error handling — AI generated**
> **[1]** "what are all the errors that can happen when loading a JSON file in Python and how should I handle them?"

> **[2]** "write a safe JSON file loader that handles FileNotFoundError, empty files, and JSONDecodeError separately. return a default value for all failure cases and print a warning for decode errors"

**load_config() with default merging — AI suggested**
> **[1]** "my config JSON file might be missing some keys if it was saved by an older version of the app. how do I make sure all keys are always present when I load it?"

> **[2]** "show me how to merge a loaded config dict with a DEFAULT_CONFIG dict so any missing keys get filled in automatically, without overwriting keys that already exist"

---

## analytics.py

**Overall module — AI generated + human polished**
> **[1]** "what kinds of statistics and analytics would be useful to include in a personal spending tracker app?"

> **[2]** "write a Python analytics module that works on a list of transaction dicts with keys: id, date, amount, currency, category, description. include functions for: filtering by date range, totals by category, top N categories with percentage share, 7-day vs 30-day daily average trends, per-day totals for a category, consecutive days over a daily cap, savings progress given income and goal, linear end-of-month forecast, and a spending heatmap"

**linear_forecast() — AI generated**
> **[1]** "how would I predict how much a user will spend by the end of the month based on what they've spent so far?"

> **[2]** "write a function that gets all transactions this month so far, calculates average daily spend, and projects the total for the full month. use the calendar module to get the correct number of days in the month"

**spending_heatmap() — AI generated + human polished**
> **[1]** "how do I categorise daily spending values into different intensity levels for a heatmap visualisation?"

> **[2]** "write a function that returns a dict mapping date strings to a symbol and amount. compare each day's spending to the monthly daily average and assign a symbol based on the ratio — low, medium, high, very high"

**get_spending_outliers() — AI generated, docstring by Mao Yicheng**
> **[1]** "how do I get the top 5 percent of values from a list in Python?"

> **[2]** "write a function that returns the top X percent of transactions sorted by amount descending, with a minimum of 1 result"

---

## alerts.py

**Overall module — AI generated + human polished (docstrings + .get() access by Mao Yicheng)**
> **[1]** "what kinds of budget alerts would make sense in a personal spending tracker?"

> **[2]** "write an alerts module that checks transactions against budget rules. each rule is a dict with a category key and optional daily_cap, monthly_cap, pct_threshold. write separate functions for: daily cap exceeded today, category exceeds percentage share of total spending, consecutive days over daily cap, forecast exceeds a monthly limit, and transactions with unknown categories. return alert dicts with type and message keys"

**check_consecutive_overspend() — AI generated**
> **[1]** "how do I check if something happened several days in a row, going backwards from today?"

> **[2]** "write a function that checks how many consecutive days going backwards from today a category has exceeded its daily cap, using a get_daily_totals_by_category function I already have. alert if the streak is 3 or more days"

---

## display.py

**Overall module — AI generated + human polished (by Andi); print_outliers by Mao Yicheng**
> **[1]** "what's the best way to display nicely formatted output in a Python terminal app? tables, colours, panels etc"

> **[2]** "write a display module using the rich library. use Tables, Panels, and Text objects, no manual ANSI codes. include functions for: a header banner, transaction table with multi-currency support, spending by category with a bar chart column, top N categories with medal ranking, 7-day vs 30-day trend with direction indicator, budget alerts panel with colour coding, daily budget progress bars, savings goal progress bar, forecast table, monthly calendar heatmap grid, and a plain text report exporter"

**print_transaction_table() with multi-currency — AI generated + human polished**
> **[1]** "how do I cleanly show amounts in different currencies in the same table column?"

> **[2]** "for non-HKD transactions, show both the original amount and the HKD equivalent as dim text side by side in a rich Table. for HKD transactions just show the HKD amount normally"

**print_heatmap() calendar grid — AI generated + human polished**
> **[1]** "I want to show a calendar grid in the terminal for the current month, with Mon-Sun as columns. what's the easiest way to get the correct day offsets in Python?"

> **[2]** "now how do I render this using the rich library? each cell should show a symbol representing how much the user spent that day, colour coded green to red based on spending intensity"

**export_report() plain text file — AI generated**
> **[1]** "how do I write output to a plain text file using rich without including any colour codes or markup?"

> **[2]** "write a function that exports a spending summary report as a plain .txt file using a rich Console pointed at a file with no colour. include: spending by category with percentages, 7-day and 30-day averages, top 3 categories, and active alerts. auto-generate a timestamped filename in an outputs/ folder"

**print_outliers() — AI generated + human polished by Mao Yicheng**
> **[1]** "how would I identify unusually large transactions compared to the user's normal spending?"

> **[2]** "write a function that displays the top 5 percent of transactions by amount in a rich table. show date, category, amount in HKD, and description. if no outliers exist print a dim placeholder message"

---

## validator.py

**Whole file — AI suggested**
> **[1]** "what's a clean way to handle input validation for things like dates and numbers in Python?"

> **[2]** "write simple validation functions for a budget app: check a date string is in YYYY-MM-DD format, check a string is a positive float, check a category is in a given list, and check a description is non-empty. return bool or (bool, value) tuples"

---

## Questionary library usage (general)

**How to use questionary — AI suggested**
> **[1]** "is there a Python library for building interactive terminal menus with arrow key navigation? I don't want to just print numbered options"

> **[2]** "show me how to use the questionary library to build interactive menus. I need: arrow-key select menus, text input with a default value, yes/no confirmation, press-any-key-to-continue, and how to detect if the user cancelled with Ctrl+C so I can handle it gracefully"

---

## tests/test_generator.py

**Test data generator — AI generated**
> **[1]** "how do I generate a large set of realistic fake transaction data to test my budget app?"

> **[2]** "write a script that generates 120+ fake transactions spread over the past 30 days. use categories: Food, Transport, Personal, Entertainment, Health, Utilities, with random amounts and dates. also include edge cases: 5 uncategorized transactions, a spike of Entertainment transactions in the last 5 days to trigger consecutive overspend alerts, and some very large transactions to test outlier detection"
