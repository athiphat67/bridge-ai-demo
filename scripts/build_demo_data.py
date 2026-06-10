"""สร้าง demo data จริงจาก data/processed (Namthip) → ตาม DATA_CONTRACT.md

อ่าน dataset_labels.csv (พิกัด pixel บนภาพ 256x256) → เลือกเคส Normal/Low/Medium/High
→ แปลงกรอบเป็นสัดส่วน 0-1 + อัปสเกลภาพเป็น 768px
→ เขียน backend/app/data/metadata.json + ก๊อปภาพเข้า backend/app/data/samples/

รันซ้ำได้เสมอ (idempotent): python3 scripts/build_demo_data.py
"""
import csv
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
LABELS_CSV = PROCESSED_DIR / "dataset_labels.csv"
CYCLEGAN = PROCESSED_DIR / "CycleGAN_Dataset"
SAMPLES_DIR = ROOT / "backend" / "app" / "data" / "samples"
METADATA_PATH = ROOT / "backend" / "app" / "data" / "metadata.json"

TARGET_SIZE = 768   # อัปสเกลจาก 256 ให้คมพอสำหรับอัดวิดีโอ
BOX_PAD_PX = 5      # ขยายกรอบจาก label เล็กน้อย ให้ครอบ physis สวยขึ้น

# เคสที่คัดมาโชว์ในวิดีโอ — เรียงลำดับตามที่อยากให้ขึ้นใน sample picker
# (folder, filename) ต้องตรงกับแถวใน dataset_labels.csv
# อายุ/เพศอิงช่วงอายุจากชื่อไฟล์ต้นฉบับในโฟลเดอร์ Knee_Fracture (เช่น "14.1 M.jpg")
CASES = [
    {
        "id": "case_normal",
        "src": ("testA", "A_0033.png"),
        "bone": "Femur",
        "out": "case_normal_age11.png",
        "display_name": "เด็กหญิง 11 ปี – Growth Plate ปกติ (ไม่พบ bar)",
        "clinical": {
            "age_years": 11, "bone_age_years": 11, "gender": "female",
            "weight_kg": 36, "height_cm": 145, "location": "lateral",
            "medical_history": [],
        },
        "label": {"bar_area_percent": 0, "salter_harris": "Normal"},
    },
    {
        "id": "case_low",
        "src": ("trainB", "B_SH_Type_I_0011.png"),
        "bone": "Femur",
        "out": "case_low_sh1_age14_lateral.png",
        "display_name": "เด็กชาย 14 ปี – SH Type I Lateral (เสี่ยงต่ำ)",
        "clinical": {
            "age_years": 14, "bone_age_years": 14.5, "gender": "male",
            "weight_kg": 52, "height_cm": 165, "location": "lateral",
            "medical_history": [],
        },
        "label": {"bar_area_percent": 14, "salter_harris": "I"},
    },
    {
        "id": "case_medium",
        "src": ("trainB", "B_SH_Type_III_0001.png"),
        "bone": "Tibia",
        "out": "case_medium_sh3_age11_lateral.png",
        "display_name": "เด็กหญิง 11 ปี – SH Type III Lateral Tibia (เสี่ยงกลาง)",
        "clinical": {
            "age_years": 11, "bone_age_years": 10.5, "gender": "female",
            "weight_kg": 35, "height_cm": 144, "location": "lateral",
            "medical_history": [],
        },
        "label": {"bar_area_percent": 38, "salter_harris": "III"},
    },
    {
        "id": "case_high",
        "src": ("trainB", "B_SH_Type_IV_0010.png"),
        "bone": "Tibia",
        "out": "case_high_sh4_age13_medial.png",
        "display_name": "เด็กชาย 13 ปี – SH Type IV Medial Tibia (เสี่ยงสูง)",
        "clinical": {
            "age_years": 13, "bone_age_years": 12.5, "gender": "male",
            "weight_kg": 45, "height_cm": 158, "location": "medial",
            "medical_history": ["corticosteroid"],
        },
        "label": {"bar_area_percent": 62, "salter_harris": "IV"},
    },
]


def load_labels() -> dict:
    """(folder, filename, bone_type) → row จาก CSV"""
    rows = {}
    with open(LABELS_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["folder_name"], r["filename"], r["bone_type"])] = r
    return rows


def to_bar_box(row: dict, img_w: int, img_h: int) -> dict:
    """พิกัด pixel จาก label → สัดส่วน 0-1 (DATA_CONTRACT.md §3) + pad เล็กน้อย"""
    x0 = max(0, int(row["X_Min"]) - BOX_PAD_PX)
    y0 = max(0, int(row["Y_Min"]) - BOX_PAD_PX)
    x1 = min(img_w, int(row["X_Max"]) + BOX_PAD_PX)
    y1 = min(img_h, int(row["Y_Max"]) + BOX_PAD_PX)
    return {
        "x": round(x0 / img_w, 4), "y": round(y0 / img_h, 4),
        "w": round((x1 - x0) / img_w, 4), "h": round((y1 - y0) / img_h, 4),
    }


def main() -> None:
    labels = load_labels()
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    cases_out = []

    for case in CASES:
        folder, fname = case["src"]
        row = labels[(folder, fname, case["bone"])]
        src_path = CYCLEGAN / folder / fname

        img = Image.open(src_path).convert("RGB")
        bar_box = to_bar_box(row, *img.size)
        img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS).save(
            SAMPLES_DIR / case["out"])

        cases_out.append({
            "id": case["id"],
            "filename": case["out"],
            "display_name": case["display_name"],
            "clinical": case["clinical"],
            "label": {**case["label"], "bar_box": bar_box},
        })
        print(f"✓ {case['id']}: {folder}/{fname} → {case['out']}  box={bar_box}")

    METADATA_PATH.write_text(
        json.dumps({"version": 1, "cases": cases_out}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"✓ เขียน {METADATA_PATH.relative_to(ROOT)} ({len(cases_out)} เคส)")


if __name__ == "__main__":
    main()
