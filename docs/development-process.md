# กระบวนการพัฒนา Bridge AI Prototype

## บทนำ

เอกสารนี้อธิบายกระบวนการทำงานของทีม Bridge AI ตั้งแต่ขึ้นโครงสร้างโปรเจกต์จนได้โปรโตไทป์ที่ทำงานได้ และวางแผนการพัฒนาต่อสำหรับการแข่งขัน BRIDGE-AI Summit 2026 (Digital Health Innovation Awards) ในสาขา Medical AI Award

โปรเจกต์ Bridge AI มีเป้าหมายเพื่อช่วยประเมินความเสี่ยงของเด็กที่ได้รับบาดเจ็บบริเวณ growth plate ของเข่า (physis) โดยรับภาพ X-ray ร่วมกับข้อมูลทางคลินิก แล้วแสดงผลการวิเคราะห์เป็น damage severity, risk level และ growth prediction ที่ 1, 3 และ 5 ปี

Repository ปัจจุบันประกอบด้วยสองส่วนหลัก:

1. **Demo Application** — เว็บแอปพลิเคชัน (React + FastAPI) ที่แสดง dashboard สำหรับวิเคราะห์ X-ray ขับเคลื่อนด้วย metadata จาก label ที่ทีมเตรียมไว้ ยังไม่มี ML model จริง
2. **Clinical Research Pipeline** — Python pipeline (`Working Prototype/knee_prognosis_pipeline.py`) ที่คำนวณ prognosis ด้วยสูตรทางคลินิกจริง (Hueter-Volkmann, WHO z-scores, Salter-Harris arrest risk)

เอกสารแบ่งเป็นสองส่วน: **ส่วนที่ 1** อธิบายกระบวนการพัฒนาที่เกิดขึ้นจริง และ **ส่วนที่ 2** วางแผนการพัฒนาระยะถัดไปสำหรับรอบ 2 ของการแข่งขันและต่อไป

---

## ส่วนที่ 1: กระบวนการพัฒนาที่ผ่านมา (Retrospective)

### 1. ทีมและบทบาท

| สมาชิก | บทบาทหลัก |
|--------|-----------|
| **Namthip** | เตรียมข้อมูล X-ray และข้อมูลทางคลินิก (Branch A Vision + Branch B Clinical Data), พัฒนา Clinical Research Pipeline (`knee_prognosis_pipeline.py`) |
| **Athiphat** | ขึ้นโครง monorepo, ออกแบบ architecture, พัฒนา backend (FastAPI), เขียน mock scoring/growth logic, deployment |
| **Purich** | ออกแบบ UI/UX, พัฒนา frontend (React + Tailwind CSS), redesign dashboard layout |

### 2. ขั้นตอนการพัฒนา

การพัฒนาดำเนินการระหว่างวันที่ 7–22 มิถุนายน 2569 (ประมาณ 15 วัน) แบ่งเป็น 6 ระยะ โดย Phase 2 และ Phase 3 ดำเนินการคู่ขนานกัน

#### Phase 1: ศึกษาปัญหาและวาง Requirements (ก่อน 7 มิ.ย.)

ทีมศึกษาปัญหาทางคลินิกเกี่ยวกับการบาดเจ็บของ growth plate ในเด็ก โดยเฉพาะ:

- การจำแนกประเภทรอยแตกแบบ Salter-Harris (Type I–IV)
- ผลกระทบต่อการเจริญเติบโตของกระดูก: Limb Length Discrepancy (LLD) และ Angular Deformity (Varus/Valgus)
- สูตรพยากรณ์การเจริญเติบโต: Hueter-Volkmann law, WHO growth reference, Geometric Tethering model
- ข้อจำกัดของวิธีปัจจุบัน: แพทย์ต้องประเมินจากประสบการณ์และการติดตามผู้ป่วยระยะยาว ไม่มีเครื่องมือช่วยพยากรณ์ล่วงหน้า

ผลลัพธ์ของระยะนี้:

- ข้อกำหนดของ prototype: ระบบต้องรับ X-ray + clinical input แล้วแสดง damage severity, risk level และ growth prediction
- เอกสารอ้างอิงทางการแพทย์ (เก็บไว้ใน `data/References/`)
- Checklist คำถามที่ต้องตอบก่อนพัฒนา (`REQUIREMENTS_UNCLEAR.md`)

#### Phase 2: เตรียมข้อมูล — Namthip (ดำเนินการคู่ขนานกับ Phase 3)

Namthip เตรียมข้อมูลทั้งหมดสำหรับระบบ แบ่งเป็นสองสาย:

**Branch A — Vision (ข้อมูลภาพ X-ray)**

- รวบรวมภาพ X-ray ข้อเข่าเด็ก: 37 ภาพปกติ (แยกตามอายุ 2–17 ปี) และ 18 ภาพ Salter-Harris fracture (Type I–IV)
- จัดระเบียบเป็นชุดข้อมูล CycleGAN (256×256 px) แบ่ง train/test 85:15
- สร้างเครื่องมือ annotation ด้วย OpenCV GUI (`annotate_physis.py`) เพื่อวาด bounding box ของ physis ได้ 92 records
- สร้าง data augmentation script (flip, rotation, contrast) เพื่อเพิ่มจำนวนภาพ

**Branch B — Clinical Data (ข้อมูลทางคลินิก)**

- สร้างข้อมูลผู้ป่วยสังเคราะห์ 1,000 ราย ด้วย `synthetic_bias_generator.py`
- ครอบคลุม: bone age, fusion stage, physeal bar area, pathology codes (ICD-10), medication modifiers
- ใช้ clinical bias weights แยกตามระดับความรุนแรง (Critical 0.70 ถึง Baseline 1.00)
- รวมตาราง WHO growth reference (BMI-for-age, Weight-for-height z-scores)

รายละเอียดเต็มอยู่ใน [`data/README.md`](../data/README.md)

#### Phase 3: พัฒนา Clinical Research Pipeline — Namthip (ดำเนินการคู่ขนานกับ Phase 2)

Namthip พัฒนา pipeline ที่คำนวณ prognosis ด้วยสูตรทางคลินิกจริง (`Working Prototype/knee_prognosis_pipeline.py`) ประกอบด้วย:

- **อ่านข้อมูล X-ray bounding box** จาก annotation ที่เตรียมไว้ใน Branch A
- **อ่านข้อมูลคลินิก** จาก synthetic clinical biases ใน Branch B
- **คำนวณ BMI z-score** จากตาราง WHO reference
- **คำนวณ growth prediction** ด้วยสูตร Hueter-Volkmann: `G = G₀ × (1 − β × σ)`
- **ประเมิน Salter-Harris arrest risk** ตาม base risk ของแต่ละ type
- **คำนวณ fusion stage multiplier** (Stage I = 1.00, Stage II = 0.50, Stage III = 0.00)
- **ปรับค่าด้วย pathology weights** ตามโรคร่วมและยาที่ใช้
- **พยากรณ์ LLD และ Angular Deformity** ที่ 1, 3 และ 5 ปี

Pipeline นี้เป็นหัวใจของ logic ทางคลินิกที่ demo app จะต้องนำไป integrate ในระยะถัดไป

#### Phase 4: ขึ้นโครง Demo Application — Athiphat (7 มิ.ย.)

Athiphat ขึ้นโครงสร้างโปรเจกต์เป็น monorepo ประกอบด้วย:

