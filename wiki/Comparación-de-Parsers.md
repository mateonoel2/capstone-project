# Comparación de *Parsers* de Estados de Cuenta Bancarios - 183 PDFs Completos

**Fecha de Prueba:** 7 de noviembre de 2025  
***Dataset*:** 183 estados de cuenta bancarios mexicanos (mezcla de PDFs basados en texto e imagen)  
***Ground Truth*:** bank_accounts_filtered.csv

---

## Resultados Generales (Ordenados por Precisión Promedio)

### Con *Fallback* de OCR (ACTUALIZADO - 7 de noviembre de 2025)

| Rango | *Parser* | Titular | CLABE | Banco | Promedio | Velocidad | Costo |
|------|--------|-------|-------|------|---------|-------|------|
| 1 | ***Claude OCR*** | 68.9% (126/183) | **80.9% (148/183)** | 41.5% (76/183) | **63.8%** | 9 min | $ |
| 2 | ***Claude Vision*** | **65.0% (119/183)** | 53.0% (97/183) | 45.4% (83/183) | **54.5%** | ~10 min | $$ |
| 3 | ***Claude Text*** | 30.6% (56/183) | 0.0% (0/183) | 18.0% (33/183) | **16.2%** | 2.7 min | $ |
| 4 | ***PDFPlumber* + OCR** | 3.8% (7/183) | 0.0% (0/183) | 33.9% (62/183) | **12.6%** | 4.2 min | GRATIS |
| 5 | ***Regex* + OCR** | 2.2% (4/183) | 0.0% (0/183) | 34.4% (63/183) | **12.2%** | 4.0 min | GRATIS |
| 6 | ***Hybrid*** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | ~25 seg | GRATIS* |

\* *Hybrid* estaba usando *fallback* de *PDFPlumber* (*Ollama* no ejecutándose)

### Sin *Fallback* de OCR (Resultados Originales)

| Rango | *Parser* | Titular | CLABE | Banco | Promedio | Velocidad |
|------|--------|-------|-------|------|---------|-------|
| 1 | ***PDFPlumber*** | 2.2% (4/183) | 0.0% (0/183) | 13.1% (24/183) | **5.1%** | 23 seg |
| 2 | ***Regex*** | 0.5% (1/183) | 0.0% (0/183) | 13.7% (25/183) | **4.7%** | 10 seg |

---

## Hallazgos Clave

### 1. **Ganador: *Claude OCR* (*Tesseract* + *Claude Haiku*)**
- **Mejor extracción de CLABE**: 80.9% (148/183) - El campo más crítico
- **Mejor extracción de Titular**: 68.9% (126/183)
- **Opción pagada más económica**: OCR gratuito + API de *Claude Text*
- **Procesó TODOS los PDFs**: 183/183 exitosos (0 errores)
- **Maneja PDFs de texto e imagen**
- **Velocidad razonable**: 9 minutos para 183 PDFs (~3s por PDF)

### 2. **Subcampeón: *Claude Vision***
- Buen rendimiento general (54.5% promedio)
- Mejor extracción de Titular (65.0%)
- Maneja bien PDFs de imagen
- Más costoso (API de *Vision* cuesta ~3x API de texto)
- Menor precisión de CLABE (53% vs 80.9%)

### 3. ***Fallback* de OCR: Mejora importante para *parsers* gratuitos**
- ***Regex* + OCR**: 4.7% → 12.2% (mejora de 2.6x)
  - Extracción de banco saltó de 13.7% a 34.4% (+150%)
  - Velocidad aumentó de 10s a 4 min (debido a OCR en 60% de PDFs)
- ***PDFPlumber* + OCR**: 5.1% → 12.6% (mejora de 2.5x)
  - Extracción de banco saltó de 13.1% a 33.9% (+160%)
  - Velocidad aumentó de 23s a 4.2 min
- **Aún 0% CLABE**: Los patrones *regex* no pueden interpretar texto OCR tan bien como los *LLMs*

