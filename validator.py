# Author: Yang Andi

from datetime import datetime


def validate_date(date_str):
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_amount(amount_str):
    if not amount_str:
        return False, 0.0
    try:
        amount = float(amount_str)
        return amount > 0, amount
    except ValueError:
        return False, 0.0


def validate_category(category, categories):
    return category in categories


def validate_description(desc):
    return bool(desc and desc.strip())
