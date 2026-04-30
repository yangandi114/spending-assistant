# Module: alerts.py — Budget Rule Checking
# Primary Authors: Mao Yicheng (check_daily_caps, check_percentage_thresholds, check_consecutive_overspend)
#                  Yang Andi (check_forecast_alerts, check_uncategorized, get_all_alerts)

from datetime import datetime
from analytics import (
    get_daily_totals_by_category,
    get_totals_by_category,
    get_consecutive_overspend,
    linear_forecast,
)


# By Mao Yicheng: Check if today's spending in any category went over the daily cap.
def check_daily_caps(transactions, budget_rules):
    today = datetime.now().strftime("%Y-%m-%d")
    alerts = []
    for rule in budget_rules:
        cap = rule.get("daily_cap")
        if cap is None:
            continue
        cat = rule["category"]
        daily = get_daily_totals_by_category(transactions, cat)
        today_total = daily.get(today, 0)
        if today_total > cap:
            alerts.append({
                "type": "daily_exceeded",
                "category": cat,
                "spent": today_total,
                "cap": cap,
                "message": f"{cat}: Daily limit exceeded! (HK${today_total:.2f} / HK${cap:.2f})",
            })
    return alerts


# By Mao Yicheng: Flag categories that take up too much of the total spending.
def check_percentage_thresholds(transactions, budget_rules):
    totals = get_totals_by_category(transactions)
    total = sum(totals.values())
    alerts = []
    if total == 0:
        return alerts
    for rule in budget_rules:
        threshold = rule.get("pct_threshold")
        if threshold is None:
            continue
        cat = rule["category"]
        pct = (totals.get(cat, 0) / total * 100)
        if pct > threshold:
            alerts.append({
                "type": "pct_exceeded",
                "category": cat,
                "pct": pct,
                "threshold": threshold,
                "message": f"{cat}: {pct:.1f}% of total (limit: {threshold}%)",
            })
    return alerts


# By Mao Yicheng: Warn if a category has been over-budget for 3+ days in a row.
def check_consecutive_overspend(transactions, budget_rules):
    alerts = []
    for rule in budget_rules:
        cap = rule.get("daily_cap")
        if cap is None:
            continue
        cat = rule["category"]
        streak = get_consecutive_overspend(transactions, cat, cap)
        if streak >= 3:
            alerts.append({
                "type": "consecutive_overspend",
                "category": cat,
                "streak": streak,
                "message": f"{cat}: Budget exceeded for {streak} consecutive days!",
            })
    return alerts


# By Yang Andi: Project this month's total spend and warn early if we're heading over budget.
def check_forecast_alerts(transactions, budget_rules):
    monthly_limit = sum(r["monthly_cap"] for r in budget_rules if "monthly_cap" in r)
    if monthly_limit <= 0:
        return []
    projected_total = linear_forecast(transactions)
    alerts = []
    if projected_total > monthly_limit:
        alerts.append({
            "type": "forecast_warning",
            "message": f"Trend Alert: Projected monthly spend (HK${projected_total:.2f}) exceeds budget!",
        })
    return alerts


# By Yang Andi: Find transactions with missing or unknown categories.
def check_uncategorized(transactions, categories):
    alerts = []
    for t in transactions:
        cat = t.get("category", "Uncategorized")
        if cat == "Uncategorized" or cat not in categories:
            alerts.append({
                "type": "uncategorized",
                "id": t["id"],
                "category": cat,
                "message": f"Transaction #{t['id']} has invalid/unknown category: '{cat}'",
            })
    return alerts


# By Yang Andi: Collect all alerts into one list for display.
def get_all_alerts(transactions, budget_rules, categories):
    alerts = []
    alerts += check_daily_caps(transactions, budget_rules)
    alerts += check_percentage_thresholds(transactions, budget_rules)
    alerts += check_consecutive_overspend(transactions, budget_rules)
    alerts += check_forecast_alerts(transactions, budget_rules)
    alerts += check_uncategorized(transactions, categories)
    return alerts