- **โครงสร้าง monorepo**: `frontend/`, `backend/`, `data/`, `scripts/`, `docs/`
- **Backend (FastAPI)**: mock API ที่ขับเคลื่อนด้วย metadata จาก label ไม่ใช่ ML model
  - `POST /api/analyze` — รับ X-ray + clinical input แล้วคืน overlay, damage%, risk level, growth prediction
  - `GET /api/samples` — รายการเคสตัวอย่าง (Normal / Low / Medium / High risk)
  - Mock scoring logic (`services/scoring.py`): คำนวณ risk score จาก bar_area, age, location, medical history
  - Mock growth logic (`services/growth.py`): พยากรณ์ LLD และ angular deformity ด้วยสูตร Hueter-Volkmann แบบ simplified
  - Visualization service (`services/visualize.py`): วาด bounding box และ heatmap บนภาพ X-ray
- **Frontend (React + Vite + Tailwind CSS)**: โครง dashboard เบื้องต้น
- **Docker Compose**: สำหรับรันทั้งระบบด้วยคำสั่งเดียว
- **Build script** (`scripts/build_demo_data.py`): แปลงข้อมูลจาก `data/` เป็นรูปแบบที่ backend อ่านได้

การตัดสินใจสำคัญในระยะนี้:

- เลือก **metadata-driven approach** แทนการ train model จริง เพราะเป้าหมายแรกคือได้ demo ที่โชว์ workflow ครบสำหรับการอัดวิดีโอ/แคปหน้าจอ ประกอบ proposal (deadline 26 มิ.ย.)
- เลือก **monorepo** เพื่อให้ทุกคนในทีมทำงานใน repository เดียว ลดปัญหาการ sync ระหว่าง repos
- ใช้ **mock scoring formula ที่อิงสูตรจริง** (Hueter-Volkmann) แม้จะ simplified แต่ให้ผลที่สมเหตุสมผลทางคลินิก

#### Phase 5: พัฒนา UI/UX — Purich (10–15 มิ.ย.)

Purich พัฒนา frontend ผ่าน branch `purichdev` โดยทำงานผ่าน Pull Request:

- **PR #1 (13 มิ.ย.)**: ออกแบบ UI ใหม่ทั้งหมด — glassmorphism design, light/dark theme toggle, ปรับ layout components และ sections ให้สมดุล
- **PR #2 (15 มิ.ย.)**: ปรับ dashboard layout ให้ compact ขึ้น, ปรับ card balance
- **PR #3 (15 มิ.ย.)**: รวม BoneDirectionGraphic component เข้ากับ dashboard ใหม่, อัพเดท UI requirements

ผลลัพธ์ของ UI ประกอบด้วย:

- **Input Section**: เลือกเคสตัวอย่าง (Normal/Low/Medium/High) หรืออัปโหลด X-ray เอง + กรอก clinical input (อายุ, เพศ, น้ำหนัก, ส่วนสูง, ตำแหน่ง, ประวัติยา)
- **Analysis Section**: แสดง X-ray overlay (bounding box + heatmap), Physeal Plate Damage %, Risk badge, Salter-Harris classification, contributing factors
- **Prediction Section**: กราฟแนวโน้ม LLD (mm) และ Angular Deformity (°) ที่ 1/3/5 ปี, Growth probability (Varus/Valgus/Arrest), Remaining growth %, BoneDirectionGraphic แสดงทิศทางการเบี้ยว

#### Phase 6: Integration, Polish และ Deploy — Athiphat + Purich (22 มิ.ย.)

ระยะสุดท้ายก่อน deadline ส่ง proposal:

- **PR #4**: แก้ไข UI layout, ทำให้ภาษาสม่ำเสมอ, แก้ bug ใน backend scoring logic
- **PR #5**: ปรับ deployable configuration
- **PR #6**: แปล UI เป็นภาษาอังกฤษ, เพิ่มการแสดงค่า BMI
- **PR #7**: แก้ไข local proxy และ deployment API base URL, เขียนเอกสาร

Deploy ขึ้น Vercel:

- Frontend: deploy เป็น React app (root directory: `frontend/`)
- Backend: deploy เป็น FastAPI app (root directory: `backend/`)
- ตั้งค่า `VITE_API_URL` ให้ frontend ชี้ไปยัง backend URL

### 3. สถานะปัจจุบัน

| ส่วน | สถานะ | รายละเอียด |
|------|-------|-----------|
| Demo App — Backend | ✅ ทำงานครบ | Mock API: scoring, growth prediction, visualization |
| Demo App — Frontend | ✅ ทำงานครบ | Dashboard ครบ 3 ส่วน: Input, Analysis, Prediction |
| ข้อมูล X-ray (Namthip) | ✅ เสร็จสมบูรณ์ | 55 ภาพ (37 ปกติ + 18 fracture), 92 bounding box annotations |
| ข้อมูล Clinical (Namthip) | ✅ เสร็จสมบูรณ์ | 1,000 synthetic records, WHO z-score tables |
| Clinical Research Pipeline | ✅ ทำงานได้ | `knee_prognosis_pipeline.py` คำนวณ prognosis จริง |
| Deployment (Vercel) | ✅ deploy แล้ว | Frontend + Backend แยก project |
| ML Vision Model | ❌ ยังไม่ได้เริ่ม | ยังใช้ label-based overlay ไม่ใช่ model inference |
| Database / Case History | ❌ ยังไม่มี | ยังไม่มี persistent storage, ทุก session เริ่มใหม่ |
| Pipeline Integration | ❌ ยังไม่ได้เชื่อม | Clinical pipeline ยังแยกจาก demo app |

สิ่งที่ demo app ทำได้ตอนนี้: โชว์ workflow ครบตั้งแต่เลือก/อัปโหลด X-ray → กรอก clinical input → แสดงผลวิเคราะห์ แต่ผลลัพธ์ขับเคลื่อนด้วย metadata ที่ label ไว้ล่วงหน้า ไม่ได้มาจาก ML model หรือ clinical pipeline จริง

สิ่งที่ clinical research pipeline ทำได้: คำนวณ prognosis จากข้อมูล X-ray bounding box + clinical biases ด้วยสูตรทางคลินิกจริง แต่ยังรันแยกเป็น standalone Python script ยังไม่ได้เชื่อมกับ demo app

---

## ส่วนที่ 2: แผนการพัฒนาระยะถัดไป (Forward Plan)

### 4. บริบทและเป้าหมาย

การแข่งขัน BRIDGE-AI Summit 2026 มี 4 รอบ:

| รอบ | เนื้อหา | จำนวนทีม |
|-----|---------|---------|
| รอบ 1 | คัดจาก Abstract | เลือก 90 ทีม |
| รอบ 2 | จัดแสดงผลงานเป็นบูธ ณ สถานที่จัดงาน (20–21 ก.ค.) | เลือก 30 ทีม |
| รอบ 3 | นำเสนอบนเวที (On-stage Pitch Presentation) | เลือก 8 ทีม |
| รอบ 4 | คัดเลือก Grand Prize | 2 รางวัล |

เกณฑ์การประเมิน:

1. **Innovation Excellence** — ความโดดเด่นของนวัตกรรม
2. **Clinical & System Impact** — ผลกระทบทางคลินิกและระบบสุขภาพ
3. **Scalability & Sustainability** — ความยั่งยืนและขยายผลได้

สำหรับระดับ Prototype/MVP กรรมการจะพิจารณาจาก Performance, Validation results, ผลลัพธ์ที่วัดได้ชัดเจน และความเป็นไปได้ในการขยายผล

