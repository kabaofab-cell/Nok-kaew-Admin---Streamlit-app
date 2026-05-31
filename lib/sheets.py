"""Google Sheets data access layer for Nok-kaew Admin."""

import streamlit as st
import gspread
from lib.schema import WORKSHEETS


def get_gsheet_connection():
    """Get authenticated gspread client from Streamlit secrets."""
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.service_account_from_dict(creds_dict)


def get_spreadsheet():
    """Get Google Sheet by URL from secrets."""
    client = get_gsheet_connection()
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    return client.open_by_key(sheet_id)


@st.cache_data(ttl=60)
def fetch_worksheet(sheet_name):
    """Fetch worksheet data with caching (TTL 60 seconds)."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_values()
    except gspread.exceptions.WorksheetNotFound:
        return []


def ensure_worksheets():
    """Create worksheets if they don't exist."""
    spreadsheet = get_spreadsheet()
    existing_sheets = {ws.title for ws in spreadsheet.worksheets()}

    for sheet_name, schema in WORKSHEETS.items():
        if sheet_name not in existing_sheets:
            ws = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(schema["headers"]))
            ws.append_row(schema["headers"])
            if "default_data" in schema:
                for row in schema["default_data"]:
                    ws.append_row(row)


def write_worksheet(sheet_name, data):
    """Write data to worksheet (replace all rows after header)."""
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)

    schema = WORKSHEETS.get(sheet_name, {})
    headers = schema.get("headers", [])

    worksheet.clear()
    worksheet.append_row(headers)

    for row in data:
        worksheet.append_row(row)

    st.cache_data.clear()


def append_row(sheet_name, row):
    """Append a single row to worksheet."""
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    worksheet.append_row(row)
    st.cache_data.clear()


def update_row(sheet_name, row_index, row):
    """Update a specific row in worksheet."""
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    worksheet.delete_rows(row_index)
    for i, cell in enumerate(row, start=1):
        worksheet.update_cell(row_index, i, cell)
    st.cache_data.clear()


def delete_row(sheet_name, row_index):
    """Delete a row from worksheet."""
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    worksheet.delete_rows(row_index)
    st.cache_data.clear()
