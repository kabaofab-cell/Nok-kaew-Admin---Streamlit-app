"""Utility functions for Nok-kaew Admin."""

from datetime import datetime
import streamlit as st


def format_currency(amount):
    """Format number as Thai currency."""
    if amount is None:
        return "0.00"
    return f"{float(amount):,.2f}"


def format_date(date_obj):
    """Format date for display."""
    if not date_obj:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%d/%m/%Y")


def parse_date(date_str):
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None


def get_settings_dict(settings_data):
    """Convert settings array to dictionary."""
    result = {}
    for row in settings_data:
        if len(row) >= 2:
            result[row[0]] = row[1]
    return result


def validate_split(user1_split, user2_split):
    """Validate that splits equal 100%."""
    total = user1_split + user2_split
    return total == 100, total
