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
- **Lenguaje**: Python 3.12+
- ***Framework* API**: *FastAPI*
- **Base de Datos**: *PostgreSQL* con *SQLAlchemy* y migraciones *Alembic*
- **Extraccion**: *StatementParser* unificado basado en vision con *Claude Haiku 4.5*
- **Gestion de dependencias**: *uv*

### *Frontend*
- ***Framework***: *Next.js* 15 con *App Router*
- **Lenguaje**: *TypeScript*
- **Estilos**: *Tailwind CSS*
- **Componentes**: *shadcn/ui* (*Radix UI*)
- **Visor PDF**: *react-pdf*
- **Iconos**: *Lucide React*

### *DevOps* y Herramientas
- **Control de versiones**: *Git* + *GitHub*
- **Gestión de dependencias**: *uv* (Python), *npm* (*Node.js*)
- ***Linting***: *Ruff* (Python), *ESLint* (*Next.js*)
- **Pruebas**: *pytest*
- **CI**: *GitHub Actions* (ruff format, lint, tests)
- **Despliegue**: *Railway* (*backend*), *Vercel* (*frontend*)
- **Contenedores**: *Docker Compose* (*backend* + *PostgreSQL* + *LocalStack*)

---

## Estructura del Proyecto

```
capstone-project/
├── backend/                        # Código del backend
│   ├── src/
│   │   ├── main.py                 # Entry point (FastAPI)
│   │   ├── domain/                 # Lógica de negocio pura
│   │   │   ├── schemas.py          # BankAccount (Pydantic)
│   │   │   ├── constants.py        # Constantes y diccionario de bancos
│   │   │   ├── validators.py       # Validacion CLABE/bancos
│   │   │   ├── parser_interface.py # BaseParser ABC
│   │   │   ├── entities.py         # Entidades de dominio y API calls
│   │   │   └── services/           # Servicios de negocio
│   │   ├── infrastructure/         # Integraciones externas
│   │   │   ├── api/extraction/     # Rutas HTTP y DTOs
│   │   │   ├── database.py         # Configuracion PostgreSQL
│   │   │   ├── models.py           # ORM (ExtractionLog, ApiCallLog)
│   │   │   ├── repository.py       # Acceso a datos
│   │   │   ├── parsers/            # StatementParser (vision unificado)
│   │   │   ├── preprocessing/      # Validacion y descarga
│   │   │   ├── evaluation/         # Experimentos y metricas
│   │   │   └── data_pipeline/      # Scripts de datos
│   │   ├── core/                   # Utilidades genericas
│   │   └── tests/                  # Tests unitarios
│   ├── alembic/                    # Migraciones de base de datos
│   ├── scripts/                    # Scripts ejecutables
│   └── data/                       # Datos de prueba
│
└── frontend/                       # Aplicacion Next.js
    ├── app/                        # Pages (Next.js 15 App Router)
    │   ├── page.tsx                # Extraccion
    │   ├── dashboard/              # Dashboard
    │   └── layout.tsx              # Layout con sidebar
    ├── components/                 # Componentes React + shadcn/ui
    │   ├── sidebar.tsx             # Navegacion
    │   ├── extraction-table.tsx    # Tabla de extracciones
    │   ├── file-viewer.tsx         # Visor de PDF e imagenes
    │   ├── file-upload.tsx         # Componente de subida
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

- *Parser* unificado (*StatementParser*) basado en vision con *Claude Haiku 4.5*
- Soporte para PDFs e imagenes (JPG/PNG)
- API REST con *endpoints* de extraccion, submission, logs, metricas y metricas de API
- *Frontend* con extraccion, visor de archivos y *dashboard*
- Base de datos *PostgreSQL* con migraciones *Alembic*
- Seguimiento de llamadas a la API (*ApiCallLog*)
- Sistema de metricas de precision y metricas de API
- Visor de PDF e imagenes con controles avanzados
- Tabla de extracciones con busqueda y paginacion
- Servicios divididos: `ExtractionService`, `SubmissionService`, `MetricsService`, `ApiMetricsService`
- CI con *GitHub Actions*, despliegue en *Railway* + *Vercel*

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
uv sync                # Instalar dependencias
cp .env.example .env   # Configurar API keys
uvicorn src.main:app --reload
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
