# CAPÍTULO: DISEÑO DE SOLUCIÓN DEL PRODUCTO DE DATOS

**Objetivo:** describir cómo funcionará el producto de datos (incluye alcance de ambos cursos)

El producto de datos se desarrollará para automatizar la extracción, estructuración y análisis de información contenida en estados de cuenta bancarios en formato PDF. Específicamente, el sistema extrae tres campos críticos de cada documento: **titular de la cuenta** (owner), **número CLABE de 18 dígitos** (account_number) y **nombre del banco** (bank_name).

La solución se construye bajo un enfoque modular que **implementa internamente tres arquitecturas de extracción complementarias** durante la fase de desarrollo: métodos determinísticos basados en expresiones regulares, modelos de lenguaje de última generación y enfoques híbridos. Esta diversidad permite evaluar múltiples estrategias, contrastar rendimiento y seleccionar el método más efectivo para desplegar en producción. **El producto final utiliza únicamente la arquitectura ganadora** (determinada mediante experimentación comparativa), garantizando la mayor precisión posible para el usuario final.

Desde la perspectiva del usuario final, el producto se presenta como un **API REST** para procesamiento bajo demanda y un **dashboard de métricas** que visualiza la precisión, tiempos de procesamiento y estadísticas de extracción. El usuario no interactúa directamente con los parsers internos ni elige entre arquitecturas, sino que consume resultados estandarizados a través de endpoints HTTP que automáticamente utilizan el parser de mejor desempeño.

---

## 1. Arquitectura del Producto de Datos

### 1.1 Descripción General de la Arquitectura

La arquitectura se divide en **dos flujos completamente separados**: el flujo de desarrollo/experimentación (continuous development) y el flujo del producto en producción.

---

#### 1.1.1 Flujo del Producto en Producción (Lo que el usuario ve)

El producto final es extremadamente simple desde la perspectiva del usuario:

```
Usuario envía PDF
    ↓
API REST recibe el documento
    ↓
PDF pasa por el parser óptimo (pre-seleccionado)
    ↓
Parser ejecuta preprocesamiento interno:
  - Extracción de texto (pdfplumber/pypdf) O
  - OCR con Tesseract O
  - Conversión a imagen (según el parser ganador)
    ↓
Extracción de 3 campos: owner, CLABE, banco
    ↓
API retorna JSON estructurado
    ↓
Dashboard registra métricas de la extracción
```

**Características del flujo de producción:**
- Sin validaciones previas de CLABE/RFC (el parser trabaja con cualquier PDF)
- Sin descarga de Airtable (el usuario envía el PDF directamente)
- Sin comparación entre parsers (usa únicamente el ganador)
- Respuesta inmediata (2-10 segundos según el parser)

---

#### 1.1.2 Flujo de Desarrollo/Experimentación (Continuous Development)

**Este flujo NO es parte del producto**, sino el proceso interno para **mejorar y validar** el sistema. Se ejecuta periódicamente para:

1. **Obtener datos actualizados** desde Airtable con nuevos estados de cuenta
2. **Validar que el parser actual sigue siendo óptimo** con documentos recientes
3. **Experimentar con nuevas arquitecturas** o mejoras a parsers existentes

**Pipeline de experimentación:**

```
1. Ingesta desde Airtable
   - Exportación manual: `bank accounts-Grid view.csv`
   - Script: upload_bank_accounts.py
   - Limpieza de datos (newlines, formatos)
   ↓
2. Validación y filtrado
   - Script: process_accounts.py
   - Validación CLABE (18 dígitos)
   - Validación RFC/CURP (patrones oficiales mexicanos)
   - Filtrado por existencia de PDF
   - Output: dataset limpio con ground truth
   ↓
3. Experimentación comparativa
   - Script: run_extraction.py + ExperimentRunner
   - Ejecución de los 9 parsers sobre mismo dataset
   - Registro de resultados y tiempos
   ↓
4. Validación contra ground truth
   - Script: validate_extraction.py
   - Comparación predicciones vs valores reales
   - Cálculo de métricas (accuracy por campo)
   - Identificación del parser ganador
   ↓
5. Decisión de despliegue
   - Si el parser actual sigue siendo óptimo → no cambios
   - Si hay un nuevo ganador → actualizar API en producción
```