### 4. **Por qué dominan los *LLMs*: La interpretación de texto importa**
- **Modelos *Claude*** extraen CLABEs de texto OCR desordenado: 80.9% (OCR), 53% (*Vision*)
- **Patrones *Regex*** fallan en artefactos de OCR: 0% CLABE a pesar de tener el texto
- El texto OCR tiene problemas de espaciado, errores de formato y artefactos que rompen *regex*
- Los *LLMs* pueden entender contexto y corregir errores de OCR

---

## Desglose Detallado

### Extracción de CLABE (Campo Más Crítico)
1. ***Claude OCR***: 80.9%
2. *Claude Vision*: 53.0%
3. TODOS LOS DEMÁS: 0.0%

**Ganador: *Claude OCR* por un margen enorme**

### Extracción de Titular
1. ***Claude OCR***: 68.9%
2. *Claude Vision*: 65.0%
3. *Claude Text*: 30.6%
4. Otros: <3%

### Extracción de Nombre del Banco
1. *Claude Vision*: 45.4%
2. ***Claude OCR***: 41.5%
3. *Claude Text*: 18.0%
4. Otros: ~13%

---

## Análisis de Costos

### Estimaciones de Costo por PDF (aproximado)

| *Parser* | Costo por PDF | Costo por 183 PDFs |
|--------|--------------|-------------------|
| *Regex* | $0 | $0 |
| *PDFPlumber* | $0 | $0 |
| *Hybrid* | $0* | $0* |
| ***Claude Text*** | ~$0.001 | ~$0.18 |
| ***Claude OCR*** | ~$0.001 | ~$0.18 |
| ***Claude Vision*** | ~$0.003-0.005 | ~$0.55-0.90 |

\* Asumiendo que *Ollama* se ejecuta localmente (gratuito)

***Claude OCR* proporciona la mejor relación precisión/costo**

---

## Comparación de Velocidad

| *Parser* | Tiempo Total | Por PDF | Notas |
|--------|------------|---------|-------|
| *Regex* (sin OCR) | 10 seg | 0.05s | Solo funciona en PDFs de texto |
| *PDFPlumber* (sin OCR) | 23 seg | 0.13s | Solo funciona en PDFs de texto |
| ***Regex* + OCR** | 240 seg (4 min) | 1.3s | OCR en ~60% de PDFs |
| ***PDFPlumber* + OCR** | 252 seg (4.2 min) | 1.4s | OCR en ~60% de PDFs |
| *Claude Text* | 162 seg (2.7 min) | 0.89s | Solo funciona en PDFs de texto |
| ***Claude OCR*** | 549 seg (9 min) | 3.0s | Funciona en todos los PDFs |
| ***Claude Vision*** | ~600 seg (10 min) | 3.3s | Funciona en todos los PDFs |

---

## Recomendación

### **Usar *Claude OCR Parser* para Producción**

**Razones:**
1. **Mejor precisión de CLABE** (80.9%) - El campo más importante para banca
2. **Mejor precisión de Titular** (68.9%)
3. **Más confiable** - 0 errores en 183 PDFs
4. **Mejor eficiencia de costo** - Mismo precio que *Claude Text* pero 4x mejor precisión
5. **Maneja todos los tipos de PDF** - Tanto basados en texto como en imagen
6. **Velocidad razonable** - ~3 segundos por PDF

**Arquitectura:**

```
PDF → Tesseract OCR (GRATIS, local) → Claude 3.5 Haiku ($) → Datos Extraídos
```

**Cuándo considerar alternativas:**
- **La velocidad es crítica y precisión < 65% es aceptable**: Usar *Claude Vision*
- **Presupuesto cero y solo se necesitan nombres de banco**: Usar *PDFPlumber* + OCR (34% precisión de banco, pero 0% CLABE)
- **Quieres probar *LlamaParse***: Corregir primero los problemas de API, pero esperar costos altos (doble cargo de OCR + *LLM*)

