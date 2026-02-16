"""Export endpoints: PDF download."""

import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io

from ..dependencies import get_database
from ..services.pdf_generator import generate_pdf

router = APIRouter()


@router.get("/analyses/{analysis_id}/pdf")
def download_pdf(analysis_id: str, db: sqlite3.Connection = Depends(get_database)):
    """Generate and stream a PDF report for the given analysis."""
    cursor = db.execute("SELECT results_json FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = json.loads(row[0])
    pdf_bytes = generate_pdf(analysis)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=analysis_{analysis_id[:8]}.pdf"},
    )
