# `data/` — ข้อมูล X-ray จาก Namthip

ข้อมูลดิบ + ข้อมูลที่ผ่านการเตรียมแล้ว ใช้เป็นวัตถุดิบให้ `scripts/build_demo_data.py`
สร้าง `backend/app/data/metadata.json` + `backend/app/data/samples/` (ดู [DATA_CONTRACT.md](../DATA_CONTRACT.md))

## โครงสร้าง

```
data/
├── raw/                  # ภาพต้นฉบับ (ก่อน resize/label) — เก็บไว้อ้างอิง ไม่ได้ใช้ตรงใน demo
│   ├── Knee_Fracture/    # ภาพ X-ray fracture จริง แยกตามเกรด Salter-Harris
│   │   ├── SH_Type_I/ … SH_Type_IV/
│   │   └── ชื่อไฟล์เข้ารหัส "<อายุ>.<ลำดับ> <เพศ>.jpg" เช่น "14.1 M.jpg" = เด็กชาย 14 ปี
│   ├── Normal_Age/       # ภาพ X-ray ปกติ แยกตามกลุ่มอายุ (Normal_Age_02 … Normal_Age_17)
│   └── reference/        # ภาพอ้างอิงจากเปเปอร์ (เช่น EOR-21-0110fig9.jpg) ใช้ตอน label
│
├── processed/            # output ของ prep_scripts/ — ใช้จริงโดย scripts/build_demo_data.py
│   ├── CycleGAN_Dataset/  # ภาพ 256x256, แบ่ง train/test
│   │   ├── trainA/ testA/  # = ภาพปกติ (จาก Normal_Age)
│   │   └── trainB/ testB/  # = ภาพ fracture (จาก Knee_Fracture, ตั้งชื่อ B_SH_Type_<grade>_xxxx.png)
│   ├── dataset_labels.csv   # bounding box (pixel, บนภาพ 256x256) + Salter-Harris grade ต่อภาพ/กระดูก
│   └── dataset_labels.json  # = csv ตัวเดียวกัน แปลงเป็น JSON (ไม่ได้ใช้โดย backend)
│
└── prep_scripts/         # สคริปต์เตรียมข้อมูลของ Namthip (รันบนเครื่องเธอ ไม่ใช่ส่วนของ demo app)
    ├── image_formatter.py   # raw/Knee_Fracture + raw/Normal_Age → processed/CycleGAN_Dataset (resize 256x256 + train/test split)
    ├── annotate_physis.py   # เปิดภาพใน CycleGAN_Dataset ให้ label bounding box → เขียน dataset_labels.csv
    ├── convert_to_json.py   # dataset_labels.csv → dataset_labels.json
    └── augment_data.py      # data augmentation (flip/brightness) สำหรับ CycleGAN training
```

## Pipeline (ลำดับที่ data ถูกสร้าง)

```
raw/Knee_Fracture, raw/Normal_Age
        │  image_formatter.py
        ▼
processed/CycleGAN_Dataset (256x256, train/test split)
        │  annotate_physis.py
        ▼
processed/dataset_labels.csv  (pixel bbox + Salter-Harris grade)
        │  scripts/build_demo_data.py  ← ดู ../scripts/README.md
        ▼
backend/app/data/metadata.json + backend/app/data/samples/  (ใช้จริงใน demo app)
```

## หมายเหตุ

- `prep_scripts/*.py` มี path hardcode แบบ `C:\Data Collection\...` (รันบนเครื่อง Windows ของ Namthip)
  — **ไม่ต้องรันสคริปต์เหล่านี้ในเครื่อง dev** เว้นแต่จะ re-generate `processed/` ใหม่ทั้งหมด
- ถ้าได้ data ชุดใหม่จาก Namthip: วาง `processed/CycleGAN_Dataset/` + `dataset_labels.csv` ทับของเดิม
  แล้วรัน `python3 scripts/build_demo_data.py` ใหม่ (idempotent — รันซ้ำได้ปลอดภัย)
