"""
FinSight AI — Text Preprocessing
Cleans and normalizes financial text for model input.
"""

import re
import string


def clean_text(text: str) -> str:
    """Full preprocessing pipeline for financial text."""
    if not text or not isinstance(text, str):
        return ""

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize financial symbols
    text = text.replace("$", " dollar ")
    text = text.replace("€", " euro ")
    text = text.replace("£", " pound ")
    text = text.replace("¥", " yen ")
    text = text.replace("₹", " rupee ")

    # Keep percentage signs as words
    text = re.sub(r"(\d+)\s*%", r"\1 percent", text)

    # Normalize numbers with commas: 1,000,000 -> 1000000
    text = re.sub(r"(\d),(\d{3})", r"\1\2", text)

    # Normalize decimal numbers
    text = re.sub(r"(\d+)\.(\d+)", r"\1 point \2", text)

    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\w\s.,!?;:\-'\"]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Lowercase
    text = text.lower()

    return text


def tokenize_simple(text: str) -> list:
    """Simple whitespace + punctuation tokenizer."""
    if not text:
        return []
    # Split on whitespace and punctuation boundaries
    tokens = re.findall(r"\b\w+\b", text.lower())
    return tokens


def split_sentences(text: str) -> list:
    """Split text into sentences for sentence-level analysis."""
    if not text:
        return []

    # Split on sentence-ending punctuation followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Filter empty and very short sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    return sentences
