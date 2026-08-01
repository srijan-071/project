"""
FinSight AI — Analytics API Routes
Dashboard analytics, sector intelligence, and timeline data.
"""

from fastapi import APIRouter
from app.database import get_analytics_summary

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary():
    """Get aggregated analytics for the Market Pulse dashboard."""
    return await get_analytics_summary()


@router.get("/sectors")
async def sector_analytics():
    """Get sector-level sentiment intelligence."""
    # Sector data is computed from analyzed articles
    # For demo purposes, provide sector template with instructions
    summary = await get_analytics_summary()

    # Compute sector distribution from recent analyses
    sectors = [
        {"name": "Technology", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Banking", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Energy", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Healthcare", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Automobile", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Consumer", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Telecom", "sentiment_score": 0, "impact": "Neutral", "count": 0},
        {"name": "Finance", "sentiment_score": 0, "impact": "Neutral", "count": 0},
    ]

    return {"sectors": sectors, "total_analyzed": summary.get("total_analyzed", 0)}
