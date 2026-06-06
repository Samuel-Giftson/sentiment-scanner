import base64
import io

import plotly.graph_objects as go
import requests
import streamlit as st

API_BASE = "http://backend:8000"

st.set_page_config(
    page_title="Sentiment Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .result-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
    }
    .badge-positive { color: #16a34a; font-weight: 700; font-size: 1.3rem; }
    .badge-neutral  { color: #d97706; font-weight: 700; font-size: 1.3rem; }
    .badge-negative { color: #dc2626; font-weight: 700; font-size: 1.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🔍 Sentiment Scanner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Analyze the sentiment of text, PDFs, or any webpage.</div>',
    unsafe_allow_html=True,
)

tab_text, tab_pdf, tab_url = st.tabs(["📝 Paste Text", "📄 Upload PDF", "🌐 Enter URL"])


def _gauge(label: str, confidence: float) -> go.Figure:
    color_map = {"Positive": "#22c55e", "Neutral": "#f59e0b", "Negative": "#ef4444"}
    color = color_map.get(label, "#6366f1")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=confidence,
            title={"text": f"Confidence — <b>{label}</b>", "font": {"size": 16}},
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 70], "color": "#fef9c3"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
                "threshold": {
                    "line": {"color": "#1e293b", "width": 3},
                    "thickness": 0.75,
                    "value": confidence,
                },
            },
        )
    )
    fig.update_layout(height=260, margin=dict(t=40, b=10, l=10, r=10))
    return fig


def _render_results(data: dict, source_text: str = "") -> None:
    label = data["label"]
    confidence = data["confidence"]
    explanation = data["explanation"]
    wc_b64 = data.get("wordcloud_base64")

    badge_class = f"badge-{label.lower()}"
    st.markdown(
        f'<div class="result-card">'
        f'<span class="{badge_class}">{label}</span> &nbsp;'
        f'<span style="color:#64748b;font-size:0.95rem;">sentiment detected</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(_gauge(label, confidence), use_container_width=True)
    with col2:
        st.markdown("### Explanation")
        st.write(explanation)

        if source_text:
            report_resp = requests.post(
                f"{API_BASE}/report", json={"text": source_text}, timeout=30
            )
            if report_resp.ok:
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=report_resp.content,
                    file_name="sentiment_report.pdf",
                    mime="application/pdf",
                )

    if wc_b64:
        st.markdown("### Word Cloud")
        img_bytes = base64.b64decode(wc_b64)
        st.image(img_bytes, use_column_width=True)


def _call_api(endpoint: str, **kwargs) -> dict | None:
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", timeout=60, **kwargs)
        if resp.ok:
            return resp.json()
        st.error(f"API error {resp.status_code}: {resp.json().get('detail', resp.text)}")
    except requests.ConnectionError:
        st.error("Cannot reach the backend. Make sure it is running.")
    return None


# ── Tab 1: Text ──────────────────────────────────────────────────────────────
with tab_text:
    text_input = st.text_area(
        "Paste your text here",
        height=200,
        placeholder="Type or paste any text you want to analyze...",
    )
    if st.button("Analyze Text", key="btn_text", type="primary"):
        if not text_input.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Analyzing…"):
                result = _call_api("/analyze/text", json={"text": text_input})
            if result:
                _render_results(result, source_text=text_input)

# ── Tab 2: PDF ───────────────────────────────────────────────────────────────
with tab_pdf:
    uploaded = st.file_uploader("Upload a PDF file", type=["pdf"])
    if st.button("Analyze PDF", key="btn_pdf", type="primary"):
        if uploaded is None:
            st.warning("Please upload a PDF first.")
        else:
            with st.spinner("Extracting and analyzing…"):
                result = _call_api(
                    "/analyze/pdf",
                    files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                )
            if result:
                _render_results(result)

# ── Tab 3: URL ───────────────────────────────────────────────────────────────
with tab_url:
    url_input = st.text_input(
        "Enter a webpage URL",
        placeholder="https://example.com/article",
    )
    if st.button("Analyze URL", key="btn_url", type="primary"):
        if not url_input.strip():
            st.warning("Please enter a URL first.")
        else:
            with st.spinner("Fetching and analyzing…"):
                result = _call_api("/analyze/url", json={"url": url_input})
            if result:
                _render_results(result)
