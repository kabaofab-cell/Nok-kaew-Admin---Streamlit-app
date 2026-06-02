"""Novel management — reads/writes the Books tab."""

import streamlit as st
import pandas as pd

from lib.sheets import (
    get_df, get_categories, get_qc_list, append_row, write_df,
    update_worksheet_row, delete_worksheet_row, log_audit,
)
from lib.schema import TAB_BOOKS, BOOKS_COLS, STATUS_CHOICES
from lib.imgbb import upload_to_imgbb


def _status_badge(status):
    colors = {
        "กำลังอัปเดต": ("#1a7f37", "#d1fae5"),
        "จบแล้ว": ("#1d4ed8", "#dbeafe"),
        "พักการแปล": ("#92400e", "#fef3c7"),
    }
    fg, bg = colors.get(status, ("#374151", "#f3f4f6"))
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:999px;font-size:0.75rem;font-weight:600">{status}</span>'
    )


def _imgbb_uploader(session_key: str, current_url: str = "") -> str:
    """Show file uploader + upload button. Returns the current cover URL."""
    uploaded = st.file_uploader(
        "📤 อัพรูปปกจากเครื่อง",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"uploader_{session_key}",
        help="รองรับ JPG, PNG, WebP ขนาดสูงสุด 32 MB",
    )
    if uploaded:
        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            if st.button("☁️ Upload", key=f"upload_btn_{session_key}", type="secondary"):
                with st.spinner("กำลัง upload..."):
                    try:
                        url = upload_to_imgbb(uploaded.read())
                        st.session_state[session_key] = url
                        st.success("✅ Upload สำเร็จ")
                    except Exception as e:
                        st.error(f"❌ Upload ไม่สำเร็จ: {e}")
        with col_info:
            st.caption("กดปุ่ม ☁️ Upload เพื่อส่งรูปขึ้น ImgBB")

    # Return URL from session_state if just uploaded, else fall back to current_url
    return st.session_state.get(session_key, current_url)


