"""
main.py
--------
FastAPI backend for VaaniShield.

Run with:
    uvicorn app.main:app --reload --port 8000

Endpoint:
    POST /analyze
        form-data: file=<audio file>, language=en|hi|mr
        returns: JSON matching the frontend's AnalysisResult shape
"""

import shutil
import tempfile
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.detection import analyze_audio
from app.transcript import transcribe, score_context, build_flagged_transcript

app = FastAPI(title="VaaniShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon demo simplicity; restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "VaaniShield backend"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), language: str = Form("en")):
    # Save uploaded audio to a temp file so librosa/whisper can read it
    suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 1. Voice authenticity (DSP-based) analysis
        voice_result = analyze_audio(tmp_path)

        # 2. Multilingual transcription
        stt_result = transcribe(tmp_path, language_hint=language)
        text = stt_result.get("text", "")

        # 3. Context/keyword risk scoring
        context_score, matched_keywords = score_context(text, language)
        flagged_transcript = build_flagged_transcript(text, language)

        if matched_keywords:
            voice_result["reasons"].append(
                {
                    "label": "High-risk phrases detected in call",
                    "detail": f"Transcript contains scam-associated phrases: {', '.join(matched_keywords[:4])}.",
                    "weight": 25,
                }
            )

        # 4. Composite score: 70% voice signal + 30% context signal
        composite = round(0.7 * voice_result["riskScore"] + 0.3 * context_score, 1)
        band = "risk" if composite >= 70 else ("warning" if composite >= 40 else "safe")

        return {
            "riskScore": composite,
            "band": band,
            "chunks": voice_result["chunks"],
            "reasons": voice_result["reasons"],
            "transcript": flagged_transcript if flagged_transcript else [
                {"text": "(No speech detected or transcription unavailable)", "flagged": False}
            ],
            "language": language,
            "durationSec": voice_result["durationSec"],
            "sttOk": stt_result.get("ok", False),
        }
    finally:
        os.remove(tmp_path)
