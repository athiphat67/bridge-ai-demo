"""Mock scoring — deterministic (input เดียวกัน → ผลเดิมเสมอ)

ตัวขับหลัก: bar_area % (จาก label) + อายุ + ตำแหน่ง + ประวัติยา
รายละเอียดแนวคิดสูตรอยู่ใน ARCHITECTURE.md §3
"""
from ..config import RISK_LOW_MAX, RISK_MED_MAX
from ..schemas import Factor


def _clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, v))


def risk_score(bar_area: float, age: float, location: str,
               medical_history: list[str]) -> float:
    """0–100 — เด็กเล็ก + medial + bar กว้าง + ใช้ steroid = เสี่ยงสูง"""
    score = bar_area
    score += 25 if age < 8 else 12 if age <= 14 else 3        # ยิ่งเด็ก ยิ่งเสี่ยง
    score += 15 if location == "medial" else 8                 # medial เสี่ยงกว่า
    if any("cortico" in m.lower() or "steroid" in m.lower()
           for m in medical_history):
        score += 10                                            # negative bias ต่อ osteogenesis
    return _clamp(score)


def risk_level(score: float) -> str:
    if score < RISK_LOW_MAX:
        return "Low"
    if score < RISK_MED_MAX:
        return "Medium"
    return "High"


def salter_harris(label_grade: str | None, bar_area: float) -> str:
    """ใช้ค่าจาก label เป็นหลัก; ถ้าไม่มีก็ประมาณจาก bar_area"""
    if label_grade:
        return label_grade
    if bar_area < 25:
        return "II"
    if bar_area < 50:
        return "III"
    return "IV"


def bend_direction(location: str) -> str:
    return "Varus" if location == "medial" else "Valgus"


def build_factors(bar_area: float, age: float, location: str,
                  medical_history: list[str]) -> list[Factor]:
    factors = [
        Factor(label=f"Physeal Bar Area {bar_area:.0f}%",
               impact="high" if bar_area >= 50 else "medium" if bar_area >= 25 else "low"),
        Factor(label=f"ตำแหน่ง {'Medial' if location == 'medial' else 'Lateral'}",
               impact="high" if location == "medial" else "medium"),
        Factor(label=f"อายุ {age:.0f} ปี" + (" (กระดูกยังโตอีกมาก)" if age < 8 else ""),
               impact="high" if age < 8 else "medium" if age <= 14 else "low"),
    ]
    if any("cortico" in m.lower() or "steroid" in m.lower() for m in medical_history):
        factors.append(Factor(label="ประวัติใช้ Corticosteroid", impact="medium"))
    return factors
