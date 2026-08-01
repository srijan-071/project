"""
FinSight AI — Analyze API Routes
POST /api/analyze — Full single-article analysis
POST /api/analyze/what-if — Scenario mutation comparison
POST /api/analyze/playground — Quick token-level analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.inference import engine
from app.services.sentiment_service import analyze_full
from app.services.market_impact import predict_market_impact
from app.services.entity_service import extract_entities, detect_events
from app.services.keyword_service import extract_keywords
from app.services.risk_service import detect_risks, compute_news_impact
from app.database import save_analysis
from app.utils.config import MAX_INPUT_LENGTH

router = APIRouter(prefix="/api", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=MAX_INPUT_LENGTH)


class WhatIfRequest(BaseModel):
    original_text: str = Field(..., min_length=5, max_length=MAX_INPUT_LENGTH)
    modified_text: str = Field(..., min_length=5, max_length=MAX_INPUT_LENGTH)


class PlaygroundRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)


@router.post("/analyze")
async def analyze_text(request: AnalyzeRequest):
    """Full financial text analysis pipeline."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Please wait or train the model first.")

    text = request.text.strip()

    if len(text) < 5:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "ERR_TEXT_001",
                "message": "Insufficient textual context detected. Please provide a financial headline or article containing meaningful context.",
            },
        )

    try:
        # Core sentiment analysis
        analysis = analyze_full(text)

        # Market impact
        market_impact = predict_market_impact(analysis, text)

        # Entities
        entities = extract_entities(text, analysis)

        # Events
        events = detect_events(text, analysis)

        # Keywords
        keywords = extract_keywords(text, analysis)

        # Risk signals
        risk = detect_risks(text, analysis)

        # News impact
        news_impact = compute_news_impact(text, analysis, risk)

        # Build response
        result = {
            "text": text,
            "sentiment": analysis["sentiment"],
            "confidence": analysis["confidence"],
            "sentiment_score": analysis["sentiment_score"],
            "interpretation": analysis["interpretation"],
            "probabilities": analysis["probabilities"],
            "market_impact": market_impact,
            "entities": entities,
            "events": events,
            "keywords": keywords,
            "risk": risk,
            "news_impact": news_impact,
            "uncertainty": analysis["uncertainty"],
            "contradictions": analysis["contradictions"],
            "sentiment_dna": analysis["sentiment_dna"],
            "positive_signals": analysis["positive_signals"],
            "negative_signals": analysis["negative_signals"],
            "reasoning": analysis["reasoning"],
            "highlights": analysis["highlights"],
            "sentence_analysis": analysis["sentence_analysis"],
            "attention_weights": analysis["attention_weights"],
            "tokens": analysis["tokens"],
            "num_tokens": analysis["num_tokens"],
            "token_importance": analysis["token_importance"],
            "latency_ms": analysis["latency_ms"],
        }

        # Save to history
        try:
            result["analysis_id"] = await save_analysis(result)
        except Exception:
            pass  # Don't fail if DB save fails

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ERR_ANALYSIS_500",
                "message": f"Analysis failed: {str(e)}",
            },
        )


@router.post("/analyze/what-if")
async def what_if_analysis(request: WhatIfRequest):
    """Compare original vs modified text predictions."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        original = engine.predict(request.original_text.strip())
        modified = engine.predict(request.modified_text.strip())

        delta_score = round(modified["sentiment_score"] - original["sentiment_score"], 4)
        delta_confidence = round(modified["confidence"] - original["confidence"], 4)

        return {
            "original": {
                "text": request.original_text.strip(),
                "sentiment": original["sentiment"],
                "confidence": original["confidence"],
                "sentiment_score": original["sentiment_score"],
                "probabilities": original["probabilities"],
            },
            "modified": {
                "text": request.modified_text.strip(),
                "sentiment": modified["sentiment"],
                "confidence": modified["confidence"],
                "sentiment_score": modified["sentiment_score"],
                "probabilities": modified["probabilities"],
            },
            "delta": {
                "sentiment_score": delta_score,
                "confidence": delta_confidence,
                "sentiment_changed": original["sentiment"] != modified["sentiment"],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/playground")
async def playground_analysis(request: PlaygroundRequest):
    """Quick token-level analysis for Transformer Playground."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        result = engine.predict(request.text.strip())
        market = predict_market_impact(result, request.text)

        return {
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "sentiment_score": result["sentiment_score"],
            "probabilities": result["probabilities"],
            "tokens": result["tokens"],
            "token_importance": result["token_importance"],
            "attention_weights": result["attention_weights"],
            "market_impact": market["market_impact"],
            "impact_score": market["impact_score"],
            "latency_ms": result["latency_ms"],
            "num_tokens": result["num_tokens"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
