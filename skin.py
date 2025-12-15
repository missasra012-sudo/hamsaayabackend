from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import os
import uuid
from datetime import datetime
import json

router = APIRouter(prefix="/skin", tags=["Skin Analyzer"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalyzeResult(BaseModel):
    skin_type: str
    acne_level: str
    redness: str
    hydration_hint: str
    sun_exposure_hint: str
    advice: str

def simple_skin_analysis(img: np.ndarray) -> dict:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v_mean = float(np.mean(hsv[:, :, 2]))
    s_mean = float(np.mean(hsv[:, :, 1]))

    if v_mean < 80:
        skin_type = "dry"
    elif v_mean > 150 and s_mean > 60:
        skin_type = "oily"
    else:
        skin_type = "normal"

    b, g, r = cv2.split(img.astype(float))
    red_ratio = np.mean(r / (b + g + 1e-6))

    if red_ratio > 1.05:
        redness = "noticeable"
    elif red_ratio > 1.01:
        redness = "mild"
    else:
        redness = "low"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 140, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    small_count = sum(1 for c in contours if 10 < cv2.contourArea(c) < 2000)

    if small_count > 10:
        acne_level = "moderate"
    elif small_count > 3:
        acne_level = "mild"
    else:
        acne_level = "low"

    hydration_hint = "low" if v_mean < 90 else "high" if v_mean > 160 else "moderate"
    sun_hint = "recent sun exposure likely" if s_mean > 90 and redness != "low" else "no strong signs"

    advice = []
    if skin_type == "dry":
        advice.append("Use a gentle hydrating moisturizer daily.")
    elif skin_type == "oily":
        advice.append("Use a light gel-based moisturizer.")
    else:
        advice.append("Maintain cleanser, moisturizer, and sunscreen routine.")

    if acne_level != "low":
        advice.append("Use a mild salicylic-acid face wash.")
    if redness != "low":
        advice.append("Use soothing products like aloe vera.")
    if sun_hint.startswith("recent"):
        advice.append("Apply SPF 30+ sunscreen daily.")

    return {
        "skin_type": skin_type,
        "acne_level": acne_level,
        "redness": redness,
        "hydration_hint": hydration_hint,
        "sun_exposure_hint": sun_hint,
        "advice": " ".join(advice)
    }

@router.post("/analyze", response_model=AnalyzeResult)
async def analyze_skin(file: UploadFile = File(...)):
    if not file.content_type.startswith("image"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    contents = await file.read()
    img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    result = simple_skin_analysis(img)

    scan = {
        "id": uuid.uuid4().hex,
        "time": datetime.utcnow().isoformat(),
        "result": result
    }

    with open(f"{UPLOAD_DIR}/{scan['id']}.json", "w") as f:
        json.dump(scan, f)

    return result
