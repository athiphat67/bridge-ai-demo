# โฟลเดอร์ Data — ระบบ AI วิเคราะห์ข้อเข่าเด็ก

โฟลเดอร์นี้เก็บข้อมูลทั้งหมดของระบบ AI สองสาขา ได้แก่ **Branch A (Computer Vision)** สำหรับตรวจจับรอยแตกแบบ Salter-Harris และ **Branch B (Clinical)** สำหรับพยากรณ์การเจริญเติบโตของกระดูก

---

## โครงสร้างโฟลเดอร์

```
data/
├── 01 Branch A Vision/          # ข้อมูลภาพและ vision pipeline
│   ├── Dataset/                 # ชุดข้อมูล CycleGAN (256×256 px)
│   │   ├── trainA/              # Training — ข้อเข่าปกติ (Domain A)
│   │   ├── testA/               # Test     — ข้อเข่าปกติ (Domain A)
│   │   ├── trainB/              # Training — รอยแตก SH (Domain B)
│   │   └── testB/               # Test     — รอยแตก SH (Domain B)
│   ├── Knee_Fracture/           # ภาพ X-ray รอยแตกดิบ แยกตามประเภท SH
│   │   ├── SH_Type_I/
│   │   ├── SH_Type_II/
│   │   ├── SH_Type_III/
│   │   └── SH_Type_IV/
│   ├── Normal_Age/              # ภาพ X-ray ปกติดิบ แยกตามอายุผู้ป่วย
│   │   └── Normal_Age_{อายุ}/   # เช่น Normal_Age_14/
│   ├── ex type/                 # ภาพตัวอย่างอ้างอิงแต่ละประเภท SH
│   ├── annotate_physis.py       # เครื่องมือ annotation แบบ manual (OpenCV GUI)
│   ├── augment_data.py          # สคริปต์ data augmentation
│   ├── synthetic_damage_generator.py  # จัดระเบียบภาพดิบ → Dataset
│   ├── xray_bounding_boxes.csv  # ข้อมูล bounding box ของ physis
│   └── xray_bounding_boxes.json # ข้อมูลเดียวกันในรูปแบบ JSON
│
├── 02 Branch B Clinical Data/   # ข้อมูลคลินิกสังเคราะห์
│   ├── synthetic_clinical_biases.csv   # ข้อมูลผู้ป่วยสังเคราะห์ 1,000 ราย
│   ├── synthetic_clinical_biases.json  # ข้อมูลเดียวกันในรูปแบบ JSON
│   ├── clinical_bias_weights.json      # นิยาม modifier ตามรหัส ICD-10 และยา
│   ├── synthetic_bias_generator.py     # สคริปต์สร้างข้อมูล
│   └── zscores/                 # ตาราง growth reference ของ WHO (xlsx)
│       ├── bmi-boys-z-who-2007-exp.xlsx
│       ├── bmi-girls-z-who-2007-exp.xlsx
│       ├── wfh_boys_2-to-5-years_zscores.xlsx
│       ├── wfh_girls_2-to-5-years_zscores.xlsx
│       ├── wfl_boys_0-to-2-years_zscores.xlsx
│       └── wfl_girls_0-to-2-years_zscores.xlsx
│
└── References/                  # เอกสารอ้างอิงทางวิชาการ (PDF)
    ├── Annotation and Anatomy/
    ├── Clinical Bias Parameters/
    └── Growth Prediction Theories/
```

---

## Branch A — Vision

### ภาพดิบ (Raw Images)

#### `Normal_Age/`
ภาพ X-ray ข้อเข่าปกติของเด็ก แยกโฟลเดอร์ตามอายุผู้ป่วย (1 โฟลเดอร์ = 1 ราย)

| โฟลเดอร์ | อายุ (ปี) | จำนวนภาพ |
|---|---|---|
| Normal_Age_02 | 2 | 2 |
| Normal_Age_04 | 4 | 2 |
| Normal_Age_05 | 5 | 6 |
| Normal_Age_06 | 6 | 2 |
| Normal_Age_07 | 7 | 4 |
| Normal_Age_09 | 9 | 3 |
| Normal_Age_11 | 11 | 6 |
| Normal_Age_14 | 14 | 4 |
| Normal_Age_15 | 15 | 2 |
| Normal_Age_16 | 16 | 2 |
| Normal_Age_17 | 17 | 4 |
| **รวม** | | **37 ภาพ** |

**ชื่อไฟล์:** `{อายุ}.{มุมถ่าย} {เพศ}.{นามสกุล}`  
ตัวอย่าง: `14.1 M.jpeg` → อายุ 14 ปี, มุมที่ 1, เพศชาย  
ตัวอย่าง: `5.3 F.jpeg` → อายุ 5 ปี, มุมที่ 3, เพศหญิง  
รหัสเพศ: `M` = ชาย, `F` = หญิง

