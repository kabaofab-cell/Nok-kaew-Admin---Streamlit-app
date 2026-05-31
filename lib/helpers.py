"""Utility functions for Nok-kaew Admin."""

import pandas as pd


def format_currency(amount):
    """Format number as Thai currency string."""
    try:
        return f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def to_num(val):
    """Convert a value to float, returning 0.0 on failure."""
    try:
        return float(str(val).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


def num_series(series):
    """Convert a Series to numeric, coercing errors to 0."""
    return pd.to_numeric(series.astype(str).str.replace(",", ""), errors="coerce").fillna(0)


def add_month_column(df, date_col):
    """Add _date and _month columns parsed from date_col."""
    df = df.copy()
    df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
    df["_month"] = df["_date"].dt.strftime("%Y-%m")
    return df


def month_options(df, date_col):
    """Return sorted list of unique YYYY-MM strings from date_col, newest first."""
    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    months = sorted(dates.dt.strftime("%Y-%m").unique(), reverse=True)
    return list(months)


def thai_month_label(ym_str):
    """Convert YYYY-MM to Thai month label like 'พ.ค. 2568'."""
    thai_months = [
        "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
        "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
    ]
    try:
        year, month = ym_str.split("-")
        thai_year = int(year) + 543
        return f"{thai_months[int(month) - 1]} {thai_year}"
    except Exception:
        return ym_str


def get_settings_dict(settings_data):
    """Convert settings list-of-lists to dictionary."""
    result = {}
    if not settings_data:
        return result
    for row in settings_data:
        if len(row) >= 2:
            result[row[0]] = row[1]
    return result


def validate_split(user1_split, user2_split):
    """Validate that splits add to 100%."""
    total = user1_split + user2_split
    return total == 100, total
