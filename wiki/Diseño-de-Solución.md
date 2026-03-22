# Diseno de Solucion

**Ultima actualizacion:** Marzo 2026

**Objetivo:** describir como funciona el producto de datos, incluyendo la arquitectura de produccion y el flujo de desarrollo/experimentacion.

El producto automatiza la extraccion, estructuracion y validacion de informacion contenida en documentos (PDF e imagenes) para entornos *fintech*. Originalmente disenado para estados de cuenta bancarios mexicanos (titular, CLABE, banco), el sistema evoluciono hacia una arquitectura de **extractores configurables** donde cada tipo de documento se define mediante *schemas*, *prompts* y modelos, permitiendo adaptarse a distintos escenarios sin cambios en el codigo.

El enfoque ganador — envio directo del PDF al modelo de lenguaje sin preprocesamiento intermedio — alcanzo una precision promedio del **93.4%** sobre 176 documentos reales.

---

## 1. Arquitectura del Producto

### 1.1 Descripcion General

La arquitectura se divide en **dos flujos separados**: el flujo de produccion (lo que el usuario ve) y el flujo de desarrollo/experimentacion (mejora continua interna).

---

#### 1.1.1 Flujo de Produccion

```
Usuario sube documento (PDF/JPG/PNG)
    ↓
Frontend solicita presigned URL → subida directa a S3
    ↓
Frontend envia s3_key + extractor_config_id al backend
    ↓
Backend descarga documento de S3
    ↓
StatementExtractor envia PDF directo a Claude Haiku 4.5
  (sin OCR, sin conversion a imagen)
    ↓
Structured output: JSON con campos extraidos
    ↓
Validacion de formato (CLABE 18 digitos, banco normalizado)
    ↓
Frontend muestra resultados editables al usuario
    ↓
Usuario revisa, corrige si es necesario, y confirma
    ↓
Persistencia en PostgreSQL con flags de correccion por campo
    ↓
Dashboard actualiza metricas de precision
```

**Caracteristicas:**
- Un solo extractor activo por configuracion (sin comparacion entre *parsers*)
- PDF enviado directamente al modelo como documento binario
- Respuesta en ~2 segundos (mediana)
- Costo: ~$0.011 USD por documento
- Subida directa a S3 con *fallback* via *backend*

---

#### 1.1.2 Flujo de Desarrollo/Experimentacion

Este flujo **no es parte del producto**, sino el proceso interno para validar y mejorar el sistema:

```
1. Ingesta de datos
   - Dataset de cuentas bancarias con ground truth
   - Scripts: upload_bank_accounts.py, process_accounts.py
   ↓
2. Experimentacion
   - Script: run_experiment.py + StatementExtractor
   - Extraccion sobre dataset completo
   - Modos: completo, subconjunto, o reanalisis sin llamadas API
   ↓
3. Validacion contra ground truth
   - Comparacion campo por campo con validadores multinivel
   - Calculo de accuracy total, condicional, similaridad
   ↓
4. Generacion de metricas y visualizaciones
   - CSV detallado por documento
   - JSON con metricas agregadas
   - Graficos para analisis
```

**Nota historica:** en fases anteriores se evaluaron 9 *parsers* distintos (Regex, PDFPlumber, Claude OCR, Claude Vision, Claude Text, Hybrid, etc.). El enfoque de PDF directo supero a todos con 93.4% de precision promedio. Ver [Comparacion de Parsers](Comparación-de-Parsers) para el analisis completo.

---

### 1.2 Arquitectura en Capas

El *backend* sigue una arquitectura de tres capas:

