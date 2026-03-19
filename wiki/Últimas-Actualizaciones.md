# Últimas Actualizaciones

**Ultima actualizacion:** Marzo 2026

## Actualizacion: Documentacion de API para Clientes (Marzo 2026)

### Cambios principales

- **Documentacion de API filtrada**: Nueva vista en `/api/docs` con *Swagger UI* que muestra unicamente los *endpoints* disponibles para integracion programatica (extraccion, extractores, tokens). La documentacion completa (incluyendo rutas internas y de admin) sigue disponible en `/docs`
- **Spec *OpenAPI* filtrado**: `GET /api/openapi.json` retorna un *OpenAPI spec* que incluye solo los *endpoints* de cliente, con *schemas* no utilizados eliminados automaticamente
- **Info banner en pagina principal**: La pagina de extraccion (`/`) ahora incluye un banner informativo que enlaza a la documentacion de la API y menciona que las extracciones via API se registran en el *dashboard* del usuario
- **Metadata de la app actualizada**: Titulo y descripcion del *FastAPI* app actualizados a "Extracto API"

---

## Actualizacion: Tokens API para Acceso Programatico (Marzo 2026)

### Cambios principales

- **Tokens API**: Los usuarios pueden crear tokens para acceder a la API de extraccion desde *scripts* o integraciones sin necesidad de autenticarse via navegador. Autenticacion via *header* `Authorization: Bearer <token>`
- **Gestion de tokens**: Nueva pagina `/settings/tokens` para crear, ver y revocar tokens. Soporte para expiracion opcional y seguimiento de ultimo uso
- **Atribucion a usuario**: Las extracciones realizadas con un token API se registran en el *dashboard* del usuario dueno del token, igual que las extracciones via interfaz web
- **Nuevos *endpoints***: `GET /tokens`, `POST /tokens`, `DELETE /tokens/{token_id}`
- **Modelo `ApiToken`**: Nueva tabla con *hash* del token, nombre, expiracion, estado de revocacion y ultimo uso
- **Sidebar actualizado**: Nueva entrada "Tokens API" en la navegacion

---

## Actualizacion: Autenticacion y *Multi-tenancy* (Marzo 2026)

### Cambios principales

- **Autenticacion con *GitHub OAuth***: Login via *NextAuth.js* con proveedor de *GitHub*. El *frontend* intercambia el *access token* de *GitHub* por un *JWT* del *backend* (`POST /auth/login`). Middleware protege todas las rutas excepto `/login`
- ***Multi-tenancy***: Nueva tabla `users` con roles (`user`/`admin`). Todas las tablas existentes (`extractor_configs`, `extraction_logs`, `api_call_logs`, `test_extraction_logs`) tienen `user_id` *FK*. Extractores con restriccion de nombre unico por usuario
- **Panel de administracion**: Nueva pagina `/admin/users` (solo admins) para gestionar usuarios: crear por *username* de *GitHub*, cambiar rol, activar/desactivar, eliminar
- **Autenticacion en *backend***: Nuevo modulo `auth.py` con creacion/validacion de *JWT*, dependencias `get_current_user` y `get_admin_user`. Rutas protegidas reciben `user_id` del token
- **Sidebar con usuario**: Muestra avatar y nombre del usuario autenticado, badge de admin, boton de cerrar sesion. Navegacion de admin condicional
- **Nuevas variables de entorno**: `JWT_SECRET` (*backend*), `AUTH_GITHUB_ID`, `AUTH_GITHUB_SECRET`, `AUTH_SECRET` (*frontend*)
- **Migracion Alembic**: Tabla `users`, columna `user_id` en tablas existentes, *backfill* de datos existentes al usuario admin

---

## Actualizacion: Extractores Configurables, Asistente IA y *React Query* (Marzo 2026)

### Cambios principales

