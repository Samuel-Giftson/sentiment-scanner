from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import uvicorn

from analyzer import analyze_sentiment
from extractor import extract_from_pdf, extract_from_url
from report import generate_pdf_report
from wordcloud_gen import generate_wordcloud

app = FastAPI(title="Sentiment Scanner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextRequest(BaseModel):
    text: str


class UrlRequest(BaseModel):
    url: str


class SentimentResponse(BaseModel):
    label: str
    confidence: float
    explanation: str
    wordcloud_base64: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/text", response_model=SentimentResponse)
def analyze_text(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = analyze_sentiment(req.text)
    result["wordcloud_base64"] = generate_wordcloud(req.text)
    return result


@app.post("/analyze/pdf", response_model=SentimentResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    content = await file.read()
    text = extract_from_pdf(content)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")
    result = analyze_sentiment(text)
    result["wordcloud_base64"] = generate_wordcloud(text)
    return result


@app.post("/analyze/url", response_model=SentimentResponse)
def analyze_url(req: UrlRequest):
    try:
        text = extract_from_url(req.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from URL.")
    result = analyze_sentiment(text)
    result["wordcloud_base64"] = generate_wordcloud(text)
    return result


@app.post("/report")
def export_report(req: TextRequest):
    result = analyze_sentiment(req.text)
    pdf_bytes = generate_pdf_report(req.text, result)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.pdf"},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
