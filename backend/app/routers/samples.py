"""GET /api/samples — รายการเคสตัวอย่าง Low/Med/High สำหรับ sample picker"""
from fastapi import APIRouter

from ..schemas import SampleCase
from ..services.metadata import all_cases

router = APIRouter()


@router.get("/samples", response_model=list[SampleCase])
def list_samples():
    return [
        SampleCase(id=c["id"], filename=c["filename"],
                   display_name=c.get("display_name", c["id"]))
        for c in all_cases()
    ]
