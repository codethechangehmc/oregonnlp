"""Oregon NLP Survey Analyzer — Streamlit app."""

import json
import sys
import uuid
from pathlib import Path

# Ensure backend/ is on sys.path so `app.*` imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.database import get_db, init_db
from app.services.file_parser import parse_upload
from app.services.text_processing import preprocess_responses
from app.services.topic_analysis import analyze_topics
from app.services.llm_labeling import label_topics
from app.services.pdf_generator import generate_pdf

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Oregon NLP Survey Analyzer",
    page_icon="🐟",
    layout="wide",
)


# ── Cached resources ─────────────────────────────────────────────────────────

@st.cache_resource
def load_model():
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    topic_model = BERTopic.load(
        settings.BERTOPIC_MODEL_PATH, embedding_model=embedding_model
    )
    return topic_model


@st.cache_resource
def setup_db():
    init_db()
    return True


# ── Helpers ──────────────────────────────────────────────────────────────────

def run_pipeline(content: bytes, filename: str) -> dict:
    """Full pipeline: parse → preprocess → analyze → label."""
    records = parse_upload(content, filename)
    if not records:
        raise ValueError("No text data found in file")

    texts = [r["text"] for r in records]
    cleaned, stats = preprocess_responses(texts)

    if len(cleaned) < 5:
        raise ValueError(f"Only {len(cleaned)} valid responses after cleaning (need at least 5)")

    topic_model = load_model()
    results = analyze_topics(topic_model, cleaned)

    db = get_db()
    try:
        label_topics(results["topics"], db)
    finally:
        db.close()

    label_map = {t["topic_id"]: t["label"] for t in results["topics"]}
    for a in results["assignments"]:
        a["topic_label"] = label_map.get(a["topic_id"], "")

    analysis_id = str(uuid.uuid4())
    response = {
        "analysis_id": analysis_id,
        "summary": {
            "total_responses": stats["final_count"],
            "num_topics": results["num_topics"],
        },
        "topics": results["topics"],
        "assignments": results["assignments"],
    }

    # Persist
    db = get_db()
    try:
        db.execute(
            "INSERT INTO analyses (id, filename, total_responses, num_topics, results_json) VALUES (?, ?, ?, ?, ?)",
            (analysis_id, filename, stats["final_count"], results["num_topics"], json.dumps(response)),
        )
        db.commit()
    finally:
        db.close()

    return response


def save_analysis(analysis_id: str, title: str | None = None):
    db = get_db()
    try:
        db.execute(
            "UPDATE analyses SET saved_to_library = TRUE, title = COALESCE(?, title) WHERE id = ?",
            (title, analysis_id),
        )
        db.commit()
    finally:
        db.close()


def load_library() -> list[dict]:
    db = get_db()
    try:
        cursor = db.execute(
            "SELECT id, filename, title, created_at, total_responses, num_topics "
            "FROM analyses WHERE saved_to_library = TRUE ORDER BY created_at DESC"
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        db.close()


def load_analysis(analysis_id: str) -> dict | None:
    db = get_db()
    try:
        cursor = db.execute("SELECT results_json FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
    finally:
        db.close()


# ── Initialize ───────────────────────────────────────────────────────────────

setup_db()

if "analysis" not in st.session_state:
    st.session_state.analysis = None

# ── Sidebar: Library ─────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Library")
    library = load_library()
    if not library:
        st.caption("No saved analyses yet")
    for item in library:
        label = item["title"] or item["filename"]
        if st.button(f"📄 {label}", key=f"lib-{item['id']}", use_container_width=True):
            data = load_analysis(item["id"])
            if data:
                st.session_state.analysis = data
                st.rerun()

# ── Main content ─────────────────────────────────────────────────────────────

st.title("Oregon NLP Survey Analyzer")
st.caption("Upload survey data to discover topics with AI-powered labeling")

# Upload
uploaded = st.file_uploader(
    "Upload a file",
    type=["csv", "xlsx", "xls", "json", "txt"],
    help="Supported formats: CSV, Excel, JSON, TXT",
)

if uploaded and st.button("Analyze", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing {uploaded.name}..."):
        try:
            result = run_pipeline(uploaded.getvalue(), uploaded.name)
            st.session_state.analysis = result
            st.rerun()
        except Exception as e:
            st.error(str(e))

# ── Results ──────────────────────────────────────────────────────────────────

data = st.session_state.analysis
if data:
    st.divider()

    # Summary metrics
    summary = data["summary"]
    topics = data["topics"]
    outlier = next((t for t in topics if t["topic_id"] == -1), None)
    outlier_count = outlier["count"] if outlier else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Responses", summary["total_responses"])
    c2.metric("Topics Found", summary["num_topics"])
    c3.metric("Classified", summary["total_responses"] - outlier_count)
    c4.metric("Outlier Rate", f"{outlier_count / max(summary['total_responses'], 1) * 100:.1f}%")

    # Action buttons
    col_pdf, col_save = st.columns(2)
    with col_pdf:
        pdf_bytes = generate_pdf(data)
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name="analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col_save:
        if st.button("Save to Library", use_container_width=True):
            save_analysis(data["analysis_id"])
            st.toast("Saved to library!")
            st.rerun()

    # Topic table
    st.subheader("Topics")
    sorted_topics = sorted(
        [t for t in topics if t["topic_id"] != -1],
        key=lambda t: t["count"],
        reverse=True,
    )

    for i, topic in enumerate(sorted_topics, 1):
        pct = topic["percentage"]
        with st.expander(
            f"**#{i} {topic['label']}** — {topic['count']} responses ({pct}%) · _{topic['category']}_"
        ):
            if topic["description"]:
                st.write(topic["description"])

            # Keywords as badges
            st.caption("Keywords")
            kw_text = " · ".join(f"`{kw}`" for kw in topic["keywords"] if kw)
            st.markdown(kw_text)

            # Sample responses
            if topic["sample_responses"]:
                st.caption("Sample responses")
                for resp in topic["sample_responses"][:5]:
                    st.markdown(f"- {resp}")

    # Outlier section
    if outlier and outlier["count"] > 0:
        with st.expander(f"**Unclassified** — {outlier['count']} responses ({outlier['percentage']}%)"):
            for resp in outlier.get("sample_responses", [])[:]:
                st.markdown(f"- {resp}")
