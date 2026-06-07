# Bridge AI Demo — Architecture (v2, build-ready)

> เป้าหมายเดียวของ demo นี้: **อัดวิดีโอ/แคปหน้าจอไปแปะใน Proposal (ส่ง 26 มิ.ย.)**
> ไม่ใช่ระบบจริง ไม่มีการเทรนโมเดล — เป็น **mock facade** ที่ขับด้วย label ที่ Namthip เตรียมให้
> (ยืนยันจาก Namthip: "ทำหน้ากากเดโม่ ไว้สำหรับอัดคลิป ไม่ต้องเอา 100%")

---

## 0. Requirement ที่เคลียร์แล้ว (จาก KneeGrowth-AI.pdf + LINE)

**ต้องโชว์บนหน้าจอ 3 ส่วน:**
1. 🖼️ **ภาพ X-ray + Bounding Box/Heatmap** ไฮไลต์ตรง Growth Plate
2. 🔢 **Key Metric**: `Physeal Plate Damage = XX%` (ตัวเลข hero) + Risk badge (Low/Med/High)
3. 📈 **Growth Prediction** (กราฟ 1/3/5 ปี) — อยู่ใน **พาร์ทแยกต่างหาก** ไม่รวมกับภาพ

**Input ที่หมอกรอก:** age, bone age, gender, weight, height, location (Medial/Lateral dropdown), medical history
**Input จาก label ภาพ:** bar_area %, ตำแหน่ง bar, Salter-Harris grade (มาจากไฟล์ Namthip → ดู `DATA_CONTRACT.md`)
**Data:** synthetic + label ภายในวันอาทิตย์ / open data เป็น fallback ได้

---

## 1. หลักการออกแบบ (ทำไม build ง่าย)

| หลักการ | ผล |
|--------|-----|
| **Metadata-driven mock** — ไม่มี ML, อ่านผลจาก label | ตัด pipeline เทรนทั้งหมด เหลือแค่ math + วาดภาพ |
| **1 endpoint หลัก** `POST /api/analyze` คืนทุกอย่างใน response เดียว | frontend เรียกครั้งเดียว ได้ครบ 3 ส่วน |
| **Single-screen dashboard** (ซ้าย=ฟอร์ม, ขวา=ผล) | คลิกเดียวผลเด้ง → เหมาะกับอัดวิดีโอ |
| **Preloaded sample cases** Low/Med/High | safety net: คลิกเคสตัวอย่าง = ภาพออกเป๊ะแน่นอนตอนถ่าย |
| **Deterministic** (input เดียวกัน → ผลเดิมเสมอ) | อัดซ้ำได้ ไม่สุ่ม |

---

## 2. สิ่งที่ "ตัดออก" จาก v1 + เหตุผล

| ตัดออก | เหตุผล |
|--------|--------|
| ❌ SQLite + History page (search/filter/delete) | ไม่อยู่ใน requirement เลย — วิดีโอไม่ต้องใช้ เพิ่ม build surface เปล่าๆ |
| ❌ PDF export (reportlab) | deliverable คือ **วิดีโอ** ไม่ใช่ PDF |
| ❌ Multi-step wizard form | ฟอร์มหน้าเดียวเร็วกว่า + อัดวิดีโอลื่นกว่า |
| ❌ Risk scoring จาก gender/height (สูตรเดิมใน v1) | scoring จริงอิงสูตรใน PDF (bar area + location + age + bias) |
| 🔄 **react-scripts (CRA) → Vite** | CRA เลิก maintain + พังบน Node 17+ (เครื่องนี้ Node 25); Vite เร็วกว่า เซ็ตง่ายกว่า |

> ทั้งหมดยกไปเป็น "Future / หลังส่ง proposal" — ถ้าอยากเก็บ DB/PDF ไว้ทีหลังค่อยเติม

---

## 3. โครงสร้าง Backend (FastAPI)

