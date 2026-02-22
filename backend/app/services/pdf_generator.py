"""Generate comprehensive, beautifully formatted PDF reports using fpdf2."""

from datetime import datetime

from fpdf import FPDF

# ── Colour palette ──────────────────────────────────────────────────────────
_DARK       = (30,  41,  59)   # slate-800
_GREEN      = (22, 120,  74)   # Oregon forest green
_GREEN_LT   = (220, 242, 231)  # light green tint
_LIGHT_BG   = (248, 249, 250)  # near-white
_BORDER     = (226, 232, 240)  # slate-200
_MUTED      = (100, 116, 139)  # slate-500
_WHITE      = (255, 255, 255)
_BLACK      = ( 15,  23,  42)  # near-black

# Distinct colours for topic cards, bars, and tags
_TOPIC_COLORS = [
    ( 22, 120,  74),  # green
    ( 37,  99, 235),  # blue
    (217,  70, 239),  # purple
    (234,  88,  12),  # orange
    ( 15, 118, 110),  # teal
    (220,  38,  38),  # red
    (101,  63, 215),  # indigo
    (161,  98,   7),  # amber
]


def _s(text: str, maxlen: int = 0) -> str:
    """Sanitize text: strip non-ASCII control chars, optionally truncate."""
    if not text:
        return ""
    clean = "".join(c if 32 <= ord(c) < 127 else " " for c in str(text)).strip()
    if maxlen and len(clean) > maxlen:
        clean = clean[:maxlen].rstrip() + "..."
    return clean or " "


# ── Custom FPDF subclass ─────────────────────────────────────────────────────

class _PDF(FPDF):
    def __init__(self, report_title: str = ""):
        super().__init__()
        self._report_title = report_title
        self.set_margins(left=18, top=16, right=18)
        self.set_auto_page_break(auto=True, margin=22)

    @property
    def cw(self) -> float:
        """Usable content width."""
        return self.w - self.l_margin - self.r_margin

    # header / footer are called automatically by fpdf2 on every add_page()
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*_DARK)
        self.rect(0, 0, self.w, 9, "F")
        self.set_fill_color(*_GREEN)
        self.rect(0, 8.5, self.w, 1, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*_WHITE)
        self.set_xy(self.l_margin, 1.5)
        self.cell(self.cw * 0.7, 6, "OREGON NLP  ·  SURVEY TOPIC ANALYSIS REPORT")
        self.cell(self.cw * 0.3, 6, f"Page {self.page_no()}", align="R")
        self.set_text_color(*_BLACK)
        self.set_y(17)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*_BORDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(1.5)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*_MUTED)
        self.cell(0, 5, f"Confidential  ·  Generated {datetime.now().strftime('%B %d, %Y')}", align="C")
        self.set_text_color(*_BLACK)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def h_rule(self, color=_BORDER):
        self.set_draw_color(*color)
        self.line(self.l_margin, self.get_y(), self.l_margin + self.cw, self.get_y())

    def section_banner(self, title: str, subtitle: str = ""):
        """Full-width dark banner used as section dividers."""
        y = self.get_y()
        self.set_fill_color(*_DARK)
        self.rect(self.l_margin, y, self.cw, 12, "F")
        self.set_fill_color(*_GREEN)
        self.rect(self.l_margin, y + 11.5, self.cw, 1.5, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*_WHITE)
        self.set_xy(self.l_margin + 5, y + 2.5)
        self.cell(self.cw - 5, 7.5, _s(title))
        self.set_text_color(*_BLACK)
        self.set_y(y + 14)
        if subtitle:
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(*_MUTED)
            self.cell(0, 5.5, _s(subtitle), new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*_BLACK)
        self.ln(4)


# ── Page builders ────────────────────────────────────────────────────────────

