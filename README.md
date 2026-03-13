# Oregon NLP Survey Analyzer

An AI-powered tool for analyzing open-ended survey responses. Upload a file, automatically discover topics using BERTopic, label them with GPT-4o-mini, and explore or export the results as a PDF report.

Built by [Code the Change](https://github.com/codethechangehmc) at Harvey Mudd College.

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **OpenAI API key** (optional — the app falls back to keyword-based labels without one)

### 1. Clone the repo

```bash
git clone https://github.com/codethechangehmc/oregonnlp.git
cd oregonnlp
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Copy the example environment file and add your OpenAI API key (if you have one):

```bash
cp .env.example .env
```

Then edit `backend/.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

Start the API server:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend runs at **http://localhost:8000**.

### 3. Set up the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app runs at **http://localhost:3000**. The frontend proxies all `/api/*` requests to the backend automatically.

## How It Works

```
Upload file (.csv / .xlsx / .json / .txt)
       |
   Parse & clean text
       |
   BERTopic topic modeling (UMAP → HDBSCAN → KeyBERT)
       |
   GPT-4o-mini labels each topic with a name, description, and category
       |
   Results stored in SQLite
       |
   Browse in the web app  ─or─  Download a PDF report
```

1. **Upload** — Drop in a survey file. The app auto-detects which column contains the text responses.
2. **Preprocessing** — Cleans text, filters out empty and short responses (minimum 5 valid responses required).
3. **Topic Modeling** — BERTopic clusters responses into up to 8 topics using sentence embeddings, then deduplicates keywords to remove variants like "fish"/"fishing".
4. **LLM Labeling** — GPT-4o-mini generates a human-readable name and description for each topic. Results are cached by keyword hash so repeated topics don't cost extra API calls.
5. **Results** — View topic breakdowns, keyword badges, and sample responses in the web UI, or download a styled multi-page PDF report.
6. **Library** — Save analyses to revisit later.

## Supported File Formats

| Format | Extension |
|--------|-----------|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |
| JSON | `.json` |
| Plain text | `.txt` (one response per line) |

The parser auto-detects the text column in tabular files by finding the column with the longest average string length.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) |
| Frontend | [Next.js](https://nextjs.org/) 16 + React 19 + TypeScript |
| Topic Modeling | [BERTopic](https://maartengr.github.io/BERTopic/) + [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| LLM Labeling | OpenAI `gpt-4o-mini` |
| Database | SQLite |
| PDF Reports | [fpdf2](https://py-pdf.github.io/fpdf2/) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) 4 |

## Project Structure

```
oregonnlp/
├── backend/
│   ├── .env.example          # Environment variable template
│   ├── requirements.txt      # Python dependencies
│   └── app/
│       ├── main.py           # FastAPI app — CORS, startup, router registration
│       ├── config.py         # Settings loaded from .env
│       ├── database.py       # SQLite schema (analyses + LLM label cache)
│       ├── schemas.py        # Pydantic request/response models
│       ├── dependencies.py   # Dependency injection (embedding model, DB)
│       ├── streamlit_app.py  # Standalone Streamlit alternative UI
│       ├── routers/
│       │   ├── analysis.py   # Upload & analyze, fetch results
│       │   ├── library.py    # Save, list, remove analyses
│       │   └── export.py     # PDF download
│       └── services/
│           ├── file_parser.py      # Parse CSV/Excel/JSON/TXT
│           ├── text_processing.py  # Clean & filter text
│           ├── topic_analysis.py   # BERTopic pipeline
│           ├── llm_labeling.py     # GPT-4o-mini + keyword-hash caching
│           └── pdf_generator.py    # Multi-page PDF report
│
├── frontend/
│   └── src/
│       ├── app/              # Next.js app router (layout, page, global styles)
│       ├── hooks/            # useAnalysis (state machine), useLibrary (CRUD)
│       ├── lib/              # API client + TypeScript types
│       └── components/
│           ├── layout/       # Header, Sidebar
│           ├── upload/       # DropZone, FilePreview
│           ├── analysis/     # AnalysisView, TopicCard, SummaryMetrics, etc.
│           ├── states/       # EmptyState, AnalyzingState, ErrorState
│           └── ui/           # Button, Card, Badge, Skeleton
│
├── models/
│   └── fishing_survey_bertopic/   # Pre-trained model for ODFW fishing surveys
│
├── notebooks/                # BERTopic exploration notebooks
├── scripts/                  # Utility scripts
├── ARCHITECTURE.md           # Detailed technical documentation
└── OVERVIEW.md               # Concise project summary
```

## API Endpoints

All endpoints are under the `/api` prefix.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Upload a file and run the full analysis pipeline |
| `GET` | `/api/analyses/{id}` | Retrieve a stored analysis by ID |
| `GET` | `/api/library` | List all saved analyses |
| `POST` | `/api/library/{id}` | Save an analysis to the library (with optional title) |
| `DELETE` | `/api/library/{id}` | Remove an analysis from the library |
| `GET` | `/api/analyses/{id}/pdf` | Download a PDF report |

## Configuration

All configuration is managed through environment variables in `backend/.env`. See [`backend/.env.example`](backend/.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(empty)* | Your OpenAI API key for topic labeling |
| `LLM_PROVIDER` | `openai` | LLM provider (`openai` or `local`) |
| `LOCAL_LLM_MODEL` | `flan-t5` | Model name when using local provider |
| `DATABASE_PATH` | `./data/app.db` | SQLite database file path |
| `BERTOPIC_MODEL_PATH` | `../models/fishing_survey_bertopic` | Path to pre-trained BERTopic model |

Without an OpenAI API key, the app still works — topics will be labeled using their top keywords instead of LLM-generated names.

## Streamlit Alternative

A standalone Streamlit app is included for quick use without the full frontend:

```bash
cd backend
streamlit run app/streamlit_app.py
```

This uses the same backend services (parsing, modeling, labeling, PDF generation) with a simpler UI.

## Further Reading

- [ARCHITECTURE.md](ARCHITECTURE.md) — detailed technical docs (database schema, BERTopic parameters, PDF structure, component props, CSS system)
- [OVERVIEW.md](OVERVIEW.md) — concise project summary
