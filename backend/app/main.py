"""FastAPI application for Oregon NLP Survey Analyzer."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from .config import settings
from .database import init_db
from .routers import analysis, library, export  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB and load embedding model (reused across analyses)
    init_db()
    app.state.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    yield


app = FastAPI(title="Oregon NLP Survey Analyzer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api")
app.include_router(library.router, prefix="/api")
app.include_router(export.router, prefix="/api")
