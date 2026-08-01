"""
FinSight AI — Comparison API
POST /api/compare — Compare two articles side by side.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ml.inference import engine
from app.services.sentiment_service import analyze_full
from app.services.market_impact import predict_market_impact
from app.services.entity_service import extract_entities, detect_events
from app.services.keyword_service import extract_keywords
from app.services.risk_service import detect_risks
from app.utils.config import MAX_INPUT_LENGTH

router = APIRouter(prefix="/api", tags=["compare"])


class CompareRequest(BaseModel):
    text_a: str = Field(..., min_length=5, max_length=MAX_INPUT_LENGTH)
    text_b: str = Field(..., min_length=5, max_length=MAX_INPUT_LENGTH)


def _build_article_result(text: str, analysis: dict) -> dict:
    """Build a compact result for one article."""
    market = predict_market_impact(analysis, text)
    entities = extract_entities(text, analysis)
    events = detect_events(text, analysis)
    keywords = extract_keywords(text, analysis)
    risk = detect_risks(text, analysis)

    return {
        "text": text[:500],
        "sentiment": analysis["sentiment"],
        "confidence": analysis["confidence"],
        "sentiment_score": analysis["sentiment_score"],
        "probabilities": analysis["probabilities"],
        "interpretation": analysis["interpretation"],
        "market_impact": market,
        "entities": entities,
        "events": events,
        "keywords": keywords[:8],
        "risk": risk,
        "sentiment_dna": analysis["sentiment_dna"],
        "uncertainty": analysis["uncertainty"],
        "num_tokens": analysis["num_tokens"],
    }


@router.post("/compare")
async def compare_articles(request: CompareRequest):
    """Compare two financial articles."""
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        analysis_a = analyze_full(request.text_a.strip())
        analysis_b = analyze_full(request.text_b.strip())

        result_a = _build_article_result(request.text_a.strip(), analysis_a)
        result_b = _build_article_result(request.text_b.strip(), analysis_b)

        # Compute deltas
        deltas = {
            "sentiment_score": round(
                result_b["sentiment_score"] - result_a["sentiment_score"], 4
            ),
            "confidence": round(
                result_b["confidence"] - result_a["confidence"], 4
            ),
            "impact_score": (
                result_b["market_impact"]["impact_score"]
                - result_a["market_impact"]["impact_score"]
            ),
            "risk_score": (
                result_b["risk"]["overall_risk_score"]
                - result_a["risk"]["overall_risk_score"]
            ),
            "sentiment_match": result_a["sentiment"] == result_b["sentiment"],
            "market_impact_match": (
                result_a["market_impact"]["market_impact"]
                == result_b["market_impact"]["market_impact"]
            ),
        }

        return {
            "article_a": result_a,
            "article_b": result_b,
            "deltas": deltas,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
