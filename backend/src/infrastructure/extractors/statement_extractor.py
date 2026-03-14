import base64
import io
import os
from pathlib import Path

import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from PIL import Image

from src.core.logger import get_logger

logger = get_logger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS

EXTRACTION_PROMPT = """Analiza este documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:
1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   IMPORTANTE: La CLABE puede aparecer con espacios entre grupos de dígitos
   (ej: "072 691 00844421773 3"). Elimina todos los espacios y devuelve solo
   los 18 dígitos consecutivos. Si el resultado tiene más de 18 dígitos, toma
   los primeros 18.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos, documentos
legales, etc.), marca is_valid_document como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""

ORIENTATION_CHECK_PROMPT = (
    "Look at the main text in this document image. "
    "In which direction does the text run? "
    "Is it horizontal and readable (normal), "
    "or is it rotated sideways or upside down?"
)

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

# Map detected text direction to clockwise rotation needed to correct it
DIRECTION_TO_ROTATION = {
    "normal": 0,
    "rotated_left": 270,  # top of text points left → rotate 270° CW (= 90° CCW)
    "rotated_right": 90,  # top of text points right → rotate 90° CW
    "upside_down": 180,
}


class StatementExtractor:
    def __init__(
        self,
        prompt: str = EXTRACTION_PROMPT,
        model: str = "claude-haiku-4-5-20251001",
        output_schema: dict | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model_name = model
        self.max_tokens = max_tokens
        self.prompt = prompt
        self.output_schema = output_schema
        self.llm = ChatAnthropic(
            model=model,
            api_key=self.api_key,
            max_tokens=max_tokens,
            temperature=0,
        )
        if output_schema:
            if isinstance(output_schema, dict) and "title" not in output_schema:
                output_schema = {"title": "extraction_output", **output_schema}
            self.structured_llm = self.llm.with_structured_output(output_schema)
        else:
            from src.domain.schemas import ExtractionOutput

            self.structured_llm = self.llm.with_structured_output(ExtractionOutput)

    def _image_to_base64(self, image: Image.Image) -> str:
        max_dimension = 2048
        if image.width > max_dimension or image.height > max_dimension:
            ratio = min(max_dimension / image.width, max_dimension / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _check_orientation(self, image_b64: str) -> int:
        """Ask the model to detect text orientation. Returns CW degrees to correct."""
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model_name,
                max_tokens=256,
                temperature=0,
                tools=[
                    {
                        "name": "orientation_check",
                        "description": "Report the orientation of the document text",
                        "input_schema": ORIENTATION_SCHEMA,
                    }
                ],
                tool_choice={"type": "tool", "name": "orientation_check"},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_b64,
                                },
                            },
                            {"type": "text", "text": ORIENTATION_CHECK_PROMPT},
                        ],
                    }
                ],
            )
            tool_block = next(b for b in response.content if b.type == "tool_use")
            direction = tool_block.input.get("text_direction", "normal")
            rotation = DIRECTION_TO_ROTATION.get(direction, 0)
            logger.info("Orientation check: %s → rotation %d°", direction, rotation)
            return rotation
        except Exception as e:
            logger.warning("Orientation check failed, assuming normal: %s", e)
            return 0

    def _load_image_file(self, image_path: Path) -> list[str]:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # First pass: encode for orientation check
        image_b64 = self._image_to_base64(image)
        rotation = self._check_orientation(image_b64)

        if rotation != 0:
            logger.info("Rotating image %d° clockwise", rotation)
            # PIL rotate is counterclockwise, so negate
            image = image.rotate(-rotation, expand=True)
            image_b64 = self._image_to_base64(image)

        return [image_b64]

    def _extract_with_pdf(self, pdf_path: Path) -> dict:
        logger.info("=== PDF extraction ===")
        logger.info("Model: %s, prompt length: %d", self.model_name, len(self.prompt))
        pdf_data = pdf_path.read_bytes()
        pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
        content = [
            {
                "type": "file",
                "source_type": "base64",
                "mime_type": "application/pdf",
                "data": pdf_base64,
            },
            {"type": "text", "text": self.prompt},
        ]
        message = HumanMessage(content=content)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        logger.info("Extraction result: %s", result)
        return result

    def _extract_with_vision(self, base64_images: list[str]) -> dict:
        logger.info("=== Vision extraction ===")
        logger.info("Model: %s, prompt length: %d", self.model_name, len(self.prompt))
        content = [
            {
                "type": "image",
                "source_type": "base64",
                "data": base64_images[0],
                "mime_type": "image/jpeg",
            },
            {"type": "text", "text": self.prompt},
        ]
        message = HumanMessage(content=content)
        result = self.structured_llm.invoke([message])
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        logger.info("Extraction result: %s", result)
        return result

    def extract_file(self, file_path: Path) -> dict:
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {suffix}")

        if suffix in PDF_EXTENSIONS:
            return self._extract_with_pdf(file_path)

        base64_images = self._load_image_file(file_path)
        if not base64_images:
            raise ValueError("No se pudo procesar el archivo")

        return self._extract_with_vision(base64_images)
