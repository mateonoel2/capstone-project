# Recomendaciones de Generalización para el *Capstone*

## Problema Actual: Demasiado Específico al Dominio

El proyecto actual es **demasiado limitado** para un *capstone* porque:
- Solo maneja estados de cuenta bancarios mexicanos
- Extrae solo 3 campos fijos (titular, CLABE, nombre del banco)
- Contiene nombres de bancos y lógica específica del país codificados directamente
- Carece de extensibilidad a otros tipos de documentos

## Solución Propuesta: *Framework* General de Extracción de Información de Documentos

Transformar el proyecto en un **sistema de extracción de documentos configurable y dirigido por *schemas*** capaz de manejar múltiples tipos de documentos y esquemas de extracción.

---

## 1. Cambios Arquitectónicos Principales

### 1.1 Sistema de Extracción Dirigido por *Schemas*

**Estado Actual:**
- *Schema* fijo `BankAccount` con 3 campos
- Reglas de validación codificadas directamente (CLABE = 18 dígitos)
- Lógica específica del país incrustada en los *parsers*

**Cambio Propuesto:**
Crear un **sistema dinámico de *schemas*** donde los esquemas de extracción se definen como configuración:

```python
# Ejemplo: schemas/invoice_schema.yaml
document_type: "invoice"
fields:
  - name: "invoice_number"
    type: "string"
    validation: "regex:^INV-\\d+$"
    description: "Número de factura en formato INV-XXXXX"

  - name: "total_amount"
    type: "float"
    validation: "range:0.0:999999.99"
    description: "Monto total de la factura"

  - name: "vendor_name"
    type: "string"
    validation: "required"
    description: "Nombre del proveedor"

# Ejemplo: schemas/bank_statement_schema.yaml
document_type: "bank_statement"
fields:
  - name: "account_holder"
    type: "string"
    validation: "required"

  - name: "account_number"
    type: "string"
    validation: "regex:^\\d{18}$"

  - name: "bank_name"
    type: "string"
    validation: "enum:BBVA,SANTANDER,BANAMEX,..."
```

**Beneficios:**
- Soporte para múltiples tipos de documentos (facturas, recibos, contratos, estados de cuenta, etc.)
- No se requieren cambios en el código para agregar nuevos tipos de documentos
- Hace el sistema agnóstico al dominio
- Demuestra principios de ingeniería de software (configuración sobre código)

---

### 1.2 Capa de Abstracción de *Parsers*

**Estado Actual:**
- Los *parsers* retornan objetos `BankAccount`
- Cada *parser* tiene lógica específica de bancos incrustada

**Cambio Propuesto:**
Hacer que los *parsers* retornen **datos estructurados genéricos** basados en el *schema*:

```python
class BaseParser(ABC):
    @abstractmethod
    def parse_file(
        self,
        file_path: Path,
        schema: ExtractionSchema
    ) -> Dict[str, Any]:
        """
        Parsea archivo y retorna diccionario que coincide
        con los campos del schema.
        """
        pass
```

**Beneficios:**
- Los *parsers* se vuelven reutilizables entre tipos de documentos
- Clara separación de responsabilidades (*parsing* vs. validación)
- Más fácil de probar y mantener

---

### 1.3 Soporte para Múltiples Tipos de Documentos

**Estado Actual:**
- La API solo acepta PDFs para extracción de estados de cuenta
- *Endpoint* único: `/extraction/pdf`

**Cambio Propuesto:**
Soportar múltiples tipos de documentos con selección de *schema*:

```python
@router.post("/extract")
async def extract_document(
    file: UploadFile,
    document_type: str,  # "invoice", "receipt", "bank_statement", etc.
    schema_name: Optional[str] = None  # Schema personalizado opcional
):
    schema = load_schema(document_type, schema_name)
    result = parser.parse_file(file, schema)
    return validate_and_format(result, schema)
```

**Beneficios:**
- Demuestra aplicabilidad en el mundo real
- Muestra habilidades de diseño de sistemas
- Más impresionante para la evaluación del *capstone*

---

## 2. Investigación y Contribución Académica

### 2.1 *Framework* de Análisis Comparativo

