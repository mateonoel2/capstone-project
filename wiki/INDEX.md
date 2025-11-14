# 📚 Wiki del Proyecto - Extracción de Datos Bancarios

Bienvenido a la wiki del proyecto. Aquí encontrarás toda la documentación organizada.

---

## 📖 Documentación Principal

### [README.md](../README.md) ⬆️ (en raíz del proyecto)
Descripción general del proyecto, cómo instalarlo y primeros pasos.

### [CAPITULO_DISENO_SOLUCION.md](CAPITULO_DISENO_SOLUCION.md)
Capítulo completo del informe de tesis sobre el diseño de la solución del producto de datos. Incluye:
- Arquitectura del producto (flujos de producción y desarrollo)
- Diagramas de pipeline
- Requisitos funcionales y no funcionales

---

## 🔧 Documentación Técnica - Backend

### [SCRIPTS_README.md](SCRIPTS_README.md)
Guía completa de todos los scripts del proyecto:
- `upload_bank_accounts.py` - Carga y limpieza de datos desde Airtable
- `process_accounts.py` - Validación y filtrado de cuentas
- `run_extraction.py` - Ejecución de experimentos con parsers
- `validate_extraction.py` - Validación contra ground truth
- `run_api.py` - Servidor API REST

### [PARSER_COMPARISON_SUMMARY.md](PARSER_COMPARISON_SUMMARY.md)
Comparativa y análisis de los diferentes parsers implementados:
- Arquitectura 1: Parsers determinísticos (Regex, PDFPlumber)
- Arquitectura 2: Parsers basados en LLMs (Claude, Llama)
- Arquitectura 3: Parsers híbridos (Hybrid, LayoutLM)
- Resultados experimentales y parser ganador

---

## 💻 Documentación Frontend

### [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
Guía completa de instalación y configuración del frontend:
- Setup de Next.js + TypeScript + Tailwind
- Configuración de la base de datos SQLite
- Cómo ejecutar backend y frontend
- Troubleshooting común

### [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
Resumen técnico de la implementación del frontend:
- Arquitectura de componentes (React/Next.js)
- Integración con API del backend
- Sistema de base de datos para logging
- Flujo completo de extracción y verificación

### [DASHBOARD_IMPLEMENTATION.md](DASHBOARD_IMPLEMENTATION.md)
Documentación del dashboard de métricas:
- Endpoints del backend (`/logs`, `/metrics`)
- Cálculo de accuracy y correcciones
- Tabla de extracciones con búsqueda y ordenamiento
- Visualización de métricas por campo

### [LATEST_UPDATES.md](LATEST_UPDATES.md)
Log de las últimas actualizaciones y mejoras:
- Sidebar navigation
- Dropdown de bancos mexicanos
- Controles del PDF viewer
- Fixes de bugs

---

## 📅 Gestión del Proyecto

### [WEEKLY_UPDATE_WORKFLOW.md](WEEKLY_UPDATE_WORKFLOW.md)
Workflow y proceso de actualizaciones semanales del proyecto.

---

## 🗂️ Organización de Archivos

```
capstone-project/
├── README.md                       # 📖 Descripción general del proyecto
├── LICENSE
│
├── wiki/                           # 📚 Documentación (estás aquí)
│   ├── INDEX.md                    # Este archivo - índice de la wiki
│   ├── CAPITULO_DISENO_SOLUCION.md # Capítulo de tesis
│   ├── SCRIPTS_README.md           # Guía de scripts (backend)
│   ├── PARSER_COMPARISON_SUMMARY.md # Comparativa de parsers
│   ├── FRONTEND_SETUP.md           # Setup del frontend
│   ├── IMPLEMENTATION_SUMMARY.md   # Implementación frontend
│   ├── DASHBOARD_IMPLEMENTATION.md # Dashboard de métricas
│   ├── LATEST_UPDATES.md           # Log de actualizaciones
│   └── WEEKLY_UPDATE_WORKFLOW.md   # Workflow de updates
│
├── backend/                        # 🚀 Código del backend
│   ├── application/                # API REST + Database
│   ├── src/                        # Código fuente
│   │   ├── extraction/             # Parsers (9 implementaciones)
│   │   ├── preprocessing/          # Limpieza y OCR
│   │   ├── experiments/            # ExperimentRunner
│   │   └── utils/                  # Utilidades
│   ├── scripts/                    # Scripts ejecutables
│   ├── tests/                      # Tests unitarios
│   ├── data/                       # Datos y base de datos SQLite
│   └── config/                     # Configuraciones
│
├── frontend/                       # 💻 Aplicación Next.js
│   ├── app/                        # Pages (Next.js 13+)
│   ├── components/                 # Componentes React + shadcn/ui
│   ├── lib/                        # API client + Utils + Store
│   └── public/                     # Assets estáticos
```

---

## 🚀 Quick Start

### Para empezar con el proyecto:
1. **Setup inicial**: Lee [README.md](../README.md) (en raíz)
2. **Entender la arquitectura**: Lee [CAPITULO_DISENO_SOLUCION.md](CAPITULO_DISENO_SOLUCION.md)

### Para trabajar con el backend:
3. **Ejecutar scripts**: Sigue [SCRIPTS_README.md](SCRIPTS_README.md)
4. **Ver resultados de parsers**: Consulta [PARSER_COMPARISON_SUMMARY.md](PARSER_COMPARISON_SUMMARY.md)

### Para trabajar con el frontend:
5. **Setup del frontend**: Sigue [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
6. **Entender la implementación**: Lee [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
7. **Ver métricas**: Consulta [DASHBOARD_IMPLEMENTATION.md](DASHBOARD_IMPLEMENTATION.md)

---

## 📝 Notas

- Todos los documentos están en formato Markdown (`.md`)
- Los diagramas están en formato ASCII art
- Para convertir a PDF usa: `pandoc documento.md -o documento.pdf`

