# Authors: Yang Andi, Mao Yicheng

import questionary
from questionary import Separator, Style

from alerts import get_all_alerts
from analytics import filter_by_date
from data import (
    ensure_dirs,
    fetch_exchange_rates,
    get_next_id,
    load_budget_rules,
    load_config,
    load_transactions,
    save_budget_rules,
    save_config,
    save_transactions,
)
from datetime import datetime
from display import (
    console,
    export_report,
    print_alerts,
    print_budget_bars,
    print_budget_rules,
    print_forecast,
    print_header,
    print_heatmap,
    print_outliers,
    print_savings_goal,
    print_statistics,
    print_top_categories,
    print_transaction_table,
    print_trends,
)
from validator import validate_amount, validate_date, validate_description

STYLE = Style([
    ("pointer",     "fg:#00ff88 bold"),
    ("highlighted", "fg:#00ff88 bold"),
    ("question",    "bold"),
    ("answer",      "fg:#00ff88 bold"),
    ("separator",   "fg:#555555 italic"),
])

BACK = "↩   Back"

def _sep(label=""):
    # Returns a styled questionary Separator for menu visual grouping.
    return Separator(f"  {'─' * 2} {label} " if label else f"  {'─' * 44}")


def ask(prompt, default=""):
    # Prompts user for text input; raises KeyboardInterrupt if cancelled.
    result = questionary.text(prompt, default=default, style=STYLE).ask()
    if result is None:
        raise KeyboardInterrupt
    return result


def choose(prompt, choices):
    # Prompts user to select from a list; raises KeyboardInterrupt if cancelled.
    result = questionary.select(prompt, choices=choices, style=STYLE, pointer="❯").ask()
    if result is None:
        raise KeyboardInterrupt
    return result


def confirm(prompt, default=False):
    # Prompts user for yes/no confirmation; raises KeyboardInterrupt if cancelled.
    result = questionary.confirm(prompt, default=default, style=STYLE).ask()
    if result is None:
        raise KeyboardInterrupt
    return result


def pause():
    # Waits for any keypress before continuing.
    questionary.press_any_key_to_continue(style=STYLE).ask()


def get_valid_date(prompt, default=None):
    # Repeatedly asks for a date until valid format is provided.
    if default is None:
        default = datetime.now().strftime("%Y-%m-%d")
    while True:
        date_str = ask(prompt, default=default)
        if validate_date(date_str):
            return date_str
        console.print("[red]Invalid date. Use YYYY-MM-DD.[/red]")


def get_valid_amount(prompt):
    # Repeatedly asks for an amount until valid number is provided.
    while True:
        amount_str = ask(prompt)
        valid, amount = validate_amount(amount_str)
        if valid:
            return amount
        console.print("[red]Must be a positive number.[/red]")


def get_valid_percentage(prompt):
    # Repeatedly asks for a percentage (0-100) until valid.
    while True:
        val = ask(prompt)
        try:
            pct = float(val)
            if 0 < pct <= 100:
                return pct
            console.print("[red]Must be 1–100.[/red]")
        except ValueError:
            console.print("[red]Invalid.[/red]")


def get_valid_description(prompt):
    # Repeatedly asks for a description until non-empty.
    while True:
        desc = ask(prompt)
        if validate_description(desc):
            return desc.strip()
        console.print("[red]Description cannot be empty.[/red]")


def find_transaction_by_id(transactions, txn_id):
    # Finds a transaction by ID, returns None if not found.
    for txn in transactions:
        if txn["id"] == txn_id:
            return txn
    return None


def show_hkd_conversion(amount, currency, config):
    # Shows HKD equivalent if currency is not default.
    if currency != config["default_currency"]:
        rate = config["currencies"][currency]
        console.print(f"[dim]≈ HK${amount * rate:.2f}[/dim]")


def add_transaction_flow():
    # Guides user through adding a new transaction and checks budget alerts.
    config = load_config()
    transactions = load_transactions()
    console.print("\n[bold cyan]➕  Add Transaction[/bold cyan]")

    date_str = get_valid_date("Date (YYYY-MM-DD):")
    amount = get_valid_amount("Amount:")
    currency = choose("Currency:", list(config["currencies"].keys()))
    show_hkd_conversion(amount, currency, config)
    category = choose("Category:", config["categories"] + ["Uncategorized"])
    description = get_valid_description("Description:")

    txn = {
        "id": get_next_id(transactions),
        "date": date_str,
        "amount": amount,
        "currency": currency,
        "category": category,
        "description": description,
    }
    transactions.append(txn)
    save_transactions(transactions)
    console.print(f"\n[green]✅  Transaction #{txn['id']} added.[/green]")

    budget_rules = load_budget_rules()
    alerts = get_all_alerts(transactions, budget_rules, config["categories"])
    triggered = [a for a in alerts if a["type"] != "uncategorized"]
    if triggered:
        print_alerts(triggered)
    print_budget_bars(transactions, budget_rules)


