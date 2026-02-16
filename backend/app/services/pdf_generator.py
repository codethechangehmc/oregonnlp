"""Generate PDF reports using fpdf2."""

from datetime import datetime

from fpdf import FPDF


def _sanitize_pdf_text(text: str) -> str:
    """Replace characters that cause FPDF rendering issues."""
    if not text or not isinstance(text, str):
        return ""
    # Replace non-ASCII and control chars to avoid "Not enough horizontal space" errors
    return "".join(
        c if 32 <= ord(c) < 127 and c not in ("\x00", "\r") else "?"
        for c in str(text)
    ).strip() or " "


def generate_pdf(analysis: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Topic Analysis Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Summary
    summary = analysis["summary"]
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Total responses: {summary['total_responses']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Topics found: {summary['num_topics']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Topics
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Topics", new_x="LMARGIN", new_y="NEXT")

    for topic in analysis["topics"]:
        if topic["topic_id"] == -1:
            continue
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(
            0, 7,
            f"{topic['label']}  ({topic['count']} responses, {topic['percentage']}%)",
            new_x="LMARGIN", new_y="NEXT",
        )
        if topic.get("description"):
            pdf.set_font("Helvetica", "I", 9)
            w = getattr(pdf, "epw", pdf.w - pdf.l_margin - pdf.r_margin)
            pdf.multi_cell(w, 5, _sanitize_pdf_text(topic["description"]))
        if topic.get("category"):
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, f"Category: {topic['category']}", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, f"Keywords: {', '.join(topic['keywords'][:8])}", new_x="LMARGIN", new_y="NEXT")

        # Sample responses
        samples = topic.get("sample_responses", [])[:3]
        if samples:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 6, "Sample responses:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            w = getattr(pdf, "epw", pdf.w - pdf.l_margin - pdf.r_margin)
            for s in samples:
                raw = (s or "")[:120] + ("..." if len(s or "") > 120 else "")
                text = _sanitize_pdf_text(raw) or "?"
                pdf.multi_cell(w, 5, f"  - {text}")

    # Outlier section
    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)
    if outlier:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(
            0, 7,
            f"Unclassified ({outlier['count']} responses, {outlier['percentage']}%)",
            new_x="LMARGIN", new_y="NEXT",
        )

    return bytes(pdf.output())
