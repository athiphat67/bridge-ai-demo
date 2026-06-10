# `scripts/` — เครื่องมือสำหรับ dev (รันในเครื่องนี้)

ต่างจาก `data/prep_scripts/` (สคริปต์ของ Namthip ที่รันบนเครื่องเธอ) — สคริปต์ในนี้เป็นส่วนหนึ่งของ
demo app นี้โดยตรง และใช้ `backend/.venv` เดียวกับ backend

## `build_demo_data.py`

แปลง `data/processed/` (ภาพ 256x256 + `dataset_labels.csv` จาก Namthip) ให้เป็น
`backend/app/data/metadata.json` + `backend/app/data/samples/*.png` ตามรูปแบบใน
[`DATA_CONTRACT.md`](../DATA_CONTRACT.md):

- คัดเลือก 4 เคสสาธิต (Normal / Low / Medium / High) — แก้ไขรายการ/เคสได้ใน `CASES` ในไฟล์นี้
- แปลงกรอบ bounding box จาก pixel (256x256) → สัดส่วน 0–1 (`bar_box`) + เผื่อขอบ (`BOX_PAD_PX`)
- อัปสเกลภาพเป็น 768px ให้คมตอนอัดวิดีโอ

### รัน

```bash
cd "brige ai"
backend/.venv/bin/python scripts/build_demo_data.py
```

รันซ้ำได้เสมอ (idempotent) — เขียนทับ `metadata.json` และไฟล์ภาพเดิมทุกครั้ง

### เมื่อไหร่ต้องรันใหม่

- ได้ `dataset_labels.csv` หรือภาพชุดใหม่จาก Namthip → วางทับใน `data/processed/` แล้วรันสคริปต์นี้ใหม่
- อยากเปลี่ยน/เพิ่มเคสตัวอย่างที่โชว์ใน sample picker → แก้ list `CASES` แล้วรันใหม่