**Mejora:** Hacer la comparación de *parsers* más rigurosa y académica:

1. **Métricas de Evaluación Estandarizadas:**
   - Precisión, *Recall*, *F1-score* por campo
   - Análisis de tiempo de procesamiento
   - Análisis de costos (costos de API vs. precisión)
   - Clasificación de tipos de error (campo faltante, formato incorrecto, alucinación)

2. **Conjunto de Datos de Referencia:**
   - Crear un conjunto de datos público de referencia (anonimizado)
   - Múltiples tipos de documentos
   - Anotaciones de *ground truth*
   - Documentar esto como contribución

3. **Análisis Estadístico:**
   - Intervalos de confianza
   - Pruebas de significancia estadística
   - Rendimiento según niveles de calidad del documento

**Beneficios:**
- Demuestra metodología de investigación
- Hace el proyecto académicamente riguroso
- Crea una contribución reutilizable para la comunidad

---

### 2.2 Investigación de Estrategia Híbrida de *Parsers*

**Estado Actual:**
- Existen múltiples *parsers* pero la selección es manual

**Cambio Propuesto:**
Implementar y evaluar **selección inteligente de *parsers***:

1. **Clasificación de Documentos:**
   - Clasificar tipo de documento automáticamente
   - Detectar calidad del documento (basado en texto vs. basado en imagen)
   - Identificar complejidad del *layout*

2. **Selección Adaptativa de *Parser*:**
   - Usar ML para seleccionar el mejor *parser* por documento
   - Métodos de *ensemble* (combinar múltiples *parsers*)
   - Enrutamiento basado en confianza

3. **Pregunta de Investigación:**
   - "¿Podemos predecir la estrategia óptima de extracción basándonos en las características del documento?"
   - Comparar *parser* fijo vs. selección adaptativa

**Beneficios:**
- Agrega componente de investigación en ML
- Más interesante para la evaluación del *capstone*
- Demuestra diseño avanzado de sistemas

---

## 3. Mejoras Técnicas

### 3.1 Arquitectura de *Plugins*

**Estado Actual:**
- Los *parsers* están codificados directamente en el código fuente

**Cambio Propuesto:**
Hacer los *parsers* cargables como *plugins*:

```python
# parsers/registry.py
class ParserRegistry:
    def register_parser(self, name: str, parser_class: Type[BaseParser]):
        """Registra un nuevo parser dinámicamente"""

    def get_parser(self, name: str) -> BaseParser:
        """Obtiene parser por nombre"""

    def list_parsers(self) -> List[str]:
        """Lista todos los parsers disponibles"""
```

**Beneficios:**
- Extensibilidad sin cambios en el código
- Demuestra arquitectura de software avanzada
- Permite contribuciones de *parsers* de terceros

---

### 3.2 *Framework* de Validación

**Estado Actual:**
- Lógica de validación dispersa entre *parsers*

**Cambio Propuesto:**
Sistema de validación centralizado:

```python
class FieldValidator:
    def validate(self, value: Any, field_config: FieldConfig) -> ValidationResult:
        """
        Valida valor extraído contra configuración del campo.
        Soporta: regex, rango, enum, validadores personalizados
        """
```

**Beneficios:**
- Lógica de validación reutilizable
- Manejo consistente de errores
- Más fácil agregar nuevas reglas de validación

---

### 3.3 *Framework* de Experimentación y Pruebas A/B

**Mejora:** Agregar experimentación en producción:

```python
@router.post("/extract")
async def extract_with_experiment(
    file: UploadFile,
    document_type: str,
    enable_experiment: bool = False  # Ejecutar múltiples parsers para comparación
):
    if enable_experiment:
        # Ejecutar múltiples parsers y comparar
        results = run_experiment(file, document_type)
        return ExperimentResponse(results)
    else:
        # Ruta de producción
        return extract_document(file, document_type)
```

**Beneficios:**
- Mejora continua en producción
- Patrón de sistema ML del mundo real
- Demuestra ingeniería de ML en producción

---

## 4. Mejoras en Documentación y Presentación

### 4.1 Planteamiento Claro del Problema

