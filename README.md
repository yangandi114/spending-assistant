# COMP1110 B12 — Personal Budget & Spending Assistant

**Project**: Personal Budget & Spending Assistant (Topic A)  
**Members**: Mao Yicheng, Tao Xinran, Wang Ziyi, Yang Andi, Yao Junzhu  

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [DOCUMENTATION.md](DOCUMENTATION.md) | Documentation |
| [PLAN.md](PLAN.md) | Timeline, research, roles |
| [FEATURES.md](FEATURES.md) | Feature list |
| [UI.md](UI.md) | UI design |

## 🗂️ Project Structure

```
comp1110projectlocal/
├── main.py              ← Entry point; questionary menu loop, live FX fetch on startup
├── display.py           ← All rich rendering (tables, panels, alerts, heatmap)
├── analytics.py         ← Statistics, trends, forecasting, heatmap, outliers
├── alerts.py            ← Alert logic (caps, thresholds, streaks, forecast)
├── data.py              ← JSON load/save, live exchange rate fetch (urllib)
├── validator.py         ← Input validation (dates, amounts, categories)
│
├── config/
│   └── config.json      ← Categories, currencies, savings goal, income
├── data/
│   ├── transactions.json
│   └── budget_rules.json
├── outputs/             ← Generated .txt reports
├── tests/
│   └── test_generator.py ← 120+ fake transactions with edge cases (Wang Ziyi)
│
├── requirements.txt
├── prompts.md            ← AI prompt log (per assignment requirement)
├── MAIN_DOCUMENTATION.md ← Full design documentation
└── README.md
```

### Module responsibilities

| File | Key functions |
|------|--------------|
| `main.py` | `main()`, `add_transaction_flow()`, `view_transactions_flow()`, `edit_delete_flow()`, `statistics_flow()`, `alerts_flow()`, `manage_budget_rules_flow()`, `manage_categories_flow()`, `settings_flow()`, `export_flow()` + helpers (`ask`, `choose`, `confirm`, `pause`, `get_valid_date`, `get_valid_amount`, `get_valid_percentage`, `get_valid_description`) |
| `display.py` | `print_header()`, `print_transaction_table()`, `print_statistics()`, `print_top_categories()`, `print_trends()`, `print_alerts()`, `print_budget_bars()`, `print_budget_rules()`, `print_savings_goal()`, `print_heatmap()`, `print_forecast()`, `print_outliers()`, `export_report()` |
| `analytics.py` | `parse_date()`, `filter_by_date()`, `get_totals_by_category()`, `get_top_n_categories()`, `get_spending_trends()`, `get_daily_totals_by_category()`, `get_consecutive_overspend()`, `get_savings_progress()`, `linear_forecast()`, `spending_heatmap()`, `get_spending_outliers()` |
| `alerts.py` | `check_daily_caps()`, `check_percentage_thresholds()`, `check_consecutive_overspend()`, `check_forecast_alerts()`, `check_uncategorized()`, `get_all_alerts()` |
| `data.py` | `fetch_exchange_rates()`, `ensure_dirs()`, `load_transactions()`, `save_transactions()`, `load_budget_rules()`, `save_budget_rules()`, `load_config()`, `save_config()`, `get_next_id()` |
| `validator.py` | `validate_date()`, `validate_amount()`, `validate_category()`, `validate_description()` |

### Data schemas

**Transaction**
```json
{"id": 1, "date": "2026-04-01", "amount": 50.5, "currency": "HKD", "category": "Food", "description": "Lunch"}
```

**Budget rule**
```json
{"category": "Food", "daily_cap": 80, "monthly_cap": 2400, "pct_threshold": 35}
```

**Config**
```json
{"categories": [...], "currencies": {"HKD": 1.0, "USD": 7.78}, "default_currency": "HKD", "savings_goal": 500, "income": 0}
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

## Timeline

- **Phase 1** (Mar 15–23): Planning & research ✅
- **Phase 2** (Mar 24–Apr 12): Architecture & implementation ✅
- **Phase 3** (Apr 13–19): Testing & evaluation ✅
- **Phase 4** (Apr 20–May 2): Final deliverables & reports 🔄

---

## Tech Stack

- **Language**: Python 3.x (text-based CLI)
- **UI**: `rich` (formatted tables, colors, panels, heatmap) + `questionary` (interactive menus, arrow-key selection)
- **Data**: JSON files (transactions.json, config.json, budget_rules.json)
- **I/O**: File-based persistence via stdlib `json`
- **Live FX**: stdlib `urllib.request` → `open.er-api.com` (8 currencies, falls back to cached rates if offline or error)

---