### **Perspectiva Clave: Por Qué *Claude OCR* Domina**

La comparación revela una perspectiva crítica: **OCR solo no es suficiente**. Necesitas interpretación inteligente de texto:

1. ***Parsers* gratuitos con OCR** (*Regex*, *PDFPlumber*):
   - Pueden extraer texto de PDFs de imagen (vía *Tesseract*)
   - Fallan al interpretar texto OCR desordenado (0% CLABE)
   - Los patrones *regex* se rompen con artefactos de OCR (espaciado, formato)
   - Resultado: 12-13% precisión promedio

2. **Modelos *Claude* con OCR** (*Claude OCR*, *Claude Vision*):
   - Pueden extraer texto de PDFs de imagen
   - Pueden entender contexto y corregir errores de OCR
   - Extraen datos estructurados de texto desordenado
   - Resultado: 54-64% precisión promedio

**La capa de *LLM* es esencial para uso en producción.**

---

## Archivos de Resultados

### Resultados Originales (sin *fallback* de OCR):
- `bank_extraction_regex_parser_20251107_193815.csv` (4.7% prom)
- `bank_extraction_pdfplumber_parser_20251107_193849.csv` (5.1% prom)
- `bank_extraction_hybrid_parser_20251107_195150.csv` (5.1% prom)

### Resultados Mejorados (con *fallback* de OCR):
- `bank_extraction_regex_parser_20251107_200430.csv` (12.2% prom, +160%)
- `bank_extraction_pdfplumber_parser_20251107_200914.csv` (12.6% prom, +147%)

### *Parsers* Basados en *Claude*:
- `bank_extraction_claude_parser_20251107_194143.csv` (16.2% prom)
- `bank_extraction_claude_vision_parser_20251107_194930.csv` (54.5% prom)
- `bank_extraction_claude_ocr_parser_20251107_195118.csv` (63.8% prom - **GANADOR**)

---

## Fase 3: Enfoque PDF Directo (Marzo 2026)

A partir de la disponibilidad de procesamiento de documentos PDF como binarios en la API de Claude, se evaluo un cuarto enfoque: **enviar el PDF completo directamente al modelo sin conversion intermedia** a texto ni a imagen. Este enfoque elimina la dependencia de herramientas externas de preprocesamiento y simplifica la arquitectura.

### Resultados (176 PDFs depurados)

| Campo | *Accuracy* Total | *Accuracy* Cond. | Correctos | Similaridad |
|-------|-----------------|-----------------|-----------|-------------|
| **Titular** | 92.8% | 94.9% | 167/175 | 0.93 |
| **CLABE** | 90.9% | --- | 160/176 | 0.91 |
| **Banco** | 96.6% | 98.8% | 84/85 | 0.99 |

### Comparacion directa con Fase 2

| Campo | Fase 2 (Claude OCR) | Fase 3 (PDF directo) | Mejora |
|-------|---------------------|---------------------|--------|
| Titular | 68.9% | 92.8% | +23.9 pp |
| CLABE | 80.9% | 90.9% | +10.0 pp |
| Banco | 41.5% | 96.6% | **+55.1 pp** |

La mejora mas significativa fue en el campo Banco: al enviar el PDF directamente, el modelo procesa simultaneamente texto y elementos visuales (logotipos), resolviendo la limitacion del OCR que no podia reconocer el nombre del banco cuando aparecia como logotipo.

### Precision por banco

| Banco | n | Titular | CLABE | Banco |
|-------|---|---------|-------|-------|
| AFIRME | 3 | 100% | 100% | 100% |
| BAJIO | 3 | 100% | 0% | 100% |
| BANAMEX | 11 | 91% | 91% | 100% |
| BANORTE | 21 | 86% | 67% | 90% |
| BANREGIO | 5 | 100% | 60% | 100% |
| BBVA | 19 | 95% | 95% | 100% |
| HSBC | 6 | 100% | 100% | 100% |
| SANTANDER | 14 | 93% | 93% | 100% |
| SCOTIABANK | 4 | 75% | 50% | 75% |

