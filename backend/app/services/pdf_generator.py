"""Generate PDF reports using fpdf2 — professional survey topic analysis layout."""

from datetime import datetime

from fpdf import FPDF
from fpdf.enums import MethodReturnValue

# PDF core serif (Times Roman). Renders like a Times New Roman report; no font files required.
FONT = "Times"


def _sanitize_pdf_text(text: str) -> str:
    """Replace characters that cause FPDF rendering issues."""
    if not text or not isinstance(text, str):
        return ""
    return "".join(
        c if 32 <= ord(c) < 127 and c not in ("\x00", "\r") else "?"
        for c in str(text)
    ).strip() or " "


# Refined palette: slate + teal accent (print-friendly)
C_PRIMARY = (30, 58, 95)  # headings, bars
C_ACCENT = (14, 116, 144)  # teal highlights, quote bar
C_TEXT = (45, 55, 72)
C_MUTED = (113, 128, 150)
C_BORDER = (226, 232, 240)
C_SURFACE = (247, 250, 252)
C_SURFACE_STRONG = (237, 242, 247)
C_WHITE = (255, 255, 255)
C_WARN_BG = (255, 251, 235)
C_WARN_BORDER = (214, 158, 46)


class AnalysisReportPDF(FPDF):
    """Report PDF with consistent footer and page totals."""

    def __init__(self, doc_title: str = "Topic Analysis Report", analysis_id_short: str = ""):
        super().__init__()
        self.doc_title = doc_title
        self.analysis_id_short = analysis_id_short
        self.set_auto_page_break(auto=True, margin=28)
        self.alias_nb_pages()

    def footer(self) -> None:
        self.set_y(-20)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)
        self.set_font(FONT, "", 8)
        self.set_text_color(*C_MUTED)
        left = self.doc_title[:42] + ("..." if len(self.doc_title) > 42 else "")
        id_part = f"  |  ID {self.analysis_id_short}" if self.analysis_id_short else ""
        self.cell(self.epw / 2, 5, left + id_part, align="L")
        self.set_font(FONT, "", 8)
        self.cell(self.epw / 2, 5, f"Page {self.page_no()} of {{nb}}", align="R", new_x="LMARGIN", new_y="NEXT")


def _ensure_space(pdf: FPDF, min_mm: float) -> None:
    if pdf.get_y() + min_mm > pdf.h - pdf.b_margin:
        pdf.add_page()


