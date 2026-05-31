"""Overview/Dashboard page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
import plotly.express as px

from lib.sheets import get_df
from lib.schema import TAB_BOOKS, TAB_FINANCE
from lib.helpers import format_currency, num_series


def render_overview():
    st.title("📊 สรุปภาพรวม")

    try:
        books = get_df(TAB_BOOKS)
        finance = get_df(TAB_FINANCE)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        return

    # --- Metric cards ---
    total_books = len(books)
    updating = done = paused = 0
    if "สถานะ" in books.columns:
        counts = books["สถานะ"].value_counts()
        updating = int(counts.get("กำลังอัปเดต", 0))
        done = int(counts.get("จบแล้ว", 0))
        paused = int(counts.get("พักการแปล", 0))

    total_income = 0.0
    if not finance.empty and "ยอดสุทธิ" in finance.columns:
        total_income = num_series(finance["ยอดสุทธิ"]).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 นิยายทั้งหมด", total_books)
    c2.metric("✍️ กำลังอัปเดต", updating)
    c3.metric("✅ จบแล้ว", done)
    c4.metric("💰 รายได้สุทธิรวม", format_currency(total_income))

    if paused:
        st.caption(f"⏸️ พักการแปล: {paused} เรื่อง")

    st.divider()

    # --- Monthly income bar chart ---
    if not finance.empty and "วันที่" in finance.columns and "ยอดสุทธิ" in finance.columns:
        try:
            fin = finance.copy()
            fin["_date"] = pd.to_datetime(fin["วันที่"], errors="coerce")
            fin["_net"] = num_series(fin["ยอดสุทธิ"])
            fin = fin.dropna(subset=["_date"])
            if not fin.empty:
                monthly = (
                    fin.groupby(fin["_date"].dt.to_period("M").astype(str))["_net"]
                    .sum().reset_index()
                )
                monthly.columns = ["เดือน", "รายได้สุทธิ"]
                fig = px.bar(monthly, x="เดือน", y="รายได้สุทธิ",
                             title="📈 รายได้สุทธิรายเดือน", text_auto=".2s")
                fig.update_layout(yaxis_title="บาท", xaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    col_a, col_b = st.columns(2)

    # --- Books by category pie chart ---
    with col_a:
        if not books.empty and "หมวดหมู่" in books.columns:
            cat = books["หมวดหมู่"].value_counts().reset_index()
            cat.columns = ["หมวดหมู่", "จำนวน"]
            fig = px.pie(cat, names="หมวดหมู่", values="จำนวน", title="📚 สัดส่วนหมวดหมู่")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลหมวดหมู่")

    # --- Top 10 earning novels ---
    with col_b:
        if not finance.empty and "ชื่อเรื่อง" in finance.columns and "ยอดสุทธิ" in finance.columns:
            try:
                fin2 = finance.copy()
                fin2["_net"] = num_series(fin2["ยอดสุทธิ"])
                top = (
                    fin2.groupby("ชื่อเรื่อง")["_net"].sum()
                    .sort_values(ascending=False).head(10).reset_index()
                )
                top.columns = ["ชื่อเรื่อง", "รายได้สุทธิ"]
                top["รายได้สุทธิ"] = top["รายได้สุทธิ"].map(format_currency)
                st.subheader("🏆 Top 10 ทำเงิน")
                st.dataframe(top, use_container_width=True, hide_index=True)
            except Exception:
                st.info("ยังไม่มีข้อมูลการขาย")
        else:
            st.info("ยังไม่มีข้อมูลรายรับ")