def _cover_page(pdf: _PDF, analysis: dict):
    summary = analysis["summary"]
    topics  = [t for t in analysis["topics"] if t["topic_id"] != -1]
    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)

    # ── DARK HERO — all positions hard-coded so nothing cascades ─────────────

    # Green pinstripe at very top
    pdf.set_fill_color(*_GREEN)
    pdf.rect(0, 0, pdf.w, 2.5, "F")

    # Dark background
    pdf.set_fill_color(*_DARK)
    pdf.rect(0, 2.5, pdf.w, 88, "F")

    # Org label — small-caps style, green, left-aligned
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(105, 175, 135)
    pdf.set_xy(pdf.l_margin, 14)
    pdf.cell(60, 5, "OREGON  NLP")

    # Main title — Times serif, large, left-aligned (editorial, not centered)
    pdf.set_font("Times", "B", 32)
    pdf.set_text_color(*_WHITE)
    pdf.set_xy(pdf.l_margin, 25)
    pdf.cell(pdf.cw, 14, "Survey Topic Analysis")

    # Short decorative green rule under title (not full-width — more intentional)
    pdf.set_fill_color(*_GREEN)
    pdf.rect(pdf.l_margin, 42, 38, 1.5, "F")

    # Descriptor — lighter, smaller, left-aligned
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(155, 185, 200)
    pdf.set_xy(pdf.l_margin, 48)
    pdf.cell(pdf.cw, 6, "Comprehensive NLP Report")

    # Date line
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(110, 140, 160)
    pdf.set_xy(pdf.l_margin, 60)
    pdf.cell(pdf.cw, 5.5, datetime.now().strftime("%B %d, %Y"))

    pdf.set_text_color(*_BLACK)

    # ── STATS ROW — pure typography, no boxes, fixed y=103 ───────────────────
    # Three columns each col_w wide; separator lines between them
    col_w     = pdf.cw / 3
    stats_y   = 103   # ← fixed, never changes between iterations
    num_y     = stats_y
    lbl_y     = stats_y + 14
    sep_top   = stats_y + 2
    sep_bot   = stats_y + 18

    outlier_pct = outlier["percentage"] if outlier else 0
    stats = [
        (str(summary["total_responses"]), "RESPONSES"),
        (str(summary["num_topics"]),      "TOPICS"),
        (f"{100 - outlier_pct:.1f}%",     "CLASSIFIED"),
    ]

    for i, (val, lbl) in enumerate(stats):
        cx = pdf.l_margin + i * col_w

        # Large serif number
        pdf.set_font("Times", "B", 26)
        pdf.set_text_color(*_DARK)
        pdf.set_xy(cx, num_y)
        pdf.cell(col_w, 12, val, align="C")

        # Small-caps label
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_MUTED)
        pdf.set_xy(cx, lbl_y)
        pdf.cell(col_w, 5, lbl, align="C")

        # Vertical separator between columns
        if i < 2:
            sep_x = pdf.l_margin + (i + 1) * col_w
            pdf.set_draw_color(*_BORDER)
            pdf.line(sep_x, sep_top, sep_x, sep_bot)

    pdf.set_text_color(*_BLACK)

    # Thin rule under stats
    rule_y = stats_y + 26
    pdf.set_draw_color(*_BORDER)
    pdf.line(pdf.l_margin, rule_y, pdf.l_margin + pdf.cw, rule_y)

    # ── CONTENTS — fixed start y, left-aligned ────────────────────────────────
    contents_y = rule_y + 10

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.set_xy(pdf.l_margin, contents_y)
    pdf.cell(pdf.cw, 5, "WHAT'S INSIDE")

    contents = [
        "Topic distribution overview with visual breakdown",
        f"Detailed analysis of {summary['num_topics']} identified topics",
        "Keywords, category labels, and sample responses per topic",
        "Unclassified and outlier responses",
    ]
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(55, 70, 90)
    for j, item in enumerate(contents):
        pdf.set_xy(pdf.l_margin, contents_y + 9 + j * 8)
        pdf.cell(5, 6, "-")
        pdf.cell(pdf.cw - 5, 6, _s(item))

    pdf.set_text_color(*_BLACK)


