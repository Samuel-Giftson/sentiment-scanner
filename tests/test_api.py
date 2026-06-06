"""
API integration tests.

These patch the heavy model calls so the test suite runs without GPU/large downloads.
"""
import sys
import os

# Ensure the backend directory is importable as a flat package (mirrors how Docker runs it)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

MOCK_RESULT = {
    "label": "Positive",
    "confidence": 92.3,
    "explanation": "The text is positive.",
}

MOCK_ANALYZE = "main.analyze_sentiment"
MOCK_WC = "main.generate_wordcloud"
MOCK_PDF = "main.extract_from_pdf"
MOCK_URL = "main.extract_from_url"


@pytest.fixture()
def client():
    import main as backend_main
    return TestClient(backend_main.app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_analyze_text(client):
    with patch(MOCK_ANALYZE, return_value=dict(MOCK_RESULT)), \
         patch(MOCK_WC, return_value="base64string"):
        resp = client.post("/analyze/text", json={"text": "I love this!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["label"] == "Positive"
    assert body["confidence"] == 92.3


def test_analyze_text_empty(client):
    resp = client.post("/analyze/text", json={"text": "   "})
    assert resp.status_code == 400


def test_analyze_pdf_wrong_extension(client):
    resp = client.post(
        "/analyze/pdf",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


def test_analyze_pdf_ok(client):
    with patch(MOCK_PDF, return_value="extracted text"), \
         patch(MOCK_ANALYZE, return_value=dict(MOCK_RESULT)), \
         patch(MOCK_WC, return_value="base64string"):
        resp = client.post(
            "/analyze/pdf",
            files={"file": ("doc.pdf", b"%PDF-fake", "application/pdf")},
        )
    assert resp.status_code == 200


def test_analyze_url(client):
    with patch(MOCK_URL, return_value="some page text"), \
         patch(MOCK_ANALYZE, return_value=dict(MOCK_RESULT)), \
         patch(MOCK_WC, return_value="base64string"):
        resp = client.post("/analyze/url", json={"url": "http://example.com"})
    assert resp.status_code == 200
    assert resp.json()["label"] == "Positive"
