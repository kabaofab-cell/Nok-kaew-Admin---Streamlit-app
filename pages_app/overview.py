"""Overview/Dashboard page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.sheets import fetch_worksheet
from lib.helpers import format_currency, get_settings_dict


def render_overview():
    """Render the overview dashboard."""
    st.title("📊 Overview")

    novels_data = fetch_worksheet("novels")
    income_data = fetch_worksheet("income")
    settings_data = fetch_worksheet("settings")

    if not novels_data or not income_data:
        st.warning("⏳ กำลังโหลดข้อมูล...")
        return

    settings = get_settings_dict(settings_data)
    user1_name = settings.get("user1_name", "ตอง")
    user2_name = settings.get("user2_name", "ตาว")

    # Parse data
    novels_df = pd.DataFrame(novels_data[1:], columns=novels_data[0])
    income_df = pd.DataFrame(income_data[1:], columns=income_data[0])

    # Summary cards
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📚 นิยายทั้งหมด", len(novels_df))

    with col2:
        if "status" in novels_df.columns:
            updating = len(novels_df[novels_df["status"] == "กำลังอัปเดต"])
            st.metric("📝 กำลังอัปเดต", updating)
        else:
            st.metric("📝 กำลังอัปเดต", 0)

    with col3:
        if "status" in novels_df.columns:
            completed = len(novels_df[novels_df["status"] == "จบแล้ว"])
            st.metric("✅ จบแล้ว", completed)
        else:
            st.metric("✅ จบแล้ว", 0)

    with col4:
        total_income = 0
        if "amount" in income_df.columns:
            try:
                total_income = pd.to_numeric(income_df["amount"], errors="coerce").sum()
            except:
                pass
        st.metric(f"💰 รวมรายได้", format_currency(total_income))

    with col5:
        st.metric("📅 วันนี้", pd.Timestamp.now().strftime("%d/%m/%Y"))

    st.divider()

    # Income chart
    if not income_df.empty and "date" in income_df.columns and "amount" in income_df.columns:
        try:
            income_df["date"] = pd.to_datetime(income_df["date"], errors="coerce")
            income_df["amount"] = pd.to_numeric(income_df["amount"], errors="coerce")
            monthly_income = income_df.groupby(income_df["date"].dt.to_period("M"))["amount"].sum()

            if not monthly_income.empty:
                fig = go.Figure(data=[
                    go.Bar(x=monthly_income.index.astype(str), y=monthly_income.values, name="รายได้")
                ])
                fig.update_layout(title="📈 รายได้รายเดือน", xaxis_title="เดือน", yaxis_title="จำนวนเงิน")
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("ยังไม่มีข้อมูลรายได้")

    st.divider()

    # Top novels
    st.subheader("🏆 Top 10 นิยายขายดี")
    if not income_df.empty:
        try:
            income_df["amount"] = pd.to_numeric(income_df["amount"], errors="coerce")
            if "novel_id" in income_df.columns and "title" in income_df.columns:
                top_novels = income_df.groupby(["novel_id", "title"])["amount"].sum().sort_values(ascending=False).head(10)
                top_df = pd.DataFrame({
                    "อันดับ": range(1, len(top_novels) + 1),
                    "ชื่อเรื่อง": top_novels.index.get_level_values(1),
                    "ยอดขาย": top_novels.values
                })
                st.dataframe(top_df, use_container_width=True, hide_index=True)
        except:
            st.info("ยังไม่มีข้อมูลการขาย")