```
backend/app/
├── main.py              # FastAPI + CORS + serve static + include routers
├── config.py            # ค่าคงที่: risk thresholds, สี heatmap, paths
├── schemas.py           # Pydantic: ClinicalInput, AnalysisResult
├── routers/
│   ├── analyze.py       # POST /api/analyze  ← endpoint หลัก
│   └── samples.py       # GET  /api/samples  ← list เคสตัวอย่าง
├── services/
│   ├── metadata.py      # โหลด metadata.json, lookup ด้วย filename
│   ├── scoring.py       # mock: damage%, risk score→level, salter-harris, varus/valgus
│   ├── growth.py        # กราฟ prediction (Hueter-Volkmann / tethering — สูตรใน PDF)
│   └── visualize.py     # วาด box+heatmap ลงภาพ → base64 PNG (Pillow+NumPy)
└── data/
    ├── samples/         # ภาพจาก Namthip
    └── metadata.json    # ตาม DATA_CONTRACT.md
```

### `POST /api/analyze` — request รับได้ 2 แบบ
multipart form: **(ก)** `sample_id` (เลือกจาก sample picker — ทางหลัก) **หรือ** **(ข)** `image` ไฟล์อัปโหลด + ฟิลด์ clinical
ต้องมาอย่างใดอย่างหนึ่ง: ถ้ามี `sample_id` → ใช้ clinical/label จาก metadata; ถ้าเป็นไฟล์อัปโหลด → ใช้ clinical จากฟอร์ม + match label ด้วย filename (ไม่เจอ → fallback ค่ากลาง/heatmap กึ่งกลาง)

### `POST /api/analyze` — response เดียวป้อนครบ 3 ส่วน
```jsonc
{
  "overlay_image": "data:image/png;base64,...",  // ส่วน 1: X-ray + box + heatmap + ป้าย "XX%"
  "damage_percent": 62,                           // ส่วน 2: ตัวเลข HERO
  "risk_level": "High",                           // ส่วน 2: badge Low/Med/High (ไม่โชว์เลข % ซ้อน)
  "salter_harris": "III",
  "bend_direction": "Varus",                      // medial→varus, lateral→valgus
  "growth_prediction": {                          // ส่วน 3: กราฟ
    "years": [0, 1, 3, 5],
    "leg_length_diff_mm": [0, 4, 11, 18],
    "angular_deg": [0, 3, 8, 14]
  },
  "factors": [                                    // "ทำไมได้คะแนนนี้"
    { "label": "Bar Area 62%", "impact": "high" },
    { "label": "ตำแหน่ง Medial", "impact": "high" },
    { "label": "อายุ 6 ปี (กระดูกยังโตอีกมาก)", "impact": "high" }
  ]
}
```

> ⚠️ **1 ตัวเลข hero เท่านั้น**: damage% ตัวใหญ่ + risk เป็น badge สี — ไม่โชว์ 2 % ตัวโตแข่งกัน (กันคนดูงง)

### Mock logic (สรุป — รายละเอียดสูตรอยู่ใน `scoring.py`/`growth.py`)
- `damage_percent` = `bar_area_percent` จาก label ตรงๆ
- `risk_level`: thresholds **Low < 40 ≤ Medium < 70 ≤ High** (ปรับได้ใน `config.py`)
- `bend_direction`: medial → Varus, lateral → Valgus
- `growth_prediction`: ใช้สูตรใน PDF เป็นฟังก์ชัน monotonic ง่ายๆ
  - `G = G0·(1 − β·σ)` (Hueter-Volkmann) → growth rate ฝั่งที่โดน bar ลดลง
  - `leg_length_diff(t) ≈ (G0 − G_damaged)·t`
  - `angular(t) ≈ Δθ·t` โดย `Δθ ∝ G_undamaged / d`
  - (ค่าพวกนี้ทำให้กราฟดู "อิงงานวิจัย" ตาม proposal — ไม่ต้องแม่นจริง)

---

## 4. โครงสร้าง Frontend (Vite + React + Tailwind)

