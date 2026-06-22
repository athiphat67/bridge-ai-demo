# `docs/` — เอกสารอ้างอิง (ไม่ใช่ source code)

เอกสารในโฟลเดอร์นี้เป็น **ไฟล์อ้างอิง/บริบทของโครงการ** ไม่เกี่ยวกับการรันแอป
ดูเอกสารออกแบบระบบ (architecture, data contract) ได้ที่ root: [`ARCHITECTURE.md`](../ARCHITECTURE.md), [`DATA_CONTRACT.md`](../DATA_CONTRACT.md)

## โครงสร้าง

```
docs/
├── proposal/    # เอกสารทางการของการประกวด (Bridge AI / DH Innovation Awards)
│                 — โจทย์, แนวทางการเขียน abstract/presentation, template proposal
│
└── team-notes/  # บันทึก/ไอเดียภายในทีม
    ├── KneeGrowth-AI.pdf         — ที่มาของสูตร scoring/growth ที่ใช้ใน
    │                               backend/app/services/scoring.py และ growth.py
    └── [LINE]Bridge Submit 2026.txt — สรุปแชทไลน์ทีม (requirement clarifications)
```

## ใช้ตอนไหน

- **proposal/** — อ่านก่อนเขียน/แก้ proposal หรือ presentation เพื่อให้ตรงรูปแบบที่กรรมการกำหนด
- **team-notes/** — อ่านถ้าต้องแก้สูตร mock scoring/growth ใน backend, เพื่อเข้าใจที่มาของตัวเลข
  (ดู `KneeGrowth-AI.pdf` ประกอบ docstring ใน `backend/app/services/`)
- **deploy.md** — วิธีรัน local และ deploy บน Vercel สำหรับ frontend/backend
