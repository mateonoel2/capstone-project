# Extracción de Datos de Documentos

🔗 **[Ver aplicación en producción](https://capstone-project-sigma-one.vercel.app/)**

Proyecto de *capstone* para la extracción automática de información estructurada de documentos utilizando Claude Haiku 4.5. Originalmente diseñado para estados de cuenta bancarios mexicanos, ahora soporta tipos de documentos arbitrarios con extractores configurables.


https://github.com/user-attachments/assets/24bcde60-1447-4f51-83c4-c7a791d7b3b1


## Descripción

Sistema de producción (*FastAPI* + *Next.js*) que extrae información estructurada de documentos (PDF e imagenes JPG/PNG). Los usuarios crean extractores personalizados con *schemas*, *prompts* y modelos configurables a traves de un *wizard* con asistencia de IA.

## Características

- Aplicacion web con *FastAPI* (*backend*) y *Next.js* 15 (*frontend*)
- Autenticacion con *GitHub OAuth* (*NextAuth.js*) y tokens *JWT* en el *backend*
- *Multi-tenancy*: tabla de usuarios con roles (*user*/*admin*/*guest*), datos aislados por usuario
- Registro automatico como *guest* para usuarios nuevos de *GitHub*, con cuotas de uso diarias
- Panel de administracion para gestion de usuarios (crear, editar rol, activar/desactivar, eliminar)
- Extractores configurables con *schemas*, *prompts* y modelos personalizados
- *Wizard* multi-paso para crear extractores (identidad, *schema*, *prompt*, prueba)
- Asistente de IA para generacion de *schemas* y *prompts* (alimentado por Claude)
- Extractor multi-proveedor (*DocumentExtractor*) con arquitectura extensible para Anthropic, OpenAI y Google Gemini. Actualmente solo *Claude Haiku* esta disponible en produccion
- Soporte para PDFs e imagenes (JPG/PNG) con visor integrado (*react-zoom-pan-pinch*)
- Versionado de extractores con soporte para pruebas A/B
- Extracciones de prueba con registro detallado (*TestExtractionLog*)
- *Dashboard* con metricas de precision, correcciones por campo y metricas de llamadas API
- Seguimiento de llamadas a la API de Claude (tasa de error, tiempo de respuesta)
- *React Query* para gestion de estado del servidor, *Zustand* para estado de UI
- Almacenamiento en PostgreSQL con migraciones Alembic
- Subida de archivos a S3 con *presigned URLs* (subida directa desde el navegador, con *fallback* via *backend*)
- Tokens API para acceso programatico con autenticacion *Bearer*
- Documentacion de API para clientes en `/api/docs` (vista filtrada del *OpenAPI spec*)
- Despliegue en Railway (backend) y Vercel (frontend)
- CI con GitHub Actions (ruff format, lint, tests)
- Docker Compose para desarrollo local (backend + PostgreSQL + LocalStack)

## Resultados de Evaluacion

Evaluado sobre 176 estados de cuenta bancarios de 11 instituciones financieras mexicanas, utilizando el enfoque de PDF directo a *Claude Haiku 4.5* (sin OCR ni conversion intermedia):

| Campo | Precision | Correctos | Similaridad |
|-------|-----------|-----------|-------------|
| **Titular** | 92.8% | 163/175 | 0.93 |
| **CLABE** | 90.9% | 160/176 | 0.91 |
| **Banco** | 96.6% | 82/85 | 0.99 |

- **Tiempo de procesamiento:** mediana 1.9s, 85% en <4s
- **Costo:** ~$0.011 USD por documento
- **Promedio general:** 93.4% de precision

## Impacto Operativo

- Reduccion estimada del 60% en intervenciones de soporte (de ~18 a ~7 casos/mes)
- Ahorro anual: 315 horas-hombre (~1.8 FTE)
- Ahorro economico estimado: USD $6,480–$16,200 anuales por *fintech* (escala a USD $540k+ en operaciones de alto volumen)
- 80% de documentos procesados sin intervencion humana

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
│   │   │   └── services/             # ExtractionService, SubmissionService, MetricsService, ExtractorConfigService, QuotaService
│   │   ├── infrastructure/            # Integraciones externas
│   │   │   │   ├── api/auth/             # Rutas de autenticación (/auth)
│   │   │   ├── api/admin/            # Rutas de administración (/admin/users)
│   │   │   ├── api/extraction/       # Rutas HTTP y DTOs (/extraction)
│   │   │   ├── api/extractors/       # Rutas HTTP (/extractors CRUD, AI, test)
│   │   │   ├── api/tokens/          # Rutas HTTP (/tokens CRUD)
│   │   │   ├── auth.py                # JWT y validación de tokens GitHub
│   │   │   ├── ai_assist.py          # Generacion de schemas/prompts con Claude
│   │   │   ├── database.py           # SQLAlchemy + PostgreSQL
│   │   │   ├── models.py             # ORM (User, ExtractionLog, ApiCallLog, etc.)
│   │   │   ├── repository.py         # Acceso a datos
│   │   │   ├── storage.py            # StorageBackend (S3 / local)
│   │   │   ├── extractors/           # DocumentExtractor (multi-proveedor)
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
│   ├── app/                           # Páginas (/, /login, /extractors, /dashboard, /admin, /settings/tokens)
│   ├── auth.ts                        # Configuración NextAuth.js (GitHub OAuth)
│   ├── middleware.ts                  # Protección de rutas (redirige a /login)
│   ├── components/                    # Componentes React + shadcn/ui
│   │   ├── auth-provider.tsx         # Proveedor de autenticación (NextAuth + JWT backend)
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
| `ANTHROPIC_API_KEY` | API key de Anthropic (backend, proveedor por defecto) |
| `OPENAI_KEY` | API key de OpenAI (backend, opcional) |
| `GOOGLE_API_KEY` | API key de Google Gemini (backend, opcional) |
| `DATABASE_URL` | URL de PostgreSQL (backend) |
| `JWT_SECRET` | Clave secreta para firmar tokens JWT (backend) |
| `AWS_ENDPOINT_URL` | Endpoint S3 / LocalStack (backend) |
| `AWS_PUBLIC_ENDPOINT_URL` | Endpoint S3 accesible desde el navegador para *presigned URLs* (default: `AWS_ENDPOINT_URL`) |
| `AWS_S3_BUCKET_NAME` | Nombre del bucket S3 (backend) |
| `NEXT_PUBLIC_API_URL` | URL del backend, default `http://localhost:8000` (frontend) |
| `AUTH_GITHUB_ID` | Client ID de la GitHub OAuth App (frontend) |
| `AUTH_GITHUB_SECRET` | Client secret de la GitHub OAuth App (frontend) |
| `AUTH_SECRET` | Secreto de NextAuth.js para cifrado de sesiones (frontend) |

## Licencia

Ver el archivo [LICENSE](LICENSE) para más detalles.
