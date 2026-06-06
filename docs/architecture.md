# Architecture

## Overview

Sentiment Scanner is a two-service application:

1. **Backend** — FastAPI REST API that handles text extraction and sentiment inference.
2. **Frontend** — Streamlit single-page application that provides the user interface.

Both services run inside Docker containers and communicate over an internal Docker network.

## Request Flow

```
User browser
    │
    ▼
Streamlit (port 8501)
    │   HTTP POST /analyze/{text|pdf|url}
    ▼
FastAPI (port 8000)
    ├── extractor.py  ──►  pdfplumber / requests + BeautifulSoup
    ├── analyzer.py   ──►  HuggingFace Transformers (RoBERTa)
    ├── wordcloud_gen.py ► WordCloud + matplotlib → base64 PNG
    └── report.py     ──►  ReportLab → PDF bytes
```

## Sentiment Model

Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`

- Three classes: `positive`, `neutral`, `negative`
- Input is chunked at ~500 tokens to handle long documents
- Per-chunk scores are averaged, then the dominant class wins

## Text Extraction

| Mode | Library | Notes |
|---|---|---|
| PDF | pdfplumber | Page-by-page extraction |
| URL | requests + BeautifulSoup | Strips scripts, nav, footer |
| Text | — | Passed directly |

## Word Cloud

Generated with the `wordcloud` library using the `RdYlGn` colormap.
Common English stop words and a custom list of noise words are removed.
The image is base64-encoded and returned in the API response so the frontend can render it without a second request.

## PDF Report

ReportLab renders a styled A4 document containing:
- Summary table (label + confidence)
- Explanation paragraph
- First 2 000 characters of the source text
