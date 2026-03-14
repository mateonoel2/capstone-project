import json
import os

from anthropic import Anthropic

from src.core.logger import get_logger

logger = get_logger(__name__)

MODEL = "claude-haiku-4-5-20251001"


def _get_client() -> Anthropic:
    return Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def generate_schema_from_description(description: str) -> dict:
    """Convert natural language description into a JSON Schema for extraction fields."""
    client = _get_client()

    system_prompt = """Eres un asistente que genera JSON Schemas para extracción de documentos.
Dado una descripción en lenguaje natural de los campos a extraer, genera un JSON Schema válido.

Reglas:
- Siempre incluye un campo booleano de validación del tipo de documento como primer campo
  (ej: "is_valid_document"), con description que indique qué validar
- Los tipos permitidos son: "string", "number", "integer", "boolean"
- Para campos de fecha usa: {"type": "string", "format": "date"} (formato YYYY-MM-DD)
- Cada campo debe tener "type" y "description" (en español)
- Los nombres de campo deben ser snake_case en inglés
- El schema debe tener "type": "object", "properties": {...}, "required": [...]
- Todos los campos deben estar en "required"

Responde SOLO con el JSON Schema, sin explicaciones ni markdown."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": description}],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [line for line in lines if not line.startswith("```")]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"El modelo generó un JSON inválido: {e}") from e


def generate_prompt_from_schema(output_schema: dict, document_type: str | None = None) -> str:
    """Generate an extraction prompt in Spanish based on the schema fields."""
    client = _get_client()

    properties = output_schema.get("properties", {})
    fields_desc = []
    for name, prop in properties.items():
        if prop.get("type") == "boolean" and name.startswith("is_"):
            continue
        desc = prop.get("description", "")
        field_type = prop.get("type", "string")
        fields_desc.append(f"- {name} ({field_type}): {desc}")

    fields_text = "\n".join(fields_desc)
    doc_context = (
        f"Tipo de documento: {document_type}"
        if document_type
        else "Tipo de documento: no especificado"
    )

    system_prompt = """Eres un asistente que genera prompts de extracción de documentos en español.
Dado un schema de campos y un tipo de documento, genera un prompt claro y detallado
para un modelo de visión que extraerá esos campos de una imagen de documento.

Reglas:
- El prompt debe estar en español
- Debe ser específico sobre qué campos extraer y cómo
- Debe incluir instrucciones sobre qué hacer cuando un campo no se encuentra
- Debe indicar que no invente información
- No incluyas markdown, solo el texto del prompt

Responde SOLO con el texto del prompt."""

    user_msg = f"""{doc_context}

Campos a extraer:
{fields_text}

Genera un prompt de extracción para estos campos."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )

    return response.content[0].text.strip()


def update_prompt_with_instructions(
    current_prompt: str,
    instructions: str,
    output_schema: dict,
) -> str:
    """Update an existing extraction prompt based on user instructions."""
    client = _get_client()

    properties = output_schema.get("properties", {})
    fields_desc = []
    for name, prop in properties.items():
        if prop.get("type") == "boolean" and name.startswith("is_"):
            continue
        desc = prop.get("description", "")
        field_type = prop.get("type", "string")
        fields_desc.append(f"- {name} ({field_type}): {desc}")

    fields_text = "\n".join(fields_desc)

    system_prompt = """Eres un asistente que modifica prompts de extracción de documentos.
Se te dará un prompt existente, los campos del schema y las instrucciones del usuario
sobre qué cambiar. Debes devolver el prompt actualizado.

Reglas:
- Aplica SOLO los cambios que pide el usuario
- Mantén el estilo y estructura del prompt original
- El prompt debe seguir en español
- No incluyas markdown, solo el texto del prompt actualizado

Responde SOLO con el texto del prompt actualizado."""

    user_msg = f"""Prompt actual:
---
{current_prompt}
---

Campos del schema:
{fields_text}

Instrucciones del usuario: {instructions}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )

    return response.content[0].text.strip()
