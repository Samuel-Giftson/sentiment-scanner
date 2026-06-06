import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


LABEL_COLORS = {
    "Positive": colors.HexColor("#22c55e"),
    "Neutral": colors.HexColor("#f59e0b"),
    "Negative": colors.HexColor("#ef4444"),
}


def generate_pdf_report(text: str, result: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#1e293b"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#334155"),
    )

    label = result["label"]
    confidence = result["confidence"]
    explanation = result["explanation"]
    label_color = LABEL_COLORS.get(label, colors.black)

    story = [
        Paragraph("Sentiment Analysis Report", title_style),
        Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")),
        Spacer(1, 0.4 * cm),
        Paragraph("Results Summary", heading_style),
        Table(
            [
                ["Sentiment", "Confidence"],
                [
                    Paragraph(f'<font color="{label_color.hexval()}">{label}</font>', body_style),
                    Paragraph(f"{confidence}%", body_style),
                ],
            ],
            colWidths=["50%", "50%"],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#475569")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]),
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Explanation", heading_style),
        Paragraph(explanation, body_style),
        Spacer(1, 0.3 * cm),
        Paragraph("Analyzed Text", heading_style),
        Paragraph(text[:2000].replace("\n", "<br/>"), body_style),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.read()
