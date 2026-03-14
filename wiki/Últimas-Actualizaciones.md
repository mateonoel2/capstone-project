# Últimas Actualizaciones

**Ultima actualizacion:** Marzo 2026

## Actualizacion: Subida con *Presigned URLs* y Abstraccion de *Storage* (Marzo 2026)

### Cambios principales

- **Subida con *presigned URLs***: El *frontend* ahora sube archivos directamente a S3 via *presigned PUT URLs*, eliminando la necesidad de pasar el archivo por el *backend*. Incluye *fallback* automatico via *backend* si la subida directa falla (CORS, red, etc.)
- **Abstraccion de *storage***: Nuevo `StorageBackend` ABC con implementaciones `LocalStorage` y `S3Storage` en `infrastructure/storage.py`
- **Desacoplamiento subida/extraccion**: La subida y la extraccion son pasos separados. El *frontend* primero sube el archivo y recibe un `s3_key`, luego solicita la extraccion por referencia
- **Nuevos *endpoints***: `POST /extraction/upload-url` (obtener *presigned URL*) y `POST /extraction/upload` (*fallback* de subida via *backend*)
- **Extraccion por JSON**: Los *endpoints* `/extraction/extract` y `/extractors/test-extract` ahora reciben JSON con `s3_key` en lugar de *multipart form data*
- **Configuracion CORS de S3**: El *backend* configura CORS en el *bucket* S3 al iniciar
- **Nueva variable de entorno**: `AWS_PUBLIC_ENDPOINT_URL` para *endpoints* accesibles desde el navegador

---

## Actualizacion: *Parser* Unificado y Seguimiento de API (Marzo 2026)

### Cambios principales

- **Parser unificado**: Los 3 *parsers* anteriores (*claude_ocr*, *claude_text*, *claude_vision*) se reemplazaron por un unico `StatementExtractor` basado en vision con *structured output*
- **Soporte de imagenes**: El sistema ahora acepta JPG y PNG ademas de PDF
- **Seguimiento de llamadas API**: Nuevo modelo `ApiCallLog` que registra cada llamada a Claude (exito/error, tiempo de respuesta, tipo de error)
- **Metricas de API**: Nuevo *endpoint* `GET /extraction/api-metrics` y seccion en el *dashboard*
- **Visor de archivos**: Nuevo componente `FileViewer` que muestra PDFs e imagenes con controles de zoom y rotacion
- **`ExtractionOutput`**: Modelo *Pydantic* con *structured output* de *LangChain* para respuestas tipadas de Claude
- **Migracion Alembic**: Nueva tabla `api_call_logs`

---

## Estado Actual del Proyecto

El proyecto esta completamente funcional con todas las funcionalidades principales implementadas.

## Funcionalidades Implementadas

### 1. Navegacion con *Sidebar*
- *Sidebar* oscuro con navegación implementado
- Dos páginas funcionales: "Extraer PDF" y "*Dashboard*"
- Resaltado de estado activo
- Diseño profesional con *sidebar* fijo

### 2. *Dropdown* de Selección de Banco
- *Input* de texto reemplazado con *dropdown* de selección
- *Endpoint* del *backend*: `GET /extraction/banks`
- Retorna 91 bancos mexicanos de *BANK_DICT_KUSHKI*
- Bancos ordenados alfabéticamente
- Incluye códigos de banco

### 3. *Dashboard* Completo (Implementado)
- Ruta `/dashboard` completamente funcional
- Tarjetas de métricas mostrando:
  - Total de Extracciones
  - Correcciones Realizadas
  - Tasa de Precisión
  - Actividad de Esta Semana
- Tabla completa de extracciones con:
  - Búsqueda y filtrado
  - Ordenamiento por columnas
  - Paginación
  - Indicadores visuales de corrección
- Gráficos de precisión por campo
- Interfaz profesional integrada

### 4. Visor de PDF Mejorado
- Controles de *Zoom* In/Out (50% - 300%)
- Botón de rotación (incrementos de 90°)
- Visualización del porcentaje de *zoom* actual
- Desplazamiento optimizado para visibilidad completa del documento
- Iconos para todos los controles

