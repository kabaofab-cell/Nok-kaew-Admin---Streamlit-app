"""Settings page — manage categories, platforms, and view audit log."""

import streamlit as st
import pandas as pd
import io
import zipfile

from lib.sheets import get_df, get_categories, get_platforms, get_qc_list, write_df, fetch_worksheet
from lib.schema import TAB_SETTINGS, TAB_AUDIT, TAB_BOOKS


def render_settings():
    st.title("⚙️ ตั้งค่าระบบ")

    try:
        settings_df = get_df(TAB_SETTINGS)
        audit_df = get_df(TAB_AUDIT)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        return

    tab_ref, tab_audit, tab_backup = st.tabs(["📋 ค่าอ้างอิง", "🧾 ประวัติการแก้ไข", "💾 Backup"])

    # ── Reference values (categories & platforms from Settings tab) ──
    with tab_ref:
        st.info("แก้ไขตารางด้านล่างแล้วกด **บันทึก** เพื่ออัปเดต Settings tab ใน Google Sheet")

        if settings_df.empty:
            # Initialize with empty scaffold
            settings_df = pd.DataFrame({"categories": [], "platforms": []})

        edited = st.data_editor(
            settings_df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "categories": st.column_config.TextColumn("📚 หมวดหมู่"),
                "platforms": st.column_config.TextColumn("🌐 แพลตฟอร์ม"),
            },
        )

        if st.button("💾 บันทึกค่าอ้างอิง", type="primary"):
            try:
                write_df(TAB_SETTINGS, edited)
                st.success("✅ บันทึกสำเร็จ")
                st.rerun()
            except Exception as e:
                st.error(f"❌ บันทึกไม่สำเร็จ: {e}")

        st.divider()
        st.subheader("📋 รายการปัจจุบัน")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**📚 หมวดหมู่**")
            for x in get_categories():
                st.write(f"• {x}")
        with c2:
            st.write("**🌐 แพลตฟอร์ม**")
            for x in get_platforms():
                st.write(f"• {x}")
        with c3:
            st.write("**👥 ผู้ QC** (จาก Books)")
            for x in get_qc_list():
                st.write(f"• {x}")

    # ── Audit log ──
    with tab_audit:
        if audit_df.empty:
            st.info("ยังไม่มีประวัติใน AuditLog")
        else:
            st.dataframe(audit_df.iloc[::-1], use_container_width=True, hide_index=True)

    # ── Backup ──
    with tab_backup:
        st.subheader("💾 Backup ข้อมูลทั้งหมด")
        if st.button("📦 สร้าง Backup ZIP"):
            try:
                from lib.schema import TAB_CALENDAR, TAB_FINANCE, TAB_PROGRESS
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for tab in [TAB_BOOKS, TAB_CALENDAR, TAB_FINANCE,
                                TAB_SETTINGS, TAB_PROGRESS, TAB_AUDIT]:
                        df = get_df(tab)
                        if not df.empty:
                            csv_buf = io.StringIO()
                            df.to_csv(csv_buf, index=False)
                            zf.writestr(f"{tab}.csv", csv_buf.getvalue())
                zip_buffer.seek(0)
                st.download_button(
                    label="⬇️ ดาวน์โหลด Backup",
                    data=zip_buffer,
                    file_name="nok-kaew-backup.zip",
                    mime="application/zip",
                )
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
