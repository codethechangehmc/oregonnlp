"""FastAPI dependencies for dependency injection."""

import sqlite3

from fastapi import Request
from sentence_transformers import SentenceTransformer

from .database import get_db


def get_embedding_model(request: Request) -> SentenceTransformer:
    """Retrieve the shared embedding model from app state."""
    return request.app.state.embedding_model


def get_database() -> sqlite3.Connection:
    """Yield a database connection, closing it after use."""
    db = get_db()
    try:
        yield db
    finally:
        db.close()
