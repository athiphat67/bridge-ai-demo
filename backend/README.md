# `backend/` — FastAPI mock API

API ตัวเดียว `POST /api/analyze` ที่คืนผลครบ 3 ส่วนของ demo (ภาพ overlay, damage% + risk badge,
growth prediction) โดยอ่านค่าจาก `app/data/metadata.json` แทนการรันโมเดล ML จริง
ดูเหตุผลการออกแบบเต็มๆ ที่ [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

## โครงสร้าง

```
app/
├── main.py              # สร้าง FastAPI app, CORS, mount routers
├── config.py            # ค่าคงที่ที่ tune ได้: risk thresholds, สี/ความเข้ม heatmap, paths
├── schemas.py           # Pydantic models (request/response contracts)
├── routers/
│   ├── analyze.py       # POST /api/analyze — endpoint หลัก
│   └── samples.py       # GET  /api/samples — รายการเคสตัวอย่างให้ sample picker
├── services/
│   ├── metadata.py       # โหลด/lookup metadata.json
│   ├── scoring.py         # damage% → risk score/level, Salter-Harris, varus/valgus
│   ├── growth.py           # คำนวณกราฟ growth prediction (1/3/5 ปี)
│   └── visualize.py        # วาด bounding box + heatmap ลงภาพ → base64 PNG
└── data/
    ├── metadata.json     # เคสตัวอย่าง (สร้างโดย ../../scripts/build_demo_data.py — ดู DATA_CONTRACT.md)
    └── samples/           # ไฟล์ภาพของแต่ละเคส
```

## รัน

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000
```

(ครั้งแรก ถ้ายังไม่มี `.venv`: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`)

- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## แก้ tuning โดยไม่ต้องแก้ logic

ค่าที่ปรับได้บ่อยอยู่ใน `app/config.py` ทั้งหมด: risk thresholds (Low/Medium/High),
สีและความเข้มของ heatmap/box

## เพิ่ม/แก้เคสตัวอย่าง

อย่าแก้ `app/data/metadata.json` หรือ `app/data/samples/` ตรงๆ — ไฟล์เหล่านี้ถูก generate โดย
`../scripts/build_demo_data.py` จาก `../data/processed/` ดู [`../scripts/README.md`](../scripts/README.md)