**Características del flujo de desarrollo:**
- Se ejecuta offline (no impacta al usuario)
- Requiere ground truth (datos reales de Airtable)
- Proceso batch (puede tomar horas para dataset completo)
- Genera reportes comparativos entre arquitecturas

---

#### 1.1.3 Relación entre ambos flujos

El flujo de desarrollo **alimenta** al flujo de producción:

- **Desarrollo** identifica cuál parser usar → **Producción** lo implementa
- **Desarrollo** valida precisión con datos reales → **Producción** garantiza calidad
- **Desarrollo** permite continuous improvement → **Producción** evoluciona sin downtime

El usuario final **solo interactúa con el flujo de producción**, el flujo de desarrollo es transparente para él.

---

### 1.2 Diagramas de Pipeline

#### 1.2.1 Pipeline de Producción (Usuario Final)

```
┌──────────────────────────────────────────────────────┐
│                   USUARIO FINAL                       │
│               (Envía PDF → Recibe JSON)               │
└───────────────────────┬──────────────────────────────┘
                        │
                        │ HTTP POST /api/extract
                        ▼
            ┌──────────────────────┐
            │      API REST        │
            │   (FastAPI/Flask)    │
            └──────────┬───────────┘
                       │
                       │ Enruta a parser ganador
                       ▼
            ┌──────────────────────┐
            │  PARSER ÓPTIMO       │
            │ (ClaudeVisionParser) │◄─── Pre-seleccionado
            │                      │     en fase de desarrollo
            └──────────┬───────────┘
                       │
                       │ Preprocesamiento interno
                       │ (texto/OCR/imagen)
                       ▼
            ┌──────────────────────┐
            │   EXTRACCIÓN         │
            │ owner | CLABE | banco│
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │    JSON Response     │
            │  + Métricas logging  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   DASHBOARD          │
            │ (Métricas tiempo real)│
            └──────────────────────┘
```

**Características:**
- 1 parser activo (el ganador)
- Sin validación previa
- Respuesta en segundos
- Sin acceso a ground truth

---

#### 1.2.2 Pipeline de Desarrollo (Continuous Improvement)

```
┌──────────────────────────────────────────────────────┐
│              EQUIPO DE DESARROLLO                     │
│        (Exporta datos desde Airtable)                 │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
            ┌──────────────────────┐
            │   INGESTA & LIMPIEZA │
            │  upload_bank_accounts│
            │  + process_accounts  │
            └──────────┬───────────┘
                       │
                       │ Dataset limpio + ground truth
                       ▼
┌──────────────────────────────────────────────────────┐
│           EXPERIMENTACIÓN COMPARATIVA                 │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Arquitect1│  │Arquitect2│  │Arquitect3│          │
│  │Determinís│  │   LLM    │  │ Híbrida  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │             │             │                  │
│  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐             │
│  │ Regex   │  │ Claude  │  │ Hybrid  │             │
│  │PDFPlumb │  │ClaudeVis│  │LayoutLM │             │
│  └─────────┘  │ClaudeOCR│  └─────────┘             │
│               │Llama    │                           │
│               └─────────┘                           │
│                                                      │
│  Todos ejecutados en paralelo sobre mismo dataset   │
└──────────────────────┬───────────────────────────────┘
                       │
                       │ Resultados CSV + logs
                       ▼
            ┌──────────────────────┐
            │  VALIDACIÓN          │
            │  validate_extraction │
            │  vs ground truth     │
            └──────────┬───────────┘
                       │
                       │ Métricas de accuracy
                       ▼
            ┌──────────────────────┐
            │  IDENTIFICACIÓN      │
            │  PARSER GANADOR      │
            │  (mayor accuracy)    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  DECISIÓN DEPLOYMENT │
            │  ¿Actualizar prod?   │
            └──────────┬───────────┘
                       │
                       │ Si nuevo ganador > actual
                       ▼
            ┌──────────────────────┐
            │  ACTUALIZAR API      │
            │  (sin downtime)      │
            └──────────────────────┘
```

