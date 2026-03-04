# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mexican bank statement extraction system. Uploads PDF bank statements and extracts structured fields (owner name, CLABE account number, bank name) using Claude Haiku 4.5. Two subsystems: a research/experimentation layer for comparing parser strategies, and a production FastAPI + Next.js application.

## Commands

### Backend (`cd backend`)
```bash
pip install -r requirements.txt          # install deps
uvicorn src.main:app --reload            # run API server (port 8000)
pytest                                   # run all tests
pytest src/tests/test_file_validator.py  # run single test file
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

### Backend (`backend/src/`)

Three layers under `src/`:

- **`src/main.py`** — FastAPI app entry point with CORS and lifespan

- **`src/domain/`** — Pure business logic (no external dependencies)
  - `schemas.py` — `BankAccount` Pydantic model
  - `constants.py` — `UNKNOWN_OWNER`, `UNKNOWN_ACCOUNT`, `CLABE_LENGTH`
  - `banks.py` — `BANK_DICT_KUSHKI` (91 Mexican banks)
  - `validators.py` — CLABE/bank regex patterns and validation
  - `parser_interface.py` — `BaseParser` ABC
  - `entities.py` — `SubmissionData`, `MetricsData` dataclasses
  - `services/` — `ExtractionService`, `SubmissionService`, `MetricsService`

- **`src/infrastructure/`** — External integrations
  - `api/extraction/routes.py` — HTTP routes under `/extraction`
  - `api/extraction/dtos.py` — Request/response Pydantic models
  - `database.py` — SQLAlchemy engine + session (SQLite at `data/extractions.db`)
  - `models.py` — `ExtractionLog` ORM model
  - `repository.py` — `ExtractionRepository` data access
  - `parsers/` — Parser implementations: `claude_ocr`, `claude_text`, `claude_vision`, `hybrid`, `regex`, `pdfplumber`, `llama`, `layoutlm`
  - `preprocessing/` — `OCRProcessor`, `DataCleaner`, `FileValidator`, `FileDownloader`
  - `evaluation/` — `ExperimentRunner` + validation metrics
  - `data_pipeline/` — Download/cleanup scripts

- **`src/core/`** — Generic utilities (`logger.py`, `file_utils.py`)

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

- Backend: Ruff (line-length 100, rules E/F/W/I)
- Frontend: ESLint with next/core-web-vitals
- All UI text and prompts are in Spanish