#### `Knee_Fracture/`
ภาพ X-ray รอยแตกแบบ Salter-Harris แยกตามประเภท

| ประเภท | จำนวนภาพ | คำอธิบาย |
|---|---|---|
| SH_Type_I | 4 | รอยแตกผ่าน physis เท่านั้น |
| SH_Type_II | 7 | physis + ชิ้นส่วน metaphysis |
| SH_Type_III | 3 | physis + ชิ้นส่วน epiphysis |
| SH_Type_IV | 4 | ผ่าน physis, metaphysis และ epiphysis |
| **รวม** | **18 ภาพ** | |

ชื่อไฟล์ใช้รูปแบบเดียวกับ Normal_Age

#### `ex type/`
ภาพตัวอย่างอ้างอิงจากวรรณกรรมทางการแพทย์ แสดงลักษณะของ SH แต่ละประเภท ใช้เป็นแนวทางการ annotate เท่านั้น — ไม่ใช้ในการ train

---

### ชุดข้อมูล CycleGAN (`Dataset/`)

สร้างโดย `synthetic_damage_generator.py` ภาพทุกใบถูก resize และ centre-pad ให้ขนาด **256×256 pixels**  
แบ่ง train/test ที่อัตราส่วน **85% / 15%** (random seed = 42)

| ชุดข้อมูล | Domain | เนื้อหา | จำนวน |
|---|---|---|---|
| trainA | ปกติ (A) | ข้อเข่าปกติ | 31 |
| testA | ปกติ (A) | ข้อเข่าปกติ | 6 |
| trainB | รอยแตก (B) | รอยแตก SH | 15 |
| testB | รอยแตก (B) | รอยแตก SH | 3 |

**ชื่อไฟล์ Domain A:** `A_{XXXX}.png` (ต่อเนื่อง เช่น `A_0001.png`)  
**ชื่อไฟล์ Domain B:** `B_{SH_Type}_{XXXX}.png` (เช่น `B_SH_Type_II_0003.png`)

> **หมายเหตุ:** ไฟล์ augmented จะมี `_aug_` ในชื่อ (เช่น `A_0001_aug_flip.png`) สคริปต์ต่าง ๆ จะข้ามไฟล์เหล่านี้โดยอัตโนมัติ

รายละเอียด trainB แยกตามประเภท SH:

| ประเภท SH | trainB | testB |
|---|---|---|
| Type I | 2 | 2 |
| Type II | 6 | 1 |
| Type III | 3 | 0 |
| Type IV | 4 | 0 |

---

### ไฟล์ Annotation — `xray_bounding_boxes.csv` / `.json`

เก็บ bounding box ของ physis สำหรับภาพในโฟลเดอร์ Dataset รวม **92 records** (Domain A = 2 กระดูกต่อภาพ, Domain B = 1 กระดูกต่อภาพ)

| คอลัมน์ | ประเภท | คำอธิบาย |
|---|---|---|
| `folder_name` | string | โฟลเดอร์ย่อย (`trainA`, `trainB`, `testA`, `testB`) |
| `filename` | string | ชื่อไฟล์ภาพ |
| `bone_type` | string | `Femur` หรือ `Tibia` |
| `side` | string | `Medial`, `Lateral`, `Unknown`, หรือ `N/A` (Domain A) |
| `X_Min` | int | ขอบซ้ายของ bounding box (px) |
| `Y_Min` | int | ขอบบนของ bounding box (px) |
| `X_Max` | int | ขอบขวาของ bounding box (px) |
| `Y_Max` | int | ขอบล่างของ bounding box (px) |
| `X_Bar` | int | จุดศูนย์กลาง X = (X_Min + X_Max) / 2 |
| `Y_Bar` | int | จุดศูนย์กลาง Y = (Y_Min + Y_Max) / 2 |
| `Salter_Type` | string | `Normal`, `SH_Type_I`, `SH_Type_II`, `SH_Type_III`, หรือ `SH_Type_IV` |

---

### สคริปต์

#### `synthetic_damage_generator.py`
จัดระเบียบภาพดิบจาก `Normal_Age/` และ `Knee_Fracture/` เข้าสู่โครงสร้าง `Dataset/` ของ CycleGAN

- `Normal_Age/` → `trainA/` และ `testA/` (Domain A)
- `Knee_Fracture/` → `trainB/` และ `testB/` (Domain B)
- Resize เป็น 256×256 ด้วย centre-padding (ขอบดำ)
- แบ่ง train/test 85/15 (random seed 42)

```bash
python synthetic_damage_generator.py
```

