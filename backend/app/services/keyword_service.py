"""
FinSight AI — Financial Keyword Extraction Service
Extracts top financial keywords using attention weights + lexicon matching.
"""

import re
from collections import Counter


FINANCIAL_LEXICON = {
    "revenue", "earnings", "profit", "loss", "margin", "growth", "decline",
    "dividend", "buyback", "acquisition", "merger", "ipo", "valuation",
    "guidance", "forecast", "outlook", "estimate", "consensus", "target",
    "inflation", "deflation", "gdp", "interest", "rate", "yield",
    "bond", "equity", "stock", "share", "market", "index", "benchmark",
    "bull", "bear", "volatile", "volatility", "liquidity", "credit",
    "debt", "leverage", "default", "downgrade", "upgrade", "rating",
    "cash flow", "operating", "capex", "opex", "ebitda", "eps",
    "pe ratio", "return", "risk", "hedge", "portfolio", "fund",
    "sector", "industry", "supply", "demand", "commodity", "futures",
    "options", "derivatives", "short", "long", "position", "trade",
    "regulation", "compliance", "audit", "restructuring", "layoff",
    "innovation", "technology", "disruption", "expansion", "contraction",
    "recovery", "recession", "stimulus", "fiscal", "monetary",
    "bankruptcy", "insolvency", "impairment", "writedown", "provision",
}


def extract_keywords(text: str, prediction: dict = None) -> list:
    """Extract top financial keywords from text."""
    text_lower = text.lower()

    # Split into words
    words = re.findall(r"\b\w+\b", text_lower)
    word_counts = Counter(words)

    # Score keywords
    keyword_scores = {}

    # Match against financial lexicon
    for word, count in word_counts.items():
        if word in FINANCIAL_LEXICON:
            score = count * 2.0  # Boost financial terms
        elif len(word) > 3:
            score = count * 0.5
        else:
            continue

        keyword_scores[word] = score

    # Check multi-word phrases
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
    for bigram in bigrams:
        if bigram in FINANCIAL_LEXICON:
            keyword_scores[bigram] = keyword_scores.get(bigram, 0) + 3.0

    # Boost keywords with high attention importance
    if prediction and "token_importance" in prediction and "tokens" in prediction:
        tokens = prediction["tokens"]
        importance = prediction["token_importance"]
        for tok, imp in zip(tokens, importance):
            tok_lower = tok.lower()
            if tok_lower in keyword_scores:
                keyword_scores[tok_lower] += imp * 5.0
            elif imp > 0.5 and tok_lower in FINANCIAL_LEXICON:
                keyword_scores[tok_lower] = imp * 5.0

    # Sort by score
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)

    # Return top keywords with formatted labels
    result = []
    for word, score in sorted_keywords[:15]:
        result.append({
            "keyword": word.title(),
            "score": round(score, 2),
            "is_financial": word in FINANCIAL_LEXICON,
        })

    return result
