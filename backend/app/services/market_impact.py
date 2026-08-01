"""
FinSight AI — Market Impact Service
Predicts market direction and impact from sentiment analysis.
"""


def predict_market_impact(prediction: dict, text: str = "") -> dict:
    """
    Predict market impact from sentiment prediction.

    Returns market impact class, score, horizon, and bull/bear evidence.
    """
    sentiment_score = prediction.get("sentiment_score", 0)
    confidence = prediction.get("confidence", 0.5)
    probabilities = prediction.get("probabilities", {})

    # ─── Impact Score (0-100) ─────────────────────────────
    # Weighted combination of sentiment score and confidence
    raw_impact = sentiment_score * 50 + 50  # Map -1..+1 to 0..100
    confidence_adjustment = (confidence - 0.5) * 20  # Higher confidence pushes further from center
    impact_score = int(max(0, min(100, raw_impact + confidence_adjustment)))

    # ─── Market Impact Class ──────────────────────────────
    if impact_score >= 80:
        market_impact = "Strong Bullish"
    elif impact_score >= 60:
        market_impact = "Bullish"
    elif impact_score >= 40:
        market_impact = "Neutral"
    elif impact_score >= 20:
        market_impact = "Bearish"
    else:
        market_impact = "Strong Bearish"

    # ─── Impact Horizon ───────────────────────────────────
    horizon = _predict_horizon(sentiment_score, confidence, text)

    # ─── Bull vs Bear Evidence ────────────────────────────
    bull_bear = _extract_bull_bear_evidence(text, prediction)

    return {
        "market_impact": market_impact,
        "impact_score": impact_score,
        "horizon": horizon,
        "bull_bear_evidence": bull_bear,
        "disclaimer": "Market impact prediction represents model-estimated textual sentiment and must not be considered financial advice.",
    }


def _predict_horizon(sentiment_score: float, confidence: float, text: str) -> dict:
    """Estimate market impact across time horizons."""
    text_lower = text.lower()

    # Immediate reaction based on headline sentiment
    immediate_score = sentiment_score
    if confidence > 0.8:
        immediate_impact = _score_to_horizon_label(immediate_score, strong=True)
    else:
        immediate_impact = _score_to_horizon_label(immediate_score, strong=False)

    # Short-term: moderate the signal
    short_term_score = sentiment_score * 0.7
    short_term_impact = _score_to_horizon_label(short_term_score, strong=False)

    # Long-term: depends on event type
    long_term_keywords = {
        "earnings", "acquisition", "merger", "restructuring",
        "strategy", "investment", "expansion", "regulation",
    }
    has_structural = any(kw in text_lower for kw in long_term_keywords)

    if has_structural:
        long_term_score = sentiment_score * 0.5
        long_term_impact = _score_to_horizon_label(long_term_score, strong=False)
    else:
        long_term_impact = "Uncertain"

    # Confidence values
    immediate_conf = round(confidence * 0.95, 2)
    short_conf = round(confidence * 0.70, 2)
    long_conf = round(confidence * 0.40, 2) if has_structural else round(0.25, 2)

    return {
        "immediate": {"impact": immediate_impact, "confidence": immediate_conf},
        "short_term": {"impact": short_term_impact, "confidence": short_conf},
        "long_term": {"impact": long_term_impact, "confidence": long_conf},
    }


def _score_to_horizon_label(score: float, strong: bool = False) -> str:
    """Convert a sentiment score to a horizon label."""
    if score >= 0.5:
        return "Bullish" if not strong else "Strong Bullish"
    elif score >= 0.15:
        return "Moderately Bullish"
    elif score > -0.15:
        return "Neutral"
    elif score > -0.5:
        return "Moderately Bearish"
    else:
        return "Bearish" if not strong else "Strong Bearish"


def _extract_bull_bear_evidence(text: str, prediction: dict) -> dict:
    """Extract bullish and bearish evidence from text."""
    text_lower = text.lower()

    bullish_patterns = [
        (r"revenue (?:increased|grew|rose|surged)[\w\s]*\d+", "Revenue growth"),
        (r"earnings (?:exceeded|beat|surpassed)", "Earnings beat expectations"),
        (r"(?:raised|increased|upgraded)\s+guidance", "Guidance raised"),
        (r"strong demand", "Strong demand"),
        (r"record (?:revenue|profit|earnings|results)", "Record results"),
        (r"(?:profit|earnings|revenue)\s+(?:increased|grew|rose)", "Improved financials"),
        (r"margin\s+(?:improved|expanded|increased)", "Margin expansion"),
        (r"dividend\s+(?:increased|raised|declared)", "Dividend increase"),
        (r"(?:stock|share)\s+buyback", "Share buyback"),
        (r"market share\s+(?:gained|grew|increased)", "Market share gains"),
    ]

    bearish_patterns = [
        (r"revenue (?:declined|fell|dropped|decreased)[\w\s]*\d*", "Revenue decline"),
        (r"(?:missed|below)\s+(?:expectations|estimates|forecast)", "Missed expectations"),
        (r"(?:reduced|lowered|cut)\s+guidance", "Guidance cut"),
        (r"(?:operating|total)\s+(?:expenses|costs)\s+(?:increased|rose)", "Rising expenses"),
        (r"(?:layoffs|job cuts|restructuring)", "Workforce reduction"),
        (r"(?:profit|earnings|revenue)\s+(?:declined|fell|dropped)", "Declining financials"),
        (r"margin\s+(?:compressed|declined|narrowed)", "Margin compression"),
        (r"(?:debt|leverage)\s+(?:increased|rose|grew)", "Rising debt"),
        (r"(?:demand|sales)\s+(?:weakened|declined|slowed)", "Weakening demand"),
        (r"(?:downgrade|investigation|lawsuit|regulatory)", "Regulatory/Legal risk"),
    ]

    bullish_evidence = []
    for pattern, label in bullish_patterns:
        import re
        if re.search(pattern, text_lower):
            bullish_evidence.append(label)

    bearish_evidence = []
    for pattern, label in bearish_patterns:
        import re
        if re.search(pattern, text_lower):
            bearish_evidence.append(label)

    # Add from prediction signals if available
    positive_signals = prediction.get("positive_signals", [])
    negative_signals = prediction.get("negative_signals", [])

    for sig in positive_signals[:3]:
        word = sig.get("word", "")
        if word and word not in [e.lower() for e in bullish_evidence]:
            bullish_evidence.append(word.title())

    for sig in negative_signals[:3]:
        word = sig.get("word", "")
        if word and word not in [e.lower() for e in bearish_evidence]:
            bearish_evidence.append(word.title())

    # Calculate balance
    total = len(bullish_evidence) + len(bearish_evidence)
    if total > 0:
        bullish_pct = round(len(bullish_evidence) / total * 100)
        bearish_pct = 100 - bullish_pct
    else:
        bullish_pct = 50
        bearish_pct = 50

    return {
        "bullish": bullish_evidence[:6],
        "bearish": bearish_evidence[:6],
        "bullish_percentage": bullish_pct,
        "bearish_percentage": bearish_pct,
    }