def view_transactions_flow():
    # Lets user browse, filter, or search existing transactions.
    transactions = load_transactions()
    config = load_config()
    mode = choose("View mode:", [
        _sep("Browse"),
        "All Transactions",
        _sep("Filter"),
        "Filter by Date Range",
        "Filter by Category",
        "Search by Keyword",
        _sep(),
        BACK,
    ])
    if mode == BACK:
        return

    if mode == "All Transactions":
        print_transaction_table(transactions)

    elif mode == "Filter by Date Range":
        start_str = get_valid_date("Start date (YYYY-MM-DD):")
        end_str = get_valid_date("End date (YYYY-MM-DD):")
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
        filtered = filter_by_date(transactions, start, end)
        print_transaction_table(filtered, f"Transactions {start_str} → {end_str}")

    elif mode == "Filter by Category":
        category = choose("Category:", config["categories"])
        filtered = [t for t in transactions if t["category"] == category]
        print_transaction_table(filtered, f"{category} Transactions")

    elif mode == "Search by Keyword":
        keyword = ask("Keyword:")
        filtered = [t for t in transactions if keyword.lower() in t["description"].lower()]
        print_transaction_table(filtered, f'Results for "{keyword}"')


def select_transaction_by_id(transactions):
    # Prompts user to select a transaction by ID. Returns (txn, txn_id) or (None, None).
    while True:
        user_input = ask("Transaction ID to edit/delete (or 'q' to cancel):")
        if user_input.lower() == "q":
            return None, None
        try:
            txn_id = int(user_input)
            txn = find_transaction_by_id(transactions, txn_id)
            if txn:
                return txn, txn_id
            console.print(f"[red]ID {txn_id} not found.[/red]")
        except ValueError:
            console.print("[red]Enter a valid number.[/red]")


def edit_transaction_field(txn, field, config):
    # Edits a single field of a transaction. Returns True if edited, False if cancelled.
    if field == "Date":
        val = get_valid_date(f"New date (current: {txn['date']}):")
        txn["date"] = val
    elif field == "Amount":
        val = get_valid_amount(f"New amount (current: {txn['amount']}):")
        txn["amount"] = val
    elif field == "Currency":
        txn["currency"] = choose("Currency:", list(config["currencies"].keys()))
    elif field == "Category":
        txn["category"] = choose("Category:", config["categories"])
    elif field == "Description":
        val = get_valid_description(f"New description (current: {txn['description']}):")
        txn["description"] = val
    return True


def edit_delete_flow():
    # Lets user select a transaction by ID and edit a field or delete it.
    transactions = load_transactions()
    if not transactions:
        console.print("[dim]No transactions.[/dim]")
        return
    print_transaction_table(transactions)

    txn, txn_id = select_transaction_by_id(transactions)
    if txn is None:
        return

    action = choose(f"Action for #{txn_id}:", [
        "Edit Field",
        "Delete Transaction",
        _sep(),
        "Cancel",
    ])
    if action == "Cancel":
        return

    if action == "Delete Transaction":
        if confirm(f"Delete transaction #{txn_id}?"):
            transactions = [t for t in transactions if t["id"] != txn_id]
            save_transactions(transactions)
            console.print("[green]✅  Deleted.[/green]")

    elif action == "Edit Field":
        config = load_config()
        field = choose("Field to edit:", [
            "Date", "Amount", "Currency", "Category", "Description",
            _sep(),
            "Cancel",
        ])
        if field == "Cancel":
            return
        edit_transaction_field(txn, field, config)
        save_transactions(transactions)
        console.print("[green]✅  Updated.[/green]")