แก้ไข path ที่หัวสคริปต์ (`SOURCE_NORMAL`, `SOURCE_FRACTURE`, `OUTPUT_ROOT`) ก่อนรัน

#### `augment_data.py`
สร้างภาพ augmented เพิ่มเติมใน `trainA/` และ `trainB/` ภาพต้นฉบับแต่ละภาพจะได้ภาพ augmented 4 แบบ:

| Suffix | การแปลง |
|---|---|
| `_aug_flip` | กลับซ้าย-ขวา |
| `_aug_rot_p5` | หมุน +5° |
| `_aug_rot_m5` | หมุน −5° |
| `_aug_contrast` | เพิ่ม contrast (α=1.2, β=−10) |

```bash
python augment_data.py
```

#### `annotate_physis.py`
โปรแกรม GUI ด้วย OpenCV สำหรับวาดและบันทึก bounding box ของ physis

**Domain A (ปกติ):** วาดกล่อง 2 กล่องตามลำดับ — Femur ก่อน แล้ว Tibia กด `Enter` หรือ `Space` เพื่อบันทึก  
**Domain B (รอยแตก):** วาดกล่อง 1 กล่องรอบรอยแตก กด `F` (Femur) หรือ `T` (Tibia) แล้วกด `M` / `L` / `U` เพื่อบันทึก

| ปุ่ม | การทำงาน |
|---|---|
| `Enter` / `Space` | บันทึก annotation (Domain A) |
| `F` | เลือก Femur (Domain B) |
| `T` | เลือก Tibia (Domain B) |
| `M` / `L` / `U` | บันทึกเป็น Medial / Lateral / Unknown (Domain B) |
| `R` | รีเซ็ตภาพปัจจุบัน |
| `Q` / `Esc` | ออก (ข้อมูลที่บันทึกแล้วไม่หาย) |

บันทึกผลลัพธ์ลง `xray_bounding_boxes.csv` และสามารถรันต่อจากจุดที่ค้างได้

```bash
python annotate_physis.py
```

---

## Branch B — Clinical Data

### `synthetic_clinical_biases.csv` / `.json`

ข้อมูลผู้ป่วยสังเคราะห์ 1,000 ราย สร้างโดย `synthetic_bias_generator.py` (random seed 42) แต่ละ record จำลองผู้ป่วยเด็กที่มี physeal bar และพยากรณ์ผลการเจริญเติบโตที่ 1, 3 และ 5 ปี

**คอลัมน์หลัก:**

| คอลัมน์ | คำอธิบาย |
|---|---|
| `record_id` | รหัสผู้ป่วย (เช่น `REC_0001`) |
| `gender` | `M` (ชาย) หรือ `F` (หญิง) |
| `bone_age_years` | อายุกระดูก (ปี) |
| `maturity_limit_years` | อายุที่ physis ปิด (ชาย: 16, หญิง: 14) |
| `years_to_maturity` | เวลาการเจริญเติบโตที่เหลือ (ปี) |
| `bone_site` | `distal_femur` หรือ `proximal_tibia` |
| `fusion_stage` | `Stage_I`, `Stage_II`, หรือ `Stage_III` |
| `physeal_bar_area_pct` | พื้นที่ physeal bar คิดเป็น % ของ physis |
| `bar_location` | `Central` หรือ `Peripheral` |
| `pixel_spacing_mm` | ระยะ pixel spacing ของ X-ray (mm/px) |
| `d_px` / `d_mm` | เส้นผ่านศูนย์กลาง bar (pixel / มิลลิเมตร) |
| `pathology_code` | รหัส ICD-10 หรือรหัสยา; `NONE` = ไม่มีโรคร่วม |
| `pathology_base_weight` | ค่า modifier ผลกระทบทางคลินิก (0.70–1.00) |
| `pathology_severity_tier` | `Critical`, `High`, `Moderate`, `Low`, หรือ `Baseline` |
| `g0_rate_cm_per_year` | อัตราการเจริญเติบโตพื้นฐาน (cm/ปี) |
| `G_basal_remaining_cm` | การเจริญเติบโตที่เหลือโดยรวม (ไม่มี bar) (cm) |
| `G_fused_cm` | การเจริญเติบโตที่เหลือหลังปรับ fusion stage |
| `G_undamaged_remaining_cm` | การเจริญเติบโตที่เหลือหลังปรับ pathology |
| `delta_theta_deg_per_year` | อัตราการเบี้ยวของกระดูก (°/ปี) |
| `projected_LLD_cm_yr{1,3,5}` | การพยากรณ์ความยาวขาไม่เท่ากัน LLD (cm) |
| `projected_deformity_deg_yr{1,3,5}` | การพยากรณ์มุมความเบี้ยว (°) |
| `lld_5yr_severity` | ความรุนแรง LLD ที่ 5 ปี (`None`, `Mild`, `Moderate`, `Severe`) |
| `deformity_5yr_severity` | ความรุนแรงของความเบี้ยวที่ 5 ปี |
| `intervention_flag` | `True` หากแนะนำให้ผ่าตัด |

