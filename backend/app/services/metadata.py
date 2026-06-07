"""โหลด metadata.json + lookup เคส (ตาม DATA_CONTRACT.md)"""
import json
from functools import lru_cache
from typing import Optional

from ..config import METADATA_PATH


@lru_cache(maxsize=1)
def _load() -> dict:
    if not METADATA_PATH.exists():
        return {"version": 1, "cases": []}
    with open(METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def reload_metadata() -> None:
    """เรียกหลังวางไฟล์ data ใหม่จาก Namthip"""
    _load.cache_clear()


def all_cases() -> list[dict]:
    return _load().get("cases", [])


def get_by_id(sample_id: str) -> Optional[dict]:
    return next((c for c in all_cases() if c.get("id") == sample_id), None)


def get_by_filename(filename: str) -> Optional[dict]:
    return next((c for c in all_cases() if c.get("filename") == filename), None)
