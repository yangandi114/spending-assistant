# COMP1110 B12 — Personal Budget & Spending Assistant

**Project**: Personal Budget & Spending Assistant (Topic A)  
**Members**: Mao Yicheng, Tao Xinran, Wang Ziyi, Yang Andi, Yao Junzhu  
**Repo**: `comp1110-project` (private)

---

## 📋 Quick Links

| Document | Purpose |
|----------|---------|
| [MAIN_DOCUMENTATION.md](MAIN_DOCUMENTATION.md) | Full module & function reference |
| [prompts.md](prompts.md) | AI prompts used during development |
| [requirements.txt](requirements.txt) | Python dependencies |

## 🗂️ Project Structure

```
./
├── main.py              ← Entry point; questionary menu loop
├── display.py           ← All rich rendering (tables, panels, alerts)
├── analytics.py         ← Statistics, trends, forecasting, heatmap
├── alerts.py            ← Alert logic (caps, thresholds, streaks)
├── data.py              ← JSON load/save; file I/O helpers
├── validator.py         ← Input validation (dates, amounts, categories)
│
├── config/
│   └── config.json      ← Categories, currencies, savings goal, income
├── data/
│   ├── transactions.json
│   └── budget_rules.json
├── outputs/             ← Generated .txt reports
├── tests/
│   └── test_generator.py ← 120+ fake transactions with edge cases
│
├── requirements.txt
└── README.md
```

### Module responsibilities

| File | Author(s) | Key functions |
|------|-----------|--------------|
| `main.py` | Yang Andi, Mao Yicheng | `main()`, `add_transaction_flow()`, `view_transactions_flow()`, `edit_delete_flow()`, `statistics_flow()`, `alerts_flow()`, `manage_budget_rules_flow()`, `manage_categories_flow()`, `settings_flow()`, `export_flow()` |
| `display.py` | Yang Andi, Mao Yicheng | `print_transaction_table()`, `print_statistics()`, `print_top_categories()`, `print_trends()`, `print_alerts()`, `print_budget_bars()`, `print_budget_rules()`, `print_savings_goal()`, `print_heatmap()`, `print_forecast()`, `print_outliers()`, `export_report()` |
| `analytics.py` | Mao Yicheng, Yang Andi | `filter_by_date()`, `get_totals_by_category()`, `get_top_n_categories()`, `get_spending_trends()`, `get_daily_totals_by_category()`, `get_consecutive_overspend()`, `get_savings_progress()`, `linear_forecast()`, `spending_heatmap()`, `get_spending_outliers()` |
| `alerts.py` | Mao Yicheng, Yang Andi | `check_daily_caps()`, `check_percentage_thresholds()`, `check_consecutive_overspend()`, `check_forecast_alerts()`, `check_uncategorized()`, `get_all_alerts()` |
| `data.py` | Yang Andi, Yao Junzhu | `fetch_exchange_rates()`, `ensure_dirs()`, `load_transactions()`, `save_transactions()`, `load_budget_rules()`, `save_budget_rules()`, `load_config()`, `save_config()`, `get_next_id()` |
| `validator.py` | Yang Andi | `validate_date()`, `validate_amount()`, `validate_category()`, `validate_description()` |
| `tests/test_generator.py` | Wang Ziyi | `generate_transactions()`, `generate_budget_rules()`, `generate_config()`, `print_test_summary()` |

### Data schemas

**Transaction** (`data/transactions.json` — array of objects)

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-incremented unique ID |
| `date` | string | `YYYY-MM-DD` format |
| `amount` | float | Positive number in the transaction's original currency |
| `currency` | string | One of the supported currency codes (e.g. `"HKD"`, `"USD"`) |
| `category` | string | Must match a category in `config.json` |
| `description` | string | Non-empty user-entered label |

```json
{"id": 1, "date": "2026-04-01", "amount": 50.5, "currency": "HKD", "category": "Food", "description": "Lunch"}
```

**Budget rule** (`data/budget_rules.json` — array of objects, all cap fields optional)

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Category the rule applies to |
| `daily_cap` | float | Max HKD spend per day (optional) |
| `monthly_cap` | float | Max HKD spend per month (optional) |
| `pct_threshold` | int | Alert if category exceeds this % of total spending (optional) |

```json
{"category": "Food", "daily_cap": 80, "monthly_cap": 2400, "pct_threshold": 35}
```

**Config** (`config/config.json`)

| Field | Type | Description |
|-------|------|-------------|
| `categories` | list | User-editable list of valid category names |
| `currencies` | dict | Map of currency code → HKD rate (how many HKD per 1 unit) |
| `default_currency` | string | Default currency shown during transaction entry |
| `savings_goal` | float | Monthly savings target in HKD |
| `income` | float | Monthly income in HKD (used for savings progress) |

```json
{"categories": ["Food", "Transport", ...], "currencies": {"HKD": 1.0, "USD": 7.83}, "default_currency": "HKD", "savings_goal": 2000.0, "income": 12000.0}
```

### Run

```bash
pip install -r requirements.txt
python main.py

# Generate test data
python tests/test_generator.py
```

---

## 👥 Team Roles

| Role | Lead | ID |
|------|------|-----|
| **Project Lead & UI Design** | Yang Andi | 3036587092 |
| Algorithm & Logic | Mao Yicheng | 3036483040 |
| Research & Documentation | Tao Xinran | 3036525393 |
| Testing & Evaluation | Wang Ziyi | 3036484020 |
| Data Modeling & File Management | Yao Junzhu | 3036590427 |

---

## ⏱️ Timeline

- **Phase 1** (Mar 15–23): Planning & research ✅
- **Phase 2** (Mar 24–Apr 12): Architecture & implementation 🔄
- **Phase 3** (Apr 13–19): Testing & evaluation
- **Phase 4** (Apr 20–May 2): Final deliverables & reports

---

## 🎯 Tech Stack

- **Language**: Python (text-based)
- **UI**: `rich` (formatted tables, colors, panels) + `questionary` (interactive menu)
- **Data**: JSON files (transactions.json, config.json, budget_rules.json)
- **I/O**: File-based persistence via `json` module

---

## 📌 Key Deliverables

✅ Problem modeling & design justification (5+ trade-offs)  
✅ Research & tool comparison (Goodbudget, YNAB, Spendee, etc.)  
✅ Implementation: Python CLI with transaction management, analytics, alerts  
✅ 3–4 realistic case studies with sample data & evidence  
✅ Final report + individual reports + video demo

---

**Start with**: [MAIN_DOCUMENTATION.md](MAIN_DOCUMENTATION.md) for the full module reference, [prompts.md](prompts.md) for AI usage disclosure
