"""Income & accounts — reads/writes the Finance tab."""

import datetime as dt

import streamlit as st
import pandas as pd
import plotly.express as px

from lib.sheets import get_df, get_platforms, get_qc_list, append_rows, log_audit, title_to_qc_map
from lib.schema import TAB_FINANCE, TAB_BOOKS, PLATFORM_FEE_RATE
from lib.helpers import format_currency, num_series, to_num, add_month_column, month_options, thai_month_label


def _save_finance_rows(rows, source):
    from lib.sheets import append_rows
    append_rows(TAB_FINANCE, rows)
    log_audit("เพิ่มรายรับ", f"{source} ({len(rows)} รายการ)")


def render_accounts():
    st.title("💰 บัญชี & ส่วนแบ่ง")

    try:
        finance = get_df(TAB_FINANCE)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        return

    tab_quick, tab_month, tab_data, tab_split = st.tabs([
        "⚡ ลงบัญชีด่วนรายคน",
        "📅 รายรับเดือนนี้",
        "📊 ฐานข้อมูลรายรับ",
        "💵 สรุปส่วนแบ่ง",
    ])

    # ── Quick per-QC entry ──
    with tab_quick:
        st.info("เลือกวันที่ แพลตฟอร์ม และผู้ดูแล (QC) เพื่อดูข้อมูลที่เคยลงในวันนั้น")

        c1, c2, c3 = st.columns(3)
        with c1:
            entry_date = st.date_input("วันที่ลงบัญชี", value=dt.date.today())
        with c2:
            platform = st.selectbox("แพลตฟอร์ม", get_platforms() or ["(ไม่มีแพลตฟอร์ม)"])
        with c3:
            qc = st.selectbox("กรองตามผู้ดูแล (QC)", get_qc_list() or ["(ไม่มี QC)"])

        books = get_df(TAB_BOOKS)
        if books.empty or "ชื่อเรื่อง" not in books.columns:
            st.warning("ยังไม่มีข้อมูลนิยายใน Books")
        else:
            qc_col = books.get("QC", pd.Series(dtype=str))
            qc_titles = books.loc[qc_col == qc, "ชื่อเรื่อง"].tolist()
            if not qc_titles:
                st.warning(f"ไม่พบนิยายของผู้ดูแล '{qc}'")
            else:
                # Get existing entries for this date
                date_str = entry_date.strftime("%Y-%m-%d")
                existing = finance[(finance["วันที่"] == date_str) & (finance["แพลตฟอร์ม"] == platform)]

                # Build grid starting with all titles for QC
                grid = pd.DataFrame({"ชื่อเรื่อง": qc_titles, "ยอดดิบ (฿)": [0.0] * len(qc_titles)})

                # Fill in existing values
                for idx, title in enumerate(qc_titles):
                    existing_row = existing[existing["ชื่อเรื่อง"] == title]
                    if not existing_row.empty:
                        grid.loc[idx, "ยอดดิบ (฿)"] = to_num(existing_row.iloc[0].get("ยอดดิบ", 0))

                # Show existing entries summary
                if not existing.empty:
                    st.markdown(f"**📊 ข้อมูลที่ลงไปแล้วในวันนี้ ({date_str}):**")
                    summary_cols = ["ชื่อเรื่อง", "ยอดดิบ", "ยอดสุทธิ"]
                    summary_cols = [c for c in summary_cols if c in existing.columns]
                    st.dataframe(
                        existing[summary_cols],
                        use_container_width=True,
                        hide_index=True,
                    )
                    total_net = num_series(existing["ยอดสุทธิ"]).sum() if "ยอดสุทธิ" in existing.columns else 0
                    st.caption(f"รวมสุทธิในวันนี้: {format_currency(total_net)} ฿")
                    st.divider()

                st.markdown("**เพิ่มเติม หรือแก้ไขยอด:**")
                edited = st.data_editor(
                    grid,
                    use_container_width=True,
                    hide_index=True,
                    disabled=["ชื่อเรื่อง"],
                    column_config={
                        "ยอดดิบ (฿)": st.column_config.NumberColumn(
                            "ยอดดิบ (฿)", min_value=0.0, step=100.0, format="%.2f"
                        )
                    },
                    key=f"quick_{qc}_{platform}_{date_str}",
                )

                filled = [(r["ชื่อเรื่อง"], to_num(r["ยอดดิบ (฿)"]))
                          for _, r in edited.iterrows() if to_num(r["ยอดดิบ (฿)"]) > 0]
                preview_total = sum(g for _, g in filled)
                st.caption(
                    f"กรอกแล้ว {len(filled)} เรื่อง · รวมยอดดิบ {format_currency(preview_total)} ฿ "
                    f"→ สุทธิหลังหัก {int(PLATFORM_FEE_RATE*100)}% "
                    f"≈ {format_currency(preview_total * (1 - PLATFORM_FEE_RATE))} ฿"
                )

                if st.button("💾 บันทึกยอดรายรับทั้งหมด", type="primary"):
                    if not filled:
                        st.error("ยังไม่ได้กรอกยอดเลย")
                    else:
                        rows = []
                        for title, gross in filled:
                            fee = round(gross * PLATFORM_FEE_RATE, 2)
                            net = round(gross - fee, 2)
                            rows.append([
                                date_str,
                                title, platform, gross, fee, net
                            ])
                        _save_finance_rows(rows, f"{date_str} / {platform} / {qc}")
                        st.success(f"✅ บันทึก {len(rows)} รายการสำเร็จ")
                        st.rerun()

    # ── This month ──
    with tab_month:
        if finance.empty or "ยอดสุทธิ" not in finance.columns:
            st.info("ยังไม่มีข้อมูลใน Finance")
        else:
            fin = add_month_column(finance, "วันที่")
            fin["_gross"] = num_series(fin.get("ยอดดิบ", pd.Series(dtype=float)))
            fin["_net"] = num_series(fin["ยอดสุทธิ"])

            this_month = dt.date.today().strftime("%Y-%m")
            st.subheader(f"📅 {thai_month_label(this_month)}")

            cur = fin[fin["_month"] == this_month]
            if cur.empty:
                st.warning(f"เดือนนี้ ({thai_month_label(this_month)}) ยังไม่มีรายรับ")
                latest = month_options(finance, "วันที่")
                if latest:
                    st.caption(f"เดือนล่าสุดที่มีข้อมูล: {thai_month_label(latest[0])}")
            else:
                m1, m2, m3 = st.columns(3)
                m1.metric("จำนวนรายการ", len(cur))
                m2.metric("ยอดดิบรวม", format_currency(cur["_gross"].sum()))
                m3.metric("💰 ยอดสุทธิรวม", format_currency(cur["_net"].sum()))

                qc_map = title_to_qc_map()
                cur = cur.copy()
                cur["ผู้ QC"] = cur["ชื่อเรื่อง"].map(lambda t: qc_map.get(str(t).strip(), "ไม่ระบุ"))
                by_qc = cur.groupby("ผู้ QC")["_net"].sum().reset_index()
                cols = st.columns(max(len(by_qc), 1))
                for col, (_, r) in zip(cols, by_qc.iterrows()):
                    col.metric(f"👤 {r['ผู้ QC']}", format_currency(r["_net"]))

                st.divider()
                show_cols = [c for c in ["วันที่", "ชื่อเรื่อง", "แพลตฟอร์ม", "ยอดดิบ",
                                          "หักแพลตฟอร์ม (17%)", "ยอดสุทธิ", "ผู้ QC"]
                             if c in cur.columns or c == "ผู้ QC"]
                st.dataframe(cur[show_cols], use_container_width=True, hide_index=True)

    # ── All data with month filter ──
    with tab_data:
        if finance.empty:
            st.info("ยังไม่มีข้อมูลรายรับ")
        else:
            months = month_options(finance, "วันที่")
            picked = st.selectbox(
                "เลือกเดือน", ["ทั้งหมด"] + months,
                format_func=lambda x: "ทั้งหมด" if x == "ทั้งหมด" else thai_month_label(x),
                key="data_month",
            )
            fin = add_month_column(finance, "วันที่")
            if picked != "ทั้งหมด":
                fin = fin[fin["_month"] == picked]

            fin = fin.sort_values("_date", ascending=False)
            net_total = num_series(fin["ยอดสุทธิ"]).sum() if "ยอดสุทธิ" in fin.columns else 0
            st.caption(f"แสดง {len(fin)} รายการ · ยอดสุทธิรวม {format_currency(net_total)} ฿")
            st.dataframe(
                fin.drop(columns=["_date", "_month"], errors="ignore"),
                use_container_width=True, hide_index=True,
            )

    # ── Split summary ──
    with tab_split:
        if finance.empty or "ยอดสุทธิ" not in finance.columns:
            st.info("ยังไม่มีข้อมูลใน Finance")
        else:
            months = month_options(finance, "วันที่")
            picked = st.selectbox(
                "เลือกเดือน", ["ทั้งหมด"] + months,
                format_func=lambda x: "ทั้งหมด" if x == "ทั้งหมด" else thai_month_label(x),
                key="split_month",
            )
            fin = add_month_column(finance, "วันที่")
            if picked != "ทั้งหมด":
                fin = fin[fin["_month"] == picked]

            fin = fin.copy()
            fin["_gross"] = num_series(fin.get("ยอดดิบ", pd.Series(dtype=float)))
            fin["_net"] = num_series(fin["ยอดสุทธิ"])

            period_label = "ทุกเดือน" if picked == "ทั้งหมด" else thai_month_label(picked)

            c1, c2, c3 = st.columns(3)
            c1.metric("ยอดดิบรวม", format_currency(fin["_gross"].sum()))
            c2.metric("หักแพลตฟอร์ม", format_currency(fin["_gross"].sum() - fin["_net"].sum()))
            c3.metric("💰 ยอดสุทธิรวม", format_currency(fin["_net"].sum()))

            st.divider()

            qc_map = title_to_qc_map()
            fin["ผู้ QC"] = fin["ชื่อเรื่อง"].map(lambda t: qc_map.get(str(t).strip(), "ไม่ระบุ"))

            by_qc = (
                fin.groupby("ผู้ QC")
                .agg(ยอดดิบ=("_gross", "sum"), ยอดสุทธิ=("_net", "sum"))
                .sort_values("ยอดสุทธิ", ascending=False)
                .reset_index()
            )

            st.subheader(f"👥 รายได้สุทธิ แยกตามผู้ QC · {period_label}")

            # Per-QC detail cards: gross total, net total, top novels
            for _, r in by_qc.iterrows():
                qc_name = r["ผู้ QC"]
                with st.container(border=True):
                    st.markdown(f"### 👤 {qc_name}")
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("ยอดขายรวม (ดิบ)", format_currency(r["ยอดดิบ"]))
                    mc2.metric("หักแพลตฟอร์ม", format_currency(r["ยอดดิบ"] - r["ยอดสุทธิ"]))
                    mc3.metric("💰 ยอดสุทธิ", format_currency(r["ยอดสุทธิ"]))

                    qc_rows = fin[fin["ผู้ QC"] == qc_name]
                    top_books = (
                        qc_rows.groupby("ชื่อเรื่อง")
                        .agg(ยอดดิบ=("_gross", "sum"), ยอดสุทธิ=("_net", "sum"))
                        .sort_values("ยอดสุทธิ", ascending=False)
                        .head(5)
                        .reset_index()
                    )
                    if not top_books.empty:
                        st.caption("🏆 เรื่องขายดี (Top 5)")
                        disp = top_books.copy()
                        disp["ยอดดิบ"] = disp["ยอดดิบ"].map(format_currency)
                        disp["ยอดสุทธิ"] = disp["ยอดสุทธิ"].map(format_currency)
                        st.dataframe(disp, use_container_width=True, hide_index=True)

            st.divider()

            cc1, cc2 = st.columns(2)
            with cc1:
                if not by_qc.empty:
                    fig = px.pie(by_qc, names="ผู้ QC", values="ยอดสุทธิ",
                                 title="สัดส่วนรายได้ตาม QC")
                    st.plotly_chart(fig, use_container_width=True)
            with cc2:
                if "แพลตฟอร์ม" in fin.columns:
                    by_plat = (
                        fin.assign(แพลตฟอร์ม=fin["แพลตฟอร์ม"].str.strip())
                        .groupby("แพลตฟอร์ม")["_net"].sum().sort_values(ascending=False)
                        .reset_index()
                    )
                    by_plat.columns = ["แพลตฟอร์ม", "รายได้สุทธิ"]
                    st.subheader("🌐 ตามแพลตฟอร์ม")
                    disp = by_plat.copy()
                    disp["รายได้สุทธิ"] = disp["รายได้สุทธิ"].map(format_currency)
                    st.dataframe(disp, use_container_width=True, hide_index=True)

            # Reference table: all titles + sales for the selected period
            st.divider()
            st.subheader(f"📋 ตารางอ้างอิง — ยอดขายรายเรื่อง · {period_label}")
            ref = (
                fin.groupby(["ชื่อเรื่อง", "ผู้ QC"])
                .agg(ยอดดิบ=("_gross", "sum"), ยอดสุทธิ=("_net", "sum"))
                .sort_values("ยอดสุทธิ", ascending=False)
                .reset_index()
            )
            if ref.empty:
                st.info("ยังไม่มีข้อมูลในช่วงที่เลือก")
            else:
                st.caption(f"รวม {len(ref)} เรื่อง")
                disp_ref = ref.copy()
                disp_ref["ยอดดิบ"] = disp_ref["ยอดดิบ"].map(format_currency)
                disp_ref["ยอดสุทธิ"] = disp_ref["ยอดสุทธิ"].map(format_currency)
                st.dataframe(disp_ref, use_container_width=True, hide_index=True)
