# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Configurable document extraction system. Users create extractors with custom schemas, prompts, and models via a wizard with AI assistance (Claude-powered schema/prompt generation). Originally built for Mexican bank statements (owner name, CLABE, bank name), now supports arbitrary document types. Two subsystems: a research/experimentation layer for comparing extractor strategies, and a production FastAPI + Next.js application.

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
  - `entities.py` — `SubmissionData`, `MetricsData`, `ApiCallResult`, `ApiCallMetricsData`, `ExtractionError`, `ExtractorConfigData`, `UserData`
  - `services/` — `ExtractionService`, `SubmissionService`, `MetricsService`, `ApiMetricsService`, `ExtractorConfigService`

- **`src/infrastructure/`** — External integrations
  - `api/auth/routes.py` — Authentication routes (`/auth/login`, `/auth/me`)
  - `api/admin/routes.py` — Admin routes for user management (`/admin/users` CRUD)
  - `api/extraction/routes.py` — HTTP routes under `/extraction`
  - `api/extraction/dtos.py` — Request/response Pydantic models
  - `api/extractors/routes.py` — HTTP routes under `/extractors` (CRUD, versioning, AI generation, test extraction)
  - `auth.py` — JWT token creation/validation, `get_current_user`/`get_admin_user` dependencies, GitHub token validation
  - `ai_assist.py` — Claude-powered schema generation, prompt generation, and prompt refinement
  - `database.py` — SQLAlchemy engine + session (PostgreSQL via `DATABASE_URL`)
  - `models.py` — `User`, `ExtractorConfig`, `ExtractorConfigVersion`, `ExtractionLog`, `ApiCallLog`, `TestExtractionLog` ORM models
  - `repository.py` — `UserRepository`, `ExtractionRepository`, `ExtractorConfigRepository`, `ApiCallRepository`, `TestExtractionLogRepository`
  - `storage.py` — `StorageBackend` ABC with `LocalStorage` and `S3Storage` (presigned upload URLs, download, CORS config)
  - `extractors/` — `StatementExtractor`: unified vision-based extractor (PDF + images)
  - `preprocessing/` — `OCRProcessor`, `DataCleaner`, `FileValidator`, `FileDownloader`
  - `evaluation/` — `ExperimentRunner` + validation metrics
  - `data_pipeline/` — Download/cleanup scripts

- **`src/core/`** — Generic utilities (`logger.py`, `file_utils.py`)

### Frontend (`frontend/`)

Next.js 15 App Router with TypeScript, Tailwind CSS, Radix UI (shadcn/ui), React Query for server state, and Zustand for UI state.

- `/login` — GitHub OAuth login page
- `/` — Main extraction workflow: upload file (PDF/JPG/PNG) → preview → editable extracted fields → submit
- `/extractors` — Extractor config management (list, create, edit, delete)
- `/extractors/new` — Multi-step wizard to create extractor configs (identity, schema, prompt, test)
- `/extractors/[id]/edit` — Edit existing extractor config
- `/dashboard` — Accuracy metrics and extraction history
- `/admin/users` — User management (admin only): create, edit roles, activate/deactivate, delete
- `auth.ts` — NextAuth.js configuration (GitHub provider, JWT callbacks)
- `middleware.ts` — Route protection (redirects unauthenticated users to `/login`)
- `components/auth-provider.tsx` — `SessionProvider` + `BackendAuthSync` (exchanges GitHub token for backend JWT)
- `components/app-shell.tsx` — Conditional layout (hides sidebar on login page)
- `components/assistant/` — AI-powered sidebar for schema/prompt generation
- `components/extractor-wizard/` — Multi-step wizard components
- `lib/hooks.ts` — React Query hooks for server state (configs, versions, AI generation, extraction, users)
- `lib/query-provider.tsx` — React Query provider configuration
- `lib/store.ts` — Zustand store (sessionStorage persistence, UI state, backend auth token/user)
- `lib/api.ts` — Typed fetch wrappers for backend endpoints (includes JWT Authorization header)

## Key Domain Concepts

- **Authentication**: GitHub OAuth via NextAuth.js (frontend) + JWT tokens for backend API. Frontend exchanges GitHub access token for a backend JWT via `POST /auth/login`
- **Multi-tenancy**: `users` table with roles (`user`/`admin`). All data tables have `user_id` FK. Extractor configs scoped per user (unique name per user). Admin pre-registers users by GitHub username
- **Extractor config**: User-defined extraction configuration with name, model, prompt, and JSON output schema. Supports draft/active status and versioning for A/B testing
- **Upload flow**: Frontend requests presigned URL → direct S3 PUT (with backend fallback) → extract by S3 key
- **Extraction flow**: S3 key → download from storage → vision-based Claude extractor (using config's prompt + schema) → structured output → user correction → persistence with correction flags
- **AI assistant**: Claude-powered generation of JSON schemas from descriptions, extraction prompts from schemas, and prompt refinement (`ai_assist.py`)
- **Test extraction**: Test an extractor config against a sample file, logged in `test_extraction_logs` for debugging
- **CLABE**: 18-digit Mexican interbank account number (validated with `^\d{18}$`)
- **Accuracy metrics**: Calculated from per-field boolean correction flags stored in `ExtractionLog`

## Environment Variables

- `ANTHROPIC_API_KEY` — Required for Claude API calls (backend)
- `DATABASE_URL` — PostgreSQL connection string (backend)
- `JWT_SECRET` — Secret key for signing JWT tokens (backend, defaults to dev value)
- `AWS_ENDPOINT_URL` — S3/LocalStack endpoint (backend)
- `AWS_PUBLIC_ENDPOINT_URL` — Browser-reachable S3 endpoint for presigned URLs (defaults to `AWS_ENDPOINT_URL`)
- `AWS_S3_BUCKET_NAME` — S3 bucket for PDF uploads (backend)
- `NEXT_PUBLIC_API_URL` — Backend URL, defaults to `http://localhost:8000` (frontend)
- `AUTH_GITHUB_ID` — GitHub OAuth App client ID (frontend)
- `AUTH_GITHUB_SECRET` — GitHub OAuth App client secret (frontend)
- `AUTH_SECRET` / `NEXTAUTH_SECRET` — NextAuth.js secret for session encryption (frontend)

## Code Style

- Backend: Ruff (line-length 100, rules E/F/W/I)
- Frontend: ESLint with next/core-web-vitals
- All UI text and prompts are in Spanish

## Verification

When finishing a big task, only run linter and tests — do NOT run `npm run build` or other build commands.
