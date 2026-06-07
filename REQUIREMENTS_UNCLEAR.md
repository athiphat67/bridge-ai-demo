# Requirements ที่ยังไม่เคลีย 🚩

## Output / Mock Logic

### 1. **Salter-Harris Grade (I-V)**
- ❓ ต้อง determine ยังไง?
- ❓ Mock logic ใช้พารามิเตอร์ไหน? (age? location? bar-area?)
- ❓ Display ที่ไหนใน UI? (results page ใช่ไหม)

### 2. **Physeal Bar Area %**
- ❓ ต้องให้ user input ไหม? (slider? numeric input?)
- ❓ Acceptable range คืออะไร? (0-100%?)
- ❓ เป็น primary driver ของ risk score ใช่ไหม?
- ❓ Default value ถ้า user ไม่ใส่?

### 3. **Varus / Valgus Direction**
- ❓ Determine ยังไง? (from bone location: medial=varus, lateral=valgus?)
- ❓ Display ที่ไหน? (in factor list? in report?)

### 4. **Risk Score Complete Formula**
- ❓ Bar area ① + Location ② + Age ③ + Gender/Weight/Height ④ → Risk %?
- ❓ Exact weights/multipliers?
- ❓ Example: age 6, medial, 60% bar → risk score คือเท่าไร?
- ❓ Risk thresholds: Low (<?) / Medium (?-?) / High (>?)

### 5. **Predictive Graph (1yr/3yr/5yr projection)**
- ❓ ทำนาย อะไร? 
  - Leg-length difference (mm)?
  - Angular deformity (degrees)?
  - Both?
- ❓ Axes labels?
- ❓ Units?
- ❓ Example data: age 6, high-risk → 1yr=?mm, 3yr=?mm, 5yr=?mm

## Input / Form

### 6. **Clinical Input Fields - Complete List**
- ✅ Age (ปี)
- ✅ Gender (ชาย/หญิง)
- ✅ Weight (kg)
- ✅ Height (cm)
- ✅ Bone Location (Medial/Lateral)
- ❓ Physeal Bar Area % (see #2)
- ❓ Other fields? (side of body? affected bone name? patient ID?)
- ❓ Required vs optional fields?
- ❓ Input validation ranges? (age 0-18? weight 5-100kg?)

## Sample Data

### 7. **X-ray Sample Images**
- ❓ Namthip เตรียมให้ยัง? (when?)
- ❓ ถ้ายังไม่ได้ เราใช้ open data จากไหน?
  - Radiopaedia?
  - EuroRad?
  - MURA dataset?
- ❓ ต้องกี่ภาพ? (3-5 ตัวอย่าง?)
- ❓ Image format/size requirements? (JPG/PNG? max 10MB?)

## Visualization

### 8. **Heatmap Specifications**
- ❓ Color scheme? (red→yellow→green? or jet?)
- ❓ Center location on image? (growth plate region? how to determine?)
- ❓ Intensity/opacity ที่ drive โดย what? (bar-area %?)
- ❓ Heatmap extent (cover whole image or localized?)
- ❓ Blur/sigma ของ Gaussian?

## Report / Export

### 9. **PDF Report - Exact Structure**
- ❓ Sections ต้องมี:
  - ① Title/Header (Thai?)
  - ② Clinical input table
  - ③ X-ray + heatmap overlay
  - ④ Risk score display + Salter-Harris + varus/valgus
  - ⑤ Predictive graph
  - ⑥ "Why this score?" factors list
  - ⑦ Recommendations/Clinical notes
  - ⑧ Timestamp
  - ⑨ Other?
- ❓ Logos/branding ต้องใส่ไหม? (Bridge AI logo?)
- ❓ Page size (A4? Letter?)
- ❓ Footer/header?

### 10. **Export Formats**
- ❓ PDF เท่านั้น? หรือต้อง PNG/Excel ด้วย?
- ❓ Filename format? (patient_{id}_{date}.pdf?)

## History / Database

### 11. **History Features**
- ❓ ต้อง search/filter ไหม? (by date? by patient age?)
- ❓ ต้อง delete ไหม? (soft delete or hard?)
- ❓ ต้อง edit ไหม?
- ❓ Display ทั้งหมด default? หรือ paginate?
- ❓ Patient ID / name field ต้องเก็บไหม?

## UI / Language

### 12. **Thai Language - Complete UI Strings**
- ❓ Button labels?
- ❓ Form labels?
- ❓ Error messages?
- ❓ Risk level descriptions? (e.g., "ความเสี่ยงสูง" vs "High Risk"?)
- ❓ Terminology (e.g., "Growth Plate" → "แผ่นกำลังเจริญเติบโต"?)

### 13. **Demo Scenario - What to Screen Record?**
- ❓ ต้อง demo cases คือเท่าไร? (Low/Medium/High risk? 1 case or 3?)
- ❓ Patient details (age, gender, bar-area) ที่ demo?
- ❓ Exact click flow?
- ❓ Show history page ด้วยไหม?

## Technical

### 14. **Thai Font for PDF**
- ❓ ใช้ Sarabun font จาก Google Fonts? (ใช่ๆ)
- ❓ Need Bold variant ด้วยไหม? (ใช่ๆ)

### 15. **Server-side Predictive Graph Rendering**
- ❓ Frontend Recharts + screenshot ไหม?
- ❓ หรือ render server-side (matplotlib/plotly) เป็น image → embed ใน PDF?
- ❓ เลือกอย่างไหนหลังจาก align outputs?

---

## Summary for Namthip

**ต้องถาม Namthip:**
- Salter-Harris grade mock logic ใช้พารามิเตอร์ไหน?
- Physeal Bar Area % range + user input ไหม?
- Risk score formula (bar-area weight เท่าไร?)
- Varus/valgus determination
- Predictive graph: ทำนาย อะไร (leg-length/angular)? units?
- Sample X-ray images: when ready? หรือใช้ open data?
- Clinical input complete checklist
- Risk level thresholds (Low/Medium/High cutoffs)
- PDF report exact sections + branding

**เราเตรียมเองได้:**
- Thai UI strings (เลือก terminology)
- Demo scenarios
- Heatmap visualization specs
- History features scope

---

## Decision Dependencies

```
Salter-Harris formula (1)
    ↓
Risk Score Formula (4)
    ↓
Frontend Step 2 form (6)
    ↓
Backend scoring.py
    ↓
Results visualization (8) + PDF (9)
    ↓
Predictive graph (5) → if server-side (15)
```

**Critical path:** 1 → 4 → ให้ได้ก่อนเริ่ม Phase 1 backend