def _overview_page(pdf: _PDF, analysis: dict):
    topics  = [t for t in analysis["topics"] if t["topic_id"] != -1]
    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)
    total   = analysis["summary"]["total_responses"]

    pdf.section_banner(
        "TOPIC DISTRIBUTION OVERVIEW",
        f"{len(topics)} topics  ·  {total} total responses"
    )

    lw = pdf.cw * 0.36
    bw = pdf.cw * 0.42
    pw = pdf.cw * 0.11
    nw = pdf.cw * 0.11

    # Column headers
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*_MUTED)
    pdf.set_x(pdf.l_margin)
    pdf.cell(lw, 6.5, "TOPIC")
    pdf.cell(bw, 6.5, "DISTRIBUTION")
    pdf.cell(pw, 6.5, "PERCENT", align="R")
    pdf.cell(nw, 6.5, "RESPONSES", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.h_rule()
    pdf.ln(1.5)

    for i, t in enumerate(topics):
        color  = _TOPIC_COLORS[i % len(_TOPIC_COLORS)]
        row_y  = pdf.get_y()
        label  = _s(t["label"], 42)

        # color dot
        pdf.set_fill_color(*color)
        pdf.rect(pdf.l_margin, row_y + 3.5, 4, 5, "F")

        # label
        pdf.set_x(pdf.l_margin + 7)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*_BLACK)
        pdf.cell(lw - 7, 12, label)

        # bar
        bar_x = pdf.l_margin + lw
        bar_filled = (bw - 5) * t["percentage"] / 100
        pdf.set_fill_color(*_BORDER)
        pdf.rect(bar_x, row_y + 4, bw - 5, 4, "F")
        if bar_filled > 0:
            pdf.set_fill_color(*color)
            pdf.rect(bar_x, row_y + 4, bar_filled, 4, "F")

        # pct
        pdf.set_x(bar_x + bw)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_GREEN)
        pdf.cell(pw, 12, f"{t['percentage']}%", align="R")

        # count
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(nw, 12, str(t["count"]), align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_draw_color(*_BORDER)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + pdf.cw, pdf.get_y())

    # outlier row (greyed out)
    if outlier:
        row_y = pdf.get_y()
        pdf.set_x(pdf.l_margin + 7)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(lw - 7, 12, "Unclassified / Other")
        bar_x = pdf.l_margin + lw
        bar_filled = (bw - 5) * outlier["percentage"] / 100
        pdf.set_fill_color(210, 210, 215)
        pdf.rect(bar_x, row_y + 4, bw - 5, 4, "F")
        if bar_filled > 0:
            pdf.set_fill_color(160, 160, 170)
            pdf.rect(bar_x, row_y + 4, bar_filled, 4, "F")
        pdf.set_x(bar_x + bw)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(pw, 12, f"{outlier['percentage']}%", align="R")
        pdf.cell(nw, 12, str(outlier["count"]), align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.h_rule()

    pdf.set_text_color(*_BLACK)
    pdf.ln(6)

    # Key-insight summary blurb
    if topics:
        biggest = max(topics, key=lambda t: t["count"])
        pdf.set_fill_color(*_LIGHT_BG)
        pdf.set_draw_color(*_BORDER)
        rect_y = pdf.get_y()
        pdf.rect(pdf.l_margin, rect_y, pdf.cw, 18, "FD")
        pdf.set_fill_color(*_GREEN)
        pdf.rect(pdf.l_margin, rect_y, 3, 18, "F")
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_DARK)
        pdf.set_xy(pdf.l_margin + 7, rect_y + 3)
        pdf.cell(0, 6, "KEY INSIGHT")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(50, 60, 80)
        pdf.set_xy(pdf.l_margin + 7, rect_y + 10)
        biggest_label = _s(biggest["label"], 50)
        pdf.cell(0, 5.5, (
            f'The largest topic - "{biggest_label}" - accounts for '
            f'{biggest["percentage"]}% of responses ({biggest["count"]} of '
            f'{analysis["summary"]["total_responses"]}).'
        ))
        pdf.set_text_color(*_BLACK)
        pdf.set_y(rect_y + 22)