def render_novels():
    st.title("📚 จัดการนิยาย")

    try:
        books = get_df(TAB_BOOKS)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        return

    categories = get_categories()
    qc_list = get_qc_list()

    tab_gallery, tab_quick, tab_add = st.tabs(["🖼️ แกลลอรี่", "⚡ แก้ไขด่วน", "➕ เพิ่มนิยายใหม่"])

    # ── Gallery (row/table layout) ──
    with tab_gallery:
        if books.empty:
            st.info("ยังไม่มีนิยายใน Books")
        else:
            # Filters
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                search = st.text_input("🔍 ค้นหา", placeholder="ชื่อเรื่อง...")
            with fc2:
                f_cat = st.multiselect("หมวดหมู่", categories)
            with fc3:
                f_qc = st.multiselect("QC", qc_list)
            with fc4:
                f_status = st.multiselect("สถานะ", STATUS_CHOICES)

            view = books.copy()
            if search:
                view = view[view["ชื่อเรื่อง"].str.contains(search, case=False, na=False)]
            if f_cat:
                view = view[view["หมวดหมู่"].isin(f_cat)]
            if f_qc:
                view = view[view["QC"].isin(f_qc)]
            if f_status:
                view = view[view["สถานะ"].isin(f_status)]

            # Newest first (last rows in the sheet are the most recently added)
            view = view.iloc[::-1]

            st.caption(f"แสดง {len(view)} เรื่อง · ใหม่สุดก่อน · 👆 คลิกชื่อเพื่อแก้ไข")

            # Header row
            widths = [0.55, 4.2, 1.5, 0.9, 1.4, 1.0]
            header = st.columns(widths)
            labels = ["ปก", "ชื่อเรื่อง", "หมวดหมู่", "QC", "สถานะ", "ตอน"]
            for h, lbl in zip(header, labels):
                h.markdown(f"<small style='color:#6b7280;font-weight:600'>{lbl}</small>",
                           unsafe_allow_html=True)
            st.divider()

            clicked_idx = None
            for row_idx, (df_idx, book) in enumerate(view.iterrows()):
                row = st.columns(widths)
                cover = str(book.get("ภาพปก", "")).strip()
                with row[0]:
                    if cover and cover.startswith("http"):
                        st.image(cover, width=38)
                    else:
                        st.markdown("📖")
                with row[1]:
                    title = str(book.get("ชื่อเรื่อง", ""))
                    if st.button(title, key=f"edit_{df_idx}", use_container_width=True,
                                 help="คลิกเพื่อแก้ไข"):
                        clicked_idx = df_idx
                with row[2]:
                    st.markdown(f"<small>{book.get('หมวดหมู่','')}</small>", unsafe_allow_html=True)
                with row[3]:
                    st.markdown(f"<small>{book.get('QC','')}</small>", unsafe_allow_html=True)
                with row[4]:
                    st.markdown(_status_badge(book.get("สถานะ", "")), unsafe_allow_html=True)
                with row[5]:
                    ep_cur = book.get("ตอนปัจจุบัน", "")
                    ep_goal = book.get("เป้าหมาย", "")
                    ep_str = f"{ep_cur}/{ep_goal}" if ep_goal else str(ep_cur)
                    st.markdown(f"<small>{ep_str}</small>", unsafe_allow_html=True)

                if row_idx < len(view) - 1:
                    st.markdown(
                        "<hr style='margin:2px 0;border:none;border-top:1px solid #e5e7eb'>",
                        unsafe_allow_html=True,
                    )

            # Open the edit dialog only when a title was clicked this run.
            if clicked_idx is not None:
                _show_edit_dialog(books, clicked_idx, categories, qc_list)

    # ── Quick edit table ──
    with tab_quick:
        st.info("แก้ไขข้อมูลในตารางด้านล่าง แล้วกด **บันทึก**")
        if books.empty:
            st.info("ยังไม่มีนิยาย")
        else:
            status_col_cfg = st.column_config.SelectboxColumn("สถานะ", options=STATUS_CHOICES)
            cat_col_cfg = st.column_config.SelectboxColumn("หมวดหมู่", options=categories) if categories else None
            qc_col_cfg = st.column_config.SelectboxColumn("QC", options=qc_list) if qc_list else None

            col_cfgs = {"สถานะ": status_col_cfg}
            if cat_col_cfg:
                col_cfgs["หมวดหมู่"] = cat_col_cfg
            if qc_col_cfg:
                col_cfgs["QC"] = qc_col_cfg

            edited = st.data_editor(
                books,
                use_container_width=True,
                hide_index=True,
                column_config=col_cfgs,
                key="quick_novels_editor",
            )

            if st.button("💾 บันทึกการแก้ไข", type="primary"):
                try:
                    write_df(TAB_BOOKS, edited)
                    log_audit("แก้ไขนิยาย (bulk)", f"บันทึก {len(edited)} รายการ")
                    st.success("✅ บันทึกสำเร็จ")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ บันทึกไม่สำเร็จ: {e}")

    # ── Add new novel ──
    with tab_add:
        # Upload widget sits outside the form so it can trigger a rerun
        cover_url = _imgbb_uploader("add_novel_cover")

        with st.form("add_novel"):
            title = st.text_input("ชื่อเรื่อง *", placeholder="เช่น พรายก้อยฟ้อง")
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox("หมวดหมู่ *", categories or [""])
                qc = st.selectbox("QC *", qc_list or [""])
                status = st.selectbox("สถานะ *", STATUS_CHOICES)
            with c2:
                ep_cur = st.text_input("ตอนปัจจุบัน", placeholder="เช่น 20")
                ep_goal = st.text_input("เป้าหมาย", placeholder="เช่น 50")
                cover_input = st.text_input(
                    "ลิงก์ภาพปก",
                    value=cover_url,
                    placeholder="https://... (หรืออัพรูปด้านบน)",
                )

            synopsis = st.text_area("เรื่องย่อ")

            if st.form_submit_button("➕ เพิ่มนิยาย", type="primary"):
                if title.strip():
                    new_row = [
                        title.strip(), category, qc, status,
                        ep_cur, ep_goal, cover_input,
                        "", "[]", "[]", synopsis, ""
                    ]
                    append_row(TAB_BOOKS, new_row)
                    log_audit("เพิ่มนิยาย", title.strip())
                    # Clear uploaded cover from session state after save
                    st.session_state.pop("add_novel_cover", None)
                    st.success(f"✅ เพิ่ม '{title}' สำเร็จ")
                    st.rerun()
                else:
                    st.error("กรุณากรอกชื่อเรื่อง")


