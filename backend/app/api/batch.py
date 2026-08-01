"""
FinSight AI — Batch Analysis API
POST /api/batch-analyze — Analyze multiple headlines at once.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List

from app.ml.inference import engine
from app.services.market_impact import predict_market_impact
from app.services.risk_service import detect_risks
from app.utils.config import MAX_INPUT_LENGTH, MAX_FILE_SIZE_MB

router = APIRouter(prefix="/api", tags=["batch"])


class BatchRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=50)


@router.post("/batch-analyze")
async def batch_analyze(request: BatchRequest):
    """Analyze multiple headlines simultaneously."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    results = []
    for i, text in enumerate(request.texts):
        text = text.strip()
        if len(text) < 3:
            results.append({
                "index": i,
                "text": text,
                "error": "Text too short",
            })
            continue

        try:
            prediction = engine.predict(text)
            market = predict_market_impact(prediction, text)

            results.append({
                "index": i,
                "text": text[:200],
                "sentiment": prediction["sentiment"],
                "confidence": prediction["confidence"],
                "sentiment_score": prediction["sentiment_score"],
                "probabilities": prediction["probabilities"],
                "market_impact": market["market_impact"],
                "impact_score": market["impact_score"],
                "latency_ms": prediction["latency_ms"],
            })
        except Exception as e:
            results.append({
                "index": i,
                "text": text[:200],
                "error": str(e),
            })

    # Summary stats
    valid = [r for r in results if "error" not in r]
    summary = {}
    if valid:
        sentiments = [r["sentiment"] for r in valid]
        summary = {
            "total": len(results),
            "successful": len(valid),
            "failed": len(results) - len(valid),
            "positive_count": sentiments.count("positive"),
            "neutral_count": sentiments.count("neutral"),
            "negative_count": sentiments.count("negative"),
            "avg_confidence": round(
                sum(r["confidence"] for r in valid) / len(valid), 4
            ),
            "avg_sentiment_score": round(
                sum(r["sentiment_score"] for r in valid) / len(valid), 4
            ),
        }

    return {"results": results, "summary": summary}


@router.post("/batch-analyze/upload")
async def batch_upload(file: UploadFile = File(...)):
    """Upload a text or CSV file for batch analysis."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    # Validate file type
    filename = file.filename or ""
    if not filename.endswith((".txt", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload .txt or .csv files.",
        )

    # Read file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.",
        )

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file. Please use UTF-8 encoding.")

    # Split into lines
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]

    if len(lines) > 50:
        lines = lines[:50]  # Limit to 50

    # Analyze batch
    request = BatchRequest(texts=lines)
    return await batch_analyze(request)