def _draw_sample_quote(pdf: _PDF, text: str, color: tuple):
    """Draw a quote block with a coloured left accent bar.

    Strategy: render text twice.  First pass establishes the end-y so we know
    the block height; second pass is on top of the filled background rect.
    """
    txt = _s(text, 400)
    if not txt or txt == " ":
        return

    sy = pdf.get_y()
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(40, 55, 75)
    # First pass — just to measure height (text rendered but will be covered)
    pdf.set_xy(pdf.l_margin + 8, sy + 2.5)
    pdf.multi_cell(pdf.cw - 10, 5.2, f'"{txt}"')
    ey = pdf.get_y()
    block_h = max(ey - sy + 2, 12)

    # Background fill
    pdf.set_fill_color(*_LIGHT_BG)
    pdf.rect(pdf.l_margin + 3, sy, pdf.cw - 3, block_h, "F")
    # Accent bar
    pdf.set_fill_color(*color)
    pdf.rect(pdf.l_margin, sy, 3, block_h, "F")
    # Second pass — text on top of background
    pdf.set_text_color(40, 55, 75)
    pdf.set_xy(pdf.l_margin + 8, sy + 2.5)
    pdf.multi_cell(pdf.cw - 10, 5.2, f'"{txt}"')
    pdf.set_y(pdf.get_y() + 4)


