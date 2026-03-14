# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mexican bank statement extraction system. Uploads PDF bank statements and extracts structured fields (owner name, CLABE account number, bank name) using Claude Haiku 4.5. Two subsystems: a research/experimentation layer for comparing extractor strategies, and a production FastAPI + Next.js application.

## Commands

### Backend (`cd backend`)
```bash
uv sync                                  # install deps
uvicorn src.main:app --reload            # run API server (port 8000)
pytest                                   # run all tests
pytest src/tests/test_file_validator.py  # run single test file
ruff check .                             # lint
ruff format .                            # format
```

### Docker (project root)
```bash
docker compose up                        # run full stack (backend + postgres + localstack)
docker compose build backend             # rebuild backend image
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
  - `schemas.py` — `BankAccount`, `ExtractionOutput` Pydantic models
  - `constants.py` — `UNKNOWN_OWNER`, `UNKNOWN_ACCOUNT`, `CLABE_LENGTH`, `BANK_DICT_KUSHKI`
  - `validators.py` — CLABE/bank regex patterns and validation
  - `extractor_interface.py` — `BaseExtractor` ABC
  - `entities.py` — `SubmissionData`, `MetricsData`, `ApiCallResult`, `ApiCallMetricsData`, `ExtractionError`, `ExtractorConfigData`
  - `services/` — `ExtractionService`, `SubmissionService`, `MetricsService`, `ApiMetricsService`, `ExtractorConfigService`

- **`src/infrastructure/`** — External integrations
  - `api/extraction/routes.py` — HTTP routes under `/extraction`
  - `api/extraction/dtos.py` — Request/response Pydantic models
  - `database.py` — SQLAlchemy engine + session (PostgreSQL via `DATABASE_URL`)
  - `models.py` — `ExtractorConfig`, `ExtractorConfigVersion`, `ExtractionLog`, `ApiCallLog` ORM models
  - `repository.py` — `ExtractionRepository`, `ExtractorConfigRepository`, `ApiCallRepository` data access
  - `storage.py` — `StorageBackend` ABC with `LocalStorage` and `S3Storage` (presigned upload URLs, download, CORS config)
  - `extractors/` — `StatementExtractor`: unified vision-based extractor (PDF + images)
  - `preprocessing/` — `OCRProcessor`, `DataCleaner`, `FileValidator`, `FileDownloader`
  - `evaluation/` — `ExperimentRunner` + validation metrics
  - `data_pipeline/` — Download/cleanup scripts

- **`src/core/`** — Generic utilities (`logger.py`, `file_utils.py`)

### Frontend (`frontend/`)

Next.js 15 App Router with TypeScript, Tailwind CSS, Radix UI (shadcn/ui), and Zustand for state.

- `/` — Main extraction workflow: upload file (PDF/JPG/PNG) → preview → editable extracted fields → submit
- `/dashboard` — Accuracy metrics and extraction history
- `lib/store.ts` — Zustand store (sessionStorage persistence)
- `lib/api.ts` — Typed fetch wrappers for backend endpoints

## Key Domain Concepts

- **CLABE**: 18-digit Mexican interbank account number (validated with `^\d{18}$`)
- **Upload flow**: Frontend requests presigned URL → direct S3 PUT (with backend fallback) → extract by S3 key
- **Extraction flow**: S3 key → download from storage → vision-based Claude extractor → structured output → user correction → persistence with correction flags
- **Accuracy metrics**: Calculated from per-field boolean correction flags stored in `ExtractionLog`

## Environment Variables

- `ANTHROPIC_API_KEY` — Required for Claude API calls (backend)
- `DATABASE_URL` — PostgreSQL connection string (backend)
- `AWS_ENDPOINT_URL` — S3/LocalStack endpoint (backend)
- `AWS_PUBLIC_ENDPOINT_URL` — Browser-reachable S3 endpoint for presigned URLs (defaults to `AWS_ENDPOINT_URL`)
- `AWS_S3_BUCKET_NAME` — S3 bucket for PDF uploads (backend)
- `NEXT_PUBLIC_API_URL` — Backend URL, defaults to `http://localhost:8000` (frontend)

## Code Style

- Backend: Ruff (line-length 100, rules E/F/W/I)
- Frontend: ESLint with next/core-web-vitals
- All UI text and prompts are in Spanish

## Verification

When finishing a big task, only run linter and tests — do NOT run `npm run build` or other build commands.
