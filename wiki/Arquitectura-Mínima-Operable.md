# Arquitectura Mínima Operable

## Componentes

### Línea Base

| Componente | Descripción |
|------------|-------------|
| **Datos** | PDFs e imagenes de documentos (estados de cuenta bancarios) almacenados en S3 (Tigris) |
| **Procesamiento** | *Backend* *FastAPI* con *StatementParser* unificado basado en vision |
| **Modelo** | *Claude Haiku 4.5* con *structured output* para extraccion de campos |
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
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         API REST (FastAPI)              │
│  - POST /extraction/extract             │
│  - POST /extraction/submit              │
│  - GET /extraction/metrics, logs, etc.  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      Capa de Procesamiento              │
│  - StatementParser (vision)             │
│  - Schema Validation                    │
│  - API Call Tracking                    │
└─────────────────────────────────────────┘
    ↓            ↓            ↓
┌────────┐  ┌──────────┐  ┌──────────────┐
│Postgre │  │  S3 /    │  │ Claude       │
│  SQL   │  │  Tigris  │  │ Haiku 4.5    │
│        │  │          │  │              │
│-Logs   │  │ -PDFs    │  │ -Vision API  │
│-API    │  │ -Images  │  │ -Structured  │
│ Calls  │  │          │  │  Output      │
└────────┘  └──────────┘  └──────────────┘
```

---

## Flujo de Datos

### 1. Carga de Documento
1. Usuario sube PDF o imagen (JPG/PNG) via interfaz web
2. *FastAPI* recibe el archivo, lo guarda en S3 y crea archivo temporal

### 2. Extraccion de Informacion
1. `StatementParser` convierte el archivo a imagen(es) *base64*
2. Envia imagen + *prompt* a *Claude Haiku 4.5* via *LangChain*
3. *Structured output* (`ExtractionOutput`) retorna campos tipados
4. Se registra la llamada API en `api_call_logs` (tiempo, exito/error)

### 3. Validacion y Respuesta
1. Validacion de CLABE (18 digitos) y nombre de banco
2. Deteccion de documentos no bancarios (`is_bank_statement: false`)
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
