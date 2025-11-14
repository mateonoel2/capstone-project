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

## Estructura del Proyecto

```
capstone-project/
├── backend/                        # Código del backend
│   ├── application/                # API REST + Database
│   ├── src/                        # Código fuente
│   │   ├── extraction/             # Parsers (9 implementaciones)
│   │   ├── preprocessing/          # Limpieza y OCR
│   │   └── experiments/            # ExperimentRunner
│   ├── scripts/                    # Scripts ejecutables
│   └── data/                       # Datos y base de datos SQLite
│
└── frontend/                       # Aplicación Next.js
    ├── app/                        # Pages (Next.js 13+)
    ├── components/                 # Componentes React + shadcn/ui
    └── lib/                        # API client + Utils
```

---

## Documentación por Tema

### Arquitectura y Diseño
- [📖 Diseño de Solución](Diseño-de-Solución) - Arquitectura completa del producto de datos

### *Backend*
- [⚙️ Guía de *Scripts*](Guía-de-Scripts) - Cómo usar los *scripts* del proyecto
- [🔬 Comparación de *Parsers*](Comparación-de-Parsers) - Análisis de 9 *parsers* diferentes
- [🔄 *Workflow* Semanal](Workflow-Semanal) - Proceso de actualización de datos

### *Frontend*
- [🚀 Configuración del *Frontend*](Configuración-Frontend) - *Setup* completo
- [💻 Resumen de Implementación](Resumen-Implementación) - Detalles técnicos
- [📊 *Dashboard*](Dashboard) - Métricas y análisis
- [🆕 Últimas Actualizaciones](Últimas-Actualizaciones) - Cambios recientes

---

## Enlaces Útiles

- [Repositorio Principal](https://github.com/mateonoel2/capstone-project)
- [*Issues*](https://github.com/mateonoel2/capstone-project/issues)
- [*Pull Requests*](https://github.com/mateonoel2/capstone-project/pulls)

---

**Nota**: Todos los documentos están en español con términos técnicos en inglés en cursiva.

