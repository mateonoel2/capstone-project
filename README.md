# Extracción de Datos de Documentos

Proyecto de *capstone* para la extracción automática de información estructurada de documentos utilizando Claude Haiku 4.5. Originalmente diseñado para estados de cuenta bancarios mexicanos, ahora soporta tipos de documentos arbitrarios con extractores configurables.


https://github.com/user-attachments/assets/24bcde60-1447-4f51-83c4-c7a791d7b3b1


## Descripción

Sistema de producción (*FastAPI* + *Next.js*) que extrae información estructurada de documentos (PDF e imagenes JPG/PNG). Los usuarios crean extractores personalizados con *schemas*, *prompts* y modelos configurables a traves de un *wizard* con asistencia de IA.

## Características

- Aplicacion web con *FastAPI* (*backend*) y *Next.js* 15 (*frontend*)
- Extractores configurables con *schemas*, *prompts* y modelos personalizados
- *Wizard* multi-paso para crear extractores (identidad, *schema*, *prompt*, prueba)
- Asistente de IA para generacion de *schemas* y *prompts* (alimentado por Claude)
- *Parser* unificado (*StatementExtractor*) basado en vision con *Claude Haiku 4.5*
- Soporte para PDFs e imagenes (JPG/PNG) con visor integrado (*react-zoom-pan-pinch*)
- Versionado de extractores con soporte para pruebas A/B
- Extracciones de prueba con registro detallado (*TestExtractionLog*)
- *Dashboard* con metricas de precision, correcciones por campo y metricas de llamadas API
- Seguimiento de llamadas a la API de Claude (tasa de error, tiempo de respuesta)
- *React Query* para gestion de estado del servidor, *Zustand* para estado de UI
- Almacenamiento en PostgreSQL con migraciones Alembic
- Subida de archivos a S3 con *presigned URLs* (subida directa desde el navegador, con *fallback* via *backend*)
- Despliegue en Railway (backend) y Vercel (frontend)
- CI con GitHub Actions (ruff format, lint, tests)
- Docker Compose para desarrollo local (backend + PostgreSQL + LocalStack)

## Estructura del Proyecto

```
capstone-project/
├── backend/
│   ├── src/
│   │   ├── main.py                     # Entry point (FastAPI)
│   │   ├── domain/                     # Lógica de negocio pura
│   │   │   ├── schemas.py             # BankAccount (Pydantic)
│   │   │   ├── constants.py           # Constantes y diccionario de bancos
│   │   │   ├── validators.py         # Validación de CLABE y bancos
│   │   │   ├── extractor_interface.py # BaseExtractor ABC
│   │   │   ├── entities.py           # Entidades de dominio y API calls
│   │   │   └── services/             # ExtractionService, SubmissionService, MetricsService, ExtractorConfigService
│   │   ├── infrastructure/            # Integraciones externas
│   │   │   ├── api/extraction/       # Rutas HTTP y DTOs (/extraction)
│   │   │   ├── api/extractors/       # Rutas HTTP (/extractors CRUD, AI, test)
│   │   │   ├── ai_assist.py          # Generacion de schemas/prompts con Claude
│   │   │   ├── database.py           # SQLAlchemy + PostgreSQL
│   │   │   ├── models.py             # ORM (ExtractionLog, ApiCallLog, TestExtractionLog)
│   │   │   ├── repository.py         # Acceso a datos
│   │   │   ├── storage.py            # StorageBackend (S3 / local)
│   │   │   ├── extractors/           # StatementExtractor (vision unificado)
│   │   │   ├── preprocessing/        # OCR, validación, limpieza, descarga
│   │   │   ├── evaluation/           # Experimentos y métricas
│   │   │   └── data_pipeline/        # Scripts de datos
│   │   ├── core/                      # Utilidades (logger, file_utils)
│   │   └── tests/                     # Pruebas unitarias
│   ├── alembic/                       # Migraciones de base de datos
│   ├── scripts/                       # Scripts ejecutables
│   └── data/                          # Datos de prueba
│
├── frontend/                          # Next.js 15 (App Router)
│   ├── app/                           # Páginas (/, /extractors, /dashboard)
│   ├── components/                    # Componentes React + shadcn/ui
│   │   ├── assistant/                # Sidebar de asistente IA
│   │   └── extractor-wizard/        # Wizard multi-paso para extractores
│   └── lib/                           # API client, React Query hooks, Zustand store
│
├── docker-compose.yml                 # Backend + PostgreSQL + LocalStack
└── localstack/                        # Config de LocalStack (S3)
```

## Requisitos

- Python >= 3.12
- Node.js >= 18
- Docker y Docker Compose (para desarrollo local)
- Poppler (`brew install poppler` en macOS, para conversion PDF a imagen)

## Instalación

1. Clonar el repositorio:

```bash
git clone <repository-url>
cd capstone-project
```

2. Backend:

```bash
cd backend
uv sync                # instalar dependencias
cp .env.example .env   # configurar ANTHROPIC_API_KEY
```

3. Frontend:

```bash
cd frontend
npm install
```

## Uso

### Con Docker Compose (recomendado)

```bash
docker compose up   # levanta backend + PostgreSQL + LocalStack
```

### Sin Docker

```bash
# Backend (requiere PostgreSQL corriendo)
cd backend
uvicorn src.main:app --reload  # http://localhost:8000

# Frontend
cd frontend
npm run dev  # http://localhost:3000
```

## Pruebas

```bash
cd backend
pytest                                   # todas las pruebas
pytest src/tests/test_file_validator.py  # prueba específica
```

## Linting

```bash
cd backend
ruff check .    # lint
ruff format .   # formato
```

## Variables de Entorno

| Variable | Descripción |
|---|---|
| `ANTHROPIC_API_KEY` | API key de Anthropic (backend) |
| `DATABASE_URL` | URL de PostgreSQL (backend) |
| `AWS_ENDPOINT_URL` | Endpoint S3 / LocalStack (backend) |
| `AWS_PUBLIC_ENDPOINT_URL` | Endpoint S3 accesible desde el navegador para *presigned URLs* (default: `AWS_ENDPOINT_URL`) |
| `AWS_S3_BUCKET_NAME` | Nombre del bucket S3 (backend) |
| `NEXT_PUBLIC_API_URL` | URL del backend, default `http://localhost:8000` (frontend) |

## Licencia

Ver el archivo [LICENSE](LICENSE) para más detalles.