### Analisis de errores en CLABE

Distribucion bimodal de errores:
- **1–7 digitos diferentes**: lecturas cercanas, limitaciones de vision del modelo. Dificiles de resolver con cambios de *prompt*
- **10–18 digitos diferentes**: confusion de campo (numero de cuenta vs CLABE). Mitigables con instrucciones especificas y validaciones post-extraccion

### Rendimiento
- **Mediana:** 1.9 segundos por archivo
- **Media:** 2.6 segundos
- **85%** procesados en <4 segundos
- **Costo promedio:** $0.011 USD por archivo

> Para el analisis completo de la metodologia de evaluacion, metricas y desglose de resultados, ver [Evaluacion y Metricas](Evaluación-y-Métricas).

---

## Estado Actual (Marzo 2026)

Los 3 *parsers* de *Claude* (OCR, Text, Vision) se unificaron en un unico `StatementExtractor` que envia el PDF directamente como documento binario al modelo, con *structured output*. El sistema ahora soporta extractores configurables con *schemas*, *prompts* y modelos personalizados. Cada extractor:
- Usa un modelo Claude configurable (por defecto *Haiku 4.5*) con `with_structured_output()` de *LangChain*
- Envia el PDF directamente al modelo como documento binario (sin conversion intermedia)
- Soporta PDFs e imagenes (JPG/PNG)
- Detecta automaticamente si el documento es valido para el tipo de extraccion (`is_valid_document`)
- Registra cada llamada en `api_call_logs` para monitoreo
- Soporta extracciones de prueba registradas en `test_extraction_logs`

## Recomendacion Actualizada

### **Usar enfoque de PDF directo para produccion**

**Razones:**
1. **Mejor precision en todos los campos** — 93.4% promedio vs 63.8% del anterior ganador (Claude OCR)
2. **Arquitectura mas simple** — Sin dependencias de OCR ni conversion a imagen
3. **Costo competitivo** — $0.011 USD por documento
4. **Velocidad rapida** — Mediana de 1.9 segundos
5. **Acceso a contenido visual** — Resuelve la extraccion de bancos por logotipo (96.6%)

**Arquitectura:**

```
PDF → Claude Haiku 4.5 (PDF directo) → Datos Extraidos (JSON estructurado)
```

**Limitaciones conocidas:**
- BanBajio: 0% CLABE (ambiguedad inherente del formato del documento)
- Documentos manuscritos o de muy baja calidad
- PDFs encriptados

---

## Impacto del *Fallback* de OCR

| *Parser* | Sin OCR | Con OCR | Mejora |
|--------|-------------|----------|-------------|
| ***Regex*** | 4.7% | 12.2% | **+160%** |
| ***PDFPlumber*** | 5.1% | 12.6% | **+147%** |

### Qué Cambió:
- Extracción de banco: ~13% → ~34% (mejora de 2.6x)
- Extracción de titular: Ligera mejora
- Extracción de CLABE: Aún 0% (*regex* no puede manejar artefactos de OCR)

### Por Qué CLABE Aún Falla:
El texto OCR tiene problemas que rompen patrones *regex*:
- Espaciado: `123 456 789 012 345 678` en lugar de `123456789012345678`
- Saltos de línea: CLABE dividido entre líneas
- Errores de OCR: `0` → `O`, `1` → `l`, etc.
- Contexto necesario: Los *LLMs* pueden encontrar y reconstruir CLABEs, *regex* no puede

**Conclusión**: Los *parsers* gratuitos mejoraron 2.5x con OCR, pero aún no pueden igualar a los *parsers* basados en *LLM* para uso en producción.

---

Generado: 7 de noviembre de 2025
Ultima Actualizacion: Marzo 2026 (Parsers unificados en `StatementExtractor`)