**เป้าหมายของแผนนี้**: พัฒนาระบบให้เป็น prototype จริงที่ทำงานได้ ไม่ใช่แค่ facade — โดยวางรากฐานที่แข็งแรงพอสำหรับ **ทุกรอบของการแข่งขัน** ไม่ใช่ทำ fast path ให้ผ่านรอบ 2 แล้วต้องมาเริ่มใหม่ตอนเข้ารอบ 3

หลักการวางแผน:

- ทุก phase ต้อง **buildable ภายในเวลาจำกัด** แต่ไม่ตัด corner ที่จะทำให้ต้อง rewrite ทีหลัง
- สถาปัตยกรรมที่เลือกต้อง **รองรับการเติบโต** ตั้งแต่รอบ 2 (demo ที่บูธ) ถึงรอบ 3 (pitch บนเวที) จนถึงการพัฒนาต่อหลังการแข่งขัน
- Model approach ต้อง **ซื่อสัตย์ทางวิชาการ** — ไม่ overclaim ว่าระบบทำนายอนาคตได้จริง แต่แสดงให้เห็นว่า pipeline ทำงานได้ ผลลัพธ์ interpretable และมีทฤษฎีรองรับ

### 5. ข้อตั้ง (Assumptions)

- โปรเจกต์นี้เป็น **early decision-support prototype** ไม่ใช่ระบบวินิจฉัยทางการแพทย์
- ข้อมูลที่มีจำกัด: 55 ภาพ X-ray, 92 bounding box annotations, 1,000 synthetic clinical records — ยังไม่มี longitudinal outcome data จริง
- ยังไม่มี dataset ขนาดใหญ่พอที่จะ train end-to-end deep prognosis model สำหรับพยากรณ์ผลระยะยาว
- ทีมต้องการ prototype ที่ **น่าเชื่อถือ อธิบายได้ สาธิตได้ และสร้างได้ภายในเวลาจำกัด**
- ระยะเวลาจากตอนนี้ถึงรอบ 2 ประมาณ **4 สัปดาห์** (ถึง 20 ก.ค.)

### 6. เป้าหมายของ Prototype จริง

Prototype จริงที่ต้องโชว์ให้กรรมการเห็น ควรทำได้ดังนี้:

**ต้องมี:**

- รับ X-ray ผ่าน upload หรือเลือกจากเคสตัวอย่าง
- รับ clinical input: อายุ, bone age, เพศ, น้ำหนัก, ส่วนสูง, ตำแหน่ง, ประวัติโรคร่วม/ยา
- **Vision model จริง** ที่ localize growth-plate region และ predict coarse injury class ได้ (แทน label-based overlay)
- **Prognosis engine จริง** ที่ integrate สูตรจาก clinical research pipeline เข้ากับ web app (แทน mock scoring)
- Dashboard แสดง overlay, key metrics, risk explanation และ trend visualization
- Persistent storage สำหรับ case metadata, uploaded images และ generated outputs

**ยังไม่ต้องมี (อยู่ใน phase หลัง):**

- Clinical deployment หรือ treatment recommendation แบบอัตโนมัติ
- PACS integration, hospital-wide authentication, enterprise audit controls
- Custom end-to-end multimodal deep model ที่ train จาก raw X-ray ถึง long-term outcome
- การอ้าง diagnostic accuracy ที่เกินขอบเขตของ evaluation set ที่มี

### 7. Tech Stack ที่แนะนำ

Stack ควรอยู่ใกล้กับสิ่งที่มีอยู่แล้วใน repository โดยเปลี่ยนเฉพาะส่วนที่จำเป็นสำหรับ prototype จริง

#### Frontend

**React + Vite + Tailwind CSS** (เหมือนเดิม)

Stack นี้มีอยู่แล้วและเหมาะกับ dashboard-style prototype รองรับ iteration เร็ว, deploy ง่าย, แยก input flow / visual overlay / analytical sections ได้ชัดเจน ไม่มีเหตุผลที่ต้องเปลี่ยนในขั้นนี้

#### Backend

**FastAPI + Python** (เหมือนเดิม)

Backend ปัจจุบันมี API shape ที่ดีอยู่แล้ว และ Python เป็นภาษาเดียวกับ data processing, image handling และ ML inference ทำให้ทีมใช้ภาษาเดียวตั้งแต่ API logic ถึง research scripts

#### Database

**PostgreSQL** สำหรับ hosted prototype, **SQLite** สำหรับ local development เท่านั้น

Demo ปัจจุบันไม่มี persistent storage — prototype จริงต้องเก็บ cases, inputs, run metadata และ generated outputs PostgreSQL รองรับ structured clinical fields, model-run metadata และ auditability โดยไม่ซับซ้อนเกินไป

#### Object Storage

**S3-compatible storage** (Supabase Storage, Cloudflare R2 หรือ AWS S3)

ภาพ X-ray ที่อัปโหลด, overlay images และ artifacts ที่สร้างขึ้น ไม่ควรเก็บใน API container หรือ database โดยตรง Object storage เป็นทางเลือกที่ทนทานที่สุดและเตรียมพร้อมสำหรับ dataset versioning ในภายหลัง

#### AI และ Data Tooling

**PyTorch + Ultralytics YOLO** สำหรับ vision model ตัวแรก, **scikit-learn** สำหรับ tabular baselines, **NumPy, Pandas, Pillow, OpenCV** สำหรับ preprocessing

เลือก YOLO เพราะเป็น object detection ที่ train และ demo ได้เร็วกว่า custom medical segmentation stack สำหรับโปรเจกต์ที่ต้องเห็นผล localization output ภายในเวลาจำกัด Repository ปัจจุบันใช้ Python-based image/numeric tooling อยู่แล้ว

ถ้าทีมต้องการย้ายไป medical imaging workflow หรือ DICOM pipeline ในภายหลัง สามารถเพิ่ม MONAI ได้ใน phase ถัดไป ไม่ต้องเพิ่มตอนเริ่ม

#### Cloud และ Deployment

**Vercel** สำหรับ frontend, **Render / Railway / Fly.io** สำหรับ backend ที่มี model inference

Demo ปัจจุบัน deploy ทั้งคู่บน Vercel ซึ่งเพียงพอสำหรับ facade เมื่อเพิ่ม model inference จริง backend ต้องการ Python host ที่มี filesystem access, memory มากกว่า และ runtime ที่เสถียรกว่า แยก deploy เป็นทางเลือกที่ปลอดภัยกว่า

### 8. สถาปัตยกรรมระบบ (System Architecture)

สถาปัตยกรรมที่แนะนำเป็น hybrid application ประกอบด้วย 5 layers:

#### Presentation Layer (Frontend)

Dashboard แบบ single workflow: อัปโหลด/เลือกภาพ → กรอก clinical input → submit → แสดงผลรวม (overlay, risk metrics, explanatory factors, projection charts) บนหน้าเดียว

#### API Layer (Backend)

FastAPI endpoints: sample retrieval, case submission, analysis execution, result retrieval ใน prototype แรก inference สามารถ synchronous ได้ถ้า runtime สั้น ถ้า model runtime นานขึ้น สามารถเปลี่ยนเป็น asynchronous job flow ได้ภายหลัง

#### Data Layer

- Case metadata + clinical inputs → PostgreSQL
- Uploaded X-rays + overlay images → Object Storage
- Model artifacts + version metadata → controlled file/storage location

#### Model Layer

แบ่งออกเป็นสองส่วนแยกกัน ไม่ใช่ end-to-end:

- **Vision component**: localize physis region และ predict coarse fracture/damage features
- **Prognosis component**: รวม vision output + clinical inputs + สูตรทางคลินิกจาก research pipeline → risk-oriented projections

