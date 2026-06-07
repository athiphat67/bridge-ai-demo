"""POST /api/analyze — endpoint หลัก คืนผลครบ 3 ส่วนใน response เดียว

รับได้ 2 แบบ (ดู ARCHITECTURE.md §3):
  (ก) sample_id          → ใช้ clinical + label จาก metadata
  (ข) image + clinical   → clinical จากฟอร์ม, match label ด้วย filename (ไม่เจอ → ค่ากลาง)
"""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas import (AnalysisResult, BarBox, ClinicalInput,
                       GrowthPrediction)
from ..services import scoring
from ..services.growth import predict
from ..services.metadata import get_by_filename, get_by_id
from ..services.visualize import render

router = APIRouter()

_DEFAULT_BAR_AREA = 45.0   # fallback เมื่อภาพอัปโหลดไม่มี label


def _clinical_from_dict(c: dict) -> ClinicalInput:
    return ClinicalInput(**c)


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(
    sample_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    age_years: Optional[float] = Form(None),
    bone_age_years: Optional[float] = Form(None),
    gender: Optional[str] = Form(None),
    weight_kg: Optional[float] = Form(None),
    height_cm: Optional[float] = Form(None),
    location: Optional[str] = Form(None),
    medical_history: Optional[str] = Form(None),  # comma-separated
):
    # --- resolve clinical + label + ภาพ จาก 2 ทาง ---
    if sample_id:
        case = get_by_id(sample_id)
        if not case:
            raise HTTPException(404, f"ไม่พบ sample_id: {sample_id}")
        clinical = _clinical_from_dict(case["clinical"])
        label = case.get("label", {})
        filename = case["filename"]
    elif image is not None:
        if None in (age_years, gender, weight_kg, height_cm, location):
            raise HTTPException(422, "ต้องกรอก clinical input ให้ครบเมื่ออัปโหลดภาพเอง")
        clinical = ClinicalInput(
            age_years=age_years, bone_age_years=bone_age_years, gender=gender,
            weight_kg=weight_kg, height_cm=height_cm, location=location,
            medical_history=[s.strip() for s in (medical_history or "").split(",") if s.strip()],
        )
        case = get_by_filename(image.filename)
        label = case.get("label", {}) if case else {}
        filename = case["filename"] if case else None   # unmatched → placeholder
    else:
        raise HTTPException(422, "ต้องส่ง sample_id หรือ image อย่างใดอย่างหนึ่ง")

    # --- คำนวณ mock outputs ---
    bar_area = float(label.get("bar_area_percent", _DEFAULT_BAR_AREA))
    box_data = label.get("bar_box")
    box = BarBox(**box_data) if box_data else None

    score = scoring.risk_score(bar_area, clinical.age_years,
                               clinical.location, clinical.medical_history)
    growth: GrowthPrediction = predict(bar_area, clinical.age_years,
                                       clinical.gender, clinical.location)

    return AnalysisResult(
        overlay_image=render(filename, box, bar_area),
        damage_percent=round(bar_area, 1),
        risk_level=scoring.risk_level(score),
        salter_harris=scoring.salter_harris(label.get("salter_harris"), bar_area),
        bend_direction=scoring.bend_direction(clinical.location),
        growth_prediction=growth,
        factors=scoring.build_factors(bar_area, clinical.age_years,
                                      clinical.location, clinical.medical_history),
    )
