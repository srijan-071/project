"""
FinSight AI — Database Module
SQLite database for analysis history, entities, and model runs.
"""

import aiosqlite
import json
from datetime import datetime
from typing import Optional, List

from app.utils.config import DB_PATH


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                confidence REAL NOT NULL,
                sentiment_score REAL NOT NULL,
                market_impact TEXT,
                impact_score INTEGER,
                risk_score INTEGER,
                probabilities TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                entity TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                sentiment TEXT,
                confidence REAL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT NOT NULL,
                latency REAL NOT NULL,
                tokens INTEGER NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print("[+] Database initialized")


async def save_analysis(result: dict) -> int:
    """Save an analysis result to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO analyses (text, sentiment, confidence, sentiment_score,
                                  market_impact, impact_score, risk_score,
                                  probabilities, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.get("cleaned_text", result.get("text", ""))[:2000],
                result.get("sentiment", "neutral"),
                result.get("confidence", 0.0),
                result.get("sentiment_score", 0.0),
                result.get("market_impact", {}).get("market_impact", "Neutral") if isinstance(result.get("market_impact"), dict) else result.get("market_impact", "Neutral"),
                result.get("market_impact", {}).get("impact_score", 50) if isinstance(result.get("market_impact"), dict) else 50,
                result.get("risk", {}).get("overall_risk_score", 0) if isinstance(result.get("risk"), dict) else 0,
                json.dumps(result.get("probabilities", {})),
                json.dumps([k.get("keyword", "") for k in result.get("keywords", [])[:10]]),
            ),
        )
        analysis_id = cursor.lastrowid

        # Save entities
        entities = result.get("entities", {}).get("entities", [])
        for entity in entities:
            await db.execute(
                """
                INSERT INTO entities (analysis_id, entity, entity_type, sentiment, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    entity.get("entity", ""),
                    entity.get("type", "Unknown"),
                    entity.get("sentiment"),
                    entity.get("confidence"),
                ),
            )

        # Save model run
        await db.execute(
            """
            INSERT INTO model_runs (model_version, latency, tokens, prediction, confidence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "FinSight-TX v1.0",
                result.get("latency_ms", 0),
                result.get("num_tokens", 0),
                result.get("sentiment", "neutral"),
                result.get("confidence", 0),
            ),
        )

        await db.commit()
        return analysis_id


async def get_history(
    limit: int = 50,
    offset: int = 0,
    sentiment_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    """Get analysis history with optional filters."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query = "SELECT * FROM analyses WHERE 1=1"
        params = []

        if sentiment_filter:
            query += " AND sentiment = ?"
            params.append(sentiment_filter)

        if search:
            query += " AND text LIKE ?"
            params.append(f"%{search}%")

        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        async with db.execute(count_query, params) as cursor:
            row = await cursor.fetchone()
            total = row[0]

        # Fetch page
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "text": row["text"][:200],
                "sentiment": row["sentiment"],
                "confidence": row["confidence"],
                "sentiment_score": row["sentiment_score"],
                "market_impact": row["market_impact"],
                "impact_score": row["impact_score"],
                "risk_score": row["risk_score"],
                "created_at": row["created_at"],
            })

        return {"items": results, "total": total, "limit": limit, "offset": offset}


async def delete_history_item(item_id: int) -> bool:
    """Delete a history item."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM entities WHERE analysis_id = ?", (item_id,))
        cursor = await db.execute("DELETE FROM analyses WHERE id = ?", (item_id,))
        await db.commit()
        return cursor.rowcount > 0


async def get_analytics_summary() -> dict:
    """Get aggregated analytics for dashboard."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Total count
        async with db.execute("SELECT COUNT(*) as count FROM analyses") as cursor:
            row = await cursor.fetchone()
            total = row["count"]

        if total == 0:
            return {
                "total_analyzed": 0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "avg_confidence": 0,
                "market_mood": 50,
                "high_risk_count": 0,
                "timeline": [],
                "recent": [],
            }

        # Sentiment distribution
        distribution = {}
        for sentiment in ["positive", "neutral", "negative"]:
            async with db.execute(
                "SELECT COUNT(*) as count FROM analyses WHERE sentiment = ?",
                (sentiment,),
            ) as cursor:
                row = await cursor.fetchone()
                distribution[sentiment] = row["count"]

        # Average confidence
        async with db.execute("SELECT AVG(confidence) as avg_conf FROM analyses") as cursor:
            row = await cursor.fetchone()
            avg_conf = round(row["avg_conf"] or 0, 3)

        # Market mood (average sentiment score mapped to 0-100)
        async with db.execute("SELECT AVG(sentiment_score) as avg_score FROM analyses") as cursor:
            row = await cursor.fetchone()
            avg_score = row["avg_score"] or 0
            market_mood = int(avg_score * 50 + 50)

        # High risk count
        async with db.execute(
            "SELECT COUNT(*) as count FROM analyses WHERE risk_score >= 60"
        ) as cursor:
            row = await cursor.fetchone()
            high_risk = row["count"]

        # Timeline (last 30 analyses)
        async with db.execute(
            "SELECT sentiment_score, created_at FROM analyses ORDER BY created_at DESC LIMIT 30"
        ) as cursor:
            timeline_rows = await cursor.fetchall()
            timeline = [
                {"score": row["sentiment_score"], "date": row["created_at"]}
                for row in timeline_rows
            ]

        # Recent analyses
        async with db.execute(
            "SELECT id, text, sentiment, confidence, market_impact, created_at FROM analyses ORDER BY created_at DESC LIMIT 5"
        ) as cursor:
            recent_rows = await cursor.fetchall()
            recent = [
                {
                    "id": row["id"],
                    "text": row["text"][:100],
                    "sentiment": row["sentiment"],
                    "confidence": row["confidence"],
                    "market_impact": row["market_impact"],
                    "created_at": row["created_at"],
                }
                for row in recent_rows
            ]

        return {
            "total_analyzed": total,
            "sentiment_distribution": distribution,
            "avg_confidence": avg_conf,
            "market_mood": market_mood,
            "high_risk_count": high_risk,
            "timeline": timeline,
            "recent": recent,
        }
