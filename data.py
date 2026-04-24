import json
import os
import urllib.request

DATA_DIR = "data"
CONFIG_DIR = "config"
OUTPUTS_DIR = "outputs"
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
BUDGET_RULES_FILE = os.path.join(DATA_DIR, "budget_rules.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "categories": ["Food", "Transport", "Personal", "Entertainment", "Health", "Utilities"],
    "currencies": {
        "HKD": 1.0, "CNY": 1.15, "JPY": 0.052, "KRW": 0.0057,
        "NTD": 0.24, "USD": 7.78, "GBP": 10.51, "EUR": 9.15,
    },
    "default_currency": "HKD",
    "savings_goal": 500.0,
    "income": 0.0,
}

_ISO = {"HKD": "HKD", "CNY": "CNY", "JPY": "JPY", "KRW": "KRW",
        "NTD": "TWD", "USD": "USD", "GBP": "GBP", "EUR": "EUR"}

# Fetch exchange rates from API and convert to HKD-based rates, written by Andi
def fetch_exchange_rates():
    try:
        url = "https://open.er-api.com/v6/latest/HKD"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        if data.get("result") != "success":
            return None
        api = data["rates"]
        return {
            name: round(1.0 / api[iso], 6)
            for name, iso in _ISO.items()
            if iso in api and api[iso] != 0
        }
    except Exception:
        return None


def ensure_dirs():
    for d in [DATA_DIR, CONFIG_DIR, OUTPUTS_DIR]:
        os.makedirs(d, exist_ok=True)


def _load_json(filepath, default):
    try:
        with open(filepath, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"Warning: {filepath} is corrupted. Using default.")
        return default


def _save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_transactions():
    return _load_json(TRANSACTIONS_FILE, [])


def save_transactions(transactions):
    _save_json(TRANSACTIONS_FILE, transactions)


def load_budget_rules():
    return _load_json(BUDGET_RULES_FILE, [])


def save_budget_rules(rules):
    _save_json(BUDGET_RULES_FILE, rules)


def load_config():
    config = _load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())
    for key, val in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = val
    return config


def save_config(config):
    _save_json(CONFIG_FILE, config)


def get_next_id(transactions):
    if not transactions:
        return 1
    return max(t["id"] for t in transactions) + 1