**Características:**
- 9 parsers ejecutados
- Validación completa (CLABE/RFC/CURP)
- Proceso batch (horas)
- Ground truth obligatorio
- Genera reportes comparativos

---

### 1.3 Flujos de Datos Detallados

#### 1.3.1 Flujo de Producción

Este es el flujo que experimenta el usuario al usar el producto:

```
1. Usuario
   - Envía PDF vía HTTP POST a /api/extract
   ↓
2. API REST
   - Recibe el documento
   - Enruta al parser ganador (ej: ClaudeVisionParser)
   ↓
3. Parser Óptimo
   - Preprocesa el PDF (texto/OCR/imagen según parser)
   - Extrae los 3 campos (owner, CLABE, banco)
   - Valida formato CLABE (18 dígitos)
   ↓
4. API REST
   - Retorna JSON estructurado al usuario
   - Registra métricas (tiempo, éxito/error)
   ↓
5. Dashboard
   - Actualiza métricas en tiempo real
   - Usuario visualiza precisión histórica
```

**Tiempo total:** 2-10 segundos  
**Input:** 1 PDF  
**Output:** 1 JSON con 3 campos

---

#### 1.3.2 Flujo de Desarrollo

Este es el flujo interno para mejorar el sistema, ejecutado periódicamente por el equipo de desarrollo:

```
1. Ingesta de datos actualizados
   - Exportar CSV desde Airtable
   - Script: upload_bank_accounts.py
   - Limpia datos y hace backup
   ↓
2. Descarga de PDFs (si aplica)
   - Script: download_statements.py
   - Descarga archivos binarios referenciados
   ↓
3. Validación y filtrado
   - Script: process_accounts.py
   - Valida CLABE (18 dígitos)
   - Valida RFC/CURP (patrones oficiales)
   - Filtra por existencia de PDF
   - Genera dataset limpio con ground truth
   ↓
4. Experimentación comparativa
   - Script: run_extraction.py + ExperimentRunner
   - Ejecuta los 9 parsers sobre mismo dataset
   - Guarda resultados en CSV con timestamp
   - Genera logs detallados
   ↓
5. Validación contra ground truth
   - Script: validate_extraction.py
   - Compara predicciones vs valores reales
   - Calcula accuracy por campo (Owner, CLABE, Bank)
   - Genera reporte comparativo
   - Identifica parser ganador
   ↓
6. Decisión de deployment
   - Si parser actual ≥ nuevo ganador → mantener producción
   - Si nuevo ganador > parser actual → actualizar API
   - Documentar cambios en logs
   ↓
7. Actualización en producción (solo si aplica)
   - Configurar API para usar nuevo parser
   - Deploy sin downtime
   - Monitoreo de métricas post-deployment
```

**Tiempo total:** Horas (para dataset completo)  
**Frecuencia:** Semanal/Mensual  
**Input:** Dataset completo de Airtable  
**Output:** Parser óptimo + reportes de precisión

---

#### 1.3.3 Separación de Responsabilidades

| Aspecto | Flujo de Producción | Flujo de Desarrollo |
|---------|-------------------|-------------------|
| **Usuario** | Cliente final | Equipo técnico |
| **Input** | 1 PDF individual | Dataset batch completo |
| **Validación** | Sin validación previa | Valida CLABE/RFC/CURP |
| **Ground truth** | No requerido | Necesario (Airtable) |
| **Parsers ejecutados** | 1 (el ganador) | 9 (todos) |
| **Tiempo respuesta** | 2-10 segundos | Horas |
| **Propósito** | Servicio al usuario | Mejora continua |
| **Frecuencia** | Tiempo real | Periódica |

---

## 2. Requisitos Funcionales y No Funcionales Mínimos

### 2.1 Requisitos Funcionales

**RF1 - Ingesta de documentos**
- El sistema debe aceptar archivos CSV con referencias a PDFs y descargar/validar automáticamente los documentos asociados.

**RF2 - Validación de datos**
- El sistema debe validar que las CLABEs tengan 18 dígitos
- Los RFCs cumplan el formato oficial mexicano (12-13 caracteres)
- Las CURPs tengan 18 caracteres con estructura válida

