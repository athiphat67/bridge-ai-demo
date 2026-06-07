"""Growth prediction — กราฟแนวโน้ม 1/3/5 ปี

อิงสูตรใน KneeGrowth-AI.pdf (ใช้เป็นฟังก์ชัน deterministic ง่ายๆ เพื่อความน่าเชื่อถือ ไม่ต้องแม่นจริง):
- Hueter-Volkmann:  G = G0 · (1 − β·σ)   → ฝั่งที่โดน bar โตช้าลง
- leg-length diff(t) ≈ (G0 − G_damaged) · t
- angular(t)        ≈ Δθ · t,  Δθ ∝ G_undamaged / d   (Geometric Tethering)
"""
from ..schemas import GrowthPrediction

YEARS = [0, 1, 3, 5]


def _basal_growth_rate(age: float, gender: str) -> float:
    """G0 (mm/ปี) อัตราการเจริญเติบโตพื้นฐาน — ยิ่งเด็ก ยิ่งเหลือโตเยอะ"""
    g0 = max(0.0, (16 - age) * 0.7)          # age 6 → ~7 mm/ปี, age 15 → ~0.7
    if gender == "female":
        g0 *= 0.9                             # ผู้หญิงปิด growth plate เร็วกว่า
    return g0


def predict(bar_area: float, age: float, gender: str,
            location: str) -> GrowthPrediction:
    g0 = _basal_growth_rate(age, gender)
    bar_frac = bar_area / 100.0

    # ฝั่งที่มี bar โตช้าลงตามสัดส่วน bar (Hueter-Volkmann, β·σ ≈ bar_frac)
    g_damaged = g0 * (1 - bar_frac)
    leg_rate = g0 - g_damaged                 # = g0 · bar_frac (mm/ปี)

    # มุมโก่ง: bar ยิ่งเบี้ยวข้าง (peripheral) d ยิ่งเล็ก → โก่งเร็ว
    d_norm = 0.7 if location == "medial" else 1.0   # medial เบี้ยวชัดกว่าใน mock นี้
    angular_rate = (g0 * bar_frac) / d_norm * 0.9   # องศา/ปี (สเกล mock)

    return GrowthPrediction(
        years=[float(y) for y in YEARS],
        leg_length_diff_mm=[round(leg_rate * y, 1) for y in YEARS],
        angular_deg=[round(angular_rate * y, 1) for y in YEARS],
    )
