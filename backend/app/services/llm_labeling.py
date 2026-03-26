"""GPT-4o mini topic labeling with SQLite cache."""

import hashlib
import json
import sqlite3

from openai import AzureOpenAI

from ..config import settings

_client: AzureOpenAI | None = None


def _get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        _client = AzureOpenAI(azure_endpoint = settings.AZURE_OPENAI_ENDPOINT, 
        api_key=settings.AZURE_OPENAI_API_KEY, api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT)
    return _client


def _hash_keywords(keywords: list[str]) -> str:
    return hashlib.sha256(",".join(sorted(keywords)).encode()).hexdigest()


def _check_cache(db: sqlite3.Connection, kw_hash: str) -> dict | None:
    cursor = db.execute(
        "SELECT short_name, description, category FROM llm_label_cache WHERE keyword_hash = ?",
        (kw_hash,),
    )
    row = cursor.fetchone()
    if row:
        return {"short_name": row[0], "description": row[1], "category": row[2]}
    return None


def _save_cache(db: sqlite3.Connection, kw_hash: str, label: dict):
    db.execute(
        "INSERT OR REPLACE INTO llm_label_cache (keyword_hash, short_name, description, category) VALUES (?, ?, ?, ?)",
        (kw_hash, label["short_name"], label["description"], label["category"]),
    )
    db.commit()


def _label_via_openai(keywords: list[str], samples: list[str]) -> dict:
    client = _get_client()
    prompt = (
        "You are labeling topics from survey responses. Produce one clear, coherent theme per topic.\n"
        f"Keywords: {', '.join(keywords)}\n"
        "Sample responses:\n" + "\n".join(f"- {s}" for s in samples[:5]) + "\n\n"
        "Return JSON with exactly these keys:\n"
        '- "short_name": one coherent phrase (3–5 words) that reads as a single theme, e.g. "Wild fish and salmon" or "Hatchery programs and ODFW", not a list of words\n'
        '- "description": one sentence describing what this topic is about\n'
        '- "category": broad category\n'
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=200,
    )
    data = json.loads(resp.choices[0].message.content)  # type: ignore[arg-type]
    # Normalize: GPT sometimes uses variant key names
    return {
        "short_name": data.get("short_name") or data.get("name") or data.get("label") or " ".join(keywords[:3]),
        "description": data.get("description") or data.get("desc") or "",
        "category": data.get("category") or data.get("cat") or "General",
    }


def label_topics(topic_results: list[dict], db: sqlite3.Connection) -> list[dict]:
    """Add LLM labels to each topic dict in-place and return them."""
    for topic in topic_results:
        if topic["topic_id"] == -1:
            topic["label"] = "Other / Unclassified"
            topic["description"] = "Responses that did not fit clearly into any topic."
            topic["category"] = "Other"
            continue

        keywords = topic["keywords"]
        kw_hash = _hash_keywords(keywords)

        cached = _check_cache(db, kw_hash)
        if cached:
            label_data = cached
        elif settings.LLM_PROVIDER == "azure_openai" and settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            try:
                label_data = _label_via_openai(keywords, topic["sample_responses"])
                _save_cache(db, kw_hash, label_data)
            except Exception:
                label_data = {
                    "short_name": " ".join(w.capitalize() for w in keywords[:3]),
                    "description": f"Topic about {', '.join(keywords[:5])}",
                    "category": "General",
                }
        else:
            label_data = {
                "short_name": " ".join(w.capitalize() for w in keywords[:3]),
                "description": f"Topic about {', '.join(keywords[:5])}",
                "category": "General",
            }

        topic["label"] = label_data["short_name"]
        topic["description"] = label_data["description"]
        topic["category"] = label_data["category"]

    return topic_results
