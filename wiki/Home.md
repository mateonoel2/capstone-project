# Wiki del Proyecto - Extracción de Datos Bancarios

Bienvenido a la *wiki* del proyecto de extracción automática de información de estados de cuenta bancarios.

---

## Inicio Rápido

### Para empezar con el proyecto:
1. **Configuración inicial**: Lee el [README](https://github.com/mateonoel2/capstone-project) del repositorio principal
2. **Entender la arquitectura**: Consulta [Diseño de Solución](Diseño-de-Solución)

### Para trabajar con el *backend*:
3. **Ejecutar *scripts***: Sigue la [Guía de *Scripts*](Guía-de-Scripts)
4. **Ver resultados de *parsers***: Consulta [Comparación de *Parsers*](Comparación-de-Parsers)
5. **Actualizar datos**: Revisa el [*Workflow* Semanal](Workflow-Semanal)

### Para trabajar con el *frontend*:
6. **Configuración**: Sigue la [Configuración del *Frontend*](Configuración-Frontend)
7. **Entender la implementación**: Lee el [Resumen de Implementación](Resumen-Implementación)
8. **Ver métricas**: Consulta la documentación del [*Dashboard*](Dashboard)
9. **Últimas mejoras**: Revisa las [Últimas Actualizaciones](Últimas-Actualizaciones)

---

## Tecnologías Utilizadas

### *Backend*
- **Lenguaje**: Python 3.10+
- ***Framework* API**: *FastAPI*
- **Base de Datos**: *SQLite* con *SQLAlchemy*
- **Extracción**: 9 *parsers* implementados
  - *Claude* (Haiku/Sonnet)
  - *LlamaParse*
  - *Tesseract OCR*
  - *PDFPlumber*, *PyPDF2*
  - *LayoutLM*
  - *Ollama* (*Llama 3.2*)

### *Frontend*
- ***Framework***: *Next.js* 15 con *App Router*
- **Lenguaje**: *TypeScript*
- **Estilos**: *Tailwind CSS*
- **Componentes**: *shadcn/ui* (*Radix UI*)
- **Visor PDF**: *react-pdf*
- **Iconos**: *Lucide React*

### *DevOps* y Herramientas
- **Control de versiones**: *Git* + *GitHub*
- **Gestión de dependencias**: *pip* (Python), *npm* (*Node.js*)
- ***Linting***: *Ruff* (Python)
- **Pruebas**: *pytest*

---

## Estructura del Proyecto

```
capstone-project/
├── backend/                        # Código del backend
│   ├── application/                # API REST + Database
│   │   ├── api/                    # Endpoints
│   │   ├── modules/                # Lógica de negocio
│   │   ├── database.py             # Configuración SQLite
│   │   └── constants.py            # Diccionario de bancos
│   ├── src/                        # Código fuente
│   │   ├── extraction/             # 9 parsers implementados
│   │   ├── preprocessing/          # Limpieza y OCR
│   │   ├── experiments/            # ExperimentRunner
│   │   └── utils/                  # Utilidades
│   ├── scripts/                    # Scripts ejecutables
│   ├── tests/                      # Tests unitarios
│   └── data/                       # Datos y base de datos SQLite
│
└── frontend/                       # Aplicación Next.js
    ├── app/                        # Pages (Next.js 13+)
    │   ├── page.tsx                # Extracción
    │   ├── dashboard/              # Dashboard
    │   └── layout.tsx              # Layout con sidebar
    ├── components/                 # Componentes React + shadcn/ui
    │   ├── sidebar.tsx             # Navegación
    │   ├── extraction-table.tsx    # Tabla de extracciones
    │   ├── pdf-viewer.tsx          # Visor de PDF
    │   └── ui/                     # Componentes base
    └── lib/                        # API client + Utils + Store
```

---

## Documentación por Tema

### Arquitectura y Diseño
- [Diseño de Solución](Diseño-de-Solución) - Arquitectura completa del producto de datos
- [Arquitectura Mínima Operable](Arquitectura-Mínima-Operable) - Componentes e infraestructura mínima

### Planificación y Evolución
- [Autodiagnóstico Prototipo-MVP](Autodiagnóstico-Prototipo-MVP) - Evaluación del estado actual del prototipo
- [Recomendaciones de Generalización](Recomendaciones-de-Generalización) - Hoja de ruta para evolucionar el proyecto

### *Backend*
- [Guía de *Scripts*](Guía-de-Scripts) - Cómo usar los *scripts* del proyecto
- [Comparación de *Parsers*](Comparación-de-Parsers) - Análisis de 9 *parsers* diferentes
- [*Workflow* Semanal](Workflow-Semanal) - Proceso de actualización de datos

### *Frontend*
- [Configuración del *Frontend*](Configuración-Frontend) - *Setup* completo
- [Resumen de Implementación](Resumen-Implementación) - Detalles técnicos
- [*Dashboard*](Dashboard) - Métricas y análisis
- [Últimas Actualizaciones](Últimas-Actualizaciones) - Estado actual del proyecto

---

## Estado del Proyecto

### Completamente Implementado

- Sistema de extracción con 9 *parsers*
- API REST con 7 *endpoints*
- *Frontend* con extracción y *dashboard*
- Base de datos *SQLite* con *logging*
- Sistema de métricas y análisis
- Visor de PDF con controles avanzados
- Tabla de extracciones con búsqueda y paginación

### *Parser* Recomendado

Según pruebas con 183 PDFs reales:
- ***Claude OCR Parser***: 63.8% precisión promedio
  - 80.9% en CLABE (campo más crítico)
  - 68.9% en Titular
  - 41.5% en Banco

---

## Enlaces Útiles

- [Repositorio Principal](https://github.com/mateonoel2/capstone-project)
- [*Issues*](https://github.com/mateonoel2/capstone-project/issues)
- [*Pull Requests*](https://github.com/mateonoel2/capstone-project/pulls)
- [Documentación API](http://localhost:8000/docs) (cuando el *backend* está ejecutándose)

---

## Inicio Rápido de Desarrollo

### 1. Clonar el repositorio

```bash
git clone https://github.com/mateonoel2/capstone-project.git
cd capstone-project
```

### 2. Configurar *backend*

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configurar API keys
python scripts/run_api.py
```

### 3. Configurar *frontend*

```bash
cd frontend
npm install
npm run dev
```

### 4. Acceder a la aplicación

- *Frontend*: http://localhost:3000
- API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

---

**Nota**: Todos los documentos están en español con términos técnicos en inglés en cursiva.