def statistics_flow():
    # Shows analytics sub-menu: totals, trends, forecast, heatmap, etc.
    transactions = load_transactions()
    budget_rules = load_budget_rules()
    action = choose("Statistics:", [
        _sep("Overview"),
        "Category Totals — Current Month",
        "Category Totals — All Time",
        "Top 3 Categories",
        "Major Expenses (Top 5%)",
        _sep("Trends & Forecast"),
        "Spending Trends (7d vs 30d)",
        "Spending Forecast",
        _sep("Visuals"),
        "Budget Progress Bars",
        "Spending Heatmap",
        _sep(),
        BACK,
    ])
    if action == BACK:
        return
    if action == "Category Totals — Current Month":
        now = datetime.now()
        filtered = filter_by_date(transactions, datetime(now.year, now.month, 1), now)
        print_statistics(filtered, now.strftime("%B %Y"))
    elif action == "Category Totals — All Time":
        print_statistics(transactions)
    elif action == "Top 3 Categories":
        print_top_categories(transactions)
    elif action == "Major Expenses (Top 5%)":
        print_outliers(transactions)
    elif action == "Spending Trends (7d vs 30d)":
        print_trends(transactions)
    elif action == "Budget Progress Bars":
        print_budget_bars(transactions, budget_rules)
    elif action == "Spending Forecast":
        print_forecast(transactions)
    elif action == "Spending Heatmap":
        print_heatmap(transactions)


def alerts_flow():
    # Loads and displays all active budget alerts.
    transactions = load_transactions()
    budget_rules = load_budget_rules()
    config = load_config()
    alerts = get_all_alerts(transactions, budget_rules, config["categories"])
    print_alerts(alerts)


def add_or_update_budget_rule(budget_rules, config):
    # Prompts user to create or update a budget rule for a category.
    category = choose("Category:", config["categories"])
    rule = {"category": category}

    if confirm("Set daily cap?"):
        amt = get_valid_amount("Daily cap (HKD):")
        rule["daily_cap"] = amt

    if confirm("Set monthly cap?"):
        amt = get_valid_amount("Monthly cap (HKD):")
        rule["monthly_cap"] = amt

    if confirm("Set % threshold?"):
        pct = get_valid_percentage("Max % of total spending (0–100):")
        rule["pct_threshold"] = pct

    existing_index = None
    for i, r in enumerate(budget_rules):
        if r["category"] == category:
            existing_index = i
            break

    if existing_index is not None:
        budget_rules[existing_index] = rule
    else:
        budget_rules.append(rule)

    save_budget_rules(budget_rules)
    console.print("[green]✅  Rule saved.[/green]")


def manage_budget_rules_flow():
    # Lets user view, add/update, or delete per-category budget rules.
    budget_rules = load_budget_rules()
    config = load_config()
    action = choose("Budget Rules:", [
        "View Rules",
        "Add / Update Rule",
        "Delete Rule",
        _sep(),
        BACK,
    ])
    if action == BACK:
        return

    if action == "View Rules":
        print_budget_rules(budget_rules)

    elif action == "Add / Update Rule":
        add_or_update_budget_rule(budget_rules, config)

    elif action == "Delete Rule":
        if not budget_rules:
            console.print("[dim]No rules to delete.[/dim]")
            return
        categories = [r["category"] for r in budget_rules]
        cat = choose("Delete rule for:", categories)
        if confirm(f"Delete rule for '{cat}'?"):
            new_rules = [r for r in budget_rules if r["category"] != cat]
            save_budget_rules(new_rules)
            console.print("[green]✅  Deleted.[/green]")


def view_categories(config):
    # Displays all spending categories.
    console.print("[bold]Categories:[/bold]")
    for category in config["categories"]:
        console.print(f"  • {category}")


def add_category(config):
    # Prompts user to add a new category.
    name = ask("New category name:").strip()
    if not name:
        return
    if name in config["categories"]:
        console.print("[yellow]Already exists.[/yellow]")
        return
    config["categories"].append(name)
    save_config(config)
    console.print(f"[green]✅  Added '{name}'.[/green]")


def remove_category(config):
    # Prompts user to remove a category.
    if not config["categories"]:
        console.print("[dim]No categories.[/dim]")
        return
    category = choose("Remove:", config["categories"])
    if confirm(f"Remove '{category}'?"):
        config["categories"].remove(category)
        save_config(config)
        console.print(f"[green]✅  Removed '{category}'.[/green]")


def manage_categories_flow():
    # Lets user view, add, or remove spending categories.
    config = load_config()
    action = choose("Categories:", [
        "View",
        "Add",
        "Remove",
        _sep(),
        BACK,
    ])
    if action == BACK:
        return

    if action == "View":
        view_categories(config)
    elif action == "Add":
        add_category(config)
    elif action == "Remove":
        remove_category(config)


