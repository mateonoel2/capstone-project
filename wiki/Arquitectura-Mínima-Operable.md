# Arquitectura Mínima Operable

## Componentes

### Línea Base

| Componente | Descripción |
|------------|-------------|
| **Datos** | Imágenes de documentos (estados de cuenta bancarios) almacenadas en *Backblaze B2* |
| **Procesamiento** | *Backend* *FastAPI* con *parsers* configurables para extracción de información |
| **Modelo** | API de LLM (*Claude*, *OpenAI* u otros proveedores) para extracción estructurada de campos |
| ***Output*** | JSON estructurado con campos validados y metadatos de extracción |

---

## Infraestructura

### Servicios *Core*

- ***Deployment*:** *Railway* (PaaS)
- ***Backend*:** *FastAPI* (Python)
- **Base de Datos:** *PostgreSQL* (datos, metadatos y resultados de extracción)
- **Almacenamiento:** *Backblaze B2* (imágenes de documentos)
- **Procesamiento:** APIs de LLM (*Claude*, *OpenAI*, etc.) para extracción multimodal

### Arquitectura de Capas

```
┌─────────────────────────────────────────┐
│          Cliente (Web UI)               │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         API REST (FastAPI)              │
│  - Upload endpoint                      │
│  - Extraction endpoint                  │
│  - Results endpoint                     │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      Capa de Procesamiento              │
│  - Parser Registry                      │
│  - Schema Validation                    │
│  - LLM Orchestration                    │
└─────────────────────────────────────────┘
    ↓            ↓            ↓
┌────────┐  ┌──────────┐  ┌──────────────┐
│Postgre │  │Backblaze │  │  LLM APIs    │
│  SQL   │  │    B2    │  │  (Externas)  │
│        │  │          │  │  - Claude    │
│-Schemas│  │ -Images  │  │  - GPT-4     │
│-Results│  │ -Docs    │  │  - Gemini    │
│-Meta   │  │          │  │              │
└────────┘  └──────────┘  └──────────────┘
```

---

## Flujo de Datos

### 1. Carga de Documento
1. Usuario sube imagen vía interfaz web
2. *FastAPI* recibe el archivo y lo almacena temporalmente
3. Imagen se sube a *Backblaze B2*
4. Metadatos se registran en *PostgreSQL* (id, nombre de archivo, *timestamp*, estado)

### 2. Extracción de Información
1. Sistema recupera imagen de B2
2. Se selecciona *schema* de extracción (*bank_statement*)
3. *Parser* procesa imagen según configuración:
   - *Schema-driven*: campos dinámicos según *schema* YAML
   - API de LLM: envío de imagen + *prompt* estructurado
4. LLM retorna JSON estructurado

### 3. Validación y Almacenamiento
1. Validación de campos extraídos contra *schema*
2. Verificación de formatos (CLABE 18 dígitos, nombres válidos)
3. Almacenamiento de resultados en *PostgreSQL*
4. Generación de *confidence scores*

### 4. Revisión Humana
1. Interfaz muestra resultados extraídos
2. Usuario valida o corrige información
3. Confirmación final actualiza estado en BD

---

## Nivel de Automatización

**Semi-automatizado:** El sistema extrae automáticamente la información y el usuario valida los resultados a través de la interfaz web antes de confirmar.

**Proceso de validación:**
1. Sistema asigna *confidence score* a cada campo extraído
2. Campos con alta confianza (>90%) se marcan como "probables"
3. Campos con baja confianza (<70%) requieren revisión manual
4. Usuario revisa y confirma/corrige antes de almacenamiento final
