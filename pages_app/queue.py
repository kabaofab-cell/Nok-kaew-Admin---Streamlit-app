"""Work queue — reads the Calendar tab, plus ProgressLog."""

import datetime as dt

import streamlit as st
import pandas as pd

from lib.sheets import get_df, append_row, write_df, log_audit
from lib.schema import TAB_CALENDAR, TAB_PROGRESS, TAB_BOOKS, CALENDAR_COLS
from lib.helpers import num_series


def render_queue():
    st.title("📅 ปฏิทินคิวงาน")

    try:
        cal = get_df(TAB_CALENDAR)
        books = get_df(TAB_BOOKS)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        return

    titles = books["ชื่อเรื่อง"].tolist() if not books.empty and "ชื่อเรื่อง" in books.columns else []

    tab_cal, tab_quick, tab_add, tab_progress = st.tabs([
        "🗓️ คิวงาน",
        "⚡ ลงรายการด่วน (ตาราง)",
        "➕ เพิ่มคิว",
        "📈 ความคืบหน้า",
    ])

    # ── Calendar view ──
    with tab_cal:
        if cal.empty:
            st.info("ยังไม่มีคิวงานใน Calendar")
        else:
            view = cal.copy()
            view["_date"] = pd.to_datetime(view["วันที่"], errors="coerce")
            valid = view.dropna(subset=["_date"])

            if not valid.empty:
                months = sorted(valid["_date"].dt.to_period("M").astype(str).unique(), reverse=True)
                picked = st.selectbox("เลือกเดือน", ["ทั้งหมด"] + months)
                if picked != "ทั้งหมด":
                    valid = valid[valid["_date"].dt.to_period("M").astype(str) == picked]

                st.caption(f"แสดง {len(valid)} คิว")
                for day, group in valid.sort_values("_date", ascending=False).groupby(
                    valid["_date"].dt.date, sort=False
                ):
                    with st.container(border=True):
                        st.markdown(f"**📌 {day}**")
                        for _, r in group.iterrows():
                            st.write(f"• {r['ชื่อเรื่อง']} — ตอน {r['ตอนที่']}")
            else:
                st.dataframe(cal, use_container_width=True, hide_index=True)

    # ── Quick table entry ──
    with tab_quick:
        st.info("แก้ไขตารางด้านล่างได้เลย แล้วกด **บันทึก** เพื่อบันทึกทั้งหมด")

        if cal.empty:
            template = pd.DataFrame(columns=CALENDAR_COLS)
        else:
            template = cal.copy()
            template["วันที่"] = pd.to_datetime(template["วันที่"], errors="coerce")

        edited = st.data_editor(
            template,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "วันที่": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                "ชื่อเรื่อง": st.column_config.SelectboxColumn("ชื่อเรื่อง", options=titles) if titles
                              else st.column_config.TextColumn("ชื่อเรื่อง"),
                "ตอนที่": st.column_config.TextColumn("ตอนที่", help="เช่น 36-37"),
            },
            key="quick_cal_editor",
        )

        if st.button("💾 บันทึกทั้งหมด", type="primary", key="save_cal_quick"):
            try:
                clean = edited.dropna(subset=["ชื่อเรื่อง"])
                clean = clean[clean["ชื่อเรื่อง"].astype(str).str.strip() != ""]
                if clean.empty:
                    st.warning("ไม่มีรายการให้บันทึก")
                else:
                    clean["วันที่"] = clean["วันที่"].dt.strftime("%Y-%m-%d")
                    write_df(TAB_CALENDAR, clean)
                    log_audit("แก้ไขคิวงาน", f"บันทึก {len(clean)} รายการ")
                    st.success(f"✅ บันทึก {len(clean)} รายการสำเร็จ")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ บันทึกไม่สำเร็จ: {e}")

    # ── Add single entry ──
    with tab_add:
        with st.form("add_queue"):
            d = st.date_input("วันที่", value=dt.date.today())
            title = st.selectbox("ชื่อเรื่อง", titles) if titles else st.text_input("ชื่อเรื่อง")
            ep = st.text_input("ตอนที่", placeholder="เช่น 36-37")
            if st.form_submit_button("➕ เพิ่มคิว", type="primary"):
                if title and ep:
                    append_row(TAB_CALENDAR, [d.strftime("%Y-%m-%d"), str(title), ep])
                    log_audit("เพิ่มคิวงาน", f"{d} / {title} / {ep}")
                    st.success("✅ เพิ่มคิวสำเร็จ")
                    st.rerun()
                else:
                    st.error("กรุณากรอกชื่อเรื่องและตอนที่")

    # ── Progress log ──
    with tab_progress:
        try:
            prog = get_df(TAB_PROGRESS)
        except Exception:
            prog = pd.DataFrame()

        if prog.empty:
            st.info("ยังไม่มีข้อมูลใน ProgressLog")
        else:
            st.dataframe(prog, use_container_width=True, hide_index=True)
            if "จำนวนตอนที่เพิ่ม" in prog.columns and "QC" in prog.columns:
                prog2 = prog.copy()
                prog2["_n"] = num_series(prog2["จำนวนตอนที่เพิ่ม"])
                summary = prog2.groupby("QC")["_n"].sum().reset_index()
                summary.columns = ["ผู้ QC", "ตอนที่เพิ่มรวม"]
                st.subheader("รวมตอนที่เพิ่ม แยกตามผู้ QC")
                st.dataframe(summary, use_container_width=True, hide_index=True)