### 5. Sistema de Extraccion
- *Parser* unificado `StatementExtractor` basado en vision con *Claude Haiku 4.5*
- Soporte para PDFs e imagenes (JPG/PNG)
- *Structured output* via *LangChain* (`ExtractionOutput`)
- Deteccion automatica de documentos no bancarios
- Seguimiento de llamadas API con metricas de error y tiempo de respuesta

### 6. Base de Datos y *Logging*
- *PostgreSQL* con migraciones *Alembic*
- Gestion de sesiones con *SQLAlchemy*
- *Rollback* automatico en errores
- Seguimiento de correcciones por campo (`ExtractionLog`)
- Seguimiento de llamadas API (`ApiCallLog`)

## Archivos del Sistema

### *Backend*
- `backend/src/infrastructure/api/extraction/routes.py` - Todos los *endpoints* implementados
- `backend/src/infrastructure/api/extraction/dtos.py` - *DTOs* y validación
- `backend/src/domain/services/` - Lógica de negocio (extraction, submission, metrics)
- `backend/src/infrastructure/repository.py` - Acceso a datos
- `backend/src/infrastructure/models.py` - Modelos ORM de base de datos
- `backend/src/domain/entities.py` - Entidades de dominio
- `backend/src/domain/constants.py` - Constantes y diccionario de bancos
- `backend/src/infrastructure/extractors/statement_extractor.py` - Extractor unificado
- `backend/src/infrastructure/storage.py` - Abstraccion de *storage* (S3 / local)

### *Frontend*
- `frontend/app/page.tsx` - Página de extracción
- `frontend/app/dashboard/page.tsx` - *Dashboard* completo
- `frontend/app/layout.tsx` - *Layout* con *sidebar*
- `frontend/components/sidebar.tsx` - Navegación
- `frontend/components/extraction-table.tsx` - Tabla de extracciones
- `frontend/components/pdf-viewer.tsx` - Visor con controles
- `frontend/components/bank-combobox.tsx` - Selector de bancos
- `frontend/lib/api.ts` - Cliente de API
- `frontend/lib/store.ts` - Gestión de estado

## *Endpoints* de la API

### Implementados y Funcionales

```
GET  /extraction/banks        - Lista de 91 bancos mexicanos
POST /extraction/upload-url   - Obtener presigned URL para subida directa a S3
POST /extraction/upload       - Subida de archivo via backend (fallback)
POST /extraction/extract      - Extraer informacion por s3_key (JSON)
POST /extraction/submit       - Enviar extraccion con correcciones
GET  /extraction/logs         - Obtener logs con paginacion
GET  /extraction/metrics      - Obtener metricas de precision
GET  /extraction/api-metrics  - Obtener metricas de llamadas API
GET  /health                  - Verificacion de salud
GET  /docs                    - Documentacion interactiva
```

## Cómo Usar

### *Backend*

```bash
cd backend
python scripts/run_api.py
```

El servidor inicia en http://localhost:8000

### *Frontend*

```bash
cd frontend
npm run dev
```

La aplicación inicia en http://localhost:3000

### Navegación
- Hacer clic en "Extraer PDF" en el *sidebar* para subir y extraer
- Hacer clic en "*Dashboard*" para ver métricas y análisis
- Usar controles de *zoom* en el visor de PDF
- Seleccionar banco del *dropdown* (91 opciones)

## Base de Datos

*PostgreSQL* con dos tablas principales:
- `extraction_logs`: Valores extraidos, correcciones del usuario, *flags* de correccion por campo
- `api_call_logs`: Modelo utilizado, exito/error, tiempo de respuesta, tipo de error

## Métricas y Análisis

El *dashboard* proporciona:
- Conteo total de extracciones
- Tasa de precisión general
- Precisión por campo (Titular, Banco, CLABE)
- Actividad semanal
- Tabla completa de extracciones con búsqueda y filtrado

## Pruebas

1. Subir un estado de cuenta bancario en PDF
2. Verificar que el *dropdown* de banco muestre los 91 bancos
3. Usar controles de *zoom* en el PDF
4. Seleccionar banco del *dropdown*
5. Enviar formulario
6. Verificar entrada en la base de datos
7. Navegar a la página de *Dashboard*
8. Ver métricas y tabla de extracciones
