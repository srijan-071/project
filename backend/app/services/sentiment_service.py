"""
FinSight AI — Sentiment Analysis Service
Orchestrates the full analysis pipeline: sentiment, confidence, uncertainty,
contradiction detection, sentiment DNA, and model reasoning.
"""

import math
import re
from typing import Optional

from app.ml.inference import engine
from app.ml.preprocessing import split_sentences


# ─── Financial Keyword Lexicons ───────────────────────────

POSITIVE_KEYWORDS = {
    "revenue growth", "profit", "earnings", "beat", "exceeded", "surpassed",
    "record", "strong demand", "increased", "gained", "upgraded", "bullish",
    "outperformed", "growth", "improved", "expansion", "raised guidance",
    "dividend", "buyback", "recovery", "breakthrough", "innovation",
    "higher", "surge", "accelerated", "robust", "solid", "upbeat",
    "optimistic", "positive", "momentum", "profitable", "benefit",
}

NEGATIVE_KEYWORDS = {
    "loss", "declined", "missed", "fell", "decreased", "downgraded",
    "bearish", "underperformed", "contraction", "reduced guidance",
    "layoffs", "restructuring", "bankruptcy", "default", "weakness",
    "lower", "plunged", "slumped", "disappointing", "negative",
    "struggling", "cut", "deficit", "impairment", "writedown",
    "risk", "warning", "concern", "volatile", "uncertain",
    "expenses", "costs", "debt", "investigation", "lawsuit",
}

GROWTH_KEYWORDS = {"growth", "expansion", "increased", "accelerated", "gained", "grew", "higher", "surge", "breakthrough"}
RISK_KEYWORDS = {"risk", "volatile", "uncertain", "warning", "concern", "exposure", "threat", "vulnerability"}
PROFITABILITY_KEYWORDS = {"profit", "margin", "earnings", "revenue", "income", "profitable", "yield", "return"}
UNCERTAINTY_KEYWORDS = {"uncertain", "unclear", "depends", "may", "might", "could", "possibly", "expected", "forecast"}


def analyze_full(text: str) -> dict:
    """Run the complete sentiment analysis pipeline."""
    if not engine.is_loaded:
        raise RuntimeError("Model not loaded")

    # ─── Core Prediction ─────────────────────────────────
    prediction = engine.predict(text)

    # ─── Sentence-level Analysis ─────────────────────────
    sentence_analysis = engine.predict_sentences(text)

    # ─── Sentiment Score Interpretation ──────────────────
    score = prediction["sentiment_score"]
    interpretation = _interpret_sentiment_score(score)

    # ─── Uncertainty / Confidence ────────────────────────
    uncertainty = _compute_uncertainty(prediction["probabilities"])

    # ─── Contradiction Detection ─────────────────────────
    contradictions = _detect_contradictions(sentence_analysis)

    # ─── Sentiment DNA ───────────────────────────────────
    sentiment_dna = _compute_sentiment_dna(text, prediction, sentence_analysis)

    # ─── Positive / Negative Signal Words ────────────────
    positive_signals, negative_signals = _extract_signal_words(text, prediction["token_importance"], prediction["tokens"])

    # ─── Model Reasoning ─────────────────────────────────
    reasoning = _generate_reasoning(
        prediction, positive_signals, negative_signals, contradictions
    )

    # ─── Word Highlights ─────────────────────────────────
    highlights = _generate_highlights(text, prediction["tokens"], prediction["token_importance"])

    return {
        **prediction,
        "interpretation": interpretation,
        "uncertainty": uncertainty,
        "sentence_analysis": sentence_analysis,
        "contradictions": contradictions,
        "sentiment_dna": sentiment_dna,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
        "reasoning": reasoning,
        "highlights": highlights,
    }


def _interpret_sentiment_score(score: float) -> str:
    """Human-readable interpretation of sentiment score."""
    if score >= 0.6:
        return "Strong Positive Financial Sentiment"
    elif score >= 0.2:
        return "Moderately Positive Financial Sentiment"
    elif score > -0.2:
        return "Neutral Financial Sentiment"
    elif score > -0.6:
        return "Moderately Negative Financial Sentiment"
    else:
        return "Strong Negative Financial Sentiment"