**RF3 - Extracción de campos**
- El sistema debe extraer correctamente titular, CLABE y banco de estados de cuenta de al menos 11 bancos mexicanos principales: BBVA MEXICO, SANTANDER, BANAMEX, BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX

**RF4 - Comparación de métodos**
- El sistema debe ejecutar múltiples parsers sobre los mismos documentos y generar reportes comparativos de precisión

**RF5 - API REST**
- El sistema debe exponer endpoints HTTP que acepten PDFs (multipart/form-data) y retornen JSON con los campos extraídos

**RF6 - Persistencia de resultados**
- Todos los resultados de extracción deben guardarse en CSV con timestamp para auditoría
- Formato: `{experiment_name}_{parser_name}_{timestamp}.csv`

**RF7 - Logging**
- Cada operación debe registrarse en logs estructurados con nivel de severidad (INFO, ERROR) y trazabilidad
- Logs separados por experimento en `data/results/logs/`

---

### 2.2 Requisitos No Funcionales

**RNF1 - Precisión**
- El parser en producción debe alcanzar mínimo **85% de precisión promedio** en los tres campos sobre documentos de prueba

**RNF2 - Latencia**
- El API debe responder en menos de **10 segundos** para documentos de hasta 5 páginas (percentil 95)

**RNF3 - Disponibilidad**
- El API debe tener disponibilidad mínima de **99%** durante horario laboral (8am-8pm)

**RNF4 - Escalabilidad**
- El sistema debe soportar procesamiento de al menos **100 documentos por hora** con una sola instancia

**RNF5 - Reproducibilidad**
- Todas las extracciones deben ser reproducibles con `temperature=0` en LLMs
- Versionamiento de prompts en el código fuente
- Logs detallados de parámetros usados

**RNF6 - Seguridad**
- Los PDFs procesados no deben persistir en disco más de **24 horas**
- Las APIs deben requerir autenticación por token (Bearer token)
- No se debe exponer información sensible en logs

**RNF7 - Observabilidad**
- El dashboard debe actualizarse en tiempo real (**<5s de delay**) al completar nuevas extracciones
- Métricas expuestas: latencia p50/p95/p99, tasa de error, throughput

**RNF8 - Costo**
- El costo promedio por documento procesado no debe exceder **$0.02 USD** considerando APIs pagadas
- Presupuesto mensual estimado: $20 USD para 1000 documentos

**RNF9 - Mantenibilidad**
- El código debe seguir principios SOLID (herencia de `BaseParser`)
- Cobertura de tests **>70%** (pytest)
- Documentación actualizada en docstrings y README

---

### 2.3 Configuración Mínima del Entorno

#### Hardware
- **CPU**: 4 núcleos mínimo (recomendado: 8 núcleos para LayoutLM)
- **RAM**: 8GB mínimo (recomendado: 16GB si se usa LayoutLM + Ollama)
- **Almacenamiento**: 20GB mínimo (incluye modelos, PDFs temporales, logs)
- **GPU**: Opcional (acelera LayoutLM y embeddings)

#### Software
- **Python**: 3.10+ (requerido por type hints y f-strings)
- **Tesseract OCR**: 5.x (para OCR con idioma español)
- **Poppler**: Última versión (requerido por pdf2image)
- **Ollama**: Opcional (solo si se usa HybridParser)

#### APIs Externas
- **Anthropic Claude**: API key válida (modelos Haiku/Sonnet)
- **LlamaParse**: API key válida (solo si se usa LlamaParser)

#### Dependencias Python
Listadas en `project/requirements.txt` con versiones fijadas:
```
anthropic>=0.18.0
pdfplumber>=0.10.0
pypdf>=3.17.0
pdf2image>=1.16.3
pytesseract>=0.3.10
pandas>=2.1.0
llama-index>=0.10.0
llama-parse>=0.4.0
transformers>=4.36.0
torch>=2.1.0
pillow>=10.1.0
```

#### Variables de Entorno
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
LLAMA_CLOUD_API_KEY=llx-xxx
```
