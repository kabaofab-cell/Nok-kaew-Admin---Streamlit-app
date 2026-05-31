"""Nok-kaew Admin - Novel Management System
Main entry point and navigation.
"""

import streamlit as st

try:
    st.set_page_config(
        page_title="🐦 Nok-kaew Admin",
        page_icon="🐦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except:
    pass

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🐦 Nok-kaew Admin")
    st.caption("จัดการนิยาย คิวงาน และรายรับในที่เดียว")

    page = st.radio(
        "📌 เมนู",
        [
            "📊 Overview",
            "📅 ปฏิทินคิวงาน",
            "📚 จัดการนิยาย",
            "💰 บัญชี & ส่วนแบ่ง",
            "⚙️ ตั้งค่า"
        ]
    )

    st.divider()

    if st.button("🔄 รีเฟรช", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Made with 💖 for Nok-kaew")

if page == "📊 Overview":
    from pages_app.overview import render_overview
    render_overview()

elif page == "📅 ปฏิทินคิวงาน":
    from pages_app.queue import render_queue
    render_queue()

elif page == "📚 จัดการนิยาย":
    from pages_app.novels import render_novels
    render_novels()

elif page == "💰 บัญชี & ส่วนแบ่ง":
    from pages_app.accounts import render_accounts
    render_accounts()

elif page == "⚙️ ตั้งค่า":
    from pages_app.settings import render_settings
    render_settings()
