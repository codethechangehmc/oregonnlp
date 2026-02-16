"""Library endpoints: list, save, and remove saved analyses."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_database
from ..schemas import LibraryItem, SaveRequest

router = APIRouter()


@router.get("/library", response_model=list[LibraryItem])
def list_library(db: sqlite3.Connection = Depends(get_database)):
    """Return all analyses saved to the library."""
    cursor = db.execute(
        "SELECT id, filename, title, created_at, total_responses, num_topics "
        "FROM analyses WHERE saved_to_library = TRUE ORDER BY created_at DESC"
    )
    return [dict(r) for r in cursor.fetchall()]


@router.post("/library/{analysis_id}", response_model=LibraryItem)
def save_to_library(
    analysis_id: str,
    body: SaveRequest | None = None,
    db: sqlite3.Connection = Depends(get_database),
):
    """Save an analysis to the library with an optional title."""
    title = body.title if body else None
    db.execute(
        "UPDATE analyses SET saved_to_library = TRUE, title = COALESCE(?, title) WHERE id = ?",
        (title, analysis_id),
    )
    db.commit()

    cursor = db.execute(
        "SELECT id, filename, title, created_at, total_responses, num_topics "
        "FROM analyses WHERE id = ?",
        (analysis_id,),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return dict(row)


@router.delete("/library/{analysis_id}")
def remove_from_library(analysis_id: str, db: sqlite3.Connection = Depends(get_database)):
    """Remove an analysis from the library (does not delete the analysis)."""
    db.execute("UPDATE analyses SET saved_to_library = FALSE WHERE id = ?", (analysis_id,))
    db.commit()
    return {"ok": True}