การแยกสองส่วนทำให้ระบบ **explainable** และตรงกับความเป็นจริงของ dataset ที่มี

#### User Interaction Flow

1. ผู้ใช้ส่งภาพ + clinical inputs
2. Backend validate + preprocess
3. Vision model สร้าง region/feature outputs
4. Prognosis engine รวม model outputs + clinical data → structured risk results
5. ผลลัพธ์ถูกบันทึกและส่งกลับ frontend
6. Frontend แสดง overlay, scores, factors, projected trend

### 9. แนวทาง AI/ML Model

#### 9.1 สถาปัตยกรรม: Neuro-Symbolic AI

ระบบใช้สถาปัตยกรรมแบบ **Neuro-Symbolic AI** (Physics-Informed Machine Learning) ตามที่ออกแบบไว้ใน KneeGrowth-AI-2.pdf โดยแบ่งการทำงานเป็น 2 สาย:

1. **Neural Network (Branch A — Computer Vision)**: สกัด features จากภาพ X-ray → `Area%`, `Location`, `bone_type`
2. **Symbolic Logic (Branch B — Clinical Math Engine)**: นำค่าที่สกัดได้ + ข้อมูลทางคลินิกจากแพทย์ → คำนวณผ่านสูตรทางการแพทย์ (Hueter-Volkmann, Geometric Tethering, Paley Multiplier, WHO z-score)
3. **Prediction Head**: รวม features จากทั้ง 2 สาย → Regression → ผลพยากรณ์แสดงบน Dashboard

เลือก Neuro-Symbolic แทน end-to-end deep learning เพราะ:

- **Data จริงมีจำกัด** (55 ภาพ X-ray, 18 fracture cases) — ไม่พอสำหรับ end-to-end model ที่น่าเชื่อถือ
- **ต้องอธิบายผลลัพธ์ได้ทุกขั้นตอน** — ระบบ medical AI ที่ดีต้องบอกได้ว่าทำไมถึงได้ผลลัพธ์นี้
- **สูตรทางคลินิกมีพื้นฐานจากวรรณกรรมทางการแพทย์** — Tachdjian's Pediatric Orthopaedics, JCEM, Pediatrics
- **Scalable by design** — เมื่อมี data มากขึ้น สามารถ upgrade ML module ทีละตัวโดยไม่ต้อง rewrite ระบบ

อ้างอิง: Karniadakis, G. E., et al. (2021). Physics-informed machine learning. Nature Reviews Physics, 3(6), 422-440.

---

#### 9.2 Branch A: Computer Vision Pipeline

Branch A ทำหน้าที่ **สกัดข้อมูลจากภาพ X-ray** ออกมาเป็น structured features ที่ป้อนเข้า Branch B ได้ แบ่งเป็น 3 ขั้นตอน:

##### ขั้นที่ 1: YOLO Object Detection — ระบุตำแหน่ง Physis

**Input**: ภาพ X-ray ข้อเข่าเด็ก (PNG/JPEG)

**Process**: Fine-tune pre-trained YOLOv8 บน dataset ที่มี bounding box annotations 92 records

**Output**:
- Bounding box ของ physis region พร้อม confidence score
- Class: `Femur_physis` หรือ `Tibia_physis`

**การออกแบบ Model**:

| รายละเอียด | ค่า |
|------------|-----|
| จำนวน classes | **2** (Femur_physis, Tibia_physis) |
| Training data | Normal: 37 ภาพ × 2 boxes/ภาพ = 74 boxes, Fracture: 18 ภาพ × 1 box/ภาพ = 18 boxes |
| Augmentation | flip, rotate ±5°, contrast (α=1.2, β=−10) → 4 augmented ต่อ original (จาก `augment_data.py`) |
| Data หลัง augment | ~460 bounding box annotations |
| Evaluation | mAP@0.5, IoU, visual review โดยทีม |

เลือก **2 classes** (ไม่แยก Normal/Damaged เป็น 4 classes) เพราะ:
- Data ต่อ class มากกว่า (Femur ~48, Tibia ~44 ก่อน augment)
- YOLO ทำหน้าที่ **localization เท่านั้น** — การจำแนก Normal/Fracture เป็นงานของขั้นถัดไป
- ตรงกับหลักการ Neuro-Symbolic: Neural Network สกัด features → ขั้นถัดไปวิเคราะห์

##### ขั้นที่ 2: Binary Classification — Normal vs Fracture

**Input**: Cropped physis region จาก YOLO (ขั้นที่ 1)

**Process**: Transfer learning บน pre-trained CNN (เช่น ResNet-18 หรือ EfficientNet-B0) fine-tune สำหรับ binary classification

**Output**:
- Classification: `Normal` หรือ `Fracture`
- Confidence score (0–1)

**Data ที่ใช้**:

| Class | จำนวน crops (ก่อน augment) | หลัง augment (×5) |
|-------|---------------------------|-------------------|
| Normal | ~74 | ~370 |
| Fracture | ~18 | ~90 |

เลือก **binary** (ไม่ทำ multi-class SH classification) เพราะ:
- Data 18 fracture ภาพแบ่งเป็น 4 SH types (SH-I: 4, SH-II: 7, SH-III: 3, SH-IV: 4) — **ไม่เพียงพอ** สำหรับ 4-class classifier ที่น่าเชื่อถือ
- Augmentation เพิ่ม variation แต่ไม่เพิ่ม clinical diversity — ต่อให้ augment 10 เท่า model ก็ไม่ได้เห็น anatomy ใหม่
- การ overclaim accuracy จาก tiny dataset **ทำลายความน่าเชื่อถือของทั้งโปรเจกต์**
- SH type classification ให้ **แพทย์ระบุ** (human-in-the-loop) — ถูกต้องกว่าทาง clinical practice

##### ขั้นที่ 3: CycleGAN Damage Visualization (Experimental)

**Input**: Cropped physis region ที่ classify เป็น Fracture (ขั้นที่ 2)

**Process**:
1. CycleGAN Generator: Fracture → Normal (แปลงภาพ fracture ให้เหมือนไม่มี fracture)
2. Difference Map: |ภาพจริง − ภาพ normalized|
3. Thresholding + Area Calculation: พื้นที่ที่ต่างกัน ÷ พื้นที่ physis ทั้งหมด

**Output**:
- **Damage heatmap** (visual aid สำหรับแพทย์)
- **Area% suggestion** (ค่าประมาณ physeal bar area)

**Data ที่ใช้** (เตรียมไว้แล้วใน `data/01 Branch A Vision/CycleGAN/`):

| Domain | จำนวน (ก่อน augment) | หลัง augment |
|--------|---------------------|-------------|
| trainA (Normal) | 31 | ~155 |
| trainB (Fracture) | 15 | ~75 |
| testA / testB | 6 / 3 | 6 / 3 |

**สถานะ**: CycleGAN เป็น **experimental module** — ผลลัพธ์ไม่ถูกใช้โดยตรงในการตัดสินใจทางคลินิก แต่เป็น:
- **Visual aid**: แพทย์ดู heatmap ประกอบการตัดสินใจ
- **Area% suggestion**: model แนะนำค่าผ่าน slider ที่แพทย์ปรับแก้ได้
- **Synthetic data potential**: แสดงศักยภาพในการสร้าง synthetic fracture data สำหรับ training ในอนาคต

ถ้า CycleGAN quality ไม่ดีพอ → fallback: แพทย์กรอก Area% เองทั้งหมด (ไม่มี suggestion)

##### สรุป Branch A: Vision Pipeline Flow

