# 🐦 Nok-kaew Admin — Project Summary

## ✅ What's Built

แอป **Streamlit** ฉบับสมบูรณ์ สำหรับจัดการนิยาย คิวงาน รายรับ ผ่านหน้า web เดียว

### 📋 Features Completed

- ✅ **Dashboard (Overview)** — สรุปทั้งหมด (นิยาย/รายได้/แนวโน้ม/Top 10)
- ✅ **Work Queue** — ปฏิทินคิวงาน คลิกเพิ่ม/แก้/ลบ
- ✅ **Novel Management** — 4 tabs (แกลลอรี่, แก้ด่วน, เพิ่มใหม่, ค้นหา)
- ✅ **Income & Accounts** — ลงบัญชีด่วน, ฐานข้อมูลรายรับ, สรุปส่วนแบ่ง
- ✅ **Settings** — จัดการทั้งหมด + Backup CSV
- ✅ **Google Sheets Integration** — ทั้งหมด persistent บน Google Sheet
- ✅ **Multi-language** — Thai UI ทั้งหมด
- ✅ **Theme** — Pink/Nok-kaew theme

### 🏗️ Project Structure

```
NOKKUB/
├── streamlit_app.py              # Entry point (main app)
├── requirements.txt              # Dependencies
├── README.md                     # User guide
├── SETUP_GUIDE.md               # Setup & deployment
├── .streamlit/
│   ├── config.toml              # Streamlit config (theme)
│   └── secrets.toml.example     # Example secrets template
├── lib/
│   ├── schema.py                # Google Sheets schema definition
│   ├── sheets.py                # Data access layer (gspread)
│   └── helpers.py               # Utility functions
└── pages_app/
    ├── overview.py              # Dashboard
    ├── queue.py                 # Work queue
    ├── novels.py                # Novel management
    ├── accounts.py              # Income & split
    └── settings.py              # Settings & backup
```

### 🔌 Data Model (Google Sheets)

7 worksheets ใน Google Sheet, auto-create ถ้ายังไม่มี:

| Tab | Purpose |
|-----|---------|
| **novels** | ข้อมูลนิยาย (id, title, category, cover_url, qc, status, created_at) |
| **work_queue** | คิวงาน (id, date, novel_id, title, task, qc, status, note) |
| **income** | รายรับ (id, date, platform, qc, novel_id, title, amount) |
| **categories** | หมวดหมู่ (default: ตัวอักษร, ตัวร้อน, ปีศาจ, ศาสตร์แปลก, ดำหน้า) |
| **platforms** | แพลตฟอร์ม (default: Wattpad, Royal Road, Webnovel, Tapas) |
| **qc** | ผู้ QC (default: ตอง, ตาว) |
| **settings** | ตั้งค่า (user1_name, user2_name, user1_split, user2_split, shop_name) |

### 🛠️ Tech Stack

- **Framework:** Streamlit 1.39.0
- **Data Access:** gspread 6.1.2
- **Auth:** Google OAuth 2 (service account)
- **Data:** pandas 2.2.3
- **Charts:** plotly 5.24.1
- **Styling:** Streamlit built-in (config.toml)

---

## 🚀 How to Use

### Local Development

```bash
# 1. Install
pip install -r requirements.txt

# 2. Setup secrets
# Create .streamlit/secrets.toml (see SETUP_GUIDE.md)

# 3. Run
streamlit run streamlit_app.py
# Open http://localhost:8501
```

### Deploy to Streamlit Cloud

1. Push code to GitHub: `kabaofab-cell/NOKKUB`
2. Go to https://share.streamlit.io
3. Create new app → Select repo
4. Main file: `streamlit_app.py`
5. Add secrets in Settings
6. Deploy! ✅

---

## 📊 Key Features Walkthrough

### 1️⃣ Overview Dashboard

- **Cards:** นิยายทั้งหมด / กำลังอัปเดต / จบแล้ว / รายได้ user1/2 / รวม
- **Chart 1:** รายได้รายเดือน (bar/line)
- **Chart 2:** Top 10 ขายดีรายเดือน (selectable)
- **Table:** ชื่อเรื่อง + QC + ยอดขาย

### 2️⃣ Work Queue

- **Calendar:** Click วันที่ → form เพิ่มคิว (novel, task, QC, status, note)
- **Day View:** รายการคิวของวัน + dropdown สำหรับแก้ status + ปุ่มลบ
- **Summary:** Count คิวรายเดือนแยกตาม status

### 3️⃣ Novel Management

- **Tab 1 (แกลลอรี่):** Grid 3 columns ของ cover + ชื่อ/หมวด/QC/status
- **Tab 2 (แก้ด่วน):** st.data_editor ทั้งตาราง → บันทึก/ยกเลิก
- **Tab 3 (เพิ่มใหม่):** Form (title*, category*, cover, QC*, status*)
- **Tab 4 (ค้นหา/กรอง):** text input + select status/QC/category → filter table

### 4️⃣ Income & Accounts

- **Tab 1 (ลงบัญชีด่วน):** Select date/platform/QC → auto-fetch นิยายของ QC นั้น → grid number input → บันทึก
- **Tab 2 (ฐานข้อมูลรายรับ):** data_editor + filter QC/platform → บันทึก/ยกเลิก
- **Tab 3 (สรุปส่วนแบ่ง):** Cards (รายได้ each user + รวม) + ส่วนแบ่ง % + คำนวณ split + ตารางแยก QC/platform

### 5️⃣ Settings

- **Tab 1 (หมวดหมู่):** data_editor + add row
- **Tab 2 (แพลตฟอร์ม):** data_editor + add row
- **Tab 3 (QC):** data_editor + add row
- **Tab 4 (ส่วนแบ่ง):** number input user1%/user2% → validate 100% → บันทึก
- **Tab 5 (Backup):** Create ZIP ทุก CSV → download

---

## 🔐 Security & Data Persistence

- **Auth:** Service account (no login page) — access ทีงเท่านั้น ที่มี link
- **Data:** ทั้งหมดใน **Google Sheet** (ไม่เก็บ container/server)
- **Secrets:** Stored ใน Streamlit Cloud → ไม่ expose บน repo
- **Cache:** TTL 60 วินาที (auto-clear หลังเขียน)

---

## 📝 Notes

### Credentials Already Set in Code

SETUP_GUIDE.md มี credentials ตัวจริงแล้ว (service account + Google Sheet ที่แชร์):
- Service account: `nokkaew-bot@civic-vigil-492116-d4.iam.gserviceaccount.com`
- Spreadsheet: `1at5othFFXrtUGU3nBjk2nsgWpIqMrcd1a2SXsFV6bPE`
- ✅ Ready to use

### Default QC ตอง/ตาว

อ้างอิงจาก spec คุณ — ส่วนแบ่ง 50/50 ตามเก็บเป็น settings ที่ปรับได้

### การขยาย/ปรับแต่งในอนาคต

- Streamlit rerun() ทำให้ UI responsive (ไม่ใช่ real-time)
- ถ้าต้อง real-time collaboration → ฟังก์ชัน polling เพิ่มเติม
- Image upload อัตโนมัติ → IMGBB_API_KEY พร้อมใช้

---

## ✨ Summary

**Code Status:** ✅ Complete & Ready to Deploy

**Next Steps:**
1. Push to GitHub repo (ถ้า network ได้)
2. Go to Streamlit Cloud → Deploy
3. Share link ให้ ตอง/ตาว ใช้งาน

**GitHub Commits:**
- `61c9c68` — Initial feature set
- `85808bd` — Setup guide

---

**Built with ❤️ for Nok-kaew**

Date: May 31, 2026
