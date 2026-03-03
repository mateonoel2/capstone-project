# Extracción de Estados de Cuenta Bancarios

Proyecto de *capstone* para la extracción automática de información de estados de cuenta bancarios utilizando diferentes enfoques de procesamiento.


https://github.com/user-attachments/assets/f1b3834b-239e-495c-95ac-458b0bf03d38


## Descripción

Este proyecto implementa un sistema de producción (*FastAPI* + *Next.js*) y una capa de investigación para extraer información estructurada de estados de cuenta bancarios mexicanos en formato PDF. Utiliza 8 *parsers* diferentes (2 seleccionables desde la UI) basados en *Claude Sonnet 4.6*, *LlamaParse*, OCR, expresiones regulares y más.

## Características

- Aplicación web de producción con *FastAPI* (*backend*) y *Next.js* (*frontend*)
- Selector de *parser* en la UI (*Claude OCR* 63.8%, *Claude Vision* 54.5%)
- 8 estrategias de *parsing* para experimentación
- *Dashboard* con métricas de precisión y correcciones
- Preprocesamiento y limpieza de datos (OCR, validación)
- Sistema de experimentación para comparar enfoques
- Suite de pruebas automatizadas

## Estructura del Proyecto

```
capstone-project/
├── backend/
│   ├── src/
│   │   ├── application/            # API REST (FastAPI)
│   │   │   ├── api/                # Endpoints
│   │   │   ├── modules/            # Servicios, repositorio, entidades
│   │   │   ├── database.py         # Configuración SQLite
│   │   │   └── main.py             # Entry point
│   │   ├── extraction/             # 8 parsers implementados
│   │   ├── preprocessing/          # Preprocesamiento de datos
│   │   ├── experiments/            # Sistema de experimentos
│   │   └── utils/                  # Utilidades
│   ├── scripts/                    # Scripts ejecutables
│   ├── tests/                      # Pruebas unitarias
│   └── data/                       # Datos y base de datos SQLite
│
└── frontend/                       # Aplicación Next.js
    ├── app/                        # Pages (App Router)
    ├── components/                 # Componentes React + shadcn/ui
    └── lib/                        # API client, Store, Utils
```

## Requisitos

- Python >= 3.9
- Dependencias principales:
  - *llama-index-core*
  - *llama-parse*
  - *anthropic*
  - *pandas*
  - *pydantic*
  - *PyPDF2*
  - *torch*
  - *sentence-transformers*

## Instalación

1. Clonar el repositorio:

```bash
git clone <repository-url>
cd capstone-project
```

2. Crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
cd backend
pip install -r requirements.txt
```

4. Configurar variables de entorno:

```bash
cp .env.example .env
# Editar .env con tus credenciales de API
```

## Uso

### Aplicación web

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.application.main:app --reload  # http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### *Scripts* de investigación

```bash
cd backend
python scripts/run_extraction.py --parser all --input-dir data/raw/bank_statements
python scripts/run_extraction.py --parser llama --limit 10
```

## Pruebas

Ejecutar todas las pruebas:

```bash
pytest
```

Ejecutar pruebas específicas:

```bash
pytest tests/test_file_validator.py
pytest tests/test_data_cleaner.py
```

## Resultados

Los resultados de las extracciones se guardan en `data/results/` con:

- Archivos CSV con los datos extraídos
- Archivos JSON con resúmenes estadísticos
- *Logs* detallados en `data/results/logs/`

## Desarrollo

### *Linting*

El proyecto utiliza *Ruff* para *linting*:

```bash
ruff check .
ruff format .
```

### Agregar un nuevo *parser*

1. Crear una nueva clase que herede de `BaseParser` en `src/extraction/`
2. Implementar el método `parse()`
3. Agregar el *parser* a `run_extraction.py`

## Notas

- Los estados de cuenta deben estar en formato PDF
- Asegúrate de tener las *API keys* necesarias configuradas en el archivo `.env`
- Los resultados incluyen métricas de tiempo de procesamiento y éxito de extracción

## Licencia

Ver el archivo LICENSE para más detalles.
