"""Generate PDF reports using fpdf2."""

from datetime import datetime

from fpdf import FPDF


def _sanitize_pdf_text(text: str) -> str:
    """Replace characters that cause FPDF rendering issues."""
    if not text or not isinstance(text, str):
        return ""
    return "".join(
        c if 32 <= ord(c) < 127 and c not in ("\x00", "\r") else "?"
        for c in str(text)
    ).strip() or " "


def generate_pdf(analysis: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Standard professional colors
    NAVY = (31, 78, 121)         # Navy blue
    LIGHT_BLUE = (79, 129, 189)  # Light blue
    DARK_GRAY = (64, 64, 64)     # Dark gray
    LIGHT_GRAY = (242, 242, 242) # Light gray background
    BLACK = (0, 0, 0)            # Black text
    WHITE = (255, 255, 255)      # White

    # ===== TITLE SECTION =====
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 28)
    pdf.ln(4)
    pdf.cell(0, 12, "Topic Analysis Report", new_x="LMARGIN", new_y="NEXT", fill=True, align="L")

    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
             new_x="LMARGIN", new_y="NEXT", fill=False)
    pdf.ln(8)

    # ===== EXECUTIVE SUMMARY =====
    summary = analysis["summary"]
    pdf.set_fill_color(*LIGHT_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 9, "Executive Summary", new_x="LMARGIN", new_y="NEXT", fill=True)

    pdf.set_text_color(*BLACK)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(3)

    # Summary stats with spacing
    pdf.cell(30, 8, "")
    pdf.cell(0, 8, f"Total Responses: {summary['total_responses']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(30, 8, "")
    pdf.cell(0, 8, f"Topics Identified: {summary['num_topics']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ===== TOPICS SECTION =====
    pdf.set_fill_color(*LIGHT_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 9, "Topic Details", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(5)

    topic_count = 0
    for topic in analysis["topics"]:
        if topic["topic_id"] == -1:
            continue

        topic_count += 1

        # Topic title with percentage
        pdf.set_fill_color(*LIGHT_GRAY)
        pdf.set_text_color(*NAVY)
        pdf.set_font("Helvetica", "B", 12)
        topic_title = f"{topic['label']}"
        pdf.cell(0, 8, topic_title, new_x="LMARGIN", new_y="NEXT", fill=True)

        # Response count and percentage
        pdf.set_text_color(*DARK_GRAY)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(20, 6, "")
        pdf.cell(0, 6, f"{topic['count']} responses ({topic['percentage']}%)",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Description
        if topic.get("description"):
            pdf.set_text_color(*BLACK)
            pdf.set_font("Helvetica", "", 11)
            w = pdf.w - pdf.l_margin - pdf.r_margin - 8
            pdf.set_x(pdf.l_margin + 4)
            description_text = _sanitize_pdf_text(topic["description"])
            if description_text:
                pdf.multi_cell(w, 5.5, description_text)
            pdf.ln(2)

        # Keywords section
        keywords_list = topic.get("keywords", [])
        if keywords_list:
            pdf.set_text_color(*DARK_GRAY)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_x(pdf.l_margin + 4)
            keywords_str = ", ".join(str(k) for k in keywords_list[:10])
            w = pdf.w - pdf.l_margin - pdf.r_margin - 8
            pdf.multi_cell(w, 5, f"Key Terms: {keywords_str}")
            pdf.ln(2)

        # Representative quotes
        samples = topic.get("sample_responses", [])
        if samples:
            pdf.set_text_color(*NAVY)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_x(pdf.l_margin + 4)
            pdf.cell(0, 6, "Representative Feedback:", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

            pdf.set_text_color(*BLACK)
            pdf.set_font("Helvetica", "", 10)
            w = pdf.w - pdf.l_margin - pdf.r_margin - 12

            for response in samples[:3]:
                if response:
                    text = _sanitize_pdf_text(response)
                    if text:
                        pdf.set_x(pdf.l_margin + 8)
                        pdf.multi_cell(w - 4, 5, f"- {text}")

        pdf.ln(4)

    # ===== UNCLASSIFIED SECTION =====
    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)
    if outlier:
        pdf.set_fill_color(*LIGHT_GRAY)
        pdf.set_text_color(*NAVY)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Unclassified Responses", new_x="LMARGIN", new_y="NEXT", fill=True)

        pdf.set_text_color(*DARK_GRAY)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.cell(20, 6, "")
        pdf.cell(0, 6, f"{outlier['count']} responses ({outlier['percentage']}%)",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # ===== FOOTER =====
    pdf.ln(6)
    pdf.set_draw_color(*LIGHT_BLUE)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    pdf.ln(3)
    pdf.cell(0, 5, f"Page {pdf.page_no()}", align="C", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
