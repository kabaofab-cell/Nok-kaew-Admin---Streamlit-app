# 🐦 Nok-kaew Admin

จัดการนิยาย คิวงาน และรายรับในที่เดียวด้วย Streamlit

## ✨ Features

- 📊 **Dashboard Overview** — สรุปภาพรวมนิยาย รายได้ และแนวโน้ม
- 📅 **Work Queue Calendar** — ปฏิทินคิวงานรายเดือน
- 📚 **Novel Management** — เพิ่ม/แก้ไข/ค้นหานิยาย
- 💰 **Income & Accounts** — ลงบัญชีรายรับด่วน และสรุปส่วนแบ่ง
- ⚙️ **Settings** — จัดการหมวดหมู่, แพลตฟอร์ม, ผู้ QC

## 🛠️ Tech Stack

- **Framework:** Streamlit
- **Data Storage:** Google Sheets
- **Database:** gspread
- **Data Processing:** pandas, plotly
- **UI Theme:** Pink (Nok-kaew)

## 📋 Prerequisites

- Python 3.9+
- Google Cloud Project with Sheets API enabled
- Service Account JSON key
- Google Sheet (ที่แชร์กับ service account)

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/kabaofab-cell/NOKKUB.git
cd NOKKUB
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Google Sheets

#### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Create **Service Account**:
   - IAM & Admin → Service Accounts
   - Create new service account
   - Create JSON key
   - Download JSON file

#### 3.2 Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet (หรือใช้ sheet ที่มีอยู่)
3. Share sheet with service account email (สิทธิ์ Editor)
4. Copy spreadsheet ID จาก URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```

### 4. Setup Streamlit Secrets

**สำหรับรันโลคัล:**

สร้างไฟล์ `.streamlit/secrets.toml`:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----
"""
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL@iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT_EMAIL%40iam.gserviceaccount.com"
```

**สำหรับ Streamlit Cloud:**

1. Push code ไป GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Deploy → Select repository
4. Settings → Secrets
5. ใส่ secrets.toml content เดียวกับข้างบน

## 🏃 Run Locally

```bash
streamlit run nokkaew_admin/streamlit_app.py
```

จากนั้นเปิด `http://localhost:8501`

## 📊 Database Schema

Worksheets ใน Google Sheet:

| Tab | Columns | Purpose |
|-----|---------|---------|
| **novels** | id, title, category, cover_url, qc, status, created_at | บัญชีนิยาย |
| **work_queue** | id, date, novel_id, title, task, qc, status, note | คิวงาน |
| **income** | id, date, platform, qc, novel_id, title, amount | รายรับ |
| **categories** | name | หมวดหมู่นิยาย |
| **platforms** | name | แพลตฟอร์ม |
| **qc** | name | ผู้ QC |
| **settings** | key, value | ตั้งค่าระบบ |

## 🔑 Default Settings

- **ผู้ QC:** ตอง, ตาว
- **หมวดหมู่:** ตัวอักษร, ตัวร้อน, ปีศาจ, ศาสตร์แปลก, ดำหน้า
- **แพลตฟอร์ม:** Wattpad, Royal Road, Webnovel, Tapas
- **ส่วนแบ่ง:** ตอง 50%, ตาว 50%

สามารถแก้ไขได้ในหน้า **⚙️ ตั้งค่า**

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub:
```bash
git add .
git commit -m "Initial commit: Nok-kaew Admin"
git push origin main
```

2. Go to [Streamlit Cloud](https://share.streamlit.io)

3. Click **"New app"** → Select your repo

4. Set:
   - **Repository:** `kabaofab-cell/NOKKUB`
   - **Branch:** `main` (or your branch)
   - **Main file path:** `nokkaew_admin/streamlit_app.py`

5. **Settings** → **Secrets** → ใส่ credentials (เหมือน local)

6. Deploy!

Your app จะ live ที่ `https://your-app.streamlit.app`

## 📝 Usage Tips

- **รีเฟรชข้อมูล:** คลิกปุ่ม "🔄 รีเฟรช" ที่ sidebar (cache TTL 60 วินาที)
- **Backup:** ไปที่ **⚙️ ตั้งค่า** → **💾 Backup** → ดาวน์โหลด ZIP
- **Multi-user:** ทำงานได้พร้อมกันหลายคน (Google Sheets handles sync)

## 🐛 Troubleshooting

### ❌ `AuthenticationError: No credentials found`
- ตรวจสอบ `.streamlit/secrets.toml` ถูกต้อง
- Streamlit Cloud: ตรวจสอบ Secrets ใน Settings

### ❌ `Worksheet not found`
- เปิด Google Sheet → ตรวจสอบ tab names ถูกต้อง
- ลองสร้าง tab เอง หรือ restart app

### ❌ `Permission denied`
- ตรวจสอบ service account email มี Editor permission
- Google Sheet → Share → ใส่ service account email

## 📧 Support

Contact: kabaofab@gmail.com

## 📄 License

Private use only

---

**Last Updated:** May 31, 2026