def _topic_page(pdf: _PDF, topic: dict, index: int):
    color       = _TOPIC_COLORS[index % len(_TOPIC_COLORS)]
    label       = _s(topic["label"])
    description = _s(topic.get("description", ""))
    category    = _s(topic.get("category", ""))
    keywords    = topic.get("keywords", [])
    samples     = topic.get("sample_responses", [])

    # ── header bar ──
    y = pdf.get_y()
    pdf.set_fill_color(*color)
    pdf.rect(pdf.l_margin, y, pdf.cw, 15, "F")

    # number badge
    badge = 12
    bx, by = pdf.l_margin + 4, y + 1.5
    pdf.set_fill_color(*_WHITE)
    pdf.rect(bx, by, badge, badge, "F")
    r, g, b = color
    pdf.set_text_color(r, g, b)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(bx, by + 1.5)
    pdf.cell(badge, 9, str(index + 1), align="C")

    # label + stats in header
    stats_txt = f"{topic['count']} responses  ·  {topic['percentage']}%"
    pdf.set_font("Helvetica", "", 9)
    stats_w = pdf.get_string_width(stats_txt) + 4
    pdf.set_text_color(*_WHITE)
    pdf.set_xy(pdf.l_margin + badge + 8, y + 2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(pdf.cw - badge - 8 - stats_w, 11, label)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(stats_w, 11, stats_txt, align="R")
    pdf.set_text_color(*_BLACK)
    pdf.set_y(y + 17)

    # ── description ──
    if description:
        pdf.set_font("Helvetica", "I", 9.5)
        pdf.set_text_color(50, 60, 80)
        pdf.multi_cell(pdf.cw, 5.5, description)
        pdf.ln(4)
        pdf.set_text_color(*_BLACK)

    # ── category pill ──
    if category:
        cat_txt = f"  {category.upper()}  "
        pdf.set_font("Helvetica", "B", 7.5)
        cat_w = pdf.get_string_width(cat_txt) + 2
        py = pdf.get_y()
        pdf.set_fill_color(*color)
        pdf.rect(pdf.l_margin, py, cat_w, 7, "F")
        pdf.set_text_color(*_WHITE)
        pdf.set_xy(pdf.l_margin, py)
        pdf.cell(cat_w, 7, cat_txt)
        pdf.set_text_color(*_BLACK)
        pdf.ln(10)

    # ── keywords ──
    if keywords:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(0, 5.5, "KEY TERMS", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        tag_y = pdf.get_y()
        x_pos = pdf.l_margin
        for kw in keywords:
            kw_txt = f" {_s(kw)} "
            pdf.set_font("Helvetica", "", 8)
            kw_w = pdf.get_string_width(kw_txt) + 6
            if x_pos + kw_w > pdf.l_margin + pdf.cw:
                x_pos = pdf.l_margin
                tag_y += 10
            pdf.set_fill_color(240, 245, 255)
            pdf.set_draw_color(*color)
            pdf.rect(x_pos, tag_y, kw_w, 7.5, "FD")
            pdf.set_text_color(*_DARK)
            pdf.set_xy(x_pos, tag_y)
            pdf.cell(kw_w, 7.5, kw_txt)
            x_pos += kw_w + 3
        pdf.set_draw_color(*_BORDER)
        pdf.set_text_color(*_BLACK)
        pdf.set_y(tag_y + 11)

    # ── sample responses ──
    if samples:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*_MUTED)
        n = min(5, len(samples))
        pdf.cell(0, 5.5, f"SAMPLE RESPONSES  ({n} shown of {topic['count']} total)",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        for sample in samples[:5]:
            _draw_sample_quote(pdf, sample, color)
        pdf.set_text_color(*_BLACK)

    # bottom rule
    pdf.ln(3)
    pdf.set_draw_color(*color)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + pdf.cw, pdf.get_y())
    pdf.set_draw_color(*_BORDER)


def _outlier_page(pdf: _PDF, outlier: dict):
    pdf.section_banner(
        f"UNCLASSIFIED  ·  {outlier['count']} responses  ({outlier['percentage']}%)",
        "Responses that did not fit clearly into any identified topic cluster."
    )

    samples = outlier.get("sample_responses", [])
    if samples:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*_MUTED)
        n = min(5, len(samples))
        pdf.cell(0, 5.5, f"SAMPLE RESPONSES  ({n} shown)",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        for sample in samples[:5]:
            _draw_sample_quote(pdf, sample, (150, 150, 160))
        pdf.set_text_color(*_BLACK)

    # note
    pdf.ln(4)
    pdf.set_fill_color(*_LIGHT_BG)
    pdf.set_draw_color(*_BORDER)
    note_y = pdf.get_y()
    pdf.rect(pdf.l_margin, note_y, pdf.cw, 16, "FD")
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*_MUTED)
    pdf.set_xy(pdf.l_margin + 5, note_y + 4)
    pdf.multi_cell(pdf.cw - 10, 5.5, (
        "Unclassified responses typically include very short answers, non-responsive "
        "text, or niche viewpoints that form clusters too small to constitute a distinct topic."
    ))
    pdf.set_text_color(*_BLACK)


# ── Public entry point ───────────────────────────────────────────────────────

def generate_pdf(analysis: dict, filename: str = "") -> bytes:
    """Render a full multi-page PDF report and return raw bytes."""
    title = f"Survey Analysis - {filename}" if filename else "Survey Topic Analysis"
    pdf = _PDF(report_title=title)

    topics  = [t for t in analysis["topics"] if t["topic_id"] != -1]
    outlier = next((t for t in analysis["topics"] if t["topic_id"] == -1), None)

    # Page 1 — cover
    pdf.add_page()
    _cover_page(pdf, analysis)

    # Page 2 — overview / distribution
    pdf.add_page()
    _overview_page(pdf, analysis)

    # Page per topic
    for i, topic in enumerate(topics):
        pdf.add_page()
        _topic_page(pdf, topic, i)

    # Outlier page
    if outlier:
        pdf.add_page()
        _outlier_page(pdf, outlier)

    return bytes(pdf.output())