**Replantear el problema** de:
- "Extraer información bancaria de estados de cuenta mexicanos"
- A: "Construir un sistema de extracción de información de documentos de propósito general que pueda configurarse para cualquier tipo de documento y *schema*"

### 4.2 Estructura de Artículo Académico

Organizar la documentación como:
1. **Introducción:** Problema de digitalización de documentos, desafíos de extracción de información
2. **Trabajo Relacionado:** Revisión de métodos de extracción (*regex*, OCR, LLMs, modelos de visión)
3. **Metodología:** *Framework* de comparación de *parsers*
4. **Experimentos:** Resultados del *benchmark* entre tipos de documentos
5. **Discusión:** Compensaciones, limitaciones, trabajo futuro
6. **Conclusión:** Contribuciones e impacto

### 4.3 Escenarios de Demostración

Mostrar el sistema funcionando con **múltiples tipos de documentos**:
- Estados de cuenta bancarios (actual)
- Facturas
- Recibos
- Registros médicos (anonimizados)
- Contratos legales (anonimizados)

---

## 5. Hoja de Ruta de Implementación

### Fase 1: Sistema de *Schemas* (Semana 1-2)
- [ ] Crear formato de definición de *schemas* YAML/JSON
- [ ] Construir cargador y validador de *schemas*
- [ ] Refactorizar *parsers* para usar *schemas*
- [ ] Actualizar API para aceptar parámetro *document_type*

### Fase 2: Soporte Multi-Documento (Semana 3-4)
- [ ] Crear 2-3 *schemas* adicionales de documentos (factura, recibo)
- [ ] Probar *parsers* con nuevos tipos de documentos
- [ ] Actualizar *frontend* para soportar selección de *schema*
- [ ] Crear conjuntos de datos de ejemplo para cada tipo

### Fase 3: Mejora de Investigación (Semana 5-6)
- [ ] Implementar métricas de evaluación estandarizadas
- [ ] Crear conjunto de datos de referencia
- [ ] Ejecutar comparación integral de *parsers*
- [ ] Análisis estadístico y visualización

### Fase 4: Funcionalidades Avanzadas (Semana 7-8)
- [ ] Arquitectura de *plugins* para *parsers*
- [ ] Sistema de clasificación de documentos
- [ ] Selección adaptativa de *parsers*
- [ ] *Framework* de experimentación en producción

### Fase 5: Documentación (Semana 9-10)
- [ ] Escribir artículo de estilo académico
- [ ] Crear videos de demostración
- [ ] Documentar API y arquitectura
- [ ] Preparar presentación

---

## 6. Métricas Clave de Éxito

### Métricas Técnicas
- Soportar al menos 3 tipos diferentes de documentos
- Dirigido por *schemas* (sin cambios de código para nuevos tipos)
- Comparación de *parsers* con rigor estadístico
- API lista para producción con manejo adecuado de errores

### Métricas Académicas
- Pregunta de investigación y metodología claras
- Experimentos reproducibles
- Contribución de conjunto de datos de referencia
- Análisis comparativo con significancia estadística

### Métricas de Presentación
- Planteamiento claro del problema (no específico al dominio)
- Demuestra principios de ingeniería de software
- Muestra contribución de investigación en ML/NLP
- Aplicabilidad en el mundo real

---

## 7. Estrategia de Migración

No es necesario descartar el trabajo actual. Así se puede migrar:

1. **Mantener la funcionalidad existente de estados de cuenta** como un tipo de documento
2. **Refactorizar gradualmente** los *parsers* para usar el sistema de *schemas*
3. **Agregar nuevos tipos de documentos** incrementalmente
4. **Mantener compatibilidad hacia atrás** durante la transición

La extracción de estados de cuenta se convierte en un **caso de uso** en lugar de ser el proyecto completo.

---

## Conclusión

Al generalizar el proyecto, se transforma de:
- Una herramienta específica para estados de cuenta bancarios mexicanos
- A: Un *framework* de extracción de documentos de propósito general con contribuciones de investigación

Esto lo hace mucho más adecuado para un proyecto *capstone* manteniendo todo el trabajo técnico actual y agregando valor significativo a través de la generalización y el rigor de investigación.
