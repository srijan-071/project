"""
FinSight AI — Risk Signal Detection Service
Detects financial, regulatory, operational, and market risks from text.
"""

import re


# ─── Risk Signal Lexicons ─────────────────────────────────

FINANCIAL_RISK_SIGNALS = [
    "bankruptcy", "default", "debt", "leverage", "insolvency",
    "credit downgrade", "downgrade", "liquidity crisis", "cash burn",
    "debt restructuring", "writedown", "impairment", "provision",
    "capital raise", "dilution", "negative cash flow",
]

REGULATORY_RISK_SIGNALS = [
    "investigation", "probe", "regulatory action", "fine", "penalty",
    "compliance", "antitrust", "lawsuit", "litigation", "sec",
    "subpoena", "indictment", "fraud", "violation", "sanction",
    "ban", "recall", "data breach", "privacy",
]

OPERATIONAL_RISK_SIGNALS = [
    "layoffs", "job cuts", "restructuring", "downsizing", "supply disruption",
    "supply chain", "production halt", "outage", "cybersecurity",
    "data breach", "leadership change", "ceo departure", "resignation",
    "strike", "labor dispute", "quality issues", "product recall",
]

MARKET_RISK_SIGNALS = [
    "volatile", "volatility", "market crash", "correction", "bear market",
    "sell-off", "selloff", "panic", "uncertainty", "recession",
    "geopolitical", "trade war", "tariff", "sanctions", "inflation",
    "stagflation", "contagion", "bubble", "overvalued",
]


def detect_risks(text: str, prediction: dict = None) -> dict:
    """Detect all risk categories from text."""
    text_lower = text.lower()

    financial_risk = _score_risk(text_lower, FINANCIAL_RISK_SIGNALS)
    regulatory_risk = _score_risk(text_lower, REGULATORY_RISK_SIGNALS)
    operational_risk = _score_risk(text_lower, OPERATIONAL_RISK_SIGNALS)
    market_risk = _score_risk(text_lower, MARKET_RISK_SIGNALS)

    # Boost risk scores if sentiment is negative
    if prediction and prediction.get("sentiment") == "negative":
        multiplier = 1.3
        financial_risk["score"] = min(100, int(financial_risk["score"] * multiplier))
        regulatory_risk["score"] = min(100, int(regulatory_risk["score"] * multiplier))
        operational_risk["score"] = min(100, int(operational_risk["score"] * multiplier))
        market_risk["score"] = min(100, int(market_risk["score"] * multiplier))
        # Recalculate levels
        financial_risk["level"] = _score_to_level(financial_risk["score"])
        regulatory_risk["level"] = _score_to_level(regulatory_risk["score"])
        operational_risk["level"] = _score_to_level(operational_risk["score"])
        market_risk["level"] = _score_to_level(market_risk["score"])

    # Overall risk score
    overall_score = int(
        (financial_risk["score"] + regulatory_risk["score"]
         + operational_risk["score"] + market_risk["score"]) / 4
    )

    return {
        "overall_risk_score": overall_score,
        "overall_risk_level": _score_to_level(overall_score),
        "financial_risk": financial_risk,
        "regulatory_risk": regulatory_risk,
        "operational_risk": operational_risk,
        "market_risk": market_risk,
    }


def compute_news_impact(text: str, prediction: dict, risk_data: dict) -> dict:
    """Compute overall news impact score combining multiple signals."""
    # Base from sentiment confidence
    confidence = prediction.get("confidence", 0.5)
    sentiment_intensity = abs(prediction.get("sentiment_score", 0))

    # Component scores (0-100)
    sentiment_component = int(sentiment_intensity * 40)
    confidence_component = int(confidence * 20)
    risk_component = int(risk_data.get("overall_risk_score", 0) * 0.2)

    # Count financial keywords
    text_lower = text.lower()
    keyword_count = sum(
        1 for word in FINANCIAL_RISK_SIGNALS + REGULATORY_RISK_SIGNALS
        if word in text_lower
    )
    keyword_component = min(20, keyword_count * 5)

    impact_score = min(100, sentiment_component + confidence_component + risk_component + keyword_component)

    if impact_score >= 80:
        level = "CRITICAL"
    elif impact_score >= 60:
        level = "HIGH"
    elif impact_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "impact_score": impact_score,
        "impact_level": level,
        "components": {
            "sentiment_intensity": sentiment_component,
            "model_confidence": confidence_component,
            "risk_signals": risk_component,
            "financial_keywords": keyword_component,
        },
    }


def _score_risk(text: str, signals: list) -> dict:
    """Score risk level based on signal matches."""
    matched = []
    for signal in signals:
        if signal in text:
            matched.append(signal)

    # Score: each match adds points (diminishing returns)
    if not matched:
        score = 5  # Base low risk
    elif len(matched) == 1:
        score = 35
    elif len(matched) == 2:
        score = 55
    elif len(matched) == 3:
        score = 72
    else:
        score = min(95, 72 + len(matched) * 5)

    return {
        "score": score,
        "level": _score_to_level(score),
        "signals": matched,
    }


def _score_to_level(score: int) -> str:
    """Convert numeric score to risk level."""
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"
