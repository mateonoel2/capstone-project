# Extracción de Estados de Cuenta Bancarios

Proyecto de *capstone* para la extracción automática de información de estados de cuenta bancarios mexicanos utilizando Claude Haiku 4.5.


https://github.com/user-attachments/assets/f1b3834b-239e-495c-95ac-458b0bf03d38


## Descripción

Sistema de producción (*FastAPI* + *Next.js*) que extrae información estructurada de estados de cuenta bancarios mexicanos en formato PDF. Utiliza 3 *parsers* basados en *Claude Haiku 4.5* (OCR, texto directo y visión) para extraer nombre del titular, cuenta CLABE y banco.

## Características

- Aplicación web con *FastAPI* (*backend*) y *Next.js* 15 (*frontend*)
- 3 estrategias de *parsing*: Claude OCR, Claude Text y Claude Vision
- *Dashboard* con métricas de precisión y correcciones por campo
- Preprocesamiento OCR (*pdf2image* + *pytesseract*) y validación de archivos
- Almacenamiento en PostgreSQL con migraciones Alembic
- Subida de PDFs a S3 (Tigris en producción, LocalStack en desarrollo)
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
│   │   │   ├── constants.py           # Constantes del dominio
│   │   │   ├── banks.py              # Diccionario de 91 bancos mexicanos
│   │   │   ├── validators.py         # Validación de CLABE y bancos
│   │   │   ├── parser_interface.py   # BaseParser ABC
│   │   │   ├── entities.py           # SubmissionData, MetricsData
│   │   │   └── services/             # ExtractionService, SubmissionService, MetricsService
│   │   ├── infrastructure/            # Integraciones externas
│   │   │   ├── api/extraction/       # Rutas HTTP y DTOs
│   │   │   ├── database.py           # SQLAlchemy + PostgreSQL
│   │   │   ├── models.py             # ORM (ExtractionLog)
│   │   │   ├── repository.py         # Acceso a datos
│   │   │   ├── parsers/              # claude_ocr, claude_text, claude_vision
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
│   ├── app/                           # Páginas (/, /dashboard)
│   ├── components/                    # Componentes React + shadcn/ui
│   └── lib/                           # API client, Zustand store, utils
│
├── docker-compose.yml                 # Backend + PostgreSQL + LocalStack
└── localstack/                        # Config de LocalStack (S3)
```

## Requisitos

- Python >= 3.12
- Node.js >= 18
- Docker y Docker Compose (para desarrollo local)
- Tesseract OCR (`brew install tesseract` en macOS)

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
| `AWS_S3_BUCKET_NAME` | Nombre del bucket S3 (backend) |
| `NEXT_PUBLIC_API_URL` | URL del backend, default `http://localhost:8000` (frontend) |

## Licencia

Ver el archivo [LICENSE](LICENSE) para más detalles.
