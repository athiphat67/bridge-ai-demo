"""POST /api/analyze — sample metadata or real C1+C2 inference."""
import asyncio
import io
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from ..schemas import AnalysisResult, BarBox, ClinicalInput, Factor, GrowthPrediction
from ..services import scoring, vision
from ..services.growth import predict
from ..services.metadata import get_by_id
from ..services.visualize import render

router = APIRouter()
log = logging.getLogger("bridge-ai")

_DEFAULT_BAR_AREA = 45.0   # fallback เมื่อภาพอัปโหลดไม่มี label
_REAL_MODEL_NOTE = (
    "C1 detects the physis and C2 reports fracture probability. C3 is deferred, "
    "so the percentage shown is C2 fracture confidence, not measured damage area."
)


def _clinical_from_dict(c: dict) -> ClinicalInput:
    return ClinicalInput(**c)


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(
    mode: str = Form("sample"),
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
    if mode not in {"sample", "real"}:
        raise HTTPException(422, "mode must be 'sample' or 'real'")

    if mode == "sample":
        if not sample_id:
            raise HTTPException(422, "sample_id is required in sample mode")
        case = get_by_id(sample_id)
        if not case:
            raise HTTPException(404, f"Sample not found: {sample_id}")
        clinical = _clinical_from_dict(case["clinical"])
        label = case.get("label", {})
        filename = case["filename"]
        bar_area = float(label.get("bar_area_percent", _DEFAULT_BAR_AREA))
        box_data = label.get("bar_box")
        box = BarBox(**box_data) if box_data else None
        return _result(clinical, bar_area, render(filename, box, bar_area),
                       label.get("salter_harris"))

    if image is None:
        raise HTTPException(422, "image is required in real mode")
    if None in (age_years, gender, weight_kg, height_cm, location):
        raise HTTPException(422, "Clinical input fields are required in real mode")

    clinical = ClinicalInput(
        age_years=age_years, bone_age_years=bone_age_years, gender=gender,
        weight_kg=weight_kg, height_cm=height_cm, location=location,
        medical_history=[s.strip() for s in (medical_history or "").split(",") if s.strip()],
    )
    image_bytes = await image.read()
    if len(image_bytes) > 4 * 1024 * 1024:
        raise HTTPException(413, "Image must be 4 MB or smaller")
    try:
        with Image.open(io.BytesIO(image_bytes)) as uploaded:
            normalized = io.BytesIO()
            uploaded.convert("RGB").save(normalized, format="PNG")
            image_bytes = normalized.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(422, "Uploaded file is not a valid image") from exc

    try:
        output, overlay = await asyncio.to_thread(vision.run, image_bytes)
    except RuntimeError as exc:
        log.error("Vision model error (RuntimeError): %s", exc)
        raise HTTPException(503, f"Vision model error: {exc}") from exc
    except Exception as exc:
        log.exception("Unexpected error during vision inference")
        raise HTTPException(503, f"Vision inference failed: {type(exc).__name__}: {exc}") from exc

    detections = output.get("detections", [])
    fracture_conf = max((float(d.get("fracture_conf", 0)) for d in detections), default=0)
    confidence_percent = round(fracture_conf * 100, 1)
    factors = scoring.build_factors(
        confidence_percent, clinical.age_years, clinical.location, clinical.medical_history
    )
    factors[0] = Factor(
        label=f"C2 Fracture Confidence {confidence_percent:.0f}%",
        impact="high" if confidence_percent >= 70 else "medium" if confidence_percent >= 40 else "low",
    )
    factors.insert(1, Factor(
        label=f"C1 Physis Detections: {len(detections)}",
        impact="low" if detections else "high",
    ))
    return _result(clinical, confidence_percent, overlay, "N/A", factors,
                   analysis_mode="real", metric_label="C2 Fracture Confidence",
                   model_note=_REAL_MODEL_NOTE)


def _result(
    clinical: ClinicalInput,
    percent: float,
    overlay: str,
    salter_harris: str | None,
    factors: list[Factor] | None = None,
    analysis_mode: str = "sample",
    metric_label: str = "Physeal Plate Damage",
    model_note: str | None = None,
) -> AnalysisResult:
    score = scoring.risk_score(percent, clinical.age_years,
                               clinical.location, clinical.medical_history)
    growth: GrowthPrediction = predict(percent, clinical.age_years,
                                       clinical.gender, clinical.location)
    return AnalysisResult(
        overlay_image=overlay,
        damage_percent=round(percent, 1),
        risk_level=scoring.risk_level(score),
        salter_harris=scoring.salter_harris(salter_harris, percent),
        bend_direction=scoring.bend_direction(clinical.location),
        growth_prediction=growth,
        factors=factors or scoring.build_factors(
            percent, clinical.age_years, clinical.location, clinical.medical_history
        ),
        clinical_used=clinical,
        analysis_mode=analysis_mode,
        metric_label=metric_label,
        model_note=model_note,
    )
