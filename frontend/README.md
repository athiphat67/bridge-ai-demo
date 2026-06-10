# `frontend/` — React + Vite + Tailwind dashboard

หน้าจอเดียว (single-screen dashboard): ซ้าย = เลือกเคส/กรอกฟอร์ม, ขวา = ผลลัพธ์ 3 ส่วน
เรียก backend ครั้งเดียวที่ `POST /api/analyze` แล้วโชว์ทุกอย่างจาก response เดียว

## โครงสร้าง

```
src/
├── main.jsx, App.jsx, index.css   # entry point
├── api/
│   └── client.js              # axios — getSamples(), analyze()
├── pages/
│   └── Dashboard.jsx           # layout หลัก: ฟอร์ม (ซ้าย) + ผลลัพธ์ (ขวา), state ทั้งหมดอยู่ที่นี่
├── components/
│   ├── SamplePicker.jsx        # เลือกเคสตัวอย่าง Normal/Low/Medium/High
│   ├── ClinicalForm.jsx        # ฟอร์ม clinical input (อายุ, เพศ, น้ำหนัก, ส่วนสูง, ตำแหน่ง bar)
│   ├── XrayOverlay.jsx         # แสดงภาพ overlay (box+heatmap) ที่ backend วาดมาให้แล้ว
│   ├── RiskBadge.jsx           # badge สี Low(เขียว)/Medium(เหลือง)/High(แดง)
│   ├── FactorList.jsx          # รายการ "ทำไมได้คะแนนนี้"
│   └── GrowthChart.jsx         # recharts line chart: leg-length diff + มุมโก่ง
└── sections/
    ├── AnalysisSection.jsx          # ส่วนที่ 1+2: ภาพ + damage% + risk + factors
    └── GrowthPredictionSection.jsx  # ส่วนที่ 3 (แยกต่างหาก): กราฟ growth prediction
```

## รัน

```bash
cd frontend
npm install        # ครั้งแรกเท่านั้น
npm run dev         # → http://localhost:5173
```

dev server proxy `/api/*` ไปที่ FastAPI `:8000` ให้อัตโนมัติ (ตั้งค่าใน `vite.config.js`)
ต้องรัน backend คู่กันด้วย — ดู [`../backend/README.md`](../backend/README.md)

## Build

```bash
npm run build    # → dist/
npm run preview  # serve dist/ ทดสอบ production build
```
