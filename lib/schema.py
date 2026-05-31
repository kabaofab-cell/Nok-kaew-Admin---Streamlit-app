"""Google Sheets schema definition for Nok-kaew Admin."""

WORKSHEETS = {
    "novels": {
        "headers": ["id", "title", "category", "cover_url", "qc", "status", "created_at"],
        "frozen_rows": 1,
    },
    "work_queue": {
        "headers": ["id", "date", "novel_id", "title", "task", "qc", "status", "note"],
        "frozen_rows": 1,
    },
    "income": {
        "headers": ["id", "date", "platform", "qc", "novel_id", "title", "amount"],
        "frozen_rows": 1,
    },
    "categories": {
        "headers": ["name"],
        "frozen_rows": 1,
        "default_data": [["ตัวอักษร"], ["ตัวร้อน"], ["ปีศาจ"], ["ศาสตร์แปลก"], ["ดำหน้า"]],
    },
    "platforms": {
        "headers": ["name"],
        "frozen_rows": 1,
        "default_data": [["Wattpad"], ["Royal Road"], ["Webnovel"], ["Tapas"]],
    },
    "qc": {
        "headers": ["name"],
        "frozen_rows": 1,
        "default_data": [["ตอง"], ["ตาว"]],
    },
    "settings": {
        "headers": ["key", "value"],
        "frozen_rows": 1,
        "default_data": [
            ["user1_name", "ตอง"],
            ["user2_name", "ตาว"],
            ["user1_split", "50"],
            ["user2_split", "50"],
            ["shop_name", "Nok-kaew"],
        ],
    },
}

STATUS_CHOICES = ["ร่าง", "กำลังอัปเดต", "จบแล้ว"]
TASK_CHOICES = ["แก้นิยาย", "QC", "อื่นๆ"]
