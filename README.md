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
bridge-ai/
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
npm run up
```

- Backend API: http://localhost:8000  (docs: `/docs`)
- Frontend: http://localhost:5173

ถ้าต้องการ rebuild ใหม่ทั้งชุด:

```bash
npm run up:build
```

`Ctrl+C` จะหยุด `docker compose up` ให้อัตโนมัติ ไม่ต้องสั่ง `down` ทุกครั้ง

## Deploy to Vercel

This repo is a monorepo, so the simplest full deploy on Vercel is two projects:

1. `frontend/` as the React app
2. `backend/` as the FastAPI API

Frontend project:

1. Import the repo into Vercel.
2. Set `Root Directory` to `frontend`.
3. Keep the default build command: `npm run build`.
4. Keep the output directory: `dist`.
5. Set `VITE_API_URL` to the backend deployment URL.

Backend project:

1. Create a second Vercel project from the same repo.
2. Set `Root Directory` to `backend`.
3. Let Vercel detect FastAPI.
4. No build command is required; `api/index.py`, `.python-version`, and
   `vercel.json` are included.

If you are only a contributor, you can still deploy your own Vercel projects as long as your Git account can access the repo. If you want to deploy into someone else’s existing Vercel project, they need to add you to that Vercel team/project first.

## Development (Native)

### Backend

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload   # → http://localhost:8000
```

Real model mode is self-contained. C1/C2 weights live in
`backend/app/models/`; `bridge-ai-vision` is not required at runtime.
The deployment runtime uses ONNX models through OpenCV, without PyTorch.

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
  - Sample: form `mode=sample` + `sample_id`
  - Real: form `mode=real` + `image` (ไม่เกิน 4 MB) + ฟิลด์ clinical

## Architecture Decisions

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed design decisions and rationale.