def _hero_header(pdf: AnalysisReportPDF, generated_at: str, analysis_id_short: str) -> None:
    pdf.set_fill_color(*C_PRIMARY)
    pdf.set_text_color(*C_WHITE)
    band_h = 36
    pdf.rect(pdf.l_margin, pdf.get_y(), pdf.epw, band_h, "F")

    y0 = pdf.get_y()
    pad = 8
    pdf.set_xy(pdf.l_margin + pad, y0 + 7)
    pdf.set_font(FONT, "", 8)
    pdf.cell(0, 5, "QUALITATIVE SURVEY ANALYSIS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + pad)
    pdf.set_font(FONT, "B", 20)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(0, 12, "Topic Analysis Report", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(pdf.l_margin + pad)
    pdf.set_font(FONT, "", 10)
    meta = f"Generated {generated_at}"
    if analysis_id_short:
        meta += f"   |   Reference {analysis_id_short}"
    pdf.cell(0, 6, meta, new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(y0 + band_h + 12)
    pdf.set_text_color(*C_TEXT)


def _section_heading(pdf: FPDF, title: str, subtitle: str | None = None) -> None:
    pdf.set_font(FONT, "B", 12)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    if subtitle:
        pdf.set_font(FONT, "", 9)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 5, subtitle, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_text_color(*C_TEXT)


def _summary_cards(pdf: FPDF, total_responses: int, num_topics: int) -> None:
    col_gap = 8
    col_w = (pdf.epw - col_gap) / 2
    inner_pad = 6
    # Subtitle ends at y + inner_pad + 25 (label/value/sub layout); add room below inside the box
    bottom_pad_inside = 8
    card_h = inner_pad + 25 + bottom_pad_inside
    y = pdf.get_y()

    for i, (label, value, sub) in enumerate(
        [
            ("Total responses analyzed", str(total_responses), "Open-ended survey answers in this run"),
            ("Distinct topics", str(num_topics), "Themes identified by the model"),
        ]
    ):
        x = pdf.l_margin + i * (col_w + col_gap)
        pdf.set_xy(x, y)
        pdf.set_fill_color(*C_SURFACE)
        pdf.set_draw_color(*C_BORDER)
        pdf.rect(x, y, col_w, card_h, "FD")

        pdf.set_xy(x + inner_pad, y + inner_pad)
        pdf.set_font(FONT, "", 8)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(col_w - 2 * inner_pad, 5, label.upper())

        pdf.set_xy(x + inner_pad, y + inner_pad + 7)
        pdf.set_font(FONT, "B", 18)
        pdf.set_text_color(*C_ACCENT)
        pdf.cell(col_w - 2 * inner_pad, 11, value)

        pdf.set_xy(x + inner_pad, y + inner_pad + 20)
        pdf.set_font(FONT, "", 8)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(col_w - 2 * inner_pad, 5, sub)

    pdf.set_y(y + card_h + 4)
    pdf.set_text_color(*C_TEXT)


def _representative_responses_layout(
    pdf: FPDF,
    content_w: float,
    items: list[str],
) -> tuple[float, float, float, float, float, float]:
    """Dry-run height for bullets + layout constants (must match _draw_representative_responses)."""
    bullet_col = 5.5
    item_gap = 2.5
    r_dot = 0.55
    lh = 5.5
    w_text = content_w - bullet_col

    pdf.set_font(FONT, "", 9)
    total_h = 0.0
    for i, t in enumerate(items):
        h_item = pdf.multi_cell(
            w_text,
            lh,
            t,
            dry_run=True,
            output=MethodReturnValue.HEIGHT,
        )
        total_h += float(h_item)
        if i < len(items) - 1:
            total_h += item_gap
    return total_h, w_text, bullet_col, item_gap, lh, r_dot


def _draw_representative_responses(
    pdf: FPDF,
    inner_x: float,
    content_w: float,
    items: list[str],
) -> None:
    """Circular bullets with indented wrapped text (no surrounding box)."""
    _, w_text, bullet_col, item_gap, lh, r_dot = _representative_responses_layout(pdf, content_w, items)

    pdf.set_text_color(*C_TEXT)
    for i, t in enumerate(items):
        y_line = pdf.get_y()
        pdf.set_fill_color(*C_ACCENT)
        pdf.circle(inner_x + 1.0, y_line + lh / 2, r_dot, "F")
        pdf.set_xy(inner_x + bullet_col, y_line)
        pdf.set_font(FONT, "", 9)
        pdf.set_text_color(*C_TEXT)
        pdf.multi_cell(w_text, lh, t)
        if i < len(items) - 1:
            pdf.ln(item_gap)


def _topic_card(
    pdf: FPDF,
    topic: dict,
    index: int,
) -> None:
    _ensure_space(pdf, 68)

    card_x = pdf.l_margin
    card_w = pdf.epw
    y_top = pdf.get_y()

    inner_pad = 11
    inner_x = card_x + inner_pad
    top_pad = 7
    pdf.set_xy(inner_x, y_top + top_pad)

    # Index badge
    badge = f"{index:02d}"
    pdf.set_font(FONT, "B", 8)
    tw = pdf.get_string_width(badge) + 5
    pdf.set_fill_color(*C_SURFACE_STRONG)
    pdf.set_draw_color(*C_BORDER)
    pdf.rect(inner_x, y_top + top_pad - 0.5, tw + 2, 7, "FD")
    pdf.set_xy(inner_x + 2, y_top + top_pad + 0.5)
    pdf.set_text_color(*C_ACCENT)
    pdf.cell(tw, 5, badge)

    # Title (may wrap)
    pdf.set_xy(inner_x + tw + 9, y_top + top_pad)
    pdf.set_font(FONT, "B", 13)
    pdf.set_text_color(*C_PRIMARY)
    title = _sanitize_pdf_text(topic.get("label") or "Untitled topic")
    pdf.multi_cell(card_w - (inner_x - card_x) - tw - 18, 7, title)

    y_after_title = pdf.get_y()

    # Meta row: share, count, category
    pdf.set_xy(inner_x, y_after_title + 3)
    pdf.set_font(FONT, "", 9)
    pdf.set_text_color(*C_MUTED)
    pct = topic.get("percentage", 0)
    count = topic.get("count", 0)
    meta_parts = [f"{pct}% of corpus", f"n={count}"]
    cat = topic.get("category") or ""
    if cat:
        meta_parts.append(f"Category: {_sanitize_pdf_text(cat)}")
    pdf.cell(0, 6, "   |   ".join(meta_parts), new_x="LMARGIN", new_y="NEXT")

    # Description in tinted block
    desc = topic.get("description") or ""
    if desc:
        desc = _sanitize_pdf_text(desc)
        pdf.ln(4)
        pdf.set_x(inner_x)
        w_desc = card_w - 2 * inner_pad
        pdf.set_font(FONT, "", 10)
        pdf.set_text_color(*C_TEXT)
        pdf.multi_cell(w_desc, 6, desc, align="L")

    # Keywords
    keywords_list = topic.get("keywords") or []
    if keywords_list:
        pdf.ln(4)
        pdf.set_x(inner_x)
        pdf.set_font(FONT, "B", 8)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 5, "KEYWORDS", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_x(inner_x)
        pdf.set_font(FONT, "", 9)
        pdf.set_text_color(*C_TEXT)
        kw_text = "  |  ".join(_sanitize_pdf_text(str(k)) for k in keywords_list[:12])
        pdf.multi_cell(card_w - 2 * inner_pad, 5.5, kw_text)

    # Representative responses — circular bullets, indented text (no box)
    samples = topic.get("sample_responses") or []
    response_lines = [_sanitize_pdf_text(response) for response in samples[:3] if response]
    if response_lines:
        content_w = card_w - 2 * inner_pad
        block_h, *_ = _representative_responses_layout(pdf, content_w, response_lines)
        y_here = pdf.get_y()
        reserve_below = 5 + 6 + 2 + block_h  # ln(5) + title + ln(2) + bullets
        trigger = pdf.page_break_trigger
        if y_here + reserve_below > trigger:
            y_top_margin = pdf.t_margin
            if y_top_margin + reserve_below <= trigger:
                pdf.add_page()

        pdf.ln(5)
        pdf.set_x(inner_x)
        pdf.set_font(FONT, "B", 9)
        pdf.set_text_color(*C_PRIMARY)
        pdf.cell(0, 6, "Representative responses", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        _draw_representative_responses(pdf, inner_x, content_w, response_lines)

    y_bottom = pdf.get_y() + 7

    # Card border + left stripe full height
    h_card = y_bottom - y_top
    pdf.set_fill_color(*C_ACCENT)
    pdf.rect(card_x, y_top, 3.5, h_card, "F")
    pdf.set_draw_color(*C_BORDER)
    pdf.set_line_width(0.2)
    pdf.rect(card_x, y_top, card_w, h_card, "D")

    pdf.set_y(y_bottom)
    pdf.ln(6)


def _outlier_section(pdf: FPDF, outlier: dict) -> None:
    _ensure_space(pdf, 36)
    pdf.set_fill_color(*C_WARN_BG)
    pdf.set_draw_color(*C_WARN_BORDER)
    y0 = pdf.get_y()
    box_h = 26
    pdf.rect(pdf.l_margin, y0, pdf.epw, box_h, "FD")
    pad = 7
    pdf.set_xy(pdf.l_margin + pad, y0 + pad)
    pdf.set_font(FONT, "B", 11)
    pdf.set_text_color(*C_PRIMARY)
    pdf.cell(0, 6, "Other / unclassified", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + pad)
    pdf.set_font(FONT, "", 9)
    pdf.set_text_color(*C_TEXT)
    pdf.cell(
        0,
        6,
        f"{outlier['count']} responses ({outlier['percentage']}%) did not align strongly with the topics above.",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_y(y0 + box_h + 4)


def generate_pdf(analysis: dict) -> bytes:
    analysis_id = analysis.get("analysis_id") or ""
    short_id = (analysis_id[:8] + "...") if len(analysis_id) > 8 else analysis_id

    pdf = AnalysisReportPDF(
        doc_title="Topic Analysis Report",
        analysis_id_short=short_id,
    )
    pdf.set_margins(22, 24, 22)
    pdf.add_page()

    generated_at = datetime.now().strftime("%B %d, %Y  |  %H:%M")
    _hero_header(pdf, generated_at, short_id)

    summary = analysis["summary"]
    _section_heading(
        pdf,
        "At a glance",
        "High-level statistics for this analysis run.",
    )
    _summary_cards(pdf, summary["total_responses"], summary["num_topics"])

    topics_main = [t for t in analysis["topics"] if t["topic_id"] != -1]
    n_topics = len(topics_main)

    pdf.ln(8)
    _section_heading(
        pdf,
        "Topic breakdown",
        f"{n_topics} themes ordered by prevalence in the response set.",
    )

    for i, topic in enumerate(topics_main, start=1):
        _topic_card(pdf, topic, i)

    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)
    if outlier:
        pdf.ln(6)
        _section_heading(pdf, "Residual bucket", "Responses outside the main themes.")
        _outlier_section(pdf, outlier)

    pdf.ln(12)
    pdf.set_font(FONT, "", 8)
    pdf.set_text_color(*C_MUTED)
    pdf.multi_cell(
        pdf.epw,
        5,
        "This report was produced automatically. Topic labels and descriptions are model-generated and should be reviewed "
        "before use in formal research or policy documents.",
    )

    return bytes(pdf.output())
