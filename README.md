# Extracción de Estados de Cuenta Bancarios

Proyecto de capstone para la extracción automática de información de estados de cuenta bancarios utilizando diferentes enfoques de procesamiento.

## 📋 Descripción

Este proyecto implementa y compara múltiples métodos para extraer información estructurada de estados de cuenta bancarios en formato PDF, incluyendo:

- **LlamaParse**: Extracción basada en modelos de lenguaje (LLM)
- **Regex Parser**: Extracción basada en expresiones regulares

El sistema está diseñado para experimentar con diferentes técnicas y evaluar su efectividad en la extracción de datos bancarios.

## ✨ Características

- Extracción automatizada de datos de estados de cuenta en PDF
- Múltiples estrategias de parsing (LLM y Regex)
- Sistema de experimentación para comparar diferentes enfoques
- Preprocesamiento y limpieza de datos
- Validación de archivos
- Descarga automatizada de estados de cuenta
- Logging detallado de experimentos
- Suite de pruebas automatizadas

## 📁 Estructura del Proyecto

```
backend/
├── config/                      # Archivos de configuración
│   └── extraction_config.yaml
├── data/                        # Datos del proyecto
│   ├── raw/                     # Datos sin procesar
│   ├── processed/               # Datos procesados
│   └── results/                 # Resultados de extracción
├── notebooks/                   # Jupyter notebooks para análisis
├── scripts/                     # Scripts ejecutables
│   ├── clean_data.py           # Limpieza de datos
│   ├── download_statements.py  # Descarga de estados de cuenta
│   └── run_extraction.py       # Ejecución de extracción
├── src/                        # Código fuente
│   ├── experiments/            # Sistema de experimentos
│   ├── extraction/             # Parsers y esquemas
│   ├── preprocessing/          # Preprocesamiento de datos
│   └── utils/                  # Utilidades
└── tests/                      # Pruebas unitarias
```

## 🔧 Requisitos

- Python >= 3.9
- Dependencias principales:
  - llama-index-core
  - llama-parse
  - anthropic
  - pandas
  - pydantic
  - PyPDF2
  - torch
  - sentence-transformers

## 🚀 Instalación

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

## 💻 Uso

### Extracción con LlamaParse

```bash
python scripts/run_extraction.py --parser llama --input-dir data/raw/bank_statements
```

### Extracción con Regex

```bash
python scripts/run_extraction.py --parser regex --input-dir data/raw/bank_statements
```

### Comparar todos los parsers

```bash
python scripts/run_extraction.py --parser all --input-dir data/raw/bank_statements
```

### Limitar número de archivos a procesar

```bash
python scripts/run_extraction.py --parser llama --limit 10
```

### Preprocesamiento de datos

```bash
# Limpiar datos crudos
python scripts/clean_data.py

# Descargar estados de cuenta
python scripts/download_statements.py
```

## 🧪 Pruebas

Ejecutar todas las pruebas:

```bash
pytest
```

Ejecutar pruebas específicas:

```bash
pytest tests/test_file_validator.py
pytest tests/test_data_cleaner.py
```

## 📊 Resultados

Los resultados de las extracciones se guardan en `data/results/` con:

- Archivos CSV con los datos extraídos
- Archivos JSON con resúmenes estadísticos
- Logs detallados en `data/results/logs/`

## 🛠️ Desarrollo

### Linting

El proyecto utiliza Ruff para linting:

```bash
ruff check .
ruff format .
```

### Agregar un nuevo parser

1. Crear una nueva clase que herede de `BaseParser` en `src/extraction/`
2. Implementar el método `parse()`
3. Agregar el parser a `run_extraction.py`

## 📝 Notas

- Los estados de cuenta deben estar en formato PDF
- Asegúrate de tener las API keys necesarias configuradas en el archivo `.env`
- Los resultados incluyen métricas de tiempo de procesamiento y éxito de extracción

## 📄 Licencia

Ver el archivo LICENSE para más detalles.
