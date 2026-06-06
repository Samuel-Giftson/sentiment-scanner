import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from unittest.mock import patch, MagicMock

from extractor import extract_from_pdf, extract_from_url


def test_extract_from_url_success():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = "<html><body><p>Hello world, this is a test page.</p></body></html>"

    with patch("extractor.requests.get", return_value=mock_resp):
        text = extract_from_url("http://example.com")

    assert "Hello world" in text


def test_extract_from_url_failure():
    import requests as req
    with patch("extractor.requests.get", side_effect=req.RequestException("timeout")):
        with pytest.raises(ValueError, match="Failed to fetch URL"):
            extract_from_url("http://bad-url.example")


def test_extract_from_url_strips_scripts():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = (
        "<html><body>"
        "<script>var x = 1;</script>"
        "<p>Real content here.</p>"
        "<footer>Footer text</footer>"
        "</body></html>"
    )

    with patch("extractor.requests.get", return_value=mock_resp):
        text = extract_from_url("http://example.com")

    assert "var x" not in text
    assert "Real content" in text
