"""Growth prediction — กราฟแนวโน้ม 1/3/5 ปี

อิงสูตรใน KneeGrowth-AI.pdf (ใช้เป็นฟังก์ชัน deterministic ง่ายๆ เพื่อความน่าเชื่อถือ ไม่ต้องแม่นจริง):
- Hueter-Volkmann:  G = G0 · (1 − β·σ)   → ฝั่งที่โดน bar โตช้าลง
- leg-length diff(t) ≈ (G0 − G_damaged) · t
- angular(t)        ≈ Δθ · t,  Δθ ∝ G_undamaged / d   (Geometric Tethering)
"""
from ..schemas import GrowthPrediction, GrowthProbabilities

YEARS = [0, 1, 3, 5]
_GROWTH_START_AGE = 2.0   # อายุอ้างอิงเริ่มนับศักยภาพการโต (longitudinal)


def _maturity_age(gender: str) -> float:
    """อายุที่ growth plate ปิด (skeletal maturity)"""
    return 14.0 if gender == "female" else 16.0


def _basal_growth_rate(age: float, gender: str) -> float:
    """G0 (mm/ปี) อัตราการเจริญเติบโตพื้นฐาน — ยิ่งเด็ก ยิ่งเหลือโตเยอะ"""
    g0 = max(0.0, (16 - age) * 0.7)          # age 6 → ~7 mm/ปี, age 15 → ~0.7
    if gender == "female":
        g0 *= 0.9                             # ผู้หญิงปิด growth plate เร็วกว่า
    return g0


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _remaining_growth(bar_area: float, age: float, gender: str) -> tuple[float, float]:
    """ศักยภาพการเติบโตที่เหลือ (%) — เทียบกับเด็กปกติวัยเดียวกัน

    - normal_remaining: เด็กปกติวัยนี้ยังเหลือโตอีกกี่ % ของช่วงการโตทั้งหมด
    - affected_remaining: ฝั่งที่มี physeal bar เหลือศักยภาพเท่าไร
      (Hueter-Volkmann: physeal bar กิน growth plate ไป bar_frac → เหลือ 1−bar_frac)
    """
    maturity = _maturity_age(gender)
    span = maturity - _GROWTH_START_AGE
    normal_remaining = _clamp((maturity - age) / span * 100.0) if span > 0 else 0.0

    bar_frac = bar_area / 100.0
    affected_remaining = _clamp(normal_remaining * (1 - bar_frac))
    return round(affected_remaining, 1), round(normal_remaining, 1)


def _probabilities(bar_area: float, age: float, gender: str, location: str) -> GrowthProbabilities:
    """โอกาส 3 รูปแบบ (รวม = 100%) — deterministic mock

    - bar กว้าง → growth plate ปิดเกือบหมด → "หยุดโต" (arrest) เด่น
    - bar แคบ–กลาง → โตไม่สมมาตร → เกิด "ขาเอียง" ตามตำแหน่ง bar
      medial bar → Varus (ขาโก่งออก), lateral bar → Valgus (ขาฉิ่งเข้า)
    - เด็กเล็กยังเหลือโตมาก → แนวโน้มเอียงเด่นกว่าหยุดโต
    """
    maturity = _maturity_age(gender)
    age_factor = 1.0 if age < 8 else 0.85 if age < maturity else 0.6
    arrest = _clamp(bar_area * 0.75 * (2 - age_factor), 5, 92)
    deform = 100.0 - arrest

    # medial bar → Varus (ขาโก่งออก), lateral bar → Valgus (ขาฉิ่งเข้า)
    if location == "medial":
        varus = deform * 0.82          # ขาโก่งออก
        valgus = deform - varus
    else:
        valgus = deform * 0.82         # ขาฉิ่งเข้า
        varus = deform - valgus

    return GrowthProbabilities(
        varus_percent=round(varus, 1),
        valgus_percent=round(valgus, 1),
        arrest_percent=round(arrest, 1),
    )


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

    remaining, normal_remaining = _remaining_growth(bar_area, age, gender)

    return GrowthPrediction(
        years=[float(y) for y in YEARS],
        leg_length_diff_mm=[round(leg_rate * y, 1) for y in YEARS],
        angular_deg=[round(angular_rate * y, 1) for y in YEARS],
        remaining_growth_percent=remaining,
        normal_remaining_percent=normal_remaining,
        probabilities=_probabilities(bar_area, age, gender, location),
    )
