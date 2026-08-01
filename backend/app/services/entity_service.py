"""
FinSight AI — Entity Extraction Service
Rule-based financial entity extractor with entity-wise sentiment.
"""

import re
from typing import List


# ─── Entity Patterns ──────────────────────────────────────

COMPANY_PATTERNS = [
    # Known major companies
    r"\b(Apple|Google|Microsoft|Amazon|Tesla|Meta|Netflix|Nvidia|AMD|Intel)\b",
    r"\b(JPMorgan|Goldman Sachs|Morgan Stanley|Bank of America|Citigroup|Wells Fargo)\b",
    r"\b(Reliance Industries|Tata|Infosys|Wipro|TCS|HCL|HDFC|ICICI|SBI)\b",
    r"\b(Samsung|Toyota|Sony|Alibaba|Tencent|Baidu|Uber|Lyft|Airbnb|Spotify)\b",
    r"\b(Berkshire Hathaway|Walmart|Disney|Coca-Cola|PepsiCo|Johnson & Johnson)\b",
    r"\b(Pfizer|Moderna|AstraZeneca|Merck|Abbott|Roche|Novartis)\b",
    # Pattern: "X Inc", "X Corp", "X Ltd", "X Group"
    r"\b([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)\s+(?:Inc|Corp|Ltd|Group|Holdings|Co|PLC|AG|SA|NV)\b",
]

PERSON_PATTERNS = [
    r"\b(?:CEO|CFO|CTO|Chairman|President|Director|Founder)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b",
    r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s*,\s*(?:CEO|CFO|CTO|Chairman|President|Director|Founder)\b",
]

SECTOR_KEYWORDS = {
    "Technology": ["technology", "tech", "software", "hardware", "semiconductor", "ai", "artificial intelligence", "cloud", "saas"],
    "Banking": ["banking", "bank", "financial services", "lending", "credit", "deposits"],
    "Healthcare": ["healthcare", "pharma", "pharmaceutical", "biotech", "medical", "drug", "vaccine"],
    "Energy": ["energy", "oil", "gas", "petroleum", "renewable", "solar", "wind", "nuclear"],
    "Automobile": ["automobile", "automotive", "car", "vehicle", "ev", "electric vehicle"],
    "Consumer": ["consumer", "retail", "e-commerce", "fmcg", "consumer goods"],
    "Telecom": ["telecom", "telecommunications", "wireless", "broadband", "5g"],
    "Finance": ["finance", "insurance", "asset management", "investment", "mutual fund"],
    "Real Estate": ["real estate", "property", "housing", "reit"],
    "Industrial": ["industrial", "manufacturing", "construction", "infrastructure"],
}

CURRENCY_PATTERNS = [
    r"\b(USD|EUR|GBP|JPY|INR|CNY|AUD|CAD|CHF)\b",
    r"\b(dollar|euro|pound|yen|rupee|yuan)\b",
]

COUNTRY_PATTERNS = [
    r"\b(United States|US|USA|America|China|India|Japan|Germany|UK|United Kingdom|France|Canada|Australia|Brazil|Russia)\b",
]

FINANCIAL_METRICS = {
    "Revenue": [r"\brevenue\b", r"\bsales\b", r"\btop.?line\b"],
    "Profit": [r"\bprofit\b", r"\bnet income\b", r"\bbottom.?line\b"],
    "Earnings": [r"\bearnings\b", r"\beps\b", r"\bearnings per share\b"],
    "Margin": [r"\bmargin\b", r"\bgross margin\b", r"\boperating margin\b"],
    "Growth": [r"\bgrowth\b", r"\byoy\b", r"\byear.over.year\b"],
    "Market Cap": [r"\bmarket cap\b", r"\bvaluation\b"],
    "Dividend": [r"\bdividend\b", r"\byield\b"],
    "Debt": [r"\bdebt\b", r"\bleverage\b", r"\bliabilities\b"],
    "Cash Flow": [r"\bcash flow\b", r"\bfree cash flow\b", r"\bfcf\b"],
}

EVENT_PATTERNS = {
    "Earnings Report": [r"\bearnings\b.*\breport\b", r"\bquarterly results\b", r"\bq[1-4]\b.*\bresults\b", r"\bfiscal\b.*\bresults\b"],
    "Acquisition": [r"\bacquir\w+\b", r"\bacquisition\b", r"\btakeover\b", r"\bbuyout\b"],
    "Merger": [r"\bmerger\b", r"\bmerge\b"],
    "Layoffs": [r"\blayoff\b", r"\bjob cut\b", r"\bdownsiz\w+\b", r"\brestructur\w+\b"],
    "Investment": [r"\binvest\w+\b", r"\bfunding\b", r"\braise\w*\s+capital\b"],
    "Product Launch": [r"\blaunch\w*\b", r"\breleas\w+\b", r"\bunveil\w*\b", r"\bannounce\w*\s+product\b"],
    "Leadership Change": [r"\bappoint\w+\b", r"\bresign\w+\b", r"\bstep\w*\s+down\b", r"\bnew\s+ceo\b"],
    "Regulatory Action": [r"\bregulat\w+\b", r"\bfine\b", r"\bpenalty\b", r"\bcompliance\b", r"\bantitrust\b"],
    "Interest Rate Decision": [r"\binterest rate\b", r"\bfed\b.*\brate\b", r"\bmonetary policy\b"],
    "IPO": [r"\bipo\b", r"\binitial public offering\b", r"\bpublic listing\b"],
    "Stock Buyback": [r"\bbuyback\b", r"\bshare repurchase\b"],
    "Dividend": [r"\bdividend\b.*\b(?:declared|announced|increased|cut)\b"],
    "Legal Dispute": [r"\blawsuit\b", r"\blitigation\b", r"\blegal\b", r"\bsue\b"],
    "Partnership": [r"\bpartnership\b", r"\bcollaboration\b", r"\bjoint venture\b", r"\balliance\b"],
    "GDP": [r"\bgdp\b", r"\bgross domestic product\b"],
    "Inflation": [r"\binflation\b", r"\bcpi\b", r"\bconsumer price\b"],
}