```
frontend/src/
├── api/client.js              # axios: analyze(), getSamples()
├── components/
│   ├── ClinicalForm.jsx       # ฟอร์ม input + dropdown Medial/Lateral
│   ├── SamplePicker.jsx       # thumbnail Low/Med/High (safety net การถ่าย)
│   ├── XrayOverlay.jsx        # ภาพ + box/heatmap + ป้าย "Damage XX%"
│   ├── RiskBadge.jsx          # badge สี Low(เขียว)/Med(เหลือง)/High(แดง)
│   ├── FactorList.jsx         # "ทำไมได้คะแนนนี้"
│   └── GrowthChart.jsx        # recharts line chart 1/3/5 ปี
├── sections/
│   ├── AnalysisSection.jsx    # พาร์ท 1: ภาพ + damage% + risk + factors
│   └── GrowthPredictionSection.jsx  # พาร์ท 2 (แยก): กราฟ
├── pages/Dashboard.jsx        # ซ้าย ClinicalForm | ขวา ผลลัพธ์
├── App.jsx, main.jsx, index.css
```

- เพิ่ม dep: `recharts` (กราฟ declarative ง่าย), เปลี่ยน build เป็น `vite`
- **Layout การถ่าย:** หน้าเดียว ซ้ายกรอกฟอร์ม → กด "วิเคราะห์" → ขวาเด้งผล → เลื่อนลงดู Growth Prediction
- UI ภาษาไทย (term เทคนิคคงอังกฤษ: Salter-Harris, BMI)

---

## 5. การ match ภาพ → label (หัวใจของ mock)
1. **Sample picker (หลัก, การันตี):** คลิก 1 ใน 3 เคส → backend รู้ filename แน่นอน → ภาพออกเป๊ะ
2. **Upload (รอง):** match ด้วย filename ใน metadata; ถ้าไม่เจอ → คำนวณ score จาก clinical input + วาง heatmap กลางภาพ (default) → ยังได้ผลที่ดูสมจริง

> ตอนอัดวิดีโอจริงให้ใช้ **sample picker** เป็นหลัก = ไม่มีพลาด

---

## 6. ลำดับ Build (milestone)

| # | งาน | เสร็จเมื่อ |
|---|-----|----------|
| 1 | **ส่ง DATA_CONTRACT.md ให้ Namthip** | วันนี้ (critical path) |
| 2 | Scaffold: Vite frontend + FastAPI routers/services (stub) | วันที่ 1 |
| 3 | Backend mock (scoring/growth/visualize) + 1 เคส hardcode | วันที่ 2 |
| 4 | Frontend dashboard ต่อ `/api/analyze` ครบ 3 ส่วน | วันที่ 3 |
| 5 | Polish Tailwind + 3 sample + Thai strings | วันที่ 4 |
| 6 | วาง data จริงจาก Namthip ลง `samples/` + `metadata.json` | เมื่อได้ (~อาทิตย์) |
| 7 | อัดวิดีโอ | ก่อน 26 มิ.ย. |

> milestone 2–5 ทำได้เลย **ไม่ต้องรอ data** เพราะ mock + sample เป็น self-contained

---

## 7. รันยังไง

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload          # :8000

# Frontend
cd frontend && npm install && npm run dev   # :5173 (Vite)

# หรือ
docker-compose up
```

---

## 8. Success Criteria (สำหรับวิดีโอ)
- [ ] เลือก/อัปโหลด X-ray แล้วกรอก clinical input ได้
- [ ] กดวิเคราะห์ → ภาพโชว์ box/heatmap ตรง growth plate + ป้าย "Damage XX%"
- [ ] Risk badge Low/Med/High โชว์สีถูก
- [ ] พาร์ท Growth Prediction โชว์กราฟ 1/3/5 ปี
- [ ] ครบ 3 เคส (Low/Med/High) ถ่ายได้ลื่น UI ไทยสวยพอลงเล่ม proposal

---

## 9. Future (หลังส่ง proposal — ไม่ทำตอนนี้)
DB + History, PDF export, โมเดล ML จริง (Branch A CV + Branch B tabular ตาม PDF), auth, multi-image
