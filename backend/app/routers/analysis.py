"""Analysis endpoints: run pipeline and retrieve results."""

import json
import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from sentence_transformers import SentenceTransformer

from ..dependencies import get_embedding_model, get_database
from ..schemas import AnalysisResponse
from ..services.file_parser import parse_upload
from ..services.text_processing import preprocess_responses
from ..services.topic_analysis import analyze_topics
from ..services.llm_labeling import label_topics

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile, embedding_model: SentenceTransformer = Depends(get_embedding_model), db: sqlite3.Connection = Depends(get_database)):
    """Upload a file and run the full analysis pipeline."""
    try:
        content = await file.read()
        filename = file.filename or "upload"

        try:
            records = parse_upload(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not records:
            raise HTTPException(status_code=400, detail="No text data found in file")

        texts = [r["text"] for r in records]
        cleaned, stats = preprocess_responses(texts)

        if len(cleaned) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Only {len(cleaned)} valid responses after cleaning (need at least 5)",
            )

        try:
            results = analyze_topics(embedding_model, cleaned)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Topic analysis failed: {e}")

        try:
            label_topics(results["topics"], db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Topic labeling failed: {e}")

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

        db.execute(
            "INSERT INTO analyses (id, filename, total_responses, num_topics, results_json) VALUES (?, ?, ?, ?, ?)",
            (analysis_id, filename, stats["final_count"], results["num_topics"], json.dumps(response)),
        )
        db.commit()

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: sqlite3.Connection = Depends(get_database)):
    """Retrieve a previously run analysis by ID."""
    cursor = db.execute("SELECT results_json FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return json.loads(row[0])
