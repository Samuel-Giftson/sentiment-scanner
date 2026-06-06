from transformers import pipeline
import re

_sentiment_pipeline = None


def _get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            top_k=None,
        )
    return _sentiment_pipeline


LABEL_MAP = {
    "positive": "Positive",
    "neutral": "Neutral",
    "negative": "Negative",
}

EXPLANATIONS = {
    "Positive": (
        "The text carries an overall positive tone, expressing optimism, satisfaction, or favorable sentiment."
    ),
    "Neutral": (
        "The text is largely neutral, presenting information without strong emotional polarity."
    ),
    "Negative": (
        "The text conveys a negative tone, suggesting dissatisfaction, criticism, or unfavorable sentiment."
    ),
}


def _chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""
    for sent in sentences:
        if len((current + " " + sent).split()) > max_tokens:
            if current:
                chunks.append(current.strip())
            current = sent
        else:
            current = (current + " " + sent).strip()
    if current:
        chunks.append(current.strip())
    return chunks or [text[:2000]]


def analyze_sentiment(text: str) -> dict:
    pipe = _get_pipeline()
    chunks = _chunk_text(text)

    scores: dict[str, float] = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    for chunk in chunks:
        results = pipe(chunk[:512])[0]
        for item in results:
            label = item["label"].lower()
            if label in scores:
                scores[label] += item["score"]

    total = sum(scores.values()) or 1.0
    normalized = {k: v / total for k, v in scores.items()}

    top_label = max(normalized, key=normalized.get)
    mapped = LABEL_MAP[top_label]
    confidence = round(normalized[top_label] * 100, 1)

    return {
        "label": mapped,
        "confidence": confidence,
        "explanation": EXPLANATIONS[mapped],
    }
