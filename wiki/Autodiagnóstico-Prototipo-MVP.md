# Autodiagnóstico: Transición de Prototipo a MVP

Curso: *Capstone Project* II
Maestría en Ciencia de Datos e IA — 2026

---

**NOTA:** Este documento es un ejemplo completamente ficticio y sirve únicamente como guía de cómo llenar la plantilla. No debe copiarse literalmente para los proyectos reales.

---

## Índice

1. Información básica del equipo
2. Estado actual del prototipo

---

## 1. Información básica del equipo

**Nombre del proyecto**
Extracción de Estados de Cuenta Bancarios

**Nombre del equipo**
[Nombre del Equipo]

**Dominio / Industria**
Validación de documentos – *Fintech*

**Problema que aborda**
Alta demora en la revisión manual de carátulas bancarias para activación de cuentas en colegios, con riesgo de errores humanos en la extracción de datos clave.

---

## 2. Estado actual del prototipo

### ¿Qué demuestra bien nuestro prototipo?

- **Flujo *end-to-end* funcional**: El sistema procesa documentos PDF de carátulas bancarias desde la carga hasta la extracción de datos sin intervención manual intermedia.
- **Extracción automática de datos clave**: Logra extraer consistentemente los tres campos principales (titular, CLABE y banco) de documentos reales.
- **Múltiples estrategias de *parsing***: Implementa y compara diferentes enfoques (LLM, *regex*, OCR) permitiendo elegir la mejor técnica según el caso.
- **Procesamiento de datos reales**: Ha sido probado con más de 300 documentos reales de la plataforma, demostrando viabilidad técnica.
- **Sistema de métricas y validación**: Incluye medición de precisión por campo y capacidad de corrección manual cuando es necesario.

### Supuestos críticos no validados

| Supuesto | Por qué es crítico | Si es falso |
|----------|-------------------|-------------|
| Los documentos procesados representan adecuadamente la variedad futura de formatos y calidades | El sistema depende de patrones aprendidos de datos históricos | El modelo pierde precisión con documentos no vistos durante el entrenamiento |
| El sistema puede extenderse fácilmente a otros tipos de documentos financieros | Limita el valor a largo plazo del *framework* desarrollado | Se requeriría reimplementación completa para documentos como facturas o contratos |
| Los usuarios (equipo de validación) confiarán en las recomendaciones automáticas | Sin adopción no hay reducción real del tiempo de procesamiento | El prototipo no genera impacto operativo significativo |
| La calidad de OCR es suficiente para documentos escaneados de baja resolución | Muchos documentos reales llegan en formatos subóptimos | El sistema falla en casos reales más allá del entorno controlado |
