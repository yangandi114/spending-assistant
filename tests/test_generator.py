#!/usr/bin/env python3
# Author: Wang Ziyi
# Test Data Generator for Personal Budget Assistant
# Generates 120+ realistic transactions with baked-in edge cases.

import json
import os
import random
import sys
from datetime import datetime, timedelta

# Add project root to path so imports work when run from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

random.seed(42)  # Fixed seed for reproducible test data

CATEGORIES = ["Food", "Transport", "Personal", "Entertainment", "Health", "Utilities"]

DESCRIPTIONS = {
    "Food": ["McDonald's", "KFC", "Canteen lunch", "Bubble tea", "7-Eleven",
             "Sushi", "Hotpot", "Dim sum", "Noodles", "Cake shop", "Starbucks"],
    "Transport": ["MTR fare", "Bus fare", "Taxi", "Cross-harbour tunnel",
                  "Airport Express", "Minibus", "Ferry", "Octopus top-up"],
    "Personal": ["Uniqlo shirt", "Skincare", "Haircut", "Stationery",
                 "Phone case", "Earphones", "Shoes", "Bag", "Cosmetics"],
    "Entertainment": ["Netflix", "Cinema ticket", "KTV", "Board game cafe",
                      "Steam game", "Concert ticket", "Spotify", "Disney+"],
    "Health": ["Pharmacy", "Face mask", "Vitamins", "Gym pass",
               "Doctor visit", "Dental check", "Medicine"],
    "Utilities": ["Phone bill", "Water bill", "Electricity", "Internet fee",
                  "Cloud storage", "Gas bill"],
}

AMOUNT_RANGES = {
    "Food": (15, 120),
    "Transport": (5, 55),
    "Personal": (50, 400),
    "Entertainment": (30, 600),
    "Health": (20, 250),
    "Utilities": (100, 600),
}

# Multi-currency support — 70% HKD, rest spread across other currencies
CURRENCIES = ["HKD", "CNY", "USD", "JPY", "KRW", "NTD", "GBP", "EUR"]
CURRENCY_WEIGHTS = [0.70, 0.10, 0.05, 0.05, 0.03, 0.03, 0.02, 0.02]


def rand_amount(cat):
    """Return a random realistic amount (1 decimal place) for the given category."""
    lo, hi = AMOUNT_RANGES.get(cat, (10, 100))
    return round(random.uniform(lo, hi), 1)


def rand_currency():
    """Return a weighted random currency code — mostly HKD, occasionally others."""
    return random.choices(CURRENCIES, weights=CURRENCY_WEIGHTS)[0]


def generate_transactions(n=120):
    """
    Generate n transactions covering normal spending and deliberate edge cases:
      - First 5:     Uncategorized (tests alert for unknown categories)
      - Position 50: Zero-amount refund (tests handling of 0-value entries)
      - Last 15:     Entertainment subscription spike in last 5 days
                     (tests consecutive-overspend and % threshold alerts)
      - Rest:        Random categories, descriptions, amounts, multi-currency
    Returns list sorted by date ascending.
    """
    transactions = []
    now = datetime.now()

    for i in range(n):
        # Edge case: first 5 are Uncategorized to trigger uncategorized alert
        if i < 5:
            cat = "Uncategorized"
            desc = "Miscellaneous item"
            days_ago = random.randint(0, 30)
            amount = round(random.uniform(10, 50), 1)
            currency = "HKD"

        # Edge case: last 15 are Entertainment subscriptions in the past 5 days
        # to trigger percentage-threshold and consecutive-overspend alerts
        elif i >= 105:
            cat = "Entertainment"
            desc = random.choice(["Netflix", "Spotify", "YouTube Premium",
                                  "iCloud+", "Disney+", "Apple Music"])
            days_ago = random.randint(0, 5)
            amount = round(random.uniform(80, 250), 1)
            currency = random.choice(["HKD", "USD"])

        # Normal transactions: random category, description, amount, currency
        else:
            cat = random.choice(CATEGORIES)
            desc = random.choice(DESCRIPTIONS[cat])
            days_ago = random.randint(0, 30)
            amount = rand_amount(cat)
            currency = rand_currency()

        date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        # Edge case: position 50 is a zero-amount refund/adjustment
        # (tests that the app handles 0.0 values without crashing)
        if i == 50:
            amount = 0.0
            desc = "Refund / Adjustment"
            cat = "Personal"

        transactions.append({
            "id": i + 1,
            "date": date,
            "amount": amount,
            "currency": currency,
            "category": cat,
            "description": desc,
        })

    # Sort oldest → newest so the table displays chronologically
    return sorted(transactions, key=lambda x: x["date"])


