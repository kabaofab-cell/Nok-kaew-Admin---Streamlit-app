"""Novel management page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
from datetime import datetime
from lib.sheets import fetch_worksheet, write_worksheet, append_row
from lib.schema import STATUS_CHOICES


def render_novels():
    """Render the novel management page."""
    st.title("📚 จัดการนิยาย")

    novels_data = fetch_worksheet("novels")
    categories_data = fetch_worksheet("categories")
    qc_data = fetch_worksheet("qc")

    categories = [row[0] for row in categories_data[1:]] if categories_data else []
    qc_list = [row[0] for row in qc_data[1:]] if qc_data else []

    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ แกลลอรี่", "⚡ แก้ด่วน", "➕ เพิ่มใหม่", "🔍 ค้นหา"])

    with tab1:
        st.subheader("🖼️ แกลลอรี่นิยาย")
        if novels_data and len(novels_data) > 1:
            df = pd.DataFrame(novels_data[1:], columns=novels_data[0])
            cols = st.columns(3)
            for idx, row in df.iterrows():
                with cols[idx % 3]:
                    st.write(f"📖 **{row.get('title', 'N/A')}**")
                    st.caption(f"หมวดหมู่: {row.get('category', 'N/A')}")
                    st.caption(f"QC: {row.get('qc', 'N/A')}")
                    st.caption(f"สถานะ: {row.get('status', 'N/A')}")
        else:
            st.info("ยังไม่มีนิยายในระบบ")

    with tab2:
        st.subheader("⚡ แก้ไขข้อมูลด่วน")
        if novels_data and len(novels_data) > 1:
            df = pd.DataFrame(novels_data[1:], columns=novels_data[0])
            edited_df = st.data_editor(df, use_container_width=True)

            if st.button("💾 บันทึกการแก้ไข"):
                new_data = edited_df.values.tolist()
                write_worksheet("novels", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()
        else:
            st.info("ยังไม่มีนิยายในระบบ")

    with tab3:
        st.subheader("➕ เพิ่มนิยายใหม่")

        with st.form("add_novel_form"):
            title = st.text_input("ชื่อเรื่อง *", placeholder="เช่น พรายก้อยฟ้อง")
            category = st.selectbox("หมวดหมู่ *", categories)
            cover_url = st.text_input("ลิงก์รูปปก", placeholder="https://...")
            qc = st.selectbox("ผู้ QC *", qc_list)
            status = st.selectbox("สถานะ *", STATUS_CHOICES)

            submitted = st.form_submit_button("➕ เพิ่มนิยาย")

            if submitted:
                if title and category and qc and status:
                    novel_id = f"NOVEL_{datetime.now().timestamp()}"
                    new_row = [novel_id, title, category, cover_url, qc, status, datetime.now().strftime("%d/%m/%Y")]
                    append_row("novels", new_row)
                    st.success("✅ เพิ่มนิยายสำเร็จ")
                    st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลที่จำเป็น (*)")

    with tab4:
        st.subheader("🔍 ค้นหาและกรองนิยาย")

        search_term = st.text_input("ค้นหาชื่อเรื่อง")
        filter_category = st.multiselect("กรองตามหมวดหมู่", categories)
        filter_status = st.multiselect("กรองตามสถานะ", STATUS_CHOICES)
        filter_qc = st.multiselect("กรองตามผู้ QC", qc_list)

        if novels_data and len(novels_data) > 1:
            df = pd.DataFrame(novels_data[1:], columns=novels_data[0])

            if search_term:
                df = df[df["title"].str.contains(search_term, case=False, na=False)]

            if filter_category:
                df = df[df["category"].isin(filter_category)]

            if filter_status:
                df = df[df["status"].isin(filter_status)]

            if filter_qc:
                df = df[df["qc"].isin(filter_qc)]

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่มีนิยายในระบบ")
