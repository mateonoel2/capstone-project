---
name: update-docs
description: Actualiza README.md, CLAUDE.md y la wiki para reflejar el estado actual del proyecto después de un PR.
argument-hint: "[número de PR o descripción de los cambios]"
---

# Actualizar documentación del proyecto

Después de que se mergea (o está por mergearse) un PR, actualiza `README.md`, `CLAUDE.md` y los archivos de la `wiki/` para que reflejen el estado actual del codebase.

## Pasos

1. **Entender qué cambió**: Si se proporciona un número de PR o descripción en `$ARGUMENTS`, usa `gh pr view $ARGUMENTS` para ver los detalles. Si no, revisa `git log main --oneline -10` y el diff de los cambios recientes.

2. **Auditar el codebase**: Lee los docs actuales (`README.md`, `CLAUDE.md`, y los archivos relevantes en `wiki/`). Luego explora el codebase para verificar:
   - Estructura del proyecto (directorios, archivos clave)
   - Comandos disponibles (backend, frontend, Docker)
   - Arquitectura (layers, services, parsers, models)
   - Variables de entorno
   - Conceptos clave del dominio
   - Lista de features

3. **Actualizar `CLAUDE.md`**: Es la guía interna para Claude Code. Mantenla concisa y factual. Actualiza:
   - Sección de arquitectura (layers, archivos, services)
   - Sección de comandos (si se agregaron scripts o comandos nuevos)
   - Conceptos clave del dominio (si se introdujeron nuevos)
   - Variables de entorno (si se agregaron nuevas)
   - NO agregues secciones que no existan a menos que sea claramente necesario

4. **Actualizar `README.md`**: Es la descripción del proyecto para el usuario (en español). Actualiza:
   - Lista de features (`Características`)
   - Árbol de estructura del proyecto (`Estructura del Proyecto`)
   - Cualquier descripción que ya no aplique
   - NO cambies las secciones de instalación o uso a menos que los comandos hayan cambiado

5. **Actualizar la wiki** (`wiki/`): Los archivos son markdown en español con términos técnicos en inglés en cursiva. Actualiza solo las páginas afectadas por los cambios del PR:
   - `Home.md` — Estructura del proyecto, tecnologías, estado general
   - `Dashboard.md` — Si cambiaron métricas o secciones del dashboard
   - `Arquitectura-Mínima-Operable.md` — Si cambió la arquitectura
   - `Guía-de-Scripts.md` — Si se agregaron/eliminaron scripts
   - `Comparación-de-Parsers.md` — Si cambió algo de parsers
   - `Últimas-Actualizaciones.md` — Agregar entrada con los cambios del PR
   - `_Sidebar.md` — Si se agregó/eliminó una página de la wiki
   - NO toques páginas que no fueron afectadas por los cambios

## Reglas
- Mantén el mismo idioma y tono: español con términos técnicos en inglés en *cursiva*
- NO agregues emojis
- NO infles las descripciones — solo documenta lo que realmente existe en el código
- Elimina referencias a archivos borrados, parsers viejos o features deprecadas
- Mantén `CLAUDE.md` conciso — es una referencia, no un tutorial
- NO hagas commit — solo haz los edits para que el usuario los revise
