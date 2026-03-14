"""Debug script: test orientation detection + extraction pipeline.

Usage:
    python scripts/debug_extraction.py <image_path>

Example:
    python scripts/debug_extraction.py data/IMG_8400.jpg
"""

import base64
import io
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

PROMPT = """Analiza la imagen del documento de identidad y extrae la siguiente información:

1. first_name: Extrae el nombre de pila del titular del documento. Debe ser una cadena de texto que contenga solo el primer nombre.

2. last_name: Extrae el apellido del titular del documento. Si hay múltiples apellidos, incluye todos separados por espacio.

3. dni_number: Extrae el número de identificación nacional exactamente como aparece en el documento. Incluye letras y números si existen, sin modificar su formato original.

4. birth_date: Extrae la fecha de nacimiento del titular y conviértela al formato YYYY-MM-DD. Por ejemplo, si la fecha aparece como "15 de marzo de 1990", debes extraerla como "1990-03-15".

Instrucciones importantes:
- Si algún campo no es visible o no aparece en el documento, responde con el valor null para ese campo.
- No inventes ni asumas información que no esté claramente visible en la imagen.
- Extrae solo la información que puedas leer directamente del documento.
- Responde en formato JSON con las claves exactas mencionadas.
- Si la fecha de nacimiento está en un formato diferente, conviértela al formato especificado YYYY-MM-DD.

Proporciona la respuesta como un objeto JSON válido."""

SCHEMA = {
    "type": "object",
    "properties": {
        "is_valid_document": {
            "type": "boolean",
            "description": "Indica si el documento es un DNI válido y legible",
        },
        "first_name": {
            "type": "string",
            "description": "Nombre del titular del DNI",
        },
        "last_name": {
            "type": "string",
            "description": "Apellido del titular del DNI",
        },
        "dni_number": {
            "type": "string",
            "description": "Número de identificación del DNI",
        },
        "birth_date": {
            "type": "string",
            "format": "date",
            "description": "Fecha de nacimiento del titular en formato YYYY-MM-DD",
        },
    },
    "required": [
        "is_valid_document",
        "first_name",
        "last_name",
        "dni_number",
        "birth_date",
    ],
}

ORIENTATION_SCHEMA = {
    "type": "object",
    "properties": {
        "text_direction": {
            "type": "string",
            "enum": ["normal", "rotated_left", "rotated_right", "upside_down"],
            "description": (
                "How the text in the document currently appears: "
                "'normal' = reads left-to-right horizontally, "
                "'rotated_left' = text runs upward (top of text is on the left side of image), "
                "'rotated_right' = text runs downward (top of text is on the right side of image), "
                "'upside_down' = text is flipped 180 degrees."
            ),
        },
    },
    "required": ["text_direction"],
}

# Map text direction to clockwise rotation needed to fix
DIRECTION_TO_ROTATION = {
    "normal": 0,
    "rotated_left": 270,     # top of text points left → rotate 270° CW (= 90° CCW)
    "rotated_right": 90,     # top of text points right → rotate 90° CW
    "upside_down": 180,
}

MODEL = "claude-haiku-4-5-20251001"


def load_image_b64(image_path: Path) -> tuple[str, str]:
    raw_bytes = image_path.read_bytes()
    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    mime = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return b64, mime


def pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def check_orientation(client: anthropic.Anthropic, image_b64: str, mime: str) -> dict:
    """Ask Haiku if the image needs rotation."""
    tool = {
        "name": "orientation_check",
        "description": "Report the orientation of the document in the image",
        "input_schema": ORIENTATION_SCHEMA,
    }
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        temperature=0,
        tools=[tool],
        tool_choice={"type": "tool", "name": "orientation_check"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": mime, "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Look at the main text in this document image. "
                            "In which direction does the text run? "
                            "Is it horizontal and readable (normal), "
                            "or is it rotated sideways or upside down?"
                        ),
                    },
                ],
            }
        ],
    )
    tool_block = next(b for b in response.content if b.type == "tool_use")
    text_direction = tool_block.input.get("text_direction", "normal")
    rotation = DIRECTION_TO_ROTATION.get(text_direction, 0)
    return {
        "text_direction": text_direction,
        "rotation_degrees": rotation,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def rotate_image(image_path: Path, degrees_cw: int) -> str:
    """Rotate image by degrees clockwise and return base64."""
    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if degrees_cw != 0:
        # PIL rotate is counterclockwise, so negate
        img = img.rotate(-degrees_cw, expand=True)
    # Resize if too large
    max_dim = 2048
    if img.width > max_dim or img.height > max_dim:
        ratio = min(max_dim / img.width, max_dim / img.height)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.Resampling.LANCZOS)
    return pil_to_b64(img)


def extract(client: anthropic.Anthropic, image_b64: str, mime: str) -> dict:
    """Run extraction with tool_use."""
    tool = {
        "name": "extraction_output",
        "description": "Extract structured data from the document",
        "input_schema": SCHEMA,
    }
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        temperature=0,
        tools=[tool],
        tool_choice={"type": "tool", "name": "extraction_output"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": mime, "data": image_b64},
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )
    tool_block = next(b for b in response.content if b.type == "tool_use")
    return {
        **tool_block.input,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/debug_extraction.py <image_path>")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"File not found: {image_path}")
        sys.exit(1)

    image_b64, mime = load_image_b64(image_path)
    print(f"Image: {image_path.name} ({len(image_path.read_bytes())} bytes)\n")

    client = anthropic.Anthropic()

    # Step 1: Check orientation
    print("=== Step 1: Orientation check ===")
    orientation = check_orientation(client, image_b64, mime)
    print(f"  text_direction: {orientation['text_direction']}")
    print(f"  rotation_degrees: {orientation['rotation_degrees']}")
    print(f"  tokens: {orientation['usage']}")

    # Step 2: Rotate if needed
    rotation = orientation["rotation_degrees"]
    if rotation != 0:
        print(f"\n=== Step 2: Rotating {rotation}° clockwise ===")
        corrected_b64 = rotate_image(image_path, rotation)
    else:
        print("\n=== Step 2: No rotation needed ===")
        corrected_b64 = image_b64

    # Step 3: Extract
    print("\n=== Step 3: Extraction ===")
    result = extract(client, corrected_b64, "image/jpeg")
    usage = result.pop("usage")
    print(f"  tokens: {usage}")
    print(f"  Result: {json.dumps(result, indent=2)}")

    # Compare
    print("\n=== Baseline (no rotation) ===")
    baseline = extract(client, image_b64, mime)
    baseline_usage = baseline.pop("usage")
    print(f"  tokens: {baseline_usage}")
    print(f"  Result: {json.dumps(baseline, indent=2)}")

    print("\nExpected: MATEO | NOEL RABINES | 73858504 | 2001-03-24")


if __name__ == "__main__":
    main()