การเจริญเติบโตพยากรณ์ด้วย **กฎ Hueter-Volkmann**: `G = G₀ × (1 − β × σ)`

### `clinical_bias_weights.json`

นิยาม modifier ผลกระทบทางคลินิกแยกตามระดับความรุนแรง แต่ละรายการแมปรหัส ICD-10 หรือรหัสยาไปยัง weight ที่คูณกับการเจริญเติบโตที่เหลือ

| Weight | ระดับ | ความหมายทางคลินิก |
|---|---|---|
| 0.70 | Critical | ความเสียหายต่อ physis ถาวร (เช่น Osteogenesis Imperfecta, เคมีบำบัด) |
| 0.80 | High | การรบกวนระบบเรื้อรัง (เช่น Hypothyroidism, Juvenile Arthritis) |
| 0.90 | Moderate | ผลกระทบด้านเมตาบอลิซึมหรือโภชนาการ (เช่น ขาดวิตามิน D, โรคหืด) |
| 0.95 | Low | ผลกระทบต่อการเจริญเติบโตเล็กน้อย (เช่น โรคอ้วน, กระดูกสันหลังคด) |
| 1.00 | Baseline | ไม่มีโรคร่วม |

### `zscores/`

ตาราง growth reference ของ WHO 2007 ใช้สำหรับ normalize อายุกระดูกและคำนวณ BMI z-score

| ไฟล์ | ข้อมูล |
|---|---|
| `bmi-boys-z-who-2007-exp.xlsx` | BMI-for-age z-scores เด็กชาย 5–19 ปี |
| `bmi-girls-z-who-2007-exp.xlsx` | BMI-for-age z-scores เด็กหญิง 5–19 ปี |
| `wfh_boys_2-to-5-years_zscores.xlsx` | Weight-for-height z-scores เด็กชาย 2–5 ปี |
| `wfh_girls_2-to-5-years_zscores.xlsx` | Weight-for-height z-scores เด็กหญิง 2–5 ปี |
| `wfl_boys_0-to-2-years_zscores.xlsx` | Weight-for-length z-scores เด็กชาย 0–2 ปี |
| `wfl_girls_0-to-2-years_zscores.xlsx` | Weight-for-length z-scores เด็กหญิง 0–2 ปี |

### `synthetic_bias_generator.py`

สร้าง `synthetic_clinical_biases.csv` และ `.json` ปรับค่าคงที่ได้ที่หัวสคริปต์ (N_RECORDS, RANDOM_SEED, อัตราการเจริญเติบโต, pathology pools ฯลฯ)

```bash
python synthetic_bias_generator.py
```

---

## References

เอกสารอ้างอิงสำหรับ annotation schema, clinical parameters และโมเดลพยากรณ์การเจริญเติบโต ทุกไฟล์เป็น PDF

| โฟลเดอร์ | เนื้อหา |
|---|---|
| `Annotation and Anatomy/` | การจำแนกประเภท Salter-Harris (Tachdjian), กายวิภาคข้อเข่า, บทความ EOR |
| `Clinical Bias Parameters/` | วรรณกรรมเกี่ยวกับโรคและยาที่ส่งผลต่อการเจริญเติบโตของ physis (คอร์ติโคสเตียรอยด์, เคมีบำบัด, ยากดภูมิ, CNS stimulants ฯลฯ) |
| `Growth Prediction Theories/` | การเจริญเติบโตและพัฒนาการ (Tachdjian Vol. 1), การจัดการ Limb Length Discrepancy |

---

## ขั้นตอนการเริ่มต้น (Quick-Start)

เพื่อสร้าง Dataset จากภาพดิบใหม่ทั้งหมด:

1. รัน `synthetic_damage_generator.py` — สร้างโฟลเดอร์ `Dataset/{trainA,testA,trainB,testB}/`
2. รัน `augment_data.py` — เพิ่มไฟล์ `_aug_*` ใน `trainA/` และ `trainB/`
3. รัน `annotate_physis.py` — วาด bounding box บันทึกลง `xray_bounding_boxes.csv`
4. รัน `synthetic_bias_generator.py` — สร้าง `synthetic_clinical_biases.csv/.json` ใหม่

> สคริปต์ทุกตัวมี path แบบ hard-code อยู่ที่หัวไฟล์ — กรุณาแก้ไขให้ตรงกับ directory ของเครื่องก่อนรัน