```
ภาพ X-ray ข้อเข่าเด็ก
    │
    ▼
[ขั้นที่ 1: YOLO Detection]
    │ Output: bounding box + class (Femur_physis / Tibia_physis)
    │
    ▼
[Crop physis region]
    │
    ▼
[ขั้นที่ 2: Binary Classification]
    │ Output: Normal / Fracture + confidence
    │
    ├── Normal → ไม่มี damage → ข้ามขั้นที่ 3
    │
    └── Fracture →
            │
            ▼
        [ขั้นที่ 3: CycleGAN (experimental)]
            │ Output: damage heatmap + Area% suggestion
            │
            ▼
        [แพทย์ review + ยืนยัน/แก้ไข]
            │ ยืนยัน: SH type, Area%, fusion_stage
            │
            ▼
        Features พร้อมส่งเข้า Branch B
```

**Features ที่ Branch A ส่งออก**:

| Feature | ที่มา | ค่า |
|---------|------|-----|
| `bone_type` | YOLO class | Femur / Tibia |
| `bone_site` | derive จาก bone_type | distal_femur / proximal_tibia |
| `X_Min, Y_Min, X_Max, Y_Max` | YOLO bounding box | พิกัด pixel |
| `X_Bar, Y_Bar` | จุดกึ่งกลาง bounding box | พิกัด pixel → bar_location (Central/Peripheral) |
| `classification` | Binary classifier | Normal / Fracture |
| `damage_heatmap` | CycleGAN difference map | ภาพ overlay |
| `area_pct_suggestion` | CycleGAN area calculation | 0–100% (experimental) |

---

#### 9.3 Branch B: Clinical Math Engine (Symbolic Logic)

Branch B คือ `knee_prognosis_pipeline.py` ที่ Namthip พัฒนา — เป็น **rule-based engine** ที่ใช้สูตรทางการแพทย์คำนวณ prognosis จาก structured data

##### Input ของ Branch B

**จากแพทย์ (User Input)**:

| ตัวแปร | ตัวอย่างค่า | หมายเหตุ |
|--------|------------|----------|
| `gender` | male / female | — |
| `chronological_age_yr` | 10.5 | อายุจริง (ปี) |
| `bone_age_yr` | 12.0 | อายุกระดูก (ปี) — จาก Bone Age X-ray |
| `height_cm` | 140 | ส่วนสูง |
| `weight_kg` | 35 | น้ำหนัก |
| `pathology_code` | S79.0 | ICD-10 code ของการบาดเจ็บ |
| `fusion_stage` | 2 | ระยะการเชื่อมของ growth plate (clinical assessment) |
| `location` | medial / lateral | ตำแหน่งที่เสียหาย (= `side` ใน annotation) |
| `salter_harris_type` | SH_Type_II | ประเภท fracture (human-in-the-loop) |

**จาก Branch A (Vision Features)**:

| ตัวแปร | ที่มา | หมายเหตุ |
|--------|------|----------|
| `bone_site` | YOLO class → derive | distal_femur / proximal_tibia |
| `X_Min, Y_Min, X_Max, Y_Max` | YOLO bounding box | สำหรับ `compute_vision_features()` |
| `physeal_bar_area_pct` | CycleGAN suggestion → แพทย์ยืนยัน | % ของ growth plate ที่เสียหาย |

**ค่าที่ระบบคำนวณเอง**:

| ตัวแปร | วิธีคำนวณ | หมายเหตุ |
|--------|----------|----------|
| `BMI` | weight / (height/100)² | ClinicalMathEngine §6 |
| `z_score` | WHO LMS method จาก เพศ+อายุ → lookup L, M, S | ใช้ตาราง WHO reference |
| `beta` | default 0.10 | ค่าความไวต่อแรงกระตุ้นทางชีวภาพ (configurable) |
| `sigma` (dynamic) | `(mech_bias - 1.0) × -1.5` จาก BMI z-score | Mechanical stress — pipeline คำนวณจาก BMI |

##### Process ของ Branch B (5 ขั้นตอน)

**Step 1 — BMI + WHO Z-Score**:
- คำนวณ BMI จากน้ำหนัก/ส่วนสูง
- Lookup ค่า L, M, S จากตาราง WHO ตามเพศ+อายุ
- คำนวณ z-score: `Z = ((BMI/M)^L − 1) / (L × S)`
- แปลงเป็น mechanical stress bias สำหรับ Hueter-Volkmann

