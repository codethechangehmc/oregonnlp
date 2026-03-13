# Architecture

Oregon NLP Survey Analyzer: upload survey data, run BERTopic topic modeling, label topics with GPT-4o-mini, explore results interactively, and export PDF reports.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| Frontend | Next.js 16 + React 19 + TypeScript |
| Topic Modeling | BERTopic + sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM Labeling | OpenAI `gpt-4o-mini` (with local fallback) |
| Database | SQLite |
| PDF Generation | fpdf2 |
| Styling | Tailwind CSS 4 + CSS custom properties |
| Alternative UI | Streamlit |

## Project Structure

```
oregonnlp/
├── backend/app/
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # SQLite schema & connection
│   ├── schemas.py           # Pydantic request/response models
│   ├── dependencies.py      # Dependency injection
│   ├── streamlit_app.py     # Standalone Streamlit UI
│   ├── routers/
│   │   ├── analysis.py      # /api/analyze, /api/analyses/{id}
│   │   ├── library.py       # /api/library CRUD
│   │   └── export.py        # /api/analyses/{id}/pdf
│   └── services/
│       ├── file_parser.py   # CSV/Excel/JSON/TXT parsing
│       ├── text_processing.py  # Text cleaning & filtering
│       ├── topic_analysis.py   # BERTopic pipeline
│       ├── llm_labeling.py     # GPT-4o-mini labeling + cache
│       └── pdf_generator.py    # Multi-page PDF report
├── frontend/src/
│   ├── app/
│   │   ├── layout.tsx       # Fonts (Newsreader + Outfit), metadata
│   │   ├── page.tsx         # Home — orchestrates all state & UI
│   │   └── globals.css      # Theme variables, animations
│   ├── hooks/
│   │   ├── useAnalysis.ts   # Analysis state machine
│   │   └── useLibrary.ts    # Library CRUD state
│   ├── lib/
│   │   ├── api.ts           # HTTP client functions
│   │   └── types.ts         # TypeScript interfaces
│   └── components/
│       ├── layout/          # Header, Sidebar, SidebarItem
│       ├── upload/          # DropZone, FilePreview
│       ├── analysis/        # AnalysisView, TopicCard, etc.
│       ├── states/          # EmptyState, AnalyzingState, ErrorState
│       └── ui/              # Button, Card, Badge, Skeleton
├── models/
│   └── fishing_survey_bertopic/  # Pre-trained ODFW fishing survey model
├── notebooks/               # BERTopic exploration notebooks
└── scripts/                 # save_model.py
```

## Data Flow

```
File Upload
    │
    ▼
parse_upload()          CSV / XLSX / XLS / JSON / TXT → list[{id, text}]
    │                   Auto-detects text column by avg string length
    ▼
preprocess_responses()  Clean text, remove empty/short (< 2 words),
    │                   filter "nan"/"none"/"n/a". Requires ≥ 5 valid responses.
    ▼
analyze_topics()        UMAP → HDBSCAN → CountVectorizer → KeyBERT + MMR
    │                   Max 8 topics, 1–4 n-grams, keyword deduplication
    ▼
label_topics()          GPT-4o-mini generates short_name + description + category
    │                   SHA-256 keyword-hash caching in SQLite
    ▼
Database                Store results_json in `analyses` table
    │
    ├──▶ Frontend       Interactive topic explorer
    └──▶ PDF Export     Multi-page report with cover, charts, topic cards
```

## Backend

### Entry Point — `main.py`

- **Lifespan**: loads `SentenceTransformer("all-MiniLM-L6-v2")` into `app.state.embedding_model`; calls `init_db()`
- **CORS**: allows `http://localhost:3000` (frontend dev server)
- **Routers**: all mounted under `/api` prefix

### Configuration — `config.py`

```python
class Settings(BaseSettings):
    BERTOPIC_MODEL_PATH: str = "../models/fishing_survey_bertopic"
    DATABASE_PATH: str = "./data/app.db"
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"      # or "local"
    LOCAL_LLM_MODEL: str = "flan-t5"
```

Loads from `backend/.env`.

### Database — `database.py`

Two SQLite tables:

**`analyses`** — stores analysis results

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | UUID |
| filename | TEXT NOT NULL | Original upload filename |
| title | TEXT | User-assigned title (optional) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| total_responses | INTEGER NOT NULL | |
| num_topics | INTEGER NOT NULL | |
| results_json | TEXT NOT NULL | Full AnalysisResponse as JSON |
| saved_to_library | BOOLEAN | DEFAULT FALSE |

**`llm_label_cache`** — caches LLM-generated topic labels

| Column | Type | Notes |
|--------|------|-------|
| keyword_hash | TEXT PK | SHA-256 of sorted keywords |
| short_name | TEXT NOT NULL | e.g. "Wild fish and salmon" |
| description | TEXT NOT NULL | One-sentence description |
| category | TEXT NOT NULL | Broad category |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### Schemas — `schemas.py`