def _compute_uncertainty(probabilities: dict) -> dict:
    """Compute prediction uncertainty from probability distribution entropy."""
    probs = [probabilities["positive"], probabilities["neutral"], probabilities["negative"]]

    # Shannon entropy
    entropy = 0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)

    # Max entropy for 3 classes is log2(3) ≈ 1.585
    max_entropy = math.log2(3)
    normalized_entropy = entropy / max_entropy

    if normalized_entropy < 0.3:
        level = "Low"
    elif normalized_entropy < 0.6:
        level = "Medium"
    else:
        level = "High"

    # Confidence threshold check
    max_prob = max(probs)
    conflicting = max_prob < 0.5

    return {
        "entropy": round(entropy, 4),
        "normalized_entropy": round(normalized_entropy, 4),
        "level": level,
        "conflicting_signals": conflicting,
        "message": (
            "Prediction contains conflicting financial signals."
            if conflicting
            else f"Model shows {level.lower()} uncertainty in this prediction."
        ),
    }


def _detect_contradictions(sentence_analysis: list) -> dict:
    """Detect conflicting sentiments across sentences."""
    if len(sentence_analysis) < 2:
        return {"detected": False, "details": []}

    sentiments = [s.get("sentiment", "neutral") for s in sentence_analysis]
    has_positive = "positive" in sentiments
    has_negative = "negative" in sentiments

    if not (has_positive and has_negative):
        return {"detected": False, "details": []}

    positive_sentences = [
        s for s in sentence_analysis if s.get("sentiment") == "positive"
    ]
    negative_sentences = [
        s for s in sentence_analysis if s.get("sentiment") == "negative"
    ]

    return {
        "detected": True,
        "message": "Conflicting financial signals detected in this article.",
        "positive_sentences": [
            {"sentence": s["sentence"], "confidence": s["confidence"]}
            for s in positive_sentences
        ],
        "negative_sentences": [
            {"sentence": s["sentence"], "confidence": s["confidence"]}
            for s in negative_sentences
        ],
    }


def _compute_sentiment_dna(text: str, prediction: dict, sentences: list) -> dict:
    """Compute the Sentiment DNA fingerprint."""
    text_lower = text.lower()

    # Optimism: based on positive probability + positive keywords
    positive_keyword_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    optimism = min(100, int(prediction["probabilities"]["positive"] * 70 + positive_keyword_count * 5))

    # Risk: based on risk keywords
    risk_count = sum(1 for kw in RISK_KEYWORDS if kw in text_lower)
    risk = min(100, int(prediction["probabilities"]["negative"] * 40 + risk_count * 15))

    # Uncertainty: based on entropy + uncertainty keywords
    uncertainty_count = sum(1 for kw in UNCERTAINTY_KEYWORDS if kw in text_lower)
    uncertainty_val = min(100, int(prediction["probabilities"]["neutral"] * 50 + uncertainty_count * 10))

    # Growth: based on growth keywords
    growth_count = sum(1 for kw in GROWTH_KEYWORDS if kw in text_lower)
    growth = min(100, int(growth_count * 15 + prediction["probabilities"]["positive"] * 30))

    # Profitability: based on profitability keywords
    profit_count = sum(1 for kw in PROFITABILITY_KEYWORDS if kw in text_lower)
    profitability = min(100, int(profit_count * 15 + prediction["probabilities"]["positive"] * 25))

    # Volatility: based on mixed signals
    if sentences and len(sentences) > 1:
        scores = [s.get("sentiment_score", 0) for s in sentences]
        import numpy as np
        volatility = min(100, int(np.std(scores) * 100 + 20))
    else:
        volatility = min(100, int(prediction["probabilities"]["neutral"] * 40 + 15))

    return {
        "optimism": optimism,
        "risk": risk,
        "uncertainty": uncertainty_val,
        "growth": growth,
        "profitability": profitability,
        "volatility": volatility,
    }


