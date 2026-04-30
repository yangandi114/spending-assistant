# Module: analytics.py — Statistics & Aggregations
# Primary Authors: Mao Yicheng (get_top_n_categories, get_consecutive_overspend, linear_forecast, spending_heatmap, get_spending_outliers)
#                  Yang Andi (parse_date, filter_by_date, get_totals_by_category, get_daily_totals_by_category, get_spending_trends, get_savings_progress)

import calendar
from collections import defaultdict
from datetime import datetime, timedelta


# By Yang Andi: Turn a YYYY-MM-DD string into a datetime.
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


# By Yang Andi: Keep only transactions in the given date range.
def filter_by_date(transactions, start=None, end=None):
    result = []
    for t in transactions:
        d = parse_date(t["date"])
        if start and d < start:
            continue
        if end and d > end:
            continue
        result.append(t)
    return result


# By Yang Andi: Total up spending per category (optional date filter).
def get_totals_by_category(transactions, start=None, end=None):
    filtered = filter_by_date(transactions, start, end)
    totals = defaultdict(float)
    for t in filtered:
        totals[t["category"]] += t["amount"]
    return dict(totals)


# By Mao Yicheng: Get the top N categories by spending, with % share.
def get_top_n_categories(transactions, n=3, start=None, end=None):
    totals = get_totals_by_category(transactions, start, end)
    total = sum(totals.values())
    sorted_cats = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return [
        (cat, amt, (amt / total * 100) if total > 0 else 0)
        for cat, amt in sorted_cats[:n]
    ]


# By Yang Andi: Compare 7-day vs 30-day daily averages.
def get_spending_trends(transactions):
    now = datetime.now()
    last_7 = filter_by_date(transactions, now - timedelta(days=7), now)
    last_30 = filter_by_date(transactions, now - timedelta(days=30), now)
    avg_7 = sum(t["amount"] for t in last_7) / 7 if last_7 else 0
    avg_30 = sum(t["amount"] for t in last_30) / 30 if last_30 else 0
    return avg_7, avg_30


# By Yang Andi: Daily totals for one category.
def get_daily_totals_by_category(transactions, category):
    daily = defaultdict(float)
    for t in transactions:
        if t["category"] == category:
            daily[t["date"]] += t["amount"]
    return dict(daily)


# By Mao Yicheng: Count consecutive over-cap days for a category (starting from the most recent).
def get_consecutive_overspend(transactions, category, daily_cap):
    daily = get_daily_totals_by_category(transactions, category)
    sorted_dates = sorted(daily.keys(), reverse=True)
    streak = 0
    for date_str in sorted_dates:
        if daily[date_str] > daily_cap:
            streak += 1
        else:
            break
    return streak


# By Yang Andi: This month's spending + how much is left toward the savings goal.
def get_savings_progress(transactions, savings_goal, income):
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    monthly = filter_by_date(transactions, start, now)
    spent = sum(t["amount"] for t in monthly)
    remaining = income - spent
    savings = remaining - savings_goal
    return spent, remaining, savings


# By Mao Yicheng: Guess this month's total by extrapolating from the daily average so far.
def linear_forecast(transactions):
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    monthly = filter_by_date(transactions, start, now)
    if not monthly:
        return 0.0
    days_elapsed = (now - start).days + 1
    spent = sum(t["amount"] for t in monthly)
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    return (spent / days_elapsed) * days_in_month


# By Mao Yicheng: Build heatmap symbols per day by comparing to the monthly average.
def spending_heatmap(transactions):
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    monthly = filter_by_date(transactions, start, now)

    daily = defaultdict(float)
    for t in monthly:
        daily[t["date"]] += t["amount"]

    if not daily:
        return {}

    avg = sum(daily.values()) / len(daily)
    result = {}
    for date_str, amt in daily.items():
        ratio = amt / avg if avg > 0 else 0
        if ratio < 0.5:
            sym = "░"
        elif ratio < 1.0:
            sym = "▒"
        elif ratio < 1.5:
            sym = "▓"
        else:
            sym = "█"
        result[date_str] = (sym, amt)
    return result


# By Mao Yicheng: Grab the top X% biggest transactions (default 5%).
def get_spending_outliers(transactions, top_percent=0.05):
    if not transactions:
        return []
    ordered = sorted(transactions, key=lambda x: x["amount"], reverse=True)
    count = max(1, int(len(ordered) * top_percent))
    return ordered[:count]
