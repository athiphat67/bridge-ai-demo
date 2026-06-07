# Bridge AI Demo

A Medical AI demo application for bone X-ray analysis with risk scoring, developed for the Medical AI Awards submission.

> **Note:** นี่คือ **mock demo facade** สำหรับอัดวิดีโอ/แคปหน้าจอไปแปะ Proposal (ส่ง 26 มิ.ย.)
> ไม่มีการเทรนโมเดลจริง — ผลลัพธ์ขับด้วย label ที่ทีมเตรียมให้ ดู `ARCHITECTURE.md` + `DATA_CONTRACT.md`

## Features

- Upload / เลือกเคสตัวอย่าง X-ray + กรอก clinical input
- โชว์ Bounding Box / Heatmap ตรง Growth Plate + Key Metric `Physeal Plate Damage = XX%`
- Risk badge (Low / Medium / High)
- พาร์ท Growth Prediction: กราฟแนวโน้ม 1 / 3 / 5 ปี
- Thai language UI

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + Python (Pillow + NumPy สำหรับวาดภาพ)
- **Deployment**: Docker Compose

## Project Structure

```
bridge-ai-demo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── routers/      # analyze.py, samples.py
│   │   ├── services/     # metadata, scoring, growth, visualize
│   │   └── data/         # samples/ + metadata.json (ดู DATA_CONTRACT.md)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/ components/ sections/ pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── ARCHITECTURE.md       # การออกแบบ v2
├── DATA_CONTRACT.md      # รูปแบบไฟล์ที่ Namthip ส่งให้
├── docker-compose.yml
└── README.md
```

## Current Status

| ส่วน | สถานะ |
|------|-------|
| Backend (FastAPI mock: scoring / growth / visualize) | ✅ ทำงานครบ |
| Frontend (Dashboard + 3 ส่วนผลลัพธ์ + กราฟ) | ✅ ทำงานครบ |
| ภาพ X-ray จริงจากทีม | ⏳ รอ — ระหว่างนี้ backend สร้าง placeholder ให้อัตโนมัติ |
| Polish UI + อัดวิดีโอ | 🔜 |

demo รันได้เต็มรูปแบบแล้วด้วย placeholder — ดูแผนเต็มใน `ARCHITECTURE.md` §6

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
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Vite → http://localhost:5173
```

## API Endpoints

- `GET  /api/health`  - Health check
- `GET  /api/samples` - รายการเคสตัวอย่าง (Low / Medium / High)
- `POST /api/analyze` - วิเคราะห์ X-ray + clinical input → คืน overlay + damage% + risk + growth prediction
  - รับได้ 2 แบบ: form `sample_id` (เลือกเคสตัวอย่าง) **หรือ** `image` + ฟิลด์ clinical (อัปโหลดเอง)

## การวาง data จริงจากทีม

เมื่อได้ภาพ X-ray + label จาก Namthip (ตามรูปแบบใน `DATA_CONTRACT.md`):

1. วางไฟล์ภาพใน `backend/app/data/samples/` (ชื่อไฟล์ตรงกับ `metadata.json`)
2. อัปเดต `backend/app/data/metadata.json` ตาม contract (พิกัด `bar_box` เป็นสัดส่วน 0–1)
3. รีสตาร์ท backend — ใช้ได้ทันที ไม่ต้องแก้โค้ด

## Architecture Decisions

See `ARCHITECTURE.md` for detailed design decisions and rationale.
