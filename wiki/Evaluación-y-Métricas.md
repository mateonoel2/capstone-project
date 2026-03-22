# Evaluacion y Metricas

**Ultima actualizacion:** Marzo 2026

Este documento describe la metodologia de evaluacion utilizada para validar el sistema de extraccion, incluyendo el *dataset*, las metricas empleadas, los resultados por fase y el analisis de errores.

---

## *Dataset*

- **308 registros** originales de cuentas bancarias de instituciones educativas mexicanas
- **183 documentos** utilizados en fases 1 y 2 (con URL valida, formato PDF y *ground truth* completo)
- **176 documentos** utilizados en fase 3 (tras remover 8 documentos invalidos y corregir 15 entradas del *ground truth*)
- **11 instituciones bancarias** representadas: BBVA, Banorte, Santander, Banamex, Scotiabank, Bajio, HSBC, Afirme, Banregio, Mifel, Bmonex
- **97.5%** de registros con caratula bancaria descargada exitosamente

---

## Metricas utilizadas

### *Accuracy* total
Proporcion de extracciones correctas respecto al total de documentos con *ground truth* disponible. Incluye como errores tanto extracciones incorrectas como casos donde el modelo no produjo respuesta.

### *Accuracy* condicional
Excluye los casos donde el modelo no intento la extraccion. Refleja la capacidad del modelo cuando logra identificar el campo en el documento.

### Similaridad textual
Calculada mediante `SequenceMatcher` entre el valor predicho y el valor real (escala 0–1). Util para el campo Titular donde diferencias de formato no necesariamente invalidan el resultado.

---

## Validacion por campo

### Titular
Validacion multinivel con normalizacion previa (descomposicion *Unicode NFKD*, estandarizacion de sufijos legales como `A.C.` → `AC`, `S.A. DE C.V.` → `SA DE CV`):

1. **Coincidencia exacta** tras normalizacion
2. **Coincidencia parcial**: ≥70% de palabras del *ground truth* presentes
3. **Coincidencia difusa**: ≥85% similaridad textual

### CLABE
Comparacion estricta: coincidencia exacta de 18 digitos tras eliminar espacios y caracteres no numericos.

### Banco
Normalizacion a mayusculas, acepta variaciones comunes del nombre.

---

## Resultados por fase

| Fase | Enfoque | Titular | CLABE | Banco | Promedio |
|------|---------|---------|-------|-------|----------|
| 1 | *Regex* | 0.5% | 0.0% | 13.7% | 4.7% |
| 1 | *PDFPlumber* | 2.2% | 0.0% | 13.1% | 5.1% |
| 1 | *Regex* + OCR | 2.2% | 0.0% | 34.4% | 12.2% |
| 1 | *PDFPlumber* + OCR | 3.8% | 0.0% | 33.9% | 12.6% |
| 2 | Claude + texto extraido | 30.6% | 0.0% | 18.0% | 16.2% |
| 2 | Claude + vision (imagen) | 65.0% | 53.0% | 45.4% | 54.5% |
| 2 | Claude + OCR (*Tesseract*) | 68.9% | 80.9% | 41.5% | 63.8% |
| **3** | **Claude + PDF directo** | **92.8%** | **90.9%** | **96.6%** | **93.4%** |

---

## Resultados detallados de la fase 3

### Precision por campo (176 PDFs)

| Campo | n | Acc. Total | Acc. Cond. | Correctos | Sim. Media |
|-------|---|------------|------------|-----------|------------|
| Titular | 175 | 92.8% | 94.9% | 167/175 | 0.93 |
| CLABE | 176 | 90.9% | --- | 160/176 | 0.91 |
| Banco | 85 | 96.6% | 98.8% | 84/85 | 0.99 |

### Desglose de tipos de coincidencia (Titular)

| Tipo | Cantidad | Descripcion |
|------|----------|-------------|
| `exact_match` | 118 | Coincidencia exacta tras normalizacion |
| `partial_match` | 41 | ≥70% de palabras del *GT* presentes |
| `fuzzy_match` | 8 | ≥85% similaridad textual |
| `no_match` | 9 | Extraccion incorrecta |
| `not_extracted` | 4 | Modelo devolvio "Unknown" |

### Precision por banco (instituciones con ≥3 documentos)

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

**Observaciones:**
- HSBC, Afirme: 100% en los tres campos
- BanBajio: 0% en CLABE — el formato presenta la CLABE junto al numero de cuenta con formato y longitud similares, provocando que el modelo extraiga el campo equivocado
- Banorte: 67% en CLABE — CLABEs con espacios entre grupos de digitos y formatos tabulares que confunden numero de cuenta con CLABE

---

## Analisis de errores en CLABE

Distribucion bimodal de errores:

- **1–7 digitos diferentes**: lecturas cercanas donde el modelo identifico el campo correcto pero leyo mal algunos digitos. Limitaciones de la capacidad de vision del modelo, dificilmente se resuelven con cambios de *prompt*
- **10–18 digitos diferentes**: extraccion de un campo completamente distinto (numero de cuenta o de cliente). Confusiones de campo mitigables con instrucciones mas especificas o validaciones post-extraccion

### Impacto acumulado de mejoras sobre CLABE

| Variante | Correctos | Total | *Accuracy* |
|----------|-----------|-------|-----------|
| Base (sin mejoras) | 147 | 182 | 80.8% |
| + Correccion de *ground truth* | 150 | 176 | 85.2% |
| + *Prompt* reforzado | 156 | 176 | 88.6% |
| + Validacion post-extraccion | 158 | 176 | 89.8% |
| + Deteccion de orientacion + *retry* | 160 | 176 | 90.9% |

---

## Rendimiento y costo

### Tiempo de procesamiento
- **Mediana:** 1.9 segundos por archivo
- **Media:** 2.6 segundos
- **Maximo:** 15.3 segundos
- **85%** procesados en <4 segundos
- Valores atipicos: PDFs de multiples paginas o documentos con mecanismo de *retry*

### Costo (Claude Haiku 4.5)
- *Input tokens* promedio por archivo: ~13,500
- *Output tokens* promedio por archivo: ~100
- **Costo promedio por archivo:** ~$0.011 USD
- **Costo total (176 archivos):** ~$2.03 USD
- **Costo con *retry* (~15% archivos):** ~$2.20 USD

---

## Conclusiones experimentales

1. **El enfoque de PDF directo es superior**: elimina etapas intermedias de OCR/conversion, reduce la superficie de error. La mejora mas significativa fue en Banco (41.5% → 96.6%), confirmando que el acceso simultaneo a contenido textual y visual es fundamental
2. **El diseño del *prompt* es determinante**: el *prompt* generico alcanzo 80.8% en CLABE; tras instrucciones de desambiguacion, subio a 90.9%. Sin embargo, ciertos formatos (BanBajio) resisten todas las mejoras de *prompt*
3. **No existe un *prompt* universal**: la variabilidad por banco (0%–100% en CLABE) motivo la decision de implementar extractores configurables
