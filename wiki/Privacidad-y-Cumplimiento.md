# Privacidad y Cumplimiento

**Ultima actualizacion:** Marzo 2026

El proyecto trabaja con datos personales y financieros, lo que exige un tratamiento responsable desde el diseno del sistema. Este documento describe el marco legal aplicable, las medidas de proteccion implementadas y las politicas de retencion y auditoria.

---

## Marco legal aplicable

| Regulacion | Descripcion |
|------------|-------------|
| **LFPDPPP** | Ley Federal de Proteccion de Datos Personales en Posesion de los Particulares. Establece principios para el tratamiento de datos personales en Mexico, incluyendo derechos ARCO (Acceso, Rectificacion, Cancelacion y Oposicion) |
| **INAI** | Lineamientos del Aviso de Privacidad. Especifica como informar a los usuarios sobre el uso de sus datos |
| **CNBV** | Estandares de seguridad de la Comision Nacional Bancaria y de Valores para informacion financiera sensible |

---

## Informacion Personal Identificable (PII)

### Alta sensibilidad
| Campo | Categoria | Medidas |
|-------|-----------|---------|
| CLABE | Datos financieros | Tokenizacion, cifrado en reposo |
| RFC/CURP | Identificador fiscal/personal | Enmascaramiento, acceso restringido |
| Owner (Titular) | Nombre completo | Anonimizacion, cifrado |
| Caratula (documento) | Documento bancario | Control de acceso, cifrado, URLs prefirmadas |

### Sensibilidad media
| Campo | Categoria | Medidas |
|-------|-----------|---------|
| school_id | Afiliacion institucional | Pseudonimizacion |
| Colegio | Nombre de institucion | Puede revelar ubicacion |
| banco | Institucion financiera | Dato semi-publico |

---

## Medidas de proteccion implementadas

### Cifrado
- **En transito:** HTTPS/TLS con cabeceras de seguridad (HSTS, X-Content-Type-Options, X-Frame-Options, CSP)
- **En reposo:** Cifrado a nivel de campo mediante Fernet (AES en modo CBC con HMAC-SHA256) para campos sensibles de los registros de extraccion

### Control de acceso
- **RBAC** (*Role-Based Access Control*) con tres roles: *user*, *admin*, *guest*
- Autenticacion via *GitHub OAuth* con *JWT* para el *backend*
- Tokens API con autenticacion *Bearer* para acceso programatico
- URLs prefirmadas con expiracion para acceso a documentos en S3

### Auditoria
- Registro automatico de accesos a *endpoints* sensibles (usuario, accion, IP, timestamp)
- Tabla `ai_usage_logs` para rastreo de uso de IA por usuario

---

## Anonimizacion para procesamiento con modelos

Dado que la solucion emplea modelos de lenguaje a traves de una API externa (Claude), el sistema incorpora un modulo de anonimizacion estructurada que transforma la PII antes de su uso en tareas de evaluacion o analisis:

```
Documento original → Extraccion de texto → Identificacion de PII → Reemplazo por tokens
```

| Texto original | Texto anonimizado |
|----------------|-------------------|
| `Titular: [NOMBRE COMPLETO]` | `Titular: [NOMBRE_PERSONA]` |
| `RFC: [13 CARACTERES]` | `RFC: [RFC_ID]` |
| `CLABE: [18 DIGITOS]` | `CLABE: [CLABE_18_DIGITOS]` |

El proceso preserva la estructura y formato del documento (longitud de campos, posicion espacial, elementos visuales como tablas y logotipos).

---

## Flujo de datos y controles de privacidad

1. **Fuentes de datos** — Registros bancarios y documentos. *Control:* acceso restringido al equipo autorizado
2. **Procesamiento y proteccion** — Descarga, extraccion, tokenizacion y enmascaramiento. *Control:* tratamiento de datos antes de evaluacion
3. **Almacenamiento** — Datos estructurados y documentos. *Control:* cifrado conforme a normativa
4. **Evaluacion y validacion** — Evaluacion de modelos sobre documentos. *Control:* modulo de anonimizacion
5. **Retencion y eliminacion** — Politica de 5 anos (cumplimiento fiscal), seguida de eliminacion segura. *Control:* *endpoint* de eliminacion + purga automatica conforme a LFPDPPP

---

## Requerimientos de privacidad

| Codigo | Descripcion | Tipo |
|--------|-------------|------|
| R-01 | Cifrado de CLABE, RFC y CURP en transito (TLS) y en reposo (Fernet AES-CBC con HMAC-SHA256) | No funcional |
| R-02 | Control de acceso basado en roles (RBAC) y auditoria de accesos a datos sensibles | Funcional |
| R-03 | Gestion del consentimiento informado con opcion de revocacion via *endpoints* dedicados | Funcional |
| R-04 | Anonimizacion automatica mediante tokenizacion, enmascaramiento y pseudonimizacion antes del uso en evaluacion | No funcional |
| R-05 | Eliminacion segura de datos personales con politica de retencion de 5 anos y mecanismo de purga | No funcional |

---

## Riesgos de privacidad

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Fuga de CLABEs en datos de evaluacion | Media | Critico | Tokenizacion + cifrado en reposo |
| Acceso no autorizado a documentos | Baja | Alto | RBAC + cifrado + URLs prefirmadas |
| Re-identificacion de datos anonimizados | Baja | Alto | Pseudonimizacion + enmascaramiento parcial |
| Perdida de datos por fallo de hardware | Media | Medio | Respaldos gestionados por Railway/PostgreSQL |
| Uso indebido por personal interno | Baja | Alto | RBAC + auditoria + minimo privilegio |
