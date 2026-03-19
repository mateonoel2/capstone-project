# Análisis de Costos por Solicitud de Extracción

## Stack actual

| Servicio | Propósito | Costo actual |
|----------|-----------|-------------|
| **Claude API (Haiku 4.5)** | Extracción de documentos + AI assistant | Por uso |
| **Railway** | Backend (FastAPI) + PostgreSQL | Gratis (free tier) |
| **Vercel** | Frontend (Next.js) | Gratis (free tier) |
| **Tigris (S3-compatible)** | Almacenamiento de archivos | Gratis (incluido en Railway) |

> Railway y Vercel están en free tier por ahora. Los costos de infraestructura aplican solo cuando se superen los límites gratuitos.

---

## 1. Claude API — Costo principal

**Modelo:** `claude-haiku-4-5-20251001`

| Concepto | Precio |
|----------|--------|
| Input tokens | $1.00 / millón de tokens |
| Output tokens | $5.00 / millón de tokens |

### Extracción de imágenes (JPG/PNG)

Se realizan **2 llamadas** a Claude por imagen: verificación de orientación + extracción.

| Llamada | Input tokens | Output tokens | Costo |
|---------|-------------|---------------|-------|
| Orientation check | ~1,650 | ~50 | ~$0.0019 |
| Extracción | ~1,900 | ~200 | ~$0.0029 |
| **Total por imagen** | | | **~$0.005** |

### Extracción de PDFs

Claude convierte cada página del PDF en imagen (~1,500 tokens/página). **1 sola llamada**.

| Escenario | Páginas | Input tokens | Costo estimado |
|-----------|---------|-------------|----------------|
| PDF chico (carátula) | 1-2 | ~3,300 | **~$0.004** |
| PDF mediano | 10 | ~15,300 | **~$0.016** |
| PDF grande | 50 | ~75,300 | **~$0.077** |
| PDF máximo (~20MB) | 100 | ~150,300 | **~$0.15** |

> Nota: Claude soporta máximo 100 páginas por PDF.

### AI Assistant (costos one-time por extractor)

Estas llamadas ocurren solo al **crear o editar** un extractor, no por cada extracción.

| Operación | Input tokens | Output tokens | Costo estimado |
|-----------|-------------|---------------|----------------|
| Generar schema | ~500 | ~500 | ~$0.003 |
| Generar prompt | ~600 | ~500 | ~$0.003 |
| Refinar prompt | ~800 | ~500 | ~$0.004 |

---

## 2. S3 Storage (Tigris)

Actualmente incluido en Railway free tier. Costos futuros de referencia:

| Concepto | Costo |
|----------|-------|
| PUT (upload) | ~$0.000005/request |
| GET (download) | ~$0.0000004/request |
| Almacenamiento | ~$0.023/GB/mes |
| **Total por request** | **< $0.001 (despreciable)** |

Un archivo de 20MB almacenado cuesta ~$0.0005/mes.

---

## 3. Infraestructura (post free-tier)

Estos costos aplican solo cuando se excedan los free tiers.

| Servicio | Costo mensual estimado | A 1,000 req/mes | A 10,000 req/mes |
|----------|----------------------|-----------------|------------------|
| Railway (backend + DB) | ~$5-20/mes | ~$0.02/req | ~$0.002/req |
| Vercel (frontend) | ~$0-20/mes | ~$0.02/req | ~$0.002/req |
| **Total infra** | **~$10-40/mes** | **~$0.04/req** | **~$0.004/req** |

---

## Resumen: Costo total por solicitud

### Fase actual (free tiers activos)

Solo se paga Claude API:

| Escenario | Costo por solicitud |
|-----------|-------------------|
| Imagen simple | **~$0.005** |
| PDF 1-2 páginas | **~$0.004** |
| PDF 10 páginas | **~$0.016** |
| PDF 50 páginas | **~$0.077** |
| PDF 100 páginas (~20MB) | **~$0.15** |

### Fase futura (sin free tiers, ~1,000 req/mes)

| Escenario | Claude API | Infra | **Total** |
|-----------|-----------|-------|-----------|
| Imagen simple | $0.005 | $0.04 | **~$0.045** |
| PDF 1-2 páginas | $0.004 | $0.04 | **~$0.044** |
| PDF 10 páginas | $0.016 | $0.04 | **~$0.056** |
| PDF 50 páginas | $0.077 | $0.04 | **~$0.117** |
| PDF 100 páginas (~20MB) | $0.15 | $0.04 | **~$0.19** |

---

## Precio sugerido por solicitud

Margen recomendado: **3x-5x** sobre costo total (fase futura).

| Escenario | Costo | Precio 3x | Precio 5x |
|-----------|-------|-----------|-----------|
| Documento típico (1-10 págs) | ~$0.05 | **$0.15** | **$0.25** |
| Documento grande (50+ págs) | ~$0.12 | **$0.36** | **$0.60** |
| Worst case (100 págs, 20MB) | ~$0.19 | **$0.57** | **$0.95** |

### Modelos de pricing sugeridos

1. **Precio flat:** $0.15 - $0.25 USD por extracción (cubre ~80% de casos con buen margen)
2. **Por tiers:**
   - Documentos ≤20 páginas: $0.15
   - Documentos >20 páginas: $0.50
3. **Paquetes de créditos:**
   - 100 extracciones: $15-20 USD
   - 500 extracciones: $60-80 USD
   - 1,000 extracciones: $100-150 USD

---

## Consideraciones

- **Cambio de modelo:** Migrar a Sonnet multiplica el costo de API ~3x. Migrar a Opus ~15x.
- **Orientation check:** Solo aplica a imágenes, no a PDFs. Se podría eliminar si los documentos siempre llegan bien orientados.
- **Archivos de 20MB:** El límite práctico es 100 páginas (límite de Claude), no el tamaño del archivo.
- **Volumen:** A mayor volumen, el costo de infra por request baja drásticamente. El costo de API se mantiene lineal.
