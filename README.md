# 🔍 Sentiment Scanner

A full-stack sentiment analysis application that accepts **free text**, **PDFs**, or **URLs** and returns a sentiment label (Positive / Neutral / Negative), a confidence score, an explanation, a word cloud, and an exportable PDF report.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Three input modes** | Paste text · Upload PDF · Enter URL |
| **Sentiment analysis** | Powered by `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| **Confidence gauge** | Interactive Plotly gauge chart |
| **Word cloud** | Auto-generated from analysed text |
| **PDF report export** | Download a formatted report via ReportLab |
| **REST API** | FastAPI backend with OpenAPI docs at `/docs` |
| **Containerised** | Docker + Docker Compose one-command startup |
| **Tested** | Pytest suite covering API, analyzer, and extractor |

---

## 🗂 Folder Structure

```
sentiment-scanner/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── analyzer.py        # Sentiment model logic
│   ├── extractor.py       # PDF & URL text extraction
│   ├── wordcloud_gen.py   # Word cloud generation
│   ├── report.py          # PDF report generation
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py             # Streamlit single-page app
│   ├── requirements.txt
│   └── Dockerfile
├── tests/
│   ├── test_api.py
│   ├── test_analyzer.py
│   └── test_extractor.py
├── docs/
│   └── architecture.md
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## 🚀 Quick Start (Docker — recommended)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 24

```bash
# 1. Clone the repo
git clone https://github.com/Samuel-Giftson/sentiment-scanner.git
cd sentiment-scanner

# 2. Build & start both services
docker compose up --build

# 3. Open the app
#   Streamlit UI  → http://localhost:8501
#   API docs      → http://localhost:8000/docs
```

> **Note:** The first build downloads the ~500 MB RoBERTa model. Subsequent starts use the cached layer and are fast.

---

## 🛠 Local Development (without Docker)

### Requirements

- Python 3.11+

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API is now live at **http://localhost:8000**.  
Interactive docs at **http://localhost:8000/docs**.

### Frontend

```bash
cd frontend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Point the frontend at your local backend
# Edit frontend/app.py line: API_BASE = "http://localhost:8000"

streamlit run app.py
```

Streamlit UI is now live at **http://localhost:8501**.

---

## 🔌 API Reference

### `POST /analyze/text`

```json
{ "text": "I love this product!" }
```

### `POST /analyze/pdf`

Multipart form upload — field name `file`, `.pdf` only.

### `POST /analyze/url`

```json
{ "url": "https://example.com/article" }
```

### Response (all three endpoints)

```json
{
  "label": "Positive",
  "confidence": 94.2,
  "explanation": "The text carries an overall positive tone...",
  "wordcloud_base64": "<base64 PNG string>"
}
```

### `POST /report`

Accepts `{ "text": "..." }`, returns a downloadable PDF.

### `GET /health`

Returns `{ "status": "ok" }`.

---

## 🧪 Running Tests

```bash
# From the project root
pip install -r backend/requirements.txt pytest httpx
pytest
```

---

## 🏗 Architecture

```
Browser
  └── Streamlit (port 8501)
        └── HTTP → FastAPI (port 8000)
                    ├── HuggingFace Transformers  (sentiment)
                    ├── pdfplumber                (PDF text)
                    ├── BeautifulSoup + requests  (URL scraping)
                    ├── WordCloud + matplotlib    (word cloud)
                    └── ReportLab                 (PDF report)
```

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `transformers` + `torch` | Sentiment model inference |
| `pdfplumber` | PDF text extraction |
| `beautifulsoup4` | HTML parsing for URL mode |
| `wordcloud` | Word cloud image generation |
| `reportlab` | PDF report generation |
| `streamlit` | Frontend single-page app |
| `plotly` | Interactive gauge chart |

---

## 📄 License

MIT
