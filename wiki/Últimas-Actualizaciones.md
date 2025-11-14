# Últimas Actualizaciones

## Nuevas Funcionalidades Agregadas

### 1. Navegación con *Sidebar*
- Agregado un *sidebar* oscuro con navegación
- Dos páginas: "Extraer PDF" y "*Dashboard*"
- Resaltado de estado activo
- Diseño profesional con *sidebar* fijo

### 2. *Dropdown* de Selección de Banco
- Reemplazado *input* de texto con *dropdown* de selección
- *Endpoint* del *backend*: `GET /extraction/banks`
- Retorna 91 bancos mexicanos de *BANK_DICT_KUSHKI*
- Bancos ordenados alfabéticamente
- Incluye códigos de banco para uso futuro

### 3. Página de *Dashboard* (Fase 2)
- Creada ruta `/dashboard`
- Tarjetas de métricas mostrando:
  - Total de Extracciones
  - Correcciones Realizadas
  - Tasa de Precisión
  - Actividad de Esta Semana
- Contenido de funcionalidades de Fase 2
- Interfaz profesional que coincide con la página de extracción

### 4. Mejoras del Visor de PDF
- Controles de *Zoom* In/Out (50% - 300%)
- Botón de rotación (incrementos de 90°)
- Visualización del porcentaje de *zoom* actual
- Mejor desplazamiento para visibilidad completa del documento
- Iconos para todos los controles

### 5. Correcciones de Errores del *Backend*
- Corregido error de sesión de *SQLAlchemy*
- Gestión adecuada de sesión con *refresh*
- Agregado *rollback* en errores
- Bloques *try-finally* para limpieza

## Cambios en Archivos

### Nuevos Archivos
- `frontend/components/sidebar.tsx` - *Sidebar* de navegación
- `frontend/components/ui/select.tsx` - Componente *dropdown* de selección
- `frontend/app/dashboard/page.tsx` - Página de *dashboard*
- `backend/application/constants.py` - Diccionario de bancos

### Archivos Modificados
- `frontend/app/layout.tsx` - Agregado *sidebar* al *layout*
- `frontend/app/page.tsx` - Selección de banco + *useEffect* para bancos
- `frontend/components/pdf-viewer.tsx` - Controles de *zoom* y rotación
- `frontend/lib/api.ts` - Agregada función *getBanks()*
- `backend/application/api/extraction.py` - *Endpoint* de bancos + corrección de sesión

## *Endpoints* de la API

### Nuevos

```
GET /extraction/banks
Response: { "banks": [{ "name": "...", "code": "..." }] }
```

### Corregidos

```
POST /extraction/submit
- Corregida gestión de sesión
- Manejo adecuado de errores
```

## Cómo Usar

### *Backend*

```bash
cd backend
python scripts/run_api.py
```

### *Frontend*

```bash
cd frontend
npm run dev
```

### Navegación
- Hacer clic en "Extraer PDF" en el *sidebar* para subir y extraer
- Hacer clic en "*Dashboard*" para ver la página de Fase 2
- Usar controles de *zoom* en el visor de PDF
- Seleccionar banco del *dropdown* (91 opciones)

## Base de Datos
La base de datos *SQLite* en `backend/data/extractions.db` ahora almacena adecuadamente:
- Valores extraídos originales
- Correcciones del usuario
- *Flags* de corrección por campo
- Sin más errores de sesión

## Próximos Pasos (Fase 2)

Para implementar el *dashboard* completo:
1. Agregar *endpoint* para obtener *logs* de extracción
2. Calcular métricas de precisión
3. Construir tabla de datos con filtrado
4. Agregar gráficos para tendencias
5. Funcionalidad de exportación

## Pruebas

1. Subir un estado de cuenta bancario en PDF
2. Verificar que el *dropdown* de banco muestre los 91 bancos
3. Usar controles de *zoom* en el PDF
4. Seleccionar banco del *dropdown*
5. Enviar formulario
6. Verificar entrada en la base de datos
7. Navegar a la página de *Dashboard*
