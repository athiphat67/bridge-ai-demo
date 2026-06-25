"""ค่าคงที่ของ demo — ปรับ tuning ได้ที่นี่ที่เดียว"""
import os
from pathlib import Path

# --- paths ---
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
METADATA_PATH = DATA_DIR / "metadata.json"
MODELS_DIR = APP_DIR / "models"
C1_MODEL = MODELS_DIR / "c1_physis_yolo.onnx"
C2_MODEL = MODELS_DIR / "c2_classifier.onnx"

# --- risk thresholds (Low < LOW_MAX <= Medium < MED_MAX <= High) ---
RISK_LOW_MAX = 40
RISK_MED_MAX = 70

# --- heatmap / box drawing ---
HEATMAP_COLOR = (255, 60, 40)      # แดง
HEATMAP_ALPHA = 0.55               # ความเข้มสูงสุดตรงกลาง blob
BOX_COLOR = (255, 215, 0)          # เหลืองทอง
BOX_WIDTH = 4