```
┌─────────────────────────────────────────┐
│          Cliente (Next.js 15)           │
│  - NextAuth.js (GitHub OAuth)           │
│  - React Query + Zustand                │
│  - Middleware de proteccion de rutas    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         API REST (FastAPI)              │
│  - /auth (login, me, usage)             │
│  - /admin/users (gestion)               │
│  - /extraction (upload, extract, submit)│
│  - /extractors (CRUD, AI, test, A/B)    │
│  - /tokens (API tokens CRUD)            │
│  - /api/docs (client API docs)          │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        domain/ (logica pura)            │
│  - ExtractionService                    │
│  - SubmissionService                    │
│  - MetricsService                       │
│  - ExtractorConfigService               │
│  - QuotaService                         │
│  - Validators (CLABE, banco)            │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│     infrastructure/ (externo)           │
│  - StatementExtractor (Claude vision)   │
│  - AI Assist (schema/prompt generation) │
│  - Repository (SQLAlchemy)              │
│  - Storage (S3/Tigris)                  │
│  - Auth (JWT, GitHub OAuth, API tokens) │
└─────────────────────────────────────────┘
    ↓            ↓            ↓
┌────────┐  ┌──────────┐  ┌──────────────┐
│Postgre │  │  S3 /    │  │ Claude       │
│  SQL   │  │  Tigris  │  │ Haiku 4.5    │
│        │  │          │  │              │
│-Users  │  │ -PDFs    │  │ -PDF directo │
│-Logs   │  │ -Images  │  │ -Structured  │
│-API    │  │          │  │  Output      │
│ Calls  │  │          │  │              │
│-AI Use │  │          │  │              │
└────────┘  └──────────┘  └──────────────┘
```

---

## 2. Requisitos Funcionales y No Funcionales

### 2.1 Requisitos Funcionales

| Codigo | Requisito | Estado |
|--------|-----------|--------|
| RF1 | Aceptar documentos PDF e imagenes (JPG/PNG) para extraccion | Implementado |
| RF2 | Validar CLABE (18 digitos) y normalizar nombre de banco | Implementado |
| RF3 | Extraer campos definidos por el usuario via *schemas* configurables | Implementado |
| RF4 | Exponer API REST con *endpoints* HTTP que retornen JSON estructurado | Implementado |
| RF5 | Persistir resultados con *flags* de correccion por campo para metricas | Implementado |
| RF6 | Autenticacion con *GitHub OAuth* y tokens API para acceso programatico | Implementado |
| RF7 | Gestion de usuarios con roles (*user*/*admin*/*guest*) y cuotas diarias | Implementado |
| RF8 | Asistente de IA para generacion de *schemas* y *prompts* | Implementado |
| RF9 | Versionado de extractores con soporte para pruebas A/B | Implementado |

### 2.2 Requisitos No Funcionales

| Codigo | Requisito | Objetivo | Resultado |
|--------|-----------|----------|-----------|
| RNF1 | Precision del extractor en produccion | ≥85% promedio | **93.4%** |
| RNF2 | Latencia de respuesta | <10 segundos (p95) | **Mediana 1.9s** |
| RNF3 | Costo por documento | <$0.02 USD | **$0.011 USD** |
| RNF4 | Seguridad | Autenticacion + cifrado + RBAC | Implementado |
| RNF5 | Reproducibilidad | temperature=0, versionado de *prompts* | Implementado |

---

## 3. Separacion de Responsabilidades

| Aspecto | Flujo de Produccion | Flujo de Desarrollo |
|---------|-------------------|-------------------|
| **Usuario** | Cliente final | Equipo tecnico |
| **Input** | 1 documento individual | *Dataset batch* completo |
| **Validacion** | Formato (CLABE 18 digitos) | Contra *ground truth* |
| **Extractores** | 1 (configurado por usuario) | Multiples variantes |
| **Tiempo** | ~2 segundos | Minutos/horas |
| **Proposito** | Servicio al usuario | Mejora continua |

---

## 4. Stack Tecnologico

### *Backend*
- **Lenguaje:** Python 3.12+
- ***Framework*:** *FastAPI*
- **Base de datos:** *PostgreSQL* con *SQLAlchemy* y migraciones *Alembic*
- **Extraccion:** *Claude Haiku 4.5* via *LangChain* (*structured output*)
- **Almacenamiento:** S3/Tigris (compatible con *Railway Storage Buckets*)
- **Gestion de dependencias:** *uv*
- **Autenticacion:** *JWT* + *GitHub OAuth* + tokens API

### *Frontend*
- ***Framework*:** *Next.js* 15 con *App Router*
- **Lenguaje:** *TypeScript*
- **Estilos:** *Tailwind CSS* + *shadcn/ui* (*Radix UI*)
- **Estado:** *React Query* (servidor) + *Zustand* (UI)

### *DevOps*
- **CI:** *GitHub Actions* (ruff format, lint, tests)
- **Despliegue:** *Railway* (*backend*) + *Vercel* (*frontend*)
- **Contenedores:** *Docker Compose* (desarrollo local: *backend* + *PostgreSQL* + *LocalStack*)

### APIs Externas
- **Anthropic Claude:** API para extraccion de documentos y asistente de IA
