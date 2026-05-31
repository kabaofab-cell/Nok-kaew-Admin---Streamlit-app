"""Work queue page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
from datetime import datetime
from lib.sheets import fetch_worksheet, write_worksheet, append_row
from lib.schema import STATUS_CHOICES, TASK_CHOICES


def render_queue():
    """Render the work queue page."""
    st.title("📅 ปฏิทินคิวงาน")

    queue_data = fetch_worksheet("work_queue")
    novels_data = fetch_worksheet("novels")
    qc_data = fetch_worksheet("qc")

    novels_list = [row[1] for row in novels_data[1:]] if novels_data else []
    qc_list = [row[0] for row in qc_data[1:]] if qc_data else []

    tab1, tab2 = st.tabs(["📋 ตารางคิวงาน", "📊 สรุปคิว"])

    with tab1:
        st.subheader("📋 รายการคิวงาน")

        if queue_data and len(queue_data) > 1:
            df = pd.DataFrame(queue_data[1:], columns=queue_data[0])
            edited_df = st.data_editor(df, use_container_width=True)

            if st.button("💾 บันทึกการเปลี่ยนแปลง"):
                new_data = edited_df.values.tolist()
                write_worksheet("work_queue", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()

        else:
            st.info("ยังไม่มีคิวงาน")

        if st.button("➕ เพิ่มคิวงานใหม่"):
            st.divider()
            st.subheader("➕ เพิ่มคิวงานใหม่")

            with st.form("add_queue_form"):
                queue_date = st.date_input("วันที่", value=pd.Timestamp.now().date())
                novel = st.selectbox("นิยาย *", novels_list)
                task = st.selectbox("งาน *", TASK_CHOICES)
                qc = st.selectbox("ผู้ QC *", qc_list)
                status = st.selectbox("สถานะ *", STATUS_CHOICES)
                note = st.text_area("หมายเหตุ")

                submitted = st.form_submit_button("➕ เพิ่มคิว")

                if submitted:
                    if novel and task and qc and status:
                        queue_id = f"QUEUE_{datetime.now().timestamp()}"
                        new_row = [
                            queue_id,
                            queue_date.strftime("%d/%m/%Y"),
                            "",
                            novel,
                            task,
                            qc,
                            status,
                            note
                        ]
                        append_row("work_queue", new_row)
                        st.success("✅ เพิ่มคิวสำเร็จ")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลที่จำเป็น (*)")

    with tab2:
        st.subheader("📊 สรุปคิวงาน")

        if queue_data and len(queue_data) > 1:
            df = pd.DataFrame(queue_data[1:], columns=queue_data[0])

            if "status" in df.columns:
                status_counts = df["status"].value_counts()
                st.bar_chart(status_counts)

                col1, col2, col3 = st.columns(3)
                for status_type in STATUS_CHOICES:
                    count = status_counts.get(status_type, 0)
                    if status_type == STATUS_CHOICES[0]:
                        with col1:
                            st.metric(status_type, count)
                    elif status_type == STATUS_CHOICES[1]:
                        with col2:
                            st.metric(status_type, count)
                    else:
                        with col3:
                            st.metric(status_type, count)
        else:
            st.info("ยังไม่มีข้อมูลคิวงาน")
