# 🐦 Nok-kaew Admin — Setup & Deployment Guide

## ⚡ Quick Start (Local)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets Credentials

สร้างไฟล์ `.streamlit/secrets.toml` แล้วใส่ credentials:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1at5othFFXrtUGU3nBjk2nsgWpIqMrcd1a2SXsFV6bPE/edit"
type = "service_account"
project_id = "civic-vigil-492116-d4"
private_key_id = "43c0ad2cf7ffa874df8167fca246bba2cf894be9"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCwDMu5KNtS2Jr3
8TnKMDutWnMKAlM9TgyH9mVBegO0/mYP3fHgFcKKUPeJYdlJAWKJ+8LUssTjIreS
kXNGS0rUXtQLn7Z2HecKj7u2u/Y4N/TnIS6yqV8U688efABLkJyeErdypZcpMqoF
5BJrtv+750g0uNMHQ3Yh1drmuw3Fr01WdKAchh5xevaxUzrmtMroBk2M5tc8BfCz
pxkTElXxhfr+VMotGYYbP/FhUPg74Ll6N9Y+ycuFNVN4Pukx0TjEHGgDXe7EQwKJ
8GYscF2cVkHLl7Bp1qhjPPMg/wf4nslfql18r3k3Wf0kE9ihbJN1zdAWoRDyusc0
WBxyDSHzAgMBAAECggEAERrVKmLRWG3KNL/fxQjFq5Snq7fJHaI5LnaepOt1c77p
7K28Q/DpS2YNfvAeW+0CBXUMG31ZCtaDLn7qS9Ch7xtdj9mPMU+7dHe9ncYKaLDr
Hw/GyT4SimZU49nZb34X8XXRFBcJpkuRYGwl7AhGNZwFlHXGryR7VFNCZvuSnXu/
BO6XmEveY7js5WE1uv7W9nNSpP55n9VbAqQxqnlzK/371mXcurxvhL9+6BG4mDwT
R2M5UW/6tpVYcmL+IjlJ47EfxG4bU2cAVNeY0P97np89frXtgyB9MNvsEyWue4kN
gMY9+/AAJym66WaEanPpCc7u85kofYcNODhb53EkSQKBgQDeCpucb/Uf699JtV4P
nhOE8LgQeY9PdXWpoxVMAFoFtGF129Hu3TlKWZsWdbvZsLsme9NOdkbaWDHlgMn1
kBFifmmBoleiRtd/tEu85wOuSn2DRkJFmWUie2GZslBM1bVIloj+nuEkRZCmLlcg
Ibhj3fF9IY4/LFuTjRqP0dRq2QKBgQDK+YZ0OukiZoSDa8LehpTuq8+SUNRRv7rM
vmJOvrBJbTNScS7DunNUiO93xi//zypWfOpC4w3r/KpgSbJnJliHIZMpDjBh26pc
YrPP0rrq25yiYUDndwyofMS8trfU/8CNt993LsccjTNLdM4oFjHsvrgW84qVhYAz
DzSJ4T/7qwKBgCb3O5m3eA/zB8tanbgl6I0C5XpWqtSp600qxnkA8stffV7+hZfi
kMRAd1v4q0+nmSBGyK1TSlnU8mSxNj/22WYsgv1x7OkYf4b0r/nlnJrAjcg00zp9
keb8OgOL7FWfh2HGsSHl5eLEpn7TUQzdfgtgjpmEAv+JHEUHlSq6Cwn5AoGAYruD
+q/ZTcF+fgsCLIpckciDXNHypZ1U+Vk2qsU5LU5wI48ox06/4QQHMET4fj/AgXeb
4FNgJ0Wtfs76eBCACaN8WQEs6b0Xnn7oppQEFlAjXh1em/kd8CtY688ZlwOdH5Ks
oeXgNvQ8Wl0EFx3MxTN0ir2G0PqyhKPF07f9DqcCgYAENAZGLS/8ZzrRdb0is54O
RksQUPlwOZ3xsWsvsWaVfznJ4ro+PNEAmDz5dpJZLVCyLq0Ind/QanckyO2GQaPV
xAhdc7j6gKi2hr2gnEWtg2s8yhSI+gGLAq9iFGnywaHk5thki+F75B0VUfhTsg+V
ih8+MfsUZitAglRSSSdkgw==
-----END PRIVATE KEY-----"""
client_email = "nokkaew-bot@civic-vigil-492116-d4.iam.gserviceaccount.com"
client_id = "108142273617574470564"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/nokkaew-bot%40civic-vigil-492116-d4.iam.gserviceaccount.com"
```

### 3. Run Locally

```bash
streamlit run streamlit_app.py
```

เปิด http://localhost:8501 ✅

---

## 🌐 Deploy to Streamlit Cloud

### Step 1: Push to GitHub

ต้องแน่ใจว่า code อยู่บน GitHub repo: `kabaofab-cell/NOKKUB`

```bash
git push origin master
```

### Step 2: Go to Streamlit Cloud

1. เข้า https://share.streamlit.io
2. Login ด้วย GitHub account
3. Click **"New app"**

### Step 3: Configure App

ใส่:
- **Repository:** `kabaofab-cell/NOKKUB`
- **Branch:** `master` (หรือ `main` ถ้า remote เป็น main)
- **Main file path:** `streamlit_app.py`

### Step 4: Add Secrets

1. ไป **Settings** → **Secrets**
2. Copy-paste content ของ `.streamlit/secrets.toml` (เว้นไว้ใน example เท่านั้น)
3. Save

### Step 5: Deploy!

Streamlit Cloud จะ auto-build & deploy

- ✅ App URL: `https://nokkub.streamlit.app` (หรือชื่ออื่นที่ custom)
- 🔄 Auto-redeploy เวลา push to GitHub
- 📱 Accessible from phone/tablet

---

## 📖 Usage

### สำหรับผู้ใช้ (ตอง/ตาว)

1. **Overview** — ดูสรุป นิยาย รายได้ แนวโน้ม
2. **ปฏิทินคิวงาน** — คลิกวันที่ เพิ่มคิวงาน
3. **จัดการนิยาย** — ดู/เพิ่ม/แก้นิยาย ค้นหา
4. **บัญชี & ส่วนแบ่ง** — ลงรายรับ ดูสรุปส่วนแบ่ง
5. **ตั้งค่า** — เพิ่ม/ลบ หมวดหมู่, แพลตฟอร์ม, QC, backup

### Tips

- **ลิงก์ Google Sheet:** ถูกอ้างอิงใน `.streamlit/secrets.toml` ให้ share ให้ service account
- **Multi-user:** Google Sheets sync แบบ real-time เมื่อหลายคนใช้พร้อม
- **Backup:** หน้าตั้งค่า → ดาวน์โหลด ZIP ได้เสมอ
- **ข้อมูลที่เก็บ:** ทั้งหมดใน Google Sheet (ไม่มีการเก็บบน Streamlit Cloud)

---

## 🛠️ Troubleshooting

### ❌ `AuthenticationError: No credentials found`

**วิธีแก้:**
- Local: ตรวจสอบ `.streamlit/secrets.toml` ถูกต้องไหม
- Streamlit Cloud: ไปที่ Settings → Secrets → แน่ใจว่า copy ถูกต้อง

### ❌ `Worksheet not found`

**วิธีแก้:**
- App สร้าง worksheets อัตโนมัติ
- ถ้าเกิดข้อผิดพลาด → ลองรีสตาร์ท app

### ❌ `Permission denied` เวลา write ไป Google Sheet

**วิธีแก้:**
- Google Sheet → Share → ใส่ `nokkaew-bot@civic-vigil-492116-d4.iam.gserviceaccount.com`
- สิทธิ์ต้องเป็น **Editor**

### ❌ ข้อมูลหาย หลังจาก Streamlit Cloud redeploy

**คำอธิบาย:**
- ฐานข้อมูลอยู่บน **Google Sheet เท่านั้น** (ไม่เก็บใน Streamlit container)
- ข้อมูลจะไม่หาย เพราะ Google Sheet persistent
- ถ้าหายจริง → เปิด Google Sheet ตรวจสอบดูว่ามีข้อมูลมั้ย

---

## 📞 Support

- **GitHub Issues:** https://github.com/kabaofab-cell/NOKKUB/issues
- **Email:** kabaofab@gmail.com

---

**Last Updated:** May 31, 2026