def generate_budget_rules():
    """
    Generate one budget rule per category.
    Each rule sets a daily cap, monthly cap, and percentage-of-total threshold
    that will be deliberately triggered by the generated transactions
    (Entertainment spike exceeds 25% threshold).
    """
    return [
        {"category": "Food",          "daily_cap": 80,   "monthly_cap": 2400, "pct_threshold": 35},
        {"category": "Transport",     "daily_cap": 30,   "monthly_cap": 900,  "pct_threshold": 20},
        {"category": "Entertainment", "daily_cap": 100,  "monthly_cap": 1500, "pct_threshold": 25},
        {"category": "Personal",      "daily_cap": 200,  "monthly_cap": 2000, "pct_threshold": 30},
        {"category": "Health",        "daily_cap": 150,  "monthly_cap": 1000, "pct_threshold": 15},
        {"category": "Utilities",     "daily_cap": 200,  "monthly_cap": 2000, "pct_threshold": 25},
    ]


def generate_config():
    """
    Generate app config with all categories, exchange rates, a realistic
    student monthly income (HK$12,000), and a savings goal (HK$2,000).
    """
    return {
        "categories": CATEGORIES.copy(),
        "currencies": {
            "HKD": 1.0,
            "CNY": 1.144452,
            "JPY": 0.049100,
            "KRW": 0.005275,
            "NTD": 0.247038,
            "USD": 7.830854,
            "GBP": 10.548634,
            "EUR": 9.179281,
        },
        "default_currency": "HKD",
        "savings_goal": 2000.0,
        "income": 12000.0,
    }


def print_test_summary(transactions):
    """
    Print a human-readable breakdown of generated test data:
    category counts/totals, edge case verification, and multi-currency count.
    """
    print("\n" + "=" * 60)
    print("TEST DATA SUMMARY")
    print("=" * 60)

    cat_counts = {}
    cat_amounts = {}
    for t in transactions:
        cat = t["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        cat_amounts[cat] = cat_amounts.get(cat, 0) + t["amount"]

    print("\nTransactions by category:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        total = cat_amounts[cat]
        print(f"  {cat:15s}: {count:3d} transactions, HK${total:8.2f}")

    print("\nEDGE CASES INCLUDED:")

    uncat = [t for t in transactions if t["category"] == "Uncategorized"]
    print(f"  * {len(uncat)} Uncategorized transactions (IDs: {[t['id'] for t in uncat]})")

    recent_ent = [
        t for t in transactions
        if t["category"] == "Entertainment"
        and (datetime.now() - datetime.strptime(t["date"], "%Y-%m-%d")).days <= 5
    ]
    print(f"  * {len(recent_ent)} Entertainment transactions in last 5 days (subscription creep)")

    zero_amt = [t for t in transactions if t["amount"] == 0]
    print(f"  * {len(zero_amt)} Zero-amount transactions (refunds/adjustments)")

    multi_currency = {}
    for t in transactions:
        if t["currency"] != "HKD":
            multi_currency[t["currency"]] = multi_currency.get(t["currency"], 0) + 1
    if multi_currency:
        print(f"  * Multi-currency: {multi_currency}")


def main():
    """
    Entry point: generate all test data files and write them to disk.
    Creates data/transactions.json, data/budget_rules.json, config/config.json.
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    config_dir = os.path.join(base, "config")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)

    transactions = generate_transactions(120)
    budget_rules = generate_budget_rules()
    config = generate_config()

    with open(os.path.join(data_dir, "transactions.json"), "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

    with open(os.path.join(data_dir, "budget_rules.json"), "w", encoding="utf-8") as f:
        json.dump(budget_rules, f, indent=2, ensure_ascii=False)

    with open(os.path.join(config_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(transactions)} transactions -> data/transactions.json")
    print(f"Generated {len(budget_rules)} budget rules  -> data/budget_rules.json")
    print(f"Generated config               -> config/config.json")

    print_test_summary(transactions)

    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. Run: python main.py")
    print("  2. Test: Add transaction, View, Edit, Delete")
    print("  3. Check alerts: Budget rules should trigger on Entertainment")
    print("  4. Run edge case validation (see tests/TEST_PLAN.md)")
    print("=" * 60)


if __name__ == "__main__":
    main()