def set_income(config):
    # Prompts user to set monthly income and saves it.
    current_income = config.get("income", 0)
    prompt = f"Monthly income in HKD (current: HK${current_income:.2f}):"
    amt = get_valid_amount(prompt)
    config["income"] = amt
    save_config(config)
    console.print("[green]✅  Saved.[/green]")


def set_savings_goal(config):
    # Prompts user to set monthly savings goal and saves it.
    current_goal = config.get("savings_goal", 0)
    prompt = f"Monthly savings goal in HKD (current: HK${current_goal:.2f}):"
    amt = get_valid_amount(prompt)
    config["savings_goal"] = amt
    save_config(config)
    console.print("[green]✅  Saved.[/green]")


def update_exchange_rate(config):
    # Prompts user to update a currency exchange rate.
    console.print("[bold]Current rates (1 unit → HKD):[/bold]")
    for cur, rate in config["currencies"].items():
        console.print(f"  {cur}: {rate}")
    if not confirm("Update a rate?"):
        return
    currency = choose("Currency:", list(config["currencies"].keys()))
    while True:
        val = ask(f"1 {currency} = ? HKD:")
        try:
            rate = float(val)
            if rate > 0:
                config["currencies"][currency] = rate
                save_config(config)
                console.print("[green]✅  Updated.[/green]")
                break
            console.print("[red]Must be positive.[/red]")
        except ValueError:
            console.print("[red]Invalid.[/red]")


def settings_flow():
    # Lets user set income, savings goal, and update currency exchange rates.
    config = load_config()
    action = choose("Settings:", [
        _sep("Income & Goals"),
        "Set Monthly Income",
        "Set Savings Goal",
        "View Savings Progress",
        _sep("Currencies"),
        "Currency Exchange Rates",
        _sep(),
        BACK,
    ])
    if action == BACK:
        return

    if action == "Set Monthly Income":
        set_income(config)

    elif action == "Set Savings Goal":
        set_savings_goal(config)

    elif action == "View Savings Progress":
        print_savings_goal(load_transactions(), config)

    elif action == "Currency Exchange Rates":
        update_exchange_rate(config)


def export_flow():
    # Exports a full summary report to a text file in outputs/.
    transactions = load_transactions()
    budget_rules = load_budget_rules()
    config = load_config()
    filename = export_report(transactions, budget_rules, config["categories"], config)
    console.print(f"\n[green]✅  Report saved → [bold]{filename}[/bold][/green]")


HANDLERS = {
    "➕   Add Transaction":            add_transaction_flow,
    "📋   View / Filter Transactions":  view_transactions_flow,
    "✏️    Edit / Delete Transaction":   edit_delete_flow,
    "📊   Statistics & Analytics":      statistics_flow,
    "⚠️    Check Budget Alerts":         alerts_flow,
    "💰   Budget Rules":                manage_budget_rules_flow,
    "🏷️    Manage Categories":           manage_categories_flow,
    "⚙️    Settings":                    settings_flow,
    "📄   Export Summary Report":       export_flow,
    "🚪   Exit":                         None,
}

MAIN_MENU = [
    _sep("Transactions"),
    "➕   Add Transaction",
    "📋   View / Filter Transactions",
    "✏️    Edit / Delete Transaction",
    _sep("Analytics"),
    "📊   Statistics & Analytics",
    "⚠️    Check Budget Alerts",
    _sep("Management"),
    "💰   Budget Rules",
    "🏷️    Manage Categories",
    "⚙️    Settings",
    _sep(),
    "📄   Export Summary Report",
    "🚪   Exit",
]


def main():
    # Entry point: initialises dirs, fetches live rates, runs the main menu loop.
    ensure_dirs()
    console.print("[dim]Fetching live exchange rates...[/dim] ", end="")
    rates = fetch_exchange_rates()
    if rates:
        cfg = load_config()
        cfg["currencies"] = rates
        save_config(cfg)
        console.print("[green]✓[/green]")
    else:
        console.print("[yellow]offline — using cached rates[/yellow]")

    try:
        while True:
            console.clear()
            print_header()
            choice = questionary.select("", choices=MAIN_MENU, style=STYLE, pointer="❯").ask()
            if choice is None or choice == "🚪   Exit":
                console.print("\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
                break
            console.print()
            HANDLERS[choice]()
            console.print()
            pause()
    except KeyboardInterrupt:
        console.print("\n[bold cyan]Goodbye! 👋[/bold cyan]\n")


if __name__ == "__main__":
    main()