def _extract_signal_words(text: str, token_importance: list, tokens: list) -> tuple:
    """Extract positive and negative signal words based on attention + lexicon."""
    text_lower = text.lower()
    positive_signals = []
    negative_signals = []

    # From attention-weighted tokens
    if tokens and token_importance:
        # Pair tokens with importance (skip CLS)
        token_scores = list(zip(tokens[1:], token_importance[1:]))
        token_scores.sort(key=lambda x: x[1], reverse=True)

        for token, score in token_scores[:20]:
            if score < 0.2:
                break
            if any(kw in token for kw in POSITIVE_KEYWORDS) or token in POSITIVE_KEYWORDS:
                positive_signals.append({"word": token, "importance": score})
            elif any(kw in token for kw in NEGATIVE_KEYWORDS) or token in NEGATIVE_KEYWORDS:
                negative_signals.append({"word": token, "importance": score})

    # From lexicon matching (multi-word phrases)
    for kw in POSITIVE_KEYWORDS:
        if " " in kw and kw in text_lower:
            positive_signals.append({"word": kw, "importance": 0.7})
    for kw in NEGATIVE_KEYWORDS:
        if " " in kw and kw in text_lower:
            negative_signals.append({"word": kw, "importance": 0.7})

    # Deduplicate
    seen = set()
    dedup_pos = []
    for s in positive_signals:
        if s["word"] not in seen:
            seen.add(s["word"])
            dedup_pos.append(s)

    seen = set()
    dedup_neg = []
    for s in negative_signals:
        if s["word"] not in seen:
            seen.add(s["word"])
            dedup_neg.append(s)

    return dedup_pos[:8], dedup_neg[:8]


def _generate_reasoning(prediction: dict, positive_signals: list, negative_signals: list, contradictions: dict) -> str:
    """Generate model reasoning summary from attention data + templates."""
    sentiment = prediction["sentiment"]
    confidence = prediction["confidence"]

    pos_words = [s["word"] for s in positive_signals[:3]]
    neg_words = [s["word"] for s in negative_signals[:3]]

    if sentiment == "positive":
        if neg_words:
            reasoning = (
                f"Positive sentiment is primarily driven by {', '.join(pos_words)}. "
                f"{'Negative signals from ' + ', '.join(neg_words) + ' introduce minor concerns' if neg_words else ''} "
                f"but do not outweigh the positive indicators."
            )
        else:
            reasoning = (
                f"Strong positive sentiment driven by {', '.join(pos_words) if pos_words else 'overall positive context'}. "
                f"No significant negative signals detected."
            )
    elif sentiment == "negative":
        if pos_words:
            reasoning = (
                f"Negative sentiment is driven by {', '.join(neg_words) if neg_words else 'overall negative context'}. "
                f"{'Positive signals from ' + ', '.join(pos_words) + ' provide partial offset' if pos_words else ''} "
                f"but insufficient to reverse the bearish outlook."
            )
        else:
            reasoning = (
                f"Strong negative sentiment detected from {', '.join(neg_words) if neg_words else 'overall negative context'}. "
                f"No significant positive counterbalancing signals."
            )
    else:
        reasoning = (
            f"The text contains balanced or ambiguous financial signals. "
            f"{'Positive factors include ' + ', '.join(pos_words) + '. ' if pos_words else ''}"
            f"{'Negative factors include ' + ', '.join(neg_words) + '. ' if neg_words else ''}"
            f"The model assigns neutral sentiment with {confidence*100:.1f}% confidence."
        )

    if contradictions.get("detected"):
        reasoning += " Note: Conflicting signals were detected across different parts of the text."

    return reasoning.strip()


def _generate_highlights(text: str, tokens: list, importance: list) -> list:
    """Generate word-level highlights with importance scores for the original text."""
    if not tokens or not importance:
        return []

    # Build a map of token → max importance
    token_imp = {}
    for tok, imp in zip(tokens[1:], importance[1:]):  # skip CLS
        if tok not in token_imp or imp > token_imp[tok]:
            token_imp[tok] = imp

    # Split original text into words and assign importance
    words = text.split()
    highlights = []
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        imp = token_imp.get(clean_word, 0.0)

        # Determine highlight type based on lexicon + importance
        highlight_type = "neutral"
        if imp > 0.3:
            if clean_word in POSITIVE_KEYWORDS or any(kw in clean_word for kw in POSITIVE_KEYWORDS):
                highlight_type = "positive"
            elif clean_word in NEGATIVE_KEYWORDS or any(kw in clean_word for kw in NEGATIVE_KEYWORDS):
                highlight_type = "negative"
            elif imp > 0.5:
                highlight_type = "important"

        highlights.append({
            "word": word,
            "importance": round(imp, 4),
            "type": highlight_type,
        })

    return highlights
