# Recomendaciones de Generalizacion

**Ultima actualizacion:** Marzo 2026

Este documento fue originalmente redactado como hoja de ruta para evolucionar el proyecto desde una herramienta especifica para estados de cuenta bancarios hacia un *framework* general de extraccion de documentos. **La mayoria de las recomendaciones principales ya fueron implementadas** como parte del MVP.

---

## Recomendaciones implementadas

### 1. Sistema de extraccion dirigido por *schemas*
**Estado: Completado**

El sistema ahora soporta extractores configurables donde cada tipo de documento se define mediante un *schema* JSON, un *prompt* de extraccion en lenguaje natural y un modelo asociado. Los usuarios crean extractores a traves de un *wizard* multi-paso en `/extractors/new`, con asistencia de IA para generar *schemas* y *prompts* automaticamente.

### 2. Capa de abstraccion de *parsers*
**Estado: Completado**

Los *parsers* fueron reemplazados por un unico `DocumentExtractor` basado en vision que retorna datos estructurados genericos via `ExtractionOutput` (*Pydantic* + *LangChain structured output*). El `BaseExtractor` ABC define la interfaz comun.

### 3. Soporte para multiples tipos de documentos
**Estado: Completado**

La API acepta PDFs e imagenes (JPG/PNG) y el *endpoint* `POST /extraction/extract` recibe un `extractor_config_id` que determina el *schema* y *prompt* a utilizar. Cada usuario define sus propios extractores sin cambios de codigo.

### 4. *Framework* de experimentacion y pruebas A/B
**Estado: Completado**

El sistema soporta versionado de extractores con seleccion aleatoria entre versiones activas durante la extraccion. Los resultados se registran con referencia a la version utilizada, habilitando comparaciones empiricas en produccion. Complementariamente, las extracciones de prueba (`POST /extractors/test-extract`) permiten validar configuraciones antes de activarlas.

### 5. Metricas de evaluacion estandarizadas
**Estado: Completado**

Se implemento una evaluacion rigurosa con *accuracy* total, *accuracy* condicional y similaridad textual por campo, con validacion multinivel para Titular (exacta, parcial, difusa) y estricta para CLABE. Ver [Evaluacion y Metricas](Evaluación-y-Métricas).

### 6. Planteamiento generalizado del problema
**Estado: Completado**

El proyecto fue replanteado como "sistema de extraccion de documentos configurable" en lugar de "extractor de estados de cuenta bancarios", con la tesis documentando esta evolucion.

---

## Recomendaciones pendientes

A partir de las conclusiones de la tesis y las limitaciones identificadas durante la evaluacion experimental:

### 1. Estandarizar la creacion de extractores
- Plantillas reutilizables para tipos de documentos comunes (facturas, identificaciones, comprobantes)
- Interfaces declarativas que reduzcan el esfuerzo de definir *schemas* y *prompts*
- Bibliotecas de *prompts* validados por tipo de documento

### 2. Optimizar costos de la API
- Reduccion de tokens de entrada (enviar solo paginas relevantes en lugar del PDF completo)
- Seleccion automatica de modelo segun complejidad del documento
- Fortalecimiento de validaciones post-extraccion con reglas deterministicas (los experimentos mostraron que las reglas solas alcanzan 4.7–12.6% pero complementan eficazmente al LLM en validacion)

### 3. Validacion externa e integridad
- Integracion con APIs bancarias para verificar existencia/vigencia de CLABEs
- Mecanismos de deteccion de fraude y autenticidad de documentos
- Validacion cruzada de campos (ej: banco inferido de los primeros digitos de la CLABE)

### 4. Monitoreo avanzado
- Filtros avanzados en el *dashboard* (por banco, periodo, extractor)
- Exportacion de metricas y reportes
- Alertas personalizadas cuando la precision cae por debajo de umbrales
- Analisis detallado por institucion bancaria

### 5. Manejo de casos extremos
- PDFs encriptados o protegidos
- Documentos manuscritos o de muy baja calidad
- Documentos con orientaciones no estandar (parcialmente resuelto con deteccion de rotacion)
- Formatos bancarios con ambiguedad inherente (como BanBajio, donde CLABE y numero de cuenta tienen formato similar)

---

## Limitaciones identificadas en la tesis

- Cada nuevo tipo de documento requiere definicion, ajuste y validacion del *schema*/*prompt*/modelo (costo de configuracion)
- Dependencia de APIs externas de modelos de lenguaje (costo, latencia, disponibilidad)
- El desempeno esta condicionado por la calidad de los *schemas* definidos
- No incorpora validacion contra sistemas bancarios ni deteccion de fraude
- El *dashboard* se limita a metricas agregadas basicas
