"""Self-contained C1 YOLO -> C2 ResNet inference using deploy-friendly ONNX."""
import base64
import io
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw

from ..config import C1_MODEL, C2_MODEL

PAD = 6
INPUT_SIZE = 256  # training/export size stored in the C1 checkpoint
CLASS_NAMES = ("Femur", "Tibia")


@lru_cache(maxsize=1)
def _models():
    missing = [str(path) for path in (C1_MODEL, C2_MODEL) if not path.exists()]
    if missing:
        raise RuntimeError(f"Model files not found: {', '.join(missing)}")
    return cv2.dnn.readNetFromONNX(str(C1_MODEL)), cv2.dnn.readNetFromONNX(str(C2_MODEL))


def _letterbox(image: np.ndarray) -> tuple[np.ndarray, float, int, int]:
    height, width = image.shape[:2]
    scale = min(INPUT_SIZE / width, INPUT_SIZE / height)
    resized = cv2.resize(image, (round(width * scale), round(height * scale)))
    pad_x = (INPUT_SIZE - resized.shape[1]) // 2
    pad_y = (INPUT_SIZE - resized.shape[0]) // 2
    canvas = np.full((INPUT_SIZE, INPUT_SIZE, 3), 114, dtype=np.uint8)
    canvas[pad_y:pad_y + resized.shape[0], pad_x:pad_x + resized.shape[1]] = resized
    return canvas, scale, pad_x, pad_y


def _detect(net, image: np.ndarray) -> list[dict]:
    letterboxed, scale, pad_x, pad_y = _letterbox(image)
    net.setInput(cv2.dnn.blobFromImage(letterboxed, 1 / 255, swapRB=False))
    output = net.forward()[0].T

    boxes, scores, class_ids = [], [], []
    for row in output:
        class_id = int(np.argmax(row[4:]))
        score = float(row[4 + class_id])
        if score < 0.25:
            continue
        cx, cy, width, height = row[:4]
        boxes.append([float(cx - width / 2), float(cy - height / 2),
                      float(width), float(height)])
        scores.append(score)
        class_ids.append(class_id)

    keep = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.7)
    detections = []
    for index in np.array(keep).reshape(-1):
        x, y, width, height = boxes[index]
        x0 = max(0, round((x - pad_x) / scale))
        y0 = max(0, round((y - pad_y) / scale))
        x1 = min(image.shape[1], round((x + width - pad_x) / scale))
        y1 = min(image.shape[0], round((y + height - pad_y) / scale))
        detections.append({
            "bone_type": CLASS_NAMES[class_ids[index]],
            "detection_conf": round(scores[index], 4),
            "box": [x0, y0, x1, y1],
        })
    return detections


def _classify(net, crop: np.ndarray) -> tuple[str, float]:
    net.setInput(cv2.dnn.blobFromImage(
        crop, 1 / 255, (224, 224), swapRB=False, crop=False
    ))
    logits = net.forward()[0]
    probabilities = np.exp(logits - logits.max())
    probabilities /= probabilities.sum()
    fracture = float(probabilities[0])  # exported class order: fracture, normal
    return ("Fracture" if fracture >= 0.4 else "Normal"), fracture


def run(image_bytes: bytes) -> tuple[dict, str]:
    c1, c2 = _models()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image.thumbnail((1200, 1200))
    pixels = np.asarray(image)
    detections = _detect(c1, pixels)
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)

    for detection in detections:
        x0, y0, x1, y1 = detection["box"]
        crop = pixels[
            max(0, y0 - PAD):min(image.height, y1 + PAD),
            max(0, x0 - PAD):min(image.width, x1 + PAD),
        ]
        classification, fracture_conf = _classify(c2, crop)
        detection.update({
            "classification": classification,
            "fracture_conf": round(fracture_conf, 4),
        })
        color = "red" if classification == "Fracture" else "lime"
        draw.rectangle((x0, y0, x1, y1), outline=color, width=3)
        draw.text((x0, max(0, y0 - 14)),
                  f"{detection['bone_type']}: {classification}", fill=color)

    buffer = io.BytesIO()
    # ponytail: JPEG keeps the serverless response safely below Vercel's 4.5 MB limit.
    overlay.save(buffer, "JPEG", quality=88, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return {"n_detections": len(detections), "detections": detections}, (
        f"data:image/jpeg;base64,{encoded}"
    )
