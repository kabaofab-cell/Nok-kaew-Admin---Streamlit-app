"""Google Sheets data access layer for Nok-kaew Admin."""

import streamlit as st
import gspread
import pandas as pd
from lib.schema import TAB_SETTINGS, TAB_BOOKS, TAB_AUDIT


def _get_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.service_account_from_dict(creds_dict)


def get_spreadsheet():
    client = _get_client()
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    return client.open_by_key(sheet_id)


@st.cache_data(ttl=60)
def get_df(tab_name):
    """Return worksheet as a DataFrame (empty DataFrame if not found)."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(tab_name)
        data = ws.get_all_values()
        if not data or len(data) < 1:
            return pd.DataFrame()
        headers = data[0]
        rows = data[1:] if len(data) > 1 else []
        return pd.DataFrame(rows, columns=headers)
    except gspread.exceptions.WorksheetNotFound:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_categories():
    """Get list of categories from Settings tab (column 0)."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(TAB_SETTINGS)
        data = ws.get_all_values()
        result = []
        for row in data[1:]:
            if row and row[0].strip():
                result.append(row[0].strip())
        return result if result else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_platforms():
    """Get list of platforms from Settings tab (column 1)."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(TAB_SETTINGS)
        data = ws.get_all_values()
        result = []
        for row in data[1:]:
            if len(row) > 1 and row[1].strip():
                result.append(row[1].strip())
        return result if result else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_qc_list():
    """Get unique QC names from Books tab."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(TAB_BOOKS)
        data = ws.get_all_values()
        if not data or len(data) < 2:
            return []
        headers = data[0]
        if "QC" not in headers:
            return []
        qc_idx = headers.index("QC")
        names = set()
        for row in data[1:]:
            if len(row) > qc_idx and row[qc_idx].strip():
                names.add(row[qc_idx].strip())
        return sorted(names)
    except Exception:
        return []


def title_to_qc_map():
    """Return {title: qc} mapping from Books tab."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(TAB_BOOKS)
        data = ws.get_all_values()
        if not data or len(data) < 2:
            return {}
        headers = data[0]
        if "ชื่อเรื่อง" not in headers or "QC" not in headers:
            return {}
        ti = headers.index("ชื่อเรื่อง")
        qi = headers.index("QC")
        return {row[ti].strip(): row[qi].strip() for row in data[1:] if len(row) > max(ti, qi)}
    except Exception:
        return {}


def fetch_worksheet(tab_name):
    """Legacy: return list-of-lists (header + rows)."""
    try:
        spreadsheet = get_spreadsheet()
        ws = spreadsheet.worksheet(tab_name)
        return ws.get_all_values()
    except Exception:
        return []


def append_row(tab_name, row):
    """Append a single row to a worksheet."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    ws.append_row(row)
    st.cache_data.clear()


def append_rows(tab_name, rows):
    """Append multiple rows to a worksheet."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    ws.append_rows(rows)
    st.cache_data.clear()


def write_df(tab_name, df):
    """Replace all worksheet data with a DataFrame (keeps header row)."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    ws.clear()
    data = [df.columns.tolist()] + df.values.tolist()
    ws.update(data)
    st.cache_data.clear()


def write_worksheet(tab_name, data):
    """Legacy: Replace worksheet rows (data is list-of-lists, no header)."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    # Get existing headers
    existing = ws.get_all_values()
    headers = existing[0] if existing else []
    ws.clear()
    if headers:
        ws.append_row(headers)
    for row in data:
        ws.append_row(row)
    st.cache_data.clear()


def update_worksheet_row(tab_name, row_index, row_data):
    """Update a specific row (1-indexed, not counting header)."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    sheet_row = row_index + 1  # +1 for header
    ws.update(f"A{sheet_row}", [row_data])
    st.cache_data.clear()


def delete_worksheet_row(tab_name, row_index):
    """Delete a specific row (1-indexed, not counting header)."""
    spreadsheet = get_spreadsheet()
    ws = spreadsheet.worksheet(tab_name)
    sheet_row = row_index + 1  # +1 for header
    ws.delete_rows(sheet_row)
    st.cache_data.clear()


def log_audit(action, detail):
    """Append an entry to the AuditLog tab."""
    try:
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        append_row(TAB_AUDIT, [now, action, detail])
    except Exception:
        pass


def ensure_worksheets():
    """No-op: real tabs managed in Google Sheet directly."""
    pass
