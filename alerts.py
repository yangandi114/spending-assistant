# Authors: Mao Yicheng, Yang Andi

from datetime import datetime
from analytics import (
    get_daily_totals_by_category,
    get_totals_by_category,
    get_consecutive_overspend,
    linear_forecast,
)


def check_daily_caps(transactions, budget_rules):
    """Check if daily spending in any category exceeds the user-defined cap."""
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


def check_percentage_thresholds(transactions, budget_rules):
    """Identify categories that consume a larger share of total spending than allowed."""
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


def check_consecutive_overspend(transactions, budget_rules):
    """Track and alert if a user exceeds the budget for several consecutive days."""
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


def check_forecast_alerts(transactions, budget_rules):
    """
    Predict end-of-month spending and alert if the trend exceeds the budget.
    Provides a proactive warning rather than a reactive one.
    """
    projected_total = linear_forecast(transactions)
    monthly_limit = 5000
    alerts = []
    if projected_total > monthly_limit:
        alerts.append({
            "type": "forecast_warning",
            "message": f"Trend Alert: Projected monthly spend (HK${projected_total:.2f}) exceeds budget!",
        })
    return alerts


def check_uncategorized(transactions, categories):
    """Audit transactions to ensure every record belongs to a valid category."""
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


def get_all_alerts(transactions, budget_rules, categories):
    """Aggregate all types of alerts into a single list for the display module."""
    alerts = []
    alerts += check_daily_caps(transactions, budget_rules)
    alerts += check_percentage_thresholds(transactions, budget_rules)
    alerts += check_consecutive_overspend(transactions, budget_rules)
    alerts += check_forecast_alerts(transactions, budget_rules)
    alerts += check_uncategorized(transactions, categories)
    return alerts
