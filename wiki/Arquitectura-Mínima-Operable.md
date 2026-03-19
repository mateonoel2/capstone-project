# Arquitectura Mínima Operable

## Componentes

### Línea Base

| Componente | Descripción |
|------------|-------------|
| **Datos** | PDFs e imagenes de documentos almacenados en S3 (Tigris) |
| **Procesamiento** | *Backend* *FastAPI* con extractores configurables (*StatementExtractor* basado en vision) |
| **Modelo** | *Claude Haiku 4.5* (configurable) con *structured output* para extraccion de campos |
| ***Output*** | JSON estructurado con campos validados y metadatos de extracción |

---

## Infraestructura

### Servicios *Core*

- ***Deployment*:** *Railway* (PaaS)
- ***Backend*:** *FastAPI* (Python)
- **Base de Datos:** *PostgreSQL* (datos, metadatos y resultados de extracción)
- **Almacenamiento:** S3 / Tigris (documentos subidos), *LocalStack* en desarrollo
- **Procesamiento:** *Claude Haiku 4.5* via *LangChain* para extraccion por vision
- ***Frontend*:** *Next.js* 15 en *Vercel*

### Arquitectura de Capas

```
┌─────────────────────────────────────────┐
│          Cliente (Web UI)               │
│  - NextAuth.js (GitHub OAuth)           │
│  - Middleware de protección de rutas    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         API REST (FastAPI)              │
│  - POST /auth/login (GitHub → JWT/guest) │
│  - GET /admin/users (gestión)           │
│  - POST /extraction/upload-url          │
│  - POST /extraction/upload (fallback)   │
│  - POST /extraction/extract             │
│  - POST /extraction/submit              │
│  - GET/POST/DELETE /tokens (API tokens) │
│  - GET /extraction/metrics, logs, etc.  │
│  - GET /api/docs (client API docs)      │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      Capa de Procesamiento              │
│  - StatementExtractor (vision)          │
│  - Extractor Configs (schema + prompt)  │
│  - AI Assist (schema/prompt generation) │
│  - QuotaService (guest limits)          │
│  - API Call Tracking                    │
└─────────────────────────────────────────┘
    ↓            ↓            ↓
┌────────┐  ┌──────────┐  ┌──────────────┐
│Postgre │  │  S3 /    │  │ Claude       │
│  SQL   │  │  Tigris  │  │ Haiku 4.5    │
│        │  │          │  │              │
│-Users  │  │ -PDFs    │  │ -Vision API  │
│-Logs   │  │ -Images  │  │ -Structured  │
│-API    │  │          │  │  Output      │
│ Calls  │  │          │  │              │
│-AI Use │  │          │  │              │
└────────┘  └──────────┘  └──────────────┘
```

---

## Flujo de Datos

### 1. Carga de Documento
1. *Frontend* solicita *presigned URL* al *backend* (`POST /extraction/upload-url`)
2. *Frontend* sube el archivo directamente a S3 via *presigned PUT URL*
3. Si la subida directa falla, se usa *fallback* via *backend* (`POST /extraction/upload`)

### 2. Extraccion de Informacion
1. *Frontend* envia `s3_key` al *backend* (`POST /extraction/extract`)
2. *Backend* descarga el archivo de S3 y lo convierte a imagen(es) *base64*
2. Envia imagen + *prompt* a *Claude Haiku 4.5* via *LangChain*
3. *Structured output* (`ExtractionOutput`) retorna campos tipados
4. Se registra la llamada API en `api_call_logs` (tiempo, exito/error)

### 3. Validacion y Respuesta
1. Validacion de CLABE (18 digitos) y nombre de banco
2. Deteccion de documentos no validos (`is_valid_document: false`)
3. Respuesta al *frontend* con campos extraidos

### 4. Revision Humana y Persistencia
1. *Frontend* muestra resultados extraidos con campos editables
2. Usuario valida o corrige informacion
3. *Submit* registra en `extraction_logs` con *flags* de correccion por campo

---

## Nivel de Automatización

**Semi-automatizado:** El sistema extrae automáticamente la información y el usuario valida los resultados a través de la interfaz web antes de confirmar.

**Proceso de validacion:**
1. Sistema extrae campos automaticamente via *Claude* vision
2. Usuario revisa los campos extraidos en la interfaz web
3. Usuario corrige los campos que lo necesiten
4. Al enviar, se calculan *flags* de correccion por campo para metricas de precision
