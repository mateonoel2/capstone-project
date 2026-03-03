# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mexican bank statement extraction system. Uploads PDF bank statements and extracts structured fields (owner name, CLABE account number, bank name) using Claude Haiku 4.5. Two subsystems: a research/experimentation layer for comparing parser strategies, and a production FastAPI + Next.js application.

## Commands

### Backend (`cd backend`)
```bash
pip install -r requirements.txt          # install deps
uvicorn application.main:app --reload    # run API server (port 8000)
pytest                                   # run all tests
pytest tests/test_file_validator.py      # run single test file
ruff check .                             # lint
ruff format .                            # format
```

### Frontend (`cd frontend`)
```bash
npm install                              # install deps
npm run dev                              # dev server
npm run build                            # production build
npm run lint                             # eslint
```

## Architecture

### Backend (`backend/`)

Two layers sharing the same codebase:

- **`application/`** — Production FastAPI API (clean architecture)
  - `main.py` — App entry point with CORS and lifespan
  - `api/extraction/routes.py` — HTTP routes under `/extraction`
  - `modules/extraction/service.py` — Business logic orchestrating parsing + persistence
  - `modules/extraction/repository.py` — SQLAlchemy data access (SQLite at `data/extractions.db`)
  - `modules/extraction/entities.py` — Domain classes (`ExtractionResult`, `SubmissionData`, `MetricsData`)
  - `modules/extraction/models.py` — ORM model (`ExtractionLog`)

- **`src/`** — Research/experimentation layer
  - `src/extraction/` — Parser implementations inheriting `BaseParser`: `ClaudeOCRParser`, `ClaudeParser`, `ClaudeVisionParser`, `LlamaParser`, `RegexParser`, `HybridParser`, `PdfplumberParser`, `LayoutLMParser`
  - `src/extraction/schemas.py` — `BankAccount` Pydantic model + `BANK_DICT_KUSHKI` (91 Mexican banks)
  - `src/preprocessing/` — `OCRProcessor`, `DataCleaner`, `FileValidator`, `FileDownloader`
  - `src/experiments/` — `ExperimentRunner` for batch parser comparison

The application layer uses `ClaudeOCRParser` from `src/extraction/` as its production parser.

### Frontend (`frontend/`)

Next.js 15 App Router with TypeScript, Tailwind CSS, Radix UI (shadcn/ui), and Zustand for state.

- `/` — Main extraction workflow: upload PDF → preview → editable extracted fields → submit
- `/dashboard` — Accuracy metrics and extraction history
- `lib/store.ts` — Zustand store (sessionStorage persistence)
- `lib/api.ts` — Typed fetch wrappers for backend endpoints

## Key Domain Concepts

- **CLABE**: 18-digit Mexican interbank account number (validated with `^\d{18}$`)
- **Extraction flow**: pdfplumber text extraction → fallback to OCR (pdf2image + pytesseract) → Claude prompt → JSON response → user correction → persistence with correction flags
- **Accuracy metrics**: Calculated from per-field boolean correction flags stored in `ExtractionLog`

## Environment Variables

- `ANTHROPIC_API_KEY` — Required for Claude API calls (backend)
- `NEXT_PUBLIC_API_URL` — Backend URL, defaults to `http://localhost:8000` (frontend)

## Code Style

- Backend: Ruff (line-length 100, rules E/F/W/I), mypy for type checking
- Frontend: ESLint with next/core-web-vitals
- All UI text and prompts are in Spanish
