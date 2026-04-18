# Oregon NLP Survey Analyzer — Overview

Upload survey responses, automatically discover topics with BERTopic, label them with GPT-4o-mini, and explore or export the results.

## How It Works

```
Upload file (.csv / .xlsx / .json / .txt)
       ↓
   Parse & clean text (remove empty, short, junk responses)
       ↓
   BERTopic topic modeling (UMAP → HDBSCAN → KeyBERT)
       ↓
   GPT-4o-mini labels each topic (cached to avoid repeat API calls)
       ↓
   Results stored in SQLite
       ↓
   Browse in the web app  ─or─  Download a PDF report
```

## Tech Stack

- **Backend**: FastAPI (Python) — `backend/app/`
- **Frontend**: Next.js 16 / React 19 / TypeScript — `frontend/src/`
- **Topic Modeling**: BERTopic with `all-MiniLM-L6-v2` embeddings
- **LLM**: OpenAI `gpt-4o-mini` (falls back to keyword-based labels if no API key)
- **Database**: SQLite (analyses + LLM label cache)
- **PDF**: fpdf2 multi-page reports
- **Alt UI**: Streamlit standalone app

## Backend at a Glance

**API Endpoints** (all under `/api`):

| Endpoint | What it does |
|----------|-------------|
| `POST /analyze` | Upload a file and run the full pipeline |
| `GET /analyses/{id}` | Fetch a stored analysis |
| `GET /library` | List saved analyses |
| `POST /library/{id}` | Save an analysis to the library |
| `DELETE /library/{id}` | Remove from library (keeps data) |
| `GET /analyses/{id}/pdf` | Download PDF report |

**Services** — the core logic lives in `backend/app/services/`:

| Service | Role |
|---------|------|
| `file_parser` | Reads CSV/Excel/JSON/TXT, auto-detects the text column |
| `text_processing` | Cleans text, filters empty/short responses (min 5 required) |
| `topic_analysis` | Runs BERTopic (max 8 topics, keyword deduplication) |
| `llm_labeling` | Calls GPT-4o-mini for topic names; caches by keyword hash |
| `pdf_generator` | Builds a styled multi-page PDF (cover, charts, topic cards) |

**Config**: copy `backend/.env.example` to `backend/.env` and add your `OPENAI_API_KEY`.

## Frontend at a Glance

Single-page app with a dark theme (amber/gold accent). The Next.js dev server proxies `/api/*` to FastAPI on port 8000.

**Key pieces**:
- `hooks/useAnalysis` — state machine: idle → analyzing → results / error
- `hooks/useLibrary` — CRUD for saved analyses
- `lib/api.ts` — thin HTTP client wrapping all endpoints
- `components/` — upload (DropZone, FilePreview), results (TopicCard, SummaryMetrics, OutlierSection), layout (Header, Sidebar), and shared UI primitives (Button, Card, Badge)

**Design**: Newsreader (serif) for display text, Outfit (sans-serif) for body. Subtle animations (fade-up, shimmer, glow-pulse) and a film-grain overlay.

## Quick Start

```bash
# Backend
cd backend
cp .env.example .env        # add your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
yarn install
yarn dev                     # http://localhost:3000
```

## Repo Layout

```
backend/app/
  main.py           App entry, CORS, startup (loads embedding model + DB)
  config.py         Env-based settings (model path, DB path, API key)
  database.py       SQLite schema — analyses table + llm_label_cache table
  schemas.py        Pydantic models shared across endpoints
  routers/          API route handlers
  services/         Business logic (parsing, modeling, labeling, PDF)
  streamlit_app.py  Standalone Streamlit alternative

frontend/src/
  app/              Next.js app router (layout, page, globals.css)
  hooks/            useAnalysis, useLibrary
  lib/              API client + TypeScript types
  components/       UI organized by feature (layout, upload, analysis, states, ui)

models/
  fishing_survey_bertopic/   Pre-trained BERTopic model for ODFW fishing surveys

notebooks/                   BERTopic exploration notebooks
scripts/                     Utility scripts (save_model.py)
```

For full technical details (database schema, BERTopic parameters, PDF structure, component props, CSS variables), see [ARCHITECTURE.md](./ARCHITECTURE.md).