```python
TopicResult     # topic_id, label, description, category, count, percentage, keywords[], sample_responses[]
Assignment      # id, text, topic_id, topic_label, probability
Summary         # total_responses, num_topics
AnalysisResponse  # analysis_id, summary, topics[], assignments[]
LibraryItem     # id, filename, title, created_at, total_responses, num_topics
SaveRequest     # title (optional)
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Upload file → run full pipeline → return results |
| `GET` | `/api/analyses/{id}` | Retrieve stored analysis by ID |
| `GET` | `/api/library` | List all saved analyses (ordered by created_at DESC) |
| `POST` | `/api/library/{id}` | Save analysis to library (with optional title) |
| `DELETE` | `/api/library/{id}` | Remove from library (soft delete — sets flag to FALSE) |
| `GET` | `/api/analyses/{id}/pdf` | Download PDF report (StreamingResponse) |

### Services

#### `file_parser.py`

`parse_upload(content: bytes, filename: str) -> list[dict]`

- Parses CSV, XLSX, XLS, JSON, TXT files
- `_detect_text_column(df)` selects the object-dtype column with the largest average string length
- TXT files: splits by newlines
- Returns `[{"id": 0, "text": "..."}, ...]`

#### `text_processing.py`

`preprocess_responses(texts: list[str], min_length: int = 2) -> tuple[list[str], dict]`

- `clean_text()`: strip, collapse whitespace
- Filters empty strings and special values (`"nan"`, `"none"`, `"n/a"`)
- Removes texts with fewer than `min_length` words
- Returns cleaned texts + stats dict (`original_count`, `after_empty_removal`, `empty_removed`, `short_removed`, `final_count`)

#### `topic_analysis.py`

`analyze_topics(embedding_model, docs) -> dict`

BERTopic pipeline configuration:

| Component | Setting |
|-----------|---------|
| UMAP | n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine' |
| HDBSCAN | min_cluster_size=dynamic (5–15 based on doc count), metric='euclidean', method='eom' |
| Vectorizer | english stop words, ngram_range=(1, 4), min_df=2 |
| Representation | KeyBERTInspired → MaximalMarginalRelevance(diversity=0.6) |
| Topic limit | Auto-merge similar, then reduce to max 8 |
| Keywords | Deduplicated (case, substring, stem), max 10 per topic |

`_dedupe_keywords()` removes case duplicates, substring overlaps, and same-stem words (first 4 chars). Returns max 10 keywords per topic.

Returns topics (with empty labels — filled by LLM), assignments with probabilities, and up to 5 sample responses per topic.

#### `llm_labeling.py`

`label_topics(topic_results, db) -> list[dict]`

- **Cache key**: `SHA-256(sorted keywords joined by comma)`
- **Cache check**: query `llm_label_cache` table before calling LLM
- **LLM call**: OpenAI `gpt-4o-mini`, temperature=0, JSON response format
- **Prompt**: asks for `short_name` (3–5 word phrase), `description` (one sentence), `category`
- **Fallback**: if no API key or LLM fails, uses first 3 keywords capitalized
- **Outlier handling**: topic_id == -1 gets label "Other / Unclassified"
- **Key normalization**: handles variant key names (`name`/`label`/`short_name`, `desc`/`description`, `cat`/`category`)

#### `pdf_generator.py`

`generate_pdf(analysis: dict, filename: str = "") -> bytes`

Multi-page PDF with fpdf2:

1. **Cover page** — green pinstripe, dark hero section, title, 3 stat columns (responses, topics, classification %), "What's Inside" list
2. **Overview page** — topic distribution table with colored dots and horizontal bar chart, key insight box
3. **Topic pages** (one per topic) — colored header bar with rank badge, description, category pill, keyword tags, up to 5 sample responses
4. **Outlier page** — unclassified response count/percentage, samples, explanatory note

Header/footer on pages 2+. 8 distinct topic colors (green, blue, purple, orange, teal, red, indigo, amber).

### Streamlit App — `streamlit_app.py`

Standalone alternative UI using the same service layer. Features file upload, analysis pipeline, expandable topic results, PDF download, and library save/load. Caches embedding model and database connection with `@st.cache_resource`.

## Frontend

### Next.js Configuration

API proxy in `next.config.ts`:

```typescript
rewrites: [{ source: "/api/:path*", destination: "http://localhost:8000/api/:path*" }]
```

All `/api/*` requests from the frontend are proxied to FastAPI on port 8000.

### Hooks

**`useAnalysis`** — state machine for the analysis workflow:
- States: `idle` → `analyzing` → `results` (or `error`)
- `analyze(file)`: uploads file, transitions through states
- `loadAnalysis(id)`: loads saved analysis from API
- `reset()`: returns to idle

**`useLibrary`** — CRUD for saved analyses:
- `items: LibraryItem[]`, `loading: boolean`
- `save(id, title?)`, `remove(id)`, `refresh()`

### API Client — `lib/api.ts`

| Function | Method | Endpoint |
|----------|--------|----------|
| `analyzeFile(file)` | POST | `/api/analyze` |
| `getAnalysis(id)` | GET | `/api/analyses/{id}` |
| `getLibrary()` | GET | `/api/library` |
| `saveToLibrary(id, title?)` | POST | `/api/library/{id}` |
| `removeFromLibrary(id)` | DELETE | `/api/library/{id}` |
| `getPdfUrl(id)` | — | Returns URL string |

Custom `ApiError` class with status code.

### TypeScript Interfaces — `lib/types.ts`

Mirrors backend Pydantic schemas: `TopicResult`, `Assignment`, `Summary`, `AnalysisResponse`, `LibraryItem`, `SaveRequest`.

### Component Tree

```
page.tsx (Home)
├── Header                    # Logo, mobile sidebar toggle
├── Sidebar                   # Fixed 260px, library items, delete
│   └── SidebarItem           # Per-item with active state
└── main
    ├── DropZone              # Drag-and-drop file upload (.csv/.xlsx/.xls/.json/.txt)
    ├── FilePreview           # File name/size, Clear + Analyze buttons
    ├── EmptyState            # Initial prompt
    ├── AnalyzingState        # Loading animation with steps
    ├── ErrorState            # Error message + retry button
    └── AnalysisView          # Results container
        ├── SummaryMetrics    # 4-column grid: Responses, Topics, Classified, Outlier Rate
        ├── TopicList         # Sorted by count
        │   └── TopicCard     # Expandable: description, keywords, samples
        │       ├── KeywordBadge → Badge
        │       └── SampleResponse
        ├── OutlierSection    # Expandable unclassified responses
        └── ActionBar         # Save to Library + Download PDF buttons
```

### UI Primitives

| Component | Variants / Props |
|-----------|-----------------|
| `Button` | `primary` / `secondary` / `ghost` |
| `Card` | `hover?`, `glow?` |
| `Badge` | Accent-colored keyword tag |
| `Skeleton` | Shimmer loading placeholder |

### Styling System

**Dark theme** with CSS custom properties in `globals.css`:

- **Base**: `#0D0D0F` (background), `#161618` (surface), `#222225` (elevated)
- **Text**: `#F5F0E8` (primary), `#9A9590` (secondary), `#6B6660` (muted)
- **Accent**: `#E2A336` (amber/gold), `#C98E2A` (hover), `#2D2214` (dim)
- **Semantic**: `#6B8F71` (sage green — success), `#D4634B` (warm red — error)
- **Border**: `#2A2A2E` (standard), `#3A3A40` (bright/hover)

**Fonts**:
- Display: **Newsreader** (serif) — headings, large numbers
- Body: **Outfit** (sans-serif) — UI text, descriptions

**Animations**:
- `fade-up`: opacity 0 + translateY(16px) → visible (0.5s)
- `fade-in`: opacity 0 → 1 (0.4s)
- `shimmer`: background-position sweep (2s infinite)
- `glow-pulse`: opacity 0.3 → 0.8 → 0.3 (2.5s infinite)
- `spin-slow`: rotation (3s infinite)
- Stagger delays: `.delay-1` through `.delay-5` (0.06s increments)

**Extras**: film grain overlay (SVG noise, opacity 0.03), custom scrollbar (6px, rounded), accent-colored text selection.

## Pre-trained Model

`models/fishing_survey_bertopic/` contains a saved BERTopic model trained on ODFW fishing survey data:
- `config.json`, `topics.json` — model configuration and discovered topics
- `ctfidf.safetensors`, `ctfidf_config.json` — class-based TF-IDF weights
- `topic_embeddings.safetensors` — topic embedding vectors

Used by the Streamlit app. The FastAPI app trains a new model per upload.

## Key Design Decisions

- **Max 8 topics**: BERTopic auto-discovers topics, then `reduce_topics()` merges down to 8 max to keep results digestible
- **Keyword deduplication**: removes case variants, substrings, and same-stem words (e.g. "fish"/"fishing", "hatchery"/"hatcheries") to avoid redundant keywords
- **LLM cache by keyword hash**: SHA-256 of sorted keywords prevents redundant API calls for identical topic keyword sets
- **No authentication**: designed as a single-user local application
- **Soft delete for library**: `DELETE /api/library/{id}` only flips the `saved_to_library` flag; analysis data is preserved
- **Next.js API rewrites**: frontend proxies `/api/*` to FastAPI on port 8000, avoiding CORS in production builds
- **Dual UI**: FastAPI + Next.js for the primary app; Streamlit for quick standalone use with the same service layer

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
yarn install
yarn dev  # http://localhost:3000

# Streamlit (alternative)
cd backend
streamlit run app/streamlit_app.py
```
