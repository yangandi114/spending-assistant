# Module: data.py — File I/O, Config & Data Persistence
# Primary Author: Yao Junzhu (all core I/O, config management)
# Secondary Author: Yang Andi (fetch_exchange_rates function)
import json
import os
import urllib.request

# ── directory and file paths ──

DATA_DIR = "data"
CONFIG_DIR = "config"
OUTPUTS_DIR = "outputs"

# build full file paths by joining directory name and file name
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
BUDGET_RULES_FILE = os.path.join(DATA_DIR, "budget_rules.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# ── default configuration ──

DEFAULT_CONFIG = {
    "categories": ["Food", "Transport", "Personal", "Entertainment", "Health", "Utilities"],
    "currencies": {
        "HKD": 1.0,
        "CNY": 1.15,
        "JPY": 0.052,
        "KRW": 0.0057,
        "NTD": 0.24,
        "USD": 7.78,
        "GBP": 10.51,
        "EUR": 9.15,
    },
    "default_currency": "HKD",
    "savings_goal": 500.0,
    "income": 0.0,
}

# ── ISO currency code mapping ──

# "NTD" is a common nickname; the official ISO code is "TWD"
_ISO = {
    "HKD": "HKD",
    "CNY": "CNY",
    "JPY": "JPY",
    "KRW": "KRW",
    "NTD": "TWD",
    "USD": "USD",
    "GBP": "GBP",
    "EUR": "EUR",
}


def fetch_exchange_rates():
    """
    Fetch live exchange rates from a free API.
    Returns a dict like {"HKD": 1.0, "USD": 7.78, ...} or None on failure.
    The API gives rates relative to HKD (e.g. 1 HKD = 0.1277 USD),
    so we invert them to get "how many HKD per 1 unit of that currency".
    """
    try:
        url = "https://open.er-api.com/v6/latest/HKD"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        if data.get("result") != "success":
            return None
        api = data["rates"]
        # invert: API gives HKD->X, we want X->HKD
        return {
            name: round(1.0 / api[iso], 6)
            for name, iso in _ISO.items()
            if iso in api and api[iso] != 0
        }
    except Exception:
        # any network error, timeout, or parsing failure -> return None
        return None


def ensure_dirs():
    """Create the required directories if they do not already exist."""
    for d in [DATA_DIR, CONFIG_DIR, OUTPUTS_DIR]:
        os.makedirs(d, exist_ok=True)  # exist_ok=True means no error if already exists


def _load_json(filepath, default):
    """
    Read a JSON file and return its content as a Python object.
    If the file is missing, empty, or corrupted, return the default value.
    """
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
    """Write a Python object to a file as formatted JSON."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_transactions():
    """Load the transactions list from disk. Returns [] if no file exists."""
    return _load_json(TRANSACTIONS_FILE, [])


def save_transactions(transactions):
    """Save the transactions list to disk."""
    _save_json(TRANSACTIONS_FILE, transactions)


def load_budget_rules():
    """Load the budget rules list from disk. Returns [] if no file exists."""
    return _load_json(BUDGET_RULES_FILE, [])


def save_budget_rules(rules):
    """Save the budget rules list to disk."""
    _save_json(BUDGET_RULES_FILE, rules)


def load_config():
    """
    Load app configuration from disk.
    If some keys are missing from the file, fill them in from DEFAULT_CONFIG.
    """
    config = _load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())
    for key, val in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = val
    return config


def save_config(config):
    """Save app configuration to disk."""
    _save_json(CONFIG_FILE, config)


def get_next_id(transactions):
    """
    Return the next available transaction ID.
    Starts from 1 if the list is empty; otherwise max existing ID + 1.
    """
    if not transactions:
        return 1
    return max(t["id"] for t in transactions) + 1
