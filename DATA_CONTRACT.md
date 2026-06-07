# Data Contract — รูปแบบไฟล์ที่ Namthip ส่งให้ (v1)

> ⚠️ **สำคัญ:** ไฟล์นี้คือ "สัญญา" ระหว่างทีมเตรียมข้อมูล (Namthip) กับ demo app
> ถ้า label ตามรูปแบบนี้ → data วาง drop เข้า app ได้ทันที ไม่ต้องแก้โค้ด
> ส่งให้ Namthip **ก่อน** เริ่ม label จริง (target: เสาร์ 7 มิ.ย.)

---

## 1. โครงสร้างโฟลเดอร์ที่ส่งมา

```
bridge_demo_data/
├── images/
│   ├── case_low_age12_lateral.png
│   ├── case_medium_age9_medial.png
│   └── case_high_age6_medial.png
└── metadata.json
```

- รูปภาพ: **PNG หรือ JPG**, แนะนำด้านยาว ~800–1200 px
- ตั้งชื่อไฟล์เป็น ASCII (a-z, 0-9, _) ห้ามเว้นวรรค/ภาษาไทยในชื่อไฟล์
- อย่างน้อย **3 เคส**: Low / Medium / High (เพื่อโชว์ในวิดีโอครบทุกระดับ)

---

## 2. รูปแบบ `metadata.json`

```json
{
  "version": 1,
  "cases": [
    {
      "id": "case_high",
      "filename": "case_high_age6_medial.png",
      "display_name": "เด็กชาย 6 ขวบ – Medial Bar รุนแรง",

      "clinical": {
        "age_years": 6,
        "bone_age_years": 5.5,
        "gender": "male",
        "weight_kg": 22,
        "height_cm": 115,
        "location": "medial",
        "medical_history": ["corticosteroid"]
      },

      "label": {
        "bar_area_percent": 62,
        "salter_harris": "III",
        "bar_box": { "x": 0.45, "y": 0.52, "w": 0.12, "h": 0.14 }
      }
    }
  ]
}
```

---

## 3. คำอธิบายแต่ละฟิลด์

### `clinical` — สิ่งที่หมอกรอกเอง (ใช้เป็นค่า default เวลา demo)
| ฟิลด์ | ชนิด | ตัวอย่าง | หมายเหตุ |
|------|------|---------|----------|
| `age_years` | number | 6 | อายุจริง |
| `bone_age_years` | number | 5.5 | อายุกระดูก |
| `gender` | `"male"` / `"female"` | male | |
| `weight_kg` | number | 22 | |
| `height_cm` | number | 115 | app คำนวณ BMI เอง |
| `location` | `"medial"` / `"lateral"` | medial | ตำแหน่ง bar |
| `medical_history` | string[] | `["corticosteroid"]` | ว่าง `[]` ได้ |

### `label` — สิ่งที่มาจากการ label ภาพ (แทน Branch A / CV ในระบบจริง)
| ฟิลด์ | ชนิด | ตัวอย่าง | หมายเหตุ |
|------|------|---------|----------|
| `bar_area_percent` | number 0–100 | 62 | = **Physeal Plate Damage %** ตัวเลข hero ที่โชว์บนภาพ |
| `salter_harris` | `"I"`–`"V"` | III | เกรดความรุนแรง |
| `bar_box` | object | ดูข้างล่าง | กรอบที่จะวาด Bounding Box / Heatmap |

### `bar_box` — ⭐ จุดที่พังง่ายสุด ต้องเป็น **สัดส่วน 0–1 เท่านั้น**
```
x, y = มุมซ้ายบนของกรอบ (เป็นสัดส่วนของความกว้าง/สูงภาพ)
w, h = ความกว้าง/สูงของกรอบ (เป็นสัดส่วน)
```
ตัวอย่าง: ภาพกว้าง 1000px ถ้า bar อยู่กลางๆ เริ่มที่ pixel 450 → `x = 0.45`

> ❗ **ห้ามใส่เป็น pixel** เพราะหน้าจอย่อ/ขยายภาพ ถ้าใช้ pixel กรอบจะเลื่อนหลุดตำแหน่ง
> ใช้สัดส่วน 0–1 แล้ว app จะวาดถูกที่ทุกขนาดหน้าจอ

---

## 4. ถ้า field ไหนยังไม่มี
- ใส่เท่าที่มี — app มี fallback ให้ field ที่ขาด (ใช้ค่ากลางๆ / ตำแหน่งกึ่งกลางภาพ)
- แต่ `filename` + `bar_box` + `bar_area_percent` คือ 3 ตัวที่ทำให้ภาพในวิดีโอออกมาเป๊ะ ควรมีให้ครบ

---

## 5. Fallback ถ้า data ไม่ทันวันอาทิตย์
ตามที่ Namthip ยืนยัน → ใช้ open data ทดแทนได้ (Radiopaedia normal pediatric knee + synthetic bar)
app ทำงานได้เลยขอแค่ metadata.json ตามรูปแบบนี้
