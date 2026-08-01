"""
FinSight AI — History API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database import get_history, delete_history_item

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def list_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sentiment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """Get analysis history with optional filters."""
    return await get_history(
        limit=limit,
        offset=offset,
        sentiment_filter=sentiment,
        search=search,
    )


@router.delete("/history/{item_id}")
async def delete_history(item_id: int):
    """Delete a history item."""
    success = await delete_history_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}
