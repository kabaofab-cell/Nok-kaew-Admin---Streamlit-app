"""Settings page for Nok-kaew Admin."""

import streamlit as st
import pandas as pd
import io
import zipfile
from lib.sheets import fetch_worksheet, write_worksheet
from lib.helpers import validate_split, get_settings_dict


def render_settings():
    """Render the settings page."""
    st.title("⚙️ ตั้งค่า")

    categories_data = fetch_worksheet("categories")
    platforms_data = fetch_worksheet("platforms")
    qc_data = fetch_worksheet("qc")
    settings_data = fetch_worksheet("settings")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 หมวดหมู่", "🌐 แพลตฟอร์ม", "👥 ผู้ QC", "⚖️ ส่วนแบ่ง", "💾 Backup"])

    with tab1:
        st.subheader("📚 จัดการหมวดหมู่นิยาย")
        if categories_data:
            headers = categories_data[0]
            data = categories_data[1:]
            df = pd.DataFrame(data, columns=headers)
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

            if st.button("💾 บันทึกหมวดหมู่", key="save_categories"):
                new_data = edited_df.values.tolist()
                write_worksheet("categories", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()

    with tab2:
        st.subheader("🌐 จัดการแพลตฟอร์ม")
        if platforms_data:
            headers = platforms_data[0]
            data = platforms_data[1:]
            df = pd.DataFrame(data, columns=headers)
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

            if st.button("💾 บันทึกแพลตฟอร์ม", key="save_platforms"):
                new_data = edited_df.values.tolist()
                write_worksheet("platforms", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()

    with tab3:
        st.subheader("👥 จัดการผู้ QC")
        if qc_data:
            headers = qc_data[0]
            data = qc_data[1:]
            df = pd.DataFrame(data, columns=headers)
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

            if st.button("💾 บันทึกผู้ QC", key="save_qc"):
                new_data = edited_df.values.tolist()
                write_worksheet("qc", new_data)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()

    with tab4:
        st.subheader("⚖️ จัดการส่วนแบ่ง")
        if settings_data:
            settings = get_settings_dict(settings_data)
            user1_name = settings.get("user1_name", "ตอง")
            user2_name = settings.get("user2_name", "ตาว")

            col1, col2 = st.columns(2)
            with col1:
                user1_split = st.number_input(f"{user1_name} (%)", value=float(settings.get("user1_split", 50)), min_value=0, max_value=100)
            with col2:
                user2_split = st.number_input(f"{user2_name} (%)", value=float(settings.get("user2_split", 50)), min_value=0, max_value=100)

            is_valid, total = validate_split(user1_split, user2_split)

            if is_valid:
                st.success(f"✅ รวม {total}%")
            else:
                st.error(f"❌ รวม {total}% (ต้องเท่ากับ 100%)")

            if st.button("💾 บันทึกส่วนแบ่ง"):
                if is_valid:
                    new_settings = settings_data[0:1]  # Keep header
                    for key, value in settings.items():
                        if key == "user1_split":
                            new_settings.append([key, str(user1_split)])
                        elif key == "user2_split":
                            new_settings.append([key, str(user2_split)])
                        else:
                            new_settings.append([key, value])

                    write_worksheet("settings", new_settings)
                    st.success("✅ บันทึกสำเร็จ")
                    st.rerun()
                else:
                    st.error("กรุณาแก้ไขให้รวมเท่ากับ 100%")

    with tab5:
        st.subheader("💾 Backup ข้อมูล")

        if st.button("📦 สร้าง Backup ZIP"):
            try:
                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    worksheets = ["novels", "work_queue", "income", "categories", "platforms", "qc", "settings"]

                    for ws_name in worksheets:
                        data = fetch_worksheet(ws_name)
                        if data:
                            df = pd.DataFrame(data[1:], columns=data[0])
                            csv_buffer = io.StringIO()
                            df.to_csv(csv_buffer, index=False)
                            zip_file.writestr(f"{ws_name}.csv", csv_buffer.getvalue())

                zip_buffer.seek(0)
                st.download_button(
                    label="⬇️ ดาวน์โหลด Backup",
                    data=zip_buffer,
                    file_name="nok-kaew-backup.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