def _show_edit_dialog(books, idx, categories, qc_list):
    """Show edit form for the book at DataFrame index idx."""
    if idx not in books.index:
        return

    book = books.loc[idx]
    session_key = f"edit_cover_{idx}"

    @st.dialog(f"แก้ไข: {book.get('ชื่อเรื่อง', '')}")
    def _dialog():
        # Cover preview
        existing_cover = str(book.get("ภาพปก", "")).strip()
        if existing_cover and existing_cover.startswith("http"):
            st.image(existing_cover, width=80)

        # Upload widget outside the form
        uploaded_url = _imgbb_uploader(session_key, existing_cover)

        with st.form("edit_novel_form"):
            title = st.text_input("ชื่อเรื่อง *", value=str(book.get("ชื่อเรื่อง", "")))
            c1, c2 = st.columns(2)
            with c1:
                cat_opts = categories or [""]
                cur_cat = str(book.get("หมวดหมู่", ""))
                cat_idx = cat_opts.index(cur_cat) if cur_cat in cat_opts else 0
                category = st.selectbox("หมวดหมู่", cat_opts, index=cat_idx)

                qc_opts = qc_list or [""]
                cur_qc = str(book.get("QC", ""))
                qc_idx_val = qc_opts.index(cur_qc) if cur_qc in qc_opts else 0
                qc = st.selectbox("QC", qc_opts, index=qc_idx_val)

                cur_status = str(book.get("สถานะ", ""))
                st_idx = STATUS_CHOICES.index(cur_status) if cur_status in STATUS_CHOICES else 0
                status = st.selectbox("สถานะ", STATUS_CHOICES, index=st_idx)
            with c2:
                ep_cur = st.text_input("ตอนปัจจุบัน", value=str(book.get("ตอนปัจจุบัน", "")))
                ep_goal = st.text_input("เป้าหมาย", value=str(book.get("เป้าหมาย", "")))
                cover = st.text_input(
                    "ลิงก์ภาพปก",
                    value=uploaded_url,
                    placeholder="https://... (หรืออัพรูปด้านบน)",
                )

            synopsis = st.text_area("เรื่องย่อ", value=str(book.get("เรื่องย่อ", "")))

            col_save, col_cancel = st.columns(2)
            with col_save:
                saved = st.form_submit_button("💾 บันทึก", type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("ยกเลิก")

        if saved:
            row_num = books.index.get_loc(idx) + 1  # 1-indexed
            new_data = [
                title.strip(), category, qc, status,
                ep_cur, ep_goal, cover,
                str(book.get("หมายเหตุ", "")),
                str(book.get("ลิงก์อ่าน", "")),
                str(book.get("ลิงก์ต้นฉบับ", "")),
                synopsis,
                str(book.get("ลิงก์ PDF", "")),
            ]
            update_worksheet_row(TAB_BOOKS, row_num, new_data)
            log_audit("แก้ไขนิยาย", title.strip())
            st.session_state.pop(session_key, None)
            st.rerun()

        if cancelled:
            st.session_state.pop(session_key, None)
            st.rerun()

        st.divider()
        with st.expander("🗑️ ลบนิยายนี้"):
            st.warning(f"ลบ '{book.get('ชื่อเรื่อง', '')}' ออกจากระบบถาวร")
            if st.button("ยืนยันการลบ", type="secondary"):
                row_num = books.index.get_loc(idx) + 1
                delete_worksheet_row(TAB_BOOKS, row_num)
                log_audit("ลบนิยาย", str(book.get("ชื่อเรื่อง", "")))
                st.rerun()

    _dialog()
