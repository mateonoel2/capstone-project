# Wiki del Proyecto - Extracción de Datos de Documentos

Bienvenido a la *wiki* del proyecto de extracción automática de información estructurada de documentos.

---

## Inicio Rápido

### Para empezar con el proyecto:
1. **Configuración inicial**: Lee el [README](https://github.com/mateonoel2/capstone-project) del repositorio principal
2. **Entender la arquitectura**: Consulta [Diseño de Solución](Diseño-de-Solución)

### Para trabajar con el *backend*:
3. **Ejecutar *scripts***: Sigue la [Guía de *Scripts*](Guía-de-Scripts)
4. **Ver resultados de *parsers***: Consulta [Comparación de *Parsers*](Comparación-de-Parsers)
5. **Metodologia de evaluacion**: Revisa [Evaluación y Métricas](Evaluación-y-Métricas)
6. **Actualizar datos**: Revisa el [*Workflow* Semanal](Workflow-Semanal)

### Para trabajar con el *frontend*:
6. **Configuración**: Sigue la [Configuración del *Frontend*](Configuración-Frontend)
7. **Entender la implementación**: Lee el [Resumen de Implementación](Resumen-Implementación)
8. **Ver métricas**: Consulta la documentación del [*Dashboard*](Dashboard)
9. **Últimas mejoras**: Revisa las [Últimas Actualizaciones](Últimas-Actualizaciones)

---

## Tecnologías Utilizadas

### *Backend*
- **Lenguaje**: Python 3.12+
- ***Framework* API**: *FastAPI*
- **Base de Datos**: *PostgreSQL* con *SQLAlchemy* y migraciones *Alembic*
- **Extraccion**: Extractores configurables con *schemas*, *prompts* y modelos personalizados. *DocumentExtractor* multi-proveedor (Anthropic, OpenAI, Google Gemini)
- **Gestion de dependencias**: *uv*

### *Frontend*
- ***Framework***: *Next.js* 15 con *App Router*
- **Lenguaje**: *TypeScript*
- **Estilos**: *Tailwind CSS*
- **Componentes**: *shadcn/ui* (*Radix UI*)
- **Visor de archivos**: *react-zoom-pan-pinch*
- **Estado del servidor**: *React Query* (*@tanstack/react-query*)
- **Iconos**: *Lucide React*

### *DevOps* y Herramientas
- **Control de versiones**: *Git* + *GitHub*
- **Gestión de dependencias**: *uv* (Python), *npm* (*Node.js*)
- ***Linting***: *Ruff* (Python), *ESLint* (*Next.js*)
- **Pruebas**: *pytest*
- **CI**: *GitHub Actions* (ruff format, lint, tests)
- **Despliegue**: *Railway* (*backend*), *Vercel* (*frontend*)
- **Contenedores**: *Docker Compose* (*backend* + *PostgreSQL* + *LocalStack*)

---

## Estructura del Proyecto

```
capstone-project/
├── backend/                        # Código del backend
│   ├── src/
│   │   ├── main.py                 # Entry point (FastAPI)
│   │   ├── domain/                 # Lógica de negocio pura
│   │   │   ├── schemas.py          # BankAccount (Pydantic)
│   │   │   ├── constants.py        # Constantes y diccionario de bancos
│   │   │   ├── validators.py       # Validacion CLABE/bancos
│   │   │   ├── extractor_interface.py # BaseExtractor ABC
│   │   │   ├── entities.py         # Entidades de dominio y API calls
│   │   │   └── services/           # Servicios de negocio (incl. QuotaService)
│   │   ├── infrastructure/         # Integraciones externas
│   │   │   ├── api/auth/           # Rutas de autenticación (/auth)
│   │   │   ├── api/admin/          # Rutas de administración (/admin/users)
│   │   │   ├── api/extraction/     # Rutas HTTP y DTOs (/extraction)
│   │   │   ├── api/extractors/     # Rutas HTTP (/extractors CRUD, AI, test)
│   │   │   ├── api/tokens/        # Rutas HTTP (/tokens CRUD)
│   │   │   ├── auth.py             # JWT y validación de tokens GitHub
│   │   │   ├── ai_assist.py        # Generacion de schemas/prompts con Claude
│   │   │   ├── database.py         # Configuracion PostgreSQL
│   │   │   ├── models.py           # ORM (User, ExtractionLog, ApiCallLog, etc.)
│   │   │   ├── repository.py       # Acceso a datos
│   │   │   ├── storage.py          # StorageBackend (S3 / local)
│   │   │   ├── extractors/        # DocumentExtractor (vision unificado)
│   │   │   ├── preprocessing/      # Validacion y descarga
│   │   │   ├── evaluation/         # Experimentos y metricas
│   │   │   └── data_pipeline/      # Scripts de datos
│   │   ├── core/                   # Utilidades genericas
│   │   └── tests/                  # Tests unitarios
│   ├── alembic/                    # Migraciones de base de datos
│   ├── scripts/                    # Scripts ejecutables
│   └── data/                       # Datos de prueba
│
└── frontend/                       # Aplicacion Next.js
    ├── app/                        # Pages (Next.js 15 App Router)
    │   ├── login/                  # Página de login (GitHub OAuth)
    │   ├── page.tsx                # Extraccion
    │   ├── extractors/             # Gestion de extractores (CRUD + wizard)
    │   ├── dashboard/              # Dashboard
    │   ├── admin/users/            # Gestion de usuarios (admin)
    │   ├── settings/tokens/       # Gestion de tokens API
    │   └── layout.tsx              # Layout con sidebar
    ├── auth.ts                     # Configuración NextAuth.js (GitHub OAuth)
    ├── middleware.ts               # Protección de rutas
    ├── components/                 # Componentes React + shadcn/ui
    │   ├── auth-provider.tsx       # Proveedor de autenticación
    │   ├── assistant/              # Sidebar de asistente IA
    │   ├── extractor-wizard/       # Wizard multi-paso para extractores
    │   ├── schema-builder/         # Editor visual de schemas JSON
    │   ├── file-viewer.tsx         # Visor de PDF e imagenes
    │   └── ui/                     # Componentes base
    └── lib/                        # API client, React Query hooks, Zustand store
```

---

## Documentación por Tema

### Arquitectura y Diseño
- [Diseño de Solución](Diseño-de-Solución) - Arquitectura completa del producto de datos
- [Arquitectura Mínima Operable](Arquitectura-Mínima-Operable) - Componentes e infraestructura mínima

### Planificación y Evolución
- [Autodiagnóstico Prototipo-MVP](Autodiagnóstico-Prototipo-MVP) - Evaluación del estado actual del prototipo
- [Recomendaciones de Generalización](Recomendaciones-de-Generalización) - Hoja de ruta para evolucionar el proyecto

### *Backend*
- [Guía de *Scripts*](Guía-de-Scripts) - Cómo usar los *scripts* del proyecto
- [Comparación de *Parsers*](Comparación-de-Parsers) - Análisis comparativo de estrategias de extraccion
- [Evaluación y Métricas](Evaluación-y-Métricas) - Metodologia de evaluacion y resultados detallados
- [*Workflow* Semanal](Workflow-Semanal) - Proceso de actualización de datos

### Operacion
- [Análisis de Costos](Análisis-de-Costos) - Desglose de costos por solicitud
- [Privacidad y Cumplimiento](Privacidad-y-Cumplimiento) - Marco legal, cifrado y proteccion de datos

### *Frontend*
- [Configuración del *Frontend*](Configuración-Frontend) - *Setup* completo
- [Resumen de Implementación](Resumen-Implementación) - Detalles técnicos
- [*Dashboard*](Dashboard) - Métricas y análisis
- [Últimas Actualizaciones](Últimas-Actualizaciones) - Estado actual del proyecto

---

## Resultados de Evaluacion

El enfoque de PDF directo a *Claude Haiku 4.5* alcanzo una precision promedio del **93.4%** sobre 176 estados de cuenta bancarios de 11 instituciones mexicanas:

| Campo | Precision | Correctos |
|-------|-----------|-----------|
| Titular | 92.8% | 167/175 |
| CLABE | 90.9% | 160/176 |
| Banco | 96.6% | 84/85 |

Tiempo de procesamiento: mediana 1.9s. Costo: ~$0.011 USD/documento. Ver detalles en [Evaluacion y Metricas](Evaluación-y-Métricas).

---

## Estado del Proyecto

### Completamente Implementado

- Autenticacion con *GitHub OAuth* (*NextAuth.js*) y tokens *JWT* en el *backend*
- *Multi-tenancy* con tabla de usuarios, roles (*user*/*admin*/*guest*) y datos aislados por usuario
- Registro automatico como *guest* con cuotas de uso diarias (extracciones, extractores, *prompts* IA)
- Panel de administracion para gestion de usuarios (crear, editar rol, activar/desactivar, eliminar)
- Extractores configurables con *schemas*, *prompts* y modelos personalizados
- *Wizard* multi-paso para crear extractores con asistente de IA
- Generacion de *schemas* y *prompts* asistida por Claude (`ai_assist.py`)
- Extractor unificado (*DocumentExtractor*) basado en vision con *Claude Haiku 4.5*
- Soporte para PDFs e imagenes (JPG/PNG)
- Versionado de extractores con soporte para pruebas A/B
- Extracciones de prueba con registro detallado (*TestExtractionLog*)
- Subida de archivos con *presigned URLs* (subida directa a S3, *fallback* via *backend*)
- Tokens API para acceso programatico con autenticacion *Bearer*
- Documentacion de API filtrada para clientes en `/api/docs`
- API REST con *endpoints* de extraccion, submission, extractores (CRUD), tokens, logs, metricas
- *Frontend* con extraccion, gestion de extractores, tokens API, visor de archivos y *dashboard*
- *React Query* para estado del servidor, *Zustand* para estado de UI
- Base de datos *PostgreSQL* con migraciones *Alembic*
- Seguimiento de llamadas a la API (*ApiCallLog*)
- Sistema de metricas de precision y metricas de API
- Visor de archivos con *react-zoom-pan-pinch*
- CI con *GitHub Actions*, despliegue en *Railway* + *Vercel*

---

## Enlaces Útiles

- [Repositorio Principal](https://github.com/mateonoel2/capstone-project)
- [*Issues*](https://github.com/mateonoel2/capstone-project/issues)
- [*Pull Requests*](https://github.com/mateonoel2/capstone-project/pulls)
- [Documentacion API (completa)](http://localhost:8000/docs) (cuando el *backend* esta ejecutandose)
- [Documentacion API (clientes)](http://localhost:8000/api/docs) (vista filtrada para integracion programatica)

---

## Inicio Rápido de Desarrollo

### 1. Clonar el repositorio

```bash
git clone https://github.com/mateonoel2/capstone-project.git
cd capstone-project
```

### 2. Configurar *backend*

```bash
cd backend
uv sync                # Instalar dependencias
cp .env.example .env   # Configurar API keys
uvicorn src.main:app --reload
```

### 3. Configurar *frontend*

```bash
cd frontend
npm install
npm run dev
```

### 4. Acceder a la aplicación

- *Frontend*: http://localhost:3000
- API: http://localhost:8000
- Documentacion API (completa): http://localhost:8000/docs
- Documentacion API (clientes): http://localhost:8000/api/docs

---

**Nota**: Todos los documentos están en español con términos técnicos en inglés en cursiva.
