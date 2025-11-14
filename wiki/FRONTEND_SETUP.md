# Guía de Configuración del *Frontend*

Esta guía te ayudará a configurar y ejecutar la aplicación completa de Extracción de Estados de Cuenta Bancarios con *backend* y *frontend*.

## Inicio Rápido

### 1. Configuración del *Backend*

Primero, asegúrate de que la API del *backend* esté ejecutándose:

```bash
cd backend

python scripts/run_api.py
```

El *backend* iniciará en http://localhost:8000

Puedes verificar que está ejecutándose visitando:
- Documentación de la API: http://localhost:8000/docs
- Verificación de salud: http://localhost:8000/health

### 2. Configuración del *Frontend*

En una nueva terminal, navega al directorio del *frontend* e instala las dependencias:

```bash
cd frontend

npm install
```

### 3. Ejecutar el *Frontend*

Inicia el servidor de desarrollo:

```bash
npm run dev
```

El *frontend* iniciará en http://localhost:3000

## Flujo Completo de la Aplicación

1. ***Backend*** (http://localhost:8000):
   - Maneja la extracción de PDF usando *Claude AI*
   - Almacena *logs* de extracción en base de datos *SQLite*
   - Proporciona *endpoints* de API REST

2. ***Frontend*** (http://localhost:3000):
   - Interfaz moderna para subir PDFs
   - Visor de PDF y formulario lado a lado
   - Interfaz de verificación y corrección de datos
   - Envía datos verificados de vuelta al *backend*

## Base de Datos

La base de datos *SQLite* se crea automáticamente en:

```
backend/data/extractions.db
```

Almacena:
- Valores extraídos originales
- Valores finales corregidos por el usuario
- *Flags* de corrección para seguimiento de precisión
- Marcas de tiempo y nombres de archivo

## Esquema de la Base de Datos

```sql
CREATE TABLE extraction_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    filename TEXT,
    extracted_owner TEXT,
    extracted_bank_name TEXT,
    extracted_account_number TEXT,
    final_owner TEXT,
    final_bank_name TEXT,
    final_account_number TEXT,
    owner_corrected BOOLEAN,
    bank_name_corrected BOOLEAN,
    account_number_corrected BOOLEAN
);
```

## Accediendo a la Base de Datos

Puedes consultar la base de datos directamente usando *SQLite*:

```bash
cd backend/data
sqlite3 extractions.db

# Ejemplos de consultas:
SELECT * FROM extraction_logs;
SELECT COUNT(*) FROM extraction_logs WHERE owner_corrected = 1;
SELECT * FROM extraction_logs ORDER BY timestamp DESC LIMIT 10;
```

## Requisitos del Entorno

### *Backend*
- Python 3.8+
- Todas las dependencias de `backend/requirements.txt`
- *ANTHROPIC_API_KEY* en archivo `.env`

### *Frontend*
- Node.js 18+
- npm/yarn/pnpm

## Solución de Problemas

### Problemas del *Backend*

**Problema**: Errores de importación

```bash
# Solución: Asegúrate de estar en el directorio del proyecto
cd backend
python -m pip install -r requirements.txt
```

**Problema**: Errores de API de *Claude*

```bash
# Solución: Verifica que tu archivo .env tenga ANTHROPIC_API_KEY
cat backend/.env | grep ANTHROPIC_API_KEY
```

### Problemas del *Frontend*

**Problema**: Errores de permisos de npm

```bash
# Solución: Intenta usar un gestor de paquetes diferente
npm install --legacy-peer-deps
# o
yarn install
# o
pnpm install
```

**Problema**: PDF no se muestra

```bash
# Solución: Asegúrate de que react-pdf esté instalado correctamente
cd frontend
npm install react-pdf --force
```

**Problema**: Errores de CORS

```bash
# Solución: El backend ya tiene CORS habilitado para todos los orígenes
# Verifica que el backend esté ejecutándose en el puerto 8000
```

## Consejos de Desarrollo

### *Hot Reload*
Tanto el *frontend* como el *backend* soportan *hot reload*:
- *Frontend*: Automático al guardar archivo
- *Backend*: Automático con `reload=True` en *uvicorn*

### Depuración

***Backend***:

```python
# Agrega declaraciones print o usa la interfaz de documentos de FastAPI
# Visita http://localhost:8000/docs para probar endpoints
```

***Frontend***:

```javascript
// Usa la consola de DevTools del navegador
// Verifica la pestaña Network para llamadas a la API
// React DevTools para el estado de componentes
```

### Probando el Flujo

1. Usa un PDF de muestra de `backend/data/processed/pdfs/test_sample/`
2. Súbelo a través del *frontend*
3. Verifica los resultados de extracción
4. Haz una corrección a un campo
5. Envía el formulario
6. Verifica la base de datos para confirmar que se creó el *log*

```bash
# Verificación rápida de la base de datos
cd backend/data
sqlite3 extractions.db "SELECT filename, owner_corrected, bank_name_corrected, account_number_corrected FROM extraction_logs ORDER BY timestamp DESC LIMIT 1;"
```

## Despliegue en Producción

### *Backend*

```bash
cd backend
pip install -r requirements.txt
python scripts/run_api.py
# o usa gunicorn para producción:
gunicorn application.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### *Frontend*

```bash
cd frontend
npm run build
npm start
# o despliega en Vercel, Netlify, etc.
```

## Próximos Pasos (Fase 2)

Después de que la página de extracción esté funcionando, la Fase 2 agregará:
- Página de *dashboard* mostrando todas las extracciones
- Métricas de precisión y gráficos
- Capacidades de filtrado y búsqueda
- Funcionalidad de exportación de datos

## Soporte

Para problemas específicos de:
- **Lógica de extracción**: Verifica `backend/src/extraction/`
- ***Endpoints* de API**: Verifica `backend/application/api/`
- **Interfaz del *frontend***: Verifica `frontend/components/`
- **Base de datos**: Verifica `backend/application/database.py`