- **Extractores configurables**: Los usuarios ahora crean extractores personalizados con *schemas*, *prompts* y modelos a traves de un *wizard* multi-paso (`/extractors/new`). Soporte para estado *draft*/*active* y versionado con pruebas A/B
- **Asistente de IA**: Nuevo *sidebar* (`AssistantSidebar`) que genera *schemas* JSON a partir de descripciones en texto natural, crea *prompts* de extraccion a partir de *schemas*, y refina *prompts* existentes. Alimentado por `ai_assist.py` en el *backend*
- ***React Query***: Se agrego `@tanstack/react-query` para gestion de estado del servidor. Nuevos *hooks* en `lib/hooks.ts` para configs, versiones, generacion IA, extraccion y subida. *Zustand* se mantiene para estado de UI
- **Visor de archivos mejorado**: Reescritura con `react-zoom-pan-pinch` para *zoom*, *pan* y rotacion de imagenes. PDFs se muestran en *iframe*
- **Rutas de extractores**: Nuevas paginas `/extractors`, `/extractors/new`, `/extractors/[id]/edit` para gestion CRUD
- **Extracciones de prueba**: Nuevo modelo `TestExtractionLog` y *endpoint* `POST /test-extract` para probar extractores con registro detallado
- **Rutas del *backend***: Nuevo modulo `api/extractors/routes.py` con CRUD, versionado, generacion IA y pruebas
- **Renombrado**: `is_bank_statement` → `is_valid_document` para soportar tipos de documentos genericos
- **Modelos disponibles**: Nuevo *endpoint* `GET /models` que lista modelos Claude disponibles con indicadores de costo

---

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
- Páginas: "Extraer PDF", "Extractores", "*Dashboard*", y "Usuarios" (admin)
- Resaltado de estado activo
- Perfil de usuario con avatar, badge de admin y cierre de sesion
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
- `frontend/app/page.tsx` - Pagina de extraccion
- `frontend/app/extractors/` - Gestion de extractores (CRUD + *wizard*)
- `frontend/app/dashboard/page.tsx` - *Dashboard* completo
- `frontend/app/layout.tsx` - *Layout* con *sidebar*
- `frontend/components/assistant/` - Sidebar de asistente IA
- `frontend/components/extractor-wizard/` - *Wizard* multi-paso para extractores
- `frontend/components/file-viewer.tsx` - Visor de PDF e imagenes
- `frontend/lib/api.ts` - Cliente de API
- `frontend/lib/hooks.ts` - *React Query hooks*
- `frontend/lib/store.ts` - Estado de UI (*Zustand*)

## *Endpoints* de la API

### Implementados y Funcionales

```
GET  /extraction/banks          - Lista de 91 bancos mexicanos
POST /extraction/upload-url     - Obtener presigned URL para subida directa a S3
POST /extraction/upload         - Subida de archivo via backend (fallback)
POST /extraction/extract        - Extraer informacion por s3_key (JSON)
POST /extraction/submit         - Enviar extraccion con correcciones
GET  /extraction/logs           - Obtener logs con paginacion
GET  /extraction/metrics        - Obtener metricas de precision
GET  /extraction/api-metrics    - Obtener metricas de llamadas API
GET  /extractors                - Listar configuraciones de extractores
POST /extractors                - Crear configuracion de extractor
PUT  /extractors/{id}           - Actualizar configuracion de extractor
DELETE /extractors/{id}         - Eliminar configuracion de extractor
POST /extractors/generate-schema  - Generar schema JSON con IA
POST /extractors/generate-prompt  - Generar prompt con IA
POST /extractors/update-prompt    - Refinar prompt con IA
POST /extractors/test-extract     - Probar extraccion con registro
GET  /extractors/models           - Listar modelos disponibles
GET  /extractors/versions         - Versiones de un extractor
POST /auth/login                 - Login con token de GitHub, retorna JWT
GET  /auth/me                    - Obtener usuario autenticado
GET  /admin/users                - Listar usuarios (admin)
POST /admin/users                - Crear usuario (admin)
PUT  /admin/users/{id}           - Actualizar usuario (admin)
DELETE /admin/users/{id}         - Eliminar usuario (admin)
GET  /tokens                    - Listar tokens API del usuario
POST /tokens                    - Crear token API
DELETE /tokens/{id}             - Revocar token API
GET  /health                    - Verificacion de salud
GET  /docs                      - Documentacion interactiva (completa)
GET  /api/docs                  - Documentacion de API para clientes (filtrada)
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

*PostgreSQL* con tablas principales:
- `users`: Usuarios registrados (*GitHub* ID, *username*, rol, estado)
- `extractor_configs`: Configuraciones de extractores (*schema*, *prompt*, modelo, estado, `user_id`)
- `extractor_config_versions`: Versiones de configuraciones para pruebas A/B
- `extraction_logs`: Valores extraidos, correcciones del usuario, *flags* de correccion por campo
- `api_call_logs`: Modelo utilizado, exito/error, tiempo de respuesta, tipo de error
- `test_extraction_logs`: Registro de extracciones de prueba con *snapshot* de configuracion

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
