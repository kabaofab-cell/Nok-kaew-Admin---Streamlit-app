"""Income & accounts page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
from datetime import datetime
from lib.sheets import fetch_worksheet, write_worksheet, append_row
from lib.helpers import format_currency, get_settings_dict


def render_accounts():
    """Render the income & accounts page."""
    st.title("💰 บัญชี & ส่วนแบ่ง")

    income_data = fetch_worksheet("income")
    platforms_data = fetch_worksheet("platforms")
    qc_data = fetch_worksheet("qc")
    novels_data = fetch_worksheet("novels")
    settings_data = fetch_worksheet("settings")

    platforms = [row[0] for row in platforms_data[1:]] if platforms_data else []
    qc_list = [row[0] for row in qc_data[1:]] if qc_data else []
    novels_list = [row[1] for row in novels_data[1:]] if novels_data else []
    settings = get_settings_dict(settings_data)

    user1_name = settings.get("user1_name", "ตอง")
    user2_name = settings.get("user2_name", "ตาว")
    user1_split = float(settings.get("user1_split", 50))
    user2_split = float(settings.get("user2_split", 50))

    tab1, tab2, tab3 = st.tabs(["📝 ลงบัญชีด่วน", "📊 ฐานข้อมูลรายรับ", "💵 สรุปส่วนแบ่ง"])

    with tab1:
        st.subheader("📝 ลงบัญชีรายรับด่วน")

        with st.form("quick_income_form"):
            income_date = st.date_input("วันที่", value=pd.Timestamp.now().date())
            platform = st.selectbox("แพลตฟอร์ม", platforms)
            qc = st.selectbox("ผู้ QC", qc_list)
            amount = st.number_input("จำนวนเงิน", min_value=0.0, format="%.2f")
            novel = st.selectbox("นิยาย", novels_list)

            submitted = st.form_submit_button("💾 บันทึก")

            if submitted:
                if amount > 0 and platform and qc and novel:
                    income_id = f"INC_{datetime.now().timestamp()}"
                    new_row = [
                        income_id,
                        income_date.strftime("%d/%m/%Y"),
                        platform,
                        qc,
                        "",
                        novel,
                        str(amount)
                    ]
                    append_row("income", new_row)
                    st.success("✅ บันทึกสำเร็จ")
                    st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบ")

    with tab2:
        st.subheader("📊 ฐานข้อมูลรายรับ")

        if income_data and len(income_data) > 1:
            df = pd.DataFrame(income_data[1:], columns=income_data[0])

            filter_qc = st.multiselect("กรองตาม QC", qc_list)
            filter_platform = st.multiselect("กรองตามแพลตฟอร์ม", platforms)

            if filter_qc:
                df = df[df["qc"].isin(filter_qc)]
            if filter_platform:
                df = df[df["platform"].isin(filter_platform)]

            edited_df = st.data_editor(df, use_container_width=True)

            if st.button("💾 บันทึกการแก้ไข"):
                new_data = edited_df.values.tolist()
                write_worksheet("income", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()
        else:
            st.info("ยังไม่มีข้อมูลรายรับ")

    with tab3:
        st.subheader("💵 สรุปส่วนแบ่ง")

        if income_data and len(income_data) > 1:
            df = pd.DataFrame(income_data[1:], columns=income_data[0])
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

            total_income = df["amount"].sum()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"📊 รวมรายได้", format_currency(total_income))
            with col2:
                user1_income = (total_income * user1_split) / 100
                st.metric(f"💰 {user1_name} ({user1_split}%)", format_currency(user1_income))
            with col3:
                user2_income = (total_income * user2_split) / 100
                st.metric(f"💰 {user2_name} ({user2_split}%)", format_currency(user2_income))

            st.divider()

            # Income breakdown by QC and platform
            st.write("**รายรับแยกตามผู้ QC**")
            qc_breakdown = df.groupby("qc")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(qc_breakdown)

            st.write("**รายรับแยกตามแพลตฟอร์ม**")
            platform_breakdown = df.groupby("platform")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(platform_breakdown)
        else:
            st.info("ยังไม่มีข้อมูลรายรับ")
