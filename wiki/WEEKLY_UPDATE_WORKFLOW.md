# *Workflow* de Actualización Semanal de Cuentas Bancarias

## Resumen General

*Workflow* simple de 3 pasos para procesar datos de cuentas bancarias para experimentos de extracción.

## *Workflow* Completo (3 Pasos)

### 1. Subir Datos de Cuentas Bancarias

```bash
python scripts/upload_bank_accounts.py
```

**Qué hace:**

- Hace respaldo del antiguo `bank_accounts_downloaded.csv` (si existe)
- Lee y **limpia automáticamente** el nuevo `bank accounts-Grid view.csv`:
  - Corrige registros de múltiples filas (saltos de línea embebidos)
  - Normaliza espacios en blanco
  - Asegura formato CSV adecuado
- Muestra cuántos registros fueron agregados/eliminados
- Guarda versión limpia como `bank_accounts_downloaded.csv`

***Output*:**

- Respaldo: `data/raw/backups/bank_accounts_downloaded_YYYYMMDD_HHMMSS.csv`
- Actualizado: `data/raw/bank_accounts_downloaded.csv` (limpio)

---

### 2. Descargar Estados de Cuenta Bancarios

```bash
python src/preprocessing/download_statements.py
```

**Qué hace:**

- Descarga archivos desde URLs en el CSV
- **Detecta y filtra automáticamente** tipos de archivo:
  - **Aceptados:** PDF, JPG, PNG, GIF, WEBP, BMP, TIFF, HEIC
  - **Omitidos:** *Excel* (.xlsx), *Word* (.docx), archivos ZIP, ejecutables
- Maneja archivos existentes (no re-descarga)
- Actualiza CSV con estado de descarga

**Se puede ejecutar en segundo plano:**

```bash
python src/preprocessing/download_statements.py > download_log.txt 2>&1 &
```

---

### 3. Procesar Cuentas (Filtrar y Preparar)

```bash
python scripts/process_accounts.py
```

**Qué hace:**

**Paso 1: Filtrar por validación**

- Valida números CLABE de 18 dígitos
- Valida formatos RFC/CURP
- Elimina CLABEs duplicados
- Limpia saltos de línea embebidos

**Paso 2: Filtrar solo a PDFs**

- Mantiene solo cuentas con archivos PDF válidos
- Copia PDFs a `data/processed/pdfs/bank_statements/`
- Crea CSV limpio final

***Output*:**

- `data/processed/pdfs/bank_accounts_filtered.csv` (cuentas con PDFs)
- `data/processed/pdfs/bank_statements/` (archivos PDF)

---

### 4. Ejecutar Experimentos de Extracción (Opcional)

```bash
# Probar con algunos archivos
python scripts/run_extraction.py --parser regex --limit 10

# Ejecutar en todos los archivos
python scripts/run_extraction.py --parser regex

# Comparar ambos parsers
python scripts/run_extraction.py --parser all
```

***Parsers* disponibles:**

- `regex` - Extracción basada en patrones (rápida)
- `llama` - Extracción basada en *LLM* (precisa, requiere *API keys*)
- `all` - Comparar ambos *parsers*

---

## Manejo de Tipos de Archivo

### Tipos de Archivo Soportados

El descargador ahora detecta y maneja adecuadamente:

| Tipo        | Extensiones                                       | Estado                     |
| ----------- | ------------------------------------------------ | -------------------------- |
| PDF         | `.pdf`                                           | Aceptado                |
| Imágenes      | `.jpg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff` | Aceptado                |
| HEIC        | `.heic`                                          | Aceptado (formato *Apple*) |
| *Office*      | `.xlsx`, `.docx`                                 | Omitido                  |
| Archivos    | `.zip`                                           | Omitido                  |
| Ejecutables | `.exe`                                           | Omitido                  |
| Desconocido     | `.bin`                                           | Mantenido para revisión         |

### Limpiar Archivos .bin Existentes

Si tienes archivos `.bin` existentes de descargas previas:

```bash
python src/preprocessing/cleanup_bin_files.py
```

Esto hará:

- Detectar tipo de archivo real
- Convertir a extensión adecuada (si es soportado)
- Eliminar archivos no soportados (documentos de *Office*, ejecutables)

---

## Validación de Datos

### Nombres de Bancos

Todos los nombres de bancos deben coincidir exactamente con ***BANK_DICT_KUSHKI***:

- BBVA MEXICO, SANTANDER, BANAMEX, BANORTE, HSBC, SCOTIABANK
- AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX
- Y 70+ más...

El esquema valida y normaliza automáticamente los nombres de bancos.

### Validación de Documentos

- **RFC:**
  - Persona: `^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$` (ej., `OEEF970812PY1`)
  - Empresa: `^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$` (ej., `STE080926CA0`)
- **CURP:** `^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$` (ej., `FOMJ870825MDGLRH01`)
- **CLABE:** Exactamente 18 dígitos (ej., `012180015788025831`)

---

## Comandos Rápidos

```bash
# 1. Subir nuevos datos
python scripts/upload_bank_accounts.py

# 2. Descargar estados de cuenta
python src/preprocessing/download_statements.py

# 3. Procesar cuentas
python scripts/process_accounts.py

# 4. Ejecutar experimentos (opcional)
python scripts/run_extraction.py --parser regex --limit 5
```

**O ejecutar todo de una vez:**

```bash
python scripts/upload_bank_accounts.py && \
python src/preprocessing/download_statements.py && \
python scripts/process_accounts.py
```

---

## Estructura de Directorios

```
data/
├── raw/
│   ├── bank accounts-Grid view.csv     # Exportación semanal desde Airtable
│   ├── bank_accounts_downloaded.csv    # Versión limpia de trabajo
│   ├── backups/                         # Respaldos con marca de tiempo
│   └── bank_statements/                 # Todos los archivos descargados
│
├── processed/
│   ├── bank_accounts_filtered.csv      # Todas las cuentas válidas
│   └── pdfs/
│       ├── bank_accounts_filtered.csv  # Solo cuentas con PDFs
│       └── bank_statements/            # Solo archivos PDF válidos
│
└── results/
    ├── bank_extraction_*.csv           # Resultados de extracción
    └── logs/                            # Logs de experimentos
```

---

## Solución de Problemas

### Problema: Registros de múltiples filas en CSV

**Solución:** El *script* `update_bank_accounts.py` ahora corrige esto automáticamente.

### Problema: Aparecen archivos .bin

**Solución:** Ejecuta `python src/preprocessing/cleanup_bin_files.py` para identificarlos y manejarlos.

### Problema: Descarga atascada o fallando

**Solución:**

1. Detener el proceso
2. Re-ejecutar `python scripts/download_statements.py` - se reanudará desde donde se detuvo
3. Verificar conexión de red y URLs de *Airtable*

### Problema: Error de archivos ya existentes

**Solución:** El descargador omite archivos existentes automáticamente.

---

## Notas

- **Respaldos:** Todos los archivos antiguos se respaldan automáticamente con marcas de tiempo
- **Idempotente:** Todos los *scripts* pueden re-ejecutarse de forma segura - manejan datos existentes
- **Limpieza de CSV:** Los saltos de línea embebidos se eliminan automáticamente
- **Detección de Archivos:** Usa *magic bytes*, no solo extensiones de archivo
