import sqlite3
from pathlib import Path

from .config import settings

DB_PATH = Path(settings.DATABASE_PATH)

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_responses INTEGER NOT NULL,
    num_topics INTEGER NOT NULL,
    results_json TEXT NOT NULL,
    saved_to_library BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS llm_label_cache (
    keyword_hash TEXT PRIMARY KEY,
    short_name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    try:
        db.executescript(SCHEMA)
        db.commit()
    finally:
        db.close()
