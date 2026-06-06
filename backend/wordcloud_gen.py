import base64
import io
import re

from wordcloud import WordCloud, STOPWORDS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


_EXTRA_STOP = {"said", "also", "would", "could", "one", "may", "like", "get", "us"}
_STOPWORDS = STOPWORDS | _EXTRA_STOP


def generate_wordcloud(text: str) -> str:
    """Return a base64-encoded PNG of the word cloud."""
    clean = re.sub(r"[^a-zA-Z\s]", " ", text)
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        stopwords=_STOPWORDS,
        max_words=100,
        colormap="RdYlGn",
    ).generate(clean)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
