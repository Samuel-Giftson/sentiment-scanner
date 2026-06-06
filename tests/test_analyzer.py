import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from analyzer import analyze_sentiment, _chunk_text


def test_positive_text():
    result = analyze_sentiment("I absolutely love this product! It's amazing and wonderful.")
    assert result["label"] == "Positive"
    assert 0 < result["confidence"] <= 100
    assert result["explanation"]


def test_negative_text():
    result = analyze_sentiment("This is terrible. I hate it. Worst experience ever.")
    assert result["label"] == "Negative"
    assert result["confidence"] > 50


def test_neutral_text():
    result = analyze_sentiment("The meeting is scheduled for Tuesday at 10am.")
    assert result["label"] in {"Neutral", "Positive", "Negative"}


def test_returns_all_fields():
    result = analyze_sentiment("Hello world.")
    assert "label" in result
    assert "confidence" in result
    assert "explanation" in result


def test_chunking_long_text():
    long = "This is a sentence. " * 300
    chunks = _chunk_text(long)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk.split()) <= 600


def test_chunking_short_text():
    short = "Short text."
    chunks = _chunk_text(short)
    assert len(chunks) == 1
    assert chunks[0] == short