EVENT_IMPORTANCE = {
    "Earnings Report": "HIGH",
    "Acquisition": "HIGH",
    "Merger": "HIGH",
    "Layoffs": "HIGH",
    "IPO": "HIGH",
    "Regulatory Action": "HIGH",
    "Interest Rate Decision": "HIGH",
    "Investment": "MEDIUM",
    "Product Launch": "MEDIUM",
    "Leadership Change": "MEDIUM",
    "Stock Buyback": "MEDIUM",
    "Dividend": "MEDIUM",
    "Legal Dispute": "HIGH",
    "Partnership": "LOW",
    "GDP": "MEDIUM",
    "Inflation": "HIGH",
}


def extract_entities(text: str, prediction: dict = None) -> dict:
    """Extract all financial entities from text."""
    entities = []

    # ─── Companies ────────────────────────────────────────
    companies = _extract_companies(text)
    for company in companies:
        entities.append({
            "entity": company,
            "type": "Company",
            "sentiment": None,
            "confidence": None,
        })

    # ─── People ───────────────────────────────────────────
    people = _extract_people(text)
    for person in people:
        entities.append({
            "entity": person,
            "type": "Person",
            "sentiment": None,
            "confidence": None,
        })

    # ─── Sectors ──────────────────────────────────────────
    sectors = _extract_sectors(text)
    for sector in sectors:
        entities.append({
            "entity": sector,
            "type": "Sector",
            "sentiment": None,
            "confidence": None,
        })

    # ─── Currencies ───────────────────────────────────────
    currencies = _extract_currencies(text)
    for currency in currencies:
        entities.append({
            "entity": currency,
            "type": "Currency",
            "sentiment": None,
            "confidence": None,
        })

    # ─── Countries ────────────────────────────────────────
    countries = _extract_countries(text)
    for country in countries:
        entities.append({
            "entity": country,
            "type": "Country",
            "sentiment": None,
            "confidence": None,
        })

    # ─── Financial Metrics ────────────────────────────────
    metrics = _extract_metrics(text)
    for metric in metrics:
        entities.append({
            "entity": metric,
            "type": "Financial Metric",
            "sentiment": None,
            "confidence": None,
        })

    # ─── Entity-wise Sentiment ────────────────────────────
    if prediction:
        entities = _assign_entity_sentiment(entities, text, prediction)

    # Deduplicate
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e["entity"], e["type"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    return {
        "entities": unique_entities,
        "count": len(unique_entities),
    }


def detect_events(text: str, prediction: dict = None) -> list:
    """Detect financial events in text."""
    text_lower = text.lower()
    events = []

    for event_type, patterns in EVENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                sentiment = prediction.get("sentiment", "neutral") if prediction else "neutral"
                events.append({
                    "event": event_type,
                    "importance": EVENT_IMPORTANCE.get(event_type, "MEDIUM"),
                    "sentiment": sentiment,
                })
                break  # Only match first pattern per event type

    return events


def _extract_companies(text: str) -> List[str]:
    companies = set()
    for pattern in COMPANY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if len(match) > 1:
                companies.add(match.strip())
    return list(companies)


def _extract_people(text: str) -> List[str]:
    people = set()
    for pattern in PERSON_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if len(match) > 2:
                people.add(match.strip())
    return list(people)


def _extract_sectors(text: str) -> List[str]:
    text_lower = text.lower()
    sectors = set()
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                sectors.add(sector)
                break
    return list(sectors)


def _extract_currencies(text: str) -> List[str]:
    currencies = set()
    for pattern in CURRENCY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            currencies.add(match.upper() if len(match) <= 3 else match.title())
    return list(currencies)


def _extract_countries(text: str) -> List[str]:
    countries = set()
    for pattern in COUNTRY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            countries.add(match)
    return list(countries)


def _extract_metrics(text: str) -> List[str]:
    text_lower = text.lower()
    metrics = set()
    for metric, patterns in FINANCIAL_METRICS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                metrics.add(metric)
                break
    return list(metrics)


def _assign_entity_sentiment(entities: list, text: str, prediction: dict) -> list:
    """Assign sentiment to entities based on surrounding context."""
    from app.ml.inference import engine

    for entity in entities:
        entity_name = entity["entity"]
        # Find sentences containing this entity
        sentences = text.split(".")
        entity_sentences = [
            s.strip() for s in sentences
            if entity_name.lower() in s.lower() and len(s.strip()) > 5
        ]

        if entity_sentences and engine.is_loaded:
            # Predict sentiment on the entity's context
            context = ". ".join(entity_sentences[:2])
            try:
                ctx_pred = engine.predict(context)
                entity["sentiment"] = ctx_pred["sentiment"]
                entity["confidence"] = ctx_pred["confidence"]
                entity["sentiment_score"] = ctx_pred["sentiment_score"]
            except Exception:
                entity["sentiment"] = prediction.get("sentiment", "neutral")
                entity["confidence"] = prediction.get("confidence", 0.5)
        else:
            # Fall back to article-level sentiment
            entity["sentiment"] = prediction.get("sentiment", "neutral")
            entity["confidence"] = prediction.get("confidence", 0.5)

    return entities
