"""Pydantic models — สัญญา request/response ของ API"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ClinicalInput(BaseModel):
    age_years: float = Field(..., ge=0, le=18)
    bone_age_years: Optional[float] = Field(None, ge=0, le=18)
    gender: Literal["male", "female"]
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    location: Literal["medial", "lateral"]
    medical_history: list[str] = Field(default_factory=list)


class BarBox(BaseModel):
    """พิกัดเป็นสัดส่วน 0–1 (ดู DATA_CONTRACT.md)"""
    x: float
    y: float
    w: float
    h: float


class Factor(BaseModel):
    label: str
    impact: Literal["low", "medium", "high"]


class GrowthProbabilities(BaseModel):
    """โอกาสเกิดผลลัพธ์ 3 รูปแบบ (รวมกัน = 100%)"""
    varus_percent: float      # ขาโก่งออก (genu varum)
    valgus_percent: float     # ขาฉิ่งเข้า (genu valgum)
    arrest_percent: float     # หยุดโต (growth arrest)


class GrowthPrediction(BaseModel):
    years: list[float]
    leg_length_diff_mm: list[float]
    angular_deg: list[float]
    # ศักยภาพการเติบโตที่เหลือ (เทียบเด็กปกติวัยเดียวกัน)
    remaining_growth_percent: float    # ฝั่งที่บาดเจ็บยังโตได้อีกกี่ % เทียบเด็กปกติ
    normal_remaining_percent: float    # เด็กปกติวัยเดียวกันยังโตได้อีกกี่ %
    probabilities: GrowthProbabilities


class AnalysisResult(BaseModel):
    overlay_image: str                 # data:image/png;base64,...
    damage_percent: float              # ตัวเลข hero
    risk_level: Literal["Low", "Medium", "High"]
    salter_harris: str
    bend_direction: Literal["Varus", "Valgus"]
    growth_prediction: GrowthPrediction
    factors: list[Factor]
    clinical_used: ClinicalInput       # actual clinical data used (for BMI display)


class SampleCase(BaseModel):
    id: str
    filename: str
    display_name: str
