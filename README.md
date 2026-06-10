# Bridge AI Demo

A Medical AI demo application for pediatric knee growth-plate (physis) X-ray analysis with
risk scoring, developed for the Medical AI Awards submission.

> **Note:** นี่คือ **mock demo facade** สำหรับอัดวิดีโอ/แคปหน้าจอไปแปะ Proposal (ส่ง 26 มิ.ย.)
> ไม่มีการเทรนโมเดลจริง — ผลลัพธ์ขับด้วย label จากภาพ X-ray จริงที่ทีมเตรียมให้
> ดู [`ARCHITECTURE.md`](ARCHITECTURE.md) + [`DATA_CONTRACT.md`](DATA_CONTRACT.md)

## Features

- เลือกเคสตัวอย่าง X-ray (Normal / Low / Medium / High risk) หรืออัปโหลดเอง + กรอก clinical input
- โชว์ Bounding Box / Heatmap ตรง Growth Plate + Key Metric `Physeal Plate Damage = XX%`
- Risk badge (Low / Medium / High)
- พาร์ท Growth Prediction: กราฟแนวโน้ม 1 / 3 / 5 ปี (leg-length difference + มุมโก่ง)
- Thai language UI

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + Python (Pillow + NumPy สำหรับวาดภาพ)
- **Deployment**: Docker Compose

## Project Structure

```
brige ai/
├── backend/        # FastAPI mock API — ดู backend/README.md
├── frontend/        # React + Vite dashboard — ดู frontend/README.md
├── data/             # X-ray ดิบ + ที่เตรียมแล้วจาก Namthip — ดู data/README.md
├── scripts/           # build_demo_data.py — แปลง data/ → backend/app/data/ — ดู scripts/README.md
├── docs/               # เอกสารอ้างอิง: proposal/ + team-notes/ — ดู docs/README.md
├── ARCHITECTURE.md      # การออกแบบระบบ (v2)
├── DATA_CONTRACT.md       # รูปแบบไฟล์ data ที่ backend อ่าน
├── REQUIREMENTS_UNCLEAR.md # คำถามช่วงต้นโปรเจกต์ (ส่วนใหญ่ตอบแล้วใน ARCHITECTURE.md v2)
├── docker-compose.yml
└── README.md
```

แต่ละโฟลเดอร์หลักมี `README.md` อธิบายไฟล์ข้างในและวิธีใช้ของตัวเอง — เริ่มอ่านจากที่นั่นถ้าจะแก้ส่วนนั้น

## Current Status

| ส่วน | สถานะ |
|------|-------|
| Backend (FastAPI mock: scoring / growth / visualize) | ✅ ทำงานครบ |
| Frontend (Dashboard + 3 ส่วนผลลัพธ์ + กราฟ) | ✅ ทำงานครบ |
| ภาพ X-ray จริงจากทีม (Namthip) | ✅ รวมเข้า demo แล้ว — 4 เคส (Normal/Low/Medium/High) |
| Polish UI + อัดวิดีโอ | 🔜 |

## Quick Start (Docker)

```bash
docker-compose up
```

- Backend API: http://localhost:8000  (docs: `/docs`)
- Frontend: http://localhost:5173

## Development (Native)

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload   # → http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Vite → http://localhost:5173
```

## API Endpoints

- `GET  /api/health`  - Health check
- `GET  /api/samples` - รายการเคสตัวอย่าง (Normal / Low / Medium / High)
- `POST /api/analyze` - วิเคราะห์ X-ray + clinical input → คืน overlay + damage% + risk + growth prediction
  - รับได้ 2 แบบ: form `sample_id` (เลือกเคสตัวอย่าง) **หรือ** `image` + ฟิลด์ clinical (อัปโหลดเอง)

## การอัปเดต data จากทีม

เมื่อได้ภาพ X-ray + label ชุดใหม่จาก Namthip:

1. วางไฟล์ลง `data/processed/` ตามโครงสร้างที่อธิบายใน [`data/README.md`](data/README.md)
2. รัน `backend/.venv/bin/python scripts/build_demo_data.py` — สร้าง `backend/app/data/metadata.json`
   + `backend/app/data/samples/` ใหม่ให้อัตโนมัติ (ดู [`scripts/README.md`](scripts/README.md))
3. รีสตาร์ท backend — ใช้ได้ทันที ไม่ต้องแก้โค้ด

## Architecture Decisions

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed design decisions and rationale.
