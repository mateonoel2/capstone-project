# *Scripts*

## Flujo de Trabajo Principal (2 *Scripts*)

### 1. `upload_bank_accounts.py`

**Propósito:** Subir y limpiar nuevos datos desde exportación de *Airtable*

```bash
python scripts/upload_bank_accounts.py
```

- *Input*: `data/raw/bank accounts-Grid view.csv` (desde *Airtable*)
- *Output*: `data/raw/bank_accounts_downloaded.csv` (limpio)
- Hace respaldo del archivo antiguo automáticamente
- Corrige saltos de línea embebidos y problemas de formato

---

### 2. `process_accounts.py`

**Propósito:** Filtrar, validar y preparar el *dataset* final

```bash
python scripts/process_accounts.py
```

**Paso 1: Validar**

- CLABE: 18 dígitos
- RFC/CURP: Formato correcto
- Eliminar duplicados

**Paso 2: Filtrar a PDFs**

- Mantener solo cuentas con archivos PDF
- Copiar PDFs a carpeta procesada

***Output*:**

- `data/processed/pdfs/bank_accounts_filtered.csv`
- `data/processed/pdfs/bank_statements/` (solo PDFs)

---

## Flujo de Trabajo Completo

```bash
# 1. Subir nuevos datos desde Airtable
python scripts/upload_bank_accounts.py

# 2. Descargar estados de cuenta (en src/preprocessing)
python src/preprocessing/download_statements.py

# 3. Procesar y filtrar cuentas
python scripts/process_accounts.py
```

**O ejecutar todo de una vez:**

```bash
python scripts/upload_bank_accounts.py && \
python src/preprocessing/download_statements.py && \
python scripts/process_accounts.py
```

---

## Servidor de API

### `run_api.py`

Ejecutar el servidor *FastAPI* para extracción de PDF

```bash
python scripts/run_api.py
```

***Endpoints*:**

- `POST /extraction/pdf` - Subir un PDF y extraer información de cuenta bancaria
- `GET /health` - Verificación de salud
- `GET /docs` - Documentación interactiva de la API

**Ejemplo de uso:**

```bash
curl -X POST "http://localhost:8000/extraction/pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/statement.pdf"
```

**Respuesta:**

```json
{
  "owner": "JOHN DOE",
  "bank_name": "BBVA MEXICO",
  "account_number": "012180015788025831"
}
```

---

## Otros *Scripts*

### `run_extraction.py`

Ejecutar experimentos de extracción en PDFs

```bash
# Probar con 10 archivos
python scripts/run_extraction.py --parser regex --limit 10

# Ejecución completa
python scripts/run_extraction.py --parser regex

# Comparar ambos parsers
python scripts/run_extraction.py --parser all
```

---

## Herramientas de Soporte (en `src/preprocessing/`)

- `download_statements.py` - Descargar archivos de estados de cuenta bancarios
- `cleanup_bin_files.py` - Corregir tipos de archivo mal detectados
- `file_downloader.py` - Funcionalidad central de descarga
- `file_validator.py` - Utilidades de validación de archivos
- `data_cleaner.py` - Utilidades de limpieza de datos
