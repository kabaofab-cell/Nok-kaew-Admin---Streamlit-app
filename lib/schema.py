"""Google Sheets schema definition for Nok-kaew Admin."""

# Real worksheet tab names in Google Sheet
TAB_BOOKS = "Books"
TAB_CALENDAR = "Calendar"
TAB_FINANCE = "Finance"
TAB_SETTINGS = "Settings"
TAB_PROGRESS = "ProgressLog"
TAB_AUDIT = "AuditLog"

# Books columns
BOOKS_COLS = [
    "ชื่อเรื่อง", "หมวดหมู่", "QC", "สถานะ",
    "ตอนปัจจุบัน", "เป้าหมาย", "ภาพปก", "หมายเหตุ",
    "ลิงก์อ่าน", "ลิงก์ต้นฉบับ", "เรื่องย่อ", "ลิงก์ PDF"
]

# Finance columns
FINANCE_COLS = ["วันที่", "ชื่อเรื่อง", "แพลตฟอร์ม", "ยอดดิบ", "หักแพลตฟอร์ม (17%)", "ยอดสุทธิ"]

# Calendar columns
CALENDAR_COLS = ["วันที่", "ชื่อเรื่อง", "ตอนที่"]

# Status options
STATUS_CHOICES = ["กำลังอัปเดต", "จบแล้ว", "พักการแปล"]

# Platform fee rate
PLATFORM_FEE_RATE = 0.17