**Step 2 — Pathology Bias (ICD-10)**:
- Lookup `pathology_code` ใน PATHOLOGY_WEIGHTS table
- ค่า weight ตาม ICD-10: เช่น S79.0 (Physeal fracture of femur) = 1.0, E25 (Cushing's) = 1.3
- คำนวณ combined modifier = pathology_weight × medication_bias

**Step 3 — Bone Age + Paley Multiplier**:
- ใช้ `bone_age_yr` (ไม่ใช่อายุจริง) เปิดตาราง Paley Multiplier
- `L_remaining = L_current × (M_BA − 1)` — ศักยภาพการเติบโตที่เหลือ (มิลลิเมตร)
- Maturity limit: ชาย 16 ปี, หญิง 14 ปี

**Step 4 — Vision Features**:
- `compute_vision_features(cv_row)` รับค่าจาก Branch A
- แปลง bounding box → `bar_location` (Central/Peripheral จาก side: Medial→Peripheral, Lateral→Peripheral)
- ดึง `physeal_bar_area_pct` (จาก CycleGAN suggestion ที่แพทย์ยืนยันแล้ว)
- Lookup `SH_ARREST_BASE_RISK` ตาม SH type: SH-I=36%, SH-II=58%, SH-III=49%, SH-IV=64%

**Step 5 — Multimodal Fusion**:
- **Hueter-Volkmann**: `G = G₀ × (1 − β × σ)` — อัตราการเจริญเติบโตที่ลดลงจากแรงกด
  - `G₀` = อัตราการเจริญเติบโตพื้นฐานตาม bone_site (distal_femur: 0.9 cm/ปี, proximal_tibia: 0.6 cm/ปี)
  - `β` = ค่าความไว (default 0.10)
  - `σ` = dynamic mechanical stress (จาก BMI)
- **Geometric Tethering**: `Δθ = G_undamaged / d` — อัตราการเอียงของกระดูก
  - `d` = ระยะ tethering point (จาก bounding box + pixel spacing)
  - Pixel spacing: `d_mm = d_px × S_pixel` (จาก DICOM tag 0028,0030, default 0.286 mm/px)
- **Projection**: คำนวณ LLD และ angular deformity ที่ 1, 3, 5 ปี
- **Probability**: P(Complete Arrest), P(Varus/Valgus) จาก combined risk factors
- **Severity Label**: Low / Medium / High จาก combined score
- **Intervention Flag**: แนะนำการรักษาเมื่อ risk สูงเกิน threshold

---

#### 9.4 Prediction Head: การรวมผลลัพธ์

Prediction Head ไม่ใช่ model แยก แต่คือ **ขั้นตอน fusion ใน Step 5 ของ Branch B** ที่ concatenate features จากทั้งสองสาย:

```
Branch A Features                 Branch B Features
(bone_site, box, area%,           (BMI z-score, pathology bias,
 bar_location, SH type)            bone age, Paley multiplier,
         │                          fusion stage, medications)
         │                                    │
         └──────────── Concatenation ──────────┘
                           │
                           ▼
                  [Multimodal Fusion]
                  Hueter-Volkmann + Geometric Tethering
                  + Paley Growth Projection
                           │
                           ▼
                  Output สำหรับ Dashboard
```

---

#### 9.5 Variable Mapping: สรุปที่มาของทุกตัวแปร

| ตัวแปร | แหล่งที่มา | หมายเหตุ |
|--------|-----------|----------|
| ภาพ X-ray | อัปโหลดโดยแพทย์ | PNG/JPEG |
| `bone_type`, `bone_site` | **Vision Model** (YOLO) | Femur→distal_femur, Tibia→proximal_tibia |
| `X_Min, Y_Min, X_Max, Y_Max` | **Vision Model** (YOLO) | Bounding box |
| `X_Bar, Y_Bar` (bar_location) | **Vision Model** (YOLO) | จุดกึ่งกลาง box → Central/Peripheral |
| Normal/Fracture classification | **Vision Model** (Binary CNN) | + confidence score |
| Damage heatmap | **Vision Model** (CycleGAN) | Experimental — visual aid |
| `area_pct` suggestion | **Vision Model** (CycleGAN) | Experimental — แพทย์ปรับได้ |
| `physeal_bar_area_pct` | **แพทย์ยืนยัน** (จาก suggestion) | ค่าสุดท้ายที่ใช้คำนวณ |
| `salter_harris_type` | **แพทย์ระบุ** (human-in-the-loop) | Data ไม่พอสำหรับ auto-classification |
| `gender` | **แพทย์กรอก** | — |
| `chronological_age_yr` | **แพทย์กรอก** | — |
| `bone_age_yr` | **แพทย์กรอก** | จาก Bone Age X-ray assessment |
| `height_cm`, `weight_kg` | **แพทย์กรอก** | — |
| `pathology_code` | **แพทย์กรอก** | ICD-10 |
| `fusion_stage` | **แพทย์กรอก** | Clinical assessment |
| `location` (medial/lateral) | **แพทย์กรอก** | ตำแหน่งที่บาดเจ็บ |
| BMI, z-score | **ระบบคำนวณ** | จาก weight + height + เพศ + อายุ |
| `beta` | **ค่า default** (0.10) | Configurable สำหรับ advanced use |
| `sigma` (dynamic) | **ระบบคำนวณ** | จาก BMI z-score → mechanical stress |

---

#### 9.6 Dashboard Output: สิ่งที่แสดงผลบนหน้าจอ

**แสดงต่อแพทย์**:

| Output | ที่มา | รูปแบบ |
|--------|------|--------|
| Damage Heatmap/Overlay บน X-ray | CycleGAN + YOLO box | ภาพ overlay |
| Physeal Bar Area % | แพทย์ยืนยัน (จาก model suggestion) | ตัวเลข hero metric |
| Risk Level | Combined score → severity label | Badge: Low / Medium / High |
| Salter-Harris Classification | แพทย์ระบุ | Text label |
| Bend Direction | bar_location → Varus/Valgus | Text + icon |
| LLD Projection 1/3/5 ปี | Hueter-Volkmann + Paley | กราฟเส้น (mm) |
| Angular Deformity 1/3/5 ปี | Geometric Tethering | กราฟเส้น (องศา) |
| P(Complete Arrest) | SH base risk × modifiers | เปอร์เซ็นต์ |
| P(Varus/Valgus) | Tethering + location | เปอร์เซ็นต์ |
| Remaining Growth % | Paley Multiplier | เปอร์เซ็นต์เทียบเด็กปกติ |
| BMI + Z-Score | WHO LMS calculation | ตัวเลข + interpretation |
| Contributing Factors | Combined analysis | รายการ + impact level |
| **Intervention Recommended** | Pipeline threshold check | ✅/❌ + คำอธิบาย |

**ไม่แสดง** (เก็บใน API response สำหรับ debugging):
- ค่า intermediate: HV growth rate, combined_modifier, dynamic_sigma, mechanical_stress_bias
- Raw model outputs: YOLO raw logits, CycleGAN raw difference values
- Pipeline internal state: step-by-step computation trace

---

#### 9.7 Design Decisions และเหตุผล

| การตัดสินใจ | ทางเลือกที่ไม่เลือก | เหตุผลที่เลือกทางนี้ |
|------------|--------------------|--------------------|
| YOLO 2 classes (Femur/Tibia physis) | 4 classes (แยก Normal/Damaged) | Data ต่อ class มากกว่า, แยก detection กับ classification ตาม Neuro-Symbolic design |
| Binary classification (Normal/Fracture) | Multi-class SH (5 classes) | SH-III มีแค่ 3 ภาพ — multi-class ไม่น่าเชื่อถือ |
| SH type = human-in-the-loop | Automated SH classifier | Data 18 fracture ÷ 4 types = ไม่พอ, แพทย์ทำได้แม่นกว่า |
| Area% = model suggest + แพทย์ปรับ | Model กำหนดเอง / แพทย์กรอกเอง | แสดง model capability + safety net จาก human oversight |
| CycleGAN = experimental module | CycleGAN เป็น primary classifier | GAN training บน 15 ภาพไม่เสถียร, ใช้เป็น visual aid ปลอดภัยกว่า |
| Neuro-Symbolic hybrid | End-to-end deep learning | Data ไม่พอ, สูตรทางคลินิกมีฐานวรรณกรรม, อธิบายได้ทุกขั้นตอน |

**หลักการสำคัญ**: ระบบถูกออกแบบให้ **ซื่อสัตย์กับข้อจำกัดของ data** — ML ทำเฉพาะสิ่งที่ data รองรับ (localization, binary classification), สิ่งที่ต้องการ precision สูงกว่า data ที่มี (SH type, fine-grained Area%) ใช้ human-in-the-loop, สูตรทางคลินิกที่มีฐาน evidence-based ใช้ rule-based engine

**Upgrade path**: เมื่อมี data มากขึ้นในอนาคต สามารถ upgrade ทีละ module:
- Binary → multi-class SH classification (เมื่อมี fracture ≥ 50 ภาพต่อ SH type)
- Area% suggestion → Area% direct estimation (เมื่อ CycleGAN quality ผ่านเกณฑ์)
- Human SH input → model SH prediction (เมื่อ validate ได้กับ clinical expert)
- ทั้งหมดนี้ทำได้ **โดยไม่ต้อง rewrite ระบบ** — เปลี่ยนเฉพาะ module ที่ upgrade

### 10. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  แพทย์                                                              │
│  ├── อัปโหลด X-ray                                                  │
│  └── กรอก Clinical Input (อายุ, bone age, เพศ, น้ำหนัก, ส่วนสูง,    │
│       pathology code, fusion stage, location)                       │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
              ┌─── 1. Validation ───┐
              │ file type, size,    │
              │ required fields,    │
              │ value ranges        │
              └────────┬────────────┘
                       │
          ┌────────────┴────────────────┐
          ▼                             ▼
   2. Branch A (Vision)          3. Branch B (Clinical)
   ├── YOLO Detection            ├── BMI + WHO Z-Score
   │   → box + class             ├── Pathology Bias (ICD-10)
   ├── Crop → Binary CNN         ├── Bone Age + Paley Multiplier
   │   → Normal/Fracture         └── (รอ features จาก Branch A)
   └── CycleGAN (experimental)
       → heatmap + Area% suggestion
          │                             │
          ▼                             │
   4. Human-in-the-Loop                │
   ├── แพทย์ review heatmap            │
   ├── ยืนยัน/แก้ Area%                │
   ├── ระบุ SH type                    │
   └── Features พร้อม ─────────────────┤
                                       │
                                       ▼
                          5. Multimodal Fusion
                          ├── Hueter-Volkmann (growth rate)
                          ├── Geometric Tethering (angular)
                          ├── Paley Projection (1/3/5 yr)
                          ├── Probability Estimation
                          └── Intervention Flag
                                       │
                                       ▼
                            6. Persistence
                            ├── PostgreSQL: case, inputs,
                            │   model run, results
                            └── Object Storage: images,
                                overlays, heatmaps
                                       │
                                       ▼
                            7. Dashboard Display
                            ├── Overlay + heatmap
                            ├── Metrics + risk level
                            ├── Growth projection graphs
                            ├── Contributing factors
                            └── Intervention recommendation
```

**จุดสำคัญของ flow นี้**: ข้อมูลผ่าน human-in-the-loop (ขั้น 4) ก่อนเข้า fusion — แพทย์เป็นคนยืนยันค่า SH type และ Area% ที่ระบบจะใช้คำนวณ ไม่ใช่ model ตัดสินใจเอง

### 11. ระยะการพัฒนา (Development Phases)

#### Phase A: ตรวจสอบข้อมูลและกำหนดขอบเขต (Scope & Data Audit)

**เป้าหมาย**: กำหนดว่า prototype ตัวแรกสามารถอ้างอะไรได้อย่างซื่อสัตย์

งานหลัก:

- ทบทวน assets ที่มีใน repo: ภาพ, labels, สูตร, pipeline
- ตรวจสอบคุณภาพ annotation (bounding box 92 records) และ dataset splits
- กำหนด clinical input schema ให้เป็นมาตรฐาน
- ตัดสินใจเป้าหมายที่แน่ชัดของ starting model (localization เท่านั้น หรือ localization + classification)
- Review pipeline ของ Namthip เพื่อกำหนดว่าส่วนใดจะ integrate เข้า backend ก่อน

ผลลัพธ์ที่คาดหวัง:

- ขอบเขต prototype ที่ finalize แล้ว
- Dataset inventory ที่ clean แล้ว
- Case schema และ result schema ที่เสถียร

#### Phase B: โครง Prototype จริงและ Persistence (Product Skeleton)

**เป้าหมาย**: เปลี่ยน demo facade ให้เป็น prototype shell ที่มี persistent storage

งานหลัก:

- คง React + FastAPI structure ที่มีอยู่
- เพิ่ม PostgreSQL-backed case storage (case, uploaded image, clinical input set, model run, result summary, overlay artifact)
- เพิ่ม object storage สำหรับ uploads และ overlays
- Refactor static metadata flows ให้เป็น database-backed records
- แยก demo-only logic ออกจาก real inference logic ใน codebase

ผลลัพธ์ที่คาดหวัง:

- Application shell ที่ deploy ได้ + persistent case handling

#### Phase C: Vision Model Pipeline (3 ขั้นตอน)

**เป้าหมาย**: สร้าง Branch A ทั้ง pipeline — แทนที่ metadata-only overlay ด้วย model inference จริง

งานหลัก:

**C1 — YOLO Physis Detection (2 classes)**:
- แปลง bounding box annotations (92 records จาก `xray_bounding_boxes.csv`) เป็น YOLO format
- Augment data ด้วย `augment_data.py` (flip, rotate ±5°, contrast) → ~460 annotations
- Fine-tune pre-trained YOLOv8 บน dataset
- Evaluation: mAP@0.5, IoU, visual review — เปรียบเทียบกับ label-based overlay เดิม

**C2 — Binary Classification (Normal vs Fracture)**:
- ใช้ YOLO จาก C1 crop physis regions จากทุกภาพ
- Train binary CNN (ResNet-18 / EfficientNet-B0) ด้วย transfer learning
- Data: ~74 Normal crops, ~18 Fracture crops (+ augmentation)
- Evaluation: accuracy, precision, recall, confusion matrix + visual review

**C3 — CycleGAN Damage Visualization (experimental)**:
- Train CycleGAN บน data ที่เตรียมไว้ใน `data/01 Branch A Vision/CycleGAN/`
- สร้าง Fracture→Normal generator
- Implement difference map → damage heatmap + Area% suggestion
- Evaluation: visual quality review โดยทีม — ไม่ต้องผ่านเกณฑ์เชิงปริมาณ (experimental)
- ถ้า quality ไม่ดีพอ: fallback เป็น Area% จากแพทย์กรอกเอง

ผลลัพธ์ที่คาดหวัง:

- Vision pipeline 3 ขั้นที่ทำงานได้: YOLO → Binary CNN → CycleGAN (experimental)
- Model inference service ใน backend

#### Phase D: เชื่อม Prognosis Engine + Human-in-the-Loop (Pipeline Integration)

**เป้าหมาย**: รวม Vision output + human review + clinical math engine เป็น end-to-end prototype

งานหลัก:

**D1 — Human-in-the-Loop UI**:
- เพิ่มหน้า review หลัง Vision inference: แสดง heatmap + Area% suggestion + slider ให้แพทย์ปรับ
- เพิ่ม input fields สำหรับ SH type, fusion_stage (ค่าที่ model ไม่ได้ predict)
- Design flow: Vision result → แพทย์ review/ยืนยัน → ส่งเข้า pipeline

**D2 — Pipeline Integration**:
- Integrate `knee_prognosis_pipeline.py` ของ Namthip เข้า backend (แทนที่ mock scoring/growth)
- Map Vision features → `cv_row` dict ที่ `compute_vision_features()` ต้องการ
- Map Clinical input → parameters ที่ `run_pipeline()` ต้องการ
- เพิ่ม Intervention Recommended flag ใน output

**D3 — End-to-End Testing**:
- ทดสอบ full flow กับ demo cases ทุกระดับ (Normal/Low/Medium/High)
- ทำให้ระบบ **deterministic ที่สุด** — input เดียวกัน + การยืนยันเดียวกัน → ผลเดิมเสมอ
- Clinical plausibility check: ผลลัพธ์สมเหตุสมผลทางการแพทย์หรือไม่

ผลลัพธ์ที่คาดหวัง:

- End-to-end Neuro-Symbolic pipeline ที่ทำงานได้จริง (Vision + Human Review + Clinical Math)

#### Phase E: ปรับปรุง UI และ User Flow (Refinement)

**เป้าหมาย**: ทำให้ระบบพร้อมสำหรับ review, demo และ feedback จากกรรมการ

งานหลัก:

- ปรับ result clarity และ section ordering ให้อ่านง่าย
- เพิ่ม status handling รอบ model execution (loading state, error state)
- ดูแลว่า sample cases ยังทำงานได้ถูกต้องหลังเปลี่ยนเป็น real inference
- Review ภาษาใน UI: แยกชัดเจนระหว่าง image findings, estimated risk และ projected outlook
- ทำให้ UI **แสดงอย่างชัดเจนว่าระบบทำอะไรและทำไม** — เหมาะกับกรรมการที่ให้คะแนน interpretability

ผลลัพธ์ที่คาดหวัง:

- Prototype dashboard ที่พร้อมโชว์ที่บูธ

#### Phase F: Validation และ Hosted Prototype (Deploy)

**เป้าหมาย**: ได้ hosted prototype ที่เสถียรสำหรับโชว์ที่งาน

งานหลัก:

- Deploy frontend + backend (แยก host)
- Seed sample cases สำหรับ demo ที่ deterministic
- รัน smoke tests + clinical plausibility checks
- ทดสอบ end-to-end ที่งานจริง (network, latency, edge cases)
- เขียน documentation: limitations, known gaps, model scope
- **Clinical face-validity review**: ให้ทีมทบทวนว่า risk output สมเหตุสมผลทางคลินิก
- **ซ้อม demo flow**: จำลองสถานการณ์ที่จะเกิดที่บูธ ทั้ง happy path และ edge cases

ผลลัพธ์ที่คาดหวัง:

- Hosted prototype ที่แชร์ได้ + validation notes
- ทีมพร้อมสำหรับรอบ 2

### 12. สิ่งที่ Prototype สุดท้ายต้องมี

เมื่อจบ Phase A–F ทีมควรมี:

- [ ] Frontend dashboard ที่ deploy แล้ว พร้อม human-in-the-loop review flow
- [ ] FastAPI backend ที่ deploy แล้ว พร้อม model inference + pipeline integration
- [ ] Persistent case + result store (PostgreSQL)
- [ ] Object storage สำหรับ uploaded + generated images
- [ ] **YOLO physis detector** (2 classes: Femur_physis, Tibia_physis)
- [ ] **Binary classifier** (Normal vs Fracture) บน cropped physis
- [ ] **CycleGAN module** (experimental) สำหรับ damage heatmap + Area% suggestion
- [ ] **Human-in-the-loop UI** สำหรับ SH type + Area% review/confirmation
- [ ] **Integrated prognosis engine** จาก `knee_prognosis_pipeline.py` (แทนที่ mock scoring/growth)
- [ ] Intervention Recommended flag ใน output
- [ ] Stable analysis API contract
- [ ] Sample demo cases สำหรับ deterministic walkthroughs
- [ ] Documentation: setup, deployment, limitations, model scope
- [ ] Validation summary: ระบบทำอะไรได้ ทำอะไรไม่ได้ + upgrade path

### 13. ความเสี่ยงและแผนรับมือ

#### ความเสี่ยงด้าน Technical

สถาปัตยกรรมปัจจุบันเรียบง่าย แต่การเพิ่ม model inference นำมาซึ่ง runtime, storage และ artifact-management concerns ถ้าทีมพยายามเพิ่ม backend patterns หลายอย่างพร้อมกัน prototype อาจ stabilize ยากกว่าตัว model เอง

**แผนรับมือ**: เพิ่มทีละ layer ตาม phase ที่วางไว้ ไม่กระโดดข้าม

#### ความเสี่ยงด้านข้อมูล

ภาพ X-ray จริง 55 ภาพ (37 Normal, 18 Fracture) เป็นจุดเริ่มต้นที่เล็ก โดยเฉพาะ fracture cases ที่แบ่งเป็น 4 SH types (SH-III มีแค่ 3 ภาพ) Augmentation เพิ่ม variation แต่ไม่เพิ่ม clinical diversity — model อาจ overfit กับ anatomy patterns ที่ซ้ำกัน

**แผนรับมือ**: ML ทำเฉพาะสิ่งที่ data รองรับ (localization + binary classification) สิ่งที่ต้องการ precision สูงกว่า (SH classification, fine-grained Area%) ใช้ human-in-the-loop ไม่ overclaim ว่า model สามารถ classify SH type จาก 18 ภาพได้

#### ความเสี่ยงด้าน Model

3 จุดเสี่ยงที่ต้องระวัง:

1. **YOLO**: 55 ภาพอาจไม่ครอบคลุม anatomy variation ทั้งหมด → localization อาจผิดพลาดกับภาพที่ต่างจาก training set
2. **Binary CNN**: Class imbalance (74 Normal vs 18 Fracture) → อาจ bias ไปทาง Normal
3. **CycleGAN**: 15 fracture images สำหรับ GAN training น้อยมาก → heatmap quality อาจไม่ดีพอ

**แผนรับมือ**:
- YOLO: ใช้ augmentation + pre-trained weights, แสดง confidence score ให้แพทย์ตัดสิน
- Binary CNN: ใช้ class weighting / oversampling, ตั้ง threshold ให้ favor recall (จับ fracture ให้ได้มากที่สุด)
- CycleGAN: เป็น experimental module — ถ้า quality ไม่ผ่าน → fallback เป็นแพทย์กรอก Area% เองทั้งหมด
- ทั้งระบบ: แยก vision model กับ prognosis engine ชัดเจน, ใช้ rule-based logic ที่อ้างอิงวรรณกรรมทางการแพทย์, แสดง limitations ใน UI

#### ความเสี่ยงด้าน User Experience

ถ้า UI แสดง probabilities โดยไม่มี explanation ผู้ใช้อาจเชื่อมากเกินไปหรือไม่เชื่อเลย

**แผนรับมือ**: แสดงชัดเจนว่า detect อะไร, ใช้ inputs อะไร, และทำไมได้ผลลัพธ์นี้ (contributing factors)

#### ความเสี่ยงด้านจริยธรรมและ Governance

การใช้ข้อมูลผู้ป่วยต้องมี consent, governance และ storage controls แม้ prototype จะใช้ open/synthetic data แต่สถาปัตยกรรมไม่ควรตั้งอยู่บนสมมติฐานว่าจะใช้ unsecured image handling ตลอดไป

**แผนรับมือ**: ออกแบบ data model ที่รองรับ access control ตั้งแต่แรก แม้จะยังไม่ enforce ใน prototype

#### ความเสี่ยงด้าน Scalability

Prototype แรกไม่ต้องการ distributed inference หรือ complex orchestration แต่ data model และ storage decisions ต้อง **ไม่ lock ทีมไว้** กับ static-demo architecture ที่ไม่สามารถรองรับ case history, versioned models หรือ validation workflows ในภายหลัง

**แผนรับมือ**: เลือก PostgreSQL + Object Storage ตั้งแต่แรก เพื่อไม่ต้อง migrate ทีหลัง

---

## สรุป

กระบวนการพัฒนา Bridge AI แบ่งเป็นสองช่วงชัดเจน:

**ช่วงที่ผ่านมา (7–22 มิ.ย.)**: ทีมสร้าง demo application ที่โชว์ workflow ครบตั้งแต่ input ถึง output ได้สำเร็จภายใน 15 วัน โดย Namthip เตรียมข้อมูลและพัฒนา clinical research pipeline คู่ขนาน Athiphat ขึ้นโครง backend/architecture และ Purich ออกแบบ UI/UX Demo นี้ขับเคลื่อนด้วย metadata ที่ label ไว้ล่วงหน้า ซึ่งเพียงพอสำหรับ proposal submission แต่ยังไม่ใช่ prototype จริง

**ช่วงถัดไป (สำหรับรอบ 2 และต่อไป)**: ระบบใช้สถาปัตยกรรม **Neuro-Symbolic AI** — แยก Neural Network (Branch A: YOLO detection → Binary classification → CycleGAN visualization) ออกจาก Symbolic Logic (Branch B: Clinical Math Engine จาก pipeline ของ Namthip) โดยมี human-in-the-loop เป็นตัวเชื่อม

แนวทางนี้ **ซื่อสัตย์กับข้อจำกัดของ data** (55 ภาพ, 18 fracture cases): ML ทำเฉพาะสิ่งที่ data รองรับ (localization, binary classification), สิ่งที่ต้องการ precision สูงกว่า (SH type, Area%) ให้แพทย์ยืนยัน, prognosis ขับเคลื่อนด้วยสูตรทางการแพทย์ที่มีฐานวรรณกรรม ทั้งระบบออกแบบให้ **upgrade ได้ทีละ module** เมื่อมี data มากขึ้นโดยไม่ต้อง rewrite — นี่คือ Scalability ที่แท้จริงของ Neuro-Symbolic design
