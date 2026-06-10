"""วาด Bounding Box + Heatmap ลงบนภาพ X-ray → base64 PNG data URL

- พิกัด bar_box เป็นสัดส่วน 0–1 → คูณด้วยขนาดภาพจริง (รองรับทุกขนาด)
- ถ้าไฟล์ภาพยังไม่มี (ก่อน Namthip ส่ง data) → สร้าง placeholder ให้ endpoint ทำงานได้
"""
import base64
import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..config import (BOX_COLOR, BOX_WIDTH, HEATMAP_ALPHA, HEATMAP_COLOR,
                      SAMPLES_DIR)
from ..schemas import BarBox

_DEFAULT_BOX = BarBox(x=0.42, y=0.45, w=0.16, h=0.18)   # กึ่งกลางค่อนล่าง (บริเวณ growth plate)


def _load_or_placeholder(filename: str | None) -> Image.Image:
    if filename:
        path = SAMPLES_DIR / filename
        if path.exists():
            return Image.open(path).convert("RGB")
    return _placeholder()


def _placeholder(w: int = 700, h: int = 900) -> Image.Image:
    """ภาพ X-ray จำลอง (gradient เทา + แท่งกระดูกคร่าวๆ) ใช้ก่อนได้ data จริง"""
    grad = np.tile(np.linspace(30, 90, h, dtype=np.uint8)[:, None], (1, w))
    img = Image.fromarray(np.stack([grad] * 3, axis=-1), "RGB")
    d = ImageDraw.Draw(img)
    cx = w // 2
    d.rectangle([cx - 70, 40, cx + 70, h // 2], fill=(150, 150, 150))      # femur
    d.rectangle([cx - 80, h // 2 + 30, cx + 80, h - 40], fill=(150, 150, 150))  # tibia
    d.ellipse([cx - 95, h // 2 - 30, cx + 95, h // 2 + 60], fill=(175, 175, 175))  # joint
    return img


def _apply_heatmap(img: Image.Image, box: BarBox,
                   damage_percent: float) -> Image.Image:
    w, h = img.size
    cx, cy = (box.x + box.w / 2) * w, (box.y + box.h / 2) * h
    sigma = max(box.w * w, box.h * h) * 0.6

    # ความเข้มแปรตามระดับ damage — เคสปกติ (0%) ไม่มีปื้นแดง, เคสหนักแดงเข้ม
    intensity = HEATMAP_ALPHA * (max(0.0, min(100.0, damage_percent)) / 100) ** 0.5

    yy, xx = np.mgrid[0:h, 0:w]
    blob = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma ** 2)))
    alpha = (blob * intensity)[..., None]                  # HxWx1

    base = np.asarray(img, dtype=np.float32)
    color = np.array(HEATMAP_COLOR, dtype=np.float32)
    blended = base * (1 - alpha) + color * alpha
    return Image.fromarray(blended.clip(0, 255).astype(np.uint8), "RGB")


def render(filename: str | None, box: BarBox | None,
           damage_percent: float) -> str:
    box = box or _DEFAULT_BOX
    img = _load_or_placeholder(filename)
    img = _apply_heatmap(img, box, damage_percent)

    w, h = img.size
    d = ImageDraw.Draw(img)
    x0, y0 = box.x * w, box.y * h
    x1, y1 = (box.x + box.w) * w, (box.y + box.h) * h
    d.rectangle([x0, y0, x1, y1], outline=BOX_COLOR, width=BOX_WIDTH)

    label = f"Physeal Plate Damage {damage_percent:.0f}%"
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    ty = max(0, y0 - 28)
    d.rectangle([x0, ty, x0 + 9 * len(label), ty + 26], fill=(0, 0, 0))
    d.text((x0 + 4, ty + 2), label, fill=BOX_COLOR, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"